class NotFoundError(Exception):
    """Raised when an entity cannot be found."""


class ValidationError(Exception):
    """Raised when validation fails inside a use case."""
