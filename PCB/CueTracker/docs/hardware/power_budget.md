# Cue Tracker R0.3 power tree and current budget

Date: 2026-07-14

Schematic basis: the current saved `CueTracker.kicad_sch` reviewed on 2026-07-14. Recheck this budget and record the release hash after the schematic is frozen.

This is a design budget, not a measured result. Typical/representative figures are deliberately rounded allowances; only figures explicitly identified as data-sheet limits should be treated as such.

## Implemented power tree

`USB-C VBUS -> U7 BQ25611DRTWR 1S buck charger / NVDC power path -> VSYS`

`TUSB320LAIRWBR -> Type-C attach, orientation and advertised-current detection for firmware`

`Raw 1S cylindrical Li-ion cell -> U10 BQ298217RUGR + CSD87313DMS + R44 protection stage -> PACK_P`

`PACK_P -> U14 BQ27427YZFR integrated 7 mOhm coulomb-counter path -> charger BAT / system battery path`

`VSYS -> U5 TPS63802DLAR buck-boost -> +3V3 -> U3 MCU, sensors, audio and logic`

`U3 VDD_SPI output -> U4 W25Q128JVSIQ external flash and the memory I/O domain`

`PACK_P -> U9 TPS22919DCKR switched divider -> ESP32 ADC fallback`

The `Earth` glyph is the project convention for circuit 0 V. `CELL_N_RAW` on the raw-cell side of R44 remains a separate electrical domain; joining it directly to Earth would bypass current sensing/protection. `VDD_SPI` is intentionally sourced by U3's dedicated 3.3 V memory-power output and must not be given an additional +3V3 feed.

## 3.3 V regulator sizing

The retained TPS63802DLAR is a 2 A buck-boost regulator and is appropriately larger than the approximately 200 mA representative active-current target. Espressif requires the ESP32-S3 supply to be capable of at least 500 mA; radio transients make a 200 mA-rated regulator unsuitable even if the long-term average is lower.

| +3V3 load | Representative active/logging allowance | Peak/design allowance | Basis |
|---|---:|---:|---|
| ESP32-S3R8, internal PSRAM and radio | 150 mA | 340 mA | Representative application allowance; 340 mA radio-transmit peak from ESP32-S3 data sheet |
| W25Q128JVSIQ external flash | 5 mA | 25 mA | High-speed read/program/erase allowance |
| LSM6DSV320XTR main-motion IMU | 2 mA | 4 mA | High-rate FIFO allowance |
| IIS3DWB10ISTR impact sensor | 10 mA | 15 mA | Continuous wide-band acquisition allowance |
| BMP581 | 0.5 mA | 2 mA | Conversion allowance |
| MMC5983MA | 1 mA | 5 mA | Measurement plus set/reset allowance |
| TLV320ADC6120IRTER | 15 mA | 20 mA | One active audio channel, clocks and references |
| IM73A135V01 microphone | 0.23 mA | 0.3 mA | Data-sheet-scale microphone allowance |
| TUSB320LAIRWBR | 0.1 mA | 0.1 mA | Conservative sub-milliamp logic allowance |
| WS2812B-2020 | 0 mA | 12 mA | Off in normal logging; one RGB LED full-current allowance |
| Pull-ups, indicators, debug and static overhead | 5 mA | 10 mA | Board-level allowance |
| **Total before margin** | **about 189 mA** | **about 433 mA** | Arithmetic sum; simultaneous peak is a design case |
| **Peak with 25% margin** | - | **about 542 mA** | Regulator, layout and battery-path sizing target |

At 3.0 V cell voltage, 3.3 V / 0.542 A output and an assumed 85% buck-boost efficiency, battery current is approximately:

`I_CELL = (3.3 V * 0.542 A) / (3.0 V * 0.85) = 0.70 A`

The calculated 0.70 A is a discharge case and is below the approximately 1.00 A overcurrent-in-discharge threshold produced by the selected protector and 60 mOhm shunt. The approximately 0.60 A charge-overcurrent threshold is lower, but the charger is intentionally limited to 180 mA. These are nominal threshold calculations; they do not include protector tolerance, shunt tolerance or temperature drift. PCB validation must still cover copper loss, inductor saturation, capacitor DC-bias derating, cell impedance and enclosure temperature.

Primary sources:

