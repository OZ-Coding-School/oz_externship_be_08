class SubmissionNotFoundError(Exception):
    def __init__(self, message: str = "해당 응시 내역을 찾을 수 없습니다."):
        super().__init__(message)


class SubmissionDeleteNotFoundError(Exception):
    def __init__(self, message: str = "삭제할 응시 내역을 찾을 수 없습니다."):
        super().__init__(message)


class SubmissionConflictError(Exception):
    def __init__(self, message: str = "응시 내역 삭제 처리 중 충돌이 발생했습니다."):
        super().__init__(message)
