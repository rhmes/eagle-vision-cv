from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from api.routes import router as api_router
from db.postgres import create_tracking_table

app = FastAPI(title="CV App")
app.include_router(api_router)
app.mount("/static", StaticFiles(directory="ui"), name="static")
templates = Jinja2Templates(directory="ui")

@app.get("/video-ui/")
async def video_ui(request: Request):
    return templates.TemplateResponse("stream.html", {"request": request})

@app.on_event("startup")
async def startup_event():
    create_tracking_table()
