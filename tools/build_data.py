"""Compute all data for the three-city lunar calendar documents (2026-2030) -> JSON."""
import sys, json, csv, os
from datetime import date, datetime, time, timedelta, timezone
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from hilal import astro as A, crescent as C
from hilal.calendars import HijriCalendar, UmmAlQura, LocalSighting, first_visibility_start, MONTHS
from hilal.places import MAKKAH, MADINAH, PESHAWAR, DALLAS

OUT = sys.argv[1] if len(sys.argv) > 1 else 'lunar_data.json'
END = date(2031, 3, 1)
iso = lambda d: d.isoformat()

# ---- calendars ----
uq = HijriCalendar(UmmAlQura(), date(2002, 3, 15), 0, 1423).extend_to(END)
conj_oct = A.new_moons_between(A.jd_from_dt(datetime(2025, 10, 20, tzinfo=timezone.utc)), A.jd_from_dt(datetime(2025, 10, 23, tzinfo=timezone.utc)))[0]
cities = {'makkah': MAKKAH, 'madinah': MADINAH, 'peshawar': PESHAWAR, 'dallas': DALLAS}
local = {}
for k, p in cities.items():
    a = first_visibility_start(p, conj_oct)
    local[k] = HijriCalendar(LocalSighting(p), a, 4, 1447).extend_to(END)
fcna = {}
for r in csv.reader(l for l in open(os.path.join(os.path.dirname(__file__), '..', 'tests', 'data', 'fcna_published.csv')) if not l.startswith('#')):
    for i in range(12): fcna[(int(r[0]), i)] = r[i + 1]
SAUDI_ANN = {(1447, 0): '2025-06-26', (1447, 8): '2026-02-18', (1447, 9): '2026-03-20', (1447, 11): '2026-05-18', (1448, 0): '2026-06-16'}
pk = json.load(open(os.path.join(os.path.dirname(__file__), '..', 'tests', 'data', 'pakistan_projection_isl_cal_005_008.json')))
PK_ACT = {('Rajab', 1447): '2025-12-22', ("Sha'ban", 1447): '2026-01-21', ('Ramadan', 1447): '2026-02-19', ('Shawwal', 1447): '2026-03-21',
          ("Dhul-Qa'dah", 1447): '2026-04-19', ('Dhul-Hijjah', 1447): '2026-05-18', ('Muharram', 1448): '2026-06-17', ('Safar', 1448): '2026-07-16',
          ('Rabi al-Awwal', 1448): '2026-08-15', ('Rabi al-Thani', 1448): '2026-09-14'}
OLDNAMES = ['Muharram', 'Safar', 'Rabi al-Awwal', 'Rabi al-Thani', 'Jumada al-Ula', 'Jumada al-Akhirah', 'Rajab', "Sha'ban", 'Ramadan', 'Shawwal', "Dhul-Qa'dah", 'Dhul-Hijjah']
pk_proj = {(m, y): d for d, m, y in pk['PK']}

def ev_dict(e):
    f = lambda j: A.dt_from_jd(j).isoformat() if j else None
    return dict(sunset=f(e['sunset']), moonset=f(e['moonset']), lag=e['lag_min'], age=e['age_h'], alt=e['alt'], elong=e['elong'],
                illum=e['illum'], V=e['V'], odeh=e['odeh'], q=e['q'], yallop=e['yallop'], W=e['W'], arcv=e['arcv'], daz=e['daz'])

months = []
for (y, m) in [(1447, i) for i in range(5, 12)] + [(yy, i) for yy in range(1448, 1452) for i in range(12)] + [(1452, i) for i in range(10)]:
    s_uq = uq.month_start(y, m)
    cj = A.previous_new_moon(A.jd_from_dt(datetime.combine(s_uq + timedelta(days=1), time(12), timezone.utc)))
    rec = dict(y=y, m=m, name=MONTHS[m], conj=A.dt_from_jd(cj).isoformat(), starts={}, evenings={})
    rec['starts']['uq'] = iso(s_uq)
    for k in cities: rec['starts'][k] = iso(local[k].month_start(y, m))
    rec['starts']['fcna'] = fcna.get((y, m))
    rec['starts']['saudi_announced'] = SAUDI_ANN.get((y, m))
    key = (OLDNAMES[m], y)
    if key in PK_ACT: rec['starts']['pakistan'] = PK_ACT[key]; rec['pk_status'] = 'actual'
    elif key in pk_proj: rec['starts']['pakistan'] = pk_proj[key]; rec['pk_status'] = 'projected'
    else: rec['starts']['pakistan'] = None; rec['pk_status'] = None
    for k, p in cities.items():
        d0 = A.dt_from_jd(cj).astimezone(p.zone).date()
        rec['evenings'][k] = [dict(date=iso(d0 + timedelta(days=i)), **ev_dict(C.evening(d0 + timedelta(days=i), p, cj))) for i in range(3)]
    months.append(rec)
    print(y, MONTHS[m], rec['starts'], flush=True)

json.dump(dict(months=months), open(OUT, 'w'), indent=0, default=str)
print('saved', OUT)
