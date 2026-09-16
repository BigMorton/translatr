import io
from dataclasses import dataclass
from typing import Protocol

from pypdf import PdfReader


@dataclass
class ExtractionResult:
    text: str
    physical_pages: int
    used_ocr: bool
    source_type: str  # "digital_pdf" or "scanned_pdf" or "image" or "text"


class OcrEngine(Protocol):
    def extract_text(self, file_bytes: bytes, mime_type: str) -> tuple[str, int]:
        """Extract text and page count from a file using an OCR Servive.

        Returns a tuple of (extracted_text, page_count).
        """
        ...


class MockOcrEngine:
    # Mock local OCR engine for testing and dev purposes
    def __init__(self, stub_text: str = "Mock extracted text"):
        self.stub_text = stub_text

    def extract_text(self, file_bytes: bytes, mime_type: str) -> tuple[str, int]:
        # Mock implementation for testing purposes
        return self.stub_text, 1


def _extract_text_from_pdf(file_bytes: bytes) -> tuple[str, int]:
    """Extract text from a PDF file using PyPDF."""
    stream = io.BytesIO(file_bytes)
    reader = PdfReader(stream)

    pages_text = []
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            pages_text.append(extracted.strip())

    full_text = "\n\n".join(pages_text).strip()
    return full_text, len(reader.pages)


def process_document(
    file_bytes: bytes,
    filename: str,
    ocr_engine: OcrEngine | None = None,
    text_threshold: int = 50,
) -> ExtractionResult:
    """Process an uploaded document in memory.

    Uses pypdf to extract text from digital PDFs. If the text extracted is below
    a certain threshold, fallback to using an OCR engine (for scanned PDFs or images). The threshold is set to 50 characters by default.
    """
    lower_name = filename.lower()
    ocr = (
        ocr_engine or MockOcrEngine()
    )  # Use the provided OCR engine or a mock for testing

    # Plain Text Files
    if lower_name.endswith(".txt"):
        text = file_bytes.decode("utf-8", errors="ignore")
        return ExtractionResult(
            text=text, physical_pages=1, used_ocr=False, source_type="text"
        )

    # Image Files
    if lower_name.endswith((".jpg", ".jpeg", ".png", ".tiff", ".bmp")):
        mime = "image/png" if lower_name.endswith(".png") else "image/jpeg"
        text, pages = ocr.extract_text(file_bytes, mime)
        return ExtractionResult(
            text=text, physical_pages=pages, used_ocr=True, source_type="image"
        )

    # PDF Files
    if lower_name.endswith(".pdf"):
        text, pages = _extract_text_from_pdf(file_bytes)

        # If significant digital text is present, treat as digital PDF
        if len(text.strip()) >= text_threshold:
            return ExtractionResult(
                text=text,
                physical_pages=pages,
                used_ocr=False,
                source_type="digital_pdf",
            )

        # If there is little to no text (implying a scanned PDF), fallback to OCR
        ocr_text, ocr_pages = ocr.extract_text(file_bytes, "application/pdf")
        return ExtractionResult(
            text=ocr_text,
            physical_pages=ocr_pages,
            used_ocr=True,
            source_type="scanned_pdf",
        )

    raise ValueError(
        f"Unsupported file format: {filename}. Supported formats are: .txt, .pdf, .jpg, .jpeg, .png, .tiff, .bmp"
    )
