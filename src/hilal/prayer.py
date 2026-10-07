"""Prayer times from the Sun's position.

Fajr / Isha  : Sun at a given depression angle below the horizon (or Isha = fixed minutes after Maghrib).
Sunrise / Maghrib : apparent upper limb on the horizon (altitude -0.833 deg), optionally + safety minutes.
Dhuhr        : Sun's transit (solar noon), optionally + safety minutes.
Asr          : shadow length = shadow factor x object height + noon shadow
               (factor 1: Shafi'i, Maliki, Hanbali, Ja'fari; factor 2: Hanafi).
High latitudes: 'angle_based' rule (portion of the night = angle/60) when Fajr/Isha do not occur.
"""
from math import sin, cos, tan, asin, acos, atan, radians as R, degrees as D
from datetime import datetime, date, time, timedelta
from . import astro as A

METHODS = {
    'MWL':       dict(name='Muslim World League',                         fajr=18.0, isha=17.0),
    'ISNA':      dict(name='Islamic Society of North America',            fajr=15.0, isha=15.0),
    'Egypt':     dict(name='Egyptian General Authority of Survey',        fajr=19.5, isha=17.5),
    'Makkah':    dict(name='Umm al-Qura University, Makkah',              fajr=18.5, isha_minutes=90, isha_minutes_ramadan=120),
    'Karachi':   dict(name='University of Islamic Sciences, Karachi',     fajr=18.0, isha=18.0),
    'Tehran':    dict(name='Institute of Geophysics, University of Tehran', fajr=17.7, isha=14.0, maghrib=4.5),
    'Jafari':    dict(name="Shia Ithna-Ashari (Leva Institute, Qum)",     fajr=16.0, isha=14.0, maghrib=4.0),
}

def _sun(jd):
    p = A.position(jd, 'sun')
    return p['ra'], p['dec']

def _transit(j0, lon):
    jd = j0 + 0.5 - lon / 360
    for _ in range(3):
        ra, _ = _sun(jd)
        H = (A.gmst(jd) + lon - ra + 180) % 360 - 180
        jd -= H / 360.98564736629
    return jd

def _time_for_altitude(transit_jd, lat, lon, alt, after_noon):
    jd = transit_jd + (0.25 if after_noon else -0.25)
    for _ in range(4):
        ra, dec = _sun(jd)
        c = (sin(R(alt)) - sin(R(lat)) * sin(R(dec))) / (cos(R(lat)) * cos(R(dec)))
        if abs(c) > 1: return None
        H0 = D(acos(c)) * (1 if after_noon else -1)
        H = (A.gmst(jd) + lon - ra + 180) % 360 - 180
        jd += ((H0 - H + 180) % 360 - 180) / 360.98564736629
    return jd

def times(d, place, method='MWL', asr='standard', ramadan=False, adjust=None, high_lat='angle_based'):
    """Prayer times for civil date d at place. Returns dict of aware datetimes in the place's time zone.
    adjust: optional minutes to add, e.g. {'dhuhr': 5, 'maghrib': 3} (local mosque safety margins)."""
    m = METHODS[method]; adjust = adjust or {}
    j0 = A.jd_from_dt(datetime.combine(d, time(0), place.zone))
    noon = _transit(j0, place.lon)
    _, dec = _sun(noon)
    sunrise = _time_for_altitude(noon, place.lat, place.lon, A.SUN_H0, False)
    sunset = _time_for_altitude(noon, place.lat, place.lon, A.SUN_H0, True)
    fajr = _time_for_altitude(noon, place.lat, place.lon, -m['fajr'], False)
    factor = 2 if asr == 'hanafi' else 1
    asr_alt = D(atan(1 / (factor + tan(abs(R(place.lat - dec))))))
    asr_t = _time_for_altitude(noon, place.lat, place.lon, asr_alt, True)
    maghrib = _time_for_altitude(noon, place.lat, place.lon, -m['maghrib'], True) if 'maghrib' in m else sunset
    if 'isha_minutes' in m:
        isha = sunset + (m['isha_minutes_ramadan'] if ramadan else m['isha_minutes']) / 1440
    else:
        isha = _time_for_altitude(noon, place.lat, place.lon, -m['isha'], True)
    if high_lat == 'angle_based' and sunrise and sunset:
        night = 1 - (sunset - sunrise)
        if fajr is None or sunrise - fajr > night * m['fajr'] / 60:
            fajr = sunrise - night * m['fajr'] / 60
        if 'isha' in m and (isha is None or isha - sunset > night * m['isha'] / 60):
            isha = sunset + night * m['isha'] / 60
    out = dict(fajr=fajr, sunrise=sunrise, dhuhr=noon, asr=asr_t, maghrib=maghrib, isha=isha)
    res = {}
    for k, v in out.items():
        if v is None: res[k] = None; continue
        res[k] = (A.dt_from_jd(v) + timedelta(minutes=adjust.get(k, 0))).astimezone(place.zone)
    return res
