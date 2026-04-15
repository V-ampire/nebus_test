from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, UUID4

from bootstrap.types import OutboxStatus, Currency, PaymentStatus


class BaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class CreatePaymentDTO(BaseDTO):
    idempotency_key: str
    amount: Decimal
    currency: Currency
    description: str
    meta_data: dict[str, Any] | None
    webhook_url: str


class PaymentDTO(BaseDTO):
    id: UUID4
    amount: Decimal
    currency: Currency
    description: str
    meta_data: dict[str, Any] | None
    status: PaymentStatus
    idempotency_key: str
    webhook_url: str
    created_at: datetime
    processed_at: datetime | None


class CreateOutboxDTO(BaseDTO):
    status: OutboxStatus
    payload: dict


class OutboxDTO(BaseDTO):
    event_id: UUID4
    status: OutboxStatus
    payload: dict

