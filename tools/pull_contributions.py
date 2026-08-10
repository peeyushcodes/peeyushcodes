"""
pull_contributions.py
---------------------
Scrapes the public GitHub contribution calendar for peeyushcodes
and writes assets/contributions.json — no API token required.
"""

import json
import re
from datetime import datetime
from pathlib import Path

import httpx
from lxml import html

USERNAME = "peeyushcodes"
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT = Path(__file__).parent.parent / "assets" / "contributions.json"


def fetch_html() -> str:
    headers = {"Accept": "text/html", "User-Agent": "Mozilla/5.0"}
    r = httpx.get(URL, headers=headers, follow_redirects=True, timeout=20)
    r.raise_for_status()
    return r.text


def parse_days(raw_html: str) -> list[dict]:
    tree = html.fromstring(raw_html)
    days = []
    # GitHub uses <td> or <rect> elements with data-date and data-level
    cells = tree.xpath('//*[@data-date and @data-level]')
    for cell in cells:
        date_str = cell.get("data-date", "")
        level = int(cell.get("data-level", 0))
        count_text = cell.get("data-count", None)
        if count_text is None:
            # try to extract from tooltip text
            tooltip = cell.get("aria-label", "")
            m = re.search(r"(\d+)\s+contribution", tooltip)
            count = int(m.group(1)) if m else 0
        else:
            count = int(count_text)
        if date_str:
            days.append({"date": date_str, "count": count, "level": level})
    # sort chronologically
    days.sort(key=lambda d: d["date"])
    return days


def compute_stats(days: list[dict]) -> dict:
    total = sum(d["count"] for d in days)

    # current streak
    current_streak = 0
    for d in reversed(days):
        if d["count"] > 0:
            current_streak += 1
        else:
            break

    # longest streak
    longest = cur = 0
    for d in days:
        if d["count"] > 0:
            cur += 1
            longest = max(longest, cur)
        else:
            cur = 0

    # busiest day of week
    weekday_counts = [0] * 7
    for d in days:
        try:
            dt = datetime.strptime(d["date"], "%Y-%m-%d")
            weekday_counts[dt.weekday()] += d["count"]
        except ValueError:
            pass
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    busiest_dow = day_names[weekday_counts.index(max(weekday_counts))]

    return {
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest,
        "busiest_day_of_week": busiest_dow,
        "fetched_at": datetime.utcnow().isoformat() + "Z",
    }


def main():
    print(f"Fetching contributions for {USERNAME}...")
    raw = fetch_html()
    days = parse_days(raw)
    if not days:
        print("WARNING: No contribution cells found — GitHub may have changed markup.")
    stats = compute_stats(days)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {"stats": stats, "days": days}
    OUT.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {len(days)} days to {OUT}")
    print(f"Stats: {stats}")


if __name__ == "__main__":
    main()
