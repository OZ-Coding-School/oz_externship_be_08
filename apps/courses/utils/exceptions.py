from rest_framework import status
from rest_framework.exceptions import APIException, NotFound


class SubjectBadRequestError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "유효하지 않은 과목 생성 요청입니다."


class CourseNotFoundError(NotFound):
    default_detail = "해당 과정을 찾을 수 없습니다."


class CohortNotFoundError(NotFound):
    default_detail = "기수를 찾을 수 없습니다."


class SubjectNotFoundError(NotFound):
    default_detail = "해당 과목을 찾을 수 없습니다."


class SubjectDuplicateTitleError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "동일한 이름의 과목이 이미 존재합니다."


class CourseAlreadyExistsError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = "이미 등록된 과정명입니다."
