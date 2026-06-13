import uuid
from datetime import datetime, date, time, timezone
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, Date, Time, Numeric, Text, ForeignKey, Index, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        Index("idx_trans_family", "family_id"),
        Index("idx_trans_date", "transaction_date"),
        Index("idx_trans_family_date", "family_id", "transaction_date"),
        Index("idx_trans_family_type_date", "family_id", "type", "transaction_date"),
        Index("idx_trans_category", "category_id"),
        Index("idx_trans_member", "member_id"),
        Index("idx_trans_family_deleted", "family_id", "is_deleted"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    family_id: Mapped[str] = mapped_column(String(36), ForeignKey("families.id"), nullable=False)
    creator_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    member_id: Mapped[str] = mapped_column(String(36), ForeignKey("family_members.id"), nullable=False)
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    transaction_time: Mapped[time | None] = mapped_column(Time)
    type: Mapped[str] = mapped_column(String(10), nullable=False)  # expense / income
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    description: Mapped[str] = mapped_column(String(200), nullable=False)
    merchant: Mapped[str | None] = mapped_column(String(100))
    category_id: Mapped[str] = mapped_column(String(36), ForeignKey("categories.id"), nullable=False)
    sub_category_id: Mapped[str] = mapped_column(String(36), ForeignKey("sub_categories.id"), nullable=False)
    payment_method_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("payment_methods.id"))
    fund_source_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("fund_sources.id"))
    reimbursement: Mapped[str] = mapped_column(String(20), default="none")  # none / pending / reimbursed
    necessity: Mapped[str | None] = mapped_column(String(20))  # necessary / needed / wanted
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text)
    attachments: Mapped[dict | None] = mapped_column(JSON, default=list)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
