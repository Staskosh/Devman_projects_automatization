from django.utils.safestring import mark_safe

from .models import Student, Project_manager, Team, Project, Student_distribution
from django.contrib import admin
#from project_automatization_bot.management.commands.tg_bot import perform_raffle

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'tg_chat_id', 'start_time_call', 'end_time_call', 'is_far_east')


@admin.register(Project_manager)
class Project_managerAdmin(admin.ModelAdmin):
    list_display = ('name', 'tg_chat_id', 'available_time')



@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = (
        'external_id', 'name',
        'start_time_call', 'end_time_call'
    )

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'project_manager', 'students')



@admin.register(Student_distribution)
class Student_distributionAdmin(admin.ModelAdmin):
    list_display = ('Student_distribution',)

    def raffles(self, obj):
        #perform_raffle()
        return mark_safe( f'<a role="button"><button class="btn btn-primary"> Группировка </button></a>' )
# Register your models here.
