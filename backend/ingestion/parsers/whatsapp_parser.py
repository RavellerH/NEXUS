import re
import os
import logging
from datetime import datetime
from typing import List, Optional
from ..models import Chunk

logger = logging.getLogger("nexus-whatsapp-parser")

# Regular Expression Patterns
# iOS Format: "[15/03/2024, 09:42:11] Budi Santoso: Sudah confirm dengan vendor"
# Matches: [Date, Time, Author, Message]
IOS_PATTERN = re.compile(
    r'^\[(\d{1,2})[\/\.-](\d{1,2})[\/\.-](\d{2,4}),\s*(\d{1,2}):(\d{2}):?(\d{2})?\]\s*([^:]+):\s*(.*)$'
)

# Android Format: "15/03/2024, 09:42 - Budi Santoso: Sudah confirm dengan vendor"
# Matches: [Date, Time, Author, Message]
ANDROID_PATTERN = re.compile(
    r'^(\d{1,2})[\/\.-](\d{1,2})[\/\.-](\d{2,4}),\s*(\d{1,2}):(\d{2})\s*-\s*([^:]+):\s*(.*)$'
)

class UnsupportedFormatError(Exception):
    """Raised when the WhatsApp export format cannot be auto-detected."""
    pass

class WhatsAppMessage:
    def __init__(self, timestamp: datetime, author: str, content: str):
        self.timestamp = timestamp
        self.author = author
        self.content = content

def parse_date_string(day: str, month: str, year: str, hour: str, minute: str, second: str = "00") -> datetime:
    """Parse date fields safely into datetime supporting both 2-digit and 4-digit years."""
    yr = int(year)
    if yr < 100:
        yr += 2000  # Assume 21st century for 2-digit years
    
    sec = int(second) if second else 0
    return datetime(yr, int(month), int(day), int(hour), int(minute), sec)

def detect_format(lines: List[str]) -> str:
    """
    Auto-detect export format based on first 20 non-empty lines.
    Addresses PRE-001: Auto-detects iOS vs. Android format, fails loudly on unrecognized formats.
    """
    ios_votes = 0
    android_votes = 0
    
    for line in lines[:20]:
        line = line.strip()
        if not line:
            continue
        if IOS_PATTERN.match(line):
            ios_votes += 1
        elif ANDROID_PATTERN.match(line):
            android_votes += 1
            
    if ios_votes > android_votes and ios_votes > 0:
        return "ios"
    elif android_votes > ios_votes and android_votes > 0:
        return "android"
    
    raise UnsupportedFormatError(
        "Unable to auto-detect WhatsApp export format. "
        "File must follow standard iOS [DD/MM/YYYY, HH:MM:SS] or Android DD/MM/YYYY, HH:MM format."
    )

def parse_whatsapp_file(file_path: str) -> List[WhatsAppMessage]:
    """Parse raw export text file into parsed WhatsAppMessage structs, handling multi-line messages."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"WhatsApp export file not found: {file_path}")
        
    with open(file_path, "r", encoding="utf-8-sig") as f:
        lines = f.readlines()
        
    fmt = detect_format(lines)
    logger.info(f"Detected WhatsApp export format: {fmt.upper()} for {file_path}")
    
    pattern = IOS_PATTERN if fmt == "ios" else ANDROID_PATTERN
    parsed_messages: List[WhatsAppMessage] = []
    
    current_message: Optional[WhatsAppMessage] = None
    
    for line_num, line in enumerate(lines, 1):
        line_str = line.strip()
        if not line_str:
            continue
            
        match = pattern.match(line)
        if match:
            # Commit the previous multi-line message if accumulated
            if current_message:
                # Filter out standard media omitted and call/encryption logs
                if not is_system_or_empty(current_message):
                    parsed_messages.append(current_message)
            
            # iOS: [day, month, year, hour, minute, second, author, content]
            # Android: [day, month, year, hour, minute, author, content]
            groups = match.groups()
            if fmt == "ios":
                day, month, year, hour, minute, second, author, content = groups
            else:
                day, month, year, hour, minute, author, content = groups
                second = "00"
                
            try:
                timestamp = parse_date_string(day, month, year, hour, minute, second)
                current_message = WhatsAppMessage(timestamp, author.strip(), content.strip())
            except ValueError as e:
                # If parsing date fails, treat line as multi-line continuation of previous message
                logger.warning(f"Line {line_num}: Failed to parse date: {str(e)}. Treating as continuation.")
                if current_message:
                    current_message.content += f"\n{line_str}"
        else:
            # Multi-line message continuation
            if current_message:
                current_message.content += f"\n{line_str}"
            else:
                logger.warning(f"Line {line_num}: Unmatched floating text before first message. Ignored.")
                
    # Commit final message
    if current_message and not is_system_or_empty(current_message):
        parsed_messages.append(current_message)
        
    return parsed_messages

def is_system_or_empty(msg: WhatsAppMessage) -> bool:
    """Detects and filters out non-content system messages."""
    content = msg.content.lower()
    # Omitted media indicators
    if "media omitted" in content or "file omitted" in content or "gambar tidak disertakan" in content:
        return True
    # Group actions/status messages
    if "joined using this group's invite link" in content:
        return True
    if "messages and calls are end-to-end encrypted" in content:
        return True
    if not msg.content.strip():
        return True
    return False

def extract_chunks(
    file_path: str,
    project_id: str,
    authority_level: int = 4,
    last_ingested_ts: Optional[datetime] = None,
    window_size: int = 15,
    overlap: int = 5
) -> List[Chunk]:
    """
    Stitches WhatsApp messages into overlapping conversation context windows.
    Addresses T12: Implements overlapping context windows to preserve conversational flow.
    """
    messages = parse_whatsapp_file(file_path)
    
    # Incremental filtering
    if last_ingested_ts:
        messages = [m for m in messages if m.timestamp > last_ingested_ts]
        logger.info(f"Incremental mode: Filtered down to {len(messages)} new messages.")
        
    if not messages:
        return []
        
    chunks: List[Chunk] = []
    chunk_index = 0
    filename = os.path.basename(file_path)
    
    # Overlapping Sliding Window Implementation
    # Slide over message index using window_size and step (window_size - overlap)
    step = max(1, window_size - overlap)
    
    for i in range(0, len(messages), step):
        window_msgs = messages[i:i + window_size]
        if not window_msgs:
            break
            
        # Compile contextual elements
        participants = sorted(list(set(m.author for m in window_msgs)))
        start_ts = window_msgs[0].timestamp.isoformat()
        
        # Build segment header
        header = f"[Participants: {', '.join(participants)} | Time: {start_ts}]\n"
        
        # Stitched content
        body_lines = []
        for m in window_msgs:
            timestamp_str = m.timestamp.strftime("%Y-%m-%d %H:%M")
            body_lines.append(f"<{m.author} at {timestamp_str}>: {m.content}")
            
        stitched_content = header + "\n".join(body_lines)
        
        # Create chunk
        chunk = Chunk(
            content=stitched_content,
            source_file=filename,
            source_type="whatsapp",
            timestamp=start_ts,
            authority_level=authority_level,
            project_id=project_id,
            chunk_index=chunk_index,
            author=window_msgs[-1].author  # Set primary author as the last speaker in segment
        )
        chunks.append(chunk)
        chunk_index += 1
        
    return chunks
