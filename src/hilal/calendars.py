"""Hijri calendars built from month-start rules.

A calendar is a chain of months. Given the 1st of a month, the evening of the 29th decides:
  if the rule is satisfied on that evening -> the next month starts the following day (29-day month)
  otherwise                                 -> the month completes 30 days.
This mirrors the hadith practice ("if it is obscured, complete thirty") for sighting-based rules and the
published Umm al-Qura procedure for the Saudi civil calendar.
"""
from datetime import date, timedelta
from . import astro as A
from . import crescent as C
from .places import MAKKAH

MONTHS = ['Muharram', 'Safar', "Rabi' al-Awwal", "Rabi' al-Thani", 'Jumada al-Ula', 'Jumada al-Akhirah',
          'Rajab', "Sha'ban", 'Ramadan', 'Shawwal', "Dhu al-Qa'dah", 'Dhu al-Hijjah']
MONTHS_AR = ['محرم', 'صفر', 'ربيع الأول', 'ربيع الآخر', 'جمادى الأولى', 'جمادى الآخرة', 'رجب', 'شعبان', 'رمضان',
             'شوال', 'ذو القعدة', 'ذو الحجة']

def conj_for_evening(d, place):
    j = C.local_midnight_jd(d, place) + 1.0
    return A.previous_new_moon(j)

class Rule:
    name = 'rule'
    def __call__(self, d):            # is the crescent condition met on the evening of civil date d?
        raise NotImplementedError

class UmmAlQura(Rule):
    name = 'Umm al-Qura (Saudi civil calendar)'
    def __call__(self, d):
        cj = conj_for_evening(d, MAKKAH)
        return C.ummalqura_condition(d, cj)[0]

class LocalSighting(Rule):
    """Crescent expected visible from `place` (Odeh criterion; threshold 5.65 = naked eye)."""
    def __init__(self, place, threshold=5.65):
        self.place, self.threshold = place, threshold
        self.name = f'Local sighting at {place.name} (Odeh V >= {threshold})'
    def __call__(self, d):
        cj = conj_for_evening(d, self.place)
        return C.evening(d, self.place, cj)['V'] >= self.threshold

class Global8_5(Rule):
    name = 'FCNA / ECFR global criterion (elongation 8, altitude 5)'
    def __call__(self, d):
        cj = conj_for_evening(d, MAKKAH)
        return C.fcna_condition(d, cj)[0]

class HijriCalendar:
    def __init__(self, rule, anchor_date, anchor_month, anchor_year):
        """anchor_*: a known 1st of month (month index 0..11)."""
        self.rule = rule
        self.starts = [(anchor_date, anchor_month, anchor_year)]

    def extend_to(self, last_date):
        while self.starts[-1][0] <= last_date + timedelta(days=31):
            s, m, y = self.starts[-1]
            nxt = s + timedelta(days=29 if self.rule(s + timedelta(days=28)) else 30)
            m, y = (m + 1, y) if m < 11 else (0, y + 1)
            self.starts.append((nxt, m, y))
        return self

    def to_hijri(self, d):
        self.extend_to(d)
        for i in range(len(self.starts) - 1):
            s, m, y = self.starts[i]
            if s <= d < self.starts[i + 1][0]:
                return y, m, (d - s).days + 1
        raise ValueError('date before anchor')

    def month_start(self, year, month):
        for s, m, y in self.starts:
            if (y, m) == (year, month): return s
        last = self.starts[-1]
        if (year, month) > (last[2], last[1]):
            self.extend_to(last[0] + timedelta(days=30 * ((year - last[2]) * 12 + month - last[1]) + 30))
            return self.month_start(year, month)
        raise KeyError((year, month))

def first_visibility_start(place, after_jd, threshold=5.65, max_days=4):
    """Day after the first evening (after conjunction) when the crescent is visible from place."""
    d = A.dt_from_jd(after_jd).astimezone(place.zone).date()
    for _ in range(max_days):
        cj = conj_for_evening(d, place)
        if C.evening(d, place, cj)['V'] >= threshold:
            return d + timedelta(days=1)
        d += timedelta(days=1)
    return d
