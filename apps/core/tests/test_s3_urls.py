from django.test import TestCase
from moto import mock_aws

from apps.core.utils.s3_urls import s3


class TestS3Urls(TestCase):
    def setUp(self) -> None:
        self.file = "test_file"
        self.suffix = ".jpg"
        self.file_name = "test_file.jpg"
        self.path = "test/"
        self.content_type = "image/jpeg"

    # 파일명이 빈 문자열일 경우 예외처리가 되는지
    def test_suffix_blank_file_name(self) -> None:
        file_name = ""
        with self.assertRaises(ValueError):
            s3._suffix(file_name)

    # 확장자가 없는 경우 예외처리가 되는지
    def test_suffix_blank_suffix(self) -> None:
        with self.assertRaises(ValueError):
            s3._suffix(self.file)

    # 화이트리스트에 없는 확장자가 들어온 경우 예외처리가 되는지
    def test_suffix_invalid_suffix(self) -> None:
        invalid_file_name = "test_file.test"
        with self.assertRaises(ValueError):
            s3._suffix(invalid_file_name)

    # 화이트리스트에 등록된 확장자가 들어온 경우 의도한 값을 반환을 하는지
    def test_suffix_valid_suffix(self) -> None:
        self.assertEqual(s3._suffix(self.file_name), (".jpg", "image/jpeg"))

    # path 마지막에 슬래시가 있어도 key가 의도한대로 생성되는지
    def test_key_path_with_slash(self) -> None:
        key = s3._key(self.path, self.suffix)
        self.assertNotIn("//", key)
        self.assertEqual(key[:5], "test/")
        self.assertEqual(key[-4:], ".jpg")

    # path 마지막에 슬래시가 없어도 key가 의도한대로 생성되는지
    def test_key_path_without_slash(self) -> None:
        path = "test"
        key = s3._key(path, self.suffix)
        self.assertNotIn("//", key)
        self.assertEqual(key[:5], "test/")
        self.assertEqual(key[-4:], ".jpg")

    # add_name을 넣었을 때 key가 의도한대로 생성되는지
    def test_key_add_name(self) -> None:
        key = s3._key(self.path, self.suffix, "cat")
        self.assertEqual(key[-8:], "_cat.jpg")

    # img_url이 잘 생성되는지
    def test_img_url(self) -> None:
        key = s3._key(self.path, self.suffix)
        img_url = s3._img_url(key)
        self.assertEqual(img_url, f"https://{s3.bucket}.s3.{s3.region}.amazonaws.com/{key}")

    # img_url이 255자 이내인지. 테스트의 img_url에선 99자
    def test_img_url_length(self) -> None:
        key = s3._key(self.path, self.suffix)
        img_url = s3._img_url(key)
        self.assertLessEqual(len(img_url), 255)

    # presigned_url이 잘 생성되는지
    @mock_aws
    def test_upload_presigned_url(self) -> None:
        key = s3._key(self.path, self.suffix)
        presigned_url = s3._upload_presigned_url(key, self.content_type)
        self.assertEqual(presigned_url.count("?"), 1)
        self.assertTrue(presigned_url.startswith("https://"))
        self.assertIn(key, presigned_url)
        self.assertIn("X-Amz-Signature", presigned_url)
        self.assertIn("X-Amz-Credential", presigned_url)
        self.assertIn("X-Amz-Algorithm", presigned_url)
        self.assertIn("X-Amz-Expires=600", presigned_url)

    # s3.create_upload_urls()가 잘 나오는지
    @mock_aws
    def test_create_upload_urls(self) -> None:
        presigned_url, img_url, key = s3.create_upload_urls(self.file_name, self.path)
        self.assertTrue(presigned_url.startswith("https://"))
        self.assertTrue(img_url.startswith("https://"))
        self.assertNotEqual(presigned_url, img_url)
