"""24-hour prayer timeline charts (one per city) for document ISL-CAL-014."""
import sys, os
from datetime import date, datetime, timedelta
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
from hilal import timeline as T
from hilal.places import MAKKAH, PESHAWAR, DALLAS

OUT, D0 = sys.argv[1], date.fromisoformat(sys.argv[2] if len(sys.argv) > 2 else '2026-10-06')
COL = {'Fajr': '#1F3F66', 'Dhuhr': '#C9A227', 'Asr': '#D9822B', 'Maghrib': '#7A2E36', 'Isha': '#1E5B3C',
       'Dhuhr & Asr': '#C9A227', 'Maghrib & Isha': '#4C6B3C'}
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8})
FAJR = {'makkah': 18.5, 'peshawar': 18.0, 'dallas': 15.0}

for place in (MAKKAH, PESHAWAR, DALLAS):
    fig, ax = plt.subplots(figsize=(10.2, 3.15))
    base = datetime.combine(D0, datetime.min.time(), place.zone)
    h = lambda t: (t - base).total_seconds() / 3600
    lo = None
    for row, (key, label) in enumerate(reversed(list(T.SCHOOLS.items()))):
        fa = 16.0 if key == 'jafari' else FAJR[place.key]
        for name, a, b, st, note in T.day(D0, place, key, fajr_angle=fa):
            x0, x1 = h(a), h(b)
            if st == 'prayer':
                base_name = name.split(' (')[0]
                c = COL.get(base_name, '#888')
                ax.add_patch(Rectangle((x0, row + 0.18), x1 - x0, 0.56, color=c, alpha=0.55, lw=0))
                ax.text((x0 + min(x1, 28)) / 2, row + 0.46, base_name, ha='center', va='center', fontsize=6.6, color='#111')
            elif st == 'preferred':
                ax.add_patch(Rectangle((x0, row + 0.18), x1 - x0, 0.12, color='#111', alpha=0.55, lw=0))
            elif st in ('forbidden', 'disliked'):
                ax.add_patch(Rectangle((x0, row + 0.74), x1 - x0, 0.16, color='#C0392B' if st == 'forbidden' else '#E59866', lw=0))
            elif a == b:
                ax.plot([x0, x0], [row + 0.12, row + 0.92], color='#555', lw=0.8, ls=':')
        lo = h(T.boundaries(D0, place, fajr_angle=FAJR[place.key])['fajr']) if lo is None else lo
    b = T.boundaries(D0, place, fajr_angle=FAJR[place.key])
    for k, lab in (('sunrise', 'sunrise'), ('transit', 'noon'), ('sunset', 'sunset')):
        x = h(b[k]); ax.axvline(x, color='#999', lw=0.6, ls='--')
        ax.text(x, 5.05, f"{lab} {b[k]:%H:%M:%S}", ha='center', fontsize=6.5, color='#555')
    ax.set_yticks([i + 0.5 for i in range(5)]); ax.set_yticklabels([v for v in reversed(list(T.SCHOOLS.values()))], fontsize=7.4)
    start = int(lo) - 1
    end = h(b['fajr_next']) + 0.5
    ax.set_xlim(start, end); ax.set_ylim(0, 5.3)
    ticks = list(range(start, int(end) + 1, 2)); ax.set_xticks(ticks); ax.set_xticklabels([f"{t % 24:02d}:00" for t in ticks], fontsize=6.8)
    for s in ('top', 'right', 'left'): ax.spines[s].set_visible(False)
    ax.tick_params(axis='y', length=0)
    ax.set_title(f"{place.name} — {D0:%A %d %B %Y} (local time; Fajr {FAJR[place.key]}°, Ja'fari 16°)", fontsize=9, loc='left')
    leg = [Patch(color=COL[k], alpha=0.55, label=k) for k in ('Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha')]
    leg += [Patch(color='#555', label='preferred (chosen) time'), Patch(color='#C0392B', label='prohibited'), Patch(color='#E59866', label='disliked (Ja\'fari)')]
    fig.legend(handles=leg, loc='lower center', ncol=8, fontsize=6.6, frameon=False, bbox_to_anchor=(0.5, -0.04))
    fig.savefig(os.path.join(OUT, f'tl_{place.key}.svg'), bbox_inches='tight', transparent=True); plt.close(fig)
print('ok')
