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
      "description": "Краткое описание"
    }}
  ],
  "total_amount": 1500000,
  "analysis": "Краткий анализ бюджета",
  "recommendations": [
    "Рекомендация 1",
    "Рекомендация 2"
  ]
}}

ВАЖНО:
- Используй КРАТКИЕ описания (до 50 символов) для экономии токенов
- Убедись, что JSON полностью закрыт (все скобки закрыты)
- Верни ТОЛЬКО валидный JSON без дополнительного текста
"""

class BudgetChain:
    """LangChain chain for budget calculation"""
    
    def __init__(self):
        # Increased max_tokens to prevent JSON truncation
        self.gigachat = GigaChatClient(temperature=0.3, max_tokens=4000)
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
        import json  # Import at function start to avoid scope issues
        
        try:
            logger.info(f"Calculating budget for event: {event_data.get('event_name')}")
            logger.info(f"Event data: {event_data}")
            
            # Prepare input
            input_data = {
                "event_name": event_data.get("event_name", ""),
                "event_type": event_data.get("event_type", ""),
                "event_date": event_data.get("event_date", ""),
                "location": event_data.get("location", ""),
                "expected_guests": event_data.get("expected_guests", 0),
                "budget_limit": event_data.get("budget_limit", 0)
            }
            
            logger.info(f"Calling GigaChat with input: {input_data}")
            
            # Generate using chain
            result = await self.chain.ainvoke(input_data)
            
            logger.info(f"GigaChat response received. Result type: {type(result)}")
            
            # Parse JSON response
            response_text = ""
            
            # Handle different response formats from LangChain
            if isinstance(result, dict):
                logger.info(f"Result keys: {result.keys()}")
                # Try different possible keys
                response_text = result.get("text", "") or result.get("output", "") or result.get("result", "")
                # If still empty, try to get the first value that's a string
                if not response_text:
                    for key, value in result.items():
                        if isinstance(value, str) and len(value) > 10:
                            response_text = value
                            logger.info(f"Using value from key '{key}' as response text")
                            break
            elif isinstance(result, str):
                response_text = result
                logger.info("Result is a string, using directly")
            else:
                # Try to convert to string
                response_text = str(result)
                logger.info(f"Result is {type(result)}, converted to string")
            
            if not response_text:
                logger.error(f"Empty response from GigaChat. Result: {result}")
                logger.warning("Using fallback budget")
                return self._fallback_budget(event_data)
            
            logger.info(f"Raw response text length: {len(response_text)}")
            logger.debug(f"Raw response text (first 500 chars): {response_text[:500]}")
            
            # Clean JSON response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            # Try to fix truncated JSON
            response_text = self._fix_truncated_json(response_text)
            
            logger.info("Parsing JSON response from GigaChat")
            parsed_result = json.loads(response_text)
            logger.info("Budget calculated successfully from GigaChat")
            return parsed_result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Response text that failed to parse: {response_text[:1000] if 'response_text' in locals() else 'N/A'}")
            # Try to recover partial JSON
            try:
                recovered_json = self._recover_partial_json(response_text)
                if recovered_json:
                    logger.info("Successfully recovered partial JSON from truncated response")
                    return recovered_json
            except Exception as recovery_error:
                logger.warning(f"Failed to recover JSON: {recovery_error}")
            
            logger.warning("Falling back to default budget calculation")
            return self._fallback_budget(event_data)
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error calculating budget: {e}", exc_info=True)
            
            # Check for 403 Forbidden error
            if "403" in error_msg or "Forbidden" in error_msg or "unauthorized" in error_msg.lower():
                logger.error("GigaChat API returned 403 Forbidden. Possible causes:")
                logger.error("1. Invalid GIGACHAT_CLIENT_ID or GIGACHAT_CLIENT_SECRET")
                logger.error("2. Incorrect scope (should be GIGACHAT_API_PERS)")
                logger.error("3. Token expired or invalid")
                logger.error("4. Insufficient permissions for the API key")
                raise RuntimeError(
                    "GigaChat API authentication failed (403 Forbidden). "
                    "Please check your GIGACHAT_CLIENT_ID and GIGACHAT_CLIENT_SECRET credentials. "
                    "Ensure they are valid and have the correct permissions."
                )
            
            logger.warning("Falling back to default budget calculation")
            # Return fallback budget
            return self._fallback_budget(event_data)
    
    def _fix_truncated_json(self, json_text: str) -> str:
        """Try to fix truncated JSON by closing unclosed structures"""
        if not json_text:
            return json_text
        
        result = json_text
        
        # Close unclosed strings (if JSON was cut in the middle of a string)
        if result.count('"') % 2 != 0:
            # Find the last unclosed quote and close the string
            last_quote_pos = result.rfind('"')
            if last_quote_pos > 0:
                # Check if it's inside a description field
                before_quote = result[:last_quote_pos]
                if '"description"' in before_quote or '"category"' in before_quote:
                    # Close the string
                    result = result[:last_quote_pos + 1] + '"'
        
        # Count open brackets/braces after fixing strings
        open_braces = result.count('{')
        close_braces = result.count('}')
        open_brackets = result.count('[')
        close_brackets = result.count(']')
        
        # If JSON seems complete, return as is
        if open_braces == close_braces and open_brackets == close_brackets:
            return result
        
        # Close unclosed arrays
        while open_brackets > close_brackets:
            result += ']'
            close_brackets += 1
        
        # Close unclosed objects
        while open_braces > close_braces:
            result += '}'
            close_braces += 1
        
        return result
    
    def _recover_partial_json(self, json_text: str) -> dict:
        """Try to recover partial JSON by extracting valid items"""
        import re
        
        try:
            # Try to extract items array
            items_match = re.search(r'"items"\s*:\s*\[(.*?)\]', json_text, re.DOTALL)
            if items_match:
                items_text = items_match.group(1)
                # Extract individual items
                items = []
                item_pattern = r'\{\s*"category"\s*:\s*"([^"]+)"\s*,\s*"planned_amount"\s*:\s*(\d+)\s*,\s*"description"\s*:\s*"([^"]*)"'
                
                for match in re.finditer(item_pattern, items_text):
                    category = match.group(1)
                    amount = float(match.group(2))
                    description = match.group(3) if match.group(3) else ""
                    items.append({
                        "category": category,
                        "planned_amount": amount,
                        "description": description
                    })
                
                if items:
                    # Calculate total
                    total = sum(item["planned_amount"] for item in items)
                    
                    return {
                        "items": items,
                        "total_amount": total,
                        "analysis": "Частично восстановленный бюджет из обрезанного ответа GigaChat",
                        "recommendations": [
                            "Ответ был обрезан, некоторые категории могут отсутствовать",
                            "Проверьте расчет бюджета вручную"
                        ]
                    }
        except Exception as e:
            logger.debug(f"Failed to recover partial JSON: {e}")
        
        return None
    
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
