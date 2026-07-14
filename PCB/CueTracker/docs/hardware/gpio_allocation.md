# Cue Tracker GPIO and interconnect allocation

Date: 2026-07-15

Target MCU: Espressif `ESP32-S3-PICO-1-N8R8`, with 8 MB in-package flash and 8 MB in-package octal PSRAM.

This document is the allocation contract for the two-rigid-board hierarchical design. `CueTracker.kicad_sch` is the hierarchy root, `rear_main.kicad_sch` contains the MCU, USB, RF, power, battery, audio and HMI circuits, and `front_sensor.kicad_sch` contains the four front sensors. The bare ESP32-S3R8, external W25Q128 flash, external 40 MHz crystal and physical JTAG header are not part of this architecture.

## Implementation assumptions requiring final readback

- GPIO46 controls both the front-board sensor load switch and the switched battery-ADC divider. This deliberately makes battery-voltage fallback measurements available only while `SENSOR_PWR_EN` is asserted. If independent battery measurement while the front board is off becomes a requirement, a separate GPIO or a hardware-timed switch is required.
- GPIO3 drives a transistor/open-drain charge-enable stage; it must not be pulled high directly by the charger circuit. The transistor gate/source network must leave the BQ25611D `/CE` pin high, and therefore charging disabled, throughout reset.
- Power-IC interrupt outputs are not assigned an MCU GPIO in this pin plan. Firmware polls the Type-C detector, charger and optional gauge. Any later requirement for interrupt-driven charger or gauge service must re-open the allocation.
- The identical 24-position connector numbering is a schematic contract. The rigid-board orientation, connector contact side and FPC topology must be reviewed together so that the cable does not mirror pin 1 to pin 24.
- The 8-position HMI map is the rear-board-to-daughterboard contract, not a claim about the raw LCD glass FPC. The daughterboard must translate it to the selected ST7789 module, and the seller drawing/contact orientation must be confirmed before PCB release.

## ESP32-S3-PICO-1-N8R8 GPIO allocation

