#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


def resolve_username() -> str:
    env = os.getenv("GITHUB_USERNAME")
    if env:
        return env

    try:
        remote = subprocess.check_output(
            ["git", "remote", "get-url", "origin"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if remote.endswith(".git"):
            remote = remote[:-4]
        if remote.startswith("git@github.com:"):
            remote = remote.split(":", 1)[1]
        if "github.com/" in remote:
            remote = remote.split("github.com/", 1)[1]
        owner = remote.split("/", 1)[0]
        if owner:
            return owner
    except Exception:
        pass

    return "Asjad611"


def sunday_on_or_before(day: date) -> date:
    return day - timedelta(days=(day.weekday() + 1) % 7)


def level_for(count: int) -> int:
    if count <= 0:
        return 0
    if count <= 2:
        return 1
    if count <= 5:
        return 2
    if count <= 8:
        return 3
    if count <= 13:
        return 4
    return 5


def parse_live(username: str) -> dict[date, int]:
    import requests
    from bs4 import BeautifulSoup

    url = f"https://github.com/users/{username}/contributions"
    resp = requests.get(
        url,
        timeout=20,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    svg = soup.select_one("svg.js-calendar-graph-svg")
    if svg is None:
        raise RuntimeError("contribution graph svg not found")

    days: dict[date, int] = {}
    for rect in svg.select("rect.ContributionCalendar-day[data-date]"):
        d = datetime.fromisoformat(rect["data-date"]).date()
        days[d] = int(rect.get("data-count", "0"))
    if not days:
        raise RuntimeError("no contribution cells found")
    return days


def parse_git_history(end: date) -> dict[date, int]:
    start = sunday_on_or_before(end - timedelta(weeks=52))
    result: dict[date, int] = {}
    try:
        raw = subprocess.check_output(
            [
                "git",
                "log",
                "--since",
                start.isoformat(),
                "--until",
                end.isoformat(),
                "--format=%ad",
                "--date=short",
            ],
            text=True,
            stderr=subprocess.DEVNULL,
        )
        counts = Counter(line.strip() for line in raw.splitlines() if line.strip())
        for offset in range(53 * 7):
            day = start + timedelta(days=offset)
            result[day] = counts.get(day.isoformat(), 0)
    except Exception:
        for offset in range(53 * 7):
            day = start + timedelta(days=offset)
            result[day] = 0
    return result


def summarize(days: dict[date, int]) -> dict[str, object]:
    ordered = sorted(days.items())
    total = sum(count for _, count in ordered)
    best_day, best_count = max(ordered, key=lambda item: (item[1], item[0].isoformat()))
    streak = 0
    last_actual = max(day for day in days if day <= date.today())
    cursor = last_actual
    while cursor in days and days[cursor] > 0:
        streak += 1
        cursor -= timedelta(days=1)

    longest = 0
    run = 0
    monthly: dict[str, int] = defaultdict(int)
    for day, count in ordered:
        monthly[day.strftime("%Y-%m")] += count
        if count > 0:
            run += 1
            longest = max(longest, run)
        else:
            run = 0

    return {
        "total": total,
        "current_streak": streak,
        "longest_streak": longest,
        "best_day": {"date": best_day.isoformat(), "count": best_count},
        "monthly_totals": dict(sorted(monthly.items())),
    }


def main() -> int:
    username = resolve_username()
    today = date.today()
    start = sunday_on_or_before(today) - timedelta(weeks=52)
    end = start + timedelta(days=53 * 7 - 1)

    try:
        raw_days = parse_live(username)
    except Exception:
        raw_days = parse_git_history(end)

    days = []
    for offset in range((end - start).days + 1):
        day = start + timedelta(days=offset)
        count = int(raw_days.get(day, 0))
        days.append(
            {
                "date": day.isoformat(),
                "weekday": (day.weekday() + 1) % 7,
                "count": count,
                "level": level_for(count),
                "week": offset // 7,
                "day": offset % 7,
            }
        )

    payload = {
        "username": username,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        **summarize({date.fromisoformat(item["date"]): item["count"] for item in days}),
        "days": days,
    }

    Path("data").mkdir(exist_ok=True)
    Path("data/contributions.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )
    print("data/contributions.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
