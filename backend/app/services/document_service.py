"""
Document processing service — PDF and TXT text extraction.
"""
import logging
import re
from io import BytesIO
from typing import Tuple

logger = logging.getLogger(__name__)

# Max characters to store/use as context
MAX_CONTENT_LENGTH = 50_000


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file using PyPDF2."""
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        pages_text = []
        for page_num, page in enumerate(reader.pages):
            try:
                text = page.extract_text()
                if text:
                    pages_text.append(text.strip())
            except Exception as e:
                logger.warning(f"Could not extract page {page_num}: {e}")
        return "\n\n".join(pages_text)
    except ImportError:
        raise RuntimeError("PyPDF2 is not installed. Run: pip install PyPDF2")
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        raise RuntimeError(f"Could not read PDF: {str(e)}")


def extract_text_from_txt(file_bytes: bytes) -> str:
    """Extract text from a plain text file."""
    encodings = ["utf-8", "latin-1", "cp1252"]
    for enc in encodings:
        try:
            return file_bytes.decode(enc)
        except UnicodeDecodeError:
            continue
    raise RuntimeError("Could not decode text file. Unsupported encoding.")


def clean_text(text: str) -> str:
    """Clean and normalize extracted text."""
    # Remove excessive whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    # Remove null bytes and non-printable chars (except newlines)
    text = re.sub(r"[^\x09\x0A\x0D\x20-\x7E\x80-\xFF]", " ", text)
    return text.strip()


def process_document(file_bytes: bytes, filename: str, content_type: str) -> Tuple[str, str]:
    """
    Process an uploaded document and return (extracted_text, file_type).
    Supports PDF and TXT files.
    """
    filename_lower = filename.lower()

    if filename_lower.endswith(".pdf") or "pdf" in content_type:
        file_type = "pdf"
        raw_text = extract_text_from_pdf(file_bytes)
    elif filename_lower.endswith(".txt") or "text/plain" in content_type:
        file_type = "txt"
        raw_text = extract_text_from_txt(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {filename}. Only PDF and TXT files are supported.")

    cleaned = clean_text(raw_text)

    if not cleaned:
        raise ValueError("No readable text could be extracted from this document.")

    # Truncate if too large
    if len(cleaned) > MAX_CONTENT_LENGTH:
        cleaned = cleaned[:MAX_CONTENT_LENGTH] + "\n\n[Content truncated...]"

    return cleaned, file_type
