#!/usr/bin/env python3
"""Remove obsolete R0.2 optional-block debris after MCP component edits.

KiCad MCP performs the electrical component removal and all replacement wiring.
This helper only removes now-orphaned point labels, stale no-connect markers, and
obsolete explanatory text left behind by the deleted microSD/TCA9534/DNP-mic
implementation.  It deliberately leaves symbols, wires, junctions, and active
labels outside the retired optional-block area untouched.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from flatten_kicad_schematic import head, indent_form, top_level_forms


NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)"
AT_RE = re.compile(rf"\(at\s+({NUMBER})\s+({NUMBER})")
LABEL_RE = re.compile(r'^\((?:label|global_label|hierarchical_label)\s+"([^"]+)"')
TEXT_RE = re.compile(r'^\(text\s+"((?:[^"\\]|\\.)*)"', re.DOTALL)


SD_TCA_NETS = {
    "+3V3_SD",
    "SD_CARD_DET_N",
    "SD_CLK",
    "SD_CLK_CARD",
    "SD_CMD",
    "SD_CMD_CARD",
    "SD_D0",
    "SD_D0_CARD",
    "SD_D1",
    "SD_D1_CARD",
    "SD_D2",
    "SD_D2_CARD",
    "SD_D3",
    "SD_D3_CARD",
    "SD_PWR_EN",
    "SD_QOD",
    "USER_BTN_N",
    "STATUS_LED_N",
    "LED_ANODE",
}

STALE_NC_POINTS = {
    (449.58, 269.24),
    (553.72, 368.30),
    (563.88, 373.38),
    (563.88, 375.92),
}

OBSOLETE_TEXT = (
    "microsd",
    "tca9534",
    "analog microphone dnp",
    "mk1 has no adc/codec",
    "optional i2c sensors",
    "04 — switched 4-bit",
    "04 - switched 4-bit",
)


def at_point(form: str) -> tuple[float, float] | None:
    match = AT_RE.search(form)
    if not match:
        return None
    return (round(float(match.group(1)), 2), round(float(match.group(2)), 2))


def is_retired_optional_label(form: str) -> bool:
    match = LABEL_RE.match(form)
    if not match:
        return False
    name = match.group(1)
    if name in SD_TCA_NETS:
        return True
    point = at_point(form)
    if point is None:
        return False
    x, y = point
    return 330.0 <= x <= 590.0 and 240.0 <= y <= 315.0


def is_stale_no_connect(form: str) -> bool:
    point = at_point(form)
    return point in STALE_NC_POINTS if point is not None else False


def is_obsolete_text(form: str) -> bool:
    match = TEXT_RE.match(form)
    if not match:
        return False
    value = match.group(1).replace(r"\n", " ").lower()
    return any(needle in value for needle in OBSOLETE_TEXT)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("schematic", type=Path)
    args = parser.parse_args()
    path = args.schematic.resolve()
    forms = top_level_forms(path.read_text(encoding="utf-8"))

    kept: list[str] = []
    removed = {"labels": 0, "no_connects": 0, "texts": 0}
    for form in forms:
        kind = head(form)
        if kind in {"label", "global_label", "hierarchical_label"} and is_retired_optional_label(form):
            removed["labels"] += 1
            continue
        if kind == "no_connect" and is_stale_no_connect(form):
            removed["no_connects"] += 1
            continue
        if kind == "text" and is_obsolete_text(form):
            removed["texts"] += 1
            continue
        kept.append(form)

    path.write_text(
        "(kicad_sch\n" + "\n".join(indent_form(form, 1) for form in kept) + "\n)\n",
        encoding="utf-8",
        newline="\n",
    )
    print(
        f"removed {removed['labels']} labels, "
        f"{removed['no_connects']} no-connects, {removed['texts']} texts"
    )


if __name__ == "__main__":
    main()
