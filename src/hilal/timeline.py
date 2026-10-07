"""Full 24-hour prayer timeline by school of thought, computed to the second.

Juristic basis (summary; see ISL-CAL-014 for details)
  * Hadith of Jibril leading the prayers on two days (Abu Dawud 393, al-Tirmidhi 149): each prayer has a first
    and a last time.
  * Hadith of 'Abdullah ibn 'Amr (Muslim 612): Dhuhr until Asr; Asr until the Sun yellows; Maghrib until the
    twilight disappears; Isha until the middle of the night; Fajr until sunrise.
  * Prohibited times: 'Uqbah ibn 'Amir (Muslim 831) - at sunrise until the Sun is high, when the Sun stands at
    its highest until it declines, and when it begins to set until it sets. Abu Sa'id al-Khudri (al-Bukhari 586,
    Muslim 827) - no voluntary prayer after Fajr until sunrise and after Asr until sunset: these depend on when a
    person prays, so they are not clock times and are shown as notes.

Astronomical definitions (every parameter can be changed by the caller)
  true dawn (Fajr)        Sun at -fajr_angle below the horizon
  sunrise / sunset        Sun's upper limb on the horizon (-0.833 deg incl. refraction)
  zawal                   Sun's transit across the meridian (true local noon)
  Asr, one shadow         shadow = object + noon shadow       (Shafi'i, Maliki, Hanbali; Abu Yusuf & Muhammad; Ja'fari)
  Asr, two shadows        shadow = 2 x object + noon shadow   (Abu Hanifa)
  red twilight gone       Sun at -red_angle   (shafaq ahmar; default 15, published estimates 12-17)
  white twilight gone     Sun at -white_angle (shafaq abyad; default 18)
  eastern redness gone    Sun at -4 deg       (Ja'fari Maghrib)
  spear's height          sunrise + ishraq_min (default 15; estimates 12-20)
  zenith margin           zawal_min before transit (default 5)
  yellowing (isfirar)     sunset - isfirar_min (default 20; estimate)
  night                   sunset to next true dawn; middle and thirds of that night
"""
from datetime import datetime, time, timedelta
from math import sin, cos, acos, atan, tan, radians as R, degrees as D
from . import astro as A

SCHOOLS = {
    'hanafi': 'Hanafi',
    'shafii': "Shafi'i",
    'maliki': 'Maliki',
    'hanbali': 'Hanbali',
    'jafari': "Ja'fari (Shia Ithna 'Ashari)",
}


def _sun(jd):
    p = A.position(jd, 'sun')
    return p['ra'], p['dec']


def transit(j0, lon):
    """Sun's meridian transit (UT JD) on the local day starting at j0, iterated to < 0.01 s."""
    jd = j0 + 0.5 - lon / 360
    for _ in range(8):
        ra, _ = _sun(jd)
        dj = -((A.gmst(jd) + lon - ra + 180) % 360 - 180) / 360.98564736629
        jd += dj
        if abs(dj) < 1e-7:
            break
    return jd


def time_for_altitude(noon_jd, lat, lon, alt, after_noon):
    """Instant (UT JD) when the Sun's centre reaches geometric altitude `alt`, iterated to < 0.01 s.
    None if the Sun never reaches that altitude on this day."""
    jd = noon_jd + (0.25 if after_noon else -0.25)
    for _ in range(10):
        ra, dec = _sun(jd)
        c = (sin(R(alt)) - sin(R(lat)) * sin(R(dec))) / (cos(R(lat)) * cos(R(dec)))
        if abs(c) > 1:
            return None
        h0 = D(acos(c)) * (1 if after_noon else -1)
        h = (A.gmst(jd) + lon - ra + 180) % 360 - 180
        dj = ((h0 - h + 180) % 360 - 180) / 360.98564736629
        jd += dj
        if abs(dj) < 1e-7:
            break
    return jd


def asr_altitude(lat, dec, k):
    """Sun's altitude when an object's shadow equals k x its height + the noon shadow."""
    return D(atan(1 / (k + tan(abs(R(lat - dec))))))


def astronomy(d, place, fajr_angle=18.0, red_angle=15.0, white_angle=18.0, jafari_maghrib_angle=4.0):
    """Every astronomical boundary for civil date d at place, as UT Julian days."""
    j0 = A.jd_from_dt(datetime.combine(d, time(0), place.zone))
    j1 = A.jd_from_dt(datetime.combine(d + timedelta(days=1), time(0), place.zone))
    noon, noon1 = transit(j0, place.lon), transit(j1, place.lon)
    dec = A.position(noon, 'sun')['dec']
    f = lambda alt, pm, base=noon: time_for_altitude(base, place.lat, place.lon, alt, pm)
    return dict(
        fajr=f(-fajr_angle, False), sunrise=f(A.SUN_H0, False), transit=noon,
        asr1=f(asr_altitude(place.lat, dec, 1), True), asr2=f(asr_altitude(place.lat, dec, 2), True),
        sunset=f(A.SUN_H0, True), jafari_maghrib=f(-jafari_maghrib_angle, True),
        red=f(-red_angle, True), white=f(-white_angle, True), fajr_next=f(-fajr_angle, False, noon1))


