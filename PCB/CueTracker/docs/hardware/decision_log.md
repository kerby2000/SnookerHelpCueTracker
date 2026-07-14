# Cue Tracker hierarchical-hardware decision log

Date: 2026-07-15

This log records the target implementation for the rear-main/front-sensor redesign. Values described as nominal, starting, proposed or validation-dependent are not production limits until verified on assembled hardware. Final schematic, netlist, ERC and rendered-sheet readback remain the implementation authority.

## Architecture and interface decisions

| Decision | Selected implementation | Reason / status |
|---|---|---|
| MCU | Espressif `ESP32-S3-PICO-1-N8R8` | Integrates the ESP32-S3, 8 MB flash, 8 MB octal PSRAM and 40 MHz crystal in a 7 x 7 mm SiP. The previous bare ESP32-S3R8, W25Q128 and external 40 MHz tuning network are removed. Use the official N8R8 pin contract; the supplied N8R2 archive is not valid symbol metadata for N8R8 even if package geometry is shared. |
| RTC crystal | Retain the 32.768 kHz crystal on GPIO15/GPIO16 | The PICO SiP exposes and supports `XTAL_32K_P/N`, the pins are free, and lower-drift sleep/wake timing is useful for this battery instrument. Firmware must select it explicitly and tolerate startup failure. Validate load capacitance and standby benefit; DNP the crystal/capacitors only if measurement shows no benefit. |
| Schematic partition | `CueTracker.kicad_sch` root with `rear_main.kicad_sch` and `front_sensor.kicad_sch` child sheets | Rear contains MCU, battery/power, audio, RF, USB and HMI. Front contains LSM6DSV320X, IIS3DWB10IS, MMC5983MA and BMP581. Hierarchical pins are the only cross-sheet electrical contract. |
| Rigid-board interconnect | Same Hirose `FH34SRJ-24S-0.5SH(50)`, LCSC `C324726`, on both boards | Exact 24-position, 0.5 mm-pitch, 0.3 mm-FPC connector. The pin map in `gpio_allocation.md` is normative. Mechanical review must catch any cable/contact-side mirroring before layout release. |
| Front sensor power | Two `+3V3_SENSOR` contacts, four Earth contacts and `SENSOR_PWR_EN` on the 24-pin link | R62, a 0-ohm link, gives the outgoing sensor supply a distinct reviewed net name; its single rear-side `PWR_FLAG` documents the otherwise invisible source through that passive link. Power and returns are interleaved around the two SPI groups. GPIO46 defaults low and enables the front load switch after boot. The front connector is not part of a 3 A battery/USB path. |
| Main motion bus | LSM6DSV320X on four-wire SPI; clock and MOSI source shared with HMI | Preserves deterministic motion capture. Separate source-resistor branches reduce interaction between the front FPC and HMI cable. |
| Impact bus | IIS3DWB10IS on its own four-wire SPI with both interrupt lines | Preserves continuous high-bandwidth vibration capture and avoids sharing its clock with display traffic. |
| I2C link | SDA/SCL cross the 24-pin connector; one pull-up pair on rear | BMP581 and MMC5983MA reside on front; charger, Type-C controller, optional gauge and audio ADC reside on rear. Addresses must appear as schematic comments and be checked for conflicts. |
| HMI target | 1.14-inch, 135 x 240, 3.3 V ST7789, four-wire SPI, no touch, on a daughterboard | Keeps the display replaceable and mechanically independent of the rear board. The project-defined eight-pin map is normative; raw panel FPC pin order is not assumed. |
| HMI connector | `FH34SRJ-8S-0.5SH(50)` with `GND, 3V3_HMI, SCK, MOSI, RST_N, DC, CS_N, BL` | Provides the exact eight-signal rear-to-daughterboard interface. Confirm contact side and seller drawing before release. |
| HMI signal conditioning | 10 uF + 1 uF + 100 nF on `+3V3_HMI`; 22-47 Ohm series resistors on SCK/MOSI; CS pull-up; explicit reset default; GPIO42-controlled MOSFET/load switch | Prevents reset-time display selection and limits cable edges. `LCD_BL/HMI_EN` defaults off. Component values are starting values for scope/EMI validation. |
| Capture-mode display policy | No display SPI transaction or backlight/HMI-state change during `ARMED` and `SHOT_CAPTURE` | The LCD shares SCK/MOSI with the main-motion interface. Firmware leaves LCD CS inactive and the bus configuration unchanged until capture is complete. This is a hard firmware requirement, not an optimization. |
| Debug and recovery | Native USB Serial/JTAG, BOOT and RESET; no physical JTAG header | GPIO39-GPIO42 are required for LCD CS/DC/reset/HMI enable. Native USB preserves programming and debug without consuming those pins. |

