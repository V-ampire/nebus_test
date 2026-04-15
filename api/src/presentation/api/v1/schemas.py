from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, UUID4

from core.dto import Currency, PaymentStatus


class CreatePaymentBody(BaseModel):
    amount: Decimal = Field(gt=0, description="Сумма платежа")
    currency: Currency = Field(description="Валюта платежа")
    description: str = Field(description="Описание платежа")
    meta_data: dict[str, Any] | None = Field(default=None, description="Дополнительные метаданные", validation_alias='metadata')
    webhook_url: HttpUrl | None = Field(default=None, description="URL для webhook-уведомлений")


class PaymentSchema(BaseModel):
    id: UUID4 = Field(description="Уникальный идентификатор платежа", serialization_alias="payment_id")
    status: PaymentStatus = Field(default=PaymentStatus.PENDING, description="Статус платежа")
    created_at: datetime = Field(description="Дата и время создания платежа")
