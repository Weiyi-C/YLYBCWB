from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.database import get_db
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.family import FamilyMember
from app.models.user import User
from app.schemas.report import (
    MonthlySummaryItem, CategoryBreakdownItem, TrendItem,
    MemberComparisonItem, NecessityAnalysisItem,
)
from app.dependencies import get_current_family_id
from decimal import Decimal

router = APIRouter()


@router.get("/monthly-summary")
async def monthly_summary(
    year: int = Query(...),
    family_id: str = Depends(get_current_family_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(
            func.month(Transaction.transaction_date).label("month"),
            Transaction.type,
            func.sum(Transaction.amount),
        )
        .where(
            Transaction.family_id == family_id,
            Transaction.is_deleted == False,
            func.year(Transaction.transaction_date) == year,
        )
        .group_by("month", Transaction.type)
        .order_by("month")
    )
    rows = result.all()
    monthly = {}
    for month_num, tx_type, total in rows:
        m = int(month_num)
        if m not in monthly:
            monthly[m] = {"income": Decimal("0"), "expense": Decimal("0")}
        monthly[m][tx_type] = total

    items = []
    for m in range(1, 13):
        data = monthly.get(m, {"income": Decimal("0"), "expense": Decimal("0")})
        items.append(MonthlySummaryItem(
            month=f"{year}-{m:02d}",
            income=data["income"], expense=data["expense"],
            balance=data["income"] - data["expense"],
        ))
    return {"code": 0, "message": "success", "data": items}


@router.get("/category-breakdown")
async def category_breakdown(
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

    result = await db.execute(
        select(Transaction.category_id, func.sum(Transaction.amount), func.count())
        .where(
            Transaction.family_id == family_id, Transaction.type == "expense",
            Transaction.is_deleted == False,
            Transaction.transaction_date >= date_from, Transaction.transaction_date < date_to,
        )
        .group_by(Transaction.category_id)
    )
    rows = result.all()
    total = sum(r[1] for r in rows) or Decimal("1")

    cat_ids = [r[0] for r in rows]
    cats_result = await db.execute(select(Category).where(Category.id.in_(cat_ids)))
    cats = {c.id: c.name for c in cats_result.scalars().all()}

    items = []
    for cat_id, amount, count in sorted(rows, key=lambda x: x[1], reverse=True):
        items.append(CategoryBreakdownItem(
            category_id=cat_id, category_name=cats.get(cat_id, "Unknown"),
            amount=amount, ratio=round(float(amount / total), 4), count=count,
        ))
    return {"code": 0, "message": "success", "data": items}


@router.get("/trend")
async def trend(
    months: int = Query(12, ge=1, le=60),
    family_id: str = Depends(get_current_family_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(
            func.date_format(Transaction.transaction_date, "%Y-%m").label("month"),
            Transaction.type,
            func.sum(Transaction.amount),
        )
        .where(Transaction.family_id == family_id, Transaction.is_deleted == False)
        .group_by("month", Transaction.type)
        .order_by("month")
    )
    rows = result.all()
    monthly = {}
    for month_str, tx_type, total in rows:
        if month_str not in monthly:
            monthly[month_str] = {"income": Decimal("0"), "expense": Decimal("0")}
        monthly[month_str][tx_type] = total

    sorted_months = sorted(monthly.keys())[-months:]
    items = []
    for m in sorted_months:
        data = monthly[m]
        items.append(TrendItem(month=m, income=data["income"], expense=data["expense"]))
    return {"code": 0, "message": "success", "data": items}


@router.get("/member-comparison")
async def member_comparison(
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

    result = await db.execute(
        select(Transaction.member_id, func.sum(Transaction.amount), func.count())
        .where(
            Transaction.family_id == family_id, Transaction.type == "expense",
            Transaction.is_deleted == False,
            Transaction.transaction_date >= date_from, Transaction.transaction_date < date_to,
        )
        .group_by(Transaction.member_id)
    )
    rows = result.all()

    member_ids = [r[0] for r in rows]
    members_result = await db.execute(select(FamilyMember).where(FamilyMember.id.in_(member_ids)))
    members = {m.id: (m.display_name or "Unknown") for m in members_result.scalars().all()}

    items = []
    for member_id, total, count in sorted(rows, key=lambda x: x[1], reverse=True):
        items.append(MemberComparisonItem(
            member_id=member_id, member_name=members.get(member_id, "Unknown"),
            total_expense=total, transaction_count=count,
        ))
    return {"code": 0, "message": "success", "data": items}


@router.get("/necessity-analysis")
async def necessity_analysis(
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

    result = await db.execute(
        select(Transaction.necessity, func.sum(Transaction.amount), func.count())
        .where(
            Transaction.family_id == family_id, Transaction.type == "expense",
            Transaction.is_deleted == False,
            Transaction.transaction_date >= date_from, Transaction.transaction_date < date_to,
        )
        .group_by(Transaction.necessity)
    )
    rows = result.all()
    total = sum(r[1] for r in rows) or Decimal("1")

    items = []
    for necessity, amount, count in rows:
        items.append(NecessityAnalysisItem(
            necessity=necessity or "unspecified",
            amount=amount, ratio=round(float(amount / total), 4), count=count,
        ))
    return {"code": 0, "message": "success", "data": items}
