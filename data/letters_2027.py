"""2027 letters. This is the only file you edit for words, songs, photos, and dates.

Each envelope stays sealed until its `unlock` time, in its own `timezone`.
The check runs on the server. `title`, `body`, `song`, and `photos` are not
sent to the browser before that moment, and not until the envelope is opened.

Times are local, 24-hour ISO. "2027-01-27T00:00:00" is the first moment of
that day. Leave `song` as "" and `photos` as [] to hide them.

    song: a Spotify or YouTube link, for example
        "https://open.spotify.com/track/..."
        "https://www.youtube.com/watch?v=..."
    photos: paths from the project folder, for example
        ["assets/letters/june.jpg"]

`timezone` is any IANA name. The default is Asia/Singapore.

The page itself stays hidden until `page_unlock` (1 Jan 2027, 00:00
Asia/Singapore). After that it becomes the default page. Older years stay
in the sidebar.

`heart` is the year mark (sidebar icon and the page). `accent` is the ivory
used on seals and rules. Placeholder heart: 🤍

Korea pictures are not listed here. Drop them in assets/korea/ and, if you
want captions, edit assets/korea/captions.toml.

Preview, only with the key in .streamlit/secrets.toml (see the example there):

    ?preview=2027-02-14&key=YOUR_KEY
    ?preview=2027-02-14T21:30&key=YOUR_KEY

A date alone means 00:00 that morning, Asia/Singapore. Without the matching
key, preview does nothing.

The dates below are checked by tests/test_letters_lock.py. If you move an
unlock, update that test too. The placeholder lines are meant to be replaced;
there is a test that still expects the word PLACEHOLDER until you remove it.
"""

from __future__ import annotations


def letter(
    *,
    id: str,
    month: str,
    label: str,
    unlock: str,
    title: str,
    body: str,
    timezone: str = "Asia/Singapore",
    song: str = "",
    photos: list | None = None,
) -> dict:
    """One envelope. Edit the arguments; you don't need to touch the page code."""
    return {
        "id": id,
        "month": month,
        "label": label,
        "unlock": unlock,
        "timezone": timezone,
        "title": title,
        "body": body,
        "song": song,
        "photos": [] if photos is None else list(photos),
    }


SETTINGS = {
    "heart": "🤍",
    "accent": "#f4efe6",
    # Sidebar icon and the mark under the headline. One place to change the year.
    "headline": "Letters for the year ahead",
    "intro": (
        "PLACEHOLDER — welcome line. Clear this if you want the envelopes "
        "to sit right under the title."
    ),
    "page_unlock": "2027-01-01T00:00:00",
    "page_timezone": "Asia/Singapore",
    "default_timezone": "Asia/Singapore",
    "reveal_prompt": "click only if you're daring enough to see whats on the other side",
    "korea_title": "Korea",
    "korea_dates": "Dec 2026 – Jan 2027",
    # Optional sentence under the Korea title. Leave "" to hide it.
    "korea_note": "",
}


LETTERS = [
    letter(
        id="2027-01",
        month="January",
        label="Birthday + final semester together",
        unlock="2027-01-27T00:00:00",
        timezone="Asia/Singapore",
        title="PLACEHOLDER — title for January",
        body="""PLACEHOLDER — body for January.

Replace this with the letter. A blank line starts a new paragraph.
""",
        song="",
        photos=[],
    ),
    letter(
        id="2027-02",
        month="February",
        label="Valentine's",
        unlock="2027-02-14T00:00:00",
        timezone="Asia/Singapore",
        title="PLACEHOLDER — title for February",
        body="""PLACEHOLDER — body for February.

Replace this with the letter. A blank line starts a new paragraph.
""",
        song="",
        photos=[],
    ),
    letter(
        id="2027-03",
        month="March",
        label="Anniversary",
        unlock="2027-03-05T00:00:00",
        timezone="Asia/Singapore",
        title="PLACEHOLDER — title for March",
        body="""PLACEHOLDER — body for March.

Replace this with the letter. A blank line starts a new paragraph.
""",
        song="",
        photos=[],
    ),
    letter(
        id="2027-04",
        month="April",
        label="Mugging together",
        unlock="2027-04-01T00:00:00",
        timezone="Asia/Singapore",
        title="PLACEHOLDER — title for April",
        body="""PLACEHOLDER — body for April.

Replace this with the letter. A blank line starts a new paragraph.
""",
        song="",
        photos=[],
    ),
    letter(
        id="2027-05",
        month="May",
        label="Your final finals",
        unlock="2027-05-01T00:00:00",
        timezone="Asia/Singapore",
        title="PLACEHOLDER — title for May",
        body="""PLACEHOLDER — body for May.

Replace this with the letter. A blank line starts a new paragraph.
""",
        song="",
        photos=[],
    ),
    letter(
        id="2027-06",
        month="June",
        label="Start of your career",
        unlock="2027-06-01T00:00:00",
        timezone="Asia/Singapore",
        title="PLACEHOLDER — title for June",
        body="""PLACEHOLDER — body for June.

Replace this with the letter. A blank line starts a new paragraph.
""",
        song="",
        photos=[],
    ),
    letter(
        id="2027-07",
        month="July",
        label="Open when",
        unlock="2027-07-01T00:00:00",
        timezone="Asia/Singapore",
        title="PLACEHOLDER — title for July",
        body="""PLACEHOLDER — body for July.

Replace this with the letter. A blank line starts a new paragraph.
""",
        song="",
        photos=[],
    ),
    letter(
        id="2027-08",
        month="August",
        label="Your convocation",
        unlock="2027-08-01T00:00:00",
        timezone="Asia/Singapore",
        title="PLACEHOLDER — title for August",
        body="""PLACEHOLDER — body for August.

Replace this with the letter. A blank line starts a new paragraph.
""",
        song="",
        photos=[],
    ),
    letter(
        id="2027-09",
        month="September",
        label="Open when",
        unlock="2027-09-01T00:00:00",
        timezone="Asia/Singapore",
        title="PLACEHOLDER — title for September",
        body="""PLACEHOLDER — body for September.

Replace this with the letter. A blank line starts a new paragraph.
""",
        song="",
        photos=[],
    ),
    letter(
        id="2027-10",
        month="October",
        label="Open when",
        unlock="2027-10-01T00:00:00",
        timezone="Asia/Singapore",
        title="PLACEHOLDER — title for October",
        body="""PLACEHOLDER — body for October.

Replace this with the letter. A blank line starts a new paragraph.
""",
        song="",
        photos=[],
    ),
    letter(
        id="2027-11",
        month="November",
        label="Your birthday",
        unlock="2027-11-08T00:00:00",
        timezone="Asia/Singapore",
        title="PLACEHOLDER — title for November",
        body="""PLACEHOLDER — body for November.

Replace this with the letter. A blank line starts a new paragraph.
""",
        song="",
        photos=[],
    ),
    letter(
        id="2027-12",
        month="December",
        label="Closing the year",
        unlock="2027-12-01T00:00:00",
        timezone="Asia/Singapore",
        title="PLACEHOLDER — title for December",
        body="""PLACEHOLDER — body for December.

Replace this with the letter. A blank line starts a new paragraph.
""",
        song="",
        photos=[],
    ),
]
