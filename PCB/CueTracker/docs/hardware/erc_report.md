# Cue Tracker ERC and integrity report

Date: 2026-07-15

Status: **PASS — 0 errors, 0 warnings**

The authoritative saved hierarchy is:

- `CueTracker.kicad_sch`: hierarchy root.
- `rear_main.kicad_sch`: MCU, USB, RF, battery/power, charger, audio and HMI.
- `front_sensor.kicad_sch`: LSM6DSV320X, IIS3DWB10IS, MMC5983MA and BMP581.

## Verification results

| Check | Result |
|---|---|
| KiCad MCP ERC | 0 errors, 0 warnings, 0 informational violations |
| ERC report | [`CueTracker_final_ERC.json`](CueTracker_final_ERC.json) |
| KiCad netlist | [`CueTracker_final_netlist.xml`](CueTracker_final_netlist.xml), 172 components and 159 nets |
| Manufacturing BOM | [`bom_manufacturing.csv`](bom_manufacturing.csv), 172 component rows and 51 columns |
| Capacitor metadata | 62 of 62 capacitors have both `Voltage` and `Dielectric` fields |
| PDF | [`CueTracker_schematic.pdf`](../../output/pdf/CueTracker_schematic.pdf), three pages |
| Renders | Root, Rear Main and Front Sensor SVGs plus three inspected PNG pages under [`output/renders`](../../output/renders) |
| Visual QA | All three PDF pages rendered successfully; no clipping or literal escaped-newline text was found |
| Saved-file readback | Fresh-process KiCad MCP readback succeeded after the final save |

The ERC JSON has no per-item exclusions. Four project-level checks remain intentionally set to `ignore`:

- `single_global_label`: this hierarchy uses no global labels; local and hierarchical labels are the design contract.
- `four_way_junction`: this is a drawing-style advisory; connectivity is verified from the saved netlist.
- `simulation_model_issue`: SPICE simulation models are outside this schematic release.
- `footprint_filter`: exact project footprints deliberately override some generic library filters. Footprint identity is checked from BOM metadata and manufacturer CAD; land-pattern validation remains a PCB-release task.

## Connector endpoint proof

Fresh netlist inspection proves that J101 and J201 both implement the normative 24-pin order:

`1 Earth; 2 +3V3_SENSOR; 3 +3V3_SENSOR; 4 Earth; 5 MOTION_SCK; 6 MOTION_MOSI; 7 MOTION_MISO; 8 MOTION_CS_N; 9 MOTION_INT1; 10 MOTION_INT2; 11 Earth; 12 IMPACT_SCK; 13 IMPACT_MOSI; 14 IMPACT_MISO; 15 IMPACT_CS_N; 16 IMPACT_INT1; 17 IMPACT_INT2; 18 Earth; 19 I2C_SDA; 20 I2C_SCL; 21 MMC_INT; 22 BMP_INT; 23 SENSOR_PWR_EN; 24 Earth`.

J102 implements:

`1 Earth; 2 +3V3_HMI; 3 LCD_SCK; 4 LCD_MOSI; 5 LCD_RST_N; 6 LCD_DC; 7 LCD_CS_N; 8 LCD_BL`.

## Power-flag readback

| Reference | Net |
|---|---|
| `#FLG101` | `VBUS_RAW` |
| `#FLG102` | `Earth` |
| `#FLG103` | `+3V3_RF` |
| `#FLG104` | `+3V3_AUDIO` |
| `#FLG105` | Protector VDD, unnamed `Net-(U10-VDD)` |
| `#FLG106` | `CHG_BAT` |
| `#FLG107` | `PACK_P` |
| `#FLG108` | `CELL_N_RAW` |
| `#FLG109` | `+3V3_SENSOR` |

These are the nine flags justified in [`power_flag_contract.md`](power_flag_contract.md). No flags are placed on real regulator, charger, eFuse or load-switch outputs.

## Release hashes

| File | SHA-256 |
|---|---|
| `CueTracker.kicad_sch` | `9F4560BB70A54A8879883C79AB46827EA505615C9ACA628D320E1089EAA1A9E7` |
| `rear_main.kicad_sch` | `790468765EF1BD33998A568D6682575F347B349E8DD7BDC62B6DD9B1323797E8` |
| `front_sensor.kicad_sch` | `E25DE021BE6F68A58CC1897E6B903C9A15DE6CDB3024EC1C4E2CB990E853DFB2` |
| `CueTracker_Exact.kicad_sym` | `FAA2B0CC868AA9D8C426F93E1D752E73090F31ECFDE8BC38E8C630B95C62378D` |
| `CueTracker_final_ERC.json` | `B1E056710DEFF55EE0F4F877C2B468CF383A0082FC79F8C957B265061465CACE` |
| `CueTracker_final_netlist.xml` | `0657D90D8FFBA701C66426677501EE9368A0EB4828B781F3A2B4D4B7F3271E9A` |
| `bom_manufacturing.csv` | `62BE9458EB484104CEB4215FD4C328D07683F0D8AB1A4ADEA61AAB6B95D760C2` |
| `CueTracker_schematic.pdf` | `FF10E01648DDEF7198738C267C4B7F20302D0FC803510ED97A3F0149EF7FC2C2` |

## Remaining PCB and hardware validation

ERC does not validate routed-copper ampacity, shunt Kelvin geometry, RF tuning/keepout, regulator and charger thermals, protector-FET SOA, connector contact-side mirroring, enclosure venting, acoustic response or MEMS placement. The current PCB file has no completed routing, so the at-least-3-A copper requirement must be proven during PCB layout.

The supplied Hirose footprints match the imported copper geometry and carry the STEP models, but their current signal pads use full-size paste openings. Replicate the vendor's reduced paste apertures and explicit mask treatment before production release. The purchased ST7789 daughterboard drawing/contact orientation also remains a required mechanical confirmation.
