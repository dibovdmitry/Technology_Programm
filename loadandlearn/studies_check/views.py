from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .forms import *
from .models import Department, StudentGroup, Student, Teacher, TeacherLoad, StudentLab
from .paginator import paginator
from .utils import verify_lab_with_ai

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseNotFound, Http404, JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, FormView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required


def studies_check(request):
    items = Item.objects.all()
    context = {
        'items': items,
        'page_obj': paginator(request, items, 12),
        'is_student': False,
        'is_teacher': False,
        'student_subjects': [],
        'student_labs': [],
        'teacher_load': [],
    }

    if request.user.is_authenticated:
        student_profile = Student.objects.filter(user=request.user).first()
        
        if student_profile:
            context['is_student'] = True
            context['student_subjects'] = TeacherLoad.objects.filter(
                group=student_profile.group
            ).select_related('subject', 'teacher')
            
            context['student_labs'] = StudentLab.objects.filter(
                student=student_profile
            )
            
            context['lab_range'] = range(1, 11)
            
        else:
            teacher_profile = Teacher.objects.filter(user=request.user).first()
            
            if teacher_profile:
                context['is_teacher'] = True
                loads = TeacherLoad.objects.filter(
                    teacher=teacher_profile
                ).select_related('subject', 'group')
                
                for load in loads:
                    load.students_in_group = Student.objects.filter(group=load.group)
                    for st in load.students_in_group:
                        st.labs = StudentLab.objects.filter(
                            student=st, 
                            teacher_load=load
                        ).order_by('lab_number')
                
                context['teacher_load'] = loads

    return render(request, 'studies_check/main_page.html', context)


def upload_lab(request, load_id, lab_number):
    if request.method == 'POST' and request.FILES.get('lab_file'):
        student = Student.objects.get(user=request.user)
        load = TeacherLoad.objects.get(id=load_id)
        lab_file = request.FILES['lab_file']
        
        lab, created = StudentLab.objects.update_or_create(
            student=student,
            teacher_load=load,
            lab_number=lab_number,
            defaults={'file_path': lab_file, 'status': 'Загружено'}
        )
        
        return redirect('studies_check:home')
    return redirect('studies_check:home')


def departments(request):
    departments_list = Department.objects.all()
    
    context = {
        'departments': departments_list, 
        'page_obj': paginator(request, departments_list, 3),
    }
    
    return render(request, 'studies_check/departments.html', context)


def department_detail(request, dept_slug):
    department = get_object_or_404(Department, slug=dept_slug)
    
    groups = StudentGroup.objects.filter(department=department)
    
    context = {
        'department': department,
        'groups': groups,
    }
    return render(request, 'studies_check/department_detail.html', context)





from django.shortcuts import render, redirect, get_object_or_404

from django.contrib import messages 
from .models import StudentLab

@login_required
def run_ai_check(request, lab_id):
    lab = get_object_or_404(StudentLab, id=lab_id)

    if not request.user.is_staff and lab.student.user != request.user:
        messages.error(request, "У вас нет прав на проверку этой работы.")
        return redirect('studies_check:home')

    if not lab.file_path:
        messages.warning(request, "Сначала загрузите файл, чтобы запустить проверку.")
        return redirect('studies_check:home')

    LAB_TOPICS = {
    "Практика речи": {
        1: "Тема: Монологическое высказывание. Требования: Использование вводных слов, связность текста, объем от 200 слов.",
        2: "Тема: Аргументация. Требования: Наличие тезиса, двух аргументов и вывода. Правильное использование времен.",
    },
    "Археология": {
        1: "Тема: Полевые исследования. Требования: Описание методов раскопок, фиксация находок, стратиграфия.",
        2: "Тема: Каменный век. Требования: Классификация орудий труда, описание материала (кремень, обсидиан).",
    },
    "Стилистика русского языка": {
        1: "Тема: Функциональные стили. Требования: Анализ научного стиля, выявление лексических и синтаксических особенностей.",
        2: "Тема: Публицистический стиль. Требования: Использование экспрессивной лексики, наличие риторических вопросов, авторская позиция.",
    },
    "Логика и критическое мышление": {
        1: "Тема: Законы логики. Требования: Определение типа силлогизма, проверка истинности посылок.",
        2: "Тема: Логические ошибки в аргументации. Требования: Выявление ошибок 'подмена тезиса' или 'после этого — значит вследствие этого'.",
    },
    "Фонетика современного русского языка": {
        1: "Тема: Транскрипция. Требования: Верная передача редукции гласных и ассимиляции согласных.",
        2: "Тема: Интонационные конструкции (ИК). Требования: Определение типа ИК в предложениях, разметка логического ударения.",
    },
    "Письменный технический перевод": {
        1: "Тема: Перевод инструкций. Требования: Соблюдение терминологического единства, отсутствие безличных конструкций.",
        2: "Тема: Перевод патентов и спецификаций. Требования: Точность передачи численных данных, использование безличных форм глагола.",
    },
    "Источниковедение": {
        1: "Тема: Классификация источников. Требования: Отличие нарративных источников от актовых.",
        2: "Тема: Внешняя критика источника. Требования: Установление подлинности документа, анализ материала письма и почерка.",
    },
    "Онтология и теория познания": {
        1: "Тема: Бытие и сущее. Требования: Разбор категорий Хайдеггера или Аристотеля, четкость определений.",
        2: "Тема: Проблема сознания и тела. Требования: Сравнение дуализма Декарта и современного функционализма.",
    },
}

    subject_name = lab.teacher_load.subject.name
    lab_number = lab.lab_number

    subject_instructions = LAB_TOPICS.get(subject_name, {})
    
    reference_knowledge = subject_instructions.get(
        lab_number, 
        f"Проверь работу по предмету '{subject_name}' на грамотность, структуру и наличие выводов."
    )

    try:
        ai_result = verify_lab_with_ai(lab.file_path.path, reference_knowledge)

        if ai_result:
            lab.ai_grade = ai_result.get('total', 0)
            lab.ai_review = ai_result.get('comment', 'Нет комментария')
            
            lab.score_tasks = ai_result.get('tasks', 0)
            lab.score_details = ai_result.get('details', 0)
            lab.score_conclusions = ai_result.get('conclusions', 0)
            
            lab.save()
            messages.success(request, f"Проверка завершена! Оценка ИИ: {lab.ai_grade}/5")
        else:
            messages.error(request, "ИИ не смог прочитать файл или произошла ошибка сервиса.")

    except Exception as e:
        print(f"Ошибка во views: {e}")
        messages.error(request, "Произошла внутренняя ошибка при обращении к ИИ.")

    return redirect('studies_check:home')
