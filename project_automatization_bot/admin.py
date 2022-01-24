from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path

from .models import (
    Student,
    Project_manager,
    Team,
    Project,
    IncompleteTeam
)
from distribution import main
from project_automatization_bot.management.commands import notify


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    change_list_template = 'students_change_list.html'
    list_display = (
        'id',
        'name',
        'tg_chat_id',
        'start_time_call',
        'end_time_call',
        'is_far_east',
        'is_out_of_project'
    )
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('notify/', self.send_notifications),
            path('distribute/', self.make_distribution)
        ]
        return my_urls+urls


    def send_notifications(self, request):
        notify.main()
        self.message_user(request, 'Уведомления разосланы')
        return redirect('../')

    def make_distribution(self, request):
        main()
        self.message_user(request, 'Распределение произведено')
        return redirect('../')



@admin.register(Project_manager)
class Project_managerAdmin(admin.ModelAdmin):
    list_display = ('name', 'tg_chat_id', 'available_time')


@admin.register(IncompleteTeam)
class IncompleteTeamAdmin(admin.ModelAdmin):
    list_display = (
        'external_id', 'name',
        'start_time_call'
    )


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
        'external_id', 'name',
        'start_time_call'
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'project_manager', 'students')

