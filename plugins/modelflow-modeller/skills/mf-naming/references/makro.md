# MAKRO names (DREAM)

Authority: the README of DREAM's repository
(https://github.com/DREAM-DK/MAKRO/blob/main/README.md) and the GAMS code of the
chosen release. MAKRO is DREAM's model, not Danmarks Nationalbank's.

## Prefixes (longest match first: `jf`, `nv` before `j`, `n`)

| Prefix | Meaning |
| --- | --- |
| `j` | additive residual |
| `f` | multiplicative factor |
| `jf` | multiplicative residual |
| `E` | expectation operator |
| `d` | derivative, e.g. `dY2dX` |
| `s` | structural version |
| `m` | marginal |
| `u` | scale/share parameter (μ in the documentation) |
| `t` | tax/transfer rate |
| `r` | rate or ratio |
| `e` | elasticity/exponent |
| `p` | price, adjusted for steady-state inflation |
| `q` | quantity, adjusted for steady-state productivity growth |
| `v` | nominal value, adjusted for both |
| `nv` | present value, adjusted for both |
| `n` | number of persons |
| `h` | hours |

Roots: `C` consumption, `Y` output, `K` capital, `L` labour ... Multi-word names
are CamelCase after the prefix: `nOrlovRest`, `jvUdlAktRenter`.

`p`, `q`, `v` are growth-adjusted, not raw prices and quantities – matters when
comparing with another model. A MAKRO `j` is not an ADAM `J`.

## Indices

GAMS sets in brackets: `pC[c,t]` price of consumption group `c`, `qC[c,t]` the
quantity, `pC[cTot,t]` the aggregate.

## In ModelFlow

GAMS is case-insensitive, and the GDX importers and `doable` use upper case and
`__` between name and index elements:

| GAMS | ModelFlow |
| --- | --- |
| `pC[c,t]` in an equation | `PC__{C}` in a `doable` line |
| `pC['cTot',t]` | `PC__CTOT` |
| `t` | the DataFrame row index |

Element names are cleaned by `clean_name` (see `mf-import`,
`references/gams-to-makemodel.md`). The CamelCase is lost on upper-casing, so
`jvUdlAktRenter` becomes `JVUDLAKTRENTER`: keep the original name in the
description.
