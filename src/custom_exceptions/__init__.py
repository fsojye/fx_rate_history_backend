class InvalidOrderException(Exception):
    """Exception raise when order is invalid"""

    def __init__(self, message="One or more product in the order list is not available"):
        super().__init__(message)


class InvalidMessageException(Exception):
    """Exception raise when order is invalid"""

    def __init__(self, message="SQS message is invalid"):
        super().__init__(message)