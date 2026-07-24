"""Export and safely extract one generated golden-path service for CI validation."""
from __future__ import annotations

import argparse
import io
from pathlib import Path
import zipfile

from platformpulse.generator import ServiceConfig, generate_service_zip, sanitize_service_name


def safe_extract(payload: bytes, destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    destination_resolved = destination.resolve()
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        for member in archive.infolist():
            target = (destination / member.filename).resolve()
            if destination_resolved not in target.parents and target != destination_resolved:
                raise ValueError(f"Unsafe archive path: {member.filename}")
        archive.extractall(destination)
    return destination


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="generated")
    args = parser.parse_args()
    config = ServiceConfig(
        service_name="demo-secure-api",
        team="developer-experience",
        database="PostgreSQL",
        environment="staging",
        slo_target=99.9,
    )
    output = safe_extract(generate_service_zip(config), Path(args.output))
    print(output / sanitize_service_name(config.service_name))


if __name__ == "__main__":
    main()
