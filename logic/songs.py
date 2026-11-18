"""Turn a song field into a safe embed or a plain link. Empty stays empty."""

from __future__ import annotations

import re

_SPOTIFY_URL = re.compile(
    r"https?://open\.spotify\.com/(?:intl-[a-zA-Z-]+/)?"
    r"(track|album|playlist|episode)/([A-Za-z0-9]+)"
)
_SPOTIFY_URI = re.compile(r"spotify:(track|album|playlist|episode):([A-Za-z0-9]+)")
_YOUTUBE = re.compile(
    r"https?://(?:www\.|m\.)?(?:youtube\.com/(?:watch\?v=|embed/|shorts/)|"
    r"youtu\.be/|music\.youtube\.com/watch\?v=)([A-Za-z0-9_-]{6,})"
)
_HTTP = re.compile(r"https?://[^\s\"'<>]+")


def classify_song(url: str) -> tuple[str, str]:
    """Return (kind, value). kind is none, spotify, youtube, or link.

    Spotify and YouTube become embed URLs built only from the id. Anything
    else http(s) stays a link. javascript: and other schemes are dropped.
    """
    if not isinstance(url, str):
        return "none", ""
    text = url.strip()
    if not text or text.upper().startswith("PLACEHOLDER"):
        return "none", ""

    if text.startswith("http"):
        spot = _SPOTIFY_URL.search(text)
        if spot:
            kind, sid = spot.group(1), spot.group(2)
            return "spotify", f"https://open.spotify.com/embed/{kind}/{sid}"
        video = _YOUTUBE.search(text)
        if video:
            return "youtube", f"https://www.youtube-nocookie.com/embed/{video.group(1)}"
        if _HTTP.fullmatch(text):
            return "link", text
        return "none", ""

    if text.startswith("spotify:"):
        spot = _SPOTIFY_URI.fullmatch(text)
        if spot:
            kind, sid = spot.group(1), spot.group(2)
            return "spotify", f"https://open.spotify.com/embed/{kind}/{sid}"
    return "none", ""
