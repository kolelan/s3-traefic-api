from fastapi import FastAPI, UploadFile, HTTPException
from minio import Minio
from minio.error import S3Error
import uuid

app = FastAPI()

# Подключение к MinIO
minio_client = Minio(
    "minio:9000",
    access_key="admin",
    secret_key="password123",
    secure=False
)

BUCKET = "files"


@app.on_event("startup")
async def startup():
    if not minio_client.bucket_exists(BUCKET):
        minio_client.make_bucket(BUCKET)


@app.post("/upload")
async def upload_file(file: UploadFile):
    file_id = str(uuid.uuid4())
    file_name = f"{file_id}_{file.filename}"

    # Загрузка в MinIO
    minio_client.put_object(
        BUCKET, file_name, file.file, file.size
    )

    return {
        "url": f"http://localhost/{BUCKET}/{file_name}",
        "file_id": file_id
    }


@app.get("/files")
async def list_files():
    files = []
    for obj in minio_client.list_objects(BUCKET):
        files.append({
            "name": obj.object_name,
            "url": f"http://localhost/{BUCKET}/{obj.object_name}"
        })
    return files