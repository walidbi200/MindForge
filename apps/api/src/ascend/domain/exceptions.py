class DomainException(Exception):
    """Base exception for all domain errors."""

    pass


class ValidationError(DomainException):
    """Raised when an operation violates domain validation rules (maps to 422/400 depending on context)."""

    pass


class ConflictError(DomainException):
    """Raised when an operation conflicts with existing state (maps to 409)."""

    pass


class NotFoundError(DomainException):
    """Raised when a requested resource or entity cannot be found (maps to 404)."""

    pass


class IntegrityError(DomainException):
    """Raised when an operation violates domain integrity or constraints (maps to 409)."""

    pass


# Specific Collection Exceptions
class DuplicateCollectionError(ConflictError):
    pass


class CollectionNotEmptyError(ConflictError):
    pass


class MembershipAlreadyExistsError(ConflictError):
    pass


class MembershipNotFoundError(NotFoundError):
    pass


class CollectionNotFoundError(NotFoundError):
    pass


# Generic Entity Exceptions
class EntityNotFoundError(NotFoundError):
    pass


class InvalidEntityStateError(ValidationError):
    pass
