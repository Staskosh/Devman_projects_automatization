from django.db import models


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
    end_time_call = models.TimeField(verbose_name='Время окончания созвона')

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'


class Student(models.Model):
    WEEK_CHOICES = [('Третья', 3), ('Четвертая', 4)]
    
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
    start_time_call = models.JSONField(verbose_name='Время начала созвона')
    week = models.PositiveIntegerField(
        verbose_name='Выбранная неделя занятий',
        choices=WEEK_CHOICES,
        null=True
    )
    is_far_east = models.BooleanField(verbose_name='Дальний Восток')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Ученик'
        verbose_name_plural = 'Ученики'


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

    class Meta:
        verbose_name = 'Провести распределение в команды'
