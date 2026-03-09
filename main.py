import logging
import sys
from fastapi import FastAPI
from app.config import settings
from app.routes.base import router as base_router
from app.routes.enrich import router as enrich_router
from app.routes.bulk import router as bulk_router

# Force unbuffered output
sys.stdout = sys.stderr

# Configurar logging para ver prints
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)
logger.info("Starting application...")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION
)

app.include_router(base_router)
app.include_router(enrich_router)
app.include_router(bulk_router)

logger.info("Application ready!")
