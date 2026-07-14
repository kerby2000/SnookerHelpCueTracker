# Cue Tracker R0.3 power tree and current budget

Date: 2026-07-15

Schematic basis: the hierarchical Cue Tracker redesign with `rear_main.kicad_sch` and `front_sensor.kicad_sch`. Recheck this budget and record the release hash after the schematic, PCB stack-up and display daughterboard are frozen.

This is a design budget, not a measured result. Typical/representative figures are deliberately rounded allowances; only figures explicitly identified as data-sheet limits should be treated as such.

## Release power tree

`USB-C VBUS -> connector-adjacent ESD441-class TVS -> TPS259470A-class 3 A eFuse/current limiter -> VBUS_PROTECTED -> BQ25611D 1S buck charger/NVDC power path -> VSYS`

`TUSB320LAI -> Type-C attach, orientation and advertised-current detection for firmware`

`1S Samsung INR18650-35E reference cell -> BQ298217 + CSD87313DMS + 20 mOhm Kelvin shunt -> PACK_P`

`PACK_P -> one of two mutually exclusive assembly paths -> charger BAT/system battery path`

- Default 3 A build: 3 A-rated gauge-bypass link fitted and BQ27427 DNP.
- Optional gauge build: BQ27427 fitted and bypass link open; long-term RMS battery-path current is limited to 2 A by the gauge's integrated sense-resistor rating.

`VSYS -> TPS63802 buck-boost -> +3V3 -> ESP32-S3-PICO-1-N8R8, logic and switched peripheral rails`

`+3V3 on rear -> R62 0-ohm naming link -> +3V3_SENSOR across the 24-pin FPC -> front TPS22919/load switch -> +3V3_SENSOR_SW -> front sensors`

`+3V3 -> HMI load switch -> +3V3_HMI -> display daughterboard`

`PACK_P -> TPS22919 switched divider -> ESP32 ADC voltage fallback`

The ESP32-S3-PICO-1-N8R8 contains the 8 MB Quad-SPI flash, 8 MB Octal-SPI PSRAM, 40 MHz crystal and SiP RF matching. There is no external W25Q128 or external 40 MHz crystal load in this power budget. The SiP's `VDD_SPI` and in-package memory pins are not board-level load rails.

The `Earth` glyph is the project convention for circuit 0 V. `CELL_N_RAW` on the raw-cell side of the protector shunt remains a separate electrical domain; joining it directly to Earth would bypass current sensing and independent protection.

## 3.3 V regulator sizing

The retained TPS63802 is a 2 A buck-boost regulator and is appropriately larger than the approximately 200 mA representative active/logging target. Espressif recommends a source capable of at least 500 mA for a single ESP32-S3-PICO-1 supply. Radio transients make a 200 mA-rated regulator unsuitable even when the long-term average is lower.

| System load | Representative active/logging allowance | Peak/design allowance | Basis |
|---|---:|---:|---|
| ESP32-S3-PICO-1-N8R8, including in-package flash and PSRAM | 150 mA | 340 mA | Representative application allowance; validate with final RF firmware and memory traffic |
| LSM6DSV320XTR main-motion IMU | 2 mA | 4 mA | High-rate FIFO allowance |
| IIS3DWB10ISTR impact sensor | 10 mA | 15 mA | Continuous wide-band acquisition allowance |
| BMP581 | 0.5 mA | 2 mA | Conversion allowance |
| MMC5983MA | 1 mA | 5 mA | Measurement plus set/reset allowance |
| TLV320ADC6120IRTER | 15 mA | 20 mA | One active audio channel, clocks and references |
| IM73A135V01 microphone | 0.23 mA | 0.3 mA | Data-sheet-scale microphone allowance |
| TUSB320LAI and low-power control logic | 0.2 mA | 0.5 mA | Conservative sub-milliamp allowance; eFuse input current is on VBUS, not +3V3 |
| ST7789 daughterboard logic and backlight | 0 mA | 70 mA provisional | Peak budget applies outside capture; replace with measured panel/backlight maximum before release |
| Pull-ups, indicators, debug and static overhead | 5 mA | 10 mA | Board-level allowance |
| **Total before margin** | **about 184 mA** | **about 467 mA** | Arithmetic sum; simultaneous peak is a design case |
| **Peak with 25% margin** | - | **about 584 mA** | Regulator, layout and battery-path sizing target |

At 3.0 V cell voltage, 3.3 V / 0.584 A output and an assumed 85% buck-boost efficiency, battery current is approximately:

`I_CELL = (3.3 V * 0.584 A) / (3.0 V * 0.85) = 0.76 A`

The calculated 0.76 A representative peak is below the nominal 3.0 A protector discharge-overcurrent threshold. The 3 A path rating is nevertheless mandatory because the battery, charger, protection and transient cases are not bounded by the representative +3V3 load alone. PCB validation must cover copper loss, plated-slot/tab current, connector current, inductor saturation, capacitor DC-bias derating, cell impedance and enclosure temperature.

Primary sources:

- ESP32-S3-PICO-1 data sheet: https://documentation.espressif.com/esp32-s3-pico-1_datasheet_en.pdf
- ESP32-S3 hardware design guidance: https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html
- TPS63802 data sheet: https://www.ti.com/lit/ds/symlink/tps63802.pdf
- Coilcraft XFL4015 data sheet, TPS63802 L2 XFL4015-471MEC 470 nH: https://www.coilcraft.com/getmedia/84927b8b-f089-421b-a7f4-a0fa23afe908/xfl4015.pdf

## USB-C input protection and charging policy

The USB-C receptacle, all paralleled VBUS contacts, vias and VBUS copper are designed for at least 3 A. There is no 500 mA PPTC in the release architecture and no firmware or documentation may assume that a PPTC limits the input to 500 mA.

The input-protection order is intentional:

1. Place the ESD441-class 5 V TVS beside the receptacle with the shortest possible discharge path to Earth.
2. Route VBUS through the TPS259470A-class eFuse/current limiter before the charger. A 1.10 kOhm, 1% `RILM` targets approximately 3.0 A nominal by TI's programming relation. Confirm the exact installed variant, tolerance, dV/dt network, fault response and thermal behavior against the release BOM.
3. Use TPD2E2U06-class low-capacitance two-channel ESD protection on CC1 and CC2, adjacent to the connector.
4. Retain low-capacitance USB D+/D- ESD protection and ESP32 ownership of the USB data pair.
5. Provide a level-safe direct `VBUS_PRESENT` indication to the MCU. This sense is independent of TUSB320 attach/status reporting.

TUSB320LAI is a Type-C CC controller, not a USB Power Delivery controller and not a charger. In the UFP configuration it can report default, 1.5 A or 3 A source advertisement. Firmware must use that result to choose a source-safe BQ25611D input-current limit; the eFuse rating does not grant permission to draw more current than the source advertises.

The BQ25611D D+ and D- pins are isolated from the USB-C data pair and go only to unused/test pads. Consequently, charger BC1.2 detection is unavailable. Native USB D+/D- remain connected only to the ESP32-S3-PICO-1.

### Reset-safe charger firmware contract

The BQ25611D data-sheet reset values enable charge (`CHG_CONFIG = 1`) and set fast charge to 1020 mA, so the board must not rely on register reset values. A hardware CE bias must keep charging disabled while the MCU is reset or high-impedance. On every power-on, charger reset and watchdog recovery, firmware must:

1. Keep hardware CE inactive/high and write `CHG_CONFIG = 0` first.
2. Write `BST_CONFIG = 0`; OTG/boost operation is not supported for R0.
3. Program a source-safe `IINDPM`, cell voltage limit and the charge-current profile, then read them back.
4. Use **960 mA** (`ICHG = 010000`) as the exact BQ25611D step implementing the **1.0 A normal R0 policy**.
5. Permit **1500 mA maximum** (`ICHG = 011001`) only in an explicitly enabled build after cell, tab, PCB, charger and enclosure thermal validation.
6. Set 4.20 V regulation for the Samsung INR18650-35E reference cell, and validate precharge, termination, NTC and safety-timer settings separately.
7. Enable charging only after the source advertisement and all programmed limits are known safe. Keep `BST_CONFIG = 0` throughout normal operation.

Primary sources:

- TUSB320LAI data sheet: https://www.ti.com/lit/ds/symlink/tusb320lai.pdf
- BQ25611D data sheet: https://www.ti.com/lit/ds/symlink/bq25611d.pdf
- TPS25947 data sheet: https://www.ti.com/lit/ds/symlink/tps25947.pdf
- ESD441 data sheet: https://www.ti.com/lit/ds/symlink/esd441.pdf
- TPD2E2U06 data sheet: https://www.ti.com/lit/ds/symlink/tpd2e2u06.pdf
- Eaton MPI40-V2 data sheet, charger L4 MPI4020V2-1R0-R 1 uH: https://www.eaton.com/content/dam/eaton/products/electronic-components/resources/data-sheet/eaton-mpi40-v2-miniature-power-inductors-data-sheet.pdf

## Battery, independent protection and high-current paths

The reference cell is **Samsung INR18650-35E**, a 1S cylindrical 18650 cell specified at 3.6 V nominal and 3350 mAh minimum. Its product specification gives 4.20 V charge termination, 1.7 A standard charge, 2.0 A maximum charge and 8 A maximum continuous discharge. The R0 product policy is deliberately more conservative at 960 mA normal charge and 1.5 A maximum only after thermal validation.

Mechanical/electrical assembly contract:

- Use a cell with factory-welded tabs; never solder directly to a bare cell can.
- Solder the battery tabs to plated PCB slots sized for the tab material and 3 A normal design current.
- Retain the cell mechanically with an insulated cradle and strain relief; solder joints do not retain the cell.
- TH1 represents remote 10 kOhm NTC solder pads and is DNP for automated PCBA. Hand-wire the qualified NTC and thermally bond it to the cell unless a deliberate and validated `TS_IGNORE` product configuration is used.

The BQ298217/CSD87313DMS stage is independent of charger firmware:

