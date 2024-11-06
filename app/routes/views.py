from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse

router = APIRouter(tags=["views"])

templates = Jinja2Templates(directory="app/templates")


@router.get("/favicon.ico")
async def favicon():
    return FileResponse("app/static/images/favicon.ico")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
