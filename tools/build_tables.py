"""Rebuild data/crescents_mecca.csv.gz and data/seasons.csv from the JPL ephemeris.

Run from the engine (app) folder:  python tools/build_tables.py
Takes about 2 minutes.
"""
import os
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sighting_calendar as sc  # noqa: E402
import solar_hijri_calendar as shc  # noqa: E402

if __name__ == "__main__":
    sc.build_mecca_table(date(1850, 1, 1), date(2150, 1, 10))
    print("written:", sc.MECCA_FILE)
    shc.build_seasons()
    print("written:", shc.SEASONS_FILE)
