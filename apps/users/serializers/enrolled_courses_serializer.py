from typing import Any

from rest_framework import serializers

from apps.courses.models.cohort import Cohort
from apps.courses.models.course import Course


# 안쪽 시리얼라이저
class MyCohortInfoSerializer(serializers.ModelSerializer[Cohort]):
    class Meta:
        model = Cohort
        fields = ["id", "number", "start_date", "end_date", "status"]
        read_only_fields = fields


class MyCourseInfoSerializer(serializers.ModelSerializer[Course]):
    class Meta:
        model = Course
        fields = ["id", "name", "tag", "thumbnail_img_url"]
        read_only_fields = fields


# 메인 시리얼라이저(위에 두개 묶어주기)
class MyCoursesSerializer(serializers.Serializer[Any]):
    cohort = MyCohortInfoSerializer(source="*", read_only=True)
    course = MyCourseInfoSerializer(read_only=True)
    # source='*'의 역할:
    # 1. 특정 필드가 아닌 '객체(instance) 전체'를 전달할때 사용
    # 2. cohort가 모델 필드명에 없어서 소스를 지정하는 용도
