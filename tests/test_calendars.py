import os, csv
from datetime import date, timedelta
from hilal.calendars import HijriCalendar, UmmAlQura

HERE = os.path.dirname(__file__)

def load_uq():
    rows = []
    for r in csv.reader(l for l in open(os.path.join(HERE, 'data', 'ummalqura_principal.csv')) if not l.startswith('#')):
        y = int(r[0]); f = date.fromisoformat
        rows += [(y, 0, f(r[1])), (y, 2, f(r[2]) - timedelta(days=11)), (y, 8, f(r[3])), (y, 9, f(r[4])),
                 (y, 11, f(r[5]) - timedelta(days=9))]
    return rows

def uq_calendar():
    cal = HijriCalendar(UmmAlQura(), date(2002, 3, 15), 0, 1423)
    return cal.extend_to(date(2029, 5, 1))

def test_ummalqura_principal_days():
    cal = uq_calendar(); miss = []
    for y, m, d in load_uq():
        got = cal.month_start(y, m)
        if got != d: miss.append((y, m, str(d), str(got)))
    assert not miss, miss
