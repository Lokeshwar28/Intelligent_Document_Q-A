import uuid
from typing import BinaryIO
import boto3
from botocore.exceptions import ClientError
import structlog
from app.core.config import get_settings

log = structlog.get_logger()
settings = get_settings()


class S3Storage:
    """Thin wrapper around boto3 S3 client."""

    def __init__(self) -> None:
        kwargs: dict = {
        "region_name": settings.aws_region,
        "aws_access_key_id": settings.aws_access_key_id or None,
        "aws_secret_access_key": settings.aws_secret_access_key or None,
    }
        if settings.aws_endpoint_url:
            kwargs["endpoint_url"] = settings.aws_endpoint_url

        self._client = boto3.client("s3", **kwargs)
        self.bucket = settings.s3_bucket_name

    def upload_file(
        self,
        file_obj: BinaryIO,
        filename: str,
        content_type: str,
        user_id: str,
    ) -> str:
        """Upload file to S3 and return the S3 key."""
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
        key = f"documents/{user_id}/{uuid.uuid4()}.{ext}"
        try:
            self._client.upload_fileobj(
                file_obj,
                self.bucket,
                key,
                ExtraArgs={"ContentType": content_type},
            )
            log.info("s3_upload_success", key=key, bucket=self.bucket)
            return key
        except ClientError as e:
            log.error("s3_upload_failed", error=str(e), key=key)
            raise

    def get_presigned_url(self, key: str, expires_in: int = 3600) -> str:
        """Generate a presigned URL for temporary file access."""
        return self._client.generate_presigned_url(
            "get_object",
            Params={"Bucket": self.bucket, "Key": key},
            ExpiresIn=expires_in,
        )

    def download_file(self, key: str) -> bytes:
        """Download file contents from S3."""
        try:
            response = self._client.get_object(Bucket=self.bucket, Key=key)
            return response["Body"].read()
        except ClientError as e:
            log.error("s3_download_failed", error=str(e), key=key)
            raise


# Module-level singleton
_storage: S3Storage | None = None


def get_storage() -> S3Storage:
    global _storage
    if _storage is None:
        _storage = S3Storage()
    return _storage