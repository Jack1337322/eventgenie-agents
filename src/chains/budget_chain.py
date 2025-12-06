from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from llm.gigachat_client import GigaChatClient
import logging

logger = logging.getLogger(__name__)

BUDGET_PROMPT_TEMPLATE = """Ты - эксперт по финансовому планированию мероприятий. Рассчитай детальную смету события.

ИНФОРМАЦИЯ О СОБЫТИИ:
- Название: {event_name}
- Тип события: {event_type}
- Дата: {event_date}
- Место проведения: {location}
- Ожидаемое количество гостей: {expected_guests}
- Лимит бюджета: {budget_limit} рублей

ЗАДАЧА:
1. Создай детальную смету по категориям
2. Рассчитай реалистичные суммы для каждой статьи расходов
3. Убедись, что итоговая сумма не превышает лимит бюджета
4. Дай рекомендации по оптимизации бюджета

ОСНОВНЫЕ КАТЕГОРИИ:
- Аренда площадки
- Кейтеринг (питание)
- Техническое обеспечение (звук, свет, проекторы)
- Декорации и оформление
- Фото/видео съемка
- Маркетинг и реклама
- Подарки и сувениры
- Персонал и координаторы
- Транспорт (если необходимо)
- Резерв (10% от общего бюджета)

ФОРМАТ ОТВЕТА (JSON):
{{
  "items": [
    {{
      "category": "Аренда площадки",
      "planned_amount": 350000,
      "description": "Конференц-зал на 500 человек, 8 часов"
    }}
  ],
  "total_amount": 1500000,
  "analysis": "Краткий анализ бюджета",
  "recommendations": [
    "Рекомендация по оптимизации 1",
    "Рекомендация по оптимизации 2"
  ]
}}

Рассчитай реалистичную смету на русском языке. Верни ТОЛЬКО JSON без дополнительного текста.
"""

class BudgetChain:
    """LangChain chain for budget calculation"""
    
    def __init__(self):
        self.gigachat = GigaChatClient(temperature=0.3, max_tokens=2000)
        self.chain = self._create_chain()
    
    def _create_chain(self) -> LLMChain:
        prompt = PromptTemplate(
            input_variables=[
                "event_name", "event_type", "event_date", "location",
                "expected_guests", "budget_limit"
            ],
            template=BUDGET_PROMPT_TEMPLATE
        )
        return LLMChain(llm=self.gigachat.llm, prompt=prompt)
    
    async def calculate_budget(self, event_data: dict) -> dict:
        """Calculate budget using GigaChat"""
        try:
            logger.info(f"Calculating budget for event: {event_data.get('event_name')}")
            
            # Prepare input
            input_data = {
                "event_name": event_data.get("event_name", ""),
                "event_type": event_data.get("event_type", ""),
                "event_date": event_data.get("event_date", ""),
                "location": event_data.get("location", ""),
                "expected_guests": event_data.get("expected_guests", 0),
                "budget_limit": event_data.get("budget_limit", 0)
            }
            
            # Generate using chain
            result = await self.chain.ainvoke(input_data)
            
            logger.info("Budget calculated successfully")
            
            # Parse JSON response
            import json
            response_text = result.get("text", "")
            
            # Clean JSON response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            return json.loads(response_text)
            
        except Exception as e:
            logger.error(f"Error calculating budget: {e}")
            # Return fallback budget
            return self._fallback_budget(event_data)
    
    def _fallback_budget(self, event_data: dict) -> dict:
        """Fallback budget if LLM fails"""
        guests = event_data.get("expected_guests", 100)
        budget_limit = float(event_data.get("budget_limit", 1000000))
        
        # Simple calculation based on guests
        venue = budget_limit * 0.25
        catering = guests * 2500
        tech = budget_limit * 0.15
        decoration = budget_limit * 0.10
        photo = budget_limit * 0.10
        marketing = budget_limit * 0.12
        gifts = guests * 500
        staff = budget_limit * 0.08
        reserve = budget_limit * 0.10
        
        items = [
            {"category": "Аренда площадки", "planned_amount": venue, "description": "Конференц-зал"},
            {"category": "Кейтеринг", "planned_amount": catering, "description": f"Питание для {guests} человек"},
            {"category": "Техническое обеспечение", "planned_amount": tech, "description": "Звук, свет, проекторы"},
            {"category": "Декорации и оформление", "planned_amount": decoration, "description": "Оформление зала"},
            {"category": "Фото/видео съемка", "planned_amount": photo, "description": "Фотограф и видеооператор"},
            {"category": "Маркетинг и реклама", "planned_amount": marketing, "description": "Реклама и продвижение"},
            {"category": "Подарки и сувениры", "planned_amount": gifts, "description": f"Сувениры для {guests} человек"},
            {"category": "Персонал и координаторы", "planned_amount": staff, "description": "Координаторы и хостес"},
            {"category": "Резерв", "planned_amount": reserve, "description": "Резервный фонд"}
        ]
        
        total = sum(item["planned_amount"] for item in items)
        
        return {
            "items": items,
            "total_amount": total,
            "analysis": "Базовый расчет сметы на основе стандартных коэффициентов",
            "recommendations": [
                "Рассмотрите возможность сокращения бюджета на декорации",
                "Договоритесь с подрядчиками заранее для получения скидок"
            ]
        }

