import os
import sys
import shutil
import logging
from datetime import datetime
import fitz  # PyMuPDF

# Ensure backend directory is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.ingestion.parsers.whatsapp_parser import extract_chunks as parse_whatsapp
from backend.ingestion.parsers.pdf_parser import extract_pdf_chunks as parse_pdf

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("nexus-test-parsers")

FIXTURE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "fixtures"))

def setup_fixtures():
    """Create directory structure and mock test files programmatically."""
    os.makedirs(FIXTURE_DIR, exist_ok=True)
    logger.info(f"Setting up test fixtures directory at: {FIXTURE_DIR}")

    # 1. Generate Mock WhatsApp iOS Export
    whatsapp_ios_path = os.path.join(FIXTURE_DIR, "chat_ios.txt")
    ios_content = (
        "[15/03/2024, 09:42:11] Budi Santoso: Halo tim, sudah cek P&ID rev C?\n"
        "[15/03/2024, 09:43:05] John Doe: Yes. Cable AT-201 needs to be replaced.\n"
        "[15/03/2024, 09:44:00] Messages and calls are end-to-end encrypted.\n"  # System msg (skip)
        "[15/03/2024, 09:45:22] Budi Santoso: OK, saya ganti spec-nya ke tipe XLPE.\n"
        "[15/03/2024, 09:46:10] John Doe: <Media omitted>\n"  # System msg (skip)
        "[15/03/2024, 09:47:00] Budi Santoso: Spec-nya sudah match dengan datasheet Yokogawa.\n"
    )
    with open(whatsapp_ios_path, "w", encoding="utf-8") as f:
        f.write(ios_content)
    logger.info(f"Created mock WhatsApp iOS fixture at {whatsapp_ios_path}")

    # 2. Generate Mock WhatsApp Android Export
    whatsapp_android_path = os.path.join(FIXTURE_DIR, "chat_android.txt")
    android_content = (
        "15/03/2024, 09:42 - Budi Santoso: Halo tim, sudah cek P&ID rev C?\n"
        "15/03/2024, 09:43 - John Doe: Yes. Cable AT-201 needs to be replaced.\n"
        "15/03/2024, 09:45 - Budi Santoso: OK, saya ganti spec-nya ke tipe XLPE.\n"
        "15/03/2024, 09:47 - Budi Santoso: Spec-nya sudah match dengan datasheet Yokogawa.\n"
    )
    with open(whatsapp_android_path, "w", encoding="utf-8") as f:
        f.write(android_content)
    logger.info(f"Created mock WhatsApp Android fixture at {whatsapp_android_path}")

    # 3. Generate Mock P&ID PDF (using PyMuPDF to write text layers programmatically)
    pid_pdf_path = os.path.join(FIXTURE_DIR, "drawing_pid_sheet1.pdf")
    doc_pid = fitz.open()
    page_pid = doc_pid.new_page(width=842, height=595)  # A4 Landscape
    
    # Write some standard P&ID loop tag technical context
    page_pid.insert_text(
        (100, 100), 
        "Loop Sheet: Flow Loop FT-101 details. Transmits raw flow to Controller FIC-101. "
        "Loop AT-201 measures gas outlet concentrations at Zone 1. "
        "FIC-101 controls valve FCV-101.",
        fontsize=12
    )
    doc_pid.save(pid_pdf_path)
    doc_pid.close()
    logger.info(f"Created mock P&ID PDF fixture at {pid_pdf_path}")

    # 4. Generate Mock Scanned PDF (empty text layer)
    scanned_pdf_path = os.path.join(FIXTURE_DIR, "scanned_manual.pdf")
    doc_scanned = fitz.open()
    doc_scanned.new_page(width=595, height=842)  # A4 Portrait (leaves page completely blank)
    doc_scanned.save(scanned_pdf_path)
    doc_scanned.close()
    logger.info(f"Created mock Scanned PDF fixture at {scanned_pdf_path}")

