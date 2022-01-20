import json
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args, **options):
        def create_json(dict, file_name):
            print(dict)
            with open(f"{file_name}", "w") as my_file:
                my_file.write(json.dumps(dict))


        def create_json_students():
            students = {
                "Джуны": [{
                          "name": "Александр Попов",
                          "level": "junior",
                          "tg_username": "@example",
                          "discord_username": "example#1234",
                          "is_far_east": True
                        },
                        {
                          "name": "Иван Петров",
                          "level": "novice+",
                          "tg_username": "@example2",
                          "discord_username": "example2#4321",
                          "is_far_east": False
                        }],
                "Новички+":[{
                          "name": "Александр Попов",
                          "level": "junior",
                          "tg_username": "@example",
                          "discord_username": "example#1234",
                          "is_far_east": True
                        },
                        {
                          "name": "Иван Петров",
                          "level": "novice+",
                          "tg_username": "@example2",
                          "discord_username": "example2#4321",
                          "is_far_east": False
                        }],
                "Новички": [{
                          "name": "Александр Попов",
                          "level": "junior",
                          "tg_username": "@example",
                          "discord_username": "example#1234",
                          "is_far_east": True
                        },
                        {
                          "name": "Иван Петров",
                          "level": "novice+",
                          "tg_username": "@example2",
                          "discord_username": "example2#4321",
                          "is_far_east": False
                        }],
            }
            create_json(students, "students_json")


        def create_json_project_managers():
            project_managers = {
                "1": {
                      "name": "Катерина",
                      "tg_username": "@example",
                      "discord_username": "example#1234",
                      "availible_time": "8:00-10:00, 19:00-21:00"
                    },
                "2": {
                    "name": "Тим",
                    "tg_username": "@example2",
                    "discord_username": "example#2234",
                    "availible_time": "18:00-20:00"
                },
            }
            create_json(project_managers, "project_managers_json")

        create_json_students()
        create_json_project_managers()
