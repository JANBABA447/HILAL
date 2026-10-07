"""Reference locations (lat, lon east-positive, IANA time zone, elevation m)."""
from dataclasses import dataclass
from zoneinfo import ZoneInfo

@dataclass(frozen=True)
class Place:
    key: str
    name: str
    lat: float
    lon: float
    tz: str
    elev: float = 0.0
    @property
    def zone(self): return ZoneInfo(self.tz)

MAKKAH   = Place('makkah',   'Makkah (Masjid al-Haram)',  21.4225, 39.8262, 'Asia/Riyadh', 277)
MADINAH  = Place('madinah',  'Madinah (Masjid an-Nabawi)', 24.4672, 39.6111, 'Asia/Riyadh', 608)
PESHAWAR = Place('peshawar', 'Peshawar',                  34.0151, 71.5249, 'Asia/Karachi', 331)
DALLAS   = Place('dallas',   'Dallas, TX',                32.7767, -96.7970, 'America/Chicago', 139)
IRVING   = Place('irving',   'Irving, TX (ICI)',          32.8550, -96.9580, 'America/Chicago', 150)
KARACHI  = Place('karachi',  'Karachi',                   24.8607, 67.0011, 'Asia/Karachi', 10)
ALL = {p.key: p for p in (MAKKAH, MADINAH, PESHAWAR, DALLAS, IRVING, KARACHI)}