## Power, battery and USB decisions

| Decision | Selected implementation | Reason / status |
|---|---|---|
| Reference cell | Samsung INR18650-35E, fixed/pre-tabbed architecture | Reference assumptions are a 1S cylindrical cell with factory-welded tabs. Tabs solder to plated PCB slots; a cradle carries mechanical loads. Never rely on solder joints for retention and never solder directly to the bare cell can. |
| Temperature sensing | Remote 10 kOhm NTC solder pads, DNP at PCBA | The NTC is installed after assembly and thermally coupled to the cell. It remains required for normal charging unless a separately reviewed and validated charger configuration explicitly permits operation without it. |
| Independent protection | BQ298217 + active CSD87313DMS dual FET + `WSL2512R0200FEA` 20 mOhm, 1%, 1 W, 2512-class shunt | Replaces the obsolete 60 mOhm value. Kelvin connections must originate at the shunt pads. Nominal targets are approximately 1.8 A charge overcurrent, 3.0 A discharge overcurrent and 10 A short circuit. Threshold tolerance, delay and temperature require validation. |
| High-current path rating | At least 3 A normal design current from cell tabs through protector, shunt, bypass, charger/power path, regulator input and returns; fault-rated where protection energy flows | Includes copper width/thickness, vias, solder lands and any zero-ohm/bypass element. Fault transients must be checked against BQ298217 delay and FET SOA, not just continuous ampacity. |
| Fuel gauge | BQ27427 retained as an optional, mutually exclusive build variant | Its integrated sense/current path is not the default choice for a 3 A-capable path because its continuous-current capability is approximately 2 A. The gauge-populated build must be limited to 2 A or less. |
| Default 3 A gauge bypass | BQ27427 DNP; fit a dedicated at-least-3-A bypass/bridge | This is the default architecture that satisfies the 3 A current-path requirement. The bypass and BQ27427 must never be fitted together. A generic small 0 Ohm resistor is not acceptable unless its continuous and transient rating is demonstrated. |
| Voltage-only fallback | Protected-pack switched divider to ESP32 ADC1, enabled by GPIO46 | Supplies battery-voltage telemetry in the default gauge-bypass build. GPIO46 also powers the front sensors, so a measurement is taken only while `SENSOR_PWR_EN` is high. This coupling is an explicit pin-budget assumption. |
| Main 3.3 V regulator | TPS63802 buck-boost retained | Provides a 3.3 V rail across the useful 1S discharge curve and sufficient transient capability for ESP32-S3 radio peaks. The approximately 200 mA figure remains an average operating target, not the regulator or source limit. |
| Charger/power path | BQ25611D retained | Switch-mode 1S charging plus NVDC power path. ESP32 owns the USB D+/D- pair; BQ25611D D+/D- are unused or test pads only. |
| Charger reset policy | Charge disabled at reset through a transistor/open-drain CE stage | `/CE` is held high independently of MCU power. GPIO3 has a pull-down and asserts the transistor only after firmware has programmed and verified limits; do not restore the former direct GPIO pull-up scheme. |
| Charger firmware defaults | 1.0 A normal R0 charge current; 1.5 A maximum only after thermal validation; OTG disabled | Firmware first disables charging and OTG, sets source-safe IINDPM and Samsung-compatible voltage/current limits, services the watchdog policy, then conditionally enables charging. The 1.5 A mode requires cell, NTC, enclosure and PCB validation. |
| USB-C data ownership | USB-C D+/D- connect only to ESP32-S3 native USB through low-capacitance ESD and source resistors | Preserves ROM download and USB Serial/JTAG. BQ25611D USB detection pins never share this pair. |
| Type-C CC control | TUSB320LAI in UFP/I2C mode | Reports attachment, orientation and advertised current. It is not USB Power Delivery and does not by itself authorize a charger current change. |
| VBUS protection chain | Receptacle VBUS -> connector-adjacent ESD441-class TVS -> TPS25947-class 3 A eFuse/current limiter -> protected VBUS | Replaces every 500 mA PPTC assumption. Receptacle contacts, vias and VBUS copper must be suitable for 3 A. Final eFuse current limit, dV/dt, overvoltage and thermal values require hardware validation. |
| CC ESD | Low-capacitance two-channel CC-rated ESD protection on CC1/CC2 | Protects TUSB320 inputs without placing USB-data protection on the CC pins. Keep the devices adjacent to the receptacle. |
| Direct VBUS sensing | `VBUS_PRESENT` on GPIO48 through a powered-off-safe level translator, transistor or validated equivalent | Provides direct source-presence information while preventing 5 V injection into the MCU when +3V3 is absent. A raw 5 V GPIO connection is prohibited. |
| Charger D+/D- policy | No functional connection; optional local test pads only | USB current policy comes from TUSB320/firmware rather than BQ25611 BC1.2 detection. Test pads must not stub the ESP32 data pair. |

