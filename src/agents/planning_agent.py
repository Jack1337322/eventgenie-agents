from chains.planning_chain import PlanningChain
import logging

logger = logging.getLogger(__name__)

class PlanningAgent:
    """
    Planning Agent - generates event plans using GigaChat
    """
    
    def __init__(self):
        self.chain = PlanningChain()
        logger.info("Planning Agent initialized")
    
    async def generate_event_plan(self, event_data: dict) -> dict:
        """
        Generate a comprehensive event plan
        
        Args:
            event_data: Dictionary containing event information
            
        Returns:
            dict: Event plan with timeline, tasks, and recommendations
        """
        try:
            logger.info(f"Planning Agent: Generating plan for {event_data.get('event_name')}")
            
            result = await self.chain.generate_plan(event_data)
            
            logger.info("Planning Agent: Plan generated successfully")
            return result
            
        except Exception as e:
            logger.error(f"Planning Agent error: {e}")
            raise

