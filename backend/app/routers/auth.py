import uuid
import hashlib
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.user import User
from app.models.family import Family, FamilyMember
from app.models.category import Category
from app.models.token import RefreshToken
from app.security import hash_password, verify_password, create_access_token
from app.schemas.auth import RegisterRequest, LoginRequest, RefreshRequest, ChangePasswordRequest
from app.schemas.common import ResponseBase
from app.config import get_settings
from app.dependencies import get_current_user

router = APIRouter()
settings = get_settings()

DEFAULT_EXPENSE_CATEGORIES = [
    ("餐饮美食", "food"), ("交通出行", "transport"), ("日用百货", "daily"),
    ("居家生活", "home"), ("水果零食", "fruit"), ("衣服鞋帽", "clothes"),
    ("美容美发", "beauty"), ("医疗健康", "health"), ("教育培训", "education"),
    ("休闲娱乐", "entertainment"), ("人情往来", "social"), ("金融保险", "finance"),
    ("其他支出", "other_expense"), ("宠物", "pet"),
]

DEFAULT_INCOME_CATEGORIES = [
    ("工资薪酬", "salary"), ("兼职外快", "parttime"), ("投资收益", "investment"),
    ("人情收入", "gift"), ("报销退款", "refund"), ("其他收入", "other_income"),
]


async def _seed_family_categories(db: AsyncSession, family_id: str):
    for i, (name, icon) in enumerate(DEFAULT_EXPENSE_CATEGORIES):
        db.add(Category(family_id=family_id, name=name, type="expense", icon=icon, sort_order=i, is_system=False))
    for i, (name, icon) in enumerate(DEFAULT_INCOME_CATEGORIES):
        db.add(Category(family_id=family_id, name=name, type="income", icon=icon, sort_order=i, is_system=False))


@router.post("/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where((User.username == req.username) | (User.email == req.email)))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Username or email already exists")

    user = User(
        username=req.username,
        email=req.email,
        password_hash=hash_password(req.password),
        nickname=req.nickname or req.username,
    )
    db.add(user)
    await db.flush()

    invite_code = uuid.uuid4().hex[:8].upper()
    family = Family(name=f"{user.nickname or user.username}的家", invite_code=invite_code, owner_id=user.id)
    db.add(family)
    await db.flush()

    member = FamilyMember(family_id=family.id, user_id=user.id, role="owner", display_name=user.nickname)
    db.add(member)
    await _seed_family_categories(db, family.id)
    await db.commit()

    return {"code": 0, "message": "success", "data": None}


@router.post("/login")
async def login(req: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where((User.username == req.username) | (User.email == req.username)))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    user.last_login_at = datetime.now(timezone.utc)

    member_result = await db.execute(select(FamilyMember).where(FamilyMember.user_id == user.id))
    fm = member_result.scalar_one_or_none()
    if not fm:
        raise HTTPException(status_code=403, detail="User has no family")

    family_result = await db.execute(select(Family).where(Family.id == fm.family_id))
    family = family_result.scalar_one()

    access_token = create_access_token(user.id, {"family_id": fm.family_id})
    refresh_raw = uuid.uuid4().hex
    refresh_hash = hashlib.sha256(refresh_raw.encode()).hexdigest()

    rt = RefreshToken(
        user_id=user.id,
        token_hash=refresh_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(rt)
    await db.commit()

    return {
        "code": 0, "message": "success",
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_raw,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {"id": user.id, "username": user.username, "nickname": user.nickname, "avatar_url": user.avatar_url},
            "family_id": fm.family_id,
            "family_name": family.name,
        },
    }


@router.post("/refresh")
async def refresh(req: RefreshRequest, db: AsyncSession = Depends(get_db)):
    token_hash = hashlib.sha256(req.refresh_token.encode()).hexdigest()
    result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    rt = result.scalar_one_or_none()
    if not rt or rt.revoked_at or rt.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    rt.revoked_at = datetime.now(timezone.utc)

    user_result = await db.execute(select(User).where(User.id == rt.user_id))
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    member_result = await db.execute(select(FamilyMember).where(FamilyMember.user_id == user.id))
    fm = member_result.scalar_one_or_none()

    access_token = create_access_token(user.id, {"family_id": fm.family_id} if fm else {})
    new_refresh_raw = uuid.uuid4().hex
    new_refresh_hash = hashlib.sha256(new_refresh_raw.encode()).hexdigest()

    new_rt = RefreshToken(
        user_id=user.id,
        token_hash=new_refresh_hash,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(new_rt)
    await db.commit()

    return {
        "code": 0, "message": "success",
        "data": {"access_token": access_token, "refresh_token": new_refresh_raw, "token_type": "bearer", "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60},
    }


@router.post("/logout")
async def logout(
    req: RefreshRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    token_hash = hashlib.sha256(req.refresh_token.encode()).hexdigest()
    result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash, RefreshToken.user_id == current_user.id))
    rt = result.scalar_one_or_none()
    if rt:
        rt.revoked_at = datetime.now(timezone.utc)
    await db.commit()
    return {"code": 0, "message": "success", "data": None}


@router.put("/password")
async def change_password(
    req: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(req.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    current_user.password_hash = hash_password(req.new_password)
    await db.commit()
    return {"code": 0, "message": "success", "data": None}
