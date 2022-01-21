from django.conf import settings
from django.core.management import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from telegram.ext import Updater
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext, MessageHandler, Filters, ConversationHandler, CommandHandler
from project_automatization_bot.models import Student


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            main()
        except Exception as exc:
            raise CommandError(exc)


WEEK, START_CALL_TIME, END_CALL_TIME = range(3)


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

    reply_keyboard = [['18:00', '18:30', '19:30', '20:00', '21:00', '22:00']]
    update.message.reply_text(
        'Укажи удобный интервал времени для созвона.\nВремя начала: ',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
    )
    return START_CALL_TIME


def start_call_time(update: Update, context: CallbackContext):
    student = context.user_data['student']
    student.start_time_call = update.message.text
    student.save()

    reply_keyboard = [['18:00', '18:30', '19:30', '20:00', '21:00', '22:00']]
    update.message.reply_text(
        'Время завершения: ',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        )
    )
    return END_CALL_TIME


def end_call_time(update: Update, context: CallbackContext):
    student = context.user_data['student']
    student.end_time_call = update.message.text
    student.save()

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text='Учел твои пожелания. Жди уведомление о распределении в команду. Удачи!'
    )
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext):
    """Cancels and ends the conversation."""
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
            START_CALL_TIME: [MessageHandler(Filters.regex('^(([0,1][0-9])|(2[0-3])):[0-5][0-9]$'), start_call_time)],
            END_CALL_TIME: [MessageHandler(Filters.regex('^(([0,1][0-9])|(2[0-3])):[0-5][0-9]$'), end_call_time)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conversation_handler)
    updater.start_polling()
    updater.idle()