- ESP32-S3 data sheet: https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf
- ESP32-S3 hardware design guidance: https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html
- TPS63802 data sheet: https://www.ti.com/lit/ds/symlink/tps63802.pdf
- Coilcraft XFL4015 data sheet, L2 XFL4015-471MEC 470 nH: https://www.coilcraft.com/getmedia/84927b8b-f089-421b-a7f4-a0fa23afe908/xfl4015.pdf

## USB-C input and charging policy

TUSB320LAIRWBR is a Type-C CC controller, not a USB Power Delivery controller and not a charger. In the implemented UFP configuration it can report default, 1.5 A or 3 A Type-C source advertisement. Firmware must use that result to set the BQ25611D input-current limit; the two ICs do not negotiate or configure each other automatically.

The current schematic leaves the U7 BQ25611D D+ and D- pins unused because ESP32 owns USB data. Therefore BQ25611D BC1.2 detection is not available to the charger. R20 pulls `/CHG_CE_N` high so charging is disabled while GPIO3 is reset/high-impedance. Use this conservative firmware sequence on every power-on, charger reset and watchdog reset:

1. Keep GPIO3 high/high-impedance and confirm charging remains disabled.
2. Program 180 mA fast charge, 60 mA precharge, 60 mA termination and 4.190 V regulation.
3. Program `IINDPM` to a source-safe value no greater than 500 mA before trusting source capability.
4. Read the TUSB320LAI attach/current result and raise `IINDPM` only within the advertised Type-C current, connector, cable and thermal limits.
5. Only after all limits have been read back successfully, make GPIO3 an output and drive `/CHG_CE_N` low.
6. Let BQ25611D dynamic power management reduce charge current when the system consumes the available input power.

The requested approximately 200 mA charge rate is not an exact BQ25611D step. `ICHG` uses 60 mA steps, so the conservative setting is **180 mA** (`ICHG[5:0] = 000011`). Do not rely on power-on defaults: the BQ25611D fast-charge reset value is 1020 mA and its IINDPM register reset value is 2400 mA before source detection/host programming. L4 is the specified Eaton MPI4020V2-1R0-R 1 uH charger inductor. The selected cell data sheet, capacity, temperature limits and certification remain authoritative.

Primary sources:

- TUSB320LAI data sheet: https://www.ti.com/lit/ds/symlink/tusb320lai.pdf
- BQ25611D data sheet: https://www.ti.com/lit/ds/symlink/bq25611d.pdf
- Eaton MPI40-V2 data sheet, L4 MPI4020V2-1R0-R 1 uH: https://www.eaton.com/content/dam/eaton/products/electronic-components/resources/data-sheet/eaton-mpi40-v2-miniature-power-inductors-data-sheet.pdf

## Battery, fuel gauge and independent protection

The intended battery is a 1S cylindrical Li-ion assembly: **a pre-tabbed 18650 is the default mechanical choice; a pre-tabbed 21700 is an alternate**. BT1 is an on-board direct-solder interface using two strain-relieved wire pads; it is not a removable battery connector. Solder the pre-welded tabs or qualified pack leads to BT1 and never solder directly to a bare cell can. TH1 remains on the schematic as a two-pad solder-wire interface but is marked DNP for PCBA; a Semitec 103AT-2 remote 10 kOhm NTC is hand-wired after assembly and thermally bonded to the cell. The remote NTC is required unless firmware deliberately enables and validates the BQ25611D `TS_IGNORE` mode. No exact cell MPN has been selected, so capacity, maximum charge voltage, charge-current limit, continuous/pulse discharge current and temperature range remain open manufacturing inputs.

The board protection stage is independent of the charger control:

| Function | Selected threshold | Result with R44 = 60 mOhm |
|---|---:|---:|
| Cell overvoltage | 4.250 V | BQ298217 fixed option |
| Cell undervoltage | 2.600 V | BQ298217 fixed option |
| Overcurrent in charge | -36 mV | about 0.60 A magnitude |
| Overcurrent in discharge | 60 mV | about 1.00 A |
| Short circuit in discharge | 200 mV | about 3.33 A, 250 us-class detection |