## Sensor, audio, RF and enclosure decisions

| Decision | Selected implementation | Reason / status |
|---|---|---|
| Main motion IMU | LSM6DSV320XTR, populated on `front_sensor` | Correct high-g motion device, with local decoupling, SPI pull/default network and two interrupts routed through the 24-pin link. |
| Impact sensor | IIS3DWB10ISTR, 16-lead wettable-flank LLGA, populated on `front_sensor` | High-bandwidth vibration capture. Verify land pattern, exposed-pad handling, axis orientation and assembly against official ST CAD before production. |
| Magnetometer | MMC5983MA populated at the extreme front, `MMC_INT` retained | Maximizes distance from battery, power inductors and high-current loops. Use nonmagnetic fasteners and calibrate in the complete cue. |
| Barometer | BMP581 populated, `BMP_INT` routed through connector pin 22 | Supports interrupt-driven pressure acquisition. Enclosure requires a separate ePTFE atmospheric vent; do not share it with the microphone chimney. |
| Audio | IM73A135 + TLV320ADC6120 populated | Retains the complete differential analogue microphone path and digital audio conversion. Use a sealed external acoustic chimney. Route ADC channel 2 to test pads or an optional expansion connector. |
| RF supply and antenna | ESP32 PICO RF pin through tuneable C-L-C/pi matching to the populated CA-C03 ceramic antenna | Retains an external antenna feed. The SiP does not remove the need for a 50 Ohm feed, edge keepout, enclosure validation and final VNA/OTA tuning. |
| Ground symbol convention | `Earth` symbol represents system 0 V | Retained at the user's request. It is not protective earth or chassis earth and must not be described as PE in safety or PCB documentation. |

## Normative interconnect maps

### Front 24-pin connector, identical at both rigid boards

| Pin | Signal | Pin | Signal |
|---:|---|---:|---|
| 1 | `Earth` | 13 | `IMPACT_MOSI` |
| 2 | `+3V3_SENSOR` | 14 | `IMPACT_MISO` |
| 3 | `+3V3_SENSOR` | 15 | `IMPACT_CS_N` |
| 4 | `Earth` | 16 | `IMPACT_INT1` |
| 5 | `MOTION_SCK` | 17 | `IMPACT_INT2` |
| 6 | `MOTION_MOSI` | 18 | `Earth` |
| 7 | `MOTION_MISO` | 19 | `I2C_SDA` |
| 8 | `MOTION_CS_N` | 20 | `I2C_SCL` |
| 9 | `MOTION_INT1` | 21 | `MMC_INT` |
| 10 | `MOTION_INT2` | 22 | `BMP_INT` |
| 11 | `Earth` | 23 | `SENSOR_PWR_EN` |
| 12 | `IMPACT_SCK` | 24 | `Earth` |

