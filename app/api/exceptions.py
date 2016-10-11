from app import app
from flask import jsonify


class APIError(Exception):
    def __init__(self, code, name, message):
        super(APIError, self).__init__()
        self.code = code
        self.name = name
        self.message = message


@app.errorhandler(APIError)
def handle_invalid_usage(error):
    response = jsonify({
        "code": error.code,
        "name": error.name,
        "message": error.message
    })
    response.status_code = error.code
    return response


class BadRequestError(APIError):
    def __init__(self, name="bad_request", message="요청이 올바르지 않습니다."):
        super(BadRequestError, self).__init__(400, name, message)


class BadContentError(BadRequestError):
    def __init__(self, name="bad_content", message="데이터가 유효하지 않습니다."):
        super(BadContentError, self).__init__(name, message)


class UnauthorizedError(APIError):
    def __init__(self, name='unauthorized', message="권한이 없습니다."):
        super(UnauthorizedError, self).__init__(401, name, message)


class RequiredSignInError(UnauthorizedError):
    def __init__(self, message='로그인 되지 않은 사용자입니다.'):
        super(RequiredSignInError, self).__init__('required_signin', message)


class NotFoundError(APIError):
    def __init__(self, name='not_found', message='데이터가 없습니다.'):
        super(NotFoundError, self).__init__(404, name, message)


class ConflictError(APIError):
    def __init__(self, name='conflict', message='이미 데이터가 존재합니다.'):
        super(ConflictError, self).__init__(409, name, message)
