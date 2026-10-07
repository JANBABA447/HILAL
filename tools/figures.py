"""Figures for ISL-CAL-011 / 012 (matplotlib -> SVG files)."""
import sys, os, json, math
from datetime import date, datetime, timedelta, timezone
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Wedge, Polygon, FancyArrowPatch, Arc, Rectangle
from hilal import astro as A, crescent as C
from hilal.places import MAKKAH, PESHAWAR, DALLAS
OUT = sys.argv[1]
BUILD = os.environ.get('HILAL_BUILD', 'build')
G, M, GOLD, NAVY, GREY = '#1E5B3C', '#7A2E36', '#B8862B', '#1F3F66', '#777777'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.edgecolor': '#999', 'axes.titleweight': 'bold'})
def save(fig, name):
    fig.savefig(os.path.join(OUT, name + '.svg'), bbox_inches='tight', transparent=True); plt.close(fig)

# F1 geometry & phases ------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.2, 3.3)); ax.set_aspect('equal'); ax.axis('off')
ax.add_patch(Circle((-7.0, 0), 0.9, color='#F2C14E')); ax.text(-7.0, -1.35, 'Sun\n(light comes\nfrom this side)', ha='center', va='top', fontsize=8)
for y in (-0.6, 0.6): ax.annotate('', xy=(-5.3, y), xytext=(-6.0, y), arrowprops=dict(arrowstyle='->', color='#E0A800'))
ax.add_patch(Circle((0, 0), 0.55, color='#3D7EA6')); ax.text(0, 0, 'Earth', ha='center', va='center', color='white', fontsize=7.5, weight='bold')
ax.add_patch(Circle((0, 0), 2.6, fill=False, ls='--', color='#aaa'))
labels = ['New moon\n(conjunction)\ninvisible', 'Waxing\ncrescent', 'First\nquarter', 'Waxing\ngibbous', 'Full moon', 'Waning\ngibbous', 'Last\nquarter', 'Waning\ncrescent']
for i in range(8):
    a = math.pi - i * math.pi / 4   # 0: toward the sun (left)
    x, y = 2.6 * math.cos(a), -2.6 * math.sin(a)
    ax.add_patch(Circle((x, y), 0.32, color='#333'))
    ax.add_patch(Wedge((x, y), 0.32, 90, 270, color='#EEE'))   # sunlit half faces left (the Sun)
    ax.add_patch(Circle((x, y), 0.32, fill=False, color='#555', lw=0.6))
    tx, ty = 3.75 * math.cos(a), -3.75 * math.sin(a)
    if i == 0: tx -= 0.35
    ax.text(tx, ty, labels[i], ha='center', va='center', fontsize=6.6, color=M if i == 0 else '#222')
ax.annotate('', xy=(-1.0, -2.75), xytext=(-2.35, -1.7), arrowprops=dict(arrowstyle='->', color=G, lw=1.2))
ax.text(2.2, -3.75, 'Moon moves ~12.2° per day relative to the Sun\n(anticlockwise, seen from above the North Pole)', fontsize=7, color=G)
ax.text(5.0, 0, 'One full cycle\n(new moon to new moon)\n= 29.53 days on average\n(29.27 – 29.82 d,\n2001–2100)', fontsize=7.5, va='center', color=NAVY)
ax.set_xlim(-8.1, 8.2); ax.set_ylim(-4.4, 4.3)
save(fig, 'f1_phases')

# F2 timeline ----------------------------------------------------------------
fig, ax = plt.subplots(figsize=(7.4, 1.9)); ax.axis('off')
ax.plot([0, 29.53], [0, 0], color='#444', lw=1.5)
marks = [(0, 'New moon\n(conjunction)', M), (0.6, '', None), (1.0, '', None), (7.38, 'First quarter', '#444'), (14.77, 'Full moon', GOLD),
         (22.15, 'Last quarter', '#444'), (29.53, 'Next new moon', M)]
for x, t, c in marks:
    if t: ax.plot([x, x], [-0.15, 0.15], color=c, lw=2); ax.text(x, -0.3, t, ha='center', va='top', fontsize=7.5, color=c)
