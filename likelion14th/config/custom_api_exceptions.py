from rest_framework.exceptions import APIException

class BaseCustomAPIException(APIException):
    status_code = 500
    default_detail = "An unexpected error occurred."
    default_code = "UNEXPECTED-ERROR"

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        
        if code is None:
            code = self.default_code
        
        super().__init__(detail=detail, code=code)

class ConflictException(BaseCustomAPIException):
    status_code = 409
    default_detail = "A conflict occurred."
    default_code = "CONFLICT"

class PostConflictException(ConflictException):
    default_detail = "A conflict occurred with the post."
    default_code = "POST-CONFLICT"

class TooManyRequestsException(BaseCustomAPIException):
    status_code = 429
    default_detail = "Request limit exceeded."
    default_code = "TOO-MANY-REQUESTS"

class PostLimitExceededException(TooManyRequestsException):
    default_detail = "게시글은 하루에 하나만 작성할 수 있습니다."
    default_code = "POST-LIMIT-EXCEEDED"