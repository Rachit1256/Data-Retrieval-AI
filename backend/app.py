import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers.upload import router as upload_router
from routers.chat import router as chat_router
from routers.report import router as report_router
from routers.dashboard import router as dashboard_router

app = FastAPI()

# On a fresh deploy this directory doesn't exist yet (it's runtime-generated
# and correctly excluded from git) -- StaticFiles() raises at import time if
# the directory it's mounting isn't there, which would crash the whole app
# before uvicorn even starts.
os.makedirs("charts", exist_ok=True)

app.mount(
    "/charts",
    StaticFiles(directory="charts"),
    name="charts"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(chat_router)
app.include_router(report_router)
app.include_router(dashboard_router)


@app.get("/")
def root():
    return {
        "message": "AI Spreadsheet Assistant Running"
    }