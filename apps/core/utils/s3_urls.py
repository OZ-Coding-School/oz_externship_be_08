"""
사용법:

from apps.core.utils.s3_urls import s3
위에서처럼 임포트해서 쓰세요

presigned_url 생성: s3.create_presigned_url()
img_url 생성: s3.create_img_url()

파라미터에 대한 설명은 create_presigned_url() 내부에 있습니다
"""

import uuid
from pathlib import Path

import boto3
from django.conf import settings


class S3Handler:
    ALLOWED_SUFFIX = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }

    def __init__(self) -> None:
        self.s3 = boto3.client(
            "s3",
            region_name=settings.AWS_S3_REGION,
            aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
        )
        self.bucket = settings.AWS_S3_BUCKET_NAME
        self.region = settings.AWS_S3_REGION

    # presigned url을 반환하는 함수
    def create_presigned_url(self, file_name: str, path: str, expire: int = 600, *, add_name: str | None = None) -> str:
        """
        file_name: 확장자를 포함한 파일명을 그대로 넣어주세요
        path: 저장경로에서 파일명을 뺀 값. 저장경로가 uploads/images/questions/uuid.png라면
            uploads/images/questions/를 넣어주세요. 마지막 슬래시는 있어도 없어도 상관 없음
        expire: 넣거나 말거나
        add_name: 파일명을 uuid_cat.png처럼 만들고 싶다면, add_name에 cat을 넣어주면 됩니다
        """

        key, content_type = self._key_and_type(path, file_name, add_name)
        presigned_url = self._presigned_url_for_upload(key, content_type, expire)

        return presigned_url

    # img_url을 반환하는 함수
    def create_img_url(self, file_name: str, path: str, *, add_name: str | None = None) -> str:
        """
        파라미터에 대한 설명은 create_presigned_url() 참고
        """

        key, _ = self._key_and_type(path, file_name, add_name)
        img_url = self._img_url(key)

        return img_url

    # key: 파일명을 포함한 저장경로. ex) uploads/images/questions/uuid.png
    def _key_and_type(self, path: str, file_name: str, add_name: str | None = None) -> tuple[str, str]:
        suffix = self._suffix(file_name)
        key = path.rstrip("/") + "/" + self._image_uuid(add_name) + suffix
        content_type = self.ALLOWED_SUFFIX[suffix]

        return key, content_type

    # 파일명에서 확장자 분리, 확장자 화이트 리스트
    @classmethod
    def _suffix(cls, file_name: str) -> str:
        suffix = Path(file_name).suffix.lower()

        if suffix not in cls.ALLOWED_SUFFIX:
            raise ValueError("지원하지 않는 파일 형식입니다.")

        return suffix

    # uuid 파일명 생성 함수
    @staticmethod
    def _image_uuid(add_name: str | None = None) -> str:
        add = f"_{add_name}" if add_name else ""

        return str(uuid.uuid4()) + add

    # 업로드용 presigned url 생성 함수
    def _presigned_url_for_upload(self, key: str, content_type: str, expire: int = 600) -> str:
        presigned_url = self.s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": self.bucket,
                "Key": key,
                "ContentType": content_type,
            },
            ExpiresIn=expire,
        )

        return presigned_url

    # DB의 img_url 생성 함수
    def _img_url(self, key: str) -> str:
        img_url = f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{key}"

        return img_url


s3 = S3Handler()
