from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path

from .models import (
    Student,
    Project_manager,
    Team,
    Project,
    Student_distribution,
    IncompleteTeam
)
from distribution import main


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'tg_chat_id',
        'start_time_call',
        'end_time_call',
        'is_far_east',
        'is_out_of_project'
    )


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


@admin.register(Student_distribution)
class Student_distributionAdmin(admin.ModelAdmin):
    list_display = ('activate_button',)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                '<int:pk>/',
                self.make_distribution,
                name='admin_make_distribution'
            )
        ]
        return my_urls + urls

    def make_distribution(self, request, pk):
        main()
        self.message_user(request, "Распределение произведено")
        return redirect("../../team/")
