"""SQL export generation compatible with PostgreSQL and SQLite."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from src.core.stations import Station

from src.core.stations import StationStatus, load_stations


def _sql_str(value: str | None, allow_null: bool = True) -> str:
    """Escape and quote a string for standard SQL, or return NULL."""
    if value is None or (allow_null and value == ""):
        return "NULL"
    escaped = value.replace("'", "''")
    return f"'{escaped}'"


def generate_upsert_statement(station: Station) -> str:
    """Generate an INSERT ... ON CONFLICT (id) DO UPDATE SET statement."""
    fields = (
        _sql_str(station.id, allow_null=False),
        _sql_str(station.name, allow_null=False),
        _sql_str(station.country),
        _sql_str(station.country_code),
        _sql_str(station.language),
        _sql_str(station.stream_url, allow_null=False),
        _sql_str(station.homepage_url),
        _sql_str(station.logo_url),
        _sql_str(station.tags),
    )

    values_clause = ",\n    ".join(fields)

    return (
        "INSERT INTO stations (\n"
        "    id, name, country, country_code, language, stream_url, homepage_url, logo_url, tags\n"
        f") VALUES (\n    {values_clause}\n)\n"
        "ON CONFLICT (id) DO UPDATE SET\n"
        "    name = EXCLUDED.name,\n"
        "    country = EXCLUDED.country,\n"
        "    country_code = EXCLUDED.country_code,\n"
        "    language = EXCLUDED.language,\n"
        "    stream_url = EXCLUDED.stream_url,\n"
        "    homepage_url = EXCLUDED.homepage_url,\n"
        "    logo_url = EXCLUDED.logo_url,\n"
        "    tags = EXCLUDED.tags;"
    )


def generate_export_filename(now: datetime | None = None) -> str:
    """Generate standard export filename: stations-<datetime>.sql."""
    ts = (now or datetime.now()).strftime("%Y%m%d_%H%M%S")
    return f"stations-{ts}.sql"


def get_default_exports_dir() -> Path:
    """Return default export directory (data/exports)."""
    return Path(__file__).resolve().parents[2] / "data" / "exports"


def export_ready_stations_sql(
    stations: Sequence[Station],
    output_dir: Path | None = None,
    filename: str | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
) -> tuple[Path, int]:
    """Export stations with status='ready' into a dual-compatible SQL file."""
    ready_stations = [s for s in stations if s.status == StationStatus.READY]
    if not ready_stations:
        raise ValueError("No stations marked as 'ready' to export.")

    dest_dir = output_dir or get_default_exports_dir()
    dest_dir.mkdir(parents=True, exist_ok=True)

    file_name = filename or generate_export_filename()
    out_path = dest_dir / file_name

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = len(ready_stations)

    with out_path.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("-- Antenna Sanitizer SQL Export\n")
        fh.write(f"-- Generated: {now_str}\n")
        fh.write(f"-- Records: {total:,}\n")
        fh.write("-- Compatible with: PostgreSQL (>= 9.5) and SQLite (>= 3.24.0)\n\n")
        fh.write("BEGIN TRANSACTION;\n\n")

        for idx, station in enumerate(ready_stations, start=1):
            fh.write(generate_upsert_statement(station))
            fh.write("\n\n")
            if progress_callback and (idx % 25 == 0 or idx == total):
                progress_callback(idx, total)

        fh.write("COMMIT;\n")

    return out_path, total


def export_sql_from_csv(
    csv_path: Path | None = None,
    output_dir: Path | None = None,
    filename: str | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
) -> tuple[Path, int]:
    """Load stations from CSV and export those marked as 'ready'."""
    stations = load_stations(csv_path)
    return export_ready_stations_sql(
        stations,
        output_dir=output_dir,
        filename=filename,
        progress_callback=progress_callback,
    )
