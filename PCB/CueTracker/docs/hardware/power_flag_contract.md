# CueTracker power-flag contract

`PWR_FLAG` is an ERC annotation, not an electrical source and not a PCB part. It tells KiCad that a net which is physically energized has a valid source even though the source path is represented only by passive pins, connector pins, a battery symbol, a protection FET, an inductor, a ferrite bead, or an IC pin whose library electrical type cannot express its operating mode.

The rule for this schematic is: use one flag on each electrically distinct powered domain that otherwise has no `power_out` pin. Do not place flags on every power symbol, and never use a flag to hide a missing physical connection.

## Required flags

| Flagged net | Physical source/path | Why KiCad needs the flag | Decision |
|---|---|---|---|
| `VBUS` | External USB-C source through J1 | USB connector pins are passive, so ERC cannot infer that an attached source drives the 5 V input rail. | Keep one |
| `VDD_SPI` | ESP32-S3 VDD_SPI output, normally 3.3 V from VDD3P3_RTC through the chip's internal path | The project symbol models VDD_SPI as a power-input pin even though this design uses it as the flash-supply output. The flag documents that selected operating mode. | Keep one |
| `Earth` | Common system return tied to USB shield/return and protected battery return | Ground/power symbols do not create a driving pin. One flag is sufficient for the complete common return domain. | Keep one |
| `+3V3_RF` | `+3V3` through RF inductor L1 | The passive inductor creates a distinct ERC net after the regulator's `power_out` pin. | Keep one on the filtered side |
| `+3V3_AUDIO` | `+3V3` through ferrite bead FB1 | The passive bead creates a distinct ERC net after the regulator's `power_out` pin. | Keep one on the filtered side |
| Protection VDD (`Net-(U10-VDD)`) | Cell positive through R30 (300 ohm) | R30 is passive, so U10 VDD has no visible `power_out` driver even though the cell supplies it. | Add one after R30 |
| `CELL_N_RAW` | External cell negative, before the current-sense shunt/protection boundary | BT1 is passive and the raw cell-negative domain is intentionally separate from system Earth. | Add one |
| `PACK_P` | Cell positive through the back-to-back protection FET Q1 | Battery and MOSFET pins are passive; ERC cannot infer the protected pack rail is energized. | Add one on the protected side |
| `CHG_BAT` | Battery/charger connection through the BQ27427 sensing boundary; JP1 is only a DNP bypass | No symbol on this electrically distinct rail is typed as a power output. | Add one |

## Rails that must not receive an extra flag

- `+3V3`: TPS63802 U5 VOUT is a real `power_out` source.
- `VSYS`: BQ25611D U7 SYS is the charger/NVDC power-path output.
- `REGN`: BQ25611D U7 REGN is an internal regulator output.
- Raw cell positive before R30: the relevant ERC consumer is on the post-R30 protection-VDD net; a second flag on raw cell positive would not satisfy that consumer and would add no useful information.

## Review rule

When ERC reports `power input not driven`, first trace the real source and every passive boundary. Add a flag only if the physical power path is complete and KiCad's pin types cannot represent it. If no physical source exists, repair the circuit instead of adding a flag.

