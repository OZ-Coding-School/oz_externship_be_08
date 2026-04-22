from typing import Any

from apps.users.models import User


# 유저 생성에 필요한 로직(토큰에서 이메일/폰번호 꺼내고, 중복 검사하고, DB에 저장)
def create_user(validated_data: dict[str, Any]) -> User:
    email_token = validated_data.pop("email_token")  # 토큰값 꺼냄
    sms_token = validated_data.pop("sms_token")
    password = validated_data.pop("password")

    # TODO: 토큰으로 교체해주시면 됩니다.
    # email = cache.get(f"email_token:{email_token}") #토큰값으로 redis 조회, 값인 이메일주소 반환
    # phone_number = cache.get(f"sms_token:{sms_token}")
    email = "email@email.com"
    phone_number = "01012345678"

    return User.objects.create_user(
        email=email,
        password=password,
        phone_number=phone_number,
        **validated_data,
    )
