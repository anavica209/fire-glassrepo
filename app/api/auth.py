import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestFormStrict

from app.core.config import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI,
)
from app.core.constants import (
    ADMIN_ROLE,
    DEMO_DISPLAY_NAME,
    DEMO_EMAIL,
    DEMO_PASSWORD,
    DEMO_USERNAME,
    FIELD_EMAIL,
    FIELD_NAME,
    FIELD_PASSWORD,
    FIELD_ROLE,
    FIELD_ACCESS_TOKEN,
    FIELD_TOKEN_TYPE,
    FIELD_USER,
    FIELD_USERNAME,
)
from app.domain.core import (
    create_access_token,
    oauth,
    require_session_user,
    signed_in_user,
    templates,
)

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if signed_in_user(request):
        return RedirectResponse("/", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "google_enabled": bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET),
            "error": request.query_params.get("error"),
            "field_username": FIELD_USERNAME,
            "field_password": FIELD_PASSWORD,
            "demo_username": DEMO_USERNAME,
            "demo_password": DEMO_PASSWORD,
        },
    )


@router.post("/auth/login")
async def login(
    request: Request,
    username: Annotated[str, Form(alias=FIELD_USERNAME)],
    password: Annotated[str, Form(alias=FIELD_PASSWORD)],
):
    valid_username = secrets.compare_digest(username, DEMO_USERNAME)
    valid_password = secrets.compare_digest(password, DEMO_PASSWORD)
    if not (valid_username and valid_password):
        return RedirectResponse("/login?error=credentials", status_code=303)

    request.session.clear()
    request.session[FIELD_USER] = {
        FIELD_NAME: DEMO_DISPLAY_NAME,
        FIELD_EMAIL: DEMO_EMAIL,
        FIELD_ROLE: ADMIN_ROLE,
    }
    return RedirectResponse("/", status_code=303)


@router.post("/auth/token")
async def issue_password_token(
    credentials: Annotated[OAuth2PasswordRequestFormStrict, Depends()],
):
    valid_username = secrets.compare_digest(credentials.username, DEMO_USERNAME)
    valid_password = secrets.compare_digest(credentials.password, DEMO_PASSWORD)
    if not (valid_username and valid_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = {FIELD_NAME: DEMO_DISPLAY_NAME, FIELD_EMAIL: DEMO_EMAIL}
    return {
        FIELD_ACCESS_TOKEN: create_access_token(user),
        FIELD_TOKEN_TYPE: "bearer",
    }


@router.post("/auth/session-token")
async def issue_session_token(
    user: Annotated[dict[str, str], Depends(require_session_user)],
):
    return {
        FIELD_ACCESS_TOKEN: create_access_token(user),
        FIELD_TOKEN_TYPE: "bearer",
    }


@router.get("/auth/google")
async def google_login(request: Request):
    if not (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET):
        return RedirectResponse("/login?error=google_not_configured", status_code=303)
    redirect_uri = GOOGLE_REDIRECT_URI or str(request.url_for("google_callback"))
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/google/callback")
async def google_callback(request: Request):
    if not (GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET):
        return RedirectResponse("/login?error=google_not_configured", status_code=303)
    token = await oauth.google.authorize_access_token(request)
    userinfo = token.get("userinfo")
    if not userinfo or not userinfo.get(FIELD_EMAIL):
        raise HTTPException(status_code=400, detail="Google no devolvió un correo verificable.")

    request.session.clear()
    request.session[FIELD_USER] = {
        FIELD_NAME: userinfo.get(FIELD_NAME) or userinfo[FIELD_EMAIL],
        FIELD_EMAIL: userinfo[FIELD_EMAIL],
    }
    return RedirectResponse("/", status_code=303)


@router.post("/auth/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)

