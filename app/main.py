from fastapi import FastAPI
import logging
from app.api.v1.api import api_router
from app.exceptions.handlers import add_exception_handlers
from app.core.config import settings

# Configure logging for deployment
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME, version="1.1.0")

add_exception_handlers(app)

app.include_router(api_router, prefix=settings.API_V1_STR)
