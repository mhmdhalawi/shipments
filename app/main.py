from fastapi import FastAPI
from app.routes import shipments

app = FastAPI()
app.include_router(shipments.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}