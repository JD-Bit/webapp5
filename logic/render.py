"""HTML for the 2027 page. Letter text is added only for an open, unlocked envelope."""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from datetime import datetime
from urllib.parse import quote, urlencode

from logic.unlock import Envelope, present_one

FALLBACK_ACCENT = "#f4efe6"
_ACCENT_RE = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
_PREVIEW_RE = re.compile(r"\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}(?::\d{2})?)?")



@dataclass(frozen=True)
class Card:
    id: str
    month: str
    label: str
    when_text: str
    when_iso: str
    state: str


@dataclass(frozen=True)
class PageBits:
    grid_html: str
    letter_html: str
    song: str
    photos: tuple[str, ...]
    opened_id: str | None


def safe_accent(value: str) -> str:
    if isinstance(value, str) and _ACCENT_RE.fullmatch(value.strip()):
        return value.strip()
    return FALLBACK_ACCENT


def _esc(value: str) -> str:
    return html.escape(value or "", quote=True)


def paragraphs(text: str) -> str:
    blocks = []
    for chunk in re.split(r"\n\s*\n", (text or "").strip()):
        lines = [_esc(line) for line in chunk.split("\n")]
        inner = "<br>".join(lines).strip()
        if inner:
            blocks.append(f"<p>{inner}</p>")
    return "".join(blocks)


def clean_keep(keep: dict | None) -> dict[str, str]:
    """Preview links keep the date and the key together, or they keep neither."""
    if not isinstance(keep, dict):
        return {}
    preview = keep.get("preview")
    key = keep.get("key")
    if not isinstance(preview, str) or not isinstance(key, str):
        return {}
    preview = preview.strip()
    if not _PREVIEW_RE.fullmatch(preview):
        return {}
    if not key or len(key) > 200 or any(ch in key for ch in "\r\n"):
        return {}
    return {"preview": preview, "key": key}


def href_for(open_id: str | None, keep: dict[str, str]) -> str:
    pairs: list[tuple[str, str]] = []
    if keep.get("preview"):
        pairs.append(("preview", keep["preview"]))
    if keep.get("key"):
        pairs.append(("key", keep["key"]))
    if open_id:
        pairs.append(("open", open_id))
    if not pairs:
        return "?"
    return "?" + urlencode(pairs, quote_via=quote)


def header_html(headline: str, heart: str, intro: str, banner: str | None) -> str:
    parts = ['<div class="ny27-top">']
    if banner:
        parts.append(f'<p class="ny27-banner">{_esc(banner)}</p>')
    parts.append(
        f'<div class="romantic-header" role="heading" aria-level="1">{_esc(headline)}</div>'
    )
    parts.append(f'<div class="ny27-heart" aria-hidden="true">{_esc(heart)}</div>')
    parts.append('<div class="ny27-rule"></div>')
    if intro and intro.strip():
        intro_html = "<br>".join(_esc(line) for line in intro.strip().splitlines())
        parts.append(f'<p class="ny27-intro">{intro_html}</p>')
    parts.append("</div>")
    return "".join(parts)


def dare_rule_html() -> str:
    return '<div class="ny27-dare"><div class="ny27-rule"></div></div>'


def _seal(state: str, heart: str) -> str:
    # An emoji, not an SVG: the page sanitizer drops inline SVG, which left
    # sealed envelopes looking unlocked.
    if state == "sealed":
        return "🔒"
    return _esc(heart or "🤍")


