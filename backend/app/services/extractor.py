import io
import os
from dataclasses import dataclass
from typing import Protocol, Any
from google.cloud import vision

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

class GoogleVisionEngine:
    """ Production OCR engine powered by Google Cloud Vision API.

    Uses DOCUMENT_TEXT_DETECTION for PDFs and TEXT_DETECTION for images. Returns the extracted text and the number of pages processed.
    """
    def __init__(self, client: Any | None = None) -> None:
        if client:
            self.client = client
        else:
            # Expects GOOGLE_APPLICATION_CREDENTIALS pointing to service_account.json
            self.client = vision.ImageAnnotatorClient()

    def extract_text(self, file_bytes: bytes, mime_type: str) -> tuple[str, int]:
        """ Sends raw bytes to Google Vision API for OCR processing. 
        
        Returns the extracted text and page count.
        """
        image = vision.Image(content=file_bytes)


        # Use DOCUMENT_TEXT_DETECTION for text extraction from PDFs and images
        response = self.client.document_text_detection(image=image)

        if response.error.message:
            raise RuntimeError(
                f"Google Vision API error: {response.error.message}"
            )

        full_text_annotation = response.full_text_annotation
        extracted_text = (
            full_text_annotation.text 
            if full_text_annotation
            else ""
        ).strip()

        # --- DEBUG LOGGING ---
        print("\n" + "=" * 50)
        print(f"[DEBUG OCR RAW LENGTH]: {len(extracted_text)} chars")
        print(f"[DEBUG OCR REPR]: {repr(extracted_text)}")
        print("-" * 50)
        print(f"[DEBUG OCR TEXT]:\n{extracted_text}")
        print("=" * 50 + "\n")
        # ---------------------


        # Determine page count based on the number of pages in the response (defaults to 1)
        phyiscal_pages = (
            len(full_text_annotation.pages)
            if (full_text_annotation and full_text_annotation.pages) 
            else 1
        )

        return extracted_text, phyiscal_pages


class MockOcrEngine:
    """ Mock local OCR engine for testing and dev purposes """
    def __init__(self, stub_text: str = "Mock extracted text"):
        self.stub_text = stub_text

    def extract_text(self, file_bytes: bytes, mime_type: str) -> tuple[str, int]:
        # Mock implementation for testing purposes
        return self.stub_text, 1


def get_ocr_engine() -> OcrEngine:
    """Factory function to get the appropriate OCR engine based on environment."""
    engine_type = os.getenv("OCR_ENGINE", "mock").lower()
    if engine_type == "google":
        return GoogleVisionEngine()
    return MockOcrEngine()

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
    ocr = ocr_engine if ocr_engine is not None else get_ocr_engine()

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
