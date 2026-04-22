from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from apps.users.serializers.user import SignupSerializer


class SignupView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({'detail': '회원가입이 완료되었습니다.'}, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({'error_detail': e.detail[0]}, status=status.HTTP_409_CONFLICT)
        return Response({'error_detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)