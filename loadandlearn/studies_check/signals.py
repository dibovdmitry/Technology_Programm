# store/signals.py
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.contrib import messages
from django.db.models import Count, Q
from .models import Teacher, TeacherLoad

@receiver(user_logged_in)
def assign_load_on_login(sender, user, request, **kwargs):
    print(f"--- СИГНАЛ СРАБОТАЛ для пользователя: {user.username} ---")
    try:
        current_teacher = Teacher.objects.select_related('department').get(user=user)
        
        if not current_teacher.department_id:
            print("--- У преподавателя нет кафедры, выходим ---")
            return

        dept_id = current_teacher.department_id
        print(f"--- Преподаватель ID {current_teacher.id}, Кафедра ID: {dept_id} ---")

        unassigned_loads = TeacherLoad.objects.filter(
            subject__department_id=dept_id, 
            teacher__isnull=True
        )

        count_new = 0
        if unassigned_loads.exists():
            for load in unassigned_loads:
                load.teacher = current_teacher
                load.is_assigned_auto = True
                load.save()
                count_new += 1
            print(f"--- Этап 1: Подобрано свободных предметов: {count_new} ---")

    
        my_load_count = TeacherLoad.objects.filter(teacher=current_teacher).count()

        richest_teacher_data = Teacher.objects.filter(department_id=dept_id) \
            .exclude(id=current_teacher.id) \
            .annotate(load_count=Count('teacherload')) \
            .order_by('-load_count') \
            .first()

        if richest_teacher_data:
            richest_count = richest_teacher_data.load_count
            
            if richest_count > my_load_count and richest_count > 1:
                
                amount_to_take = richest_count // 2 
                
                print(f"--- Нашел перегруженного коллегу (ID {richest_teacher_data.id}) с {richest_count} предметами. Забираю {amount_to_take}. ---")

                loads_to_steal = TeacherLoad.objects.filter(
                    teacher=richest_teacher_data,
                    subject__department_id=dept_id
                ).order_by('id')[:amount_to_take]

                count_stolen = 0
                for load in loads_to_steal:
                    load.teacher = current_teacher
                    load.is_assigned_auto = True
                    load.save()
                    count_stolen += 1

                total_assigned = count_new + count_stolen
                msg = f"Назначено новых: {count_new}. Перераспределено от коллег: {count_stolen}."
                messages.success(request, msg)
            else:
                print("--- Балансировка не требуется (у коллег нагрузка не сильно больше) ---")
                if count_new > 0:
                     messages.success(request, f"Взято свободных предметов: {count_new}")
        else:
            print("--- Коллег на кафедре не найдено ---")
            if count_new > 0:
                messages.success(request, f"Взято свободных предметов: {count_new}")

    except Teacher.DoesNotExist:
        pass
    except Exception as e:
        print(f"--- ОШИБКА: {e} ---")