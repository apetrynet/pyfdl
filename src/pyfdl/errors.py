class FDLError(Exception):
    pass


class FDLValidationError(FDLError):
    pass


class UnknownHandlerError(FDLError):
    pass