R44 is the Vishay Dale WSL2512R0600FEA, 60 mOhm, 1%, 1 W Power Metal Strip shunt. Route U10 BQ298217 Kelvin sense from the `CELL_N_RAW` and Earth sides of R44; no other copper path may bypass it. Q1 is the active TI CSD87313DMS dual common-drain protection MOSFET: TI specifies 100 nA maximum gate leakage, 5.5 mOhm maximum source-to-source on-resistance at 4.5 V and 17 A continuous current at `T_C = 25 C` subject to package/silicon limits. The project footprint is based on TI recommended pattern 4222980/A; CAD-only exposed lands 9 and 10 are S1 and S2. A standard KiCad VSON/NexFET footprint is incompatible.

TI currently marks CSD87313DMS active/production, but the package addendum lists it as **RoHS Exempt**. That is a release-review gate: procurement and regulatory teams must approve the exemption before production. Electrical thresholds do not replace cell qualification, abuse testing or product-level battery certification.

U14 BQ27427YZFR remains the default fuel gauge. Its integrated 7 mOhm sense resistor is rated by TI for 2 A long-term RMS average use; the gauge consumes about 50 uA in NORMAL and 9 uA in SLEEP. U10 BQ298217 adds about 4 uA in NORMAL mode. Charger/buck-boost mode currents and battery self-discharge must be included before using these values for sleep-runtime prediction.

Primary sources:

- BQ27427 data sheet: https://www.ti.com/lit/ds/symlink/bq27427.pdf
- BQ2980/BQ2982 family data sheet and BQ298217 option table: https://www.ti.com/lit/ds/symlink/bq2980.pdf
- CSD87313DMS data sheet, package data and pages 10-11 land pattern: https://www.ti.com/lit/ds/symlink/csd87313dms.pdf
- Vishay WSL Power Metal Strip data sheet: https://www.vishay.com/docs/30100/wsl.pdf
- Semitec AT thermistor data sheet for TH1 103AT-2: https://www.semitec-global.com/uploads/sites/2/2017/03/P11-12_AT_Thermistor.pdf

## Fuel-gauge DNP fallback: switched ESP32 ADC divider

If U14 is not populated, close JP1 so the battery path is not open. JP1 and U14 are mutually exclusive: JP1 must remain open/DNP whenever U14 is fitted, and U14 must be omitted whenever JP1 is closed.

U9 (TPS22919DCKR) switches PACK_P into R23/R24; GPIO14 drives U9 ON directly and R25 = 100 kOhm pulls ON to Earth so the divider stays off during reset. With R23 = 1 MOhm and R24 = 330 kOhm:

`V_ADC = V_BAT * 330k / (1M + 330k)`

`V_BAT = V_ADC * (1M + 330k) / 330k = V_ADC * 4.030303`

At 4.25 V battery voltage the ideal ADC pin voltage is about 1.054 V. C34 = 100 nF gives approximately 24.8 ms using the divider's Thevenin resistance; wait at least **125 ms** after enabling U9 before sampling, then average/calibrate against the ESP32 ADC reference. Disable U9 after measurement. TPS22919 typical quiescent current is about 8 uA when on and typical shutdown current is about 2 nA.

The divider is only a voltage fallback. It cannot reproduce BQ27427 coulomb counting, state-of-charge, state-of-health or aging compensation.

Primary source: https://www.ti.com/lit/ds/symlink/tps22919.pdf

## Release assumptions and required validation

- The approximately 189 mA active figure is a firmware target, not a guaranteed upper bound.
- A specific pre-tabbed 18650 cell, 21700 alternate and tab/lead assembly must be selected before release. TH1 is DNP at PCBA, but the remote Semitec 103AT-2 NTC remains a required hand-wired installation unless a deliberate `TS_IGNORE` product configuration is validated.
- Program charger limits before enabling unattended charging; confirm the watchdog cannot restore unsafe defaults.
- Verify TUSB320 current-mode interpretation with representative USB-C sources and cables.
- Measure VSYS, +3V3 and cell current during radio TX, flash writes, impact capture, audio capture and LED operation.
- Validate charger, protection-FET and sense-resistor temperatures under charge, supplement, overload and short-circuit tests.
- Review the CSD87313DMS RoHS Exempt status, exact DMS land/stencil and the exposed S1/S2 source lands before manufacturing release.
- Schematic ERC does not validate battery certification, PCB copper, switch-node layout, RF behavior, thermal performance or enclosure safety.
