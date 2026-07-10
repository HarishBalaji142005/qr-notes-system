"""
utils.py — Helper functions for QR Notes Sharing System
"""

import os
import json
import socket
import qrcode
from PIL import Image
from datetime import datetime

# ─────────────────────────────────────────────
# FOLDER PATHS
# ─────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
QR_DIR      = os.path.join(BASE_DIR, "qr_codes")
ASSETS_DIR  = os.path.join(BASE_DIR, "assets")
DB_PATH     = os.path.join(BASE_DIR, "notes_db.json")

# Auto-create required folders
for folder in [UPLOADS_DIR, QR_DIR, ASSETS_DIR]:
    os.makedirs(folder, exist_ok=True)


# ─────────────────────────────────────────────
# FILE SAVING
# ─────────────────────────────────────────────
def save_uploaded_file(uploaded_file) -> tuple[str, str]:
    """
    Save an uploaded Streamlit file to the uploads/ directory.
    Returns (absolute_file_path, unique_filename).
    """
    # Add timestamp to avoid overwriting duplicate filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_name = uploaded_file.name
    name_without_ext, ext = os.path.splitext(original_name)
    unique_name = f"{name_without_ext}_{timestamp}{ext}"

    save_path = os.path.join(UPLOADS_DIR, unique_name)

    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return save_path, unique_name


# ─────────────────────────────────────────────
# QR CODE GENERATION
# ─────────────────────────────────────────────
def generate_qr_code(url: str, filename: str) -> str:
    """
    Generate a QR code image for the given URL.
    Saves the QR image to qr_codes/ and returns its path.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Create a styled QR image (blue fill on white)
    img = qr.make_image(fill_color="#2563EB", back_color="white")

    qr_filename = f"qr_{filename}.png"
    qr_path = os.path.join(QR_DIR, qr_filename)
    img.save(qr_path)

    return qr_path


# ─────────────────────────────────────────────
# NETWORK IP DETECTION
# ─────────────────────────────────────────────
def get_local_ip() -> str:
    """
    Detect the local network IP address of this machine.
    Falls back to '127.0.0.1' if detection fails.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


# ─────────────────────────────────────────────
# NOTES DATABASE (JSON-based)
# ─────────────────────────────────────────────
def load_notes_db() -> list:
    """Load notes metadata from the JSON database file."""
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_notes_db(notes: list) -> None:
    """Persist notes metadata list to the JSON database file."""
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(notes, f, indent=2, ensure_ascii=False)


def delete_note(note_id: str) -> None:
    """
    Remove a note entry from the database and delete its
    associated uploaded file and QR code image from disk.
    """
    db = load_notes_db()
    note = next((n for n in db if n["id"] == note_id), None)

    if note:
        # Delete uploaded file from disk
        if os.path.exists(note.get("file_path", "")):
            try:
                os.remove(note["file_path"])
            except OSError:
                pass

        # Delete QR code image from disk
        if os.path.exists(note.get("qr_path", "")):
            try:
                os.remove(note["qr_path"])
            except OSError:
                pass

        # Remove entry from DB and save
        db = [n for n in db if n["id"] != note_id]
        save_notes_db(db)


# ─────────────────────────────────────────────
# UI HELPERS
# ─────────────────────────────────────────────
def get_file_icon(filename: str) -> str:
    """Return an emoji icon based on the file extension."""
    ext = os.path.splitext(filename)[-1].lower()
    icons = {
        ".pdf":  "📄",
        ".ppt":  "📊",
        ".pptx": "📊",
        ".doc":  "📝",
        ".docx": "📝",
        ".txt":  "📃",
        ".png":  "🖼️",
        ".jpg":  "🖼️",
        ".jpeg": "🖼️",
    }
    return icons.get(ext, "📎")


def format_file_size(size_bytes: int) -> str:
    """Convert bytes to a human-readable size string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024 ** 2):.1f} MB"
    return f"{size_bytes / (1024 ** 3):.1f} GB"
