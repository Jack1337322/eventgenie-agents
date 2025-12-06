from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from llm.gigachat_client import GigaChatClient
import logging

logger = logging.getLogger(__name__)

PLANNING_PROMPT_TEMPLATE = """Ты - эксперт по планированию мероприятий. Создай детальный план события.

ИНФОРМАЦИЯ О СОБЫТИИ:
- Название: {event_name}
- Тип события: {event_type}
- Дата: {event_date}
- Место проведения: {location}
- Ожидаемое количество гостей: {expected_guests}
- Бюджет: {budget} рублей
- Целевая аудитория: {target_audience}
- Формат: {format}

ЗАДАЧА:
1. Создай детальный таймлайн мероприятия с указанием времени
2. Раздели на основные фазы (регистрация, основная программа, перерывы, закрытие)
3. Создай список конкретных задач для подготовки
4. Укажи приоритеты задач
5. Определи критический путь подготовки

ФОРМАТ ОТВЕТА (JSON):
{{
  "timeline_phases": [
    {{
      "time": "09:00 - 10:00",
      "activity": "Регистрация участников",
      "description": "Приветственный кофе, выдача бейджей"
    }}
  ],
  "tasks": [
    {{
      "title": "Забронировать площадку",
      "priority": "HIGH",
      "deadline_days": 60,
      "description": "Забронировать конференц-зал"
    }}
  ],
  "critical_path": ["Площадка", "Программа", "Кейтеринг"],
  "recommendations": [
    "Рекомендация 1",
    "Рекомендация 2"
  ]
}}

Создай реалистичный и детальный план на русском языке. Верни ТОЛЬКО JSON без дополнительного текста.
"""

class PlanningChain:
    """LangChain chain for event planning"""
    
    def __init__(self):
        self.gigachat = GigaChatClient(temperature=0.5, max_tokens=3000)
        self.chain = self._create_chain()
    
    def _create_chain(self) -> LLMChain:
        prompt = PromptTemplate(
            input_variables=[
                "event_name", "event_type", "event_date", "location",
                "expected_guests", "budget", "target_audience", "format"
            ],
            template=PLANNING_PROMPT_TEMPLATE
        )
        return LLMChain(llm=self.gigachat.llm, prompt=prompt)
    
    async def generate_plan(self, event_data: dict) -> dict:
        """Generate event plan using GigaChat"""
        try:
            logger.info(f"Generating plan for event: {event_data.get('event_name')}")
            
            # Prepare input
            input_data = {
                "event_name": event_data.get("event_name", ""),
                "event_type": event_data.get("event_type", ""),
                "event_date": event_data.get("event_date", ""),
                "location": event_data.get("location", ""),
                "expected_guests": event_data.get("expected_guests", 0),
                "budget": event_data.get("budget", 0),
                "target_audience": event_data.get("target_audience", "Не указано"),
                "format": event_data.get("format", "")
            }
            
            # Generate using chain
            result = await self.chain.ainvoke(input_data)
            
            logger.info("Event plan generated successfully")
            
            # Parse JSON response
            import json
            response_text = result.get("text", "")
            
            # Clean JSON response (remove markdown code blocks if present)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            return json.loads(response_text)
            
        except Exception as e:
            logger.error(f"Error generating plan: {e}")
            # Return fallback plan
            return self._fallback_plan(event_data)
    
    def _fallback_plan(self, event_data: dict) -> dict:
        """Fallback plan if LLM fails"""
        return {
            "timeline_phases": [
                {"time": "09:00 - 10:00", "activity": "Регистрация участников"},
                {"time": "10:00 - 12:00", "activity": "Основная программа"},
                {"time": "12:00 - 13:00", "activity": "Обед"},
                {"time": "13:00 - 17:00", "activity": "Продолжение программы"},
            ],
            "tasks": [
                {"title": "Забронировать площадку", "priority": "HIGH", "deadline_days": 60},
                {"title": "Согласовать программу", "priority": "HIGH", "deadline_days": 45},
                {"title": "Заключить договор с кейтерингом", "priority": "MEDIUM", "deadline_days": 30},
            ],
            "critical_path": ["Площадка", "Программа", "Кейтеринг"],
            "recommendations": ["Начните подготовку за 2-3 месяца"]
        }

