from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from minio import Minio

from ..settings import settings

router = APIRouter()


def _get_minio_client() -> Minio:
    return Minio(
        settings.s3_endpoint.replace("http://", "").replace("https://", ""),
        access_key=settings.s3_access_key,
        secret_key=settings.s3_secret_key,
        secure=settings.s3_endpoint.startswith("https://"),
    )


@router.post("/upload")
async def upload_asset(file: UploadFile = File(...)) -> dict[str, str]:
    client = _get_minio_client()

    # ensure bucket exists
    if not client.bucket_exists(settings.s3_bucket):
        client.make_bucket(settings.s3_bucket)

    object_name = file.filename
    data = await file.read()

    try:
        client.put_object(
            settings.s3_bucket,
            object_name,
            data=bytes(data),
            length=len(data),
            content_type=file.content_type,
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc

    url = f"{settings.s3_endpoint}/{settings.s3_bucket}/{object_name}"
    return {"url": url}

