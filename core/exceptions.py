from fastapi import HTTPException


class CustomException(HTTPException):
    """Custom exception class for application-specific errors"""
    
    def __init__(self, status_code: int, message: str, detail: str = None):
        self.status_code = status_code
        self.message = message
        self.detail = detail
        super().__init__(status_code=status_code, detail=message)


class ValidationException(CustomException):
    def __init__(self, message: str = "Validation error", detail: str = None):
        super().__init__(status_code=400, message=message, detail=detail)


class NotFoundException(CustomException):
    def __init__(self, message: str = "Resource not found", detail: str = None):
        super().__init__(status_code=404, message=message, detail=detail)


class UnauthorizedException(CustomException):
    def __init__(self, message: str = "Unauthorized", detail: str = None):
        super().__init__(status_code=401, message=message, detail=detail)
