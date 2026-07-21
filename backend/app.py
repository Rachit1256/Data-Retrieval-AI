from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routers.upload import router as upload_router
from routers.chat import router as chat_router
from routers.report import router as report_router
from routers.dashboard import router as dashboard_router

app = FastAPI()
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
