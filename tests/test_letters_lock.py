"""Lock checks for the 2027 letters.

Run from the project folder:

    python tests/test_letters_lock.py

The calendar cases are the dates on the envelopes. If you move an unlock in
data/letters_2027.py, update EXPECTED here too. The PLACEHOLDER test is only
there until the real letters replace that word — delete it when you do.
"""

from __future__ import annotations

import base64
import sys
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from tempfile import TemporaryDirectory
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.letters_2027 import LETTERS, SETTINGS
from logic.clock import key_from_mapping, query_value
from logic.photos import (
    Polaroid,
    list_image_files,
    polaroid_from_path,
    read_captions,
    safe_photo_path,
    wall_html,
)
from logic.render import compose_page, header_html, safe_accent
from logic.songs import classify_song
from logic.unlock import (
    format_clock,
    format_when,
    parse_local,
    parse_preview,
    present_one,
    resolve_clock,
    sidebar_plan,
    year_is_open,
)

SG = ZoneInfo("Asia/Singapore")
UTC = ZoneInfo("UTC")

TINY_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)

# id, month, label, unlock. Timezone for every shipped letter is Asia/Singapore.
EXPECTED = [
    ("2027-01", "January", "Birthday + final semester together", "2027-01-27T00:00:00"),
    ("2027-02", "February", "Valentine's", "2027-02-14T00:00:00"),
    ("2027-03", "March", "Anniversary", "2027-03-05T00:00:00"),
    ("2027-04", "April", "Mugging together", "2027-04-01T00:00:00"),
    ("2027-05", "May", "Your final finals", "2027-05-01T00:00:00"),
    ("2027-06", "June", "Start of your career", "2027-06-01T00:00:00"),
    ("2027-07", "July", "Open when", "2027-07-01T00:00:00"),
    ("2027-08", "August", "Your convocation", "2027-08-01T00:00:00"),
    ("2027-09", "September", "Open when", "2027-09-01T00:00:00"),
    ("2027-10", "October", "Open when", "2027-10-01T00:00:00"),
    ("2027-11", "November", "Your birthday", "2027-11-08T00:00:00"),
    ("2027-12", "December", "Closing the year", "2027-12-01T00:00:00"),
]


def _ids(n: int) -> list[str]:
    return [row[0] for row in EXPECTED[:n]]


def _at(stamp: str, zone: ZoneInfo = SG) -> datetime:
    return datetime.fromisoformat(stamp).replace(tzinfo=zone)


def _unlocked(moment: datetime) -> list[str]:
    return [
        env.id
        for env in (present_one(letter, moment, "Asia/Singapore") for letter in LETTERS)
        if env.unlocked
    ]


