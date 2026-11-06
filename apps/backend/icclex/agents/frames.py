"""Keyframes from a video, downscaled so a handful fit in one model request."""

import cv2

MAX_SIDE = 1024


def extract_keyframes(path, count: int) -> list[tuple[float, bytes]]:
    """Returns (timestamp_seconds, jpeg_bytes) for `count` evenly spaced frames."""
    cap = cv2.VideoCapture(str(path))
    try:
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 0.0
        if total <= 0 or fps <= 0:
            return []
        out = []
        for i in range(count):
            idx = int(total * (i + 0.5) / count)
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ok, frame = cap.read()
            if not ok:
                continue
            h, w = frame.shape[:2]
            scale = MAX_SIDE / max(h, w)
            if scale < 1:
                frame = cv2.resize(frame, (int(w * scale), int(h * scale)))
            ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            if ok:
                out.append((round(idx / fps, 2), buf.tobytes()))
        return out
    finally:
        cap.release()


def downscaled_jpeg(path) -> bytes:
    from io import BytesIO

    from PIL import Image, ImageOps

    with Image.open(path) as img:
        img = ImageOps.exif_transpose(img).convert("RGB")
        img.thumbnail((MAX_SIDE, MAX_SIDE))
        buf = BytesIO()
        img.save(buf, "JPEG", quality=85)
        return buf.getvalue()
