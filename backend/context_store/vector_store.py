import os
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.utils import embedding_functions
from ..ingestion.models import Chunk
from .database import (
    init_db,
    insert_project,
    insert_document,
    index_chunks_fts,
    delete_document_index,
    delete_chunks_fts,
    query_fts
)

logger = logging.getLogger("nexus-vector-store")

# Initialize SQLite structures at module load
init_db()

# Default built-in lightweight CPU embedding function (ONNX MiniLM-L6-V2)
# Addresses Option A: Extremely light, 0MB Ollama VRAM during host development.
# In production, this can switch to Ollama multilingual-e5-large.
DEFAULT_EF = embedding_functions.DefaultEmbeddingFunction()

class VectorStore:
    def __init__(self, project_id: str, chromadb_path: str = "./data/chromadb") -> None:
        """
        Manages the project-scoped ChromaDB collection and SQLite FTS5 index.
        Addresses D05: Scope-locked per project for secure multi-tenancy.
        """
        self.project_id = project_id
        self.collection_name = f"nexus_project_{project_id}"
        
        # Ensure project metadata exists in SQLite
        insert_project(project_id, f"Project {project_id}")
        
        # Initialize persistent ChromaDB client
        os.makedirs(chromadb_path, exist_ok=True)
        self.client = chromadb.PersistentClient(path=chromadb_path)
        
        # Initialize or fetch the project-scoped collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=DEFAULT_EF
        )
        logger.info(f"Initialized Vector Store client for collection: {self.collection_name}")

    def upsert(self, chunks: List[Chunk]) -> None:
        """
        Add or update chunks concurrently inside ChromaDB and SQLite FTS5.
        Addresses T13: Ensures FTS5 sparse indexing and ChromaDB dense embedding are in-sync.
        """
        if not chunks:
            return
            
        ids = [c.chunk_id for c in chunks]
        documents = [c.content for c in chunks]
        metadatas = []
        
        # Format metadatas safely for ChromaDB (no nested lists allowed in values)
        for c in chunks:
            meta = {
                "source_file": c.source_file,
                "source_type": c.source_type,
                "timestamp": c.timestamp,
                "authority_level": c.authority_level,
                "project_id": c.project_id,
                "chunk_index": c.chunk_index
            }
            if c.author:
                meta["author"] = c.author
            if c.section_title:
                meta["section_title"] = c.section_title
            if c.instrument_tags:
                # Store tags as space-separated string since ChromaDB does not support list metadatas
                meta["instrument_tags"] = " ".join(c.instrument_tags)
            metadatas.append(meta)

        # 1. Upsert into ChromaDB
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        
        # 2. Index in SQLite FTS5 and record document metadata catalog
        serialized_chunks = []
        filename = chunks[0].source_file
        for c in chunks:
            serialized_chunks.append({
                "chunk_id": c.chunk_id,
                "content": c.content,
                "instrument_tags": c.instrument_tags
            })
            
        # Purge existing FTS5 entries to ensure absolute idempotency
        delete_chunks_fts(ids)
        index_chunks_fts(serialized_chunks)
        # Compute dynamic document catalog details
        doc_hash = chunks[0].chunk_id[:32] # Use first chunk SHA256 as document signature signature
        insert_document(
            doc_id=f"doc_{filename}",
            filename=filename,
            file_hash=doc_hash,
            project_id=self.project_id,
            chunk_count=len(chunks)
        )
        logger.info(f"Upserted {len(chunks)} chunks to collection {self.collection_name} and SQLite FTS5.")

    def delete_by_source(self, source_file: str) -> None:
        """
        Remove all document chunks from ChromaDB and FTS5.
        Guarantees re-ingestion idempotency.
        """
        # 1. Delete from ChromaDB by filtering on source_file metadata
        self.collection.delete(where={"source_file": source_file})
        
        # 2. Delete from FTS5 index catalog
        delete_document_index(source_file)
        logger.info(f"Purged all chunks matching source '{source_file}' from vector and FTS5 stores.")

    def delete_collection(self) -> None:
        """Drop the entire project ChromaDB collection."""
        self.client.delete_collection(name=self.collection_name)
        logger.info(f"Dropped ChromaDB collection: {self.collection_name}")

    def query_hybrid(self, query_text: str, n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Unified Hybrid Search using Reciprocal Rank Fusion (RRF).
        Addresses T13: Fuses SQLite FTS5 exact sparse matches and ChromaDB dense semantic matches.
        """
        # 1. Retrieve Dense Vector matches from ChromaDB
        dense_results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        
        dense_ids = dense_results["ids"][0] if dense_results["ids"] else []
        dense_docs = dense_results["documents"][0] if dense_results["documents"] else []
        dense_metas = dense_results["metadatas"][0] if dense_results["metadatas"] else []
        
        # Standardize dense results
        dense_list = []
        for rank, (chunk_id, doc, meta) in enumerate(zip(dense_ids, dense_docs, dense_metas)):
            dense_list.append({
                "chunk_id": chunk_id,
                "content": doc,
                "metadata": meta,
                "rank": rank + 1
            })

        # 2. Retrieve Sparse Keyword matches from SQLite FTS5
        # Search exact alphanumeric loops matching the tags
        sparse_ids = query_fts(query_text, limit=n_results)
        
        # 3. Fuse Results using Reciprocal Rank Fusion (RRF)
        # Score(d) = sum(1 / (k + rank_m(d))) where k = 60
        k = 60
        scores: Dict[str, float] = {}
        chunk_map: Dict[str, Dict[str, Any]] = {}
        
        # Hydrate chunk_map with dense details first
        for item in dense_list:
            chunk_id = item["chunk_id"]
            chunk_map[chunk_id] = item
            # Calculate dense RRF score contribution
            scores[chunk_id] = 1.0 / (k + item["rank"])

        # Hydrate and fuse sparse results
        for rank, chunk_id in enumerate(sparse_ids, 1):
            if chunk_id not in chunk_map:
                # If chunk is only found in sparse FTS5, fetch its details from ChromaDB
                try:
                    # ChromaDB get by ID
                    ch = self.collection.get(ids=[chunk_id])
                    if ch["ids"]:
                        # Convert space-separated string tags back to list for metadata structure
                        meta = ch["metadatas"][0]
                        chunk_map[chunk_id] = {
                            "chunk_id": chunk_id,
                            "content": ch["documents"][0],
                            "metadata": meta,
                            "rank": n_results + 1 # Default penalty rank
                        }
                except Exception:
                    continue
            
            # Add sparse RRF score contribution
            scores[chunk_id] = scores.get(chunk_id, 0.0) + (1.0 / (k + rank))

        # Re-rank according to fused scores descending
        fused_ids = sorted(scores.keys(), key=lambda cid: scores[cid], reverse=True)
        
        final_results = []
        for cid in fused_ids[:n_results]:
            if cid in chunk_map:
                final_results.append(chunk_map[cid])
                
        logger.info(
            f"Hybrid query '{query_text}' completed. "
            f"Merged {len(dense_ids)} dense vectors & {len(sparse_ids)} FTS5 keys."
        )
        return final_results