### Rear HMI 8-pin connector

| Pin | Signal | Pin | Signal |
|---:|---|---:|---|
| 1 | `Earth` | 5 | `LCD_RST_N` |
| 2 | `+3V3_HMI` | 6 | `LCD_DC` |
| 3 | `LCD_SCK` | 7 | `LCD_CS_N` |
| 4 | `LCD_MOSI` | 8 | `LCD_BL` |

## PCB and validation items

1. Verify the official ESP32-S3-PICO-1-N8R8 pinout, exposed-pad via field, package courtyard and N8R8 ordering metadata independently of the supplied N8R2 library archive.
2. Confirm 24-pin and 8-pin Hirose contact side, pin-1 orientation, FPC thickness and cable fold before PCB routing. Render both rigid boards with the cable installed to prove no mirroring. Replace the current full-size signal-pad paste openings with the reduced vendor paste apertures before production release.
3. Scope both shared SPI branches with the final FPC/daughterboard and tune the 22-47 Ohm source resistors. Prove no HMI activity occurs in `ARMED` or `SHOT_CAPTURE`.
4. Validate TPS63802 droop and thermal rise with maximum ESP32 radio activity, both IMUs streaming, audio active and HMI loads transitioning outside capture.
5. Validate BQ25611D reset-off behavior, 1.0 A charge mode, source-current policy, watchdog, NTC thresholds and OTG-disabled state. Treat 1.5 A as prohibited until thermal validation is signed off.
6. Validate ESD441-class TVS and TPS25947-class eFuse selection, 3 A receptacle/contact/copper rating, inrush, short response and thermal behavior. No 500 mA PPTC assumption may remain.
7. Verify the 20 mOhm shunt Kelvin routing and BQ298217 threshold ranges over IC, shunt and temperature tolerance; test approximately 1.8 A charge OC, 3.0 A discharge OC and 10 A short behavior safely.
8. Prove the default bypass path carries at least 3 A and relevant fault transients. Enforce mutual exclusion in BOM/assembly data. Gauge-populated hardware is a separately current-limited variant.
9. Validate the Samsung INR18650-35E tab weld, plated-slot solder joint, cradle restraint, remote NTC attachment and service procedure. Solder joints must carry current but no cell-retention load.
10. Verify BMP581 ePTFE vent and microphone acoustic chimney as separate sealed paths, including adhesive/cleaning keepouts and pressure/acoustic response.
11. Measure magnetic disturbance at the extreme-front MMC5983MA location with display, charger and radio active; use nonmagnetic fasteners and perform final-product calibration.
12. VNA/OTA tune the external antenna matching in the final cue enclosure and production stack-up; schematic values are starting values only.

Sources: [ESP32-S3-PICO-1 datasheet](https://documentation.espressif.com/esp32-s3-pico-1_datasheet_en.pdf), [ESP32-S3 hardware design guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html), [Hirose FH34SRJ-24S product page](https://www.hirose.com/en/product/p/CL0580-1255-6-50), [Hirose FH34SRJ-8S product page](https://www.hirose.com/en/product/p/CL0580-1231-8-50), [BQ2980/BQ2982 datasheet](https://www.ti.com/lit/ds/symlink/bq2980.pdf), [BQ27427 datasheet](https://www.ti.com/lit/ds/symlink/bq27427.pdf), [BQ25611D datasheet](https://www.ti.com/lit/ds/symlink/bq25611d.pdf), [TPS25947 datasheet](https://www.ti.com/lit/ds/symlink/tps25947.pdf).
