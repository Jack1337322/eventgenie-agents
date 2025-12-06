from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

class EventPlanRequest(BaseModel):
    event_name: str
    event_type: str
    event_date: str
    location: str
    expected_guests: int
    budget: Decimal
    target_audience: Optional[str] = None
    format: str  # offline, online, hybrid
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_name": "Конференция TechSummit 2025",
                "event_type": "conference",
                "event_date": "2025-12-15T09:00:00",
                "location": "Крокус Экспо, Павильон 1",
                "expected_guests": 500,
                "budget": 1500000,
                "target_audience": "IT-специалисты, предприниматели",
                "format": "hybrid"
            }
        }

class BudgetCalculationRequest(BaseModel):
    event_name: str
    event_type: str
    event_date: str
    location: str
    expected_guests: int
    budget_limit: Decimal
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_name": "Конференция TechSummit 2025",
                "event_type": "conference",
                "event_date": "2025-12-15T09:00:00",
                "location": "Крокус Экспо, Павильон 1",
                "expected_guests": 500,
                "budget_limit": 1500000
            }
        }

class MaestroRequest(BaseModel):
    user_id: str
    message: str
    context: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user-123",
                "message": "Создай план свадьбы на 150 человек 15 апреля",
                "context": {}
            }
        }

