"""Sun and Moon positions, phases, rise/set.

Algorithms: Jean Meeus, *Astronomical Algorithms*, 2nd ed. (1998)
  ch.12 sidereal time, ch.13 coordinates, ch.22 nutation (low precision),
  ch.25 Sun (low precision, ~0.01 deg), ch.47 Moon (ELP-2000/82 truncated, ~10"),
  ch.49 phases (same algorithm NASA/GSFC uses for its moon-phase catalog).
Delta-T: Espenak & Meeus polynomials (NASA eclipse web site).
All angles in degrees, times as Julian Day (UT) unless stated.
"""
from math import sin, cos, tan, asin, acos, atan2, radians as R, degrees as D, floor
from datetime import datetime, timedelta, timezone

UTC = timezone.utc

# ----------------------------------------------------------------- time
def jd_from_dt(dt):
    """Julian Day (UT) from an aware datetime."""
    return 2440587.5 + dt.astimezone(UTC).timestamp() / 86400.0

def dt_from_jd(jd):
    return datetime(1970, 1, 1, tzinfo=UTC) + timedelta(days=jd - 2440587.5)

def delta_t_seconds(year):
    """TT - UT in seconds (Espenak & Meeus 2006 polynomials)."""
    y = year
    if 2005 <= y < 2050:
        t = y - 2000
        return 62.92 + 0.32217 * t + 0.005589 * t * t
    if 2050 <= y < 2150:
        return -20 + 32 * ((y - 1820) / 100) ** 2 - 0.5628 * (2150 - y)
    if 1986 <= y < 2005:
        t = y - 2000
        return 63.86 + 0.3345 * t - 0.060374 * t**2 + 0.0017275 * t**3 + 0.000651814 * t**4 + 0.00002373599 * t**5
    u = (y - 1820) / 100
    return -20 + 32 * u * u

def year_of_jd(jd):
    return 2000 + (jd - 2451545.0) / 365.25

def tt(jd_ut):
    return jd_ut + delta_t_seconds(year_of_jd(jd_ut)) / 86400.0

# ----------------------------------------------------------------- ch.49 phases
_NEW = [(-0.40720,(0,1,0,0),0),(0.17241,(1,0,0,0),1),(0.01608,(0,2,0,0),0),(0.01039,(0,0,2,0),0),(0.00739,(-1,1,0,0),1),
        (-0.00514,(1,1,0,0),1),(0.00208,(2,0,0,0),2),(-0.00111,(0,1,-2,0),0),(-0.00057,(0,1,2,0),0),(0.00056,(1,2,0,0),1),
        (-0.00042,(0,3,0,0),0),(0.00042,(1,0,2,0),1),(0.00038,(1,0,-2,0),1),(-0.00024,(-1,2,0,0),1),(-0.00017,(0,0,0,1),0),
        (-0.00007,(2,1,0,0),0),(0.00004,(0,2,-2,0),0),(0.00004,(3,0,0,0),0),(0.00003,(1,1,-2,0),0),(0.00003,(0,2,2,0),0),
        (-0.00003,(1,1,2,0),0),(0.00003,(-1,1,2,0),0),(-0.00002,(-1,1,-2,0),0),(-0.00002,(1,3,0,0),0),(0.00002,(0,4,0,0),0)]
_FULL = [(-0.40614,(0,1,0,0),0),(0.17302,(1,0,0,0),1),(0.01614,(0,2,0,0),0),(0.01043,(0,0,2,0),0),(0.00734,(-1,1,0,0),1),
         (-0.00515,(1,1,0,0),1),(0.00209,(2,0,0,0),2),(-0.00111,(0,1,-2,0),0),(-0.00057,(0,1,2,0),0),(0.00056,(1,2,0,0),1),
         (-0.00042,(0,3,0,0),0),(0.00042,(1,0,2,0),1),(0.00038,(1,0,-2,0),1),(-0.00024,(-1,2,0,0),1),(-0.00017,(0,0,0,1),0),
         (-0.00007,(2,1,0,0),0),(0.00004,(0,2,-2,0),0),(0.00004,(3,0,0,0),0),(0.00003,(1,1,-2,0),0),(0.00003,(0,2,2,0),0),
         (-0.00003,(1,1,2,0),0),(0.00003,(-1,1,2,0),0),(-0.00002,(-1,1,-2,0),0),(-0.00002,(1,3,0,0),0),(0.00002,(0,4,0,0),0)]
