# Cue Tracker GPIO and peripheral allocation

Date: 2026-07-14

Target: U3, a bare ESP32-S3R8 in QFN56 with 8 MB in-package octal PSRAM, and U4, an external W25Q128JVSIQ 16 MB QSPI flash.

This table records the allocation implemented in the single-sheet R0.3 schematic. Native USB and physical-pad JTAG remain available. GPIO3 controls the BQ25611D active-low charge enable, GPIO43 (`U0TXD`) is assigned to the impact-sensor chip select, GPIO44 (`U0RXD`) is assigned to the magnetometer interrupt, and the BMP581 interrupt is not routed to the MCU; firmware polls the BMP581 over I²C.

## GPIO allocation

| GPIO / QFN pin | Net / function | Peripheral | Direction at ESP32 | Boot / strap behavior | Connected device | Selection reason |
|---|---|---|---|---|---|---|
| GPIO0 / pin 5 | `CHIP_BOOT` | Download strap / button | Input at reset | Internal weak pull-up plus R8 10 kOhm to +3V3; BOOT switch to Earth | BOOT1 | Native USB/UART download recovery |
| GPIO1 / pin 6 | `BAT_ADC_SENSE` | ADC1_CH0 | Analogue input | Non-strapping; divider is disconnected at its top when disabled | U9 TPS22919-switched divider: R23 1.0 MOhm, R24 330 kOhm and C34 100 nF to Earth | ADC1 avoids ADC2/Wi-Fi coexistence restrictions and keeps the full-cell voltage below the selected ADC range |
| GPIO2 / pin 7 | `IMPACT_INT1` | GPIO interrupt | Input | Non-strapping | U11 IIS3DWB10ISTR INT1 and TP10 | Impact FIFO/data-ready interrupt |
| GPIO3 / pin 8 | `/CHG_CE_N` | BQ25611D charge enable / JTAG-source strap | Strapping input at reset; output after initialization | R20 10 kOhm to +3V3 keeps charging disabled during reset. Default eFuses select USB Serial/JTAG; pad-JTAG/fused configurations must account for the GPIO3 strap level | U7 BQ25611D `/CE` and R20 | Provides a fail-safe charge-off default; firmware programs all charge limits before driving the net low |
| GPIO4 / pin 9 | `IMPACT_INT2` | GPIO interrupt | Input | Non-strapping | U11 IIS3DWB10ISTR INT2/TRIG and TP11 | Second impact/status interrupt |
| GPIO5 / pin 10 | `AUDIO_BCLK` | I2S/TDM bit clock | Output | Non-strapping | U13 TLV320ADC6120 BCLK | MCU supplies the audio serial clock |
| GPIO6 / pin 11 | `AUDIO_FSYNC` | I2S/TDM frame sync | Output | Non-strapping | U13 TLV320ADC6120 FSYNC | MCU supplies the audio frame clock |
| GPIO7 / pin 12 | `AUDIO_SDOUT` | I2S/TDM serial data | Input | Non-strapping | U13 TLV320ADC6120 SDOUT through R37 33 Ohm | Receives digitized microphone samples |
| GPIO8 / pin 13 | `I2C_SDA` | I2C0 SDA | Bidirectional, open-drain | Non-strapping; R2 4.7 kOhm pull-up to +3V3 | TUSB320LAIRWBR, U7 BQ25611DRTWR, U14 BQ27427YZFR, U6 BMP581, U8 MMC5983MA and U13 TLV320ADC6120 | One shared low-speed control bus |
| GPIO9 / pin 14 | `I2C_SCL` | I2C0 SCL | Bidirectional, open-drain | Non-strapping; R1 4.7 kOhm pull-up to +3V3 | Same I2C devices | One shared low-speed control bus |
| GPIO10 / pin 15 | `MOTION_SPI_SCK` | SPI2 SCLK | Output | Non-strapping; R40 22 Ohm source-series link | U12 LSM6DSV320XTR | Dedicated main-motion SPI controller |
| GPIO11 / pin 16 | `MOTION_SPI_MOSI` | SPI2 MOSI | Output | Non-strapping; R42 22 Ohm source-series link | U12 LSM6DSV320XTR | Dedicated main-motion SPI controller |
| GPIO12 / pin 17 | `MOTION_SPI_MISO` | SPI2 MISO | Input | Non-strapping; R34 0 Ohm link | U12 LSM6DSV320XTR | Dedicated main-motion SPI controller |
| GPIO13 / pin 18 | `MOTION_SPI_CS_N` | SPI2 CS | Output | Non-strapping; sensor CS has a 10 kOhm pull-up and R38 0 Ohm series link | U12 LSM6DSV320XTR | Dedicated main-motion device select |
| GPIO14 / pin 19 | `BAT_ADC_EN` | GPIO / load-switch enable | Output | Non-strapping; R25 100 kOhm to Earth keeps U9 TPS22919 ON low so the divider defaults off during reset | U9 TPS22919DCKR ON and R25 pull-down | Enables the voltage divider only for a battery-voltage measurement |
| GPIO17 / pin 23 | `IMPACT_SPI_SCK` | SPI3 SCLK | Output | Non-strapping; R29 22 Ohm source-series link | U11 IIS3DWB10ISTR | Dedicated impact-sensor SPI controller |
| GPIO18 / pin 24 | `IMPACT_SPI_MOSI` | SPI3 MOSI | Output | Non-strapping; R35 22 Ohm source-series link | U11 IIS3DWB10ISTR | Dedicated impact-sensor SPI controller |
| GPIO19 / pin 25 | `USB_D-` | Native USB | Bidirectional | Fixed native-USB use | USB-C through ESD protection and R5 22 Ohm | Native programming, debug, and USB device data |
| GPIO20 / pin 26 | `USB_D+` | Native USB | Bidirectional | Fixed native-USB use | USB-C through ESD protection and R6 22 Ohm | Native programming, debug, and USB device data |
| GPIO21 / pin 27 | `IMPACT_SPI_MISO` | SPI3 MISO | Input | Non-strapping; R36 0 Ohm link | U11 IIS3DWB10ISTR | Dedicated impact-sensor SPI controller |
| GPIO38 / pin 43 | `MOTION_INT1` | GPIO interrupt | Input | Non-strapping | U12 LSM6DSV320XTR INT1 and TP12 | Main FIFO/data-ready interrupt |
| GPIO39 / pin 44 | `JTAG_TCK` | Physical-pad JTAG | Input | Reserved for debug | J2 pin 4 | Hardware recovery/debug access |
| GPIO40 / pin 45 | `JTAG_TDO` | Physical-pad JTAG | Output | Reserved for debug | J2 pin 6 | Hardware recovery/debug access |
| GPIO41 / pin 47 | `JTAG_TDI` | Physical-pad JTAG | Input | Reserved for debug | J2 pin 8 | Hardware recovery/debug access |
| GPIO42 / pin 48 | `JTAG_TMS` | Physical-pad JTAG | Input | Reserved for debug | J2 pin 2 | Hardware recovery/debug access |
| GPIO43 / pin 49 (`U0TXD`) | `IMPACT_SPI_CS_N` | SPI3 CS | Output | UART0 TX function is not used; impact CS has a 10 kOhm pull-up and R32 0 Ohm series link | U11 IIS3DWB10ISTR | Keeps the impact sensor on its dedicated SPI bus while leaving GPIO1 for ADC1 |
| GPIO44 / pin 50 (`U0RXD`) | `MMC_INT` | GPIO interrupt | Input | UART0 RX function is not used | U8 MMC5983MA INT through R19 100 kOhm pull-down | Gives the populated magnetometer a dedicated interrupt |
| GPIO45 / pin 51 | `VDD_SPI_STRAP` | VDD_SPI voltage strap | Input at reset | R13 10 kOhm pull-down selects 3.3 V VDD_SPI | Strap only | Makes the external 3.3 V flash selection explicit |
| GPIO46 / pin 52 | `STATUS_LED` | Addressable-LED data | Output after reset | ROM-log/boot strap with internal weak pull-down; WS2812 DIN is high impedance | WS2812B-2020 LED1 | Status indication without disturbing the reset strap level |
| GPIO47 / pin 37 (`SPICLK_P`) | `MOTION_INT2` | GPIO interrupt | Input | Non-strapping on ESP32-S3R8 | U12 LSM6DSV320XTR INT2 and TP13 | Second main-motion event/high-g interrupt |
| GPIO48 / pin 36 (`SPICLK_N`) | `POWER_ALERT_N` | Shared power interrupt / gauge wake | Input, with controlled low pulse for gauge wake if required | Non-strapping on ESP32-S3R8; R18 10 kOhm pull-up | TUSB320LAIRWBR INT_N, U7 BQ25611DRTWR INT and U14 BQ27427YZFR GPOUT | One open-drain alert line; firmware reads all three I²C devices after an assertion |

