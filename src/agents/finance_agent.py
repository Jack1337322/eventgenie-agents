from chains.budget_chain import BudgetChain
import logging

logger = logging.getLogger(__name__)

class FinanceAgent:
    """
    Finance Agent - calculates budgets using GigaChat
    """
    
    def __init__(self):
        self.chain = BudgetChain()
        logger.info("Finance Agent initialized")
    
    async def calculate_budget(self, event_data: dict) -> dict:
        """
        Calculate event budget
        
        Args:
            event_data: Dictionary containing event information
            
        Returns:
            dict: Budget with items, total, analysis, and recommendations
        """
        try:
            logger.info(f"Finance Agent: Calculating budget for {event_data.get('event_name')}")
            
            result = await self.chain.calculate_budget(event_data)
            
            logger.info("Finance Agent: Budget calculated successfully")
            return result
            
        except Exception as e:
            logger.error(f"Finance Agent error: {e}")
            raise

