import os
from fastapi import FastAPI, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()

# Debug check: verify on startup what engine is selected
print(f"--> ACTIVE OCR_ENGINE: {os.getenv('OCR_ENGINE')}")
print(
    f"--> GOOGLE CREDENTIALS PATH: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}"
)

from app.services.counter import calculate_sworn_pages
from app.services.extractor import process_document


app = FastAPI(title="Translatr API", version="0.1.0")

# Allow Next.js frontend (localhost:3000) to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


MAX_FILESIZE_BYTES = 10 * 1024 * 1024  # 10 MB


class TextPayload(BaseModel):
    text: str


class SwornPageBreakdown(BaseModel):
    raw_character_count: int
    sworn_page_count: int
    characters_per_sworn_page: int


class FileQuoteResponse(BaseModel):
    filename: str
    source_type: str
    used_ocr: bool
    physical_pages: int
    raw_character_count: int
    sworn_page_count: int
    word_count: int
    is_empty: bool


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/v1/count")
def count_characters(payload: TextPayload) -> SwornPageBreakdown:
    stats = calculate_sworn_pages(payload.text)
    return SwornPageBreakdown(**stats)


@app.post(
    "/api/v1/quote/file",
    response_model=FileQuoteResponse,
    status_code=status.HTTP_200_OK,
)
async def quote_document_file(file: UploadFile) -> FileQuoteResponse:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is missing from the uploaded file.",
        )

    file_bytes = await file.read()

    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty."
        )

    if len(file_bytes) > MAX_FILESIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Uploaded file exceeds the maximum allowed size of {MAX_FILESIZE_BYTES} bytes.",
        )

    try:
        extraction = process_document(file_bytes=file_bytes, filename=file.filename)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
        ) from exc

    quote_stats = calculate_sworn_pages(extraction.text)
    word_count = len(extraction.text.split())

    return FileQuoteResponse(
        filename=file.filename,
        source_type=extraction.source_type,
        used_ocr=extraction.used_ocr,
        physical_pages=extraction.physical_pages,
        raw_character_count=quote_stats["raw_character_count"],
        sworn_page_count=quote_stats["sworn_page_count"],
        word_count=word_count,
        is_empty=len(extraction.text.strip()) == 0,
    )
