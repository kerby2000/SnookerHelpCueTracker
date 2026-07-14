#!/usr/bin/env python3
"""Remove point-label and wire objects before MCP-driven schematic rewiring.

This is a deterministic bulk cleanup helper.  It does not modify symbols,
properties, no-connect markers, graphics, or sheet metadata.  The target
netlist is exported before this operation and all new electrical connections
are subsequently created and verified through KiCad MCP.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from flatten_kicad_schematic import head, indent_form, top_level_forms


REMOVE = {"label", "global_label", "hierarchical_label", "wire", "junction"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("schematic", type=Path)
    args = parser.parse_args()
    path = args.schematic.resolve()
    forms = top_level_forms(path.read_text(encoding="utf-8"))
    kept = [form for form in forms if head(form) not in REMOVE]
    path.write_text(
        "(kicad_sch\n" + "\n".join(indent_form(form, 1) for form in kept) + "\n)\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"removed {len(forms) - len(kept)} connectivity objects; kept {len(kept)}")


if __name__ == "__main__":
    main()
