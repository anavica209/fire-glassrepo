import re
import unicodedata
from functools import lru_cache
from pathlib import Path

from pypdf import PdfReader

from app.core.config import PROJECT_ROOT

PDF_PATH = PROJECT_ROOT / "data" / "raw" / "guia_completa_tarot-v2.pdf"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 120
MAX_PASSAGES = 3
STOP_WORDS = {
    "como",
    "con",
    "de",
    "del",
    "el",
    "en",
    "es",
    "esta",
    "este",
    "la",
    "las",
    "lo",
    "los",
    "mi",
    "para",
    "por",
    "que",
    "se",
    "un",
    "una",
    "y",
}


def load_pdf_documents(pdf_path: Path = PDF_PATH) -> list[str]:
    if not pdf_path.is_file():
        raise FileNotFoundError(f"No se encuentra la guía de tarot: {pdf_path}")

    documents = []
    reader = PdfReader(str(pdf_path))
    for page_number, page in enumerate(reader.pages, start=1):
        text = re.sub(r"\s+", " ", page.extract_text() or "").strip()
        if text:
            documents.append(f"[Página {page_number}] {text}")

    if not documents:
        raise ValueError(f"No se pudo extraer texto de la guía de tarot: {pdf_path}")
    return documents


@lru_cache(maxsize=1)
def _load_passages() -> tuple[str, ...]:
    passages = []
    step = CHUNK_SIZE - CHUNK_OVERLAP
    for document in load_pdf_documents():
        for start in range(0, len(document), step):
            passage = document[start : start + CHUNK_SIZE].strip()
            if passage:
                passages.append(passage)
    return tuple(passages)


def _search_terms(text: str) -> set[str]:
    normalized = unicodedata.normalize("NFKD", text.casefold())
    without_accents = "".join(
        character for character in normalized if not unicodedata.combining(character)
    )
    return {
        term
        for term in re.findall(r"[a-z0-9]+", without_accents)
        if len(term) > 2 and term not in STOP_WORDS
    }


def find_relevant_passages(query: str) -> str:
    query_terms = _search_terms(query)
    if not query_terms:
        return ""

    ranked_passages = []
    for index, passage in enumerate(_load_passages()):
        overlap = query_terms & _search_terms(passage)
        if overlap:
            ranked_passages.append((len(overlap), index, passage))

    ranked_passages.sort(key=lambda result: (-result[0], result[1]))
    return "\n\n".join(
        passage for _, _, passage in ranked_passages[:MAX_PASSAGES]
    )