ax.axvspan(0, 0.55, ymin=0.45, ymax=0.55, color='#ddd')
ax.add_patch(Rectangle((0.6, 0.12), 1.4, 0.22, color=G, alpha=0.85))
ax.text(1.3, 0.48, 'First evening the crescent\ncan be seen: usually 0.6 – 2 days\nafter conjunction', ha='left', va='bottom', fontsize=7.5, color=G)
ax.text(0.2, 0.12, 'invisible', fontsize=6.5, color='#888', rotation=90, va='bottom')
ax.set_xlim(-1, 31); ax.set_ylim(-1.2, 1.3)
ax.text(29.53 / 2, -0.85, 'days after conjunction  (each Islamic month must contain 29 or 30 whole days)', ha='center', fontsize=7.5, color='#555')
save(fig, 'f2_timeline')

# F3 sunset geometry ------------------------------------------------------------
fig, ax = plt.subplots(figsize=(4.6, 3.0)); ax.set_aspect('equal'); ax.axis('off')
ax.fill_between([-1, 11], -2, 0, color='#C9B79C'); ax.plot([-1, 11], [0, 0], color='#7a6a52')
ax.text(10.8, -0.5, 'horizon (west)', ha='right', fontsize=7.5)
ax.add_patch(Circle((7.5, -0.35), 0.38, color='#F2C14E')); ax.text(9.2, -1.0, 'Sun just set', ha='center', fontsize=7.5)
mx, my = 4.6, 3.4
ax.add_patch(Circle((mx, my), 0.42, color='#2b2b2b')); ax.add_patch(Wedge((mx, my), 0.42, -60, 60, width=0.12, color='#F5F0DC'))
ax.text(mx - 0.6, my + 0.55, 'young crescent\n(lit edge faces the Sun)', ha='center', fontsize=7.2)
ax.annotate('', xy=(mx, my - 0.45), xytext=(mx, 0.02), arrowprops=dict(arrowstyle='<->', color=G))
ax.text(mx - 0.15, 1.5, 'altitude\n(height above\nhorizon)', ha='right', fontsize=7, color=G)
ax.add_patch(FancyArrowPatch((7.45, 0.1), (mx + 0.35, my - 0.2), connectionstyle='arc3,rad=-0.25', arrowstyle='<->', color=M, lw=1))
ax.text(7.2, 2.3, 'elongation\n(Sun–Moon angle;\nbelow ~7° no crescent\ncan form: Danjon limit)', fontsize=7, color=M)
ax.annotate('', xy=(mx, -0.15), xytext=(7.5, -0.15), arrowprops=dict(arrowstyle='<->', color=NAVY))
ax.text(6.0, -0.75, 'azimuth\ndifference', ha='center', fontsize=6.3, color=NAVY)
ax.text(-0.8, -1.45, 'Lag time = minutes the Moon stays above the horizon after sunset', fontsize=6.8, color='#333')
ax.set_xlim(-1, 11); ax.set_ylim(-1.6, 5.4)
save(fig, 'f3_geometry')

# F4 world visibility map -------------------------------------------------------
LAND = {
 'NA': [(-166,68),(-156,71),(-140,70),(-125,70),(-95,72),(-80,73),(-65,62),(-55,52),(-66,45),(-70,42),(-76,35),(-81,31),(-80,25),(-83,29),(-90,30),(-97,26),(-97,21),(-90,21),(-87,15),(-83,10),(-79,8),(-86,12),(-92,14),(-105,20),(-112,29),(-117,32),(-124,40),(-124,48),(-133,56),(-150,60),(-165,60)],
 'SA': [(-79,8),(-75,11),(-62,10),(-50,1),(-35,-6),(-39,-14),(-48,-27),(-58,-35),(-65,-42),(-68,-52),(-74,-52),(-73,-40),(-71,-18),(-81,-5),(-78,2)],
 'AF': [(-17,21),(-5,36),(10,37),(25,32),(33,31),(43,12),(51,12),(40,-15),(35,-25),(20,-35),(15,-28),(12,-6),(9,4),(-8,4),(-17,14)],
 'EU': [(-10,36),(-9,43),(-2,44),(-5,48),(5,53),(8,57),(5,62),(15,69),(28,71),(42,67),(60,69),(80,73),(105,78),(140,72),(180,68),(180,65),(160,60),(143,52),(140,46),(130,42),(122,40),(122,30),(110,20),(108,11),(100,13),(98,8),(103,2),(98,16),(94,16),(90,22),(80,15),(77,8),(72,20),(67,24),(57,25),(56,27),(50,30),(48,29),(56,24),(59,22),(52,16),(43,13),(39,21),(35,28),(34,31),(35,36),(28,37),(26,40),(23,36),(20,40),(13,45),(15,40),(12,38),(8,44),(3,43),(0,39),(-6,36)],
 'AU': [(114,-22),(122,-17),(130,-12),(137,-12),(142,-11),(146,-19),(153,-25),(151,-34),(144,-38),(138,-35),(131,-31),(115,-34)],
 'GL': [(-73,78),(-60,82),(-30,83),(-20,75),(-42,60),(-50,64),(-55,70)],
 'UK': [(-6,50),(1,51),(-2,57),(-5,58),(-5,54)],
}
class Pt:
    def __init__(self, lat, lon):
        self.lat, self.lon, self.key = lat, lon, f'{lat},{lon}'
        self.zone = timezone(timedelta(hours=round(lon / 15)))
