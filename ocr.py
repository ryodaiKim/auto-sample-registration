from pdf2image import convert_from_path
import pytesseract

from config import OCR_DPI, OCR_LANG


def ocr_pdf(pdf_path: str, dpi: int = OCR_DPI, lang: str = OCR_LANG) -> str:
    """Convert PDF pages to images and OCR each page via tesseract."""
    images = convert_from_path(pdf_path, dpi=dpi)
    pages = [pytesseract.image_to_string(img, lang=lang) for img in images]
    return "\n".join(pages)
