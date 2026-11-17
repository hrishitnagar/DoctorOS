


from pathlib import Path

import fitz  # PyMuPDF
import numpy as np
import pytesseract
from PIL import Image
from sqlalchemy.orm import Session

from app.models.document import Document
from app.services.image_preprocessing import preprocess_image


# Explicit Windows path to Tesseract.
# This is needed because Tesseract is not currently in your PATH.
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract embedded PDF text using PyMuPDF.

    If a page has no embedded text, render it as an image,
    preprocess it, and run Tesseract OCR.
    """
    extracted_pages = []

    with fitz.open(file_path) as pdf:
        for page in pdf:

            # 1. Try extracting embedded text first.
            page_text = page.get_text("text").strip()

            if page_text:
                extracted_pages.append(page_text)
                continue

            # 2. Render scanned PDF page as an image.
            pix = page.get_pixmap(
                matrix=fitz.Matrix(2, 2),
                alpha=False,
            )

            image = Image.frombytes(
                "RGB",
                [pix.width, pix.height],
                pix.samples,
            )

            # 3. Convert image to NumPy array.
            image_array = np.array(image)

            # 4. Preprocess scanned page.
            processed_image = preprocess_image(image_array)

            # 5. Run Tesseract OCR.
            page_text = pytesseract.image_to_string(
                processed_image
            ).strip()

            extracted_pages.append(page_text)

    return "\n\n".join(extracted_pages).strip()


def extract_text_from_file(file_path: str) -> str:
    """
    Extract text from supported PDF and image files.

    Supported:
    - PDF
    - PNG
    - JPG
    - JPEG
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Document file not found: {path}"
        )

    suffix = path.suffix.lower()

    # PDF processing
    if suffix == ".pdf":
        return extract_text_from_pdf(str(path))

    # Image processing
    if suffix in {".png", ".jpg", ".jpeg"}:

        with Image.open(path) as image:

            # Convert image to RGB.
            image = image.convert("RGB")

            # Convert PIL image to NumPy array.
            image_array = np.array(image)

            # Apply preprocessing.
            processed_image = preprocess_image(image_array)

            # Run OCR on preprocessed image.
            extracted_text = pytesseract.image_to_string(
                processed_image
            ).strip()

            return extracted_text

    raise ValueError(
        f"Unsupported file type: {suffix}"
    )


def process_document_ocr(
    db: Session,
    document: Document,
) -> Document:
    """
    Process a document using OCR.

    Updates:
    - Document.raw_text
    - Document.ocr_status
    """
    try:
        # Mark document as processing.
        document.ocr_status = "processing"
        db.commit()

        # Extract text from the document.
        extracted_text = extract_text_from_file(
            document.file_path
        )

        # Update document fields.
        if extracted_text:
            document.raw_text = extracted_text
            document.ocr_status = "done"

        else:
            document.raw_text = None
            document.ocr_status = "failed"

        # Persist changes.
        db.commit()
        db.refresh(document)

        return document

    except Exception:
        # Roll back any incomplete transaction.
        db.rollback()

        # Mark OCR as failed.
        document.ocr_status = "failed"
        db.commit()
        db.refresh(document)

        # Let the API endpoint handle the exception.
        raise
