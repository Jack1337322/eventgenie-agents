from pydantic import BaseModel
from typing import List
from decimal import Decimal

class BudgetItem(BaseModel):
    category: str
    planned_amount: Decimal
    description: str = ""
    
    class Config:
        json_schema_extra = {
            "example": {
                "category": "Аренда площадки",
                "planned_amount": 350000,
                "description": "Конференц-зал на 500 человек"
            }
        }

class BudgetResponse(BaseModel):
    items: List[BudgetItem]
    total_amount: Decimal
    analysis: str = ""
    recommendations: List[str] = []

