"""Command line:  python -m hilal --lat 34.015 --lon 71.525 --tz Asia/Karachi [--date 2027-02-07] [--method Karachi --asr hanafi]
Prints tonight's crescent circumstances, and prayer times for the place."""
import argparse
from datetime import date
from .places import Place
from . import crescent as C, prayer as P, astro as A

def main():
    ap = argparse.ArgumentParser(description='hilal: crescent visibility and prayer times for any place')
    ap.add_argument('--lat', type=float, required=True); ap.add_argument('--lon', type=float, required=True)
    ap.add_argument('--tz', required=True, help='IANA time zone, e.g. America/Chicago')
    ap.add_argument('--date', default=date.today().isoformat())
    ap.add_argument('--method', default='MWL', choices=sorted(P.METHODS)); ap.add_argument('--asr', default='standard', choices=['standard', 'hanafi'])
    a = ap.parse_args()
    place = Place('custom', 'Custom place', a.lat, a.lon, a.tz); d = date.fromisoformat(a.date)
    e = C.evening(d, place)
    z = place.zone; f = lambda j: A.dt_from_jd(j).astimezone(z).strftime('%H:%M') if j else '-'
    print(f'{d}  ({a.lat}, {a.lon}, {a.tz})')
    print(f"Sunset {f(e['sunset'])}  Moonset {f(e['moonset'])}  Moon age {e['age_h']:.1f} h  altitude {e['alt']:.1f} deg  elongation {e['elong']:.1f} deg")
    print(f"Crescent: Odeh zone {e['odeh']} (V={e['V']:.2f})   Yallop zone {e['yallop']} (q={e['q']:+.3f})")
    t = P.times(d, place, a.method, a.asr)
    print('Prayer times (' + P.METHODS[a.method]['name'] + '): ' + '  '.join(f"{k.title()} {v:%H:%M}" for k, v in t.items() if v))

if __name__ == '__main__':
    main()
