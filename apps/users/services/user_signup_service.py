from typing import Any

from apps.users.models import User

from django.core.cache import cache

from rest_framework.exceptions import ValidationError

from apps.users.serializers.purpose_enum import AuthPurpose

SIGNUP_PURPOSE = AuthPurpose.SIGNUP.value

# 유저 생성에 필요한 로직(토큰에서 이메일/폰번호 꺼내고, 중복 검사하고, DB에 저장)
def create_user(validated_data: dict[str, Any]) -> User:
    email_token = validated_data.pop("email_token")  # 토큰값 꺼냄
    sms_token = validated_data.pop("sms_token")
    password = validated_data.pop("password")

    email_key = f"purpose_{SIGNUP_PURPOSE}_email_verify_token_{email_token}"
    sms_key = f"purpose_{SIGNUP_PURPOSE}_sms_verify_token_{sms_token}"



    email_data = cache.get(email_key) #토큰값으로 redis 조회, 값인 이메일주소 반환
    sms_data = cache.get(sms_key)

    if not email_data:
        raise ValidationError("유효하지 않거나 만료된 이메일 인증입니다.")
    if not sms_data:
        raise ValidationError("유효하지 않거나 만료된 휴대폰 인증입니다.")

    email = email_data.get("email")
    phone_number = sms_data.get("phone_number")

    if User.objects.filter(email=email).exists():
        raise ValidationError("이미 가입된 이메일입니다.")
    if User.objects.filter(phone_number=phone_number).exists():
        raise ValidationError("이미 가입에 사용된 휴대전화 번호입니다.")


    user =User.objects.create_user(
        email=email,
        password=password,
        phone_number=phone_number,
        **validated_data,
    )

    cache.delete(email_key)
    cache.delete(sms_key)

    return user