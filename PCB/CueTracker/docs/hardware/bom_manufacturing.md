# Cue Tracker manufacturing BOM notes

Date: 2026-07-15

Status: **GENERATED FROM FINAL HIERARCHY — ENGINEERING BOM**

[`bom_manufacturing.csv`](bom_manufacturing.csv) was regenerated from the final saved hierarchy through KiCad MCP's Python-BOM XML export. It contains 172 component rows and 51 columns, including fitted/DNP state, manufacturer/MPN and sourcing fields where assigned, package, voltage, dielectric, population, variant, assembly and notes metadata. All 62 capacitors retain both `Voltage` and `Dielectric` fields.

This is an engineering BOM, not an authorization to purchase. Generic passives, switches, test points and other commodity lines still require approved orderable MPNs, lifecycle checks and assembly-house substitutions before procurement release.

## Required principal-part contract

The regenerated BOM must include and reconcile at least:

- ESP32-S3-PICO-1-N8R8, 8 MB in-package flash and 8 MB in-package PSRAM.
- Two Hirose FH34SRJ-24S-0.5SH(50), with LCSC C324726, plus the FH34SRJ-8S-0.5SH(50) HMI connector.
- BQ25611D, TPS63802, BQ298217, active CSD87313DMS and WSL2512R0200FEA 20 mOhm shunt.
- TPS25947-class eFuse, ESD441-class VBUS TVS, TPD2E2U06-class CC protection and retained USBLC6-2SC6 data-line protection.
- TUSB320LAI, LSM6DSV320XTR, IIS3DWB10ISTR, BMP581, MMC5983MA, IM73A135V01XTSA1 and TLV320ADC6120IRTER.
- CrossAir CA-C03 as the populated antenna; KH-3216-H0209 remains an unplaced, non-interchangeable evaluation alternative.
- Samsung INR18650-35E as the reference cell documentation item, factory-welded tab/plated-slot interfaces and the DNP TH1 remote-NTC solder pads.

## Mutually exclusive population variants

| Variant | BQ27427 | At-least-3-A bypass | Current rule |
|---|---|---|---|
| `R0_3A` default | DNP | Populate | Battery path designed for at least 3 A normal current and appropriate protection transients |
| `R0_GAUGE_2A` optional | Populate | DNP | Long-term RMS battery-path current limited to 2 A or less |

The two paths must never be fitted together. The switched ESP32 ADC divider remains available as voltage-only fallback.

## Other intentional assembly states

- TH1 is DNP for automated PCBA because it represents solder pads; the remote 10 kOhm NTC is hand-wired and bonded to the cell unless a separately validated `TS_IGNORE` configuration is approved.
- Charger D+/D- terminate only at unused/test pads.
- TLV320ADC6120 channel 2 terminates at test pads or an optional expansion connector.
- The external 32.768 kHz crystal/load network is populated only if the firmware and measured standby/timing results justify it; otherwise it must be a clearly controlled DNP group.

## Generation and procurement gate

The source intermediate is [`CueTracker_bom_intermediate.xml`](../../output/bom/CueTracker_bom_intermediate.xml), generated from the same saved hierarchy used for ERC, netlist, PDF and renders. The CSV is one row per schematic reference so mutually exclusive and hand-assembly states remain explicit. Before procurement, assign exact approved orderable MPNs to every remaining generic line, enforce the `BAT_CURRENT_PATH` variant rule, approve the RTC population decision and validate all manufacturer land patterns and paste apertures.
