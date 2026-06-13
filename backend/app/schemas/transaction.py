from pydantic import BaseModel, Field
from datetime import date, time, datetime
from decimal import Decimal


class TransactionCreate(BaseModel):
    transaction_date: date
    transaction_time: time | None = None
    type: str = Field(pattern="^(expense|income)$")
    amount: Decimal = Field(gt=0, decimal_places=2)
    description: str = Field(min_length=1, max_length=200)
    merchant: str | None = Field(None, max_length=100)
    category_id: str
    sub_category_id: str
    payment_method_id: str | None = None
    fund_source_id: str | None = None
    reimbursement: str | None = Field("none", pattern="^(none|pending|reimbursed)$")
    necessity: str | None = Field(None, pattern="^(necessary|needed|wanted)$")
    is_recurring: bool = False
    notes: str | None = None
    member_id: str | None = None


class TransactionUpdate(BaseModel):
    transaction_date: date | None = None
    transaction_time: time | None = None
    type: str | None = Field(None, pattern="^(expense|income)$")
    amount: Decimal | None = Field(None, gt=0, decimal_places=2)
    description: str | None = Field(None, min_length=1, max_length=200)
    merchant: str | None = None
    category_id: str | None = None
    sub_category_id: str | None = None
    payment_method_id: str | None = None
    fund_source_id: str | None = None
    reimbursement: str | None = Field(None, pattern="^(none|pending|reimbursed)$")
    necessity: str | None = None
    is_recurring: bool | None = None
    notes: str | None = None
    member_id: str | None = None


class TransactionResponse(BaseModel):
    id: str
    family_id: str
    creator_id: str
    member_id: str
    transaction_date: date
    transaction_time: time | None
    type: str
    amount: Decimal
    description: str
    merchant: str | None
    category_id: str
    sub_category_id: str
    payment_method_id: str | None
    fund_source_id: str | None
    reimbursement: str
    necessity: str | None
    is_recurring: bool
    notes: str | None
    attachments: list | None
    is_deleted: bool
    created_at: datetime
    updated_at: datetime
    category_name: str | None = None
    sub_category_name: str | None = None
    member_name: str | None = None

    class Config:
        from_attributes = True