| Function | Selected nominal threshold | Result with R44 = 20 mOhm |
|---|---:|---:|
| Cell overvoltage | 4.250 V | BQ298217 fixed option |
| Cell undervoltage | 2.600 V | BQ298217 fixed option |
| Overcurrent in charge | -36 mV | about 1.8 A magnitude |
| Overcurrent in discharge | 60 mV | about 3.0 A |
| Short circuit in discharge | 200 mV | about 10 A, 250 us-class detection |

R44 is the Vishay Dale **WSL2512R0200FEA**, 20 mOhm, 1%, 1 W, 2512-class Power Metal Strip shunt. Route BQ298217 Kelvin sense independently from the two R44 termination pads; do not share the sense traces with high-current copper and do not provide any copper path that bypasses R44. The figures above are nominal `V / R` results, not guaranteed trip currents. Protector threshold tolerance, shunt tolerance, temperature coefficient, FET behavior and PCB parasitics require validation.

All series elements from the USB-C VBUS contacts through the eFuse/charger, and from the cell tabs through the protector FETs, R44, gauge selector/bypass and system return, must be rated for at least **3 A normal design current** and for fault transients appropriate to the protector's approximately 10 A short-circuit threshold. This is a PCB/component rating requirement, not permission for firmware to charge at 3 A.

Primary sources:

- Samsung INR18650-35E product specification (manufacturer document mirror): https://www.18650.rs/uploads/samsung-35e.pdf
- BQ2980/BQ2982 family data sheet and BQ298217 option table: https://www.ti.com/lit/ds/symlink/bq2980.pdf
- CSD87313DMS data sheet and recommended land pattern: https://www.ti.com/lit/ds/symlink/csd87313dms.pdf
- Vishay WSL Power Metal Strip data sheet: https://www.vishay.com/docs/30100/wsl.pdf
- Semitec AT thermistor data sheet for TH1 103AT-2: https://www.semitec-global.com/uploads/sites/2/2017/03/P11-12_AT_Thermistor.pdf

## Fuel-gauge variants and switched ADC fallback

BQ27427 contains an approximately 7 mOhm integrated sense resistor. TI recommends no more than **2 A long-term RMS average utilization**, even though short-duration peak ratings are higher. It therefore cannot be series-connected in a build advertised for 3 A normal battery-path current.

Use mutually exclusive assembly variants:

| Assembly variant | BQ27427 | 3 A-rated bypass | Allowed long-term battery-path current | State-of-charge method |
|---|---|---|---:|---|
| `R0_3A` default | DNP | Fitted | 3 A board design current | Switched ESP32 ADC battery voltage; firmware estimation only |
| `R0_GAUGE_2A` optional | Fitted | Open/DNP | 2 A RMS maximum | BQ27427 coulomb counting / Impedance Track |

The bypass and BQ27427 must never be fitted together. The bypass is a production assembly option, not an emergency jumper, and its land/part/copper must be rated for 3 A plus applicable protector transients. A default-populated gauge in a 3 A build requires a different external-shunt fuel-gauge architecture.

TPS22919 switches PACK_P into the ADC divider. With R23 = 1 MOhm, R24 = 330 kOhm and C34 = 100 nF:

`V_ADC = V_BAT * 330k / (1M + 330k)`

`V_BAT = V_ADC * (1M + 330k) / 330k = V_ADC * 4.030303`

At 4.25 V battery voltage the ideal ADC pin voltage is about 1.054 V. The divider Thevenin resistance gives an approximately 24.8 ms RC constant; wait at least 125 ms after enabling the switch before sampling, then average and calibrate against the ESP32 ADC reference. Disable the divider after measurement.

This fallback measures voltage only. It does not reproduce BQ27427 coulomb counting, state-of-charge, state-of-health or aging compensation.

Primary sources:

- BQ27427 data sheet: https://www.ti.com/lit/ds/symlink/bq27427.pdf
- TPS22919 data sheet: https://www.ti.com/lit/ds/symlink/tps22919.pdf

## Release assumptions and required validation

- The approximately 184 mA active figure is a firmware target, not a guaranteed upper bound.
- Replace the provisional 70 mA display/backlight allowance with a measurement from the selected daughterboard; firmware must issue no display transaction and make no backlight/HMI-state change during `ARMED` and `SHOT_CAPTURE`.
- Confirm the exact Samsung INR18650-35E tabbed-cell supplier, authentic cell traceability, tab alloy/thickness, insulation, cradle, strain relief and approved assembly drawing.
- Program charger limits before enabling unattended charging; prove that reset and watchdog paths cannot restore unsafe charge defaults.
- Verify TUSB320 current-mode interpretation with representative USB-C sources and cables; the 3 A eFuse does not supersede source advertisement.
- Measure VSYS, +3V3 and cell current during radio TX, SiP flash writes, impact capture, audio capture, display operation and indicator operation.
- Validate charger, eFuse, protection FET, shunt, tab/slot and PCB temperatures under charging, supplement, overload and short-circuit tests.
- Review the CSD87313DMS material declaration, exact DMS land/stencil and exposed S1/S2 source lands before manufacturing release.
- Schematic ERC does not validate battery certification, PCB copper, switch-node layout, RF behavior, thermal performance, ESD current return or enclosure safety.
