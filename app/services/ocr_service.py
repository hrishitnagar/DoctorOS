



from pathlib import Path

import fitz  # PyMuPDF
import numpy as np
import pytesseract
from PIL import Image
from sqlalchemy.orm import Session

from app.models.document import Document
from app.services.image_preprocessing import preprocess_image


# Explicit Windows path to Tesseract.
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def extract_pages_from_pdf(file_path: str) -> list[tuple[int, str]]:
    """
    Extract text page by page.

    Uses embedded PDF text first. If a page has no embedded
    text, renders that page and runs Tesseract OCR.

    Returns:
        [(1, "page one text"), (2, "page two text"), ...]
    """
    extracted_pages = []

    with fitz.open(file_path) as pdf:
        for page_number, page in enumerate(pdf, start=1):

            page_text = page.get_text("text").strip()

            if not page_text:
                pix = page.get_pixmap(
                    matrix=fitz.Matrix(2, 2),
                    alpha=False,
                )

                image = Image.frombytes(
                    "RGB",
                    [pix.width, pix.height],
                    pix.samples,
                )

                image_array = np.array(image)
                processed_image = preprocess_image(image_array)

                page_text = pytesseract.image_to_string(
                    processed_image
                ).strip()

            extracted_pages.append((page_number, page_text))

    return extracted_pages


def extract_pages_from_file(
    file_path: str,
) -> list[tuple[int, str]]:
    """
    Extract page-aware text from supported files.

    PDF pages retain their original page numbers.
    Image files are treated as page 1.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Document file not found: {path}"
        )

    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return extract_pages_from_pdf(str(path))

    if suffix in {".png", ".jpg", ".jpeg"}:

        with Image.open(path) as image:
            image = image.convert("RGB")

            image_array = np.array(image)
            processed_image = preprocess_image(image_array)

            extracted_text = pytesseract.image_to_string(
                processed_image
            ).strip()

            return [(1, extracted_text)]

    raise ValueError(
        f"Unsupported file type: {suffix}"
    )


def extract_text_from_pdf(file_path: str) -> str:
    """
    Backward-compatible PDF extraction function.

    Keeps page boundaries using form-feed separators.
    """
    pages = extract_pages_from_pdf(file_path)

    return "\n\f\n".join(
        text for _, text in pages
    ).strip()


def extract_text_from_file(file_path: str) -> str:
    """
    Backward-compatible text extraction function.
    """
    pages = extract_pages_from_file(file_path)

    return "\n\f\n".join(
        text for _, text in pages
    ).strip()


def process_document_ocr(
    db: Session,
    document: Document,
) -> Document:
    """
    Process a document using page-aware OCR.

    Updates:
    - Document.raw_text
    - Document.ocr_status

    Page boundaries are retained using form-feed separators.
    """
    try:
        document.ocr_status = "processing"
        db.commit()

        pages = extract_pages_from_file(
            document.file_path
        )

        extracted_text = "\n\f\n".join(
            page_text for _, page_text in pages
        ).strip()

        if extracted_text:
            document.raw_text = extracted_text
            document.ocr_status = "done"
        else:
            document.raw_text = None
            document.ocr_status = "failed"

        db.commit()
        db.refresh(document)

        return document

    except Exception:
        db.rollback()

        try:
            failed_document = (
                db.query(Document)
                .filter(Document.id == document.id)
                .first()
            )

            if failed_document is not None:
                failed_document.ocr_status = "failed"
                db.commit()

        except Exception:
            db.rollback()

        raise