| GPIO / SiP pin | Net / function | Direction at MCU | Reset / strap behavior | Connected block | Selection reason |
|---|---|---|---|---|---|
| GPIO0 / pin 5 | `CHIP_BOOT` | Input at reset | 10 kOhm pull-up; BOOT switch to Earth | BOOT button | Native USB download recovery |
| GPIO1 / pin 6 | `BAT_ADC_SENSE` | Analogue input, ADC1_CH0 | Non-strapping; divider top is disconnected when GPIO46 is low | Rear switched battery divider | ADC1 avoids ADC2/Wi-Fi coexistence restrictions |
| GPIO2 / pin 7 | `IMPACT_INT1` | Input | Non-strapping | Front connector pin 16, IIS3DWB10IS INT1 | Primary impact interrupt |
| GPIO3 / pin 8 | `CHG_ENABLE` | Output after initialization | JTAG-source strap; external gate pull-down keeps the CE transistor off during reset | Rear BQ25611D CE transistor stage | Firmware-controlled, fail-safe charge enable without a pull-up on the strap pin |
| GPIO4 / pin 9 | `IMPACT_INT2` | Input | Non-strapping | Front connector pin 17, IIS3DWB10IS INT2/TRIG | Secondary impact interrupt/trigger |
| GPIO5 / pin 10 | `AUDIO_BCLK` | Output | Non-strapping | TLV320ADC6120 BCLK | Audio serial clock |
| GPIO6 / pin 11 | `AUDIO_FSYNC` | Output | Non-strapping | TLV320ADC6120 FSYNC | Audio frame sync |
| GPIO7 / pin 12 | `AUDIO_SDOUT` | Input | Non-strapping | TLV320ADC6120 SDOUT | Digitized microphone data |
| GPIO8 / pin 13 | `I2C_SDA` | Bidirectional, open-drain | Non-strapping; one rear-board pull-up to +3V3 | Both sheets through connector pin 19 | Shared control bus |
| GPIO9 / pin 14 | `I2C_SCL` | Bidirectional, open-drain | Non-strapping; one rear-board pull-up to +3V3 | Both sheets through connector pin 20 | Shared control bus |
| GPIO10 / pin 15 | `MOTION_SCK`, branched as `LCD_SCK` | Output | Non-strapping | Front connector pin 5 and HMI connector pin 3 | Shared SPI clock; separate source resistors serve the two physical branches |
| GPIO11 / pin 16 | `MOTION_MOSI`, branched as `LCD_MOSI` | Output | Non-strapping | Front connector pin 6 and HMI connector pin 4 | Shared SPI MOSI; separate source resistors serve the two physical branches |
| GPIO12 / pin 17 | `MOTION_MISO` | Input | Non-strapping | Front connector pin 7 | Main-motion SPI input |
| GPIO13 / pin 18 | `MOTION_CS_N` | Output | Non-strapping; 10 kOhm pull-up at the sensor branch | Front connector pin 8 | Main-motion device select |
| GPIO14 / pin 19 | `BMP_INT` | Input | Non-strapping | Front connector pin 22, BMP581 INT | Barometer interrupt retained across the interconnect |
| GPIO15 / pin 21 | `XTAL_32K_P` | RTC crystal pin | Do not use as GPIO while the crystal is fitted | 32.768 kHz crystal | Supported external low-frequency clock for lower-drift sleep timing |
| GPIO16 / pin 22 | `XTAL_32K_N` | RTC crystal pin | Do not use as GPIO while the crystal is fitted | 32.768 kHz crystal | Paired RTC crystal terminal |
| GPIO17 / pin 23 | `IMPACT_SCK` | Output | Non-strapping | Front connector pin 12 | Dedicated impact SPI clock |
| GPIO18 / pin 24 | `IMPACT_MOSI` | Output | Non-strapping | Front connector pin 13 | Dedicated impact SPI output |
| GPIO19 / pin 25 | `USB_D-` | Bidirectional | Native USB function | USB-C through ESD and source resistor | Programming, USB Serial/JTAG and product USB data |
| GPIO20 / pin 26 | `USB_D+` | Bidirectional | Native USB function | USB-C through ESD and source resistor | Programming, USB Serial/JTAG and product USB data |
| GPIO21 / pin 27 | `IMPACT_MISO` | Input | Non-strapping | Front connector pin 14 | Dedicated impact SPI input |
| GPIO38 / pin 43 | `MOTION_INT1` | Input | Non-strapping | Front connector pin 9, LSM6DSV320X INT1 | Main FIFO/data-ready interrupt |
| GPIO39 / pin 44 | `LCD_CS_N` | Output | Non-strapping; HMI-side pull-up keeps display deselected | HMI connector pin 7 | ST7789 chip select; replaces physical JTAG TCK use |
| GPIO40 / pin 45 | `LCD_DC` | Output | Non-strapping | HMI connector pin 6 | ST7789 data/command select; replaces physical JTAG TDO use |
| GPIO41 / pin 47 | `LCD_RST_N` | Output | Non-strapping; default resistor state holds or releases reset as documented in the HMI circuit | HMI connector pin 5 | Display reset; replaces physical JTAG TDI use |
| GPIO42 / pin 48 | `HMI_EN` / `LCD_BL` | Output | Non-strapping; pull-down keeps HMI/backlight off during reset | HMI load switch or MOSFET and connector pin 8 | One quiet-state control for HMI power/backlight; replaces physical JTAG TMS use |
| GPIO43 / pin 49 | `IMPACT_CS_N` | Output | UART0 TX alternate function not used; sensor CS has a pull-up | Front connector pin 15 | Dedicated impact device select |
| GPIO44 / pin 50 | `MMC_INT` | Input | UART0 RX alternate function not used | Front connector pin 21, MMC5983MA INT | Dedicated magnetometer interrupt |
| GPIO45 / pin 51 | `VDD_SPI_STRAP` | Input at reset; otherwise unused | Keep the Espressif-required strap state; do not allocate to a peripheral | SiP strap network | Protects the internal flash/PSRAM supply selection |
| GPIO46 / pin 52 | `SENSOR_PWR_EN` and battery-divider enable | Output after boot | Strapping pin; pull-down keeps both switched loads off at reset | Front connector pin 23, front load switch and rear battery-divider switch | Consolidates two low-duty enable functions to preserve GPIO capacity |
| GPIO47 / pin 37 | `MOTION_INT2` | Input | Non-strapping | Front connector pin 10, LSM6DSV320X INT2 | Secondary motion event/high-g interrupt |
| GPIO48 / pin 36 | `VBUS_PRESENT` | Input | Non-strapping; never expose the GPIO directly to 5 V | Rear powered-off-safe VBUS sense circuit | Direct, low-latency USB source-presence indication |

## SiP-reserved and non-GPIO pins

