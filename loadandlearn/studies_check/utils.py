from django.db.models import Count
from django.core.cache import cache

from .models import *
import openai
from openai import OpenAI
import docx2txt
import json
import os
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def verify_lab_with_ai(file_path, reference_knowledge):
    try:
        lab_content = docx2txt.process(file_path)
        
        prompt = f"""
        Ты — экспертный преподаватель. Проверь лабораторную работу студента.
        
        ЭТАЛОННЫЕ ТРЕБОВАНИЯ:
        {reference_knowledge}
        
        ТЕКСТ РАБОТЫ СТУДЕНТА:
        {lab_content}
        
        ОЦЕНИ работу по шкале от 0 до 5 по критериям:
        1. Выполненные задания
        2. Подробные описания действий
        3. Верные выводы на основе работы
        
        ВЕРНИ ответ строго в формате JSON:
        {{
            "tasks": 0,
            "details": 0,
            "conclusions": 0,
            "total": 0,
            "comment": "короткая рецензия"
        }}
        """

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ты помощник, который возвращает только чистый JSON."},
                {"role": "user", "content": prompt}
            ],
            response_format={ "type": "json_object" }
        )

        result_text = response.choices[0].message.content
        return json.loads(result_text)

    except Exception as e:
        print(f"Ошибка OpenAI: {e}")
        return None

menu = [{'title': "О сайте", 'url_name': 'about'},
        {'title': "Обратная связь", 'url_name': 'contact'},
]