_A = [(299.77,0.107408,0.000325),(251.88,0.016321,0.000165),(251.83,26.651886,0.000164),(349.42,36.412478,0.000126),
      (84.66,18.206239,0.000110),(141.74,53.303771,0.000062),(207.14,2.453732,0.000060),(154.84,7.306860,0.000056),
      (34.52,27.261239,0.000047),(207.19,0.121824,0.000042),(291.34,1.844379,0.000040),(161.72,24.198154,0.000037),
      (239.56,25.513099,0.000035),(331.55,3.592518,0.000023)]

def _phase_jde(k, table):
    T = k / 1236.85
    jde = 2451550.09766 + 29.530588861*k + 0.00015437*T**2 - 0.000000150*T**3 + 0.00000000073*T**4
    E = 1 - 0.002516*T - 0.0000074*T**2
    M = R(2.5534 + 29.10535670*k - 0.0000014*T**2 - 0.00000011*T**3)
    Mp = R(201.5643 + 385.81693528*k + 0.0107582*T**2 + 0.00001238*T**3 - 0.000000058*T**4)
    F = R(160.7108 + 390.67050284*k - 0.0016118*T**2 - 0.00000227*T**3 + 0.000000011*T**4)
    O = R(124.7746 - 1.56375588*k + 0.0020672*T**2 + 0.00000215*T**3)
    s = sum(c * E**e * sin(a*M + b*Mp + f*F + o*O) for c, (a, b, f, o), e in table)
    s += sum(c * sin(R(a0 + a1*k - (0.009173*T*T if i == 0 else 0))) for i, (a0, a1, c) in enumerate(_A))
    return jde + s

def new_moon(k):
    """UT Julian Day of new moon number k (k=0: 2000 Jan 6)."""
    jde = _phase_jde(k, _NEW)
    return jde - delta_t_seconds(year_of_jd(jde)) / 86400.0

def full_moon(k):
    jde = _phase_jde(k + 0.5, _FULL)
    return jde - delta_t_seconds(year_of_jd(jde)) / 86400.0

def k_near(jd):
    return round((year_of_jd(jd) - 2000) * 12.3685)

def new_moons_between(jd1, jd2):
    out, k = [], k_near(jd1) - 2
    while True:
        t = new_moon(k); k += 1
        if t > jd2: return out
        if t >= jd1: out.append(t)

def full_moons_between(jd1, jd2):
    out, k = [], k_near(jd1) - 2
    while True:
        t = full_moon(k); k += 1
        if t > jd2: return out
        if t >= jd1: out.append(t)

def previous_new_moon(jd):
    k = k_near(jd) + 1
    while new_moon(k) > jd: k -= 1
    return new_moon(k)

