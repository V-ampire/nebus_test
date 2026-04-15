from pydantic import BaseModel, UUID4

from bootstrap.types import OutboxStatus


class OutboxDTO(BaseModel):
    event_id: UUID4
    status: OutboxStatus
    payload: dict