| SiP pin(s) | Handling | Reason |
|---|---|---|
| 28 `SPICS1` | No board connection | Internal PSRAM connection |
| 29 `VDD_SPI` | Do not load as a board power rail | Internal flash/PSRAM I/O supply node |
| 30-35 | No board connection | Internal flash connections |
| 38-42, corresponding to ESP32 GPIO33-GPIO37 | No board connection | Internal octal-PSRAM connections |
| 53-54 | No board connection | Internal 40 MHz crystal connections; the previous external 40 MHz network is removed |
| 57 exposed pad | Earth with a low-inductance via field | Electrical and thermal return |

The external 32.768 kHz crystal is retained on GPIO15/GPIO16 because the PICO SiP supports those RTC crystal pins, both pins are available in this allocation, and the design benefits from stable sleep/wake timing. Firmware must select the external RTC clock and fall back safely to the internal clock if crystal startup fails. Load capacitors remain assembly-validation values; mark the crystal and its capacitors DNP only if measured standby energy and timing show no benefit.

## Front-board 24-position interconnect

Both rigid boards use `Hirose FH34SRJ-24S-0.5SH(50)`, LCSC `C324726`, 24 positions, 0.5 mm pitch, for 0.3 mm FPC/FFC. The schematic pin map is identical at both ends.

| Pin | Signal | Purpose |
|---:|---|---|
| 1 | `Earth` | Return |
| 2 | `+3V3_SENSOR` | Front-board supply, paralleled with pin 3 |
| 3 | `+3V3_SENSOR` | Front-board supply, paralleled with pin 2 |
| 4 | `Earth` | Return |
| 5 | `MOTION_SCK` | LSM6DSV320X SPI clock; shared MCU source with LCD clock |
| 6 | `MOTION_MOSI` | LSM6DSV320X SPI MOSI; shared MCU source with LCD MOSI |
| 7 | `MOTION_MISO` | LSM6DSV320X SPI MISO |
| 8 | `MOTION_CS_N` | LSM6DSV320X chip select |
| 9 | `MOTION_INT1` | LSM6DSV320X INT1 |
| 10 | `MOTION_INT2` | LSM6DSV320X INT2 |
| 11 | `Earth` | Return between SPI groups |
| 12 | `IMPACT_SCK` | IIS3DWB10IS SPI clock |
| 13 | `IMPACT_MOSI` | IIS3DWB10IS SPI MOSI |
| 14 | `IMPACT_MISO` | IIS3DWB10IS SPI MISO |
| 15 | `IMPACT_CS_N` | IIS3DWB10IS chip select |
| 16 | `IMPACT_INT1` | IIS3DWB10IS INT1 |
| 17 | `IMPACT_INT2` | IIS3DWB10IS INT2/TRIG |
| 18 | `Earth` | Return |
| 19 | `I2C_SDA` | Shared front-sensor I2C data |
| 20 | `I2C_SCL` | Shared front-sensor I2C clock |
| 21 | `MMC_INT` | MMC5983MA interrupt |
| 22 | `BMP_INT` | BMP581 interrupt |
| 23 | `SENSOR_PWR_EN` | Front sensor-rail enable; default low at reset |
| 24 | `Earth` | Return |

The two +3V3 and four Earth contacts reduce connector impedance but do not by themselves prove a 3 A rating; the front sensor branch is a low-current branch. Keep high-current battery, charger and USB paths off this FPC.

## Rear-board HMI connector

Use `FH34SRJ-8S-0.5SH(50)` for the display daughterboard interface. Target display class is a 1.14-inch, 135 x 240, 3.3 V ST7789 module with 4-wire SPI and no touch.

| Pin | Signal | Required rear-board support |
|---:|---|---|
| 1 | `Earth` | Return |
| 2 | `+3V3_HMI` | Locally switched rail; 10 uF, 1 uF and 100 nF at the connector/load |
| 3 | `LCD_SCK` | GPIO10 branch with 22-47 Ohm source resistor |
| 4 | `LCD_MOSI` | GPIO11 branch with 22-47 Ohm source resistor |
| 5 | `LCD_RST_N` | GPIO41; explicit passive default state |
| 6 | `LCD_DC` | GPIO40 |
| 7 | `LCD_CS_N` | GPIO39; pull-up keeps the display deselected during reset |
| 8 | `LCD_BL` | GPIO42-controlled MOSFET/load-switch output or daughterboard logic input; default off |

