import os
import re
import logging
from datetime import datetime
import fitz  # PyMuPDF
from typing import List, Set
from ..models import Chunk

logger = logging.getLogger("nexus-pid-parser")

# ISA 5.1 Standard Instrument Tag Pattern
# Matches patterns like: AT-201, FT-101, FCV-302, TIC-101A
# Group 1: Letters (1-4 capital letters)
# Group 2: Loop Number (3-5 digits with optional trailing letter)
PID_TAG_PATTERN = re.compile(
    r'\b([A-Z]{1,4})-(\d{3,5}[A-Z]?)\b'
)

def extract_instrument_tags(text: str) -> List[str]:
    """Find and return all unique instrument tags in the text segment."""
    matches = PID_TAG_PATTERN.findall(text)
    tags = [f"{m[0]}-{m[1]}" for m in matches]
    return sorted(list(set(tags)))

def extract_pid_chunks(
    file_path: str,
    project_id: str,
    authority_level: int = 2,
    context_window_chars: int = 350
) -> List[Chunk]:
    """
    Extracts text windows around unique instrument tags found in a P&ID sheet.
    Addresses D09: Extracts loops and tags to support precise metadata tag-based queries.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"P&ID file not found: {file_path}")
        
    filename = os.path.basename(file_path)
    logger.info(f"Extracting instrument loops from P&ID drawing: {filename}")
    
    try:
        doc = fitz.open(file_path)
    except Exception as e:
        logger.error(f"Failed to open P&ID PDF: {str(e)}")
        raise e

    chunks: List[Chunk] = []
    chunk_index = 0
    total_text_len = 0
    
    # We acquire modification time of the file to use as the document date/timestamp
    mtime = os.path.getmtime(file_path)
    doc_date = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")

    for page_num in range(len(doc)):
        page = doc[page_num]
        page_text = page.get_text("text")
        # Standardize whitespace and remove excessive carriage returns
        page_text_clean = " ".join(page_text.split())
        total_text_len += len(page_text_clean)
        
        if not page_text_clean:
            continue
            
        # Find all match indices on this page
        # To avoid duplicate context overlaps, we first extract all unique tags
        all_tags = extract_instrument_tags(page_text_clean)
        if not all_tags:
            # If no tags are found, fall back to standard page chunking so text is not lost
            logger.info(f"No specific loop tags detected on page {page_num + 1}. Creating fallback page chunk.")
            chunk = Chunk(
                content=f"[P&ID page fallback] {page_text_clean[:1000]}",
                source_file=filename,
                source_type="pid",
                timestamp=doc_date,
                authority_level=authority_level,
                project_id=project_id,
                chunk_index=chunk_index,
                section_title=f"Sheet {page_num + 1} | Fallback Chunk"
            )
            chunks.append(chunk)
            chunk_index += 1
            continue

        logger.info(f"Page {page_num + 1}: Found {len(all_tags)} loop tags: {', '.join(all_tags)}")

        # For each tag, find its matches and extract a context window around it
        for tag in all_tags:
            # Find all indices of this tag in the text
            for match in re.finditer(re.escape(tag), page_text_clean):
                start_idx = match.start()
                end_idx = match.end()
                
                # Determine slice coordinates
                slice_start = max(0, start_idx - context_window_chars)
                slice_end = min(len(page_text_clean), end_idx + context_window_chars)
                
                context_segment = page_text_clean[slice_start:slice_end].strip()
                
                # Highlight and clean up the contextual segment
                # Prepend with a strong structural title
                content_block = (
                    f"[Instrument Loop Tag: {tag} | Sheet: {page_num + 1}]\n"
                    f"... {context_segment} ..."
                )
                
                # Extract any other nested tags present inside this context window
                co_located_tags = extract_instrument_tags(context_segment)
                
                # Create the chunk
                chunk = Chunk(
                    content=content_block,
                    source_file=filename,
                    source_type="pid",
                    timestamp=doc_date,
                    authority_level=authority_level,
                    project_id=project_id,
                    chunk_index=chunk_index,
                    section_title=f"Sheet {page_num + 1} | Tag {tag}",
                    instrument_tags=co_located_tags
                )
                chunks.append(chunk)
                chunk_index += 1

    doc.close()

    # Log scanned warning if drawing text layer is empty (Critique T11 & T10 related)
    if total_text_len == 0:
        logger.warning(
            f"[Warning] Scanned P&ID: P&ID file '{filename}' has no digital text layer. "
            "Scanned drawing/blueprint matching is disabled until Phase 4 OCR is integrated."
        )
        
    logger.info(f"Completed P&ID parsing: generated {len(chunks)} tag context chunks for {filename}.")
    return chunks
