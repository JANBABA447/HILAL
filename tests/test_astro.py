import re, os
from datetime import datetime, timezone
from hilal import astro as A

HERE = os.path.dirname(__file__)
MON = {m: i + 1 for i, m in enumerate('Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec'.split())}

def load_nasa():
    """Parse NASA/GSFC phase table -> {'new': [datetime], 'full': [datetime]}"""
    out = {'new': [], 'full': []}; year = None
    for line in open(os.path.join(HERE, 'data', 'nasa_phases.txt')):
        if line.startswith('#') or not line.strip(): continue
        if line[:4].isdigit(): year = int(line[:4])
        for key, (a, b) in (('new', (7, 20)), ('full', (43, 56))):
            s = line[a:b].strip()
            m = re.match(r'([A-Z][a-z]{2})\s+(\d+)\s+(\d\d):(\d\d)', s)
            if m:
                out[key].append(datetime(year, MON[m[1]], int(m[2]), int(m[3]), int(m[4]), tzinfo=timezone.utc))
    return out

def test_meeus_example_47a():
    lam, beta, dist, eps = A.moon_ecliptic(2448724.5)
    assert abs(lam - 133.167265) < 0.0002 and abs(beta + 3.229126) < 0.0001 and abs(dist - 368409.7) < 0.5

def test_meeus_example_49a():
    assert abs(A._phase_jde(-283, A._NEW) - 2443192.65118) < 1e-5

def test_against_nasa_catalog():
    nasa = load_nasa(); worst = 0
    for key, fn in (('new', A.new_moon), ('full', A.full_moon)):
        for t in nasa[key]:
            jd = A.jd_from_dt(t); k = A.k_near(jd)
            calc = min((fn(kk) for kk in (k - 1, k, k + 1)), key=lambda x: abs(x - jd))
            worst = max(worst, abs(calc - jd) * 1440)
    assert len(nasa['new']) > 100 and worst <= 1.6, worst   # NASA rounds to the minute
