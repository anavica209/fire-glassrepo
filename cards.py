"""Card catalog and card-related request models."""

from enum import Enum
from typing import NamedTuple

from pydantic import BaseModel, Field, model_validator

from app_constants import (
    FIELD_NAME,
    FIELD_POSITION,
    POSITION_FUTURE,
    POSITION_PAST,
    POSITION_PRESENT,
)
from constants import CARD_TEXT


class CardPosition(str, Enum):
    PAST = POSITION_PAST
    PRESENT = POSITION_PRESENT
    FUTURE = POSITION_FUTURE


class Card(NamedTuple):
    name: str
    keywords: tuple[str, ...]
    interpretation: str


CARDS = {
    name: Card(name, keywords, interpretation)
    for name, (keywords, interpretation) in CARD_TEXT.items()
}
MAJOR_ARCANA = tuple(CARDS)


class ReadingCard(BaseModel):
    position: CardPosition = Field(alias=FIELD_POSITION)
    name: str = Field(alias=FIELD_NAME)

    @model_validator(mode="after")
    def validate_card_name(self):
        if self.name not in CARDS:
            raise ValueError("La lectura contiene una carta no reconocida.")
        return self
