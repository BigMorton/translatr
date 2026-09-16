import io

from pypdf import PageObject, PdfWriter

from app.services.extractor import MockOcrEngine, process_document


def create_blank_pdf() -> bytes:
    writer = PdfWriter()
    page = PageObject.create_blank_page(width=612, height=792)  # Standard letter size
    writer.add_page(page)
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def test_plain_text_processing():
    sample = b"Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    res = process_document(sample, "document.txt")

    assert res.source_type == "text"
    assert not res.used_ocr
    assert res.physical_pages == 1
    assert "consectetur" in res.text


def test_scanned_pdf_triggers_ocr_fallback():
    # Create a blank PDF to simulate a scanned PDF with no extractable text
    blank_pdf = create_blank_pdf()
    mock_ocr = MockOcrEngine(stub_text="Extracted text from scanned document")

    res = process_document(blank_pdf, "scanned_document.pdf", ocr_engine=mock_ocr)

    assert res.source_type == "scanned_pdf"
    assert res.used_ocr is True
    assert res.text == "Extracted text from scanned document"
    assert res.physical_pages == 1


def test_image_routes_to_ocr():
    dummy_image_bytes = b"\x89PNG\r\n\x1a\nfakeimagedata"
    mock_ocr = MockOcrEngine(stub_text="Extracted text from image")

    res = process_document(dummy_image_bytes, "image.png", ocr_engine=mock_ocr)

    assert res.source_type == "image"
    assert res.used_ocr is True
    assert res.text == "Extracted text from image"


def test_unsupported_file_extension():
    dummy_data_bytes = b"dummy data"
    try:
        process_document(dummy_data_bytes, "unsupported_file.xyz")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Unsupported file format" in str(e)
