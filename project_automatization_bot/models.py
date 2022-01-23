from django.db import models
from django.utils.html import format_html
from django.urls import reverse_lazy
from datetime import datetime


class Project_manager(models.Model):
    name = models.CharField(
        max_length=256,
        verbose_name='Имя и фамилия ПМ'
    )
    tg_chat_id = models.PositiveIntegerField(
        verbose_name='Чат id ПМ в Телеграм',
        unique=True
    )
    available_time = models.JSONField(verbose_name='Время cозвонов')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Проект менеджер'
        verbose_name_plural = 'Проект менеджеры'


class Team(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='Внешний ID команды',
        unique=True
    )
    name = models.CharField(
        max_length=256,
        verbose_name='Имя команды'
    )
    start_time_call = models.TimeField(verbose_name='Время начала созвонов')
    manager = models.ForeignKey(Project_manager, on_delete=models.CASCADE, null=True)
    # end_time_call = models.TimeField(verbose_name='Время окончания созвона')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'


class IncompleteTeam(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='Внешний ID команды',
        unique=True
    )
    name = models.CharField(
        max_length=256,
        verbose_name='Имя команды'
    )
    start_time_call = models.TimeField(verbose_name='Время начала созвонов')
    manager = models.ForeignKey(Project_manager, on_delete=models.CASCADE, null=True)
    # end_time_call = models.TimeField(verbose_name='Время окончания созвона')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Неполная команда'
        verbose_name_plural = 'Неполные команды'


class Student(models.Model):
    WEEK_CHOICES = [('3', '3'), ('4', '4')]

    name = models.CharField(
        max_length=256,
        verbose_name='Имя и фамилия студента'
    )
    tg_chat_id = models.PositiveIntegerField(
        verbose_name='Чат id ученика в Телеграм',
        unique=True
    )
    status = models.CharField(
        max_length=256,
        verbose_name='Статус ученика (джун, новичок+, новичок,)'
    )
    start_time_call = models.TimeField(
        verbose_name='Удобное время начала созвона',
        null=True
    )
    end_time_call = models.TimeField(
        verbose_name='Удобное время конца созвона',
        null=True
    )
    time_call = models.JSONField('JSON формат времени', null=True)
    week = models.CharField(
        verbose_name='Выбранная неделя занятий',
        max_length=1,
        choices=WEEK_CHOICES,
        null=True
    )
    is_far_east = models.BooleanField(verbose_name='Дальний Восток')
    is_out_of_project = models.BooleanField(
        verbose_name='Без созвонов с ПМ',
        default=False
    )
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)
    incomplete_team = models.ForeignKey(
        IncompleteTeam,
        on_delete=models.CASCADE,
        null=True
    )

    def time_to_json(self):
        times = ["08:00","08:30","09:00","09:30","10:00",
                 "10:30","11:00","11:30","12:00","12:30",
                 "13:00","13:30","14:00","14:30","15:00",
                 "15:30","16:00","16:30","17:00","17:30",
                 "18:00","18:30","19:00","19:30","20:00","20:30"]
        def to_dateime(time):
            return datetime.strptime(time,'%H:%M')
        if self.end_time_call and self.start_time_call:
            json_times = {
                time: 1 if (to_dateime(self.start_time_call) <= to_dateime(time) < to_dateime(self.end_time_call))
                else 0 for time in times
            }
            self.time_call = json_times


    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Ученик'
        verbose_name_plural = 'Ученики'


class Project(models.Model):
    name = models.CharField(max_length=256)
    project_manager = models.ForeignKey(Project_manager, on_delete=models.CASCADE)
    students = models.JSONField()
    teams = models.ManyToManyField(Team)

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'


class Student_distribution(models.Model):
    Student_distribution = models.CharField(max_length=256)

    def activate_button(self):
        return format_html('<a href="{}" class="button">Distribution</a>',
            reverse_lazy("admin:admin_make_distribution", args=[self.pk])
        )
    
    class Meta:
        verbose_name = 'Провести распределение в команду'
        verbose_name_plural = 'Провести распределение в команды'
