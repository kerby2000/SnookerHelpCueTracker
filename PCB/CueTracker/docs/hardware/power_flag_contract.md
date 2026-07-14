# Cue Tracker power-flag contract

Date: 2026-07-15

`PWR_FLAG` is an ERC annotation. It is not a voltage source, a protection device or a PCB part. Place one only when the physical source path is complete but KiCad cannot see a `power_out` pin because the source crosses a passive connector, resistor, bead, inductor, battery pad, shunt or protection FET.

For the hierarchical design, the flag belongs on the child sheet that contains the physical source path. Do not duplicate it at the hierarchy root or on the other rigid-board sheet. A flag must never be used to hide an open wire, an incorrectly typed pin or a missing regulator connection.

## Intended flags

These are the only justified powered domains in the present architecture. Reference numbers may change during final annotation; the net and reason are the contract.

| Net | Physical source/path | Why ERC cannot infer the source | Decision |
|---|---|---|---|
| `VBUS_RAW` | External USB-C source through the passive receptacle contacts, before ESD441 and TPS25947 | Connector pins do not provide a KiCad `power_out` driver | One flag beside the receptacle input only |
| `Earth` | Common circuit return on the protected/system side of the battery shunt | Power symbols name the return domain but do not drive it | One flag for the complete system-return domain |
| `+3V3_RF` | `+3V3` through the RF filter inductor/bead | The passive filter creates a distinct net after the TPS63802 output | One flag on the filtered RF side |
| `+3V3_AUDIO` | `+3V3` through FB1 | The ferrite bead creates a distinct net after the TPS63802 output | One flag on the filtered audio side |
| `+3V3_SENSOR` | TPS63802 `+3V3` output through R62, the deliberate 0-ohm sensor-rail naming link | R62 is passive, so ERC cannot propagate the TPS63802 `power_out` type onto the separately named hierarchical rail | One flag after R62 on the rear sheet only; never duplicate it on the front sheet |
| Protector VDD, currently `Net-(U10-VDD)` | Raw cell positive through R30 to BQ298217 VDD | R30 is passive and isolates the protector-supply net from any visible `power_out` pin | One flag after R30, not on both sides |
| `CHG_BAT` | Charger battery node reached through the mutually exclusive BQ27427 or at-least-3-A bypass path | Gauge/bypass pins are passive and neither build option exposes a `power_out` pin | One flag on the charger side of the selection path |
| `PACK_P` | Protected cell positive after the BQ298217-controlled back-to-back FET | Battery pads and MOSFET pins are passive | One flag on the protected pack rail |
| `CELL_N_RAW` | Raw cell negative before R44 | Battery pads are passive; this domain is intentionally isolated from system Earth by the 20 mOhm shunt | One flag on the raw-cell side only |

## Saved reference assignment

Fresh saved-schematic traversal gives the following exact reference-to-net map:

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

These are the only nine `PWR_FLAG` instances. The final KiCad MCP ERC result is 0 errors and 0 warnings.

## Nets that must not receive another flag

- `VBUS_PROTECTED`: TPS25947 OUT is the real protected-source output. If ERC does not recognize it, fix the eFuse symbol pin type or connectivity rather than adding a flag.
- `VSYS`: BQ25611D SYS is the NVDC power-path output.
- `REGN`: BQ25611D REGN is an internal regulator output.
- `+3V3`: TPS63802 VOUT is a real regulator output.
- `+3V3_SENSOR_SW`: the front-board TPS22919/load-switch VOUT is the source for the switched sensor rail.
- `+3V3_HMI`: the rear HMI load-switch output is the source for the daughterboard rail.
- ESP32-S3-PICO-1 `VDD_SPI` and internal flash/PSRAM nodes: these are package-internal connections and are not board power rails.
- Raw cell positive before R30: the consumer that needs annotation is on the post-R30 protector-VDD net.

## Battery-return safety rule

`CELL_N_RAW` and `Earth` are different electrical nets. They meet only through the 20 mOhm Kelvin shunt in the intended protection/sense path. Placing an Earth symbol on `CELL_N_RAW`, or a flag that masks an accidental direct join, defeats the BQ298217 current thresholds.

## Review sequence

When ERC reports “power input not driven”:

1. Trace the physical source and every passive boundary in the saved netlist.
2. Confirm the relevant regulator, eFuse, charger or load-switch output pin type.
3. Repair missing wires or hierarchy labels first.
4. Add a single flag only if the completed physical path still has no visible `power_out` pin.
5. Re-run ERC and inspect the net endpoints; do not suppress the violation.

The final ERC report lists the same references and nets after saved-file MCP readback. Do not add another flag without updating both this contract and the report.
