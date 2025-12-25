import os
from gigachat import GigaChat
import json

class BudgetChain:
    def __init__(self):
        auth_key = os.getenv("GIGACHAT_AUTH_KEY")
        scope = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")

        if not auth_key:
            raise RuntimeError("GIGACHAT_AUTH_KEY не задан в переменных окружения")

        self.client = GigaChat(
            credentials=auth_key,
            scope=scope,
            verify_ssl_certs=False,
        )

    async def calculate_budget(self, event_data: dict) -> dict:
        event_name = event_data.get("event_name", "Event")
        guests = event_data.get("guests", 0)
        total_budget = event_data.get("budget_total", 0)

        prompt = f"""
Ты финансовый аналитик для организации мероприятий.
У тебя есть данные о событии:

- Название: {event_name}
- Количество гостей: {guests}
- Общий бюджет (в рублях): {total_budget}
- Доп. данные: {json.dumps(event_data, ensure_ascii=False)}

Распредели бюджет по основным категориям:
- venue (площадка)
- catering (еда и напитки)
- entertainment (развлекательная программа)
- other (прочие расходы)

Требования к ответу:
- строго верни JSON без пояснительного текста;
- сумма по всем категориям НЕ должна превышать общий бюджет;
- структура ответа:

{{
  "event_name": "...",
  "total_budget": число,
  "guests": число,
  "items": [
    {{
      "category": "venue",
      "amount": число,
      "description": "краткое описание"
    }},
    ...
  ],
  "analysis": "краткий анализ распределения бюджета",
  "recommendations": [
    "рекомендация 1",
    "рекомендация 2"
  ]
}}
"""

        response = self.client.chat(prompt)
        raw_content = response.choices[0].message.content

        cleaned = raw_content.strip()
        if cleaned.startswith("```
            cleaned = cleaned.strip("`")
            cleaned = cleaned.replace("json", "", 1).strip()

        data = json.loads(cleaned)
        return data
