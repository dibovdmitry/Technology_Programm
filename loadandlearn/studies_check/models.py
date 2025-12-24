from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Department(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Название кафедры")
    slug = models.SlugField(max_length=50, unique=True)
    head_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Зав. кафедрой")

    class Meta:
        db_table = 'Department'
        verbose_name = 'Кафедра'
        verbose_name_plural = 'Кафедры'

    def __str__(self):
        return self.name


class StudentGroup(models.Model):
    name = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name="Название Группы"
    )
    
    department = models.ForeignKey(
        'Department',
        on_delete=models.CASCADE,
        db_column='department_id', 
        verbose_name="Кафедра"
    )
    
    course = models.IntegerField(
        default=1, 
        verbose_name="Курс"
    )
    code = models.CharField(
        max_length=100, 
        null=True, 
        blank=True,
        verbose_name="Сокращенное название"
    )
    slug = models.SlugField(max_length=100, default = 'NULL')
    
    class Meta:
        db_table = 'StudentGroup' 
        verbose_name = 'Учебная Группа'
        verbose_name_plural = 'Учебные Группы'

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Название дисциплины")
    code = models.CharField(max_length=10, unique=True, verbose_name="Код дисциплины")
    department = models.ForeignKey(
        'Department', 
        on_delete=models.CASCADE, 
        related_name='subjects', 
        verbose_name="Кафедра",
        default=0
    )

    class Meta:
        db_table = 'Subject'
        managed = False
        verbose_name = 'Дисциплина'
        verbose_name_plural = 'Дисциплины'

    def __str__(self):
        return self.name


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    position = models.CharField(max_length=100, verbose_name="Должность", default="Преподаватель")
    salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Зарплата", default=0.00)
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, verbose_name="Кафедра")
    full_name = models.CharField(max_length=255, verbose_name="ФИО преподавателя")

    class Meta:
        db_table = 'Teacher'
        managed = False
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'
        
    def __str__(self):
        return f"{self.full_name} - {self.position}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Teacher.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.teacher.save()
    except Teacher.DoesNotExist:
        Teacher.objects.create(user=instance)


class TeacherLoad(models.Model):
    teacher = models.ForeignKey(
        'Teacher', 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Преподаватель",
        db_column='teacher_id'
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name="Дисциплина")
    group = models.ForeignKey(
        'StudentGroup', 
        on_delete=models.CASCADE, 
        verbose_name="Группа/Поток",
        db_column='group_id'
    )
    
    hours_lecture = models.IntegerField(default=0, verbose_name="Часы лекций")
    hours_practice = models.IntegerField(default=0, verbose_name="Часы практики")
    semester = models.CharField(max_length=50, verbose_name="Семестр", default="1 Семестр")
    is_assigned_auto = models.BooleanField(default=False, verbose_name="Назначено автоматически")

    class Meta:
        db_table = 'TeacherLoad'
        managed = False
        verbose_name = 'Назначение нагрузки'
        verbose_name_plural = 'Назначения нагрузки'

    def total_hours(self):
        return self.hours_lecture + self.hours_practice
    
    def __str__(self):
        teacher_name = self.teacher.user.username if self.teacher else "Не назначен"
        return f"{teacher_name} - {self.subject.name}"

from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    full_name = models.CharField(
        max_length=255, 
        verbose_name="Полное имя"
    )
    group = models.ForeignKey(
        'StudentGroup', 
        on_delete=models.CASCADE, 
        related_name='students',
        verbose_name="Группа"
    )
    enrollment_year = models.IntegerField(
        default=2025, 
        verbose_name="Год поступления"
    )
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        verbose_name="Пользователь"
    )

    class Meta:
        db_table = 'Student'
        managed = False
        verbose_name = "Студент"
        verbose_name_plural = "Студенты"

    def __str__(self):
        return f"{self.full_name} ({self.group.name})"

class StudentLab(models.Model):
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    teacher_load = models.ForeignKey('TeacherLoad', on_delete=models.CASCADE)
    lab_number = models.IntegerField()
    file_path = models.FileField(upload_to='labs/', null=True, blank=True)
    status = models.CharField(max_length=20, default='Ожидает')
    ai_grade = models.IntegerField(null=True, blank=True, verbose_name="Оценка ИИ")
    ai_review = models.TextField(null=True, blank=True, verbose_name="Комментарий ИИ")
    
    score_tasks = models.IntegerField(default=0)
    score_details = models.IntegerField(default=0)
    score_conclusions = models.IntegerField(default=0)

    class Meta:
        db_table = 'StudentLab'
        managed = False
