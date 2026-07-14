# Cue Tracker one-sheet primary-source register

Date: 2026-07-14

This register records the manufacturer sources used for the current single-sheet schematic pin maps, support networks, footprints, power limits and provisional tuning values.

| Block | Primary source | Applied decision |
|---|---|---|
| ESP32-S3R8 | https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf | U3 QFN56 pin map, the `-R8` in-package octal-PSRAM reservation, dedicated 3.3 V VDD_SPI output handling, approximately 340 mA maximum-power radio peaks and operating limits |
| ESP32-S3 hardware guidance | https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html | At-least-500-mA 3.3 V source requirement, main-entry bulk capacitance, CHIP_PU/BOOT, 40 MHz crystal, RF matching reserve and filtered VDD3P3 supply |
| USB data ESD | https://assets.nexperia.com/documents/short-data-sheet/PESD5V0Y1BCSF_SDS.pdf | PESD5V0Y1BCSF, 5 V bidirectional, 0.16 pF typical, one DSN0603-2 device per USB data line |
| VBUS ESD | https://assets.nexperia.com/documents/data-sheet/PESD5V0S1BA.pdf | PESD5V0S1BA SOD323 protector on the fused USB VBUS input |
| USB input PPTC | https://www.littelfuse.com/assetdocs/ptc-0402l-datasheet?assetguid=5ceb0255-2d0d-4ad7-91b7-158480540a30 | Littelfuse 0402L050SLKR, 0.50 A hold / 1.00 A trip, 6 V |
| W25Q128JVSIQ | https://www.winbond.com/hq/support/documentation/?__locale=en&line=/product/code-storage-flash/index.html&family=/product/code-storage-flash/qspi-nor/index.html&category=/.categories/resources/datasheet/&pno=W25Q128JV | U4 3.3 V SOIC-8 QSPI pin map, connection to U3's VDD_SPI output and local decoupling; no separate +3V3 feed is intended |
| TPS63802DLAR | https://www.ti.com/lit/ds/symlink/tps63802.pdf | U5 DLA0010A pin map, true buck-boost topology, 2 A at 3.3 V for input at or above 2.3 V, 0.47 uH, input/output capacitance, feedback and PG implementation |
| TPS63802 power inductor | https://www.coilcraft.com/getmedia/84927b8b-f089-421b-a7f4-a0fa23afe908/xfl4015.pdf | XFL4015-471MEC, 0.47 uH, low DCR and saturation/thermal-current margin |
| ESP32 RF-supply inductor | https://www.sunlordinc.com/uploads/files/20221116/SDCL-D%20Series%20of%20Multilayer%20Chip%20Ceramic%20Inductor.pdf | SDCL1608C2N2STDF, 2.2 nH, 500 mA and 0.10 Ohm maximum DCR between `+3V3` and `+3V3_RF` |
| USB-C source detector | https://www.ti.com/lit/ds/symlink/tusb320lai.pdf | TUSB320LAIRWBR RWB0012A pin map, fixed-UFP/I2C address `0x47`, orientation and Type-C advertised-current reporting; not USB PD |
| Charger and NVDC power path | https://www.ti.com/lit/ds/symlink/bq25611d.pdf | U7 BQ25611DRTWR RTW0024A pin map, fixed I2C address `0x6B`, 1 uH buck-charger network, NVDC system path, TS network, R20 CE pull-up behavior and register settings: ICHG 180 mA, precharge 60 mA, termination 60 mA, VREG 4.190 V and source-safe IINDPM before CE low |
| BQ25611D power inductor | https://www.eaton.com/content/dam/eaton/products/electronic-components/resources/data-sheet/eaton-mpi40-v2-miniature-power-inductors-data-sheet.pdf | L4 MPI4020V2-1R0-R, 1 uH, 6.5 A rated current, 7 A saturation current and 24 mOhm maximum DCR |
| Fuel gauge | https://www.ti.com/lit/ds/symlink/bq27427.pdf | U14 BQ27427YZFR YZF0009 pin map, fixed I2C address `0x55`, internal 7 mOhm sense path, coulomb counting and default-fit use; JP1 is a mutually exclusive bypass only when U14 is DNP |
| Switched voltage fallback | https://www.ti.com/lit/ds/symlink/tps22919.pdf | U9 TPS22919DCKR disconnects R23/R24 and C34 from PACK_P between samples; GPIO14 drives ON and R25 100 kOhm pulls ON to Earth at reset. This is a voltage-only fallback when U14 is omitted |
| Independent battery protector | https://www.ti.com/lit/ds/symlink/bq2980.pdf | U10 BQ298217RUGR fixed 4.250 V OVP / 2.600 V UVP and -36 mV OCC / 60 mV OCD / 200 mV SCD thresholds; nominal 0.60 A / 1.00 A / 3.33 A with 60 mOhm R44 |
| Protection FET and DMS land | https://www.ti.com/lit/ds/symlink/csd87313dms.pdf | Active CSD87313DMS dual common-drain FET, 100 nA maximum gate leakage, 5.5 mOhm maximum S1-S2 at 4.5 V and 17 A at TC=25 C. Pages 10-11 / pattern 4222980/A define the custom land; CAD-only exposed pads 9=S1 and 10=S2. TI package data lists RoHS Exempt, which is a release-review gate |
| Protection current shunt | https://www.vishay.com/docs/30100/wsl.pdf | R44 WSL2512R0600FEA, 60 mOhm, 1%, 1 W Power Metal Strip; route Kelvin sense and keep `CELL_N_RAW` separate from Earth except through R44 |
| Remote cell NTC | https://www.semitec-global.com/uploads/sites/2/2017/03/P11-12_AT_Thermistor.pdf | TH1 Semitec 103AT-2, 10 kOhm at 25 C, beta 25/85 of 3435 K. TH1 is DNP for PCBA because the schematic component represents solder pads; hand-wire and thermally bond the remote sensor after assembly unless a deliberate, validated BQ25611D `TS_IGNORE` configuration is used |
| 40 MHz crystal | https://txccrystal.com/images/pdf/7m.pdf | TXC 7M package family; 7M-40.000MEEQ-T is specified at 40 MHz with a 10 pF load and uses the 3.2 x 2.5 mm four-pad package |
| LSM6DSV320XTR | https://www.st.com/resource/en/datasheet/lsm6dsv320x.pdf | U12 exact LGA-14 pin map, supply support and SPI/I2C interface requirements |
| IIS3DWB10ISTR | https://www.st.com/resource/en/datasheet/iis3dwb10is.pdf | U11 exact 16-pin wettable-flank LLGA pin map and terminal geometry |
| ST MEMS land rules | https://www.st.com/resource/en/technical_note/tn0018-surface-mounting-guidelines-for-mems-sensors--in-an-lga-package--stmicroelectronics.pdf | Manufacturer land-extension guidance for the IIS3DWB10ISTR footprint |
| IIS3DWB10IS reference PCB | https://www.st.com/en/evaluation-tools/steval-mki253ka.html | Official evaluation-board Gerber/CAD resource retained as the independent production-footprint cross-check |
| BMP581 | https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bmp581-ds004.pdf | U6 exact ten-pin LGA map, I2C address `0x46` straps, local decoupling and pressure-port keepout |
| MMC5983MA | https://www.memsic.com/Public/Uploads/uploadfile/files/20220119/MMC5983MADatasheetRevA.pdf | U8 exact 16-pin map, CAP capacitance and fixed I2C address `0x30` |
| IM73A135V01 microphone | https://www.infineon.com/assets/row/public/documents/24/49/infineon-im73a135-datasheet-en.pdf?fileId=8ac78c8c7f2a768a017fadec36b84500 | Exact PG-LLGA-5-2 connection, differential analog output, MICBIAS supply limit and characterized load |
| TLV320ADC6120IRTER | https://www.ti.com/lit/ds/symlink/tlv320adc6120.pdf | U13 exact RTE0020A pin map, differential ADC input through C55/C59 and R39/R43, integrated MICBIAS/PGA/ADC with C51 100 nF and C52 1 uF support, I2C address `0x4E` and I2S output |
| Audio analog-input design | https://www.ti.com/lit/an/sbaa583/sbaa583.pdf | AC-coupling and differential input-interface guidance for the microphone-to-ADC path |
| Audio-supply ferrite | https://www.murata.com/products/productdata/8796738650142/ENFA0003.pdf | BLM18KG601SN1D, 600 Ohm at 100 MHz, high-current DC power-line bead for the audio rail |
| Battery/NTC direct-wire interfaces | KiCad `Connector_Wire` solder-wire land definitions plus the final qualified cell/tab/lead assembly drawing | BT1 is a two-wire, strain-relieved direct-solder interface for a pre-tabbed 18650 default or pre-tabbed 21700 alternate. TH1 is DNP at PCBA and retains the separate solder pads for a required hand-wired remote NTC unless `TS_IGNORE` is deliberately validated. No removable battery connector is used |
| JTAG header | https://www.harwin.com/products/M50-3600542R | J2 Harwin M50-3600542R exact 2x5, 1.27 mm vertical SMD male header, tape-and-reel with pick-and-place cap |
| CA-C03 antenna candidate | https://fccid.io/m/c060d34abf8b55518595b1ab4dcd217b408b40b563f5f039319b2a94e9e23f11.pdf | Manufacturer-authored CrossAir V02 dimensions, 2.4-2.5 GHz performance, board reference and 0 Ohm / 3 nH / 0 Ohm starting match. It is the baseline candidate, but ANT1 is not placed in the current schematic |
| KH-3216-H0209 evaluated alternative | https://www.kinghelm.net/upload/file/20240525/KH-3216-H0209-PDF.pdf | 3.23 x 1.66 x 0.45 mm dimensions, 120 MHz minimum bandwidth, reference clearances and matching. It is not interchangeable with CA-C03 and remains an evaluation option only, not a placed DNP component |
| RF ESD | https://assets.nexperia.com/documents/data-sheet/PESD4V0Y1BBSF.pdf | PESD4V0Y1BBSF DSN0603-2 package and low-capacitance RF protection characteristics |

## Procurement and compliance notes

- Q1 is TI CSD87313DMS, LCSC/JLC catalog identifier **C2863848**. Catalog data is procurement-only; the TI data sheet, package addendum and recommended PCB pattern are authoritative.
- TI lists CSD87313DMS as active/production but marks the package **RoHS Exempt** in the package addendum checked 2026-07-14. Regulatory/procurement approval is required before release.
- The custom Q1 footprint must retain separate exposed source lands 9 and 10 from TI-linked CAD. A generic KiCad VSON/NexFET footprint is not an acceptable substitution.
- BT1 and TH1 footprints define PCB wire lands only. TH1 is DNP for PCBA but the remote 103AT-2 is hand-wired and required unless `TS_IGNORE` is deliberately validated. The exact pre-tabbed cell, lead gauge, strain relief, insulation and thermistor attachment require an approved assembly drawing.

Crystal load capacitors and both RF matching networks are starting values. They are not claimed as production-tuned values. The `Earth` symbol is a user-requested schematic convention for circuit 0 V/battery negative; it does not document a protective-earth connection.
