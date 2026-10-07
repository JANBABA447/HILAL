"""Daily sunrise/sunset/moonrise/moonset (local time) for Makkah, Peshawar, Dallas, 2026-2030."""
import sys, os, json
from datetime import date, datetime, time, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from hilal import astro as A
from hilal.places import MAKKAH, PESHAWAR, DALLAS
y0, y1, OUT = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
rows = []
d = date(y0, 1, 1)
while d.year <= y1:
    row = dict(date=d.isoformat())
    for p in (MAKKAH, PESHAWAR, DALLAS):
        j0 = A.jd_from_dt(datetime.combine(d, time(0), p.zone))
        sr, ss = A.rise_set(j0, p.lat, p.lon, 'sun')
        mr, ms = A.rise_set(j0, p.lat, p.lon, 'moon')
        f = lambda j: A.dt_from_jd(j).astimezone(p.zone).strftime('%H:%M') if j else '—'
        row[p.key] = [f(sr), f(ss), f(mr), f(ms)]
    row['illum'] = round(A.illuminated_fraction(A.jd_from_dt(datetime.combine(d, time(12), MAKKAH.zone))) * 100)
    rows.append(row); d += timedelta(days=1)
json.dump(rows, open(OUT, 'w'))
print(len(rows), rows[0], rows[-1])
