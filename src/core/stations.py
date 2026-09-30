"""Radio station CSV loading and sampling."""

from __future__ import annotations

import csv
import random
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Station:
    id: str
    name: str
    country: str
    country_code: str
    language: str
    stream_url: str
    homepage_url: str
    logo_url: str
    tags: str


def load_stations(path: Path | None = None) -> list[Station]:
    csv_path = path or Path(__file__).resolve().parents[2] / "data" / "stations.csv"

    with csv_path.open(encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        return [
            Station(
                id=row["id"],
                name=row["name"],
                country=row["country"],
                country_code=row["country_code"],
                language=row["language"],
                stream_url=row["stream_url"],
                homepage_url=row["homepage_url"],
                logo_url=row["logo_url"],
                tags=row["tags"],
            )
            for row in reader
        ]


def pick_random(stations: Sequence[Station], n: int = 3) -> list[Station]:
    if len(stations) < n:
        raise ValueError(f"Need at least {n} stations, found {len(stations)}")
    return random.sample(list(stations), n)
