import re
from datetime import date
from typing import cast

from rest_framework import serializers

from apps.users.models import User
from apps.users.utils.user_exceptions import DuplicateNicknameError


# 내 정보 조회
class UserInfoSerializer(serializers.ModelSerializer[User]):
    # 수강생인 경우 보여줄 추가 필드
    cohort_id = serializers.SerializerMethodField()
    position = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "nickname",
            "name",
            "phone_number",
            "birthday",
            "gender",
            "profile_img_url",
            "cohort_id",
            "role",
            "position",
            "created_at",
        ]
        read_only_fields = fields

    def get_cohort_id(self, obj: User) -> int | None:
        cohort_student = obj.cohort_students.first()
        # 유저 레코드가 없는 경우 or 레코드는 있는데 cohort FK가 NULL인 경우
        if cohort_student is None or cohort_student.cohort is None:
            return None
        return cohort_student.cohort.id

    def get_position(self, obj: User) -> str | None:
        if obj.training_assistants.exists():
            return "TA"
        if obj.operation_managers.exists():
            return "OM"
        if obj.learning_coachs.exists():
            return "LC"
        if obj.cohort_students.exists() or obj.role == User.Role.STUDENT:
            return "ENROLLED"
        return None


# 내 정보 수정
class UserInfoUpdateSerializer(serializers.ModelSerializer[User]):

    class Meta:
        model = User
        fields = [
            "nickname",
            "name",
            "birthday",
            "gender",
        ]

    # 닉네임 정규식 & 중복 검사(exclude로 사용자가 원래 쓰던 닉네임 제외)
    def validate_nickname(self, value: str) -> str:
        if not re.match(r"^[가-힣a-zA-Z0-9]{2,10}$", value):
            raise serializers.ValidationError("닉네임은 2~10자 이내, 특수문자 제외, 한글/영문/숫자만 허용됩니다.")
        # mypy 걸려서 추가
        instance = cast(User, self.instance)
        if User.objects.filter(nickname=value).exclude(id=instance.id).exists():
            raise DuplicateNicknameError()
        return value

    # 이름 정규식 검사(공백 허용)
    def validate_name(self, value: str) -> str:
        if not re.match(r"^[가-힣a-zA-Z\s]{1,30}$", value):
            raise serializers.ValidationError("이름은1~30자 이내, 특수문자 제외, 한글/영문만 허용됩니다.")
        return value

    # 생일 검사(미래날짜 불가능하게)
    def validate_birthday(self, value: date) -> date:
        if value > date.today():
            raise serializers.ValidationError("생일은 미래 날짜로 등록할 수 없습니다.")
        return value


class UserInfoUpdateResponseSerializer(serializers.ModelSerializer[User]):
    class Meta:
        model = User
        fields = ["id", "email", "nickname", "name", "birthday", "gender", "phone_number", "updated_at"]
        read_only_fields = fields
