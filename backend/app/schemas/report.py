from pydantic import BaseModel
from decimal import Decimal


class MonthlySummaryItem(BaseModel):
    month: str
    income: Decimal
    expense: Decimal
    balance: Decimal


class CategoryBreakdownItem(BaseModel):
    category_id: str
    category_name: str
    amount: Decimal
    ratio: float
    count: int


class FundSourceBreakdownItem(BaseModel):
    fund_source_id: str
    fund_source_name: str
    amount: Decimal
    ratio: float


class TrendItem(BaseModel):
    month: str
    income: Decimal
    expense: Decimal


class MemberComparisonItem(BaseModel):
    member_id: str
    member_name: str
    total_expense: Decimal
    transaction_count: int


class NecessityAnalysisItem(BaseModel):
    necessity: str
    amount: Decimal
    ratio: float
    count: int