Do not assume the raw display-panel pin order matches this connector. Verify connector contact side, FPC pin-1 convention, daughterboard translation and the panel backlight current before PCB release.

## Firmware mode rule for shared display SPI

`LCD_SCK` and `LCD_MOSI` share the GPIO10/GPIO11 source with the main-motion SPI bus. Firmware must obey this hard real-time rule:

```text
During ARMED and SHOT_CAPTURE:
  - issue no display SPI transaction;
  - do not change LCD_BL or HMI_EN state;
  - leave LCD_CS_N inactive;
  - do not reconfigure the shared SPI pins.
```

Display updates and backlight transitions are permitted only after leaving those states. Separate source resistors shall isolate the front FPC branch from the HMI branch; they do not replace firmware bus arbitration.

## Shared I2C addresses

| Device | Sheet | 7-bit address | Note |
|---|---|---:|---|
| TUSB320LAI | rear | `0x47` | Type-C CC detector |
| BQ25611D | rear | `0x6B` | Charger/power path |
| BQ27427 | rear | `0x55` | Present only in the optional, current-limited gauge build |
| TLV320ADC6120 | rear | `0x4E` | Audio ADC with the selected address strap |
| BMP581 | front | `0x46` | SDO/address strap must select 0x46 to avoid TUSB320 at 0x47 |
| MMC5983MA | front | `0x30` | Magnetometer |

Use one intentional pull-up pair on the rear board and verify rise time with the two connectors and FPC fitted. Device comments on the schematic should repeat these addresses. The motion and impact sensors use SPI in this design.

## Power-management and battery-ADC notes

- BQ25611D charging is disabled at reset. Firmware first writes `CHG_CONFIG=0`, confirms OTG/boost is disabled, programs a source-safe input limit and the Samsung INR18650-35E charge-voltage/current policy, then enables charging only when all checks pass.
- The R0 normal charge-current target is 1.0 A. A 1.5 A setting is a validated maximum option only after cell, connector, NTC, enclosure and PCB thermal testing. Charger D+/D- are not connected to the USB data pair; expose them only as test pads if retained.
- BQ27427's integrated current path is limited to approximately 2 A continuous. The default 3 A-capable build therefore leaves the gauge DNP and fits its mutually exclusive, at-least-3-A bypass. The gauge-populated variant must be explicitly limited to 2 A or less. Never populate both paths.
- The voltage-only fallback remains on protected `PACK_P`: `PACK_P -> load switch -> 1.0 MOhm -> BAT_ADC_SENSE -> 330 kOhm -> Earth`, with 100 nF from `BAT_ADC_SENSE` to Earth. GPIO46 enables the divider together with the sensor rail. The nominal conversion remains `Vpack = Vadc * 4.030303`.
- `VBUS_PRESENT` uses a powered-off-safe buffer, transistor, or similarly validated level-shifting circuit. A bare resistor connection from USB VBUS to GPIO48 is prohibited.

## Placement, enclosure and recovery rules

- Place MMC5983MA at the extreme front of the sensor PCB, away from battery, inductors and high-current loops. Use nonmagnetic fasteners and validate hard/soft-iron calibration in the complete cue.
- Route BMP581 to a separate ePTFE atmospheric vent. Do not share that vent with the microphone acoustic path, and protect the pressure port from adhesive and wash residue.
- Route IM73A135 through a sealed external acoustic chimney. Keep the chimney acoustically isolated from the barometer vent. TLV320ADC6120 channel 2 goes to test pads or an optional expansion connector and is not silently grounded or left as an undocumented input.
- Native USB on GPIO19/GPIO20 is the primary programming and debug interface. Physical-pad JTAG is removed because GPIO39-GPIO42 are assigned to HMI. USB Serial/JTAG plus BOOT and RESET provide recovery.
- GPIO43/GPIO44 are consumed by impact chip select and magnetometer interrupt, so there is no dedicated UART0 header in this allocation.

Sources: [ESP32-S3-PICO-1 datasheet](https://documentation.espressif.com/esp32-s3-pico-1_datasheet_en.pdf), [ESP32-S3 hardware design guidelines](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32s3/schematic-checklist.html), [BQ25611D datasheet](https://www.ti.com/lit/ds/symlink/bq25611d.pdf), [BQ27427 datasheet](https://www.ti.com/lit/ds/symlink/bq27427.pdf), [TPS22919 datasheet](https://www.ti.com/lit/ds/symlink/tps22919.pdf).
