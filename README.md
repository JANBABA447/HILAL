# hilal — Islamic calendar & crescent engine

Free, open-source engine behind the Islamic Studies Library app (project 13-ISSLAM).
For **any place on Earth and any date** it computes:

* new / full moons (same Meeus algorithms NASA uses for its moon-phase catalog)
* sunset, moonset, Moon age, altitude, elongation, illumination
* crescent visibility by the **Odeh (2004)** and **Yallop (1997)** criteria
* Hijri calendars as pluggable *rules*: Umm al-Qura (Saudi), local naked-eye sighting at any location, FCNA (published table)
* prayer times: MWL, ISNA, Egypt, Makkah (Umm al-Qura), Karachi, Tehran, Ja'fari; Asr standard or Hanafi
* **full 24-hour timeline by school** (Hanafi, Shafi'i, Maliki, Hanbali, Ja'fari): start and end of every prayer,
  preferred times, prohibited and disliked times, night thirds and midnight, to the second (`timeline.py`)

No tables are stored: everything is calculated, so it works for any year.

## Quick start
```bash
python -m hilal --lat 34.015 --lon 71.525 --tz Asia/Karachi --date 2027-02-08 --method Karachi --asr hanafi
python tests/run_tests.py          # or: pip install -e .[dev] && pytest
```

```python
from datetime import date
from hilal.places import DALLAS
from hilal import crescent, prayer
from hilal.calendars import HijriCalendar, UmmAlQura
ev = crescent.evening(date(2027, 2, 7), DALLAS)        # ev['odeh'] -> 'A' (naked eye)
from hilal import timeline
for name, start, end, status, note in timeline.day(date(2027, 2, 7), DALLAS, 'hanafi', fajr_angle=15):
    print(name, start.time(), end.time(), status)
times = prayer.times(date(2027, 2, 7), DALLAS, 'ISNA')
uq = HijriCalendar(UmmAlQura(), date(2002, 3, 15), 0, 1423)
print(uq.to_hijri(date(2027, 2, 8)))                   # (1448, 8, 1) = 1 Ramadan 1448
```

## Validation (tests/)
| Test | Reference | Result |
|---|---|---|
| Moon phases | NASA/GSFC Espenak catalog, 248 events 2024–2031, 2075, 2100 | max 31 s |
| Moon position | Meeus example 47.a | < 0.0001° |
| Umm al-Qura | van Gent (Utrecht), 140 dates 1423–1450 AH | 140/140 |
| Pakistan | Ruet-e-Hilal decisions Rajab 1447 – Rabi II 1448 | 10/10 (Peshawar naked-eye) |
| Prayer times | Islamic Center of Irving 2026 flier | within 3 min (ISNA 15/15) |
| Timeline | boundaries in order every 5 days 2026–2030, 3 cities; agrees with prayer module | within 2 s |

Known limitation: the FCNA 8°/5° *rule* reproduces about 80% of FCNA's published dates, so FCNA dates are taken from
their published table (to 2045) — see `tests/data/fcna_published.csv`.

## Layout
```
src/hilal/   astro.py crescent.py calendars.py prayer.py timeline.py places.py cli.py
tests/       unit tests + reference data (NASA, Umm al-Qura, FCNA, Pakistan, ICI)
tools/       scripts that generated documents ISL-CAL-011/012/013/014
```
Documentation: ISL-APP-001 (design, formulas, validation), ISL-CAL-014 (prayer rules by school), ISL-APP-003 (app structure). License: MIT.
