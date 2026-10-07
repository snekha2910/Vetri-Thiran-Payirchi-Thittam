class PocketSmartException(Exception):
    def __init__(self, message: str, status_code: int = 400, code: str = "ERROR", details: list = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code
        self.details = details or []

class AuthenticationError(PocketSmartException):
    def __init__(self, message: str = "Authentication failed", details: list = None):
        super().__init__(message, status_code=401, code="AUTHENTICATION_ERROR", details=details)

class AuthorizationError(PocketSmartException):
    def __init__(self, message: str = "Access forbidden", details: list = None):
        super().__init__(message, status_code=403, code="AUTHORIZATION_ERROR", details=details)

class NotFoundError(PocketSmartException):
    def __init__(self, message: str = "Resource not found", details: list = None):
        super().__init__(message, status_code=404, code="NOT_FOUND", details=details)

class ValidationError(PocketSmartException):
    def __init__(self, message: str = "Validation failed", details: list = None):
        super().__init__(message, status_code=422, code="VALIDATION_ERROR", details=details)

class AIProcessingError(PocketSmartException):
    def __init__(self, message: str = "AI generation processing error", details: list = None):
        super().__init__(message, status_code=500, code="AI_PROCESSING_ERROR", details=details)

class InvalidImageError(PocketSmartException):
    def __init__(self, message: str = "Invalid image upload", details: list = None):
        super().__init__(message, status_code=400, code="INVALID_IMAGE", details=details)

class RateLimitExceededError(PocketSmartException):
    def __init__(self, message: str = "Rate limit exceeded. Please try again later.", retry_after: int = 60, details: list = None):
        super().__init__(message, status_code=429, code="RATE_LIMIT_EXCEEDED", details=details)
        self.retry_after = retry_after
