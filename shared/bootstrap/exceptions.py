class DetailedError(Exception):
    default_message = None

    def __init__(self, detail=None):
        self.detail = detail or self.default_message
        super().__init__(detail)
