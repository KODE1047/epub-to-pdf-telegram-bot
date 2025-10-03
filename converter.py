# converter.py
import os
import asyncio
from typing import List
import ebooklib
from ebooklib import epub
from xhtml2pdf import pisa

def _extract_html_content(book: epub.EpubBook) -> str:
    """Extracts and combines all HTML content from an EPUB book."""
    html_parts: List[str] = []
    
    # Basic CSS to ensure page breaks between chapters
    css = """
    <style>
        @media print {
            .page-break {
                page-break-after: always;
            }
        }
    </style>
    """
    html_parts.append(css)
    
    # Iterate through all documents in the EPUB spine (the ordered content)
    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        # Decode content to a UTF-8 string, ignoring errors
        content = item.get_content().decode('utf-8', 'ignore')
        html_parts.append(content)
        # Add a page break element after each chapter/document
        html_parts.append('<div class="page-break"></div>')
        
    return "".join(html_parts)

async def convert_epub_to_pdf(epub_path: str) -> str:
    """
    Converts an EPUB file to a PDF file.
    
    Args:
        epub_path: The file path of the input EPUB.
        
    Returns:
        The file path of the output PDF.
        
    Raises:
        Exception: If the conversion process fails.
    """
    pdf_path = epub_path.replace(".epub", ".pdf")
    
    try:
        # Run synchronous, CPU/IO-bound code in a separate thread to avoid blocking
        # the asyncio event loop.
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None, _perform_conversion, epub_path, pdf_path
        )
        return pdf_path
    except Exception as e:
        # If the PDF was partially created, clean it up
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        # Re-raise the exception to be handled by the bot logic
        raise e

def _perform_conversion(epub_path: str, pdf_path: str):
    """Synchronous helper function that performs the actual conversion."""
    book = epub.read_epub(epub_path)
    combined_html = _extract_html_content(book)

    with open(pdf_path, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(combined_html, dest=pdf_file)

    if pisa_status.err:
        raise Exception(f"PDF conversion failed with {pisa_status.err} errors.")