from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

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
        context={"user": user},
    )
