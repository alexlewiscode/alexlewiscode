#!/usr/bin/env python3
"""Fetch the public GitHub contribution calendar and store normalized JSON."""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "alexlewiscode"
ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "contributions.json"


def streaks(days: list[dict[str, object]]) -> tuple[int, int]:
    counts = {date.fromisoformat(str(day["date"])): int(day["count"]) for day in days}
    today = date.today()

    # GitHub may not have finalized today's activity, so an active streak may end yesterday.
    cursor = today if counts.get(today, 0) else today - timedelta(days=1)
    current = 0
    while counts.get(cursor, 0) > 0:
        current += 1
        cursor -= timedelta(days=1)

    longest = running = 0
    for day in sorted(counts):
        if counts[day] > 0:
            running += 1
            longest = max(longest, running)
        else:
            running = 0
    return current, longest


def main() -> None:
    url = f"https://github.com/users/{USERNAME}/contributions"
    response = requests.get(
        url,
        timeout=30,
        headers={"User-Agent": f"{USERNAME}-profile-readme/1.0"},
    )
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    days: list[dict[str, object]] = []
    for cell in soup.select("td.ContributionCalendar-day[data-date]"):
        cell_id = cell.get("id", "")
        tooltip = soup.find("tool-tip", attrs={"for": cell_id})
        tooltip_text = tooltip.get_text(" ", strip=True) if tooltip else ""
        match = re.search(r"([\d,]+) contributions?", tooltip_text)
        count = int(match.group(1).replace(",", "")) if match else 0
        days.append(
            {
                "date": cell["data-date"],
                "count": count,
                "level": int(cell.get("data-level", 0)),
            }
        )

    if not days:
        raise RuntimeError("GitHub returned no contribution calendar cells")

    days.sort(key=lambda item: str(item["date"]))
    current, longest = streaks(days)
    best = max(days, key=lambda item: int(item["count"]))
    payload = {
        "username": USERNAME,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total": sum(int(day["count"]) for day in days),
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best,
        "days": days,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(days)} days to {OUTPUT}")


if __name__ == "__main__":
    main()

