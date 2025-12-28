class AppError(Exception):
    """Base error class for the application."""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)

class ConflictError(AppError):
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(message, status_code=409)

class ValidationError(AppError):
    def __init__(self, message: str = "Validation failed"):
        super().__init__(message, status_code=422)

# Domain Specific
class AppointmentNotFoundException(NotFoundError):
    pass

class PatientNotFoundException(NotFoundError):
    pass

class DoctorNotFoundException(NotFoundError):
    pass

class SlotUnavailableException(ConflictError):
    pass
