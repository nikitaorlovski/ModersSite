from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.auth import authenticate_user
from app.core.exceptions import AuthenticationError

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def require_login(request: Request):
    if not request.session.get("username"):
        return RedirectResponse("/", status_code=303)

@router.get("/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = authenticate_user(username, password)
    if not user:
        return templates.TemplateResponse("index.html", {"request": request, "error": "Неверный логин или пароль"})
    request.session["username"] = username
    return RedirectResponse("/projects", status_code=303)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303) 