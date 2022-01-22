from django.core.management.base import BaseCommand
from pprint import pprint

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
            teams = dict()
            for project_manager in Project_manager.objects.all():
                schedule[project_manager.tg_chat_id] = project_manager.available_time
            for time in start_time.keys():
                for tg_chat_id in schedule.keys():
                    project_manager = Project_manager.objects.get(
                        tg_chat_id=tg_chat_id
                    )
                    if (time in schedule[tg_chat_id]
                            and schedule[tg_chat_id][time] != 0):
                        external_id = f'{time[:2]}{time[3:]}{tg_chat_id}'
                        teams[external_id] = dict()
                        teams[external_id]['start_time'] = time
                        teams[external_id]['manager'] = project_manager.name
            return teams

        def sort_students_by_available_time(time_windows):
            students = dict()
            for student in Student.objects.all():
                students[student.tg_chat_id]= 0
                for time in time_windows:
                    if student.time_call[time]:
                        students[student.tg_chat_id] += 1
            return sorted(students.items(), key=lambda x: x[1])
        
        sorted_students = sort_students_by_available_time(time_windows)
        # pprint(sorted_students)
        
        def add_student_to_temp_team(teams, student, formed_teams, time, time_windows):
            for team_id in teams:
                if teams[team_id]['start_time'] == time:
                    if teams[team_id].get('level') is None:
                        teams[team_id]['first'] = student.tg_chat_id
                        teams[team_id]['level'] = student.status
                        print('add first')
                        break
                    else:
                        if (teams[team_id]['level'] != student.status
                                and (teams[team_id]['level'] == 'junior'
                                or student.status == 'junior')):
                            continue
                        else:
                            if teams[team_id].get('second') is None:
                                teams[team_id]['second'] = student.tg_chat_id
                                print('add second')
                                break
                            elif teams[team_id].get('third') is None:
                                teams[team_id]['third'] = student.tg_chat_id
                                formed_teams[team_id] = teams.pop(team_id)
                                time_windows[time] -= 1
                                print('add third')
                                print(f'Оставшиеся окна: {time_windows}')
                                break
                            else:
                                print('go next team')
                                continue

        def form_teams(sorted_students, time_windows):
            out_of_project = list()
            teams = create_teams(time_windows)
            formed_teams = dict()

            for student in sorted_students:
                chat_id = student[0]
                print(f'select student {chat_id}')
                time_windows_count = student[1]
                selected_student = Student.objects.get(tg_chat_id=chat_id)
                if not time_windows_count:
                    out_of_project.append(student)
                    print(f'student {selected_student.tg_chat_id} was added to out')
                elif time_windows_count == 1:
                    for time in selected_student.time_call:
                        if selected_student.time_call[time]:
                            add_student_to_temp_team(
                                teams=teams,
                                student=selected_student,
                                formed_teams=formed_teams,
                                time=time,
                                time_windows=time_windows
                            )
                            print(f'student {selected_student.tg_chat_id} was added to new team')
                else:
                    for time in selected_student.time_call:
                        if (time_windows.get(time) is not None
                                and time_windows.get(time)
                                and selected_student.time_call[time]):
                            add_student_to_temp_team(
                                teams=teams,
                                student=selected_student,
                                formed_teams=formed_teams,
                                time=time,
                                time_windows=time_windows
                            )
                            print(f'student {selected_student.tg_chat_id} was added to team')
                            break

            return out_of_project, teams, formed_teams
        
        teams = form_teams(sorted_students, time_windows)
        print('Без созвонов с ПМ:')
        pprint(teams[0])
        print('Неполные команды:')
        pprint(teams[1])
        print('Сформированные команды:')
        pprint(teams[2])
