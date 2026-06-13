from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.transaction import Transaction
from app.schemas.transaction import TransactionResponse
from app.dependencies import get_current_family_id

router = APIRouter()


@router.get("/overview")
async def overview(
    family_id: str = Depends(get_current_family_id),
    db: AsyncSession = Depends(get_db),
):
    today = date.today()
    month_start = date(today.year, today.month, 1)
    if today.month == 12:
        month_end = date(today.year + 1, 1, 1)
    else:
        month_end = date(today.year, today.month + 1, 1)

    result = await db.execute(
        select(Transaction.type, func.sum(Transaction.amount))
        .where(
            Transaction.family_id == family_id, Transaction.is_deleted == False,
            Transaction.transaction_date >= month_start, Transaction.transaction_date < month_end,
        )
        .group_by(Transaction.type)
    )
    data = dict(result.all())
    expense = data.get("expense", 0)
    income = data.get("income", 0)

    reimburse_result = await db.execute(
        select(func.sum(Transaction.amount))
        .where(
            Transaction.family_id == family_id, Transaction.is_deleted == False,
            Transaction.reimbursement == "pending",
        )
    )
    pending_reimbursement = reimburse_result.scalar() or 0

    return {
        "code": 0, "message": "success",
        "data": {
            "month_income": float(income),
            "month_expense": float(expense),
            "month_balance": float(income - expense),
            "pending_reimbursement": float(pending_reimbursement),
        },
    }


@router.get("/recent")
async def recent(
    limit: int = Query(10, ge=1, le=50),
    family_id: str = Depends(get_current_family_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Transaction)
        .where(Transaction.family_id == family_id, Transaction.is_deleted == False)
        .order_by(Transaction.transaction_date.desc(), Transaction.created_at.desc())
        .limit(limit)
    )
    transactions = result.scalars().all()
    items = [TransactionResponse.model_validate(t) for t in transactions]
    return {"code": 0, "message": "success", "data": items}
