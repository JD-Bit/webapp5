"""When a 2027 envelope opens, and when the year itself appears.

All datetimes that cross a boundary are timezone-aware. A letter unlocks at
its own local `unlock` instant (inclusive). The page unlock is separate and
uses the year timezone, Asia/Singapore unless the settings say otherwise.
"""

from __future__ import annotations

import hmac
import re
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

MONTHS = (
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
)

_PREVIEW_RE = re.compile(r"\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}(?::\d{2})?)?")
_MAX_KEY = 200


@dataclass(frozen=True)
class Clock:
    instant: datetime
    previewing: bool
    banner: str | None
    preview_value: str | None
    key_value: str | None


@dataclass(frozen=True)
class Envelope:
    id: str
    month: str
    label: str
    when_text: str
    when_iso: str
    unlocked: bool
    title: str | None
    body: str | None
    song: str
    photos: tuple[str, ...]


def parse_local(value: str, tzname: str) -> datetime:
    """Read an ISO date or datetime in `tzname`. Aware inputs keep their instant."""
    if not isinstance(value, str) or not isinstance(tzname, str):
        raise ValueError("unlock must be text")
    text = value.strip()
    zone = ZoneInfo(tzname.strip())
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
        text += "T00:00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=zone)
    return parsed.astimezone(zone)


def format_when(moment: datetime) -> str:
    """English date, with a time only when it isn't midnight. Locale-independent."""
    base = f"{moment.day} {MONTHS[moment.month - 1]} {moment.year}"
    if moment.hour == moment.minute == moment.second == 0:
        return base
    hour = moment.hour % 12 or 12
    ampm = "AM" if moment.hour < 12 else "PM"
    return f"{base}, {hour}:{moment.minute:02d} {ampm}"


def format_clock(moment: datetime, tzname: str) -> str:
    hour = moment.hour % 12 or 12
    ampm = "AM" if moment.hour < 12 else "PM"
    return (
        f"{moment.day} {MONTHS[moment.month - 1]} {moment.year}, "
        f"{hour}:{moment.minute:02d} {ampm} ({tzname})"
    )


def when_label(deadline: datetime, tzname: str, default_tz: str, unlocked: bool) -> str:
    text = format_when(deadline)
    if tzname != default_tz:
        text = f"{text} · {tzname}"
    prefix = "Since" if unlocked else "Opens"
    return f"{prefix} {text}"


def year_is_open(instant: datetime, unlock: str, timezone: str) -> bool:
    """True from the page unlock instant onward. Bad config stays closed."""
    try:
        if instant.tzinfo is None:
            return False
        deadline = parse_local(unlock, timezone)
    except Exception:
        return False
    return instant >= deadline


def parse_preview(value: str | None, tz: ZoneInfo) -> datetime | None:
    """`YYYY-MM-DD` is midnight. `YYYY-MM-DDTHH:MM` (optional seconds) is exact.

    The text is always read in `tz`. Offsets in the string are rejected so
    the preview clock can't be slipped into another zone by the query.
    """
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not _PREVIEW_RE.fullmatch(text):
        return None
    if len(text) == 10:
        text += "T00:00:00"
    elif len(text) == 16:
        text += ":00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is not None:
        return None
    return parsed.replace(tzinfo=tz)


def keys_match(provided: str | None, expected: str | None) -> bool:
    if not isinstance(provided, str) or not isinstance(expected, str):
        return False
    if not provided or not expected:
        return False
    if len(provided) > _MAX_KEY or len(expected) > _MAX_KEY:
        return False
    if any(ch in provided or ch in expected for ch in "\r\n"):
        return False
    given = provided.encode("utf-8")
    wanted = expected.encode("utf-8")
    if len(given) != len(wanted):
        return False
    return hmac.compare_digest(given, wanted)


def resolve_clock(
    real_now: datetime,
    preview_raw: str | None,
    provided_key: str | None,
    expected_key: str | None,
    tz: ZoneInfo,
    tzname: str,
) -> Clock:
    """Use the preview instant only when the secret matches. Otherwise `real_now`."""
    if real_now.tzinfo is None:
        real_now = real_now.replace(tzinfo=tz)
    if not keys_match(provided_key, expected_key):
        return Clock(real_now, False, None, None, None)
    if not isinstance(preview_raw, str) or not isinstance(provided_key, str):
        return Clock(real_now, False, None, None, None)
    preview_text = preview_raw.strip()
    if len(preview_text) > 40:
        return Clock(real_now, False, None, None, None)
    parsed = parse_preview(preview_text, tz)
    if parsed is None:
        return Clock(real_now, False, None, None, None)
    banner = f"Previewing {format_clock(parsed, tzname)}"
    return Clock(parsed, True, banner, preview_text, provided_key)


def _text(value: object) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()


def _sealed(id_: str, month: str, label: str, when: str = "Sealed", iso: str = "") -> Envelope:
    return Envelope(id_ or "letter", month, label, when, iso, False, None, None, "", ())


def clean_song(value: str) -> str:
    if not value or value.upper().startswith("PLACEHOLDER"):
        return ""
    return value


def present_one(letter: dict, now: datetime, default_tz: str) -> Envelope:
    """Public card, plus the letter itself only after the unlock instant.

    On any bad date, timezone, or shape, the envelope stays sealed and the
    body is not copied onto the result.
    """
    try:
        if not isinstance(letter, dict):
            return _sealed("letter", "", "")
        month = _text(letter.get("month"))
        label = _text(letter.get("label"))
        id_ = _text(letter.get("id")) or month or "letter"
        unlock_raw = letter.get("unlock")
        tzname = _text(letter.get("timezone")) or default_tz
        if not isinstance(unlock_raw, str) or now.tzinfo is None:
            return _sealed(id_, month, label)
        deadline = parse_local(unlock_raw, tzname)
        unlocked = now >= deadline
        when = when_label(deadline, tzname, default_tz, unlocked)
        iso = deadline.isoformat()
        if not unlocked:
            return Envelope(id_, month, label, when, iso, False, None, None, "", ())
        photos_raw = letter.get("photos") or []
        if isinstance(photos_raw, str):
            photos_raw = [photos_raw]
        photos = tuple(
            item.strip()
            for item in photos_raw
            if isinstance(item, str) and item.strip()
        )
        return Envelope(
            id_,
            month,
            label,
            when,
            iso,
            True,
            _text(letter.get("title")),
            _text(letter.get("body")),
            clean_song(_text(letter.get("song"))),
            photos,
        )
    except Exception:
        if isinstance(letter, dict):
            return _sealed(
                _text(letter.get("id")) or _text(letter.get("month")) or "letter",
                _text(letter.get("month")),
                _text(letter.get("label")),
            )
        return _sealed("letter", "", "")


def sidebar_plan(show_2027: bool, heart: str) -> list[dict]:
    """Sidebar order. Before 2027 this is the current site: 2026, 2025, 2024."""
    older = [
        {"title": "2026", "icon": "💜", "default": not show_2027},
        {"title": "2025", "icon": "🩷", "default": False},
        {"title": "2024", "icon": "💙", "default": False},
    ]
    if not show_2027:
        return older
    return [{"title": "2027", "icon": heart, "default": True}, *older]