# ----------------------------------------------------------------- ch.47 Moon
_LR = [(0,0,1,0,6288774,-20905355),(2,0,-1,0,1274027,-3699111),(2,0,0,0,658314,-2955968),(0,0,2,0,213618,-569925),
(0,1,0,0,-185116,48888),(0,0,0,2,-114332,-3149),(2,0,-2,0,58793,246158),(2,-1,-1,0,57066,-152138),(2,0,1,0,53322,-170733),
(2,-1,0,0,45758,-204586),(0,1,-1,0,-40923,-129620),(1,0,0,0,-34720,108743),(0,1,1,0,-30383,104755),(2,0,0,-2,15327,10321),
(0,0,1,2,-12528,0),(0,0,1,-2,10980,79661),(4,0,-1,0,10675,-34782),(0,0,3,0,10034,-23210),(4,0,-2,0,8548,-21636),
(2,1,-1,0,-7888,24208),(2,1,0,0,-6766,30824),(1,0,-1,0,-5163,-8379),(1,1,0,0,4987,-16675),(2,-1,1,0,4036,-12831),
(2,0,2,0,3994,-10445),(4,0,0,0,3861,-11650),(2,0,-3,0,3665,14403),(0,1,-2,0,-2689,-7003),(2,0,-1,2,-2602,0),
(2,-1,-2,0,2390,10056),(1,0,1,0,-2348,6322),(2,-2,0,0,2236,-9884),(0,1,2,0,-2120,5751),(0,2,0,0,-2069,0),
(2,-2,-1,0,2048,-4950),(2,0,1,-2,-1773,4130),(2,0,0,2,-1595,0),(4,-1,-1,0,1215,-3958),(0,0,2,2,-1110,0),
(3,0,-1,0,-892,3258),(2,1,1,0,-810,2616),(4,-1,-2,0,759,-1897),(0,2,-1,0,-713,-2117),(2,2,-1,0,-700,2354),
(2,1,-2,0,691,0),(2,-1,0,-2,596,0),(4,0,1,0,549,-1423),(0,0,4,0,537,-1117),(4,-1,0,0,520,-1571),(1,0,-2,0,-487,-1739),
(2,1,0,-2,-399,0),(0,0,2,-2,-381,-4421),(1,1,1,0,351,0),(3,0,-2,0,-340,0),(4,0,-3,0,330,0),(2,-1,2,0,327,0),
(0,2,1,0,-323,1165),(1,1,-1,0,299,0),(2,0,3,0,294,0),(2,0,-1,-2,0,8752)]
_B = [(0,0,0,1,5128122),(0,0,1,1,280602),(0,0,1,-1,277693),(2,0,0,-1,173237),(2,0,-1,1,55413),(2,0,-1,-1,46271),
(2,0,0,1,32573),(0,0,2,1,17198),(2,0,1,-1,9266),(0,0,2,-1,8822),(2,-1,0,-1,8216),(2,0,-2,-1,4324),(2,0,1,1,4200),
(2,1,0,-1,-3359),(2,-1,-1,1,2463),(2,-1,0,1,2211),(2,-1,-1,-1,2065),(0,1,-1,-1,-1870),(4,0,-1,-1,1828),(0,1,0,1,-1794),
(0,0,0,3,-1749),(0,1,-1,1,-1565),(1,0,0,1,-1491),(0,1,1,1,-1475),(0,1,1,-1,-1410),(0,1,0,-1,-1344),(1,0,0,-1,-1335),
(0,0,3,1,1107),(4,0,0,-1,1021),(4,0,-1,1,833),(0,0,1,-3,777),(4,0,-2,1,671),(2,0,0,-3,607),(2,0,2,-1,596),
(2,-1,1,-1,491),(2,0,-2,1,-451),(0,0,3,-1,439),(2,0,2,1,422),(2,0,-3,-1,421),(2,1,-1,1,-366),(2,1,0,1,-351),
(4,0,0,1,331),(2,-1,1,1,315),(2,-2,0,-1,302),(0,0,1,3,-283),(2,1,1,-1,-229),(1,1,0,-1,223),(1,1,0,1,223),
(0,1,-2,-1,-220),(2,1,-1,-1,-220),(1,0,1,1,-185),(2,-1,-2,-1,181),(0,1,2,1,-177),(4,0,-2,-1,176),(4,-1,-1,-1,166),
(1,0,1,-1,-164),(4,0,1,-1,132),(1,0,-1,-1,-119),(4,-1,0,-1,115),(2,-2,0,1,107)]

def nutation(T):
    """(delta-psi, true obliquity) in degrees, Meeus ch.22 low precision (0.5")."""
    O = R(125.04452 - 1934.136261*T); Ls = R(280.4665 + 36000.7698*T); Lm = R(218.3165 + 481267.8813*T)
    dpsi = (-17.20*sin(O) - 1.32*sin(2*Ls) - 0.23*sin(2*Lm) + 0.21*sin(2*O)) / 3600
    deps = (9.20*cos(O) + 0.57*cos(2*Ls) + 0.10*cos(2*Lm) - 0.09*cos(2*O)) / 3600
    eps0 = 23 + 26/60 + 21.448/3600 - (46.8150*T + 0.00059*T**2 - 0.001813*T**3) / 3600
    return dpsi, eps0 + deps

