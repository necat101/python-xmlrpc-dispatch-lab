"""Application-level validation errors for the XML-RPC dispatcher."""

class InvalidParams(Exception):
    """Raised when parameters pass arity binding but fail value validation."""
    pass
