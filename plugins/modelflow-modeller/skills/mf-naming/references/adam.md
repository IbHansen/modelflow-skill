# ADAM names (Statistics Denmark)

Authority: Statistics Denmark's *Nomenklaturregler*
(https://www.dst.dk/ext/adam/Nomenklatur--pdf) and the variable list of the
chosen release. ADAM and its databank end in 2026; note the release you use.

## Structure

`[operator][class][suffixes]`. A one-letter **class** comes first or straight
after an operator. In the documentation upper-case classes are mostly flows and
stocks, lower-case ones prices, rates and ratios. Suffixes narrow the meaning,
often in aggregation order; some names are irregular.

## Technical operators (match the longest first)

| Op | Meaning | In ModelFlow (Gekko import) |
| --- | --- | --- |
| `JR` | multiplicative adjustment | `_A` (made additive) |
| `JD` | adjustment in a difference relation | `_A` |
| `J` | additive adjustment | `_A` |
| `D` | exogenization dummy | `_D` |
| `Z` | exogenized value of an endogenous variable | `_X` |

In the Gekko `.frm` these are implied by the FRML code (`_SJRD` ...), not
written in the equation; `Makemodel(type_input='gekko')` maps J and D to `<STOC>`,
J only to `<ADD>`, D only to `<EXO>`.

## Other operators

`b` share/ratio, `f` chained volume, `k` correction/conversion, `n` number,
`p` price, `r` growth rate, `t` tax/transfer rate, `w` weight.

## Classes

`C` consumption, `E` exports, `H` hours, `I` investment, `K` capital, `M` imports,
`Q` employment, `S` taxes, `T` transfers, `U` population/labour force,
`V` production inputs, `W` financial assets/wealth, `X` production,
`Y` income/GDP; also `Inv` depreciation, `O` revaluations, `d` dummy, `dt` trend,
`iw` interest rate, `l` wage, `ui` user cost.

## Suffixes (samples – check combinations in the release list)

- Industries: `a` agriculture, `b` construction, `e` extraction, `h` housing,
  `o` public services, `ne` energy supply, `nf` food manufacturing, `ng`
  petroleum, `qf` financial services, `qs` shipping.
- Consumption groups: `Cp` private, `Cf` food, `Ch` housing, `Cb` vehicles,
  `Cs` services.
- Account sectors: `cf` financial firms, `cr` non-financial firms, `e` rest of
  the world, `h` households, `o` government, `z` residual.
- Sectors: `o1` public, `p1` private.

`p` depends on position: first it is price; as a suffix it can be "private".
`W` names read creditor / instrument / debtor in that order, not as a plain
suffix chain.

## Examples

- `pcf`: `p` price of `C` consumption, `f` food → price of food consumption
  (nomenclature example).
- `fCp`: chained volume of private consumption (verify in the release).
- `JfCp`: additive adjustment of `fCp` → `FCP_A` after import.

## In ModelFlow

Upper case: `pcf` → `PCF`, `fCp` → `FCP`. Parse operator, class and suffixes by
position; case gives no help. Descriptions from the release's variable list are
the place to confirm meaning.
