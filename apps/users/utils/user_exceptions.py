from rest_framework.exceptions import APIException


class NotAuthenticatedError(APIException):
    status_code = 401
    default_detail = "자격 인증 데이터가 제공되지 않았습니다."
    default_code = "not_authenticated"


class DuplicateNicknameError(APIException):
    status_code = 409
    default_detail = "중복된 닉네임이 존재합니다."
    default_code = "duplicate_nickname"


class ConflictError(APIException):
    status_code = 409
    default_detail = "이미 중복된 회원 가입 내역이 존재 합니다."
    default_code = "conflict"
