from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext, MessageHandler, Filters, ConversationHandler, CommandHandler, Updater
from project_automatization_bot.models import Student
import datetime


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            main()
        except Exception as exc:
            raise CommandError(exc)


WEEK, START_CALL_TIME, END_CALL_TIME = range(3)
BUTTONS_IN_ROW = 4
ROWS = 4


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_reply_keyboard(start_time='08:00', end_time='21:00', period=30):
    start_time = datetime.datetime.strptime(start_time,'%H:%M')
    end_time = datetime.datetime.strptime(end_time,'%H:%M')
    delta = datetime.timedelta(minutes=period)
    time_list = [(start_time+delta*multiper).strftime('%H:%M') for multiper in range(int((end_time-start_time)/delta))]
    button_lists = [time_list[x:x+BUTTONS_IN_ROW] for x in range(0, len(time_list), BUTTONS_IN_ROW)]
    for input_index in range(2*(ROWS-1), len(button_lists), ROWS):
        button_lists.insert(input_index, ['⬅ Назад', 'Далее ➡'])
    button_lists.insert(ROWS-1, ['Далее ➡'])
    button_lists.insert(len(button_lists), ['⬅ Назад'])
    return button_lists


def start(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    try:
        student = Student.objects.get(tg_chat_id=chat_id)
    except ObjectDoesNotExist:
        context.bot.send_message(
            chat_id=chat_id,
            text=f'Вы не найдены в списке студентов :( '
            f'Обратитесь к администратору.\nВаш id {chat_id}'
        )
        return ConversationHandler.END

    context.user_data['student'] = student

    update.message.reply_text(
        'Привет! Я бот-распределитель.'
        '\nУкажи пожалуйста в какую неделю месяца тебе удобно работать над проектом?',
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[['3', '4']], one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return WEEK


def week(update: Update, context: CallbackContext):
    student = context.user_data['student']
    selected_week = update.message.text
    student.week = selected_week
    student.save()

    reply_keyboard = generate_reply_keyboard()
    context.user_data['slice_index'] = ROWS
    context.user_data['keyboard'] = reply_keyboard
    update.message.reply_text(
        'Укажи удобный интервал времени для созвона.\nВремя начала: ',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard[:ROWS], one_time_keyboard=True, resize_keyboard=True
        )
    )
    return START_CALL_TIME


def start_call_time(update: Update, context: CallbackContext):
    reply = update.message.text
    reply_keyboard = context.user_data['keyboard']
    slice_index = context.user_data['slice_index']
    if reply == 'Далее ➡':
        context.bot.send_message(
            text='👀',
            chat_id=update.message.chat_id,
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard[slice_index:slice_index+ROWS],
                one_time_keyboard=True,
                resize_keyboard=True
            )
        )
        context.user_data['slice_index'] = slice_index + ROWS
        return START_CALL_TIME
    if reply == '⬅ Назад':
        context.bot.send_message(
            text='👀',
            chat_id=update.message.chat_id,
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard[slice_index-ROWS*2:slice_index-ROWS],
                one_time_keyboard=True,
                resize_keyboard=True
            )
        )
        context.user_data['slice_index'] = slice_index - ROWS
        return START_CALL_TIME

    student = context.user_data['student']
    student.start_time_call = update.message.text
    student.save()
    context.user_data['slice_index'] = ROWS

    update.message.reply_text(
        'Время завершения созвона: ',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard[:ROWS], one_time_keyboard=True, resize_keyboard=True
        )
    )
    return END_CALL_TIME


def end_call_time(update: Update, context: CallbackContext):
    reply = update.message.text
    reply_keyboard = generate_reply_keyboard(end_time='21:30')
    slice_index = context.user_data['slice_index']
    if reply == 'Далее ➡':
        context.bot.send_message(
            text='👀',
            chat_id=update.message.chat_id,
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard[slice_index:slice_index + ROWS],
                one_time_keyboard=True,
                resize_keyboard=True
            )
        )
        context.user_data['slice_index'] = slice_index + ROWS
        return END_CALL_TIME
    if reply == '⬅ Назад':
        context.bot.send_message(
            text='👀',
            chat_id=update.message.chat_id,
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard[slice_index - ROWS * 2:slice_index - ROWS],
                one_time_keyboard=True,
                resize_keyboard=True
            )
        )
        context.user_data['slice_index'] = slice_index - ROWS
        return END_CALL_TIME

    student = context.user_data['student']
    if datetime.datetime.strptime(student.start_time_call,'%H:%M') >= datetime.datetime.strptime(update.message.text,'%H:%M'):
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text='Укажи пожалуйста корректно время звершения звонка:',
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard[:ROWS], one_time_keyboard=True, resize_keyboard=True
            )
        )
        context.user_data['slice_index'] = ROWS
        return END_CALL_TIME
    student.end_time_call = update.message.text
    student.time_to_json()
    student.save()

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Учел твои пожелания. Жди уведомление о распределении в команду. Удачи!'
    )
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Пока!', reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main():
    updater = Updater(token=settings.TOKEN)
    dispatcher = updater.dispatcher

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            WEEK: [MessageHandler(Filters.regex('[1-4]'), week)],
            START_CALL_TIME: [
                MessageHandler(
                    Filters.regex('^(([0,1][0-9])|(2[0-3])):[0-5][0-9]$') | Filters.regex('⬅ Назад|Далее ➡'),
                    start_call_time
                )
            ],
            END_CALL_TIME: [
                MessageHandler(
                    Filters.regex('^(([0,1][0-9])|(2[0-3])):[0-5][0-9]$') | Filters.regex('⬅ Назад|Далее ➡'),
                    end_call_time
                )
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conversation_handler)
    updater.start_polling()
    updater.idle()
