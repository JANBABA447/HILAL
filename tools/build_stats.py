"""Long-run statistics: synodic month lengths (2001-2100) and month-length behaviour of calendars."""
import sys, os, json
from datetime import date, datetime, timezone, timedelta
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from hilal import astro as A
from hilal.calendars import HijriCalendar, UmmAlQura, LocalSighting, first_visibility_start
from hilal.places import MAKKAH, PESHAWAR, DALLAS
OUT = sys.argv[1]
nm = A.new_moons_between(A.jd_from_dt(datetime(2001, 1, 1, tzinfo=timezone.utc)), A.jd_from_dt(datetime(2101, 1, 1, tzinfo=timezone.utc)))
syn = [b - a for a, b in zip(nm, nm[1:])]
syn_dates = [A.dt_from_jd(a).date().isoformat() for a in nm[:-1]]
res = dict(syn_min=min(syn), syn_max=max(syn), syn_mean=sum(syn) / len(syn), n=len(syn),
           syn_2026_2030=[(d, s) for d, s in zip(syn_dates, syn) if '2025-12' <= d < '2031'])
def lengths(cal):
    st = [s for s, m, y in cal.starts]
    L = [(b - a).days for a, b in zip(st, st[1:])]
    runs = Counter(); cur = 1
    for a, b in zip(L, L[1:]):
        if a == b: cur += 1
        else: runs[(a, cur)] += 1; cur = 1
    return dict(c29=L.count(29), c30=L.count(30), other=len(L) - L.count(29) - L.count(30),
                max_run29=max([r for (l, r) in runs if l == 29] or [0]), max_run30=max([r for (l, r) in runs if l == 30] or [0]), n=len(L))
end = date(2100, 12, 1)
uq = HijriCalendar(UmmAlQura(), date(2002, 3, 15), 0, 1423).extend_to(end)
res['uq'] = lengths(uq)
conj = A.new_moons_between(A.jd_from_dt(datetime(2002, 3, 12, tzinfo=timezone.utc)), A.jd_from_dt(datetime(2002, 3, 15, tzinfo=timezone.utc)))[0]
for p in (MAKKAH, PESHAWAR, DALLAS):
    cal = HijriCalendar(LocalSighting(p), first_visibility_start(p, conj), 0, 1423).extend_to(end)
    res[p.key] = lengths(cal)
    # difference to UQ for the same months
    diff = Counter()
    for (s, m, y) in cal.starts[:-2]:
        try: diff[(s - uq.month_start(y, m)).days] += 1
        except KeyError: pass
    res[p.key]['vs_uq'] = dict(diff)
    print(p.key, res[p.key], flush=True)
print('uq', res['uq'], 'syn', res['syn_min'], res['syn_max'])
json.dump(res, open(OUT, 'w'))