## Power-management allocation notes

- GPIO48 `POWER_ALERT_N` wire-ORs the open-drain BQ25611D `INT`, TUSB320LAIRWBR `INT_N` and BQ27427 `GPOUT` outputs. No device may actively drive the line high. On every assertion, firmware reads all three devices and services their causes.
- The shared-bus addresses are TUSB320LAIRWBR `0x47`, U6 BMP581 `0x46`, U7 BQ25611D `0x6B`, U8 MMC5983MA `0x30`, U13 TLV320ADC6120 `0x4E` and U14 BQ27427 `0x55`.
- U14 BQ27427 is in the protected positive high-current path. If it is DNP, fit its mutually exclusive at-least-3-A zero-ohm bypass. Never populate the gauge and bypass simultaneously.
- Raw battery `CELL_N_RAW` is distinct from system Earth and joins it only through R44, a 60 mOhm Vishay WSL2512R0600FEA Kelvin-sensed resistor used by U10 BQ298217. No ESP32 signal or bypass may join those two nets elsewhere.
- BMP581 `INT` stays local to the barometer block and its pull network. It is not connected to an ESP32 GPIO; firmware polls the device over I²C. GPIO44 remains the MMC5983MA interrupt input.
- GPIO3 `/CHG_CE_N` is held high by R20 during reset, so U7 charging defaults off. Firmware shall configure BQ25611D for 180 mA fast charge, 60 mA precharge, 60 mA termination, 4.190 V regulation and a source-safe IINDPM limit before changing GPIO3 to an output and driving it low.
- GPIO3 remains a JTAG-source strapping pin. Default ESP32-S3 eFuses use USB Serial/JTAG; any product variant that enables pad-JTAG strap selection must review the R20 pull-up and reset sampling behavior. GPIO45 and GPIO46 retain their documented strap constraints.
- Q1 is the active, low-leakage TI CSD87313DMS protection FET on the exact project DMS land, LCSC C2863848. The deprecated EFC8811R is not used and is not footprint-compatible.
- BT1 is the direct solder-wire interface for a pre-tabbed 18650 cell (default) or 21700 cell (alternate). TH1 is a two-pad solder-wire interface marked DNP for PCBA: the remote Semitec 103AT-2 10 kOhm NTC is hand-wired after assembly and is required unless firmware deliberately enables and validates the BQ25611D `TS_IGNORE` mode. Neither interface is a detachable connector.
- L2 is Coilcraft XFL4015-471MEC, 470 nH, for TPS63802. L4 is Eaton MPI4020V2-1R0-R, 1 uH, for BQ25611D.

