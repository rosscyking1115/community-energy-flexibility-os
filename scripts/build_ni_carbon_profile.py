"""Build Northern Ireland's typical half-hourly carbon profile from EirGrid.

EirGrid publishes NI carbon intensity as *actuals* (15-min), not a forecast, so
NI can't use a live day-ahead forecast like GB. Instead we precompute a
typical-day profile: average recent actuals by half-hour-of-day into 48 slots,
and ship it as a reference file (refresh by re-running + redeploy).

    python scripts/build_ni_carbon_profile.py [days]
"""

from __future__ import annotations

import json
import sys
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "data" / "reference" / "ni_carbon_profile.json"
BASE = "https://www.smartgriddashboard.com/DashboardService.svc/data"


def _fetch_day(day: date) -> list[dict]:
    url = (
        f"{BASE}?area=co2intensity&region=NI"
        f"&datefrom={day:%d-%b-%Y}+00:00&dateto={day:%d-%b-%Y}+23:59"
    ).replace(" ", "+")
    headers = {"User-Agent": "Mozilla/5.0 ceflex", "Accept": "application/json"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:  # noqa: S310 - fixed host
        return json.loads(resp.read()).get("Rows", [])


def main(days: int = 14) -> int:
    sums = [0.0] * 48
    counts = [0] * 48
    today = date.today()
    fetched = 0
    for d in range(1, days + 1):
        day = today - timedelta(days=d)
        try:
            rows = _fetch_day(day)
        except Exception as exc:  # noqa: BLE001
            print(f"  {day}: fetch failed ({exc})")
            continue
        for r in rows:
            if r.get("Value") is None:
                continue
            t = datetime.strptime(r["EffectiveTime"], "%d-%b-%Y %H:%M:%S")
            slot = t.hour * 2 + (1 if t.minute >= 30 else 0)
            sums[slot] += float(r["Value"])
            counts[slot] += 1
        fetched += 1

    if min(counts) == 0:
        print(f"Incomplete coverage after {fetched} days (some slots empty); try more days.")
        return 1

    curve = [round(sums[i] / counts[i], 1) for i in range(48)]
    OUT.write_text(
        json.dumps(
            {
                "region": "northern-ireland",
                "source": "EirGrid Smart Grid Dashboard (co2intensity, NI) - recent actuals",
                "generated_at": datetime.now().isoformat(timespec="seconds"),
                "days_averaged": fetched,
                "unit": "gCO2/kWh",
                "curve": curve,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(
        f"{OUT.name}: 48-slot NI profile from {fetched} days "
        f"| range {min(curve):.0f}-{max(curve):.0f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 14))
