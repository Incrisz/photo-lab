import os
from io import BytesIO
from uuid import uuid4

import boto3
from botocore.exceptions import ClientError
from flask import Flask, redirect, request, send_file, url_for
from PIL import Image, UnidentifiedImageError

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


@app.get("/")
def home():
    return """
    <h1>Photo Thumbnail Lab</h1>
    <form action="/thumbnail" method="post" enctype="multipart/form-data">
        <input type="file" name="photo" accept="image/jpeg,image/png" required>
        <button type="submit">Make thumbnail</button>
    </form>
    """


@app.post("/thumbnail")
def thumbnail():
    photo = request.files.get("photo")
    if not photo:
        return "Choose a photo first.", 400

    try:
        with Image.open(photo.stream, formats=["JPEG", "PNG"]) as image:
            image.load()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError):
        return "Choose a valid JPG or PNG photo.", 400

    photo.stream.seek(0)
    job_id = uuid4()
    s3 = boto3.client("s3")
    s3.put_object(
        Bucket=os.environ["S3_BUCKET_NAME"],
        Key=f"uploads/{job_id.hex}",
        Body=photo.stream.read(),
    )

    return redirect(url_for("show_thumbnail", job_id=job_id), code=303)


@app.get("/result/<uuid:job_id>")
def show_thumbnail(job_id):
    s3 = boto3.client("s3")

    try:
        result = s3.get_object(
            Bucket=os.environ["S3_BUCKET_NAME"],
            Key=f"thumbnails/{job_id.hex}.jpg",
        )
    except ClientError as error:
        if error.response["Error"]["Code"] == "NoSuchKey":
            return (
                '<meta http-equiv="refresh" content="2">'
                "<h1>Processing…</h1>"
                "<p>Your thumbnail will appear here when it is ready.</p>"
            )
        raise

    with result["Body"] as body:
        thumbnail_data = BytesIO(body.read())

    return send_file(thumbnail_data, mimetype="image/jpeg")