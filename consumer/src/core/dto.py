from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, UUID4

from bootstrap.types import Currency, PaymentStatus


class BaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True)


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


class WebhookDTO(BaseDTO):
    url: str
    payment_id: UUID4
    amount: Decimal
    staus: PaymentStatus
    acquiring_message: str