def vis_grid(d, step=3):
    cj = A.new_moons_between(A.jd_from_dt(datetime.combine(d - timedelta(days=3), datetime.min.time(), timezone.utc)),
                             A.jd_from_dt(datetime.combine(d + timedelta(days=1), datetime.min.time(), timezone.utc)))[-1]
    pts = []
    for lat in range(-57, 61, step):
        for lon in range(-180, 180, step):
            try: V = C.evening(d, Pt(lat, lon), cj)['V']
            except Exception: V = -99
            pts.append((lon, lat, V))
    return pts
def draw_map(ax, pts, title):
    cols = {'A': '#2E8B57', 'B': '#9ACD8A', 'C': '#F3D27A'}
    for lon, lat, V in pts:
        z = C.odeh_zone(V)
        if z in cols: ax.add_patch(Rectangle((lon - 1.5, lat - 1.5), 3, 3, color=cols[z], lw=0))
    for poly in LAND.values(): ax.add_patch(Polygon(poly, closed=True, fill=False, ec='#555', lw=0.6))
    for p, c in ((DALLAS, NAVY), (MAKKAH, G), (PESHAWAR, M)):
        ax.plot(p.lon, p.lat, 'o', color=c, ms=4.5, mec='white', mew=0.8); ax.text(p.lon + 3, p.lat + 2, p.name.split(' (')[0].split(',')[0], fontsize=7, color=c, weight='bold')
    ax.set_xlim(-180, 180); ax.set_ylim(-58, 62); ax.set_xticks(range(-180, 181, 60)); ax.set_yticks([-40, -20, 0, 20, 40, 60])
    ax.tick_params(labelsize=6.5); ax.grid(color='#ddd', lw=0.4); ax.set_title(title, fontsize=8.5)
fig, axs = plt.subplots(1, 2, figsize=(7.6, 2.5))
d1, d2 = date(2027, 2, 6), date(2027, 2, 7)
draw_map(axs[0], vis_grid(d1), 'Evening of Sat 6 Feb 2027 (conjunction 15:56 UT)')
draw_map(axs[1], vis_grid(d2), 'Evening of Sun 7 Feb 2027')
from matplotlib.patches import Patch
fig.legend(handles=[Patch(color='#2E8B57', label='A: visible to the naked eye'), Patch(color='#9ACD8A', label='B: optical aid; naked eye only in perfect sky'),
                    Patch(color='#F3D27A', label='C: optical aid only')], loc='lower center', ncol=3, fontsize=7, frameon=False, bbox_to_anchor=(0.5, -0.08))
save(fig, 'f4_worldmap')

# F5 west sees first ------------------------------------------------------------
fig, axs = plt.subplots(1, 2, figsize=(7.4, 2.3))
for ax, d in zip(axs, (d1, d2)):
    vals = []
    for p in (PESHAWAR, MAKKAH, DALLAS):
        cj = A.previous_new_moon(C.local_midnight_jd(d, p) + 1)
        e = C.evening(d, p, cj); vals.append((p, e))
    names = ['Peshawar', 'Makkah', 'Dallas']; cols = [M, G, NAVY]
    ages = [max(0, e['age_h']) for _, e in vals]; alts = [e['alt'] for _, e in vals]
    b = ax.bar(names, ages, color=cols, width=0.55)
    for i, (p, e) in enumerate(vals):
        ss = A.dt_from_jd(e['sunset'])
        ax.text(i, ages[i] + 0.8, f"age {e['age_h']:.0f} h\nalt {e['alt']:.1f}°\nzone {e['odeh']}", ha='center', fontsize=6.8)
        ax.text(i, -3.2, f"sunset {ss:%H:%M} UT", ha='center', fontsize=6.3, color='#555')
    ax.set_ylim(-4.5, max(ages) + 9); ax.set_ylabel('Moon age at sunset (hours)', fontsize=7); ax.axhline(0, color='#999', lw=0.6)
    ax.set_title(f'Evening of {d:%a %d %b %Y}', fontsize=8)
    ax.tick_params(labelsize=7)
