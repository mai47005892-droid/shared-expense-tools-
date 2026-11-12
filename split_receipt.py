#!/usr/bin/env python3
"""Allocate itemized receipt lines in integer cents using largest remainder."""

from __future__ import annotations

import argparse
import csv
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path


def to_cents(raw: str, row_number: int) -> int:
    try:
        value = Decimal(raw.strip())
    except InvalidOperation as exc:
        raise ValueError(f"row {row_number}: invalid amount {raw!r}") from exc
    if not value.is_finite() or value < 0:
        raise ValueError(f"row {row_number}: amount must be a finite non-negative value")
    cents_value = value * 100
    if cents_value != cents_value.to_integral_value():
        raise ValueError(f"row {row_number}: amount must have no more than two decimal places")
    return int(cents_value)


def split_cents(total_cents: int, participants: list[str]) -> list[tuple[str, int]]:
    if not participants:
        raise ValueError("each row needs at least one participant")
    unique: list[str] = []
    seen: set[str] = set()
    for name in participants:
        cleaned = name.strip()
        if cleaned and cleaned not in seen:
            unique.append(cleaned)
            seen.add(cleaned)
    if not unique:
        raise ValueError("each row needs at least one non-empty participant name")

    base, remainder = divmod(total_cents, len(unique))
    # Equal shares have equal fractional remainders. Input order breaks the tie.
    return [(name, base + (1 if index < remainder else 0)) for index, name in enumerate(unique)]


def dollars(cents: int) -> str:
    return f"{Decimal(cents) / 100:.2f}"


def allocate(source: Path, allocation_path: Path, totals_path: Path) -> None:
    totals: dict[str, int] = {}
    try:
        with source.open("r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            required = {"item", "amount", "participants"}
            if not reader.fieldnames or not required.issubset(reader.fieldnames):
                raise ValueError("CSV must contain item, amount, and participants columns")
            with allocation_path.open("w", newline="", encoding="utf-8") as out:
                writer = csv.writer(out)
                writer.writerow(["item", "participant", "allocated_amount"])
                for row_number, row in enumerate(reader, start=2):
                    item = (row.get("item") or "").strip()
                    if not item:
                        raise ValueError(f"row {row_number}: item cannot be empty")
                    cents = to_cents(row.get("amount") or "", row_number)
                    names = (row.get("participants") or "").split("|")
                    try:
                        shares = split_cents(cents, names)
                    except ValueError as exc:
                        raise ValueError(f"row {row_number}: {exc}") from exc
                    for name, share in shares:
                        writer.writerow([item, name, dollars(share)])
                        totals[name] = totals.get(name, 0) + share
    except OSError as exc:
        raise ValueError(str(exc)) from exc

    with totals_path.open("w", newline="", encoding="utf-8") as out:
        writer = csv.writer(out)
        writer.writerow(["participant", "total_allocated_amount"])
        for name, cents in totals.items():
            writer.writerow([name, dollars(cents)])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv", type=Path, help="CSV with item, amount, participants columns")
    parser.add_argument("--allocations", type=Path, default=Path("allocations.csv"))
    parser.add_argument("--totals", type=Path, default=Path("totals.csv"))
    args = parser.parse_args()
    try:
        allocate(args.input_csv, args.allocations, args.totals)
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