## Switched battery-ADC fallback

The voltage-only fallback is supplied from protected `PACK_P`, not raw `CELL_P`:

```text
PACK_P -> U9 TPS22919DCKR IN
GPIO14 BAT_ADC_EN -> U9 ON; R25 100 kOhm from ON to Earth
U9 QOD tied to VOUT
U9 VOUT -> R23 1.0 MOhm -> BAT_ADC_SENSE -> R24 330 kOhm -> Earth
BAT_ADC_SENSE -> C34 100 nF -> Earth
BAT_ADC_SENSE -> GPIO1 / ADC1_CH0
```

Divider equations:

```text
Vadc = Vpack * 330,000 / (1,000,000 + 330,000)
     = Vpack * 0.2481203

Vpack = Vadc * (1,000,000 + 330,000) / 330,000
      = Vadc * 4.030303
```

At the BQ298217 4.25 V overvoltage threshold, `Vadc` is approximately 1.055 V, within the ESP32-S3 ADC1 range when configured for the 2.5 dB attenuation range. The divider's Thevenin resistance is approximately 248 kOhm and its 100 nF time constant is approximately 24.8 ms. Firmware shall enable GPIO14, wait at least 125 ms, discard the first conversion, average 32–64 conversions, apply ESP-IDF ADC calibration and use production two-point voltage calibration. GPIO14 must return low after measurement.

