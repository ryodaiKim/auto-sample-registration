from pdf2image import convert_from_path
import pytesseract

from config import OCR_DPI, OCR_LANG, POPPLER_PATH, TESSERACT_CMD


if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def ocr_pdf(pdf_path: str, dpi: int = OCR_DPI, lang: str = OCR_LANG) -> str:
    """Convert PDF pages to images and OCR each page via tesseract."""
    kwargs = {"dpi": dpi}
    if POPPLER_PATH:
        kwargs["poppler_path"] = POPPLER_PATH
    images = convert_from_path(pdf_path, **kwargs)
    pages = [pytesseract.image_to_string(img, lang=lang) for img in images]
    return "\n".join(pages)