def moon_ecliptic(jde):
    """Apparent geocentric ecliptic longitude, latitude (deg), distance (km), obliquity."""
    T = (jde - 2451545.0) / 36525
    Lp = 218.3164477 + 481267.88123421*T - 0.0015786*T**2 + T**3/538841 - T**4/65194000
    Dd = 297.8501921 + 445267.1114034*T - 0.0018819*T**2 + T**3/545868 - T**4/113065000
    M = 357.5291092 + 35999.0502909*T - 0.0001536*T**2 + T**3/24490000
    Mp = 134.9633964 + 477198.8675055*T + 0.0087414*T**2 + T**3/69699 - T**4/14712000
    F = 93.2720950 + 483202.0175233*T - 0.0036539*T**2 - T**3/3526000 + T**4/863310000
    A1 = R(119.75 + 131.849*T); A2 = R(53.09 + 479264.290*T); A3 = R(313.45 + 481266.484*T)
    E = 1 - 0.002516*T - 0.0000074*T**2
    Dr, Mr, Mpr, Fr, Lr = R(Dd), R(M), R(Mp), R(F), R(Lp)
    sl = sr = sb = 0.0
    for d, m, mp, f, cl, cr in _LR:
        a = d*Dr + m*Mr + mp*Mpr + f*Fr; e = E**abs(m)
        sl += cl*e*sin(a); sr += cr*e*cos(a)
    for d, m, mp, f, cb in _B:
        sb += cb * E**abs(m) * sin(d*Dr + m*Mr + mp*Mpr + f*Fr)
    sl += 3958*sin(A1) + 1962*sin(Lr - Fr) + 318*sin(A2)
    sb += -2235*sin(Lr) + 382*sin(A3) + 175*sin(A1 - Fr) + 175*sin(A1 + Fr) + 127*sin(Lr - Mpr) - 115*sin(Lr + Mpr)
    dpsi, eps = nutation(T)
    return (Lp + sl/1e6 + dpsi) % 360, sb/1e6, 385000.56 + sr/1000, eps

def sun_ecliptic(jde):
    """Apparent geocentric longitude of the Sun (deg), latitude 0, distance (km), obliquity."""
    T = (jde - 2451545.0) / 36525
    L0 = 280.46646 + 36000.76983*T + 0.0003032*T**2
    M = R(357.52911 + 35999.05029*T - 0.0001537*T**2)
    e = 0.016708634 - 0.000042037*T - 0.0000001267*T**2
    C = (1.914602 - 0.004817*T - 0.000014*T**2)*sin(M) + (0.019993 - 0.000101*T)*sin(2*M) + 0.000289*sin(3*M)
    nu = M + R(C)
    rr = 1.000001018*(1 - e*e)/(1 + e*cos(nu))
    O = R(125.04 - 1934.136*T)
    _, eps = nutation(T)
    return (L0 + C - 0.00569 - 0.00478*sin(O)) % 360, 0.0, rr*149597870.7, eps

def ecl_to_eq(lam, beta, eps):
    l, b, e = R(lam), R(beta), R(eps)
    ra = atan2(sin(l)*cos(e) - tan(b)*sin(e), cos(l))
    dec = asin(sin(b)*cos(e) + cos(b)*sin(e)*sin(l))
    return D(ra) % 360, D(dec)

def gmst(jd_ut):
    T = (jd_ut - 2451545.0) / 36525
    return (280.46061837 + 360.98564736629*(jd_ut - 2451545.0) + 0.000387933*T*T - T**3/38710000) % 360

def position(jd_ut, body):
    """Geocentric apparent position: dict(lon, lat, dist_km, ra, dec)."""
    lam, beta, dist, eps = (moon_ecliptic if body == 'moon' else sun_ecliptic)(tt(jd_ut))
    ra, dec = ecl_to_eq(lam, beta, eps)
    return dict(lon=lam, lat=beta, dist=dist, ra=ra, dec=dec)

