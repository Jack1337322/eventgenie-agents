from fastapi import APIRouter, HTTPException
from models.event import EventPlanRequest, BudgetCalculationRequest, MaestroRequest
from agents.planning_agent import PlanningAgent
from agents.finance_agent import FinanceAgent
from agents.maestro import MaestroAgent
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize agents (singleton-like pattern for MVP)
planning_agent = PlanningAgent()
finance_agent = FinanceAgent()
maestro_agent = MaestroAgent()

@router.post("/agents/planning/generate")
async def generate_event_plan(request: EventPlanRequest):
    """Generate event plan using Planning Agent"""
    try:
        logger.info(f"API: Received planning request for {request.event_name}")
        
        event_data = request.dict()
        result = await planning_agent.generate_event_plan(event_data)
        
        return result
        
    except Exception as e:
        logger.error(f"API error in planning: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agents/finance/calculate")
async def calculate_budget(request: BudgetCalculationRequest):
    """Calculate budget using Finance Agent"""
    try:
        logger.info(f"API: Received budget calculation request for {request.event_name}")
        
        event_data = request.dict()
        result = await finance_agent.calculate_budget(event_data)
        
        return result
        
    except Exception as e:
        logger.error(f"API error in finance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agents/maestro/process")
async def process_maestro_request(request: MaestroRequest):
    """Process request through Maestro Agent (orchestration)"""
    try:
        logger.info(f"API: Received maestro request from user {request.user_id}")
        
        result = await maestro_agent.process_request(
            user_id=request.user_id,
            message=request.message,
            context=request.context
        )
        
        return result
        
    except Exception as e:
        logger.error(f"API error in maestro: {e}")
        raise HTTPException(status_code=500, detail=str(e))

