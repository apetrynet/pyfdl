class FDLError(Exception):
    pass


class FDLValidationError(FDLError):
    pass


class UnsupportedHandlerError(FDLError):
    pass
