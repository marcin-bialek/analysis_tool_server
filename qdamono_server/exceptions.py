class SessionStateError(RuntimeError):
    pass


class InvalidEventError(ValueError):
    pass


class DocumentError(RuntimeError):
    pass


class DocumentNotFoundError(DocumentError):
    pass


class DuplicateDocumentError(DocumentError):
    pass


class AuthorizationError(RuntimeError):
    pass
