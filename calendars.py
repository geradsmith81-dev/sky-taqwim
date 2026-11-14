"""One interface over the four calendars, used by the pages, and the Sunni / Shia defaults.

Calendars (keys):
  ummalqura  Umm al-Qura, the official calendar of Saudi Arabia (table, or the current rule from JPL)
  sighting   crescent sighting: a month begins after the evening on which the young crescent is
             predicted visible from the chosen place (else the month is completed to 30 days)
  tabular    the arithmetic (30-year cycle) calendar: Kuwaiti / standard, or Fatimid (Bohra)
  solar      the solar Hijri calendar of Iran and Afghanistan (Nowruz at the March equinox)
"""
from __future__ import annotations

import zlib
from dataclasses import dataclass, field
from datetime import date, timedelta

import arabic_names as an
import holidays as hol
import sighting_calendar as sc
import solar_hijri_calendar as shc
import tabular_calendar as tc
import ummalqura_calendar as uq

UMMALQURA, SIGHTING, TABULAR, SOLAR = "ummalqura", "sighting", "tabular", "solar"
ALL = [UMMALQURA, SIGHTING, TABULAR, SOLAR]
LUNAR = [UMMALQURA, SIGHTING, TABULAR]

NAME = {UMMALQURA: "Umm al-Qura", SIGHTING: "Crescent sighting", TABULAR: "Tabular", SOLAR: "Solar Hijri"}
NAME_AR = {UMMALQURA: "تقويم أم القرى", SIGHTING: "رؤية الهلال", TABULAR: "التقويم الحسابي",
           SOLAR: "التقويم الهجري الشمسي"}
HELP = {
    UMMALQURA: "The official calendar of Saudi Arabia, computed in advance for Mecca. The religious dates "
               "(Ramadan, the Eids, the Hajj) are declared there from sightings and can differ by a day.",
    SIGHTING: "Each month begins after the evening on which the young crescent is predicted visible from the "
              "chosen place; if it is not visible on the evening ending the 29th, the month has 30 days.",
    TABULAR: "A fixed arithmetic calendar: months of 30 and 29 days in turn, and 11 leap years in every 30.",
    SOLAR: "The official calendar of Iran (and of Afghanistan). The year begins at the March equinox "
           "(Nowruz). It is a civil calendar; religious days follow the lunar months.",
}

# ---------------------------------------------------------------------------------------------- branches
BRANCHES = ["sunni", "shia"]
BRANCH_NAME = {"sunni": ("Sunni", "أهل السنة"), "shia": ("Shia", "الشيعة")}

# sighting rules offered per tradition: key -> (label, criterion, reference: "mecca" | "local")
SIGHTING_RULES = {
    "sunni": {
        "mecca_eye": ("Seen from Mecca with the naked eye (as the Saudi Supreme Court seeks)", "yallop_B", "mecca"),
        "mecca_aid": ("Seen from Mecca, binoculars or telescope accepted", "odeh_C", "mecca"),
        "local_eye": ("Seen from your own place with the naked eye (local sighting)", "yallop_B", "local"),
        "local_aid": ("Seen from your own place, optical aid accepted", "odeh_C", "local"),
    },
    "shia": {
        "local_eye": ("Naked eye on your local horizon (e.g. Ayatollah Sistani, Makarem Shirazi)", "yallop_B", "local"),
        "local_aid": ("Optical aid accepted on your local horizon (e.g. Ayatollah Khamenei, Bahjat)", "odeh_C", "local"),
        "najaf_eye": ("Naked eye from Najaf", "yallop_B", "Najaf"),
        "qom_aid": ("Optical aid accepted, from Qom", "odeh_C", "Qom"),
    },
}
DEFAULTS = {
    "sunni": {"calendar": UMMALQURA, "sighting_rule": "mecca_eye", "tabular": "kuwaiti", "method": "mwl"},
    "shia": {"calendar": SIGHTING, "sighting_rule": "local_eye", "tabular": "kuwaiti", "method": "jafari"},
}


