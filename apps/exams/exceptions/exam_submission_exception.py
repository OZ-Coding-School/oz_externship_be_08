class UserSubmissionNotFound(Exception):
    def __init__(self, message: str = "해당 시험 정보를 찾을 수 없습니다."):
        super().__init__(message)


class DeploymentNotFound(Exception):
    def __init__(self, message: str = "해당 시험 정보를 찾을 수 없습니다."):
        super().__init__(message)


class SubmissionAlreadyExists(Exception):
    def __init__(self, message: str = "이미 제출된 시험입니다."):
        super().__init__(message)
