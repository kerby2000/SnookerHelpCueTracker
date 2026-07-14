# Cue Tracker one-sheet schematic decision log

Date: 2026-07-14

This log records the intended implementation of the current single-sheet design. Starting component values still require PCB-stage validation where noted.

| Decision | Selected implementation | Reason / status |
|---|---|---|
| MCU | U3 ESP32-S3R8 bare QFN56 | Provides the required 8 MB in-package octal PSRAM; no module is used |
| Application flash | U4 W25Q128JVSIQ, SOIC-8, 16 MB QSPI | External application storage on the ESP32-S3 dedicated flash interface. U3's dedicated 3.3 V `VDD_SPI` output supplies U4 and the memory I/O domain; no separate +3V3 feed is required or intended |
| Main 3.3 V regulator | U5 TPS63802DLAR | True buck-boost operation over a 1S LiPo discharge curve; TI specifies 2 A at 3.3 V for input at or above 2.3 V |
| System-current policy | At least 500 mA rail capability; approximately 200 mA average target | Espressif requires a supply capable of at least 500 mA and lists radio peaks up to about 340 mA. The 200 mA figure is an operating/firmware target, not a regulator limit |
| USB-C source detection | TUSB320LAIRWBR in fixed-UFP/I2C mode | Reports Type-C attachment, orientation and advertised default/1.5 A/3 A current. It is not USB PD and does not configure the charger automatically |
| Charger and power path | U7 BQ25611DRTWR switch-mode 1S charger with NVDC power path | Provides the required higher-efficiency charger/system path while ESP32 retains the native USB data pair; the charger's D+/D- detector is intentionally unused |
| Charger fail-safe and settings | R20 pulls `/CHG_CE_N` high; firmware programs U7 for ICHG 180 mA, precharge 60 mA, termination 60 mA, VREG 4.190 V and source-safe IINDPM before GPIO3 drives CE low | Charging stays disabled through ESP32 reset/high-impedance. Reset register values are not accepted as a safe operating configuration; current advertisement is read from TUSB320LAI before any IINDPM increase |
| Fuel gauge and voltage fallback | U14 BQ27427YZFR populated by default; JP1 is a mutually exclusive DNP bypass | Provides coulomb counting through its integrated 7 mOhm sense path. If U14 is omitted, close JP1 and use U9 TPS22919 with R25 100 kOhm ON pull-down, R23/R24 and C34 as a voltage-only ESP32 ADC fallback; never populate U14 and close JP1 together |
| Independent battery protection | U10 BQ298217RUGR + CSD87313DMS + R44 WSL2512R0600FEA 60 mOhm, 1%, 1 W | Fixed 4.250 V OVP / 2.600 V UVP and nominal 0.60 A charge, 1.00 A discharge and 3.33 A short-current thresholds. The selected TI FET is active/production and meets the low-leakage requirement |
| Protection-FET land and compliance | Project-specific `TI_CSD87313DMS_DMS8_3.3x3.3mm` footprint; RoHS review required | TI pages 10-11/recommended pattern 4222980/A define the DMS land. CAD-only exposed lands 9/10 are S1/S2; a standard KiCad VSON footprint is incompatible. TI lists the part RoHS Exempt despite active/production lifecycle |
| Cell and temperature connection | Pre-tabbed 18650 default, pre-tabbed 21700 alternate; BT1 cell pads and DNP-at-PCBA TH1 NTC pads | There is no removable battery connector. BT1 accepts the pre-welded cell/pack leads. TH1 remains as solder pads for a remote Semitec 103AT-2 10 kOhm NTC that is hand-wired and thermally bonded to the cell after PCBA; it is required unless a deliberate, validated `TS_IGNORE` configuration is used. Never solder directly to the cell can |
| Power inductors | L2 Coilcraft XFL4015-471MEC 470 nH for TPS63802; L4 Eaton MPI4020V2-1R0-R 1 uH for BQ25611D | Keeps the live schematic references and exact manufacturer footprints; L2 and L4 are not interchangeable |
| Main crystal | TXC 7M-40.000MEEQ-T | Exact 40 MHz candidate. Procurement must confirm the suffix/load-capacitance configuration, and load capacitors remain board-tuning values |
| RF supply rail | `+3V3 -> 2.2 nH -> +3V3_RF`, with 10 uF plus 100 nF after the inductor | `+3V3_RF` is reserved for ESP32-S3 VDD3P3 pins 2/3. Espressif calls for an LC-fed analog/RF supply and warns of TX current steps; it is not an antenna-feed or general sensor rail |
| Primary antenna | AE1 CrossAir CA-C03 placed as the populated baseline | The 5.5 x 2.0 x 1.0 mm 2.4 GHz ceramic antenna has its project symbol and footprint assigned. Board-edge keepout and final matching still require validation against the production stack-up and enclosure |
| Evaluated antenna alternative | Kinghelm KH-3216-H0209 evaluation only; no placed schematic part | The smaller 3.23 x 1.66 x 0.45 mm PIFA/single-feed part has a different footprint, clearance and matching reference from CA-C03 and is not a drop-in substitute. It is not a current DNP component because no alternate antenna is placed |
| RF matching | Espressif chip-side C-L-C reserve plus antenna-side pi provision | All values are starting values marked TUNE; final values require the actual PCB, battery, cue enclosure, VNA and OTA measurements |
| USB | Native ESP32-S3 USB with 22 Ohm series resistors and one low-capacitance PESD5V0Y1BCSF per data line | Preserves ROM download and USB Serial/JTAG without a USB-UART bridge |
| Main motion IMU | U12 LSM6DSV320XTR | Replaces the incorrect LSM6DSL; complete local supply and interface support is populated |
| Impact sensor | U11 IIS3DWB10ISTR, 16-lead wettable-flank LLGA | Preserves continuous high-bandwidth vibration capture; the land pattern must be checked against ST package geometry and official reference CAD before production |
| Environmental and magnetic sensors | U6 BMP581 and U8 MMC5983MA populated | Both are complete default-fit I2C blocks with their required local decoupling/support components |
| Microphone and ADC | IM73A135V01 plus U13 TLV320ADC6120IRTER | Complete differential analog path: C51 100 nF and C52 1 uF support MICBIAS, while C55/C59 and R39/R43 provide the differential coupling into U13. I2C control and I2S output are retained; no separate op-amp or MCU ADC is required |
| Debug connector | J2 Harwin M50-3600542R, 2x5 1.27 mm vertical SMD header | Retains direct recovery and firmware-debug access in an assembly-compatible SMD format; native USB remains the primary programming path and GPIO43/44 are used by sensor interrupts |
| Ground symbol convention | `Earth` symbol used for the circuit return at the user's request | Electrically this is battery negative/system 0 V. The design has no protective-earth connection; PCB and safety documentation must not treat it as PE or chassis earth |

