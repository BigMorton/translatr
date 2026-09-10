from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.services.counter import calculate_sworn_pages

app = FastAPI(title="Translatr API", version="0.1.0")

# Allow Next.js frontend (localhost:3000) to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TextPayload(BaseModel):
    text: str


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/v1/count")
def count_characters(payload: TextPayload):
    return calculate_sworn_pages(payload.text)
