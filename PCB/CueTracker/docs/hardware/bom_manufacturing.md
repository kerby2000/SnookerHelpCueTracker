# Cue Tracker manufacturing BOM notes

Date: 2026-07-14

Schematic basis: `CueTracker.kicad_sch`, SHA-256 `BB31FE39BBFECC8338DEB15E1AFD2D0D79964A0BE687B1576747710CBD2F9780`.

[`bom_manufacturing.csv`](bom_manufacturing.csv) is the 149-row population BOM. The final XML netlist contains 153 components; the four intentional DNP entries are listed separately below. Blank manufacturer or MPN fields still require an approved orderable selection before procurement.

## Principal fitted parts

| Ref | Manufacturer | Orderable part | Assigned package / footprint |
|---|---|---|---|
| U1 | Texas Instruments | TUSB320LAIRWBR | RWB0012A X2QFN-12 |
| U2 | STMicroelectronics | USBLC6-2SC6 | SOT-23-6 |
| U3 | Espressif Systems | ESP32-S3R8 | QFN-56-1EP, 7 x 7 mm |
| U4 | Winbond | W25Q128JVSIQ | SOIC-8, 5.3 mm |
| U5 | Texas Instruments | TPS63802DLAR | DLA0010A VSON-HR-10 |
| U6 | Bosch Sensortec | BMP581 | LGA-10, 2 x 2 mm |
| U7 | Texas Instruments | BQ25611DRTWR | RTW0024A WQFN-24 + EP |
| U8 | MEMSIC | MMC5983MA | LGA-16, 3 x 3 mm |
| U9 | Texas Instruments | TPS22919DCKR | DCK0006A SC-70-6 |
| U10 | Texas Instruments | BQ298217RUGR | RUG0008A X2QFN-8 |
| U11 | STMicroelectronics | IIS3DWB10ISTR | Wettable-flank LLGA-16, project footprint |
| U12 | STMicroelectronics | LSM6DSV320XTR | LGA-14, 3 x 2.5 mm |
| U13 | Texas Instruments | TLV320ADC6120IRTER | RTE0020A WQFN-20 + EP |
| U14 | Texas Instruments | BQ27427YZFR | YZF0009 DSBGA-9 |
| Q1 | Texas Instruments | CSD87313DMS | Project TI DMS8 land, 3.3 x 3.3 mm |
| MK1 | Infineon Technologies | IM73A135V01XTSA1 | PG-LLGA-5-2 |
| AE1 | CrossAir | CA-C03 | Project 2.4 GHz ceramic-antenna land |
| Y1 | TXC | 7M-40.000MEEQ-T | 3225, four pad |
| Y2 | Seiko Epson | X1A0001410001 | 32.768 kHz, 3215 |
| J1 | GCT | USB4105-GF-A | Top-mount USB-C receptacle |
| J2 | Harwin | M50-3600542R | 2x5, 1.27 mm vertical SMD header |

## Intentional DNP entries

| Ref | Value / function | Assembly rule |
|---|---|---|
| C12 | 100 nF optional GPIO0 capacitor | Leave open unless boot timing is validated. |
| C57 | 100 nF optional BQ298217 CTR timing capacitor | Leave open while CTR is held low. |
| JP1 | BQ27427 gauge bypass | Leave open with U14 fitted; close only in the gauge-omitted variant. |
| TH1 | Remote 10 kOhm NTC solder pads | No PCBA-installed part. Hand-wire a Semitec 103AT-2 to the pads and bond it to the cell, unless `TS_IGNORE` is deliberately validated. |

## Power-path and fallback parts

| Refs | Function / requirement |
|---|---|
| L2 | Coilcraft XFL4015-471MEC, 470 nH, TPS63802 energy-storage inductor. |
| L4 | Eaton MPI4020V2-1R0-R, 1 uH, BQ25611D charger inductor. |
| R20 | 10 kOhm pull-up on `/CHG_CE_N`; charging remains disabled through MCU reset. |
| R23, R24, C34 | 1 MOhm / 330 kOhm / 100 nF switched ADC divider; `Vpack = Vadc x 4.030303`. |
| R25 | 100 kOhm TPS22919 ON pull-down; divider defaults off. |
| R44 | Vishay WSL2512R0600FEA, 60 mOhm, 1%, 1 W protection-current shunt; Kelvin route. |
| BT1 | Direct solder-wire pads for a pre-tabbed 1S 18650 cell or mechanically qualified 21700 alternative. |

## Capacitor procurement metadata

- All 59 capacitors carry non-empty `Voltage` and `Dielectric` properties.
- Displayed values contain capacitance only; dielectric and voltage are hidden BOM properties.
- The metadata is a minimum electrical requirement, not an approved MPN. Confirm effective capacitance after DC bias, tolerance, temperature range, package, ripple current and lifecycle before release.
- Crystal load capacitors use C0G/NP0. Bulk and decoupling ceramics use the documented X5R/X7R requirements.

## Population alternatives

- AE1 CA-C03 is the current antenna. KH-3216-H0209 is not placed and is not a drop-in alternative; it needs its own footprint, keepout and RF tuning.
- U14 BQ27427 is fitted by default and JP1 remains open. If U14 is omitted, close JP1 and use the U9 switched-divider path for voltage-only estimation.
- TH1's DNP status means “no board-installed thermistor or connector,” not “temperature sensing is unnecessary.”

## Release blockers

1. Approve exact MPNs for generic passives, LEDs, switches and test hardware.
2. Qualify the exact pre-tabbed cell, wiring, strain relief, remote NTC placement and charge limits.
3. Verify all custom land patterns against manufacturer drawings, especially IIS3DWB10ISTR, CSD87313DMS, fine-pitch TI packages and CA-C03.
4. Validate effective input/output capacitance, switching-loop layout, shunt/FET heating and protection thresholds on hardware.
5. Regenerate the BOM whenever the saved schematic hash changes.
