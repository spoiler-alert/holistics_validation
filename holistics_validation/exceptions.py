class BadAPIResponse(RuntimeError):
    pass


class ReferencesUndefinedSQL(RuntimeError):
    pass


class FailedValidation(RuntimeError):
    pass


class FailedPublish(RuntimeError):
    pass


class UnexpectedJobStatus(RuntimeError):
    pass
