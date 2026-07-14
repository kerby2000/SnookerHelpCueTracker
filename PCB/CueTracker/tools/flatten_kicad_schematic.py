#!/usr/bin/env python3
"""Flatten the four CueTracker sheets onto one A1 root sheet.

KiCad and the MCP server do not currently expose an append/flatten-sheet
operation.  This helper performs only the missing mechanical operation: it
copies complete top-level schematic objects, translates their coordinates,
deduplicates embedded symbol definitions, removes the old sheet objects, and
rewrites imported symbol instance paths to the root sheet.  Electrical edits
after the flatten step are performed through KiCad MCP.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


NUMBER = r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)"
COORD_RE = re.compile(
    rf"(?P<prefix>\((?:at|xy|start|end)\s+)"
    rf"(?P<x>{NUMBER})(?P<space>\s+)(?P<y>{NUMBER})"
)


def matching_paren(text: str, start: int) -> int:
    if text[start] != "(":
        raise ValueError("start is not an opening parenthesis")
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return index + 1
    raise ValueError("unbalanced s-expression")


def top_level_forms(text: str) -> list[str]:
    root_start = text.find("(kicad_sch")
    if root_start < 0:
        raise ValueError("not a KiCad schematic")
    root_end = matching_paren(text, root_start)
    forms: list[str] = []
    depth = 0
    in_string = False
    escaped = False
    start: int | None = None
    for index in range(root_start, root_end):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
            continue
        if char == "(":
            depth += 1
            if depth == 2:
                start = index
        elif char == ")":
            if depth == 2 and start is not None:
                forms.append(text[start : index + 1])
                start = None
            depth -= 1
    return forms


def head(form: str) -> str:
    match = re.match(r"\(\s*([^\s()]+)", form)
    return match.group(1) if match else ""


def root_uuid(forms: list[str]) -> str:
    for form in forms:
        if head(form) == "uuid":
            match = re.search(r'\(uuid\s+"([^"]+)"', form)
            if match:
                return match.group(1)
    raise ValueError("schematic root UUID not found")


def translate(form: str, dx: float, dy: float) -> str:
    def replace(match: re.Match[str]) -> str:
        x = float(match.group("x")) + dx
        y = float(match.group("y")) + dy
        return (
            f'{match.group("prefix")}{x:.6f}'.rstrip("0").rstrip(".")
            + match.group("space")
            + f"{y:.6f}".rstrip("0").rstrip(".")
        )

    return COORD_RE.sub(replace, form)


def nested_forms(container: str) -> list[str]:
    first = container.find("(")
    end = matching_paren(container, first)
    forms: list[str] = []
    depth = 0
    in_string = False
    escaped = False
    start: int | None = None
    for index in range(first, end):
        char = container[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "(":
            depth += 1
            if depth == 2:
                start = index
        elif char == ")":
            if depth == 2 and start is not None:
                forms.append(container[start : index + 1])
                start = None
            depth -= 1
    return forms


def rewrite_instances(symbol: str, root: str, project: str) -> str:
    ref_match = re.search(r'\(property\s+"Reference"\s+"([^"]+)"', symbol)
    unit_match = re.search(r"\(unit\s+(\d+)\)", symbol)
    if not ref_match:
        return symbol
    reference = ref_match.group(1)
    unit = unit_match.group(1) if unit_match else "1"

    instance_start = None
    depth = 0
    in_string = False
    escaped = False
    for index, char in enumerate(symbol):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "(":
            if depth == 1 and symbol.startswith("(instances", index):
                instance_start = index
                break
            depth += 1
        elif char == ")":
            depth -= 1

    replacement = (
        '\t\t(instances\n'
        f'\t\t\t(project "{project}"\n'
        f'\t\t\t\t(path "/{root}"\n'
        f'\t\t\t\t\t(reference "{reference}")\n'
        f'\t\t\t\t\t(unit {unit})\n'
        '\t\t\t\t)\n'
        '\t\t\t)\n'
        '\t\t)'
    )
    if instance_start is not None:
        instance_end = matching_paren(symbol, instance_start)
        return symbol[:instance_start] + replacement + symbol[instance_end:]
    return symbol[:-1] + "\n" + replacement + "\n\t)"


def indent_form(form: str, tabs: int = 1) -> str:
    prefix = "\t" * tabs
    return "\n".join(prefix + line if line else line for line in form.splitlines())


def flatten(root_path: Path, imports: list[tuple[Path, float, float]], output: Path) -> None:
    root_text = root_path.read_text(encoding="utf-8")
    root_forms = top_level_forms(root_text)
    root_id = root_uuid(root_forms)

    root_lib = next(form for form in root_forms if head(form) == "lib_symbols")
    libraries: dict[str, str] = {}
    for symbol_def in nested_forms(root_lib):
        match = re.match(r'\(symbol\s+"([^"]+)"', symbol_def)
        if match:
            libraries.setdefault(match.group(1), symbol_def)

    imported_objects: list[str] = []
    allowed = {
        "junction",
        "no_connect",
        "bus_entry",
        "wire",
        "bus",
        "label",
        "global_label",
        "hierarchical_label",
        "text",
        "text_box",
        "rectangle",
        "polyline",
        "arc",
        "circle",
        "image",
        "symbol",
    }

    for child_path, dx, dy in imports:
        child_forms = top_level_forms(child_path.read_text(encoding="utf-8"))
        child_lib = next(form for form in child_forms if head(form) == "lib_symbols")
        for symbol_def in nested_forms(child_lib):
            match = re.match(r'\(symbol\s+"([^"]+)"', symbol_def)
            if match:
                libraries.setdefault(match.group(1), symbol_def)
        for form in child_forms:
            form_head = head(form)
            if form_head not in allowed:
                continue
            if form_head == "hierarchical_label":
                form = form.replace("(hierarchical_label", "(label", 1)
            moved = translate(form, dx, dy)
            if form_head == "symbol":
                moved = rewrite_instances(moved, root_id, "CueTracker")
            imported_objects.append(moved)

    merged_library = "(lib_symbols\n" + "\n".join(
        indent_form(symbol_def, 2) for symbol_def in libraries.values()
    ) + "\n\t)"

    result_forms: list[str] = []
    for form in root_forms:
        form_head = head(form)
        if form_head == "paper":
            result_forms.append('(paper "A1")')
        elif form_head == "lib_symbols":
            result_forms.append(merged_library)
        elif form_head == "sheet":
            continue
        elif form_head == "sheet_instances":
            continue
        else:
            result_forms.append(form)

    result_forms.extend(imported_objects)
    result_forms.append(
        '(sheet_instances\n'
        f'\t\t(path "/{root_id}"\n'
        '\t\t\t(page "1")\n'
        '\t\t)\n'
        '\t)'
    )

    output.write_text(
        "(kicad_sch\n" + "\n".join(indent_form(form, 1) for form in result_forms) + "\n)\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    project = args.project_dir.resolve()
    flatten(
        project / "CueTracker.kicad_sch",
        [
            # Offsets are exact multiples of the 2.54 mm schematic grid.
            (project / "02_ESP32_Memory_RF.kicad_sch", 302.26, 0.0),
            (project / "03_Motion_Impact_Sensors.kicad_sch", 0.0, 220.98),
            (project / "04_Storage_Optional_IO.kicad_sch", 302.26, 220.98),
        ],
        args.output.resolve(),
    )


if __name__ == "__main__":
    main()
