from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.api.endpoints.auth import require_login

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/projects")
async def show_projects(request: Request, _: str = Depends(require_login)):
    return templates.TemplateResponse("projects.html", {"request": request})

@router.get("/select_project/{project_name}")
async def select_project(request: Request, project_name: str, _: str = Depends(require_login)):
    request.session["project_name"] = project_name
    return templates.TemplateResponse("server_selection.html", {"request": request, "project_name": project_name}) 