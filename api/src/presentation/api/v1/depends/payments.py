from typing import Annotated

from fastapi import Body, Header, Depends, HTTPException

from application.services import PaymentService
from core.dto import CreatePaymentDTO
from presentation.api.v1.depends.common import CommandDependency, QueryDependency
from presentation.api.v1.schemas import CreatePaymentBody


def get_create_payment_data(
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")],
    body: Annotated[CreatePaymentBody, Body()]
) -> CreatePaymentDTO:
    return CreatePaymentDTO(idempotency_key=idempotency_key, **body.model_dump(mode='json'))


create_payment_dep = Annotated[CreatePaymentDTO, Depends(get_create_payment_data)]


command_payment_service = Annotated[PaymentService, Depends(CommandDependency(PaymentService))]
query_payment_service = Annotated[PaymentService, Depends(QueryDependency(PaymentService))]
