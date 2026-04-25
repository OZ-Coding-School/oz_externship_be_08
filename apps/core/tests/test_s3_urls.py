from django.test import TestCase
from moto import mock_aws

from apps.core.utils.s3_urls import s3


class TestS3Handler(TestCase):
    def setUp(self) -> None:
        self.file_name = "test_file.jpg"
        self.path = "test/"

        self.key, self.content_type = s3._key_and_type(self.file_name, self.path)

    # 확장자가 없는 경우 예외처리가 되는지
    def test_suffix_blank_suffix(self) -> None:
        file_name = "test_file"
        with self.assertRaises(ValueError) as e:
            s3._suffix(file_name)
        self.assertEqual(str(e.exception), "지원하지 않는 파일 형식입니다.")

    # 화이트리스트에 없는 확장자가 들어온 경우 예외처리가 되는지
    def test_suffix_invalid_suffix(self) -> None:
        file_name = "test_file.test"
        with self.assertRaises(ValueError) as e:
            s3._suffix(file_name)
        self.assertEqual(str(e.exception), "지원하지 않는 파일 형식입니다.")

    # 대문자 확장자를 넣어도 소문자로 통일이 되는지
    def test_suffix_lowercase(self) -> None:
        file_name = "test_file.JPG"
        self.assertEqual(s3._suffix(file_name), ".jpg")

    # 화이트리스트에 등록된 확장자가 들어온 경우 의도한 값을 반환을 하는지
    def test_suffix_valid_suffix(self) -> None:
        self.assertEqual(s3._suffix(self.file_name), ".jpg")

    # add_name을 넣었을 때 uuid가 의도한대로 생성되는지
    def test_uuid_add_name(self) -> None:
        uuid = s3._image_uuid(add_name="cat")
        self.assertEqual(len(uuid), 40)
        self.assertTrue(uuid.endswith("_cat"))

    # path 마지막에 슬래시가 있어도 key가 의도한대로 생성되는지
    def test_key_path_with_slash(self) -> None:
        self.assertNotIn("//", self.key)
        self.assertTrue(self.key.startswith("test/"))
        self.assertTrue(self.key.endswith(".jpg"))

    # path 마지막에 슬래시가 없어도 key가 의도한대로 생성되는지
    def test_key_path_without_slash(self) -> None:
        path = "test"
        key, _ = s3._key_and_type(self.file_name, path)
        self.assertNotIn("//", key)
        self.assertTrue(key.startswith("test/"))
        self.assertTrue(key.endswith(".jpg"))

    # content_type이 의도한대로 생성되는지
    def test_content_type(self) -> None:
        self.assertEqual(self.content_type, "image/jpeg")

    # img_url이 잘 생성되는지
    def test_img_url(self) -> None:
        img_url = s3._img_url(self.key)
        self.assertEqual(img_url, f"https://{s3.bucket}.s3.{s3.region}.amazonaws.com/{self.key}")

    # img_url이 255자 이내인지. 테스트의 img_url에선 99자
    def test_img_url_length(self) -> None:
        img_url = s3._img_url(self.key)
        self.assertLessEqual(len(img_url), 255)

    # s3.create_img_url이 잘 작동하는지
    def test_create_img_url(self) -> None:
        img_url = s3.create_img_url(self.file_name, self.path)
        self.assertTrue(img_url.startswith("https://"))

    # presigned_url이 잘 생성되는지
    @mock_aws
    def test_presigned_url_for_upload(self) -> None:
        presigned_url = s3._presigned_url_for_upload(self.key, self.content_type)
        self.assertEqual(presigned_url.count("?"), 1)
        self.assertTrue(presigned_url.startswith("https://"))
        self.assertIn(self.key, presigned_url)
        self.assertIn("X-Amz-Signature", presigned_url)
        self.assertIn("X-Amz-Credential", presigned_url)
        self.assertIn("X-Amz-Algorithm", presigned_url)
        self.assertIn("X-Amz-Expires=600", presigned_url)

    # s3.create_upload_urls()가 잘 작동하는지
    @mock_aws
    def test_create_presigned_url(self) -> None:
        presigned_url = s3.create_presigned_url(self.file_name, self.path)
        self.assertTrue(presigned_url.startswith("https://"))
