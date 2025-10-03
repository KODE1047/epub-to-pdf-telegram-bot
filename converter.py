# converter.py
import os
import asyncio
import base64
from typing import List
import ebooklib
from ebooklib import epub
from xhtml2pdf import pisa
from bs4 import BeautifulSoup

def _extract_and_embed_images(book: epub.EpubBook) -> str:
    """
    Extracts HTML content and embeds images as Base64 data URIs.
    """
    html_parts: List[str] = []
    
    css = """
    <style>
        @media print {
            .page-break { page-break-after: always; }
            img { max-width: 100%; height: auto; }
        }
    </style>
    """
    html_parts.append(css)

    images = {item.get_name(): item for item in book.get_items_of_type(ebooklib.ITEM_IMAGE)}

    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
        content = item.get_content().decode('utf-8', 'ignore')
        soup = BeautifulSoup(content, 'html.parser')

        for img_tag in soup.find_all('img'):
            src = img_tag.get('src')
            # Normalize path for lookup
            normalized_src = os.path.basename(src)
            
            if src and (src in images or normalized_src in images):
                # Try original src first, then normalized basename
                image_item = images.get(src) or images.get(normalized_src)
                if not image_item:
                    continue
                    
                # --- THIS IS THE CORRECTED LINE ---
                mime_type = image_item.media_type
                image_data = image_item.get_content()
                
                base64_data = base64.b64encode(image_data).decode('utf-8')
                data_uri = f"data:{mime_type};base64,{base64_data}"
                img_tag['src'] = data_uri

        html_parts.append(str(soup))
        html_parts.append('<div class="page-break"></div>')
        
    return "".join(html_parts)


async def convert_epub_to_pdf(epub_path: str) -> str:
    """
    Converts an EPUB file to a PDF file.
    """
    pdf_path = epub_path.replace(".epub", ".pdf")
    
    try:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None, _perform_conversion, epub_path, pdf_path
        )
        return pdf_path
    except Exception as e:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        raise e

def _perform_conversion(epub_path: str, pdf_path: str):
    """Synchronous helper function that performs the actual conversion."""
    book = epub.read_epub(epub_path)
    combined_html = _extract_and_embed_images(book)

    with open(pdf_path, "wb") as pdf_file:
        pisa_status = pisa.CreatePDF(combined_html, dest=pdf_file, link_callback=lambda uri, rel: uri)

    if pisa_status.err:
        raise Exception(f"PDF conversion failed with {pisa_status.err} errors.")