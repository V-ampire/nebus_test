import uuid
from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import UUID4
from sqlalchemy import DateTime, func, String, Text, Numeric, JSON, Uuid
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

from bootstrap.types import OutboxStatus, PaymentStatus


class Base(AsyncAttrs, DeclarativeBase):
    @classmethod
    def get_pk(cls):
        return cls.id

    @classmethod
    def get_pk_name(cls):
        return 'id'


class PaymentModel(Base):
    __tablename__ = 'payments'

    id: Mapped[UUID4] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=18, scale=2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    meta_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    acquiring_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default=PaymentStatus.PENDING)
    idempotency_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    webhook_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    def __str__(self):
        return f"{self.id}: {self.amount} {self.currency} {self.description[:32]}"


class OutboxModel(Base):
    __tablename__ = 'outbox'

    event_id: Mapped[UUID4] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default=OutboxStatus.NEW)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    @classmethod
    def get_pk(cls):
        return cls.event_id

    @classmethod
    def get_pk_name(cls):
        return 'event_id'
