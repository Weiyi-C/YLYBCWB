from pydantic import BaseModel, Field
from decimal import Decimal


class BudgetItem(BaseModel):
    category_id: str
    amount: Decimal = Field(ge=0, decimal_places=2)


class BudgetSetRequest(BaseModel):
    year_month: str = Field(pattern="^\\d{4}-\\d{2}$")
    items: list[BudgetItem]


class BudgetCategoryItem(BaseModel):
    category_id: str
    category_name: str
    budget: Decimal
    actual: Decimal
    remaining: Decimal
    ratio: float
    status: str  # normal / warning / exceeded


class BudgetResponse(BaseModel):
    year_month: str
    total_budget: Decimal
    total_actual: Decimal
    total_remaining: Decimal
    items: list[BudgetCategoryItem]
