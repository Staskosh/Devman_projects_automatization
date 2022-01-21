from django.core.management.base import BaseCommand
from pprint import pprint
from collections import OrderedDict

from project_automatization_bot.models import (
    Project_manager,
    Student,
    Team
)


class Command(BaseCommand):
    def handle(self, *args, **options):
        def get_pms_available_time():
            time_windows = dict()
            for project_manager in Project_manager.objects.all():
                schedule = project_manager.available_time
                for time in schedule.keys():
                    if time in time_windows:
                        time_windows[time] += schedule[time]
                    else:
                        time_windows[time] = schedule[time]
            times = list(time_windows.keys())
            for time in times:
                if time_windows[time] == 0:
                    del time_windows[time]
            return time_windows

        time_windows = get_pms_available_time()
        print(f'Доступные окна: {time_windows}')

        def create_teams(start_time):
            schedule = dict()
            for project_manager in Project_manager.objects.all():
                schedule[project_manager.tg_chat_id] = project_manager.available_time
            for time in start_time.keys():
                for tg_chat_id in schedule.keys():
                    project_manager = Project_manager.objects.get(
                        tg_chat_id=tg_chat_id
                    )
                    if (time in schedule[tg_chat_id]
                            and schedule[tg_chat_id][time]) != 0:
                        Team.objects.create(
                            external_id=f'{time[:2]}{time[3:]}{tg_chat_id}',
                            name=f'{time} {project_manager.name}',
                            start_time_call=time,
                            manager=project_manager
                        )

        # create_teams(time_windows)

        def sort_students_by_available_time(time_windows):
            students = dict()
            for student in Student.objects.all():
                # student_time_windows = student.start_time_call
                # students[student.tg_chat_id]['time_windows'] = student_time_windows
                students[student.tg_chat_id]= 0
                for time in time_windows:
                    if student.start_time_call[time]:
                        students[student.tg_chat_id] += 1
            return sorted(students.items(), key=lambda x: x[1])
        
        pprint(sort_students_by_available_time(time_windows))
