import os, uuid
from werkzeug.utils import secure_filename

ALLOWED = {
    "pdf": ("pdf", {"application/pdf"}), "doc": ("word", {"application/msword"}),
    "docx": ("word", {"application/vnd.openxmlformats-officedocument.wordprocessingml.document"}),
    "txt": ("text", {"text/plain"}), "xls": ("excel", {"application/vnd.ms-excel"}),
    "xlsx": ("excel", {"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}),
    "ppt": ("powerpoint", {"application/vnd.ms-powerpoint"}),
    "pptx": ("powerpoint", {"application/vnd.openxmlformats-officedocument.presentationml.presentation"}),
    "jpg": ("image", {"image/jpeg"}), "jpeg": ("image", {"image/jpeg"}),
    "png": ("image", {"image/png"}), "webp": ("image", {"image/webp"}),
}
GENERIC = {"application/octet-stream", ""}  # some browsers/phones omit exact type; magic bytes still checked
MAGIC = {"pdf": [b"%PDF"], "png": [b"\x89PNG"], "jpg": [b"\xff\xd8"], "jpeg": [b"\xff\xd8"], "webp": [b"RIFF"],
         "docx": [b"PK"], "xlsx": [b"PK"], "pptx": [b"PK"], "doc": [b"\xd0\xcf\x11\xe0"], "xls": [b"\xd0\xcf\x11\xe0"], "ppt": [b"\xd0\xcf\x11\xe0"]}
INLINE = {"pdf", "png", "jpg", "jpeg", "webp", "txt"}

def validate(file):
    """Return (ext, category, mime) or raise ValueError with a user-facing message."""
    name = secure_filename(file.filename or "")
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if ext not in ALLOWED: raise ValueError("File type not supported.")
    cat, mimes = ALLOWED[ext]
    mime = (file.mimetype or "").lower()
    if mime not in mimes and mime not in GENERIC: raise ValueError("File type not supported.")
    head = file.stream.read(8); file.stream.seek(0)
    if ext in MAGIC and not any(head.startswith(m) for m in MAGIC[ext]): raise ValueError("File content does not match its type.")
    if ext == "txt" and b"\x00" in file.stream.read(1024): raise ValueError("File content does not match its type.")
    file.stream.seek(0)
    return ext, cat, sorted(mimes)[0]

def save(file, folder, ext):
    stored = f"{uuid.uuid4().hex}.{ext}"
    path = os.path.join(folder, stored); file.save(path)
    return stored, os.path.getsize(path)
