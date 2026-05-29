import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import chromadb
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexus-api")

app = FastAPI(
    title="NEXUS Context Engine API",
    description="Self-hosted AI context engine for engineering project teams in Southeast Asia.",
    version="1.0.0"
)

# CORS Configuration
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]
if not allowed_origins:
    allowed_origins = ["http://localhost:3000", "http://localhost:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Database Diagnostic
chromadb_path = os.getenv("CHROMADB_PATH", "./data/chromadb")
logger.info(f"Initializing embedded ChromaDB client at {chromadb_path}")
try:
    # Ensure parent directory exists for SQLite storage
    os.makedirs(chromadb_path, exist_ok=True)
    db_client = chromadb.PersistentClient(path=chromadb_path)
    logger.info("ChromaDB persistent client successfully initialized.")
except Exception as e:
    logger.error(f"Failed to initialize ChromaDB: {str(e)}")
    db_client = None


@app.get("/health")
def health_check():
    """
    Service health and diagnostic endpoint.
    Verifies state of embedded ChromaDB and the selected LLM provider.
    """
    # 1. Check ChromaDB Status
    db_status = "error"
    if db_client is not None:
        try:
            # Ping database by fetching version or collection list
            db_client.heartbeat()
            db_status = "ok"
        except Exception:
            db_status = "error"

    # 2. Check LLM Provider configuration
    llm_provider = os.getenv("LLM_PROVIDER", "gemini_api").lower()
    llm_status = "configured"
    
    if llm_provider == "gemini_api":
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            llm_status = "missing_api_key"
        else:
            llm_status = "ok"
            
    elif llm_provider == "ollama":
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        try:
            # Check local Ollama health
            res = requests.get(f"{ollama_url}/api/tags", timeout=2.0)
            if res.status_code == 200:
                llm_status = "ok"
            else:
                llm_status = f"error_http_{res.status_code}"
        except requests.exceptions.RequestException:
            llm_status = "unreachable (dev fallback recommended)"
            
    elif llm_provider == "mock":
        llm_status = "ok"
    else:
        llm_status = "unsupported_provider"

    # Determine overall status
    overall_status = "ok" if (db_status == "ok" and llm_status == "ok") else "degraded"

    return {
        "status": overall_status,
        "services": {
            "chromadb": db_status,
            "llm_provider": f"{llm_provider} ({llm_status})"
        },
        "version": "1.0.0"
    }


@app.get("/")
def read_root():
    return {
        "message": "NEXUS API is running. Go to /docs for interactive documentation."
    }
