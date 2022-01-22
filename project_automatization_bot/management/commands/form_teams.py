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

        def handle_distribution(
            teams,
            student,
            formed_teams,
            time,
            time_windows,
            first_level_priority,
            second_level_priority,
            is_added):
            for team_id, time_window in first_level_priority.items():
                if (student.time_call.get(time_window) is not None
                        and student.time_call.get(time_window)
                        and teams[team_id]['level'] != student.status
                        and not (teams[team_id]['level'] != student.status
                                 and (teams[team_id]['level'] == 'junior'
                                 or student.status == 'junior'))):
                    teams[team_id]['third'] = student.tg_chat_id
                    formed_teams[team_id] = teams.pop(team_id)
                    time_windows[time] -= 1
                    is_added = 1
                    print('add third')
                    print(f'Оставшиеся окна: {time_windows}')
                    del first_level_priority[team_id]
                    print('first_priority')
                    pprint(first_level_priority)
                    return is_added
            
            for team_id, time_window in second_level_priority.items():
                if (student.time_call.get(time_window) is not None
                        and student.time_call.get(time_window)
                        and teams[team_id]['level'] != student.status
                        and not (teams[team_id]['level'] != student.status
                                 and (teams[team_id]['level'] == 'junior'
                                 or student.status == 'junior'))):
                    teams[team_id]['second'] = student.tg_chat_id
                    is_added = 1
                    print('add second')
                    del second_level_priority[team_id]
                    first_level_priority[team_id] = time
                    first_level_priority = sorted(
                        first_level_priority.items(),
                        key=lambda x: x[1]
                    )
                    print('first_priority')
                    pprint(first_level_priority)
                    print('second_priority')
                    pprint(second_level_priority)
                    return is_added

            for team_id in teams:
                if teams[team_id]['start_time'] == time:
                    if teams[team_id].get('level') is None:
                        teams[team_id]['first'] = student.tg_chat_id
                        teams[team_id]['level'] = student.status
                        is_added = 1
                        print('add first')
                        second_level_priority[team_id] = time
                        second_level_priority = sorted(
                            second_level_priority.items(),
                            key=lambda x: x[1]
                        )
                        print('second_priority')
                        pprint(second_level_priority)
                        return is_added
                    else:
                        if (teams[team_id]['level'] != student.status
                                and (teams[team_id]['level'] == 'junior'
                                or student.status == 'junior')):
                            continue
                        else:
                            if teams[team_id].get('second') is None:
                                teams[team_id]['second'] = student.tg_chat_id
                                is_added = 1
                                print('add second')
                                del second_level_priority[team_id]
                                first_level_priority[team_id] = time
                                first_level_priority = sorted(
                                    first_level_priority.items(),
                                    key=lambda x: x[1]
                                )
                                print('first_priority')
                                pprint(first_level_priority)
                                print('second_priority')
                                pprint(second_level_priority)
                                return is_added
                            else:
                                teams[team_id]['third'] = student.tg_chat_id
                                formed_teams[team_id] = teams.pop(team_id)
                                time_windows[time] -= 1
                                is_added = 1
                                print('add third')
                                print(f'Оставшиеся окна: {time_windows}')
                                del first_level_priority[team_id]
                                print('first_priority')
                                pprint(first_level_priority)
                                return is_added

        def add_student_to_temp_team(
            teams,
            student,
            formed_teams,
            time,
            time_windows,
            first_level_priority,
            second_level_priority
        ):
            is_added = 0
            pprint(first_level_priority)
            pprint(second_level_priority)
            print(time)
            if (first_level_priority 
                    and (time in first_level_priority.values())):
                for team_id in first_level_priority:
                    if (teams[team_id]['level'] != student.status
                            and (teams[team_id]['level'] == 'junior'
                            or student.status == 'junior')):
                        continue
                    else:
                        teams[team_id]['third'] = student.tg_chat_id
                        formed_teams[team_id] = teams.pop(team_id)
                        time_windows[time] -= 1
                        is_added = 1
                        print('add third')
                        print(f'Оставшиеся окна: {time_windows}')
                        del first_level_priority[team_id]
                        print('first_priority')
                        pprint(first_level_priority)
                        break
            if (second_level_priority
                    and (time in second_level_priority.values())
                    and not is_added):
                for team_id in second_level_priority:
                    if time in second_level_priority.values():
                        if (teams[team_id]['level'] != student.status
                                and (teams[team_id]['level'] == 'junior'
                                or student.status == 'junior')):
                            continue
                        else:
                            teams[team_id]['second'] = student.tg_chat_id
                            is_added = 1
                            print('add second')
                            del second_level_priority[team_id]
                            first_level_priority[team_id] = time
                            first_level_priority = sorted(
                                first_level_priority.items(),
                                key=lambda x: x[1]
                            )
                            print('first_priority')
                            pprint(first_level_priority)
                            print('second_priority')
                            pprint(second_level_priority)
                            break
            if not is_added:
                print('HERE')
                is_added = handle_distribution(
                    teams=teams,
                    student=student,
                    formed_teams=formed_teams,
                    time=time,
                    time_windows=time_windows,
                    first_level_priority=first_level_priority,
                    second_level_priority=second_level_priority,
                    is_added=is_added
                )
            return is_added

        def form_teams(sorted_students, time_windows):
            out_of_project = list()
            teams = create_teams(time_windows)
            first_level_priority_teams = dict()
            second_level_priority_teams = dict()
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
                                time_windows=time_windows,
                                first_level_priority=first_level_priority_teams,
                                second_level_priority=second_level_priority_teams
                            )
                else:
                    for time in selected_student.time_call:
                        if (time_windows.get(time) is not None
                                and time_windows.get(time)
                                and selected_student.time_call[time]):
                            is_added = add_student_to_temp_team(
                                teams=teams,
                                student=selected_student,
                                formed_teams=formed_teams,
                                time=time,
                                time_windows=time_windows,
                                first_level_priority=first_level_priority_teams,
                                second_level_priority=second_level_priority_teams
                            )
                            if is_added:
                                break

            return out_of_project, teams, formed_teams
        
        teams = form_teams(sorted_students, time_windows)
        print('Без созвонов с ПМ:')
        pprint(teams[0])
        print('Неполные команды:')
        pprint(teams[1])
        print('Сформированные команды:')
        pprint(teams[2])
