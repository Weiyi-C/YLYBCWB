import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import get_db
from app.models.family import Family, FamilyMember
from app.models.user import User
from app.schemas.family import FamilyResponse, FamilyUpdate, JoinFamilyRequest, MemberResponse, MemberUpdate
from app.schemas.common import ResponseBase
from app.dependencies import get_current_user, get_current_family_id

router = APIRouter()


@router.get("/current")
async def get_family(
    family_id: str = Depends(get_current_family_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Family).where(Family.id == family_id))
    family = result.scalar_one_or_none()
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")
    return {"code": 0, "message": "success", "data": FamilyResponse.model_validate(family)}


@router.put("/current")
async def update_family(
    req: FamilyUpdate,
    family_id: str = Depends(get_current_family_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Family).where(Family.id == family_id))
    family = result.scalar_one_or_none()
    if not family:
        raise HTTPException(status_code=404, detail="Family not found")
    family.name = req.name
    await db.commit()
    return {"code": 0, "message": "success", "data": FamilyResponse.model_validate(family)}


@router.post("/join")
async def join_family(
    req: JoinFamilyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Family).where(Family.invite_code == req.invite_code))
    family = result.scalar_one_or_none()
    if not family:
        raise HTTPException(status_code=404, detail="Invalid invite code")

    existing = await db.execute(select(FamilyMember).where(FamilyMember.family_id == family.id, FamilyMember.user_id == current_user.id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Already a member")

    member = FamilyMember(family_id=family.id, user_id=current_user.id, role="member", display_name=current_user.nickname)
    db.add(member)
    await db.commit()
    return {"code": 0, "message": "success", "data": None}


@router.get("/current/members")
async def list_members(
    family_id: str = Depends(get_current_family_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(FamilyMember, User)
        .join(User, FamilyMember.user_id == User.id)
        .where(FamilyMember.family_id == family_id)
    )
    rows = result.all()
    items = []
    for fm, user in rows:
        items.append(MemberResponse(
            id=fm.id, user_id=user.id, username=user.username,
            nickname=user.nickname, display_name=fm.display_name,
            role=fm.role, joined_at=fm.joined_at,
        ))
    return {"code": 0, "message": "success", "data": items}


@router.put("/current/members/{member_id}")
async def update_member(
    member_id: str,
    req: MemberUpdate,
    family_id: str = Depends(get_current_family_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(FamilyMember).where(FamilyMember.id == member_id, FamilyMember.family_id == family_id))
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    if req.display_name is not None:
        member.display_name = req.display_name
    if req.role is not None:
        member.role = req.role
    await db.commit()
    return {"code": 0, "message": "success", "data": None}


@router.delete("/current/members/{member_id}")
async def remove_member(
    member_id: str,
    family_id: str = Depends(get_current_family_id),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(FamilyMember).where(FamilyMember.id == member_id, FamilyMember.family_id == family_id))
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    if member.role == "owner":
        raise HTTPException(status_code=403, detail="Cannot remove owner")
    await db.delete(member)
    await db.commit()
    return {"code": 0, "message": "success", "data": None}
