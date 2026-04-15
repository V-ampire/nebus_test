from logging import getLogger

from faststream import Context
from faststream.rabbit import RabbitMessage
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession

from application.services import ProcessPaymentService, NotifyService
from bootstrap.db.unit_of_work import UnitOfWork
from bootstrap.utils import log_no_raise
from presentation.depends import db_session_dep

logger = getLogger(__name__)


async def process_payment(
    payment_id: UUID4,
    db_session: db_session_dep,
    di_container=Context(),
):
    async with UnitOfWork(db_session) as uow:
        payment_service = di_container.resolve(
            ProcessPaymentService,
            depends={AsyncSession: uow.session},
        )
        if not (webhook_data := await payment_service.process_payment(payment_id)):
            logger.error(f"Payment {payment_id} not pending.")

    notify_service = di_container.resolve(NotifyService)
    await notify_service.send_webhook(webhook_data)
    logger.info(f"Payment {payment_id} processed.")


async def process_dlq(payment_id: UUID4, msg: RabbitMessage):
    logger.error(f"DLQ payment {payment_id}, {msg.headers=}")