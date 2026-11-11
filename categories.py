"""Reading category definitions."""

from enum import Enum
from typing import NamedTuple

from app_constants import (
    CATEGORY_GENERAL,
    CATEGORY_GROWTH,
    CATEGORY_LOVE,
    CATEGORY_WORK,
)
from constants import CATEGORY_TEXT


class CategoryKey(str, Enum):
    LOVE = CATEGORY_LOVE
    WORK = CATEGORY_WORK
    GROWTH = CATEGORY_GROWTH
    GENERAL = CATEGORY_GENERAL


class Category(NamedTuple):
    key: CategoryKey
    label: str
    focus: str


CATEGORIES: dict[CategoryKey, Category] = {
    key: Category(key, *CATEGORY_TEXT[key.value])
    for key in CategoryKey
}
