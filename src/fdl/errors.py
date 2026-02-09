class FDLError(Exception):
    pass


class FDLValidationError(FDLError):
    pass


class HandlerError(FDLError):
    pass


class UnknownHandlerError(HandlerError):
    pass
