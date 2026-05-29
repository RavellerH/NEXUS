import hashlib
from dataclasses import dataclass, field, asdict
from typing import Optional, List

@dataclass
class Chunk:
    content: str
    source_file: str
    source_type: str
    timestamp: str  # ISO 8601 (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)
    authority_level: int
    project_id: str
    chunk_index: int  # Monotonically increasing index within the parsed file
    author: Optional[str] = None
    section_title: Optional[str] = None
    instrument_tags: List[str] = field(default_factory=list)
    chunk_id: str = field(init=False)

    def __post_init__(self):
        """
        Generate a unique, deterministic chunk ID.
        Addresses Critique H11: Hashing content + source + chunk_index ensures absolute 
        idempotency during re-ingestion and prevents duplication inside ChromaDB.
        """
        hash_input = f"{self.source_file}:{self.chunk_index}:{self.content}"
        self.chunk_id = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

    def to_dict(self) -> dict:
        return asdict(self)
