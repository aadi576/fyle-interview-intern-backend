class FyleError(Exception):
    def __init__(self, status_code=400, message="An error occurred"):
        super().__init__(message)
        self.status_code = status_code
        self.message = message

    def to_dict(self):
        return {
            'message': self.message,
            'status_code': self.status_code
        }