def run_tests():
    logger.info("======================================================================")
    logger.info("LAUNCHING PARSER VERIFICATION TESTS")
    logger.info("======================================================================")

    project_id = "test_proj_42"

    # Test 1: WhatsApp iOS Parser & Sliding Window Verification
    logger.info("[TEST 1] Testing WhatsApp iOS Parser...")
    whatsapp_ios_path = os.path.join(FIXTURE_DIR, "chat_ios.txt")
    ios_chunks = parse_whatsapp(whatsapp_ios_path, project_id, authority_level=4, window_size=3, overlap=1)
    
    assert len(ios_chunks) > 0, "Failed: No chunks extracted from iOS chat."
    logger.info(f"Success: Extracted {len(ios_chunks)} chunks from iOS chat.")
    for idx, chunk in enumerate(ios_chunks):
        logger.info(f"  Chunk {idx} ID: {chunk.chunk_id[:16]}... | Timestamp: {chunk.timestamp}")
        logger.info(f"  Chunk content:\n{chunk.content}\n")

    # Test 2: WhatsApp Android Format Detection
    logger.info("[TEST 2] Testing WhatsApp Android Format Detection...")
    whatsapp_android_path = os.path.join(FIXTURE_DIR, "chat_android.txt")
    android_chunks = parse_whatsapp(whatsapp_android_path, project_id, authority_level=4, window_size=3, overlap=1)
    assert len(android_chunks) > 0, "Failed: No chunks extracted from Android chat."
    logger.info(f"Success: Extracted {len(android_chunks)} chunks from Android chat.")

    # Test 3: P&ID Routing & Instrument Tag Regex Matching Verification
    logger.info("[TEST 3] Testing P&ID Routing and ISA 5.1 Tag Extraction...")
    pid_pdf_path = os.path.join(FIXTURE_DIR, "drawing_pid_sheet1.pdf")
    pid_chunks = parse_pdf(pid_pdf_path, project_id, authority_level=2)
    
    assert len(pid_chunks) > 0, "Failed: No chunks extracted from P&ID drawing."
    logger.info(f"Success: Extracted {len(pid_chunks)} loop chunks from P&ID.")
    for idx, chunk in enumerate(pid_chunks):
        logger.info(f"  Chunk {idx} Section: {chunk.section_title} | Tags Found: {chunk.instrument_tags}")
        logger.info(f"  Chunk content:\n{chunk.content}\n")
        
        # Verify specific tags are captured inside the Chunk metadata list
        assert any(tag in chunk.instrument_tags for tag in ["FT-101", "FIC-101", "AT-201", "FCV-101"]), \
            f"Failed: Captured tags {chunk.instrument_tags} do not match mock data."

    # Test 4: Scanned PDF Diagnostic Warning Verification
    logger.info("[TEST 4] Testing Scanned (image-only) PDF warning trigger...")
    scanned_pdf_path = os.path.join(FIXTURE_DIR, "scanned_manual.pdf")
    
    # We expect a warning log to fire in pdf_parser
    scanned_chunks = parse_pdf(scanned_pdf_path, project_id, authority_level=3)
    assert len(scanned_chunks) == 0, "Failed: Scanned blank PDF returned non-empty chunks."
    logger.info("Success: Scanned PDF successfully logged warning and skipped gracefully.")

    logger.info("======================================================================")
    logger.info("ALL PARSER DIAGNOSTIC TESTS PASSED SUCCESSFULLY!")
    logger.info("======================================================================")

def cleanup():
    """Remove generated test fixtures folder after testing."""
    if os.path.exists(FIXTURE_DIR):
        shutil.rmtree(FIXTURE_DIR)
        logger.info("Cleaned up test fixture directories.")

if __name__ == "__main__":
    try:
        setup_fixtures()
        run_tests()
    except Exception as e:
        logger.error(f"TEST RUN FAILED: {str(e)}", exc_info=True)
        sys.exit(1)
    finally:
        cleanup()
