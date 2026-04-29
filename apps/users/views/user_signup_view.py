from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.serializers.user_signup_serializer import SignupSerializer


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request: Request) -> Response:
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error_detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            serializer.save()
            return Response({"detail": "회원가입이 완료되었습니다."}, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error_detail": e.detail}, status=status.HTTP_409_CONFLICT)
