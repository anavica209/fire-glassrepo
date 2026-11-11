from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from app_constants import ADMIN_ROLE, API_FIELDS, CATEGORY_IDS, DEFAULT_CATEGORY
from core import signed_in_user, templates

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    user = signed_in_user(request)
    if user is None:
        return RedirectResponse("/login", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "user": user,
            "admin_role": ADMIN_ROLE,
            "api_fields": API_FIELDS,
            "category_ids": CATEGORY_IDS,
            "default_category": DEFAULT_CATEGORY,
        },
    )

