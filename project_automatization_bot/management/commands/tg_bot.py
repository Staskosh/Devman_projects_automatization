from django.conf import settings
from django.core.management import BaseCommand, CommandError
from telegram.ext import Updater
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext, MessageHandler, Filters, ConversationHandler, CommandHandler


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO)

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            main()
        except Exception as exc:
            raise CommandError(exc)


WEEK, CALLTIME = range(2)


def start(update: Update, context: CallbackContext):
    reply_keyboard = [['3', '4']]
    update.message.reply_text(
        'Привет! Я бот-распределитель.\nУкажи пожалуйста в какую неделю тебе удобно работать на проектом?',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return WEEK


def week(update: Update, context: CallbackContext):
    user = update.message.from_user
    logger.info(f'{user.first_name} selected week №{update.message.text}') #Здесь нужна запись в БД
    '''Доступные временные промежутки должны браться исходя из заполненных команд'''
    reply_keyboard = [['18:00-18:30', '18:30-19:00', '19:00-19:30', '19:30-20:00', '20:30-21:00', '21:30-22:00']]
    update.message.reply_text(
        'В какое время удобно созваниваться?.',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),
    )
    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext):
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main():
    updater = Updater(token=settings.TOKEN)
    dispatcher = updater.dispatcher

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            WEEK: [MessageHandler(Filters.regex('\d'), week)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conversation_handler)
    updater.start_polling()
    updater.idle()
