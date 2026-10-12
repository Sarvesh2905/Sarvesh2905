"""Fetch Sarvesh's public GitHub contribution calendar using only Python stdlib."""

from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "data" / "contributions.json"
USERNAME = os.environ.get("GH_PROFILE_USER", "Sarvesh2905")
URL = f"https://github.com/users/{USERNAME}/contributions"


def fetch_days() -> list[dict]:
    request = urllib.request.Request(URL, headers={"User-Agent": "profile-readme-art/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        source = response.read().decode("utf-8")

    tooltips = {}
    for target, text in re.findall(r'<tool-tip[^>]+for="([^"]+)"[^>]*>(.*?)</tool-tip>', source, re.S | re.I):
        tooltips[target] = html.unescape(re.sub(r"<[^>]+>", "", text)).strip()

    days = []
    for tag in re.findall(r'<td\b[^>]*ContributionCalendar-day[^>]*>', source, re.I):
        attrs = dict(re.findall(r'([\w:-]+)="([^"]*)"', tag))
        date = attrs.get("data-date")
        if not date:
            continue
        tooltip = tooltips.get(attrs.get("id", ""), "")
        match = re.match(r"([\d,]+) contribution", tooltip, re.I)
        count = int(match.group(1).replace(",", "")) if match else 0
        days.append({"date": date, "count": count, "level": int(attrs.get("data-level", 0))})
    days.sort(key=lambda day: day["date"])
    if not days:
        raise RuntimeError("GitHub returned no contribution cells; its markup may have changed")
    return days


def streaks(days: list[dict]) -> tuple[dict, dict]:
    current = {"length": 0, "start": None, "end": None}
    index = len(days) - 1
    if days[index]["count"] == 0:
        index -= 1
    end = index
    while index >= 0 and days[index]["count"] > 0:
        current["length"] += 1
        index -= 1
    if current["length"]:
        current.update(start=days[index + 1]["date"], end=days[end]["date"])

    longest = {"length": 0, "start": None, "end": None}
    run_start = run = 0
    for index, day in enumerate(days):
        if day["count"]:
            if not run:
                run_start = index
            run += 1
            if run > longest["length"]:
                longest = {"length": run, "start": days[run_start]["date"], "end": day["date"]}
        else:
            run = 0
    return current, longest


def build(days: list[dict]) -> dict:
    current, longest = streaks(days)
    total = sum(day["count"] for day in days)
    best = max(days, key=lambda day: day["count"])
    return {
        "username": USERNAME,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "range": {"start": days[0]["date"], "end": days[-1]["date"]},
        "total_contributions": total,
        "active_days": sum(day["count"] > 0 for day in days),
        "current_streak": current,
        "longest_streak": longest,
        "best_day": {"date": best["date"], "count": best["count"]},
        "days": days,
    }


if __name__ == "__main__":
    payload = build(fetch_days())
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT}: {payload['total_contributions']} contributions")
