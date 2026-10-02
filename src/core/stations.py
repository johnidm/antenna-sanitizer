"""Radio station CSV loading, saving, and sampling."""

from __future__ import annotations

import csv
import json
import random
import uuid
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

CSV_FIELDNAMES: list[str] = [
    "id",
    "name",
    "country",
    "country_code",
    "language",
    "stream_url",
    "homepage_url",
    "logo_url",
    "tags",
    "status",
]


class StationStatus(StrEnum):
    PENDING = "pending"
    READY = "ready"
    REJECTED = "rejected"

    @classmethod
    def parse(cls, value: str | None) -> StationStatus:
        """Parse a status string, falling back to PENDING if invalid or missing."""
        if not value:
            return cls.PENDING
        try:
            return cls(value.strip().lower())
        except ValueError:
            return cls.PENDING


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
    status: StationStatus = StationStatus.PENDING


def create_station(  # noqa: PLR0913
    name: str,
    stream_url: str,
    *,
    country: str = "",
    country_code: str = "",
    language: str = "",
    homepage_url: str = "",
    logo_url: str = "",
    tags: str | list[str] = "",
    station_id: str | None = None,
) -> Station:
    """Create a new station with pending status and auto-generated UUIDv7 if not provided."""
    sid = station_id or str(getattr(uuid, "uuid7", uuid.uuid4)())
    if isinstance(tags, str):
        tag_list = [t.strip() for t in tags.split(",") if t.strip()]
        tags_json = json.dumps(tag_list)
    else:
        tags_json = json.dumps(tags)

    return Station(
        id=sid,
        name=name.strip(),
        country=country.strip(),
        country_code=country_code.strip().upper(),
        language=language.strip().lower(),
        stream_url=stream_url.strip(),
        homepage_url=homepage_url.strip(),
        logo_url=logo_url.strip(),
        tags=tags_json,
        status=StationStatus.PENDING,
    )


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
                status=StationStatus.parse(row.get("status")),
            )
            for row in reader
        ]


def filter_by_status(
    stations: Sequence[Station],
    status: StationStatus,
) -> list[Station]:
    """Return stations matching the given status."""
    return [s for s in stations if s.status == status]


def load_ready_stations(path: Path | None = None) -> list[Station]:
    """Load only stations marked as ready for export."""
    return filter_by_status(load_stations(path), StationStatus.READY)


def save_stations(stations: Sequence[Station], path: Path | None = None) -> None:
    """Save stations back to the CSV file atomically."""
    csv_path = path or Path(__file__).resolve().parents[2] / "data" / "stations.csv"
    temp_path = csv_path.with_suffix(".csv.tmp")

    with temp_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        for station in stations:
            writer.writerow(
                {
                    "id": station.id,
                    "name": station.name,
                    "country": station.country,
                    "country_code": station.country_code,
                    "language": station.language,
                    "stream_url": station.stream_url,
                    "homepage_url": station.homepage_url,
                    "logo_url": station.logo_url,
                    "tags": station.tags,
                    "status": station.status.value,
                }
            )

    temp_path.replace(csv_path)


def append_station(station: Station, path: Path | None = None) -> None:
    """Append a single station to the CSV file."""
    csv_path = path or Path(__file__).resolve().parents[2] / "data" / "stations.csv"
    file_exists = csv_path.exists() and csv_path.stat().st_size > 0

    with csv_path.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDNAMES, lineterminator="\n")
        if not file_exists:
            writer.writeheader()
        writer.writerow(
            {
                "id": station.id,
                "name": station.name,
                "country": station.country,
                "country_code": station.country_code,
                "language": station.language,
                "stream_url": station.stream_url,
                "homepage_url": station.homepage_url,
                "logo_url": station.logo_url,
                "tags": station.tags,
                "status": station.status.value,
            }
        )


def pick_random(stations: Sequence[Station], n: int = 3) -> list[Station]:
    if len(stations) < n:
        raise ValueError(f"Need at least {n} stations, found {len(stations)}")
    return random.sample(list(stations), n)


@dataclass(frozen=True, slots=True)
class StationStats:
    total: int
    pending: int
    ready: int
    rejected: int
    with_stream: int
    with_homepage: int
    countries_count: int

    @property
    def ready_pct(self) -> float:
        return (self.ready / self.total * 100) if self.total else 0.0

    @property
    def pending_pct(self) -> float:
        return (self.pending / self.total * 100) if self.total else 0.0

    @property
    def rejected_pct(self) -> float:
        return (self.rejected / self.total * 100) if self.total else 0.0


def compute_stats(stations: Sequence[Station]) -> StationStats:
    """Compute aggregate counts and readiness statistics."""
    total = len(stations)
    pending = 0
    ready = 0
    rejected = 0
    with_stream = 0
    with_homepage = 0
    countries: set[str] = set()

    for s in stations:
        match s.status:
            case StationStatus.READY:
                ready += 1
            case StationStatus.REJECTED:
                rejected += 1
            case _:
                pending += 1

        if s.stream_url.strip():
            with_stream += 1
        if s.homepage_url.strip():
            with_homepage += 1
        if s.country_code.strip():
            countries.add(s.country_code.strip().upper())

    return StationStats(
        total=total,
        pending=pending,
        ready=ready,
        rejected=rejected,
        with_stream=with_stream,
        with_homepage=with_homepage,
        countries_count=len(countries),
    )
