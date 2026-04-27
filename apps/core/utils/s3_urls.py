"""
사용법:

from apps.core.utils.s3_urls import s3
위에서처럼 임포트해서 쓰세요
s3.create_upload_urls()을 사용해서 presigned_url과 img_url을 생성하세요
파라미터에 대한 설명은 create_upload_urls() 내부에 있습니다
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

    # presigned url과 img_url 2개를 반환하는 함수
    def create_upload_urls(
        self, file_name: str, path: str, expire: int = 600, *, add_name: str | None = None
    ) -> tuple[str, str]:
        """
        file_name: 확장자를 포함한 파일명을 그대로 넣어주세요
        path: 저장경로에서 파일명을 뺀 값. 저장경로가 uploads/images/questions/uuid.png라면
            uploads/images/questions/를 넣어주세요. 마지막 슬래시는 있어도 없어도 상관 없음
        expire: 넣거나 말거나
        add_name: 파일명을 uuid_cat.png처럼 만들고 싶다면, add_name에 cat을 넣어주면 됩니다
        """

        suffix, content_type = self._suffix(file_name)

        key = self._key(path, suffix, add_name)

        presigned_url = self._upload_presigned_url(key, content_type, expire)

        img_url = self._img_url(key)

        return presigned_url, img_url

    # 확장자 분리, 확장자 화이트 리스트
    @classmethod
    def _suffix(cls, file_name: str) -> tuple[str, str]:
        suffix = Path(file_name).suffix.lower()

        if suffix not in cls.ALLOWED_SUFFIX:
            raise ValueError("지원하지 않는 파일 형식입니다.")

        content_type = cls.ALLOWED_SUFFIX[suffix]

        return suffix, content_type

    # 키: 파일명을 포함한 저장경로. ex) uploads/images/questions/uuid.png
    def _key(self, path: str, suffix: str, add_name: str | None = None) -> str:
        key = path.rstrip("/") + "/" + self._image_uuid(add_name) + suffix

        return key

    # 파일명 생성 함수
    @staticmethod
    def _image_uuid(add_name: str | None) -> str:
        add = f"_{add_name}" if add_name else ""

        return str(uuid.uuid4()) + add

    # 업로드용 presigned url 생성 함수
    def _upload_presigned_url(self, key: str, content_type: str, expire: int = 600) -> str:
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
