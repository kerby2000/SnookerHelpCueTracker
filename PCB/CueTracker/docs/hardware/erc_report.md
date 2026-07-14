# Cue Tracker final ERC and integrity report

Date: 2026-07-14

Schematic: `CueTracker.kicad_sch`  
Saved SHA-256: `BB31FE39BBFECC8338DEB15E1AFD2D0D79964A0BE687B1576747710CBD2F9780`  
Toolchain: KiCad 10.0.4 through KiCad MCP, followed by the read-only `kicad-schematic-audit` saved-file checker.

## Result

- KiCad MCP close, reopen and ERC: **0 errors, 0 warnings**.
- Independent saved-file ERC: **0 errors, 0 warnings, 0 findings**.
- One logical sheet, 153 netlist components and 137 electrical nets.
- 123 local labels; no global or hierarchical labels.
- 80 Earth symbols; no GND symbols.
- 45 `R_Small`, 59 `C_Small`, and no legacy `Device:R` or `Device:C` symbols.
- All 59 capacitors have populated `Voltage` and `Dielectric` fields.

The project policy ignores `single_global_label`, `four_way_junction`, `simulation_model_issue` and `footprint_filter`. The final ERC JSON contains no error or warning violation under that saved policy. The standalone auditor independently reports balanced KiCad syntax, portable library tables and no convention findings.

## Critical electrical readback

| Function | Verified result |
|---|---|
| Shared power alert | `POWER_ALERT_N` endpoints are R18/2, U7/7, U3/36, U1/6 and U14/A1. The accidental `/PWR_ALRT` split is removed. |
| Impact sensor | U11 is `CueTracker_Exact:IIS3DWB10ISTR`; pins 11/12 are on `+3V3`, and pins 1/5/10/14/15/16 are on Earth. |
| Protection FET | Q1 is `CueTracker_Exact:CSD87313DMS` with the project DMS8 footprint. |
| Current shunt | `CELL_N_RAW -> R44 60 mOhm -> Earth`; U10 VSS and CS sense opposite sides of the shunt. |
| Charger | U7 VBUS/VAC = `VBUS`, BAT = `CHG_BAT`, BATSNS = `PACK_P`, SYS = `VSYS`, and CE = `/CHG_CE_N`. R20 holds CE high during reset. |
| Gauge / bypass | U14 is fitted in the protected positive path; JP1 is the mutually exclusive open DNP bypass. |
| ADC fallback | GPIO14 drives U9 TPS22919; GPIO1 senses the 1 MOhm / 330 kOhm / 100 nF divider from protected `PACK_P`. |
| Memory rail | U3 sources `VDD_SPI` for U4 W25Q128JVSIQ and the memory I/O domain; it is not separately fed from `+3V3`. |
| Debug | J2 is the M50-3600542R 2x5 1.27 mm vertical SMD header. |
| Remote NTC | TH1 retains solder-wire pads and is DNP at PCBA; its remote 103AT-2 is installed by wiring after assembly. |

## PWR_FLAG review

Nine flags remain, each on an electrically distinct domain whose physical source is hidden from ERC by passive/connector/library pin types:

| Flag | Net | Reason |
|---|---|---|
| `#FLG01` | `VBUS` | External USB source enters through passive connector pins. |
| `#FLG02` | `VDD_SPI` | ESP32-S3 pin operates as the flash-supply output in this design, while the symbol pin type cannot express that mode. |
| `#FLG03` | `Earth` | One annotation for the common system-return domain. |
| `#FLG04` | `+3V3_RF` | L1 creates a distinct filtered net after the regulator output. |
| `#FLG05` | `+3V3_AUDIO` | FB1 creates a distinct filtered net after the regulator output. |
| `#FLG06` | `Net-(U10-VDD)` | Cell positive reaches U10 VDD through passive R30. |
| `#FLG07` | `CELL_N_RAW` | Raw cell negative enters through passive battery pads and is intentionally isolated from Earth by R44. |
| `#FLG08` | `PACK_P` | The protected rail is sourced through passive battery/FET pins. |
| `#FLG09` | `CHG_BAT` | This separate charger/gauge rail has no symbol pin typed as a power output. |

No extra flag is present on `+3V3`, `VSYS`, `REGN` or raw cell positive. See [`power_flag_contract.md`](power_flag_contract.md) for the review rule.

## Library and visual verification

- `sym-lib-table` registers only `${KIPRJMOD}/CueTracker_Exact.kicad_sym`.
- `CueTracker_Exact.kicad_sym` is writable and contains both exact symbols.
- The project was saved, closed, reopened through MCP, checked, and closed saved again.
- The final PDF was rendered as one A3 landscape page and inspected at full-page and block-crop scale. C16 and C58 use left-side fields to avoid collisions; the remaining compact audio area is dense but has no glyph overlap or clipping.

## Artifact hashes

| Artifact | SHA-256 |
|---|---|
| `CueTracker.kicad_sch` | `BB31FE39BBFECC8338DEB15E1AFD2D0D79964A0BE687B1576747710CBD2F9780` |
| `CueTracker_Exact.kicad_sym` | `13B09128908EBD629BE6D29E9B19520481E2E3E32C9144860FCCB6231EF39EEA` |
| `CueTracker_final_ERC.json` | `8B4A2FECA38C612314360E65DAE8F07B36A68CFDADF76BE5894C0DFF0CF9A8E6` |
| `CueTracker_final_netlist.xml` | `3E5CDD77B78F896787E3E126CB8C096D160EFD3A7AD41E8F4AEC1A59CA945B56` |
| `CueTracker_final.svg` | `60A3E686C47EF6F232067AA0CDE08BBA7BD0E072A7D9F8C540DA4868C8D32660` |
| `bom_manufacturing.csv` | `75A5369F4DDFCB630D76FFADB1383CDE30CF2BBC52CBADD837B9A611286EE7F6` |
| `CueTracker_schematic_final.pdf` | `5DCB5AB4A30B812E3702781374BD10A8079632A00A2EA03B595432B7CC2D08C7` |
