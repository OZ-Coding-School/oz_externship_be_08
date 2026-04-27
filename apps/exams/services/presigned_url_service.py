from apps.core.utils.s3_urls import s3

PATH = "uploads/exams/thumbnails"
FILE_NAME_MAX_LENGTH = 255


def presigned_url_generation(file_name: str) -> tuple[str, str, str]:
    if not file_name:
        raise ValueError("파일을 첨부해주세요.")
    if len(file_name) > FILE_NAME_MAX_LENGTH:
        raise ValueError("파일명은 최대 255자 이내여야 합니다.")
    presigned_url, img_url = s3.create_upload_urls(file_name, PATH)
    key = img_url.split(".com/")[-1]
    return presigned_url, img_url, key
