import os
from werkzeug.utils import secure_filename

UPLOADS_DIR = "uploads"
os.makedirs(UPLOADS_DIR, exist_ok=True)

def save_original_file(file_storage, rid: str):
    filename = secure_filename(file_storage.filename)

    if "." not in filename:
        raise ValueError("Invalid filename")

    ext = filename.rsplit(".", 1)[1].lower()
    if ext not in ("csv", "json"):
        raise ValueError("Unsupported file type")

    path = os.path.join(UPLOADS_DIR, f"{rid}.{ext}")

    file_storage.stream.seek(0)
    file_storage.save(path)

    return path
