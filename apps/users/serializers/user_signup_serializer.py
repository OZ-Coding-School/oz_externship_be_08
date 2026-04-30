import re
from typing import Any

from rest_framework import serializers

from apps.users.models import User
from apps.users.services.user_signup_service import create_user


class SignupSerializer(serializers.ModelSerializer["User"]):
    email_token = serializers.CharField(write_only=True)
    sms_token = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "password",
            "nickname",
            "name",
            "birthday",
            "gender",
            "email_token",
            "sms_token",
        ]
        extra_kwargs: dict[str, dict[str, Any]] = {
            "nickname": {"validators": []},
        }

    def validate_nickname(self, value: str) -> str:
        if not re.match(r"^[가-힣a-zA-Z0-9]{2,10}$", value):
            raise serializers.ValidationError("닉네임은 2~10자 이내, 특수문자 제외, 한글/영문/숫자만 허용됩니다.")
        return value

    def validate_password(self, value: str) -> str:
        if not re.match(r"^\S{6,15}$", value):
            raise serializers.ValidationError("비밀번호는 6~15자여야 합니다.")
        if not re.search(r"[a-zA-Z]", value):
            raise serializers.ValidationError("비밀번호는 영문을 포함해야 합니다.")
        if not re.search(r"[0-9]", value):
            raise serializers.ValidationError("비밀번호는 숫자를 포함해야 합니다.")
        if not re.search(r"[!@#$%^&*]", value):
            raise serializers.ValidationError("비밀번호는 특수문자를 포함해야 합니다.")
        return value

    def create(self, validated_data: dict[str, str]) -> User:
        return create_user(validated_data)