Sources: [ESP32-S3 datasheet](https://www.espressif.com/sites/default/files/documentation/esp32-s3_datasheet_en.pdf), [ESP-IDF ADC documentation](https://docs.espressif.com/projects/esp-idf/en/stable/esp32s3/api-reference/peripherals/adc/index.html), [BQ25611D datasheet](https://www.ti.com/lit/ds/symlink/bq25611d.pdf), [TPS22919 datasheet](https://www.ti.com/lit/ds/symlink/tps22919.pdf), [BQ27427 datasheet](https://www.ti.com/lit/ds/symlink/bq27427.pdf).

## Dedicated memory pins

| QFN pins | Schematic handling | Use |
|---|---|---|
| Pin 28 `SPICS1`; pins 38-42 `GPIO33`-`GPIO37` | Deliberately marked no-connect at the board level and documented as package-internal | ESP32-S3R8 in-package octal-PSRAM CS, IO4-IO7, and DQS signals; never allocate these to peripherals |
| Pins 30-35 `SPIHD`, `SPIWP`, `SPICS0`, `SPICLK`, `SPIQ`, `SPID` | Dedicated point-to-point QSPI nets | External W25Q128JVSIQ flash; these pins are not general-purpose GPIO in this design |
| Pin 29 `VDD_SPI` | Dedicated 3.3 V memory-power output from U3 | U3 sources `VDD_SPI`; the rail supplies U4 external flash and the memory I/O domain. It is intentionally not fed separately from +3V3 |

GPIO47 and GPIO48 are shown by the generic KiCad symbol under their alternate `SPICLK_P` and `SPICLK_N` names. They are normal GPIO47/GPIO48 in this 3.3 V ESP32-S3R8 topology and are not part of the in-package octal-PSRAM mapping above.

## I2C pull-up implementation

The saved schematic has one explicit +3V3 pull-up on each shared I²C line: R1 4.7 kOhm on SCL and R2 4.7 kOhm on SDA. MCP net readback verified those endpoints. R39/R43 with C55/C59 form the differential microphone coupling path, while C51 100 nF and C52 1 uF decouple MICBIAS; none of those audio parts is an I²C pull-up. Measure the assembled-bus capacitance before selecting 400 kHz operation; do not rely on undocumented sensor-internal pull-ups.

## Recovery interfaces

- Native USB on GPIO19/GPIO20 remains the primary programming and recovery interface.
- Physical-pad JTAG remains on GPIO39-GPIO42 through J2, a Harwin M50-3600542R 2x5 1.27 mm vertical SMD header.
- GPIO3 controls `/CHG_CE_N` but is sampled as a JTAG-source strap during reset; preserve the R20 high default and the firmware sequencing above.
- GPIO43/GPIO44 are intentionally consumed by `IMPACT_SPI_CS_N` and `MMC_INT`; a separate UART0 header is not present in the current schematic.
- BMP581 has no MCU interrupt connection and is polled over I²C.