save(fig, 'f5_westfirst')

# F6 synodic month length ---------------------------------------------------------
st = json.load(open(os.path.join(BUILD, 'stats.json')))
xs = [datetime.fromisoformat(d) for d, s in st['syn_2026_2030']]; ys = [s for d, s in st['syn_2026_2030']]
fig, ax = plt.subplots(figsize=(7.2, 2.1))
ax.plot(xs, ys, '-o', color=G, ms=2.5, lw=1); ax.axhline(29.530589, color=M, ls='--', lw=0.8)
ax.text(xs[2], 29.535, 'mean 29.5306 d = 29 d 12 h 44 min', color=M, fontsize=7, va='bottom')
ax.axhline(29.5, color='#bbb', lw=0.6); ax.set_ylabel('days', fontsize=7.5); ax.tick_params(labelsize=7)
ax.set_title('Length of each lunation (new moon to new moon), 2026–2030', fontsize=8.5)
save(fig, 'f6_synodic')

# F7 month lengths -----------------------------------------------------------------
fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.2))
mk = st['makkah']
axs[0].bar(['29-day months', '30-day months'], [mk['c29'], mk['c30']], color=[NAVY, G], width=0.5)
for i, v in enumerate([mk['c29'], mk['c30']]): axs[0].text(i, v + 10, f"{v}  ({v / mk['n'] * 100:.0f}%)", ha='center', fontsize=7.5)
axs[0].set_ylim(0, 760); axs[0].set_title('Month lengths, Makkah naked-eye\ncalendar 2002–2100 (1,222 months)', fontsize=8); axs[0].tick_params(labelsize=7)
vs = mk['vs_uq']; keys = sorted(int(k) for k in vs)
axs[1].bar([f'{k:+d} day' if k else 'same day' for k in keys], [vs[str(k)] for k in keys], color=[G, GOLD, M][:len(keys)], width=0.5)
for i, k in enumerate(keys): axs[1].text(i, vs[str(k)] + 10, f"{vs[str(k)] / sum(vs.values()) * 100:.0f}%", ha='center', fontsize=7.5)
axs[1].set_title('Makkah naked-eye start\ncompared with Umm al-Qura', fontsize=8); axs[1].tick_params(labelsize=7); axs[1].set_ylim(0, 1200)
save(fig, 'f7_lengths')

# F8 agreement strip -----------------------------------------------------------------
L = json.load(open(os.path.join(BUILD, 'lunar_data.json')))['months']
rows = [('makkah', 'Makkah – naked eye'), ('madinah', 'Madinah – naked eye'), ('peshawar', 'Peshawar – naked eye'),
        ('pakistan', 'Pakistan – Ruet-e-Hilal*'), ('dallas', 'Dallas – naked eye'), ('fcna', 'USA – FCNA calendar')]
fig, ax = plt.subplots(figsize=(7.6, 2.0))
cmap = {-1: '#5B8FC9', 0: '#E8E8E8', 1: '#E6B54A', 2: '#B23A48'}
for r, (k, lab) in enumerate(rows):
    for i, mrec in enumerate(L):
        s = mrec['starts'].get(k)
        if not s: continue
        dd = (date.fromisoformat(s) - date.fromisoformat(mrec['starts']['uq'])).days
        ax.add_patch(Rectangle((i, -r - 0.9), 0.92, 0.8, color=cmap.get(dd, '#000')))
    ax.text(-1, -r - 0.5, lab, ha='right', va='center', fontsize=7)
ticks = [(i, f"1 Muh\n{m['y']}") for i, m in enumerate(L) if m['m'] == 0]
for i, t in ticks: ax.text(i + 0.45, -len(rows) - 0.4, t, ha='center', va='top', fontsize=5.6)
ax.set_xlim(-28, len(L) + 1); ax.set_ylim(-len(rows) - 1.6, 0.4); ax.axis('off')
fig.legend(handles=[Patch(color=cmap[-1], label='1 day before Umm al-Qura'), Patch(color=cmap[0], label='same day as Umm al-Qura'),
                    Patch(color=cmap[1], label='1 day after'), Patch(color=cmap[2], label='2 days after')], loc='lower center', ncol=4, fontsize=6.8, frameon=False, bbox_to_anchor=(0.55, -0.1))
save(fig, 'f8_agreement')
print('figures done')
