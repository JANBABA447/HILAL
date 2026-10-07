from datetime import date, timedelta
from hilal import timeline as T, prayer as P
from hilal.places import MAKKAH, PESHAWAR, DALLAS, IRVING

ORDER = ['fajr', 'sunrise', 'ishraq', 'zawal_start', 'transit', 'asr1', 'asr2', 'yellowing', 'sunset',
         'jafari_maghrib', 'red', 'white', 'third', 'midnight', 'last_third', 'fajr_next']

def test_boundaries_are_in_order_2026_2030():
    for place in (MAKKAH, PESHAWAR, DALLAS):
        d = date(2026, 1, 1)
        while d <= date(2030, 12, 31):
            b = T.boundaries(d, place)
            seq = [b[k] for k in ORDER]
            assert all(x <= y for x, y in zip(seq, seq[1:])), (place.key, d)
            d += timedelta(days=5)

def test_timeline_matches_prayer_module():
    d = date(2026, 3, 1)
    for _ in range(60):
        t = P.times(d, IRVING, 'ISNA', 'standard')
        b = T.boundaries(d, IRVING, fajr_angle=15, white_angle=15)
        for k1, k2 in (('fajr', 'fajr'), ('sunrise', 'sunrise'), ('dhuhr', 'transit'), ('asr', 'asr1'),
                       ('maghrib', 'sunset'), ('isha', 'white')):
            assert abs((t[k1] - b[k2]).total_seconds()) <= 2, (d, k1)
        d += timedelta(days=6)

def test_every_school_covers_the_five_prayers():
    for s in T.SCHOOLS:
        names = ' '.join(x[0] for x in T.day(date(2027, 6, 21), PESHAWAR, s))
        for p in ('Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha'):
            assert p in names, (s, p)