def _card_html(card: Card, heart: str, keep: dict[str, str]) -> str:
    if card.state == "sealed":
        aria = f"{card.month}, sealed. {card.when_text}. {card.label}"
        tag_open = (
            f'<div class="ny27-card is-sealed" role="group" aria-label="{_esc(aria)}">'
        )
        tag_close = "</div>"
        pill = ""
        status = "Sealed"
    else:
        aria = f"Open the {card.month} letter. {card.label}. {card.when_text}"
        current = ' aria-current="true"' if card.state == "open" else ""
        tag_open = (
            f'<a class="ny27-card is-{card.state}" href="{_esc(href_for(card.id, keep))}"'
            f' aria-label="{_esc(aria)}"{current}>'
        )
        tag_close = "</a>"
        pill_label = "Reading" if card.state == "open" else "Open"
        pill = f'<span class="ny27-open">{pill_label}</span>'
        status = "Reading" if card.state == "open" else "Ready"
    if card.when_iso:
        when = (
            f'<time class="ny27-when" datetime="{_esc(card.when_iso)}">{_esc(card.when_text)}</time>'
        )
    else:
        when = f'<span class="ny27-when">{_esc(card.when_text)}</span>'
    return (
        f"{tag_open}"
        f'<span class="ny27-mini" aria-hidden="true">'
        f'<span class="ny27-mini-flap"></span>'
        f'<span class="ny27-mini-seal">{_seal(card.state, heart)}</span>'
        f"</span>"
        f'<span class="ny27-card-text">'
        f'<span class="ny27-month">{_esc(card.month)}</span>'
        f'<span class="ny27-label">{_esc(card.label)}</span>'
        f'<span class="ny27-status">{status}</span>'
        f"{when}"
        f"{pill}"
        f"</span>"
        f"{tag_close}"
    )


def grid_html(cards: list[Card], heart: str, keep: dict[str, str]) -> str:
    items = "".join(_card_html(card, heart, keep) for card in cards)
    return f'<div class="ny27-wrap"><div class="ny27-grid">{items}</div></div>'


def letter_html(env: Envelope, heart: str, keep: dict[str, str], animate: bool) -> str:
    anim = " ny27-animate" if animate else ""
    close = _esc(href_for(None, keep))
    return (
        f'<div class="ny27-reveal{anim}" id="opened-letter">'
        f'<div class="ny27-stage" aria-hidden="true">'
        f'<div class="ny27-big">'
        f'<span class="ny27-big-flap"></span>'
        f'<span class="ny27-big-seal">{_esc(heart or "🤍")}</span>'
        f"</div>"
        f"</div>"
        f'<article class="ny27-paper">'
        f'<p class="ny27-kicker">{_esc(env.month)}</p>'
        f'<div class="ny27-title" role="heading" aria-level="2">{_esc(env.title or "")}</div>'
        f'<p class="ny27-paper-label">{_esc(env.label)}</p>'
        f'<div class="ny27-body">{paragraphs(env.body or "")}</div>'
        f"</article>"
        f'<a class="ny27-seal-again" href="{close}">Seal it again</a>'
        f"</div>"
    )


def compose_page(
    letters: list[dict],
    now: datetime,
    default_tz: str,
    opened_id: str | None,
    keep: dict | None,
    heart: str,
    animate: bool,
) -> PageBits:
    """Build the fragments the browser is allowed to see for this instant."""
    try:
        return _compose_page(letters, now, default_tz, opened_id, keep, heart, animate)
    except Exception:
        return PageBits("", "", "", (), None)


def _compose_page(
    letters: list[dict],
    now: datetime,
    default_tz: str,
    opened_id: str | None,
    keep: dict | None,
    heart: str,
    animate: bool,
) -> PageBits:
    envelopes = [present_one(letter, now, default_tz) for letter in letters]
    opened = None
    if opened_id:
        for env in envelopes:
            if env.id == opened_id and env.unlocked and env.body is not None:
                opened = env
                break
    safe_keep = clean_keep(keep)
    cards = []
    for env in envelopes:
        if not env.unlocked:
            state = "sealed"
        elif opened is not None and env.id == opened.id:
            state = "open"
        else:
            state = "ready"
        cards.append(Card(env.id, env.month, env.label, env.when_text, env.when_iso, state))
    grid = grid_html(cards, heart, safe_keep)
    if opened is None:
        return PageBits(grid, "", "", (), None)
    return PageBits(
        grid,
        letter_html(opened, heart, safe_keep, animate),
        opened.song,
        opened.photos,
        opened.id,
    )
