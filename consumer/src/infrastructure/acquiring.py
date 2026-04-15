import asyncio
import random
from dataclasses import dataclass
from decimal import Decimal

from pydantic import BaseModel


class AcquiringRequest(BaseModel):
    terminal_key: str
    amount: Decimal
    order_id: str


class AcquiringResponse(BaseModel):
    message: str
    success: bool
    order_id: str
    payment_id: str
    amount: Decimal


@dataclass
class AcquiringClient(BaseModel):
    async def init_payment(self, payload: AcquiringRequest) -> AcquiringResponse:
        """Emulated acquiring."""
        payment_id = f"{payload.terminal_key}-{random.randint(100000, 999999)}"

        # 2-5 сек
        await asyncio.sleep(random.uniform(2, 5))

        # 90% успех, 10% ошибка
        success = random.random() < 0.9
        message = "CONFIRMED" if success else "REJECTED"

        return AcquiringResponse(
            message=message,
            success=success,
            order_id=payload.order_id,
            payment_id=payment_id,
            amount=payload.amount
        )
