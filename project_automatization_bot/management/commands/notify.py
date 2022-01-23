from django.conf import settings
from django.core.management import BaseCommand, CommandError
from project_automatization_bot.models import  Student
import telegram
import logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
           main()
        except Exception as exc:
            raise CommandError(exc)


def main():
    for student in Student.objects.select_related('team').exclude(team=None):
        bot = telegram.Bot(token=settings.TOKEN)
        call_time = student.team.start_time_call
        team_list = ', '.join([str(name) for name in Student.objects.filter(team=student.team)])
        pm = student.team.manager.name
        try:
            bot.send_message(
                text=f'Привет! Командные созвоны будут в {call_time}.\n\n'
                f'Состав вашей команды: {team_list}.\n\n'
                f'Проект-менеджером будет {pm}\n\n'
                f'Созвоны будут в Discord {settings.DISCORD}',
                chat_id=student.tg_chat_id
            )
        except Exception as err:
            print(err)