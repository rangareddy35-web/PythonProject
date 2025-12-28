from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.exceptions.custom import AppError

def add_exception_handlers(app: FastAPI):
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"status": "error", "message": exc.message}
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        # In production, log specific error but return generic message
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Internal Server Error"}
        )
