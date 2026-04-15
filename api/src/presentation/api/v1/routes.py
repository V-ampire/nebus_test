from typing import Annotated

from fastapi import APIRouter
from pydantic import UUID4
from starlette import status

from presentation.api.v1.depends.payments import command_payment_service, create_payment_dep, query_payment_service
from presentation.api.v1.schemas import PaymentSchema


router = APIRouter(
    prefix="/payments",
    tags=["Payments"],
)


@router.post("/", response_model=PaymentSchema, status_code=status.HTTP_202_ACCEPTED)
async def create_payment(
    create_payment_dto: create_payment_dep,
    service: command_payment_service,
):
    return await service.create_idempotency_payment(create_payment_dto)


@router.get("/{payment_id}", response_model=PaymentSchema)
async def get_payment(
    payment_id: UUID4,
    service: query_payment_service,
):
    return await service.get_payment_by_id(payment_id)
