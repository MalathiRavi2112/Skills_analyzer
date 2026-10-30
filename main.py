import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.core.config import settings

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("skillgap-nlp")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Preload NLP pipelines
    logger.info("Initializing spaCy matcher and sentence-transformer embedding models...")
    from app.services.extractor import extractor
    from app.services.similarity import similarity_engine
    logger.info(f"Loaded {len(extractor.alias_to_canonical)} skill aliases into PhraseMatcher.")
    logger.info(f"Embedding model ready: {settings.EMBEDDING_MODEL_NAME}")
    yield
    # Shutdown logic if needed
    logger.info("Shutting down NLP microservice.")

app = FastAPI(
    title="SkillGap Analyzer - NLP Microservice",
    description="High-performance NLP service for resume section parsing, spaCy skill extraction, semantic similarity, and weighted scoring.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount endpoints
app.include_router(api_router, prefix="", tags=["NLP Pipeline"])

@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": "nlp-service",
        "environment": settings.ENVIRONMENT,
        "embedding_model": settings.EMBEDDING_MODEL_NAME,
        "spacy_model": settings.SPACY_MODEL
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)

