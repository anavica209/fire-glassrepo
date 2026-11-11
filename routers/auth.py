import os
import secrets
from typing import Annotated

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestFormStrict

from core import (
    create_access_token,
    google_client_id,
    google_client_secret,
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
            "google_enabled": bool(google_client_id and google_client_secret),
            "error": request.query_params.get("error"),
        },
    )


@router.post("/auth/login")
async def login(
    request: Request,
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
):
    valid_username = secrets.compare_digest(username, "admin")
    valid_password = secrets.compare_digest(password, "admin")
    if not (valid_username and valid_password):
        return RedirectResponse("/login?error=credentials", status_code=303)

    request.session.clear()
    request.session["user"] = {
        "name": "Admin",
        "email": "admin@example.com",
        "role": "admin",
    }
    return RedirectResponse("/", status_code=303)


@router.post("/auth/token")
async def issue_password_token(
    credentials: Annotated[OAuth2PasswordRequestFormStrict, Depends()],
):
    valid_username = secrets.compare_digest(credentials.username, "admin")
    valid_password = secrets.compare_digest(credentials.password, "admin")
    if not (valid_username and valid_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = {"name": "Admin", "email": "admin@example.com"}
    return {
        "access_token": create_access_token(user),
        "token_type": "bearer",
    }


@router.post("/auth/session-token")
async def issue_session_token(
    user: Annotated[dict[str, str], Depends(require_session_user)],
):
    return {
        "access_token": create_access_token(user),
        "token_type": "bearer",
    }


@router.get("/auth/google")
async def google_login(request: Request):
    if not (google_client_id and google_client_secret):
        return RedirectResponse("/login?error=google_not_configured", status_code=303)
    redirect_uri = os.getenv(
        "GOOGLE_REDIRECT_URI",
        str(request.url_for("google_callback")),
    )
    return await oauth.google.authorize_redirect(request, redirect_uri)


@router.get("/auth/google/callback")
async def google_callback(request: Request):
    if not (google_client_id and google_client_secret):
        return RedirectResponse("/login?error=google_not_configured", status_code=303)
    token = await oauth.google.authorize_access_token(request)
    userinfo = token.get("userinfo")
    if not userinfo or not userinfo.get("email"):
        raise HTTPException(status_code=400, detail="Google no devolvió un correo verificable.")

    request.session.clear()
    request.session["user"] = {
        "name": userinfo.get("name") or userinfo["email"],
        "email": userinfo["email"],
    }
    return RedirectResponse("/", status_code=303)


@router.post("/auth/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
