from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services.auth_service import authenticate_user

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def require_login(request: Request):
    if not request.session.get("username"):
        raise HTTPException(status_code=302, headers={"Location": "/"})
    return request.session["username"]

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
