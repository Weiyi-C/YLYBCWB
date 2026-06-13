from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.transaction import Transaction
from app.models.category import Category, SubCategory
from app.models.family import FamilyMember
from app.schemas.transaction import TransactionCreate, TransactionUpdate, TransactionResponse
from app.schemas.common import PaginatedData
from app.dependencies import get_current_user, get_current_family_id
from app.models.user import User
from decimal import Decimal
from datetime import date

router = APIRouter()


@router.get("")
async def list_transactions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: str | None = Query(None, pattern="^(expense|income)$"),
    date_from: date | None = None,
    date_to: date | None = None,
    category_id: str | None = None,
    sub_category_id: str | None = None,
    member_id: str | None = None,
    payment_method_id: str | None = None,
    fund_source_id: str | None = None,
    reimbursement: str | None = None,
    necessity: str | None = None,
    keyword: str | None = None,
    min_amount: Decimal | None = None,
    max_amount: Decimal | None = None,
    sort_by: str = "transaction_date",
    sort_order: str = "desc",
    family_id: str = Depends(get_current_family_id),
    db: AsyncSession = Depends(get_db),
):
    q = select(Transaction).where(Transaction.family_id == family_id, Transaction.is_deleted == False)
    cq = select(func.count()).select_from(Transaction).where(Transaction.family_id == family_id, Transaction.is_deleted == False)

    filters = []
    if type:
        filters.append(Transaction.type == type)
    if date_from:
        filters.append(Transaction.transaction_date >= date_from)
    if date_to:
        filters.append(Transaction.transaction_date <= date_to)
    if category_id:
        filters.append(Transaction.category_id == category_id)
    if sub_category_id:
        filters.append(Transaction.sub_category_id == sub_category_id)
    if member_id:
        filters.append(Transaction.member_id == member_id)
    if payment_method_id:
        filters.append(Transaction.payment_method_id == payment_method_id)
    if fund_source_id:
        filters.append(Transaction.fund_source_id == fund_source_id)
    if reimbursement:
        filters.append(Transaction.reimbursement == reimbursement)
    if necessity:
        filters.append(Transaction.necessity == necessity)
    if keyword:
        kw = f"%{keyword}%"
        filters.append(or_(Transaction.description.ilike(kw), Transaction.merchant.ilike(kw), Transaction.notes.ilike(kw)))
    if min_amount is not None:
        filters.append(Transaction.amount >= min_amount)
    if max_amount is not None:
        filters.append(Transaction.amount <= max_amount)

    for f in filters:
        q = q.where(f)
        cq = cq.where(f)

    total_result = await db.execute(cq)
    total = total_result.scalar()

    sort_col = getattr(Transaction, sort_by, Transaction.transaction_date)
    order = sort_col.desc() if sort_order == "desc" else sort_col.asc()
    q = q.order_by(order, Transaction.created_at.desc())
    q = q.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(q)
    transactions = result.scalars().all()

    items = []
    for t in transactions:
        items.append(TransactionResponse.model_validate(t))

    total_pages = (total + page_size - 1) // page_size
    return {
        "code": 0, "message": "success",
        "data": PaginatedData[TransactionResponse](
            items=items, total=total, page=page, page_size=page_size, total_pages=total_pages
        ),
    }


@router.post("")
async def create_transaction(
    req: TransactionCreate,
    current_user: User = Depends(get_current_user),
    family_id: str = Depends(get_current_family_id),
    db: AsyncSession = Depends(get_db),
):
    member_id = req.member_id
    if not member_id:
        result = await db.execute(select(FamilyMember).where(FamilyMember.family_id == family_id, FamilyMember.user_id == current_user.id))
        fm = result.scalar_one_or_none()
        member_id = fm.id if fm else None

    t = Transaction(
        family_id=family_id, creator_id=current_user.id, member_id=member_id,
        transaction_date=req.transaction_date, transaction_time=req.transaction_time,
        type=req.type, amount=req.amount, description=req.description,
        merchant=req.merchant, category_id=req.category_id, sub_category_id=req.sub_category_id,
        payment_method_id=req.payment_method_id, fund_source_id=req.fund_source_id,
        reimbursement=req.reimbursement or "none", necessity=req.necessity,
        is_recurring=req.is_recurring, notes=req.notes,
    )
    db.add(t)
    await db.commit()
    return {"code": 0, "message": "success", "data": TransactionResponse.model_validate(t)}


@router.get("/{transaction_id}")
async def get_transaction(
    transaction_id: str,
    family_id: str = Depends(get_current_family_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Transaction).where(Transaction.id == transaction_id, Transaction.family_id == family_id, Transaction.is_deleted == False))
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"code": 0, "message": "success", "data": TransactionResponse.model_validate(t)}


@router.put("/{transaction_id}")
async def update_transaction(
    transaction_id: str,
    req: TransactionUpdate,
    family_id: str = Depends(get_current_family_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Transaction).where(Transaction.id == transaction_id, Transaction.family_id == family_id, Transaction.is_deleted == False))
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Transaction not found")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(t, k, v)
    await db.commit()
    return {"code": 0, "message": "success", "data": TransactionResponse.model_validate(t)}


@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: str,
    family_id: str = Depends(get_current_family_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Transaction).where(Transaction.id == transaction_id, Transaction.family_id == family_id, Transaction.is_deleted == False))
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="Transaction not found")
    t.is_deleted = True
    await db.commit()
    return {"code": 0, "message": "success", "data": None}