## PCB/mechanical validation items

1. Verify TPS63802 switching-loop layout, effective ceramic capacitance, thermal rise and 3.3 V droop during maximum ESP32-S3 radio activity with all acquisition blocks running.
2. Measure the `+3V3_RF` rail at ESP32-S3 VDD3P3 pins 2/3 and confirm the post-inductor 10 uF plus 100 nF placement.
3. Confirm the selected pre-tabbed 18650/21700 pulse capability, BT1 wire/pad rating and BQ25611D supplement behavior at cold temperature and near end of discharge.
4. Validate the 180 mA fast-charge, 60 mA precharge/termination, 4.190 V regulation, IINDPM, NTC thresholds, CE-reset state and watchdog policy against the final cell data sheet.
5. Verify the placed AE1 CA-C03 land, board-edge keepout and feed geometry before PCB release. KH-3216-H0209 remains an evaluated alternative only, not a placed DNP part or a drop-in replacement.
6. After selecting and placing the antenna, VNA/OTA tune the ESP32 chip-side and antenna-side matching networks in the final cue enclosure. Reference-board values are not production tuning values.
7. Confirm 50 Ohm controlled-impedance geometry from the final stack-up and fabrication tolerances.
8. Validate the 40 MHz crystal load capacitors and series element on assembled hardware.
9. Re-estimate I2C rise time/capacitance with all populated sensors, charger, gauge and audio ADC.
10. Verify the CSD87313DMS DMS8 land/stencil, 9=S1 and 10=S2 exposed-pad mapping and Kelvin routing to the 60 mOhm R44; complete the RoHS Exempt review before release.
11. Validate the BQ298217 thresholds over tolerance and temperature, including charger-inrush, supplement, overload and short-circuit cases.
12. Preserve IIS3DWB10ISTR axis orientation near the rigid front cue insert and independently compare its footprint with official ST reference CAD before release.