# ---------------------------------------------------------------------------------------------- views
@dataclass
class View:
    """A calendar plus the holidays of one tradition."""
    key: str
    cal: object
    branch: str
    opts: dict = field(default_factory=dict)
    detail: str = ""          # e.g. "from Mecca, Yallop B"

    @property
    def name(self) -> str:
        if self.key == TABULAR:
            return "Tabular (Fatimid)" if getattr(self.cal, "variant", "") == "fatimid" else "Tabular"
        return NAME[self.key]

    @property
    def name_ar(self) -> str:
        return NAME_AR[self.key]

    @property
    def short(self) -> str:
        return {UMMALQURA: "Umm al-Qura", SIGHTING: "Sighting", TABULAR: "Tabular", SOLAR: "Solar"}[self.key]

    @property
    def solar(self) -> bool:
        return self.key == SOLAR

    @property
    def era(self) -> str:
        return "SH" if self.solar else "AH"

    @property
    def first_day(self) -> date:
        return self.cal.first_day

    @property
    def last_day(self) -> date:
        return self.cal.last_day

    def covers(self, d: date) -> bool:
        return self.cal.covers(d)

    def hdate(self, d: date):
        return self.cal.from_gregorian(d) if self.cal.covers(d) else None

    def month_at(self, d: date):
        return self.cal.month_of(d)

    def get_month(self, y: int, m: int):
        return self.cal.get_month(y, m)

    def year_months(self, y: int):
        return self.cal.year_months(y)

    def years(self) -> list[int]:
        return self.cal.years()

    def year_of(self, d: date) -> int | None:
        h = self.hdate(d)
        return h.year if h else None

    def month_name(self, m: int) -> tuple[str, str]:
        if self.solar:
            return an.SOLAR_MONTHS[m][0], an.SOLAR_MONTHS[m][1]
        return an.MONTHS[m][0], an.MONTHS[m][1]

    def holidays_for_year(self, y: int) -> list:
        if self.solar:
            return hol.solar_holidays_for_year(self.cal, y)
        return hol.holidays_for_year(self.cal, y, self.branch, **self.opts)

    def holidays_between(self, start: date, end: date) -> list:
        if self.solar:
            out = []
            for y in {self.year_of(start), self.year_of(end)} - {None}:
                out += [h for h in hol.solar_holidays_for_year(self.cal, y) if start <= h.date <= end]
            return sorted(out, key=lambda h: h.date)
        return hol.holidays_between(self.cal, start, end, self.branch, **self.opts)


def sighting_place(rule_key: str, branch: str, place: dict) -> tuple[dict | None, str]:
    """The reference place of a sighting rule: None = Mecca (precomputed), else a place dict."""
    label, crit, ref = SIGHTING_RULES[branch][rule_key]
    if ref == "mecca":
        return None, "Mecca"
    if ref == "local":
        return {"name": place.get("name", ""), "lat": float(place["lat"]), "lon": float(place["lon"]),
                "tz": place["tz"]}, place.get("label", place.get("name", "your place"))
    p = sc.PRESETS_BY_NAME[ref]
    return p, p["name"]


def local_span(today: date, years: int = 6) -> tuple[date, date]:
    """The span computed for a sighting calendar at a place other than Mecca."""
    return (date(today.year - years, 1, 1), date(today.year + years, 12, 31))


# ---------------------------------------------------------------------------------------------- export
def to_ics(holidays: list, calname: str) -> str:
    """All-day iCalendar events (the Islamic day starts the evening before; noted in each event)."""
    def esc(s: str) -> str:
        return s.replace("\\", "\\\\").replace(";", r"\;").replace(",", r"\,").replace("\n", r"\n")

    lines = ["BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//Sky Taqwim//Islamic calendar//EN",
             "CALSCALE:GREGORIAN", f"X-WR-CALNAME:{esc(calname)}"]
    stamp = date.today().strftime("%Y%m%dT000000Z")
    for h in holidays:
        slug = "".join(c for c in h.name.lower() if c.isalnum())[:40]
        desc = f"{h.hdate} ({calname})" if h.hdate else calname
        if h.begins_evening_before:
            desc += ". Begins at sunset the evening before."
        if h.note:
            desc += f" {h.note}"
        lines += ["BEGIN:VEVENT",
                  f"UID:{h.date:%Y%m%d}-{slug}-{zlib.crc32(calname.encode('utf-8')):08x}@sky-taqwim",
                  f"DTSTAMP:{stamp}",
                  f"DTSTART;VALUE=DATE:{h.date:%Y%m%d}",
                  f"DTEND;VALUE=DATE:{(h.date + timedelta(days=1)):%Y%m%d}",
                  f"SUMMARY:{esc(h.name)}",
                  f"DESCRIPTION:{esc(desc)}",
                  "TRANSP:TRANSPARENT", "END:VEVENT"]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"