def boundaries(d, place, fajr_angle=18.0, red_angle=15.0, white_angle=18.0, ishraq_min=15, zawal_min=5,
               isfirar_min=20):
    """All clock boundaries of the day as aware local datetimes, rounded to the second."""
    a = astronomy(d, place, fajr_angle, red_angle, white_angle)
    if any(v is None for v in a.values()):
        raise ValueError('The Sun does not reach a required angle at this latitude and date; '
                         'a high-latitude rule is needed.')
    z = place.zone

    def T(j):
        t = A.dt_from_jd(j).astimezone(z)
        return (t + timedelta(microseconds=500000)).replace(microsecond=0)

    m = lambda x: timedelta(minutes=x)
    b = {k: T(v) for k, v in a.items()}
    night = b['fajr_next'] - b['sunset']
    b['ishraq'] = b['sunrise'] + m(ishraq_min)
    b['zawal_start'] = b['transit'] - m(zawal_min)
    b['yellowing'] = b['sunset'] - m(isfirar_min)
    b['third'] = b['sunset'] + night / 3
    b['midnight'] = b['sunset'] + night / 2
    b['last_third'] = b['sunset'] + night * 2 / 3
    return b


def day(d, place, school='hanafi', fajr_angle=None, **kw):
    """Ordered timeline for one school: list of (name, start, end, status, note).
    status is 'prayer', 'preferred', 'forbidden', 'disliked' or 'info'."""
    if school not in SCHOOLS:
        raise KeyError(school)
    if fajr_angle is None:
        fajr_angle = 16.0 if school == 'jafari' else 18.0
    b = boundaries(d, place, fajr_angle, **kw)
    out = []
    add = lambda *x: out.append(x)
    add('Fajr', b['fajr'], b['sunrise'], 'prayer', 'true dawn until sunrise')
    if school == 'jafari':
        add('Sunrise', b['sunrise'], b['ishraq'], 'disliked', 'starting a voluntary prayer is disliked')
        add('Morning', b['ishraq'], b['zawal_start'], 'info', 'voluntary prayers')
        add('Zenith', b['zawal_start'], b['transit'], 'disliked', 'starting a voluntary prayer is disliked (except Friday)')
        add('Dhuhr & Asr (shared time)', b['transit'], b['sunset'], 'prayer',
            "Dhuhr first; the last 4 rak'ahs' time before sunset belongs to Asr alone")
        add('Asr – recommended start', b['asr1'], b['asr2'], 'preferred', 'from one shadow length (fadila time)')
        add('Sunset', b['yellowing'], b['sunset'], 'disliked', 'starting a voluntary prayer is disliked')
        add('Maghrib & Isha (shared time)', b['jafari_maghrib'], b['midnight'], 'prayer',
            'from disappearance of the eastern redness until Islamic midnight')
        add('Isha – recommended start', b['red'], b['third'], 'preferred', 'after the western red twilight')
        add('Islamic midnight', b['midnight'], b['midnight'], 'info', 'midpoint between sunset and dawn')
        add('Night prayer (salat al-layl)', b['last_third'], b['fajr_next'], 'info', 'best in the last third')
        return out
    add('Sunrise (prohibited)', b['sunrise'], b['ishraq'], 'forbidden', "until the Sun is a spear's height")
    add('Duha / Ishraq', b['ishraq'], b['zawal_start'], 'info', 'voluntary morning prayer')
    if school == 'maliki':
        add('Zenith', b['zawal_start'], b['transit'], 'info', 'not a prohibited time in the Maliki school')
    elif school == 'shafii':
        add('Zenith (prohibited)', b['zawal_start'], b['transit'], 'forbidden', 'except on Friday')
    else:
        add('Zenith (prohibited)', b['zawal_start'], b['transit'], 'forbidden', 'until the Sun begins to decline')
    asr = b['asr2'] if school == 'hanafi' else b['asr1']
    add('Dhuhr', b['transit'], asr, 'prayer',
        'until two shadow lengths (Abu Hanifa)' if school == 'hanafi' else 'until one shadow length')
    add('Asr', asr, b['sunset'], 'prayer', 'valid until sunset')
    if school == 'shafii':
        add('Asr – preferred', b['asr1'], b['asr2'], 'preferred', 'until the shadow is twice the object')
    else:
        add('Asr – preferred', asr, b['yellowing'], 'preferred', 'before the Sun yellows')
    add('Sun yellowing (prohibited)', b['yellowing'], b['sunset'], 'forbidden',
        "only that day's Asr may be prayed; delaying to it is disliked" if school == 'hanafi'
        else 'no voluntary prayer; delaying Asr to it is disliked')
    mag_end = b['white'] if school == 'hanafi' else b['red']
    add('Maghrib', b['sunset'], mag_end, 'prayer',
        'until the white twilight disappears (Abu Hanifa)' if school == 'hanafi' else 'until the red twilight disappears')
    if school == 'maliki':
        add('Maghrib – preferred', b['sunset'], b['sunset'] + timedelta(minutes=15), 'preferred',
            'pray promptly: narrow chosen time')
    add('Isha', mag_end, b['fajr_next'], 'prayer', 'valid until true dawn')
    if school == 'hanafi':
        add('Isha – preferred', mag_end, b['third'], 'preferred',
            'recommended before one third of the night; permissible to midnight; disliked after')
    elif school == 'hanbali':
        add('Isha – preferred', mag_end, b['third'], 'preferred',
            'chosen time until one third of the night (another narration: the middle)')
    else:
        add('Isha – preferred', mag_end, b['third'], 'preferred', 'chosen time until one third of the night')
    add('Middle of the night', b['midnight'], b['midnight'], 'info', 'midpoint between sunset and dawn')
    add('Tahajjud (last third)', b['last_third'], b['fajr_next'], 'info', 'best time for night prayer')
    return out
