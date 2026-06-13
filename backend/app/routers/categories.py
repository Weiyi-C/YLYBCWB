from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.category import Category, SubCategory
from app.schemas.category import (
    CategoryResponse, CategoryCreate, CategoryUpdate,
    SubCategoryResponse, SubCategoryCreate, SubCategoryUpdate,
)
from app.dependencies import get_current_family_id

router = APIRouter()


@router.get("")
async def list_categories(
    type: str | None = Query(None, pattern="^(expense|income)$"),
    family_id: str = Depends(get_current_family_id),
    db: AsyncSession = Depends(get_db),
):
    q = select(Category).options(selectinload(Category.sub_categories)).where(
        ((Category.family_id == family_id) | (Category.family_id == None)) & (Category.is_active == True)
    )
    if type:
        q = q.where(Category.type == type)
    q = q.order_by(Category.sort_order)
    result = await db.execute(q)
    categories = result.scalars().unique().all()
    items = [CategoryResponse.model_validate(c) for c in categories]
    return {"code": 0, "message": "success", "data": items}


@router.post("")
async def create_category(
    req: CategoryCreate,
    family_id: str = Depends(get_current_family_id),
    db: AsyncSession = Depends(get_db),
):
    cat = Category(
        family_id=family_id, name=req.name, type=req.type,
        icon=req.icon, color=req.color or "#666666", sort_order=req.sort_order or 0,
    )
    db.add(cat)
    await db.commit()
    return {"code": 0, "message": "success", "data": CategoryResponse.model_validate(cat)}


@router.put("/{category_id}")
async def update_category(
    category_id: str,
    req: CategoryUpdate,
    family_id: str = Depends(get_current_family_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Category).where(Category.id == category_id, Category.family_id == family_id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    if cat.is_system:
        raise HTTPException(status_code=403, detail="Cannot modify system category")
    for k, v in req.model_dump(exclude_unset=True).items():
        setattr(cat, k, v)
    await db.commit()
    return {"code": 0, "message": "success", "data": CategoryResponse.model_validate(cat)}


@router.delete("/{category_id}")
async def delete_category(
    category_id: str,
    family_id: str = Depends(get_current_family_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Category).where(Category.id == category_id, Category.family_id == family_id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    if cat.is_system:
        raise HTTPException(status_code=403, detail="Cannot delete system category")
    cat.is_active = False
    await db.commit()
    return {"code": 0, "message": "success", "data": None}


@router.post("/{category_id}/sub-categories")
async def create_sub_category(
    category_id: str,
    req: SubCategoryCreate,
    family_id: str = Depends(get_current_family_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Category).where(Category.id == category_id, Category.family_id == family_id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    sub = SubCategory(category_id=category_id, name=req.name, sort_order=req.sort_order or 0)
    db.add(sub)
    await db.commit()
    return {"code": 0, "message": "success", "data": SubCategoryResponse.model_validate(sub)}