class CalendarTests(unittest.TestCase):
    def test_shipped_letters_match_the_year(self):
        self.assertEqual(len(LETTERS), 12)
        self.assertEqual(SETTINGS["heart"], "🤍")
        self.assertEqual(SETTINGS["page_unlock"], "2027-01-01T00:00:00")
        self.assertEqual(SETTINGS["page_timezone"], "Asia/Singapore")
        self.assertEqual(SETTINGS["default_timezone"], "Asia/Singapore")
        self.assertEqual(safe_accent(SETTINGS["accent"]), SETTINGS["accent"])
        for letter, expected in zip(LETTERS, EXPECTED):
            id_, month, label, unlock = expected
            self.assertEqual(letter["id"], id_)
            self.assertEqual(letter["month"], month)
            self.assertEqual(letter["label"], label)
            self.assertEqual(letter["unlock"], unlock)
            self.assertEqual(letter["timezone"], "Asia/Singapore")
            self.assertIsInstance(letter["song"], str)
            self.assertIsInstance(letter["photos"], list)
            self.assertTrue(letter["title"].strip())
            self.assertTrue(letter["body"].strip())

    def test_placeholders_until_the_letters_are_written(self):
        # Delete this test once a real letter replaces the word PLACEHOLDER.
        for letter in LETTERS:
            self.assertIn("PLACEHOLDER", letter["title"])
            self.assertIn("PLACEHOLDER", letter["body"])

    def test_unlock_instants(self):
        cases = [
            ("2026-12-31T23:59:59", []),
            ("2027-01-01T00:00:00", []),
            ("2027-01-26T23:59:59", []),
            ("2027-01-27T00:00:00", _ids(1)),
            ("2027-02-13T23:59:59", _ids(1)),
            ("2027-02-14T00:00:00", _ids(2)),
            ("2027-03-04T23:59:59", _ids(2)),
            ("2027-03-05T00:00:00", _ids(3)),
            ("2027-03-31T23:59:59", _ids(3)),
            ("2027-04-01T00:00:00", _ids(4)),
            ("2027-05-01T00:00:00", _ids(5)),
            ("2027-06-01T00:00:00", _ids(6)),
            ("2027-07-01T00:00:00", _ids(7)),
            ("2027-08-01T00:00:00", _ids(8)),
            ("2027-09-01T00:00:00", _ids(9)),
            ("2027-10-01T00:00:00", _ids(10)),
            ("2027-11-07T23:59:59", _ids(10)),
            ("2027-11-08T00:00:00", _ids(11)),
            ("2027-11-30T23:59:59", _ids(11)),
            ("2027-12-01T00:00:00", _ids(12)),
            ("2027-12-31T23:00:00", _ids(12)),
        ]
        for stamp, expected in cases:
            with self.subTest(stamp=stamp):
                self.assertEqual(_unlocked(_at(stamp)), expected)

    def test_singapore_midnight_is_not_utc_midnight(self):
        # 27 Jan 2027 00:00 in Singapore is 26 Jan 16:00 UTC.
        self.assertEqual(_unlocked(datetime(2027, 1, 26, 16, 0, tzinfo=UTC)), ["2027-01"])
        self.assertEqual(_unlocked(datetime(2027, 1, 26, 15, 59, 59, tzinfo=UTC)), [])

    def test_page_stays_hidden_until_singapore_new_year(self):
        unlock = SETTINGS["page_unlock"]
        zone = SETTINGS["page_timezone"]
        self.assertFalse(year_is_open(_at("2026-12-31T23:59:59"), unlock, zone))
        self.assertTrue(year_is_open(_at("2027-01-01T00:00:00"), unlock, zone))
        self.assertFalse(
            year_is_open(datetime(2026, 12, 31, 15, 59, 59, tzinfo=UTC), unlock, zone)
        )
        self.assertTrue(
            year_is_open(datetime(2026, 12, 31, 16, 0, 0, tzinfo=UTC), unlock, zone)
        )
        self.assertFalse(year_is_open(datetime(2027, 1, 1, 0, 0), unlock, zone))
        self.assertFalse(year_is_open(_at("2027-06-01T00:00:00"), "not-a-date", zone))
        self.assertFalse(year_is_open(_at("2027-06-01T00:00:00"), unlock, "Not/AZone"))

    def test_sidebar_is_unchanged_before_the_year_opens(self):
        closed = sidebar_plan(False, "🤍")
        self.assertEqual([item["title"] for item in closed], ["2026", "2025", "2024"])
        self.assertEqual([item["icon"] for item in closed], ["💜", "🩷", "💙"])
        self.assertEqual([item["default"] for item in closed], [True, False, False])
        opened = sidebar_plan(True, "🤍")
        self.assertEqual(
            [item["title"] for item in opened], ["2027", "2026", "2025", "2024"]
        )
        self.assertEqual(opened[0]["icon"], "🤍")
        self.assertEqual([item["default"] for item in opened], [True, False, False, False])

    def test_app_keeps_the_sidebar_copy(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn('st.sidebar.text("HI THERE HOTTIE😍😍")', source)
        self.assertIn("st.sidebar.image(logo_path, width=200)", source)
        self.assertIn("st.logo(logo_path)", source)
        self.assertIn("sidebar_plan", source)
        view = (ROOT / "views" / "y2027.py").read_text(encoding="utf-8")
        self.assertIn("compose_page", view)
        self.assertIn("st.stop()", view)
        self.assertNotIn("st.write(LETTERS", view)


class TimezoneTests(unittest.TestCase):
    def test_format_is_english_regardless_of_locale(self):
        self.assertEqual(format_when(datetime(2027, 1, 27, 0, 0, 0)), "27 Jan 2027")
        self.assertEqual(format_when(datetime(2027, 1, 27, 18, 30)), "27 Jan 2027, 6:30 PM")
        self.assertEqual(format_when(datetime(2027, 1, 27, 0, 5)), "27 Jan 2027, 12:05 AM")
        self.assertEqual(format_when(datetime(2027, 1, 27, 12, 0)), "27 Jan 2027, 12:00 PM")

    def test_parse_local_uses_the_envelope_zone(self):
        parsed = parse_local("2027-01-27T00:00:00", "Asia/Singapore")
        self.assertEqual(parsed, datetime(2027, 1, 27, 0, 0, tzinfo=SG))
        self.assertEqual(parse_local("2027-01-27", "Asia/Singapore"), parsed)
        aware = parse_local("2027-01-26T16:00:00+00:00", "Asia/Singapore")
        self.assertEqual(aware, parsed)

    def test_new_york_letter_is_still_shut_at_singapore_midnight(self):
        letter = self._letter("America/New_York", "2027-01-27T00:00:00", "NY_SECRET")
        singapore_midnight = datetime(2027, 1, 27, 0, 0, tzinfo=SG)
        new_york = ZoneInfo("America/New_York")
        self.assertEqual(singapore_midnight.astimezone(new_york).day, 26)
        sealed = present_one(letter, singapore_midnight, "Asia/Singapore")
        self.assertFalse(sealed.unlocked)
        self.assertIsNone(sealed.body)
        opened = present_one(letter, datetime(2027, 1, 27, 0, 0, tzinfo=new_york), "Asia/Singapore")
        self.assertTrue(opened.unlocked)
        self.assertEqual(opened.body, "NY_SECRET")
        self.assertIn("America/New_York", opened.when_text)

    def test_los_angeles_midnight_is_afternoon_in_singapore(self):
        letter = self._letter("America/Los_Angeles", "2027-05-01T00:00:00", "LA_SECRET")
        la = ZoneInfo("America/Los_Angeles")
        la_midnight = datetime(2027, 5, 1, 0, 0, tzinfo=la)
        just_before = la_midnight - timedelta(seconds=1)
        self.assertFalse(present_one(letter, just_before, "Asia/Singapore").unlocked)
        self.assertTrue(present_one(letter, la_midnight, "Asia/Singapore").unlocked)
        self.assertTrue(
            present_one(letter, la_midnight.astimezone(SG), "Asia/Singapore").unlocked
        )
        # 1 May 00:00 in Singapore is still 30 April in Los Angeles.
        self.assertFalse(
            present_one(
                letter, datetime(2027, 5, 1, 0, 0, tzinfo=SG), "Asia/Singapore"
            ).unlocked
        )

    def test_auckland_can_already_be_the_next_day(self):
        letter = self._letter("Pacific/Auckland", "2027-02-01T00:00:00", "AKL_SECRET")
        akl = ZoneInfo("Pacific/Auckland")
        akl_midnight = datetime(2027, 2, 1, 0, 0, tzinfo=akl)
        as_singapore = akl_midnight.astimezone(SG)
        self.assertEqual(as_singapore.date().isoformat(), "2027-01-31")
        self.assertTrue(present_one(letter, as_singapore, "Asia/Singapore").unlocked)
        self.assertFalse(
            present_one(letter, akl_midnight - timedelta(seconds=1), "Asia/Singapore").unlocked
        )

    def test_omitted_timezone_uses_the_default(self):
        letter = {
            "id": "x",
            "month": "May",
            "label": "L",
            "unlock": "2027-05-01T00:00:00",
            "title": "T",
            "body": "BODY",
        }
        tokyo_midnight = datetime(2027, 5, 1, 0, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
        # Tokyo midnight on 1 May is still 23:00 on 30 April in Singapore.
        self.assertFalse(present_one(letter, tokyo_midnight, "Asia/Singapore").unlocked)
        self.assertTrue(
            present_one(
                letter, datetime(2027, 5, 1, 0, 0, tzinfo=SG), "Asia/Singapore"
            ).unlocked
        )

    def test_bad_timezone_or_naive_clock_stays_sealed(self):
        letter = self._letter("Not/AZone", "2027-01-01T00:00:00", "SECRET")
        env = present_one(letter, datetime(2028, 1, 1, tzinfo=SG), "Asia/Singapore")
        self.assertFalse(env.unlocked)
        self.assertIsNone(env.body)
        naive = present_one(
            self._letter("Asia/Singapore", "2027-01-01T00:00:00", "SECRET"),
            datetime(2027, 1, 1),
            "Asia/Singapore",
        )
        self.assertFalse(naive.unlocked)
        self.assertIsNone(naive.body)

    def _letter(self, timezone: str, unlock: str, body: str) -> dict:
        return {
            "id": "z",
            "month": "Test",
            "label": "Label",
            "unlock": unlock,
            "timezone": timezone,
            "title": "Title",
            "body": body,
            "song": "",
            "photos": [],
        }


class PreviewTests(unittest.TestCase):
    def test_preview_shapes(self):
        self.assertEqual(
            parse_preview("2027-02-14", SG), datetime(2027, 2, 14, 0, 0, tzinfo=SG)
        )
        self.assertEqual(
            parse_preview("2027-02-14T21:05", SG),
            datetime(2027, 2, 14, 21, 5, tzinfo=SG),
        )
        self.assertEqual(
            parse_preview("  2027-02-14T21:05:09  ", SG),
            datetime(2027, 2, 14, 21, 5, 9, tzinfo=SG),
        )
        for bad in ("2027-02-14T21:05:09+08:00", "14-02-2027", "2027-13-01", "", "2027-02-14T25:00"):
            with self.subTest(bad=bad):
                self.assertIsNone(parse_preview(bad, SG))

    def test_secret_gates_the_clock(self):
        real = datetime(2026, 11, 18, 15, 0, tzinfo=SG)
        wrong = resolve_clock(real, "2027-08-01", "nope", "secret", SG, "Asia/Singapore")
        self.assertFalse(wrong.previewing)
        self.assertEqual(wrong.instant, real)
        self.assertIsNone(wrong.banner)
        self.assertIsNone(wrong.key_value)

        right = resolve_clock(real, "2027-08-01T18:30", "secret", "secret", SG, "Asia/Singapore")
        self.assertTrue(right.previewing)
        self.assertEqual(right.instant, datetime(2027, 8, 1, 18, 30, tzinfo=SG))
        self.assertEqual(
            right.banner, "Previewing 1 Aug 2027, 6:30 PM (Asia/Singapore)"
        )
        self.assertNotIn("secret", right.banner)

        broken = resolve_clock(real, "tomorrow", "secret", "secret", SG, "Asia/Singapore")
        self.assertFalse(broken.previewing)
        self.assertEqual(broken.instant, real)

        self.assertFalse(
            resolve_clock(real, "2027-08-01", "", "secret", SG, "Asia/Singapore").previewing
        )
        self.assertFalse(
            resolve_clock(real, "2027-08-01", "secret", None, SG, "Asia/Singapore").previewing
        )
        self.assertFalse(
            resolve_clock(real, "2027-08-01", "secret", "secret\n", SG, "Asia/Singapore").previewing
        )
        huge = "k" * 5000
        self.assertFalse(
            resolve_clock(real, "2027-08-01", huge, huge, SG, "Asia/Singapore").previewing
        )

    def test_preview_key_opens_and_hides_the_year(self):
        real = datetime(2026, 11, 18, 9, 0, tzinfo=SG)
        unlock = SETTINGS["page_unlock"]
        zone = SETTINGS["page_timezone"]
        denied = resolve_clock(real, "2027-03-05", "nope", "secret", SG, zone)
        self.assertFalse(year_is_open(denied.instant, unlock, zone))
        allowed = resolve_clock(real, "2027-03-05", "secret", "secret", SG, zone)
        self.assertTrue(year_is_open(allowed.instant, unlock, zone))
        still_early = resolve_clock(real, "2026-12-31", "secret", "secret", SG, zone)
        self.assertFalse(year_is_open(still_early.instant, unlock, zone))

    def test_query_and_secret_helpers(self):
        self.assertEqual(query_value({"preview": "2027-01-01"}, "preview"), "2027-01-01")
        self.assertEqual(query_value({"preview": ["2027-01-01", "x"]}, "preview"), "2027-01-01")
        self.assertIsNone(query_value({"preview": "  "}, "preview"))
        self.assertIsNone(query_value({}, "preview"))
        self.assertIsNone(query_value({"preview": "a" * 600}, "preview"))
        self.assertIsNone(key_from_mapping({}))
        self.assertIsNone(key_from_mapping({"preview_key": ""}))
        self.assertIsNone(key_from_mapping({"preview_key": 12}))
        self.assertEqual(key_from_mapping({"preview_key": "abc"}), "abc")
        self.assertEqual(
            format_clock(datetime(2027, 6, 1, 0, 0, tzinfo=SG), "Asia/Singapore"),
            "1 Jun 2027, 12:00 AM (Asia/Singapore)",
        )


class RenderTests(unittest.TestCase):
    def test_locked_letter_never_reaches_the_html(self):
        secret_body = "SUPER_SECRET_BODY_LINE"
        secret_title = "SUPER_SECRET_TITLE"
        song = "https://open.spotify.com/track/abc123XYZ"
        photo = "assets/letters/secret-jan.jpg"
        letter = {
            "id": "2027-01",
            "month": "January",
            "label": "Birthday note",
            "unlock": "2027-01-27T00:00:00",
            "timezone": "Asia/Singapore",
            "title": secret_title,
            "body": secret_body,
            "song": song,
            "photos": [photo],
        }
        before = datetime(2027, 1, 26, 23, 59, 59, tzinfo=SG)
        bits = compose_page([letter], before, "Asia/Singapore", "2027-01", {}, "🤍", True)
        blob = bits.grid_html + bits.letter_html + bits.song + " ".join(bits.photos)
        self.assertNotIn(secret_body, blob)
        self.assertNotIn(secret_title, blob)
        self.assertNotIn("spotify", blob.lower())
        self.assertNotIn("secret-jan", blob)
        self.assertEqual(bits.letter_html, "")
        self.assertEqual(bits.song, "")
        self.assertEqual(bits.photos, ())
        self.assertIn("Birthday note", bits.grid_html)
        self.assertIn("Opens 27 Jan 2027", bits.grid_html)
        self.assertNotIn("open=2027-01", bits.grid_html)
        self.assertNotIn("<script>", bits.grid_html)

        # Unlocked, but not the one being read: still no letter text.
        ready = datetime(2027, 1, 27, 0, 0, tzinfo=SG)
        waiting = compose_page([letter], ready, "Asia/Singapore", None, {}, "🤍", False)
        self.assertEqual(waiting.letter_html, "")
        self.assertNotIn(secret_body, waiting.grid_html)
        self.assertIn("open=2027-01", waiting.grid_html)
        self.assertNotIn("key=", waiting.grid_html)

        opened = compose_page(
            [letter],
            ready,
            "Asia/Singapore",
            "2027-01",
            {"preview": "2027-01-27", "key": "secret"},
            "🤍",
            True,
        )
        self.assertIn(secret_body, opened.letter_html)
        self.assertIn(secret_title, opened.letter_html)
        self.assertNotIn(secret_body, opened.grid_html)
        self.assertEqual(opened.song, song)
        self.assertEqual(opened.photos, (photo,))
        self.assertNotIn(song, opened.grid_html)
        self.assertNotIn(song, opened.letter_html)
        self.assertIn("key=secret", opened.grid_html)
        self.assertIn("preview=2027-01-27", opened.grid_html)

    def test_real_letters_stay_out_of_the_page_until_opened(self):
        new_year = _at("2027-01-01T00:00:00")
        bits = compose_page(LETTERS, new_year, "Asia/Singapore", "2027-01", {}, "🤍", True)
        blob = bits.grid_html + bits.letter_html
        for letter in LETTERS:
            self.assertNotIn(letter["title"], blob)
            self.assertNotIn(letter["body"].strip().splitlines()[0], blob)
        self.assertEqual(bits.song, "")
        self.assertEqual(bits.photos, ())
        self.assertIn("Opens 27 Jan 2027", bits.grid_html)
        self.assertIn("Opens 14 Feb 2027", bits.grid_html)
        self.assertIn("Opens 5 Mar 2027", bits.grid_html)
        self.assertIn("Opens 8 Nov 2027", bits.grid_html)
        self.assertIn("Opens 1 Dec 2027", bits.grid_html)
        self.assertIn("Valentine", bits.grid_html)

        valentine = _at("2027-02-14T00:00:00")
        opened = compose_page(LETTERS, valentine, "Asia/Singapore", "2027-02", {}, "🤍", True)
        february = next(letter for letter in LETTERS if letter["id"] == "2027-02")
        january = next(letter for letter in LETTERS if letter["id"] == "2027-01")
        march = next(letter for letter in LETTERS if letter["id"] == "2027-03")
        self.assertIn(february["title"], opened.letter_html)
        self.assertNotIn(february["title"], opened.grid_html)
        self.assertNotIn(january["title"], opened.letter_html + opened.grid_html)
        self.assertNotIn(march["title"], opened.letter_html + opened.grid_html)
        self.assertIn("open=2027-01", opened.grid_html)
        self.assertNotIn("open=2027-03", opened.grid_html)

        forced = compose_page(LETTERS, valentine, "Asia/Singapore", "2027-03", {}, "🤍", True)
        self.assertEqual(forced.letter_html, "")
        self.assertNotIn(march["title"], forced.grid_html)

        just_before = valentine - timedelta(seconds=1)
        early = compose_page(LETTERS, just_before, "Asia/Singapore", "2027-02", {}, "🤍", True)
        self.assertNotIn(february["title"], early.letter_html + early.grid_html)

    def test_html_escapes_labels_and_the_header(self):
        letter = {
            "id": "2027-04",
            "month": "April",
            "label": "</div><script>alert(1)</script>",
            "unlock": "2027-04-01T00:00:00",
            "timezone": "Asia/Singapore",
            "title": "<img>",
            "body": "<b>secret</b>",
            "song": "",
            "photos": [],
        }
        bits = compose_page(
            [letter],
            _at("2027-04-01T00:00:00"),
            "Asia/Singapore",
            "2027-04",
            {},
            "🤍",
            False,
        )
        self.assertNotIn("<script>", bits.grid_html)
        self.assertIn("&lt;script&gt;", bits.grid_html)
        self.assertNotIn("<b>", bits.letter_html)
        self.assertIn("&lt;b&gt;", bits.letter_html)
        header = header_html("Hi <b>", "🤍", "<script>alert(1)</script>", None)
        self.assertNotIn("<script>", header)
        self.assertIn("&lt;script&gt;", header)
        self.assertIn("🤍", header)
        self.assertEqual(safe_accent("#fff"), "#fff")
        self.assertEqual(safe_accent("#f4efe6"), "#f4efe6")
        self.assertEqual(safe_accent("red"), "#f4efe6")
        self.assertEqual(safe_accent("#f4efe6; } body{display:none"), "#f4efe6")


class SongTests(unittest.TestCase):
    def test_classify(self):
        kind, value = classify_song("https://open.spotify.com/track/abc123?si=xyz")
        self.assertEqual(kind, "spotify")
        self.assertEqual(value, "https://open.spotify.com/embed/track/abc123")
        kind, value = classify_song("https://open.spotify.com/intl-en/album/AbC987")
        self.assertEqual(value, "https://open.spotify.com/embed/album/AbC987")
        kind, value = classify_song("spotify:playlist:PlAy99")
        self.assertEqual(value, "https://open.spotify.com/embed/playlist/PlAy99")
        kind, value = classify_song("https://youtu.be/abcdefghijk?t=10")
        self.assertEqual(kind, "youtube")
        self.assertEqual(value, "https://www.youtube-nocookie.com/embed/abcdefghijk")
        kind, value = classify_song("https://www.youtube.com/shorts/abcdefghijk")
        self.assertEqual(value, "https://www.youtube-nocookie.com/embed/abcdefghijk")
        kind, value = classify_song("https://example.com/song")
        self.assertEqual((kind, value), ("link", "https://example.com/song"))
        self.assertEqual(classify_song("")[0], "none")
        self.assertEqual(classify_song("PLACEHOLDER song")[0], "none")
        self.assertEqual(classify_song("javascript:alert(1)")[0], "none")


class KoreaTests(unittest.TestCase):
    def test_folder_orders_images_and_skips_the_rest(self):
        with TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "b.JPG").write_bytes(TINY_PNG)
            (folder / "a.png").write_bytes(TINY_PNG)
            (folder / "notes.txt").write_text("hi")
            (folder / ".hidden.png").write_bytes(TINY_PNG)
            (folder / "captions.toml").write_text('"a.png" = "hello"\n')
            names = [path.name for path in list_image_files(folder)]
            self.assertEqual(names, ["a.png", "b.JPG"])
            captions, error = read_captions(folder / "captions.toml")
            self.assertIsNone(error)
            self.assertEqual(captions, {"a.png": "hello"})

    def test_empty_missing_and_broken_captions(self):
        with TemporaryDirectory() as tmp:
            folder = Path(tmp)
            self.assertEqual(list_image_files(folder), [])
            self.assertEqual(list_image_files(folder / "missing"), [])
            captions, error = read_captions(folder / "captions.toml")
            self.assertEqual(captions, {})
            self.assertIsNone(error)
            (folder / "captions.toml").write_text("this is not [\n")
            captions, error = read_captions(folder / "captions.toml")
            self.assertEqual(captions, {})
            self.assertIsNotNone(error)

    def test_thirty_images_one_image_and_none(self):
        shots = [
            Polaroid(f"{i:02d}.jpg", "data:image/jpeg;base64,aaaa", "", float((i % 7) - 3), 10, 10)
            for i in range(30)
        ]
        full = wall_html("Korea", "Dec 2026 – Jan 2027", "", shots, None)
        self.assertEqual(full.count("<img "), 30)
        self.assertNotIn("No pictures yet.", full)
        one = wall_html("Korea", "Dec 2026 – Jan 2027", "", shots[:1], None)
        self.assertEqual(one.count("<img "), 1)
        empty = wall_html("Korea", "Dec 2026 – Jan 2027", "", [], None)
        self.assertIn("No pictures yet.", empty)
        self.assertNotIn("<img", empty)
        noted = wall_html("Korea", "Dec 2026 – Jan 2027", "A note", [], None)
        self.assertIn("A note", noted)
        blank = wall_html("Korea", "Dec 2026 – Jan 2027", "", [], None)
        self.assertNotIn("A note", blank)

    def test_caption_and_title_are_escaped(self):
        shot = Polaroid("a.jpg", "data:image/jpeg;base64,aaaa", "<b>", 1.0, 4, 4)
        html = wall_html("<script>", "", "", [shot], None)
        self.assertIn("&lt;b&gt;", html)
        self.assertNotIn("<b>", html)
        self.assertNotIn("<script>", html)

    def test_small_png_becomes_a_picture(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "one.png"
            path.write_bytes(TINY_PNG)
            shot = polaroid_from_path(path, "Hi <there>")
            self.assertIsNotNone(shot)
            self.assertTrue(shot.src.startswith("data:image/"))
            html = wall_html("Korea", "Dec 2026 – Jan 2027", "", [shot], None)
            self.assertIn("Hi &lt;there&gt;", html)
            self.assertEqual(html.count("<img "), 1)

    def test_photo_path_cannot_leave_the_project(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "proj"
            root.mkdir()
            outside = base / "outside.png"
            outside.write_bytes(TINY_PNG)
            inside = root / "shot.png"
            inside.write_bytes(TINY_PNG)
            (root / "notes.txt").write_text("secret")
            link = root / "linked.png"
            link.symlink_to(outside)
            self.assertEqual(safe_photo_path(root, "shot.png"), inside.resolve())
            self.assertIsNone(safe_photo_path(root, "notes.txt"))
            self.assertIsNone(safe_photo_path(root, "../outside.png"))
            self.assertIsNone(safe_photo_path(root, str(outside)))
            self.assertIsNone(safe_photo_path(root, "linked.png"))
            self.assertIsNone(safe_photo_path(root, "https://example.com/a.png"))

    def test_shipped_korea_folder_starts_empty(self):
        folder = ROOT / "assets" / "korea"
        self.assertTrue((folder / "captions.toml").is_file())
        self.assertEqual(list_image_files(folder), [])
        captions, error = read_captions(folder / "captions.toml")
        self.assertEqual(captions, {})
        self.assertIsNone(error)


if __name__ == "__main__":
    unittest.main(verbosity=2)
