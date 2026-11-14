# Sky Taqwim · تقويم السماء

The Islamic calendar for **Sunni or Shia** practice, from NASA JPL astronomy (DE440s via Skyfield).

- **A Sunni / Shia switch** sets the holy days, the default calendar and sighting rule, and the prayer-time methods.
- **Four calendars:**
  - **Umm al-Qura · أم القرى**, the official Saudi calendar. It uses the published table for 1343–1500 AH and the current rule computed from JPL elsewhere. It matches the table in 932 of 936 months since 1423 AH.
  - **Crescent sighting · رؤية الهلال**. Months begin after the evening on which the crescent is predicted visible from Mecca, Najaf, Qom or your own place, by the Yallop or Odeh models, with the naked eye or with optical aid.
  - **Tabular · الحسابي**, standard (Kuwaiti) or Fatimid/Bohra.
  - **Solar Hijri · الهجري الشمسي** of Iran and Afghanistan, with Nowruz from the JPL equinox.
- **Prayer times:**
  - Sunni methods: MWL, ISNA, Egypt, Umm al-Qura, Karachi, Diyanet, the Gulf states, JAKIM and others, with Shafi'i or Hanafi Asr.
  - Shia methods: Leva Institute of Qum, and Tehran, with Ja'fari Maghrib and midnight.
  - Plus imsak, the qibla compass, and the Moon.
- **Pages:** Today, Month, Year & holy days (with .ics and .csv downloads), Prayer times, Crescent, Compare, How it works.
- **Sources:** each holy day opens a short sourced history (48 entries), and both traditions are presented in their own terms.
- **Location:** found automatically (the browser asks once). Proper nouns are also shown in Arabic script (Persian for the solar months). The design follows early Islamic (Umayyad and Abbasid) art.

See `HOW_IT_WORKS.md` for the rules and sources, and `docs/VALIDATION.md` for the checks.

## Put it online (GitHub + Streamlit Community Cloud)

1. On github.com, create a new **public** repository named `sky-taqwim`.
2. Choose **Add file → Upload files** and drag in *everything in this folder*. Upload the `assets`, `data`, `docs`, `ephem`, `tests` and `tools` folders as folders.
3. Browsers often skip the hidden `.streamlit` folder. If it is missing after the upload, choose **Add file → Create new file**, type the name `.streamlit/config.toml`, and paste the *contents* of `config.toml for GitHub (paste).txt` (not its file name).
4. At https://share.streamlit.io choose **Create app**, select the repository, branch `main` and file `app.py`. Under **Advanced settings** pick **Python 3.12**, then **Deploy**.
5. The first start downloads the NASA JPL file (32.7 MB), which takes about a minute.

## Run it on a computer

```
pip install -r requirements.txt
streamlit run app.py
```

Dates run from 1850 to 2149. Put de440.bsp in `ephem/` for the prayer times and the Moon to reach 1550–2650. The Mecca crescent table then needs rebuilding with `python tools/build_tables.py`.

The Arabic fonts are subsets of Noto Kufi Arabic and Noto Naskh Arabic, © The Noto Project Authors, under the SIL Open Font License (`assets/fonts/`).
