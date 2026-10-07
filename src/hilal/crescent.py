"""Evening circumstances of the young crescent and visibility criteria.

Criteria implemented
  * Odeh (2004), Experimental Astronomy 18:39-64  -> V and zones A/B/C/D
  * Yallop (1997), NAO Technical Note 69          -> q and zones A..F
  * Danjon limit (~7 deg elongation)               -> crescent physically impossible below
  * Umm al-Qura rule (Saudi Arabia, since 1423 AH) -> conjunction before sunset AND moonset after sunset at Makkah
  * FCNA / ECFR global rule                        -> somewhere on Earth at sunset: elongation >= 8, altitude >= 5
"""
from math import sin, cos, asin, acos, radians as R, degrees as D
from datetime import date, datetime, time, timedelta
from . import astro as A

ODEH_ZONES = [(5.65, 'A', 'visible to the naked eye'), (2.0, 'B', 'visible with optical aid, may be seen by naked eye'),
              (-0.96, 'C', 'visible with optical aid only'), (-1e9, 'D', 'not visible even with optical aid')]
YALLOP_ZONES = [(0.216, 'A', 'easily visible'), (-0.014, 'B', 'visible under perfect conditions'),
                (-0.160, 'C', 'may need optical aid'), (-0.232, 'D', 'optical aid needed'),
                (-0.293, 'E', 'not visible with a telescope'), (-1e9, 'F', 'below the Danjon limit')]

def odeh_zone(V):
    return next(z for z in ODEH_ZONES if V >= z[0])[1]

def yallop_zone(q):
    return next(z for z in YALLOP_ZONES if q > z[0])[1]

def local_midnight_jd(d, place):
    return A.jd_from_dt(datetime.combine(d, time(0), place.zone))

def evening(d, place, conj_jd=None):
    """Circumstances at local sunset of civil date d. Returns a dict (all angles deg, times UT JD)."""
    j0 = local_midnight_jd(d, place)
    ss = A.sunset(j0, place.lat, place.lon)
    if conj_jd is None:
        conj_jd = A.previous_new_moon(ss + 0.5)
        if conj_jd > ss:   # the relevant conjunction may be later this day / tomorrow
            pass
    age_h = (ss - conj_jd) * 24
    m_alt, m_az = A.altaz(ss, place.lat, place.lon, 'moon')
    s_alt, s_az = A.altaz(ss, place.lat, place.lon, 'sun')
    elong = A.elongation(ss)
    p = A.position(ss, 'moon')
    g_alt, _ = A.horizontal(p['ra'], p['dec'], ss, place.lat, place.lon)
    above = g_alt > A.moon_h0(p['dist'])
    ms = A._event(ss + (0.04 if above else -0.04), place.lat, place.lon, 'moon', False)
    if ms is not None and (ms > ss) != above:   # converged to the wrong side; retry
        ms = A._event(ss + (0.12 if above else -0.12), place.lat, place.lon, 'moon', False)
    lag = (ms - ss) * 1440 if ms is not None else None
    out = dict(date=d, place=place.key, sunset=ss, moonset=ms, lag_min=lag, conj=conj_jd, age_h=age_h,
               alt=m_alt, elong=elong, illum=A.illuminated_fraction(ss) * 100,
               conj_before_sunset=conj_jd < ss, moonset_after_sunset=above)
    # best time (Yallop / Odeh): sunset + 4/9 lag
    if lag is not None and lag > 0:
        tb = ss + (ms - ss) * 4 / 9
        hm, azm = A.altaz(tb, place.lat, place.lon, 'moon')            # topocentric, airless
        hmg, _ = A.altaz(tb, place.lat, place.lon, 'moon', topocentric=False)
        hs, azs = A.altaz(tb, place.lat, place.lon, 'sun')
        daz = azs - azm
        arcl_t = D(acos(max(-1, min(1, sin(R(hm))*sin(R(hs)) + cos(R(hm))*cos(R(hs))*cos(R(daz))))))
        dist = A.position(tb, 'moon')['dist']
        hp = D(asin(6378.14 / dist)) * 60                                # arcmin
        sd = 0.27245 * hp * (1 + sin(R(hm)) * sin(R(hp / 60)))           # topocentric semi-diameter, arcmin
        W = sd * (1 - cos(R(arcl_t)))
        poly = lambda w: -0.1018*w**3 + 0.7319*w**2 - 6.3226*w
        V = (hm - hs) - (poly(W) + 7.1651)
        q = ((hmg - hs) - (poly(W) + 11.8371)) / 10
        out.update(best=tb, arcv=hm - hs, daz=daz, arcl=arcl_t, W=W, V=V, q=q)
    else:
        out.update(best=None, arcv=None, daz=None, arcl=None, W=0.0, V=-99.0, q=-9.9)
    if not out['conj_before_sunset']:
        out['V'], out['q'] = -99.0, -9.9
    out['odeh'] = odeh_zone(out['V']); out['yallop'] = yallop_zone(out['q'])
    out['danjon'] = elong >= 7.0
    return out

def naked_eye(ev):
    """Crescent expected visible to the naked eye (Odeh zone A)."""
    return ev['V'] >= 5.65

def ummalqura_condition(d, conj_jd=None):
    from .places import MAKKAH
    ev = evening(d, MAKKAH, conj_jd)
    return ev['conj_before_sunset'] and ev['moonset_after_sunset'], ev

def fcna_condition(d, conj_jd, lat_step=2, lon_step=2):
    """FCNA/ECFR: somewhere on the globe, at local sunset of date d, elongation >= 8 and moon altitude >= 5."""
    from zoneinfo import ZoneInfo
    for lon in range(-180, 180, lon_step):
        for lat in range(-60, 61, lat_step):
            # local civil date d at this longitude: start at UT midnight shifted by longitude
            j0 = A.jd_from_dt(datetime.combine(d, time(0), ZoneInfo('UTC'))) - lon / 360.0
            ss = A.sunset(j0, lat, lon)
            if ss is None or ss <= conj_jd: continue
            if A.elongation(ss) < 8: continue
            alt, _ = A.altaz(ss, lat, lon, 'moon')
            if alt >= 5: return True, (lat, lon)
    return False, None
