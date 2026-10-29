from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator

PlanName = Literal["Pro", "Max", "Enterprise"]


class ClientIn(BaseModel):
    name: str
    plan: PlanName
    seats: int = Field(ge=1)
    contact_email: str | None = None


class TierChange(BaseModel):
    plan: PlanName


class BookingIn(BaseModel):
    client_id: int
    hero: str
    mission: str
    start: datetime
    end: datetime

    @model_validator(mode="after")
    def end_after_start(self):
        if self.end <= self.start:
            raise ValueError("end must be after start")
        return self
