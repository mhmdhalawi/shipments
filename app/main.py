from fastapi import FastAPI
from database import init_db
from routes import shipments_router
from contextlib import asynccontextmanager
from rich import print as rprint
from rich import panel


@asynccontextmanager
async def lifespan(app: FastAPI):
    rprint(panel.Panel("Starting up...", border_style="green"))
    await init_db()  # runs on startup, creates tables
    yield  # app runs here
    rprint(
        panel.Panel("Shutting down...", border_style="red")
    )  # anything after yield runs on shutdown


app = FastAPI(lifespan=lifespan)
app.include_router(shipments_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
