# Cue Tracker one-sheet hardware handoff

Date: 2026-07-14

The authoritative design is [`CueTracker.kicad_sch`](../../CueTracker.kicad_sch). The final saved schematic SHA-256 is `BB31FE39BBFECC8338DEB15E1AFD2D0D79964A0BE687B1576747710CBD2F9780`.

## Verified state

- One A3 landscape sheet; all functional blocks are inside the frame.
- KiCad MCP close/reopen verification: 0 ERC errors and 0 warnings.
- Independent saved-file audit with KiCad 10.0.4: 0 findings and 0 ERC violations.
- MCP netlist: 153 components and 137 electrical nets.
- 123 ordinary local labels; no global or hierarchical labels.
- 80 Earth symbols and no GND symbols.
- 45/45 resistors use `Device:R_Small`; 59/59 capacitors use `Device:C_Small`.
- Every capacitor has non-empty `Voltage` and `Dielectric` properties; displayed values remain value-only.

## Drawing contract implemented

- Use wires within a logical block and ordinary local labels between blocks.
- Preserve the user's block placement; do not globally reflow or autoplace the sheet.
- Place supply symbols above loads and Earth returns below them where practical.
- Resistors use a 40 mil reference centered in the body and a 40 mil value outside the body. Both fields follow the resistor direction.
- Capacitor references are above and values below the symbol with a nominal 50 mil offset. C16 and C58 are intentionally placed on the left side because the right-side position collided with nearby text.
- I2C address comments are present beside TUSB320LAI (`0x47`), BMP581 (`0x46`), BQ25611D (`0x6B`), MMC5983MA (`0x30`), TLV320ADC6120 (`0x4E`) and BQ27427 (`0x55`).

## Power and assembly decisions

- The nine justified ERC annotations and their physical source paths are documented in [`power_flag_contract.md`](power_flag_contract.md). No flags are placed on `+3V3`, `VSYS`, `REGN` or raw cell positive.
- U9 TPS22919 gates the 1 MOhm / 330 kOhm battery-voltage divider. It removes the divider's continuous drain when disabled and discharges the ADC node through QOD; it is not a regulator or charger.
- J2 is the Harwin M50-3600542R 2x5, 1.27 mm vertical SMD JTAG/recovery header.
- TH1 is a two-pad solder-wire interface, marked DNP for PCBA. A remote Semitec 103AT-2 10 kOhm NTC is hand-wired and bonded to the cell unless firmware deliberately validates `TS_IGNORE` operation.
- The populated antenna is AE1, CrossAir CA-C03. KH-3216-H0209 remains an evaluated but unplaced alternative; it is not footprint-interchangeable with CA-C03.

## Project symbol library

- [`CueTracker_Exact.kicad_sym`](../../CueTracker_Exact.kicad_sym) is the only project library registered by `sym-lib-table` and is the source of truth.
- The file is writable and contains both `IIS3DWB10ISTR` and `CSD87313DMS`. The placed IIS3DWB10ISTR cache entry was refreshed and its wiring was repaired through KiCad MCP.
- `cust_sym.kicad_sym` and `BQ27427YZFR.kicad_sym` remain unregistered reference files. Editing them will not update placed project symbols.
- F5 redraws the editor; it does not reload a placed symbol from its library. After editing the registered library, use **Update Symbols from Library** for the selected reference. If the Symbol Editor reverts or hides CSD87313DMS, close every KiCad editor and the KiCad Manager, then reopen `CueTracker.kicad_pro` to clear the long-lived library cache.

## Final artifacts

| Artifact | Path | SHA-256 |
|---|---|---|
| ERC JSON | [`final_20260714/CueTracker_final_ERC.json`](final_20260714/CueTracker_final_ERC.json) | `8B4A2FECA38C612314360E65DAE8F07B36A68CFDADF76BE5894C0DFF0CF9A8E6` |
| XML netlist | [`final_20260714/CueTracker_final_netlist.xml`](final_20260714/CueTracker_final_netlist.xml) | `3E5CDD77B78F896787E3E126CB8C096D160EFD3A7AD41E8F4AEC1A59CA945B56` |
| SVG render | [`final_20260714/CueTracker_final.svg`](final_20260714/CueTracker_final.svg) | `60A3E686C47EF6F232067AA0CDE08BBA7BD0E072A7D9F8C540DA4868C8D32660` |
| Manufacturing BOM CSV | [`bom_manufacturing.csv`](bom_manufacturing.csv) | `75A5369F4DDFCB630D76FFADB1383CDE30CF2BBC52CBADD837B9A611286EE7F6` |
| Review PDF | [`CueTracker_schematic_final.pdf`](../../../../output/pdf/CueTracker_schematic_final.pdf) | `5DCB5AB4A30B812E3702781374BD10A8079632A00A2EA03B595432B7CC2D08C7` |

The preservation checkpoint for this exact visually verified revision is [`CueTracker_snapshot_stepfinal_visual_verified_final_visual_verified_20260714_115438`](../../snapshots/CueTracker_snapshot_stepfinal_visual_verified_final_visual_verified_20260714_115438/).

## Remaining PCB-stage gates

ERC proves logical consistency, not PCB performance. Before release, verify the TPS63802 and BQ25611D high-current layouts and effective ceramic capacitance, CSD87313DMS/shunt Kelvin routing and thermal behavior, RF impedance/matching/antenna keepout in the final enclosure, crystal loading, MEMS orientation and land patterns, cell/NTC limits, and audio/RF noise on assembled hardware.
