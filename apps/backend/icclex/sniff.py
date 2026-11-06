"""File type from the bytes, not the extension or the browser's Content-Type. Both are supplied by
the sender; an extension/content mismatch is reported by the integrity agent."""

KIND_BY_MIME = {
    "image/jpeg": "image", "image/png": "image", "image/gif": "image", "image/webp": "image",
    "image/heic": "image", "image/tiff": "image",
    "video/mp4": "video", "video/quicktime": "video", "video/webm": "video", "video/x-matroska": "video",
    "audio/mpeg": "audio", "audio/wav": "audio", "audio/ogg": "audio", "audio/mp4": "audio",
    "audio/flac": "audio", "audio/webm": "audio",
    "application/pdf": "document",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "document",
    "text/plain": "document",
}
EXTENSIONS_BY_MIME = {
    "image/jpeg": {".jpg", ".jpeg"}, "image/png": {".png"}, "image/gif": {".gif"}, "image/webp": {".webp"},
    "image/heic": {".heic", ".heif"}, "image/tiff": {".tif", ".tiff"},
    "video/mp4": {".mp4", ".m4v"}, "video/quicktime": {".mov"}, "video/webm": {".webm"},
    "video/x-matroska": {".mkv"},
    "audio/mpeg": {".mp3"}, "audio/wav": {".wav"}, "audio/ogg": {".ogg", ".oga", ".opus"},
    "audio/mp4": {".m4a"}, "audio/flac": {".flac"}, "audio/webm": {".weba", ".webm"},
    "application/pdf": {".pdf"},
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": {".docx"},
    "text/plain": {".txt", ".text", ".md", ".csv"},
}
UNKNOWN = "application/octet-stream"


def sniff_mime(head: bytes) -> str:
    """`head` is the first few KB of the file."""
    if head.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if head.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if head[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "image/webp"
    if head[:4] == b"RIFF" and head[8:12] == b"WAVE":
        return "audio/wav"
    if head[:4] in (b"II*\x00", b"MM\x00*"):
        return "image/tiff"
    if head[4:8] == b"ftyp":
        brand = head[8:12]
        if brand in (b"heic", b"heix", b"mif1", b"heif"):
            return "image/heic"
        if brand == b"qt  ":
            return "video/quicktime"
        if brand in (b"M4A ", b"M4B "):
            return "audio/mp4"
        return "video/mp4"
    if head[:4] == b"\x1a\x45\xdf\xa3":
        return "video/webm" if b"webm" in head[:64] else "video/x-matroska"
    if head[:3] == b"ID3" or head[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2"):
        return "audio/mpeg"
    if head[:4] == b"OggS":
        return "audio/ogg"
    if head[:4] == b"fLaC":
        return "audio/flac"
    if head[:5] == b"%PDF-":
        return "application/pdf"
    if head[:4] == b"PK\x03\x04" and b"word/" in head:
        return "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    try:
        head.decode("utf-8")
        if head and b"\x00" not in head:
            return "text/plain"
    except UnicodeDecodeError:
        pass
    return UNKNOWN


def kind_of(mime: str) -> str:
    return KIND_BY_MIME.get(mime, "other")
