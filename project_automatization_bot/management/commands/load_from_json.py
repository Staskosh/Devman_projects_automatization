import json
from django.core.management.base import BaseCommand

from project_automatization_bot.models import Project_manager, Student


class Command(BaseCommand):
    def handle(self, *args, **options):
        pm_filepath = 'PMs.json'
        students_filepath = 'students.json'

        def read_from_json(filepath):
            with open(filepath, encoding='UTF-8', mode='r') as f:
                return json.loads(f.read())

        def update_project_managers(filepath):
            pm = read_from_json(filepath)
            for chat_id in pm.keys():
                product_manager = Project_manager.objects.get_or_create(
                    tg_chat_id=chat_id,
                    defaults={
                        'name': pm[chat_id]['name'],
                        'tg_chat_id': chat_id,
                        'available_time': pm[chat_id]['available_time']
                    }
                )
                product_manager[0].name = pm[chat_id]['name']
                product_manager[0].tg_chat_id = chat_id
                product_manager[0].available_time = pm[chat_id]['available_time']
                product_manager[0].save()

        update_project_managers(pm_filepath)

        def update_students(filepath):
            students = read_from_json(filepath)
            for chat_id in students.keys():
                student = Student.objects.get_or_create(
                    tg_chat_id=chat_id,
                    defaults={
                        'name': students[chat_id]['name'],
                        'tg_chat_id': chat_id,
                        'time_call': students[chat_id]['available_time'],
                        'status': students[chat_id]['level'],
                        'is_far_east': students[chat_id]['is_far_east']
                    }
                )
                student[0].name = students[chat_id]['name']
                student[0].tg_chat_id = chat_id
                student[0].time_call = students[chat_id]['available_time']
                student[0].status = students[chat_id]['level']
                student[0].is_far_east = students[chat_id]['is_far_east']
                student[0].save()
        
        update_students(students_filepath)