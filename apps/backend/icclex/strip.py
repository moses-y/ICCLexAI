"""Lossless metadata removal for export. Nothing is re-encoded: JPEG segments and PNG chunks that
carry metadata are dropped and the rest is copied byte for byte. The stored original is never touched;
the stripped file is a separate artefact and the manifest records that it was produced."""

import struct

# JPEG: APP1 (EXIF, XMP), APP2 (ICC is kept; FlashPix is not), APP13 (IPTC), COM (comments).
_JPEG_DROP = {0xE1, 0xED, 0xFE}
_PNG_DROP = {b"eXIf", b"tEXt", b"iTXt", b"zTXt", b"tIME"}


def strip_jpeg(data: bytes) -> bytes:
    if data[:2] != b"\xff\xd8":
        raise ValueError("not a JPEG")
    out, i = bytearray(data[:2]), 2
    while i < len(data):
        if data[i] != 0xFF:
            raise ValueError("corrupt JPEG segment")
        marker = data[i + 1]
        if marker == 0xDA:  # start of scan: the rest is entropy-coded image data
            out += data[i:]
            return bytes(out)
        if marker in (0xD8, 0x01) or 0xD0 <= marker <= 0xD7:
            out += data[i:i + 2]
            i += 2
            continue
        (length,) = struct.unpack(">H", data[i + 2:i + 4])
        if marker not in _JPEG_DROP:
            out += data[i:i + 2 + length]
        i += 2 + length
    return bytes(out)


def strip_png(data: bytes) -> bytes:
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG")
    out, i = bytearray(data[:8]), 8
    while i < len(data):
        (length,) = struct.unpack(">I", data[i:i + 4])
        ctype = data[i + 4:i + 8]
        end = i + 12 + length
        if ctype not in _PNG_DROP:
            out += data[i:end]
        i = end
    return bytes(out)


def strip_metadata(data: bytes, mime: str) -> bytes | None:
    """Returns stripped bytes, or None when this tool cannot strip the type losslessly."""
    if mime == "image/jpeg":
        return strip_jpeg(data)
    if mime == "image/png":
        return strip_png(data)
    return None
