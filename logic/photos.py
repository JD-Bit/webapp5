"""Korea wall and safe letter-photo paths.

Pictures are discovered from a folder. Adding one is a file drop, not a code
change. Captions are optional and live beside the pictures.
"""

from __future__ import annotations

import base64
import hashlib
import html
import io
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
_CAPTION_ERROR = (
    "captions.toml couldn't be read, so the pictures are shown without captions."
)


@dataclass(frozen=True)
class Polaroid:
    name: str
    src: str
    caption: str
    tilt: float
    width: int
    height: int


def list_image_files(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    found = []
    for path in folder.iterdir():
        if not path.is_file() or path.name.startswith("."):
            continue
        if path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        found.append(path)
    found.sort(key=lambda item: item.name.lower())
    return found


def read_captions(path: Path) -> tuple[dict[str, str], str | None]:
    """Filename to caption. A missing file is fine. A broken file is reported."""
    if not path.is_file():
        return {}, None
    try:
        with path.open("rb") as handle:
            raw = tomllib.load(handle)
    except Exception:
        return {}, _CAPTION_ERROR
    if not isinstance(raw, dict):
        return {}, _CAPTION_ERROR
    captions: dict[str, str] = {}
    for key, value in raw.items():
        if isinstance(key, str) and isinstance(value, str) and value.strip():
            captions[key] = value.strip()
    return captions, None


def tilt_for(name: str) -> float:
    """Stable little rotation from the file name, about -3.5 to 3.5 degrees."""
    digest = hashlib.md5(name.encode("utf-8")).hexdigest()
    span = int(digest[:4], 16) % 701
    return (span - 350) / 100


def polaroid_from_path(path: Path, caption: str) -> Polaroid | None:
    """A display-sized data URI. Failures are skipped so one bad file isn't fatal."""
    tilt = tilt_for(path.name)
    try:
        if path.suffix.lower() == ".gif" and path.stat().st_size <= 6_000_000:
            raw = path.read_bytes()
            src = "data:image/gif;base64," + base64.b64encode(raw).decode("ascii")
            return Polaroid(path.name, src, caption, tilt, 0, 0)
        from PIL import Image

        with Image.open(path) as image:
            if image.mode in ("RGBA", "LA") or (
                image.mode == "P" and "transparency" in image.info
            ):
                rgba = image.convert("RGBA")
                frame = Image.new("RGB", rgba.size, (246, 240, 230))
                frame.paste(rgba, mask=rgba.split()[-1])
            else:
                frame = image.convert("RGB")
            frame.thumbnail((900, 900))
            buffer = io.BytesIO()
            frame.save(buffer, format="JPEG", quality=82, optimize=True)
            src = "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode(
                "ascii"
            )
            width, height = frame.size
            return Polaroid(path.name, src, caption, tilt, width, height)
    except Exception:
        return None


def safe_photo_path(root: Path, rel: str) -> Path | None:
    """A letter photo inside the project, or None. Absolute paths and links stay out."""
    if not isinstance(rel, str):
        return None
    text = rel.strip()
    if not text or text.startswith(("/", "\\")) or "://" in text:
        return None
    if Path(text).is_absolute():
        return None
    root_resolved = root.resolve()
    try:
        candidate = (root_resolved / text).resolve()
    except (OSError, ValueError):
        return None
    if candidate != root_resolved and root_resolved not in candidate.parents:
        return None
    if not candidate.is_file():
        return None
    if candidate.suffix.lower() not in IMAGE_EXTENSIONS:
        return None
    return candidate


def _esc(value: str) -> str:
    return html.escape(value, quote=True)


def wall_html(
    title: str,
    dates: str,
    note: str,
    polaroids: list[Polaroid],
    caption_error: str | None,
) -> str:
    parts = ['<section class="ny27-korea">']
    if title.strip():
        parts.append(
            f'<div class="ny27-korea-title" role="heading" aria-level="2">{_esc(title.strip())}</div>'
        )
    if dates.strip():
        parts.append(f'<p class="ny27-korea-dates">{_esc(dates.strip())}</p>')
    if note.strip():
        note_html = "<br>".join(_esc(line) for line in note.strip().splitlines())
        parts.append(f'<p class="ny27-korea-note">{note_html}</p>')
    if caption_error:
        parts.append(f'<p class="ny27-korea-warn">{_esc(caption_error)}</p>')

    usable = [
        shot
        for shot in polaroids
        if isinstance(shot.src, str) and shot.src.startswith("data:image/")
    ]
    if not usable:
        parts.append(
            '<div class="ny27-empty">'
            '<div class="ny27-empty-frame" aria-hidden="true"></div>'
            "<p>No pictures yet.</p>"
            "</div>"
        )
    else:
        cards = []
        for shot in usable:
            alt = shot.caption.strip() or "Photo from Korea"
            size = ""
            if shot.width > 0 and shot.height > 0:
                size = f' width="{shot.width}" height="{shot.height}"'
            caption_html = ""
            extra = " no-cap" if not shot.caption.strip() else ""
            if shot.caption.strip():
                caption_html = f"<figcaption>{_esc(shot.caption.strip())}</figcaption>"
            tilt = f"{shot.tilt:.2f}"
            if not re.fullmatch(r"-?\d+\.\d{2}", tilt):
                tilt = "0.00"
            cards.append(
                f'<figure class="ny27-polaroid{extra}" style="--tilt: {tilt}deg">'
                f'<img src="{shot.src}" alt="{_esc(alt)}"{size} loading="lazy">'
                f"{caption_html}</figure>"
            )
        parts.append(f'<div class="ny27-wall">{"".join(cards)}</div>')
    parts.append("</section>")
    return "".join(parts)
