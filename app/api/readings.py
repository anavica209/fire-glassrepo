import secrets
import textwrap
from html import escape
from io import BytesIO
from typing import Annotated
from zipfile import ZIP_DEFLATED, ZipFile

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response

from app.core.constants import (
    FIELD_CARDS,
    FIELD_CATEGORY,
    FIELD_CATEGORY_FOCUS,
    FIELD_CATEGORY_LABEL,
    FIELD_INTERPRETATION,
    FIELD_KEYWORDS,
    FIELD_NAME,
    FIELD_POSITION,
    FIELD_POSITION_LABEL,
    FIELD_QUESTION,
)
from app.domain.cards import CARDS, MAJOR_ARCANA, ReadingCard
from app.domain.categories import CATEGORIES, CategoryKey
from app.core.constants import POSITION_LABELS, POSITIONS
from app.domain.core import (
    DownloadReadingRequest,
    ReadingRequest,
    require_user,
)

router = APIRouter()

ROMAN_NUMERALS = ("I", "II", "III")


def _svg_text(
    text: str,
    x: int,
    y: int,
    max_characters: int,
    font_size: int,
    line_height: int,
    color: str,
    *,
    text_anchor: str = "start",
) -> str:
    lines = textwrap.wrap(text, width=max_characters) or [""]
    spans = "".join(
        f'<tspan x="{x}" dy="{0 if index == 0 else line_height}">'
        f'{escape(line)}{" " if index < len(lines) - 1 else ""}</tspan>'
        for index, line in enumerate(lines)
    )
    return (
        f'<text xml:space="preserve" x="{x}" y="{y}" fill="{color}" font-size="{font_size}" '
        f'text-anchor="{text_anchor}">{spans}</text>'
    )


def build_card_image(card: ReadingCard, index: int, category: CategoryKey) -> str:
    card_content = CARDS[card.name]
    position_label = POSITION_LABELS[card.position]
    category_focus = CATEGORIES[category].focus
    card_name = escape(card.name)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1600" viewBox="0 0 1200 1600" role="img" aria-labelledby="title">
  <title id="title">{escape(card.position)}: {card_name} — Fire glass</title>
  <defs>
    <linearGradient id="card" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#1d2c37"/>
      <stop offset="1" stop-color="#0a1520"/>
    </linearGradient>
    <radialGradient id="glow">
      <stop stop-color="#ae7b42" stop-opacity=".3"/>
      <stop offset="1" stop-color="#ae7b42" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="1200" height="1600" fill="#0b131b"/>
  <rect x="34" y="34" width="1132" height="1532" rx="8" fill="none" stroke="#30414c"/>
  <text x="84" y="94" fill="#f0d7ae" font-family="Georgia,serif" font-size="26" letter-spacing="5">FIRE GLASS</text>
  <text x="1116" y="94" fill="#8d99a9" font-family="Arial,sans-serif" font-size="18" letter-spacing="3" text-anchor="end">TU LECTURA</text>
  <path d="M 100 680 V 310 Q 100 150 260 150 H 940 Q 1100 150 1100 310 V 680 Z" fill="url(#card)" stroke="#ae7b42" stroke-opacity=".8" stroke-width="2"/>
  <path d="M 122 658 V 310 Q 122 172 260 172 H 940 Q 1078 172 1078 310 V 658 Z" fill="url(#glow)" stroke="#c1ced6" stroke-opacity=".2"/>
  <text x="600" y="238" fill="#cfbe9f" font-family="Georgia,serif" font-size="27" text-anchor="middle">{ROMAN_NUMERALS[index]}</text>
  <text x="600" y="416" fill="#e1a95e" font-family="Georgia,serif" font-size="100" text-anchor="middle">✳</text>
  <text x="600" y="500" fill="#8d99a9" font-family="Arial,sans-serif" font-size="20" letter-spacing="5" text-anchor="middle">{escape(card.position.upper())}</text>
  {_svg_text(card.name, 600, 570, 26, 42, 50, "#f0d7ae", text_anchor="middle")}
  <text x="84" y="770" fill="#9db8c6" font-family="Arial,sans-serif" font-size="19" letter-spacing="3">{escape(position_label.upper())}</text>
  <text x="84" y="830" fill="#f0d7ae" font-family="Georgia,serif" font-size="34">Interpretación</text>
  {_svg_text(card_content.interpretation, 84, 894, 62, 27, 40, "#c4cbd0")}
  <text x="84" y="1098" fill="#cfbe9f" font-family="Arial,sans-serif" font-size="18" letter-spacing="3">PALABRAS CLAVE</text>
  {_svg_text(" · ".join(card_content.keywords), 84, 1140, 62, 23, 34, "#d5bd98")}
  <text x="84" y="1230" fill="#cfbe9f" font-family="Arial,sans-serif" font-size="18" letter-spacing="3">PARA TENER EN CUENTA</text>
  {_svg_text(category_focus, 84, 1274, 62, 24, 38, "#d3b98e")}
  <text x="600" y="1510" fill="#7e8d98" font-family="Georgia,serif" font-size="20" font-style="italic" text-anchor="middle">Las cartas muestran tendencias; tú moldeas tu camino.</text>
</svg>"""


@router.post("/api/reading")
async def draw_reading(
    reading: ReadingRequest,
    _user: Annotated[dict[str, str], Depends(require_user)],
):
    cards = secrets.SystemRandom().sample(MAJOR_ARCANA, k=3)
    category = CATEGORIES[reading.category]
    return JSONResponse(
        {
            FIELD_CATEGORY: reading.category.value,
            FIELD_CATEGORY_LABEL: category.label,
            FIELD_CATEGORY_FOCUS: category.focus,
            FIELD_QUESTION: reading.question.strip(),
            FIELD_CARDS: [
                {
                    FIELD_POSITION: position,
                    FIELD_POSITION_LABEL: POSITION_LABELS[position],
                    FIELD_NAME: card,
                    FIELD_KEYWORDS: CARDS[card].keywords,
                    FIELD_INTERPRETATION: CARDS[card].interpretation,
                }
                for position, card in zip(POSITIONS, cards, strict=True)
            ]
        }
    )


@router.post("/api/reading/download")
async def download_reading_images(
    reading: DownloadReadingRequest,
    _user: Annotated[dict[str, str], Depends(require_user)],
):
    archive = BytesIO()
    with ZipFile(archive, "w", compression=ZIP_DEFLATED) as zip_file:
        for index, card in enumerate(reading.cards):
            position_slug = card.position.lower().replace(" ", "-")
            zip_file.writestr(
                f"carta-{index + 1}-{position_slug}.svg",
                build_card_image(card, index, reading.category),
            )
    return Response(
        content=archive.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="lectura-fire-glass.zip"'},
    )
