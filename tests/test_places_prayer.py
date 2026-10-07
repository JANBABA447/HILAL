import os, json, csv
from datetime import date, timedelta
from hilal import prayer as P
from hilal.places import IRVING, PESHAWAR
from hilal.calendars import HijriCalendar, LocalSighting, first_visibility_start
from hilal import astro as A
from datetime import datetime, timezone
HERE = os.path.dirname(__file__)

def _min(s, pm):
    h, m = map(int, s.split(':')); return (h % 12 + (12 if pm else 0)) * 60 + m

def test_ici_irving_prayer_times():
    """ISNA 15/15, Asr standard, +5 min Dhuhr, +3 min Maghrib reproduces the ICI 2026 flier within 3 minutes."""
    data = json.load(open(os.path.join(HERE, 'data', 'ici_irving_2026.json')))['times']
    worst = 0
    for mo, days in data.items():
        for dd, v in days.items():
            t = P.times(date(2026, int(mo), int(dd)), IRVING, 'ISNA', 'standard', adjust={'dhuhr': 5, 'maghrib': 3})
            for k, i, pm in (('fajr', 0, False), ('sunrise', 1, False), ('asr', 3, True), ('maghrib', 4, True), ('isha', 5, True)):
                c = t[k].hour * 60 + t[k].minute + t[k].second / 60
                worst = max(worst, abs(c - _min(v[i], pm)))
    assert worst <= 3.0, worst

def test_pakistan_2026_decisions_match_peshawar_naked_eye():
    rows = [r for r in csv.reader(l for l in open(os.path.join(HERE, 'data', 'pakistan_ruet_e_hilal_2025_2026.csv')) if not l.startswith('#'))]
    conj = A.new_moons_between(A.jd_from_dt(datetime(2025, 10, 20, tzinfo=timezone.utc)), A.jd_from_dt(datetime(2025, 10, 23, tzinfo=timezone.utc)))[0]
    cal = HijriCalendar(LocalSighting(PESHAWAR), first_visibility_start(PESHAWAR, conj), 4, 1447).extend_to(date(2026, 10, 1))
    miss = [(y, m, d) for y, m, d in rows if str(cal.month_start(int(y), int(m))) != d]
    assert not miss, miss
