from agents.planning_agent import PlanningAgent
from agents.finance_agent import FinanceAgent
from llm.gigachat_client import GigaChatClient
import logging
import json

logger = logging.getLogger(__name__)

class MaestroAgent:
    """
    Maestro Agent - orchestrates other agents based on user intent
    """
    
    def __init__(self):
        self.gigachat = GigaChatClient(temperature=0.5)
        self.planning_agent = PlanningAgent()
        self.finance_agent = FinanceAgent()
        logger.info("Maestro Agent initialized")
    
    async def process_request(self, user_id: str, message: str, context: dict = None) -> dict:
        """
        Process user request by classifying intent and routing to appropriate agents
        
        Args:
            user_id: User identifier
            message: User message
            context: Optional context dictionary
            
        Returns:
            dict: Response from appropriate agent(s)
        """
        try:
            logger.info(f"Maestro: Processing request from user {user_id}")
            
            # Classify intent
            intent = await self._classify_intent(message)
            logger.info(f"Maestro: Detected intent: {intent}")
            
            # Route to appropriate agent(s)
            if intent == "create_event_plan":
                # Extract event data from message (simplified for MVP)
                event_data = self._extract_event_data(message, context)
                result = await self.planning_agent.generate_event_plan(event_data)
                return {
                    "intent": intent,
                    "confidence": 0.95,
                    "agents_used": ["planning"],
                    "results": result
                }
            
            elif intent == "calculate_budget":
                # Extract event data from message
                event_data = self._extract_event_data(message, context)
                result = await self.finance_agent.calculate_budget(event_data)
                return {
                    "intent": intent,
                    "confidence": 0.95,
                    "agents_used": ["finance"],
                    "results": result
                }
            
            elif intent == "full_event_planning":
                # Use both agents in parallel
                event_data = self._extract_event_data(message, context)
                
                # Run agents (in MVP, we'll run sequentially, can be parallelized later)
                plan_result = await self.planning_agent.generate_event_plan(event_data)
                budget_result = await self.finance_agent.calculate_budget(event_data)
                
                return {
                    "intent": intent,
                    "confidence": 0.95,
                    "agents_used": ["planning", "finance"],
                    "results": {
                        "plan": plan_result,
                        "budget": budget_result
                    }
                }
            
            else:
                # Default response
                return {
                    "intent": "unknown",
                    "confidence": 0.0,
                    "agents_used": [],
                    "results": {
                        "message": "Не удалось определить намерение. Попробуйте переформулировать запрос."
                    }
                }
                
        except Exception as e:
            logger.error(f"Maestro error: {e}")
            raise
    
    async def _classify_intent(self, message: str) -> str:
        """Classify user intent using GigaChat"""
        prompt = f"""Классифицируй намерение пользователя в следующем сообщении.

Сообщение: "{message}"

Возможные намерения:
- create_event_plan: пользователь хочет создать план события
- calculate_budget: пользователь хочет рассчитать смету/бюджет
- full_event_planning: пользователь хочет и план, и смету
- unknown: не удается определить намерение

Верни ТОЛЬКО одно слово - название намерения, без дополнительного текста.
"""
        
        try:
            response = await self.gigachat.agenerate(prompt)
            intent = response.strip().lower()
            
            # Validate intent
            valid_intents = ["create_event_plan", "calculate_budget", "full_event_planning", "unknown"]
            if intent not in valid_intents:
                # Default to full_event_planning if mentions both or unclear
                if "план" in message.lower() and "смет" in message.lower():
                    return "full_event_planning"
                elif "план" in message.lower():
                    return "create_event_plan"
                elif "смет" in message.lower() or "бюджет" in message.lower():
                    return "calculate_budget"
                else:
                    return "unknown"
            
            return intent
            
        except Exception as e:
            logger.error(f"Intent classification error: {e}")
            # Fallback to keyword matching
            message_lower = message.lower()
            if "план" in message_lower and ("смет" in message_lower or "бюджет" in message_lower):
                return "full_event_planning"
            elif "план" in message_lower:
                return "create_event_plan"
            elif "смет" in message_lower or "бюджет" in message_lower:
                return "calculate_budget"
            else:
                return "unknown"
    
    def _extract_event_data(self, message: str, context: dict = None) -> dict:
        """Extract event data from message and context (simplified for MVP)"""
        # In MVP, we expect event data to be passed in context
        # In production, this would use NER and entity extraction
        if context and "event_data" in context:
            return context["event_data"]
        
        # Fallback: return empty dict (agents will handle with defaults)
        return {
            "event_name": "Новое событие",
            "event_type": "conference",
            "event_date": "2025-12-31",
            "location": "Москва",
            "expected_guests": 100,
            "budget": 1000000,
            "budget_limit": 1000000
        }

