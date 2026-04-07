class IngemarkBaseError(Exception):
    """Base exception for all Ingemark custom exceptions."""

    def __init__(self, message: str = "An error occurred", status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class IngemarkNotFoundError(IngemarkBaseError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)


class IngemarkValidationError(IngemarkBaseError):
    def __init__(self, message: str = "Validation error"):
        super().__init__(message, 422)


class IngemarkUnauthorizedError(IngemarkBaseError):
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, 401)


class IngemarkConflictError(IngemarkBaseError):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message, 409)
