from decimal import Decimal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.budget import Budget
from app.models.transaction import Transaction
from app.models.category import Category
from app.schemas.budget import BudgetSetRequest, BudgetResponse, BudgetCategoryItem
from app.dependencies import get_current_family_id
from datetime import date

router = APIRouter()


@router.get("")
async def get_budgets(
    year_month: str = Query(..., pattern="^\\d{4}-\\d{2}$"),
    family_id: str = Depends(get_current_family_id),
    db: AsyncSession = Depends(get_db),
):
    year, month = year_month.split("-")
    date_from = date(int(year), int(month), 1)
    if int(month) == 12:
        date_to = date(int(year) + 1, 1, 1)
    else:
        date_to = date(int(year), int(month) + 1, 1)

    budget_result = await db.execute(
        select(Budget).where(Budget.family_id == family_id, Budget.year_month == year_month)
    )
    budgets = {b.category_id: b for b in budget_result.scalars().all()}

    cat_result = await db.execute(
        select(Category).where(Category.family_id == family_id, Category.type == "expense", Category.is_active == True)
    )
    categories = cat_result.scalars().all()

    actual_result = await db.execute(
        select(Transaction.category_id, func.sum(Transaction.amount))
        .where(
            Transaction.family_id == family_id,
            Transaction.type == "expense",
            Transaction.is_deleted == False,
            Transaction.transaction_date >= date_from,
            Transaction.transaction_date < date_to,
        )
        .group_by(Transaction.category_id)
    )
    actuals = dict(actual_result.all())

    items = []
    total_budget = Decimal("0")
    total_actual = Decimal("0")
    for cat in categories:
        budget_amount = budgets[cat.id].amount if cat.id in budgets else Decimal("0")
        actual_amount = actuals.get(cat.id, Decimal("0"))
        remaining = budget_amount - actual_amount
        ratio = float(actual_amount / budget_amount) if budget_amount > 0 else 0.0
        status = "normal"
        if ratio >= 1.0:
            status = "exceeded"
        elif ratio >= 0.8:
            status = "warning"
        items.append(BudgetCategoryItem(
            category_id=cat.id, category_name=cat.name,
            budget=budget_amount, actual=actual_amount,
            remaining=remaining, ratio=round(ratio, 3), status=status,
        ))
        total_budget += budget_amount
        total_actual += actual_amount

    return {
        "code": 0, "message": "success",
        "data": BudgetResponse(
            year_month=year_month,
            total_budget=total_budget, total_actual=total_actual,
            total_remaining=total_budget - total_actual, items=items,
        ),
    }


@router.put("")
async def set_budgets(
    req: BudgetSetRequest,
    family_id: str = Depends(get_current_family_id),
    db: AsyncSession = Depends(get_db),
):
    for item in req.items:
        result = await db.execute(
            select(Budget).where(Budget.family_id == family_id, Budget.category_id == item.category_id, Budget.year_month == req.year_month)
        )
        existing = result.scalar_one_or_none()
        if existing:
            existing.amount = item.amount
        else:
            db.add(Budget(family_id=family_id, category_id=item.category_id, year_month=req.year_month, amount=item.amount))
    await db.commit()
    return {"code": 0, "message": "success", "data": None}
