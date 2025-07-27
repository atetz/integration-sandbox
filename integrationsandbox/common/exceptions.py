class ValidationError(Exception):
    """Invalid input data or business rule violation"""

    pass


class NotFoundError(Exception):
    """Requested entity not found"""

    pass
