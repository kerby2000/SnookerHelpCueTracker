# Cue Tracker hierarchical hardware handoff

Date: 2026-07-15

The authoritative project is [`CueTracker.kicad_pro`](../../CueTracker.kicad_pro). Its schematic hierarchy is:

- [`CueTracker.kicad_sch`](../../CueTracker.kicad_sch): hierarchy root and rear/front board interface.
- [`rear_main.kicad_sch`](../../rear_main.kicad_sch): ESP32-S3-PICO-1, USB-C, RF, battery/protection, charger, 3.3 V conversion, audio and HMI.
- [`front_sensor.kicad_sch`](../../front_sensor.kicad_sch): LSM6DSV320X, IIS3DWB10IS, MMC5983MA and BMP581.

## Architecture contract

- MCU: Espressif `ESP32-S3-PICO-1-N8R8`, with 8 MB in-package flash, 8 MB in-package octal PSRAM, in-package 40 MHz crystal and SiP RF network. The previous bare ESP32-S3R8, W25Q128 and external 40 MHz network are removed.
- RTC: the external 32.768 kHz crystal is retained as a supported low-frequency-clock option. Firmware must explicitly select it and tolerate startup failure; make Y2/C30/C31 a controlled DNP group if firmware or measured timing/energy results do not justify it.
- Rigid-board link: both boards use Hirose `FH34SRJ-24S-0.5SH(50)`, LCSC `C324726`, with the exact 24-pin map in [`gpio_allocation.md`](gpio_allocation.md).
- HMI: an eight-pin Hirose FPC interface targets a 1.14-inch, 135 x 240, 3.3 V ST7789 daughterboard with four-wire SPI and no touch. The project connector map is not a claim about a raw panel FPC.
- Debug/recovery: native USB Serial/JTAG, BOOT and RESET. The physical JTAG header is removed because GPIO39-GPIO42 serve the HMI.

## Power and battery contract

- Reference cell: Samsung INR18650-35E with factory-welded tabs soldered into plated PCB slots, a remote 10 kOhm NTC on DNP solder pads, and a mechanically retaining cradle. Solder joints must not retain the cell.
- Independent protection: BQ298217, CSD87313DMS and `WSL2512R0200FEA` 20 mOhm, 1%, 1 W, 2512-class Kelvin shunt. Nominal threshold targets are approximately 1.8 A charge overcurrent, 3.0 A discharge overcurrent and 10 A short circuit; tolerance and temperature validation remain required.
- Gauge variants: the default `R0_3A` build makes BQ27427 DNP and fits its mutually exclusive at-least-3-A bypass. The optional gauge build fits BQ27427, leaves the bypass open and limits long-term RMS path current to 2 A or less. Never fit both paths.
- Charger: BQ25611D with NVDC power path. Hardware keeps charge disabled through reset; firmware first disables charge, keeps OTG off, uses the 1.0 A normal policy, and allows 1.5 A only after thermal validation. Charger D+/D- are unused/test pads only.
- 3.3 V source: TPS63802 buck-boost. Espressif's at-least-500-mA source guidance governs peak sizing even though the representative application average is near 200 mA.
- All high-current cell, protector, bypass, charger and USB paths require at least 3 A normal-current capability plus suitable fault-transient margin.

## USB-C contract

`USB-C VBUS -> connector-adjacent ESD441-class TVS -> TPS25947-class approximately-3-A eFuse/current limiter -> VBUS_PROTECTED -> BQ25611D`

- TUSB320LAI handles CC attach/orientation/current advertisement; it is not USB PD.
- CC1 and CC2 use connector-adjacent TPD2E2U06-class ESD protection.
- ESP32-S3-PICO-1 owns D+/D-, protected by the retained USBLC6-2SC6 network.
- A powered-off-safe buffer provides direct `VBUS_PRESENT` to GPIO48.
- No 500 mA PPTC assumption remains. Receptacle contacts, vias and VBUS copper must support the 3 A design class.

## HMI and sensor firmware rule

GPIO10/GPIO11 source both the front motion SPI clock/MOSI and the HMI clock/MOSI branches. During `ARMED` and `SHOT_CAPTURE`, firmware must issue no display SPI transactions, must not change `LCD_BL`/`HMI_EN`, must leave `LCD_CS_N` inactive and must not reconfigure the shared pins.

The front connector retains `MMC_INT`, `BMP_INT` and `SENSOR_PWR_EN`. Place MMC5983MA at the extreme front with nonmagnetic fasteners. Give BMP581 a separate ePTFE atmospheric vent. Give IM73A135 a sealed external acoustic chimney, separate from the pressure vent, and expose TLV320ADC6120 channel 2 on test pads or an optional expansion interface.

## Drawing and library contract

- Use wires within a logical block and hierarchical labels only at real sheet boundaries.
- Keep the user-arranged block placement; do not auto-reflow the child sheets.
- Use `Device:R_Small` and `Device:C_Small`, value-only Value fields, 40 mil text, and capacitor `Dielectric`/`Voltage` properties.
- The registered project-symbol source of truth is [`CueTracker_Exact.kicad_sym`](../../CueTracker_Exact.kicad_sym). The project footprints are in [`CueTracker_Exact.pretty`](../../CueTracker_Exact.pretty), and imported mechanical models are in [`CueTracker.3dshapes`](../../CueTracker.3dshapes).
- `cust_sym.kicad_sym` and other unregistered legacy/reference libraries do not update placed symbols. After a deliberate library edit, update the selected symbol from the registered library; F5 is only a redraw.

## Documentation

- [`decision_log.md`](decision_log.md): architecture and assembly decisions.
- [`gpio_allocation.md`](gpio_allocation.md) and [`gpio_allocation.csv`](gpio_allocation.csv): MCU, front-link and HMI pin contracts.
- [`power_budget.md`](power_budget.md): design current budget and charger/USB policy.
- [`power_flag_contract.md`](power_flag_contract.md): justified ERC power annotations.
- [`source_register.md`](source_register.md): manufacturer-source and CAD provenance register.

## Verification status

The saved hierarchy passes KiCad MCP ERC with **0 errors and 0 warnings**. The final netlist contains 172 components and 159 nets; both 24-pin connectors and the 8-pin HMI connector match their normative maps. The 172-row field-rich BOM, three-page PDF, per-sheet SVGs, rendered PNGs, saved-file hashes and fresh-process MCP readback are recorded in [`erc_report.md`](erc_report.md).

Schematic ERC does not validate RF tuning/keepout, regulator thermal performance, USB or battery copper ampacity, shunt Kelvin geometry, protection FET SOA, connector mirroring, land-pattern manufacturability, enclosure venting or MEMS placement. Carry those checks into PCB layout and hardware validation.
