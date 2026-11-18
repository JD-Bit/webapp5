"""The clock the running app should trust: real now, or an authorized preview."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from logic.unlock import Clock, resolve_clock


def query_value(params, name: str) -> str | None:
    """First query value, stripped. Missing, blank, or huge values are ignored."""
    try:
        if params is None or name not in params:
            return None
        value = params[name]
    except Exception:
        return None
    if isinstance(value, (list, tuple)):
        value = value[0] if value else None
    if value is None:
        return None
    text = str(value).strip()
    if not text or len(text) > 512:
        return None
    return text


def secrets_files_present() -> bool:
    candidates = (
        Path.cwd() / ".streamlit" / "secrets.toml",
        Path.home() / ".streamlit" / "secrets.toml",
    )
    return any(path.is_file() for path in candidates)


def key_from_mapping(mapping) -> str | None:
    if mapping is None:
        return None
    try:
        getter = getattr(mapping, "get", None)
        value = getter("preview_key") if callable(getter) else mapping["preview_key"]
    except Exception:
        return None
    if not isinstance(value, str) or value == "":
        return None
    return value


def load_preview_key() -> str | None:
    """Read preview_key. If no secrets file exists, don't touch st.secrets at all."""
    if not secrets_files_present():
        return None
    try:
        import streamlit as st

        return key_from_mapping(st.secrets)
    except Exception:
        return None


def current_clock() -> Clock:
    from data.letters_2027 import SETTINGS
    import streamlit as st

    tzname = str(SETTINGS["page_timezone"])
    zone = ZoneInfo(tzname)
    real_now = datetime.now(zone)
    return resolve_clock(
        real_now,
        query_value(st.query_params, "preview"),
        query_value(st.query_params, "key"),
        load_preview_key(),
        zone,
        tzname,
    )
