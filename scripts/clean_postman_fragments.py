#!/usr/bin/env python3
"""Utility to remove StartFragment/EndFragment markers from Postman collections."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Tuple

PREFIX = "StartFragment"
SUFFIX = "EndFragment"


def clean_description(value: str) -> Tuple[str, bool]:
    """Strip StartFragment/EndFragment markers from a description string."""
    changed = False
    text = value

    if text.startswith(PREFIX):
        text = text[len(PREFIX) :]
        if text.startswith("\r\n"):
            text = text[2:]
        elif text.startswith("\n"):
            text = text[1:]
        changed = True
    else:
        lstripped = text.lstrip()
        if lstripped is not text and lstripped.startswith(PREFIX):
            text = lstripped[len(PREFIX) :]
            if text.startswith("\r\n"):
                text = text[2:]
            elif text.startswith("\n"):
                text = text[1:]
            changed = True

    if text.endswith(SUFFIX):
        text = text[: -len(SUFFIX)]
        changed = True
    else:
        rstripped = text.rstrip()
        if rstripped is not text and rstripped.endswith(SUFFIX):
            text = rstripped[: -len(SUFFIX)]
            changed = True

    if changed:
        text = text.strip("\r\n")

    return text, changed


def cleanse_fragments(node: Any) -> int:
    """Traverse ``node`` and clean any description values.

    Returns the number of descriptions that were modified.
    """
    cleaned = 0

    if isinstance(node, dict):
        for key, value in list(node.items()):
            if key == "description" and isinstance(value, str):
                new_value, changed = clean_description(value)
                if changed:
                    node[key] = new_value
                    cleaned += 1
            cleaned += cleanse_fragments(value)
    elif isinstance(node, list):
        for item in node:
            cleaned += cleanse_fragments(item)

    return cleaned


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def dump_json(path: Path, payload: Any) -> None:
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
        fh.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Remove StartFragment/EndFragment markers from Postman collections.",
    )
    parser.add_argument("path", type=Path, help="Path to the Postman collection JSON file")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Inspect the file without writing changes to disk.",
    )
    args = parser.parse_args()

    data = load_json(args.path)
    modified = cleanse_fragments(data)

    if modified and not args.dry_run:
        dump_json(args.path, data)

    if args.dry_run:
        print(f"{modified} description entries would be updated.")
    else:
        if modified:
            print(f"Updated {modified} description entries in {args.path}.")
        else:
            print("No StartFragment/EndFragment markers found.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
