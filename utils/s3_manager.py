import os
import boto3
from pathlib import Path


class S3Manager:

    def __init__(self):

        self.bucket = os.getenv("S3_BUCKET_NAME")

        self.s3 = boto3.client(
            "s3",
            region_name=os.getenv("AWS_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

    ########################################################

    def upload_directory(
        self,
        local_dir: str,
        s3_prefix: str,
    ):

        local_dir = Path(local_dir)

        for file in local_dir.rglob("*"):

            if file.is_file():

                key = f"{s3_prefix}/{file.relative_to(local_dir)}"

                self.s3.upload_file(
                    str(file),
                    self.bucket,
                    key
                )

    ########################################################

    def download_directory(
        self,
        s3_prefix: str,
        local_dir: str,
    ):

        os.makedirs(local_dir, exist_ok=True)

        paginator = self.s3.get_paginator("list_objects_v2")

        pages = paginator.paginate(
            Bucket=self.bucket,
            Prefix=s3_prefix
        )

        for page in pages:

            if "Contents" not in page:
                continue

            for obj in page["Contents"]:

                key = obj["Key"]

                relative = os.path.relpath(
                    key,
                    s3_prefix
                )

                local_path = os.path.join(
                    local_dir,
                    relative
                )

                os.makedirs(
                    os.path.dirname(local_path),
                    exist_ok=True
                )

                self.s3.download_file(
                    self.bucket,
                    key,
                    local_path
                )

    ########################################################

    def delete_directory(
        self,
        s3_prefix: str,
    ):

        paginator = self.s3.get_paginator("list_objects_v2")

        pages = paginator.paginate(
            Bucket=self.bucket,
            Prefix=s3_prefix
        )

        objects = []

        for page in pages:

            if "Contents" not in page:
                continue

            for obj in page["Contents"]:

                objects.append(
                    {
                        "Key": obj["Key"]
                    }
                )

        if objects:

            self.s3.delete_objects(
                Bucket=self.bucket,
                Delete={
                    "Objects": objects
                }
            )

    ########################################################

    def exists(
        self,
        s3_prefix: str,
    ) -> bool:

        response = self.s3.list_objects_v2(
            Bucket=self.bucket,
            Prefix=s3_prefix,
            MaxKeys=1
        )

        return "Contents" in response