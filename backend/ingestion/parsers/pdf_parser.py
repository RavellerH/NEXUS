import os
import logging
from datetime import datetime
import fitz  # PyMuPDF
from typing import List, Optional
from ..models import Chunk
from .pid_parser import extract_pid_chunks

logger = logging.getLogger("nexus-pdf-parser")

def is_pid_file(file_path: str, doc_type: Optional[str] = None) -> bool:
    """
    Check if the PDF is a Piping & Instrumentation Diagram (P&ID) file.
    Identifies based on filename heuristics or explicit document type.
    """
    if doc_type == "pid":
        return True
        
    filename = os.path.basename(file_path).lower()
    pid_indicators = ["p&id", "pid", "piping", "instrument", "drawing", "schematic"]
    return any(indicator in filename for indicator in pid_indicators)

def extract_pdf_chunks(
    file_path: str,
    project_id: str,
    authority_level: int = 2,
    doc_type: Optional[str] = None,
    chunk_size_chars: int = 1000
) -> List[Chunk]:
    """
    Extracts text sections or routes P&ID drawings to tag extraction.
    Addresses T11: Detects and warns about scanned, image-only PDFs instead of failing silently.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")
        
    # Check if this is a P&ID sheet and route accordingly
    if is_pid_file(file_path, doc_type):
        logger.info(f"Routing {file_path} to P&ID parser for instrument tag extraction.")
        return extract_pid_chunks(file_path, project_id, authority_level)

    filename = os.path.basename(file_path)
    logger.info(f"Parsing standard PDF: {filename}")
    
    try:
        doc = fitz.open(file_path)
    except Exception as e:
        logger.error(f"Failed to open PDF {file_path}: {str(e)}")
        raise e

    chunks: List[Chunk] = []
    chunk_index = 0
    total_text_len = 0
    
    # We acquire modification time of the file to use as the document date/timestamp
    mtime = os.path.getmtime(file_path)
    doc_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")

    for page_num in range(len(doc)):
        page = doc[page_num]
        page_text = page.get_text("text").strip()
        total_text_len += len(page_text)
        
        if not page_text:
            logger.debug(f"Page {page_num + 1} of {filename} has no readable text.")
            continue
            
        # Parse paragraphs within the page
        paragraphs = [p.strip() for p in page_text.split("\n\n") if p.strip()]
        
        current_chunk_text = ""
        section_title = f"Page {page_num + 1}"
        
        # Determine if we have a section heading style
        # Simple heuristic: first short paragraph is treated as section title
        if paragraphs and len(paragraphs[0]) < 100:
            section_title = paragraphs[0]
            paragraphs = paragraphs[1:]
            
        for para in paragraphs:
            if len(current_chunk_text) + len(para) > chunk_size_chars:
                # Commit current chunk
                if current_chunk_text.strip():
                    chunk = Chunk(
                        content=current_chunk_text.strip(),
                        source_file=filename,
                        source_type="pdf",
                        timestamp=doc_date,
                        authority_level=authority_level,
                        project_id=project_id,
                        chunk_index=chunk_index,
                        section_title=f"Page {page_num + 1} | {section_title}"
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                current_chunk_text = para
            else:
                if current_chunk_text:
                    current_chunk_text += "\n" + para
                else:
                    current_chunk_text = para
                    
        # Commit trailing chunk on the page
        if current_chunk_text.strip():
            chunk = Chunk(
                content=current_chunk_text.strip(),
                source_file=filename,
                source_type="pdf",
                timestamp=doc_date,
                authority_level=authority_level,
                project_id=project_id,
                chunk_index=chunk_index,
                section_title=f"Page {page_num + 1} | {section_title}"
            )
            chunks.append(chunk)
            chunk_index += 1

    doc.close()

    # Technical Critique T11 & PRE-001 Check
    # If the PDF contains 0 readable characters, it is an image-only/scanned document.
    # Log a loud warning to inform the user that OCR will be required in Phase 4.
    if total_text_len == 0:
        logger.warning(
            f"[Warning] Scanned PDF Detected: File '{filename}' yielded 0 readable text characters. "
            "Scanned drawing and image-only PDF support requires OCR models deferred to Phase 4."
        )
        
    logger.info(f"Successfully extracted {len(chunks)} text chunks from standard PDF '{filename}'.")
    return chunks
