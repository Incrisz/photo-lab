import json
import os
from io import BytesIO
from urllib.parse import unquote_plus

import boto3
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

bucket = os.environ["S3_BUCKET_NAME"]
queue_url = os.environ["SQS_QUEUE_URL"]

s3 = boto3.client("s3")
sqs = boto3.client("sqs")


def make_thumbnail(key):
    body = s3.get_object(Bucket=bucket, Key=key)["Body"]
    with body:
        original = BytesIO(body.read())

    output = BytesIO()
    with Image.open(original, formats=["JPEG", "PNG"]) as image:
        image.thumbnail((200, 200))
        image.convert("RGB").save(output, format="JPEG")

    thumbnail_key = "thumbnails/" + key.removeprefix("uploads/") + ".jpg"
    s3.put_object(
        Bucket=bucket,
        Key=thumbnail_key,
        Body=output.getvalue(),
        ContentType="image/jpeg",
    )
    print(f"Saved {thumbnail_key}", flush=True)


print("Waiting for photo uploads...", flush=True)

while True:
    response = sqs.receive_message(QueueUrl=queue_url, WaitTimeSeconds=20)

    for message in response.get("Messages", []):
        event = json.loads(message["Body"])

        # S3's setup test message has no Records.
        for record in event.get("Records", []):
            key = unquote_plus(record["s3"]["object"]["key"])
            if record["s3"]["bucket"]["name"] == bucket and key.startswith("uploads/"):
                make_thumbnail(key)

        sqs.delete_message(
            QueueUrl=queue_url,
            ReceiptHandle=message["ReceiptHandle"],
        )