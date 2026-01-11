from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.exceptions.custom import AppError
import logging

logger = logging.getLogger(__name__)

def add_exception_handlers(app: FastAPI):
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "message": exc.message,
                "error_code": exc.__class__.__name__
            }
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        details = exc.errors()
        body = await request.body()
        # Log the full error and body for debugging
        logger.error(f"Validation error on {request.url}: {details}")
        logger.error(f"Raw Request Body: {body.decode('utf-8', errors='replace')}")
        
        # Simplify the message for the user/AI
        error_messages = []
        for error in details:
            loc = " -> ".join([str(x) for x in error["loc"]])
            msg = error["msg"]
            error_messages.append(f"{loc}: {msg}")
        
        return JSONResponse(
            status_code=422,
            content={
                "status": "error",
                "message": "I'm sorry, I couldn't understand some parts of your request. " + "; ".join(error_messages),
                "details": details
            }
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        # In production, log specific error but return generic message
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Internal Server Error"}
        )
