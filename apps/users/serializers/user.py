from rest_framework import serializers
from apps.users.models import User
from apps.users.services.user import create_user
import re

class SignupSerializer(serializers.ModelSerializer):
    email_token = serializers.CharField(write_only=True)
    sms_token = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'name',
            'nickname',
            'birthday',
            'gender',
            'email_token',
            'sms_token',
            'password',
            'password_confirm',
        ]

    def validate_nickname(self, value: str)-> str:
        if not re.match(r'^[가-힣a-zA-Z0-9]{2,10}$', value):
            raise serializers.ValidationError('닉네임은 2~10자 이내, 특수문자 제외, 한글/영문/숫자만 허용됩니다.')
        if User.objects.filter(nickname=value).exists():
            raise serializers.ValidationError('이미 사용 중인 닉네임입니다.')
        return value

    def validate_password(self, value: str)-> str:
        if not re.match(r'^\S{6,15}$', value):
            raise serializers.ValidationError('비밀번호는 6~15자여야 합니다.')
        if not re.search(r'[a-zA-Z]', value):
            raise serializers.ValidationError('비밀번호는 영문을 포함해야 합니다.')
        if not re.search(r'[0-9]', value):
            raise serializers.ValidationError('비밀번호는 숫자를 포함해야 합니다.')
        if not re.search(r'[!@#$%^&*]', value):
            raise serializers.ValidationError('비밀번호는 특수문자를 포함해야 합니다.')
        return value

    def validate(self, data: dict[str, str])-> dict[str, str]:
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password': '비밀번호가 일치하지 않습니다.'})
        # TODO : 토큰 구현 완료되면 email, phone_number 꺼내서 중복검사 추가해주세요
        # if User.objects.filter(email=email).exists():
        #     raise serializers.ValidationError('이미 가입된 이메일입니다.')
        # if User.objects.filter(phone_number=phone_number).exists():
        #     raise serializers.ValidationError('이미 가입에 사용된 휴대전화 번호입니다.')
        return data

    def create(self, validated_data: dict[str, str])-> User:
        validated_data.pop('password_confirm')
        return create_user(validated_data)