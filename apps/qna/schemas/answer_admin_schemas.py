from drf_spectacular.utils import OpenApiResponse, extend_schema

from apps.qna.serializers.admin_answer_serializers import AdminAnswerDeleteSerializer

answer_admin_delete_schema = extend_schema(
    tags=["admin-qna"],
    summary="어드민 댓글 삭제",
    description="어드민 댓글 삭제",
    responses={
        200: AdminAnswerDeleteSerializer,
        400: OpenApiResponse(description="유효하지 않은 답변 삭제 요청입니다."),
        401: OpenApiResponse(description="로그인이 필요합니다."),
        403: OpenApiResponse(description="답변 삭제 권한이 없습니다."),
        404: OpenApiResponse(description="삭제할 답변을 찾을 수 없습니다."),
    },
)
