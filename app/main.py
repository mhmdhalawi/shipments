from fastapi import FastAPI
from routes import shipments_router, ai_router, seller_router, delivery_partner_router
from contextlib import asynccontextmanager
from rich import print as rprint
from rich import panel
from services import init_anthropic_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    rprint(panel.Panel("Starting up...", border_style="green"))
    anthropic_client = init_anthropic_client()
    yield
    await anthropic_client.close()  # clean shutdown
    rprint(
        panel.Panel("Shutting down...", border_style="red")
    )  # anything after yield runs on shutdown


app = FastAPI(lifespan=lifespan)
app.include_router(shipments_router)
app.include_router(ai_router)
app.include_router(seller_router)
app.include_router(delivery_partner_router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