def horizontal(ra, dec, jd_ut, lat, lon):
    """Geocentric altitude & azimuth (azimuth from north, eastward). lon east positive."""
    H = R(gmst(jd_ut) + lon - ra)
    p, d = R(lat), R(dec)
    alt = asin(sin(p)*sin(d) + cos(p)*cos(d)*cos(H))
    az = atan2(sin(H), cos(H)*sin(p) - tan(d)*cos(p))
    return D(alt), (D(az) + 180) % 360

def altaz(jd_ut, lat, lon, body, topocentric=True):
    """Airless altitude/azimuth of the body's centre; Moon corrected for parallax when topocentric."""
    p = position(jd_ut, body)
    alt, az = horizontal(p['ra'], p['dec'], jd_ut, lat, lon)
    if body == 'moon' and topocentric:
        alt -= D(asin(6378.14 / p['dist'])) * cos(R(alt))
    return alt, az

def elongation(jd_ut):
    m = position(jd_ut, 'moon'); s = position(jd_ut, 'sun')
    return D(acos(cos(R(m['lat'])) * cos(R(m['lon'] - s['lon']))))

def illuminated_fraction(jd_ut):
    m = position(jd_ut, 'moon'); s = position(jd_ut, 'sun')
    psi = R(elongation(jd_ut))
    i = atan2(s['dist'] * sin(psi), m['dist'] - s['dist'] * cos(psi))
    return (1 + cos(i)) / 2

# ----------------------------------------------------------------- rise / set
SUN_H0 = -0.8333          # refraction 34' + semi-diameter 16'
def moon_h0(dist_km):     # Meeus ch.15: 0.7275*parallax - 34'  (geocentric altitude of centre)
    return 0.7275 * D(asin(6378.14 / dist_km)) - 0.5667

def _event(jd_guess, lat, lon, body, rising):
    """Iterate the hour-angle method to the rise/set nearest jd_guess. Returns JD or None."""
    jd = jd_guess
    for _ in range(6):
        p = position(jd, body)
        h0 = SUN_H0 if body == 'sun' else moon_h0(p['dist'])
        c = (sin(R(h0)) - sin(R(lat))*sin(R(p['dec']))) / (cos(R(lat))*cos(R(p['dec'])))
        if abs(c) > 1: return None
        H0 = D(acos(c)) * (-1 if rising else 1)
        H = (gmst(jd) + lon - p['ra'] + 180) % 360 - 180
        rate = 360.98564736629 - (0 if body == 'sun' else 13.176)   # moon moves east ~13.2 deg/day
        dj = ((H0 - H + 180) % 360 - 180) / rate
        jd += dj
        if abs(dj) < 1e-6: break
    return jd

def rise_set(jd_day_start, lat, lon, body):
    """Rise and set (UT JD) inside the 24-h window that starts at jd_day_start (local midnight in UT).
    Either value may be None (Moon: no rise or no set that day)."""
    out = {}
    for rising in (True, False):
        found = None
        for g in (0.25, 0.5, 0.75, 0.0, 1.0):
            t = _event(jd_day_start + g, lat, lon, body, rising)
            if t is not None and jd_day_start <= t < jd_day_start + 1:
                found = t; break
        out['rise' if rising else 'set'] = found
    return out['rise'], out['set']

def sunset(jd_day_start, lat, lon):
    return rise_set(jd_day_start, lat, lon, 'sun')[1]

def sunrise(jd_day_start, lat, lon):
    return rise_set(jd_day_start, lat, lon, 'sun')[0]

def moonset_after(jd, lat, lon):
    """First moonset after jd (within 1 day)."""
    for g in (0.05, 0.15, 0.3, 0.5, 0.7):
        t = _event(jd + g, lat, lon, 'moon', False)
        if t is not None and jd - 1e-4 < t < jd + 1.0:
            # make sure there is no earlier set between jd and t
            return t
    return None
