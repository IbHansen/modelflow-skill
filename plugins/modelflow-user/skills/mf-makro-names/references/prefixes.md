# MAKRO prefixes

## The documented list

From the README of DREAM's repository (2026-September release). The prefix is
the lower-case run before the first capital letter of the name.

| Prefix | Meaning | Example |
| --- | --- | --- |
| `j` | additive residual (J-term) | `jvBNI` |
| `f` | factor, unspecified multiplicative parameter | `fDisk` discount factor |
| `jf` | multiplicative residual (a residual added to a factor) | `jfpIOy` |
| `E` | expectation operator (rare: leads are the model-consistent expectations) | `EpC`, `EmUC` |
| `d` | derivative: `dY2dX` = ∂Y/∂X | `dFF2dLoen` |
| `s` | structural version of the variable | `snL`, `sqBVT` |
| `m` | marginal (where marginal and average differ) | `mtInd` marginal tax rate |
| `u` | scale parameter (μ in the documentation) | `uBVT` |
| `t` | tax rate | `tMoms_y` |
| `r` | unspecified rate or ratio | `rBVTGab` output gap |
| `e` | exponent, typically an elasticity | `eC` |
| `p` | price, adjusted for steady-state inflation | `pC` |
| `q` | quantity, adjusted for steady-state productivity growth | `qC` |
| `v` | value (= p·q), adjusted for both | `vC` |
| `nv` | present value, adjusted for both | `nvBNP` |
| `n` | number of persons | `nPop` |
| `h` | hours | `hL` |

`p`, `q`, `v` are *growth- and inflation-adjusted*: divided by the steady-state
factors `fpt`, `fqt`, `fvt` (`fqt = fq**(t - tBase)`). They are not the raw
national-accounts numbers. Multiply by the factor to report in ordinary units
(in the ModelFlow translation only `FQT` is a model variable; `fpt` and `fvt`
are in DREAM's `baseline.gdx`).

## Prefixes stack

Prefixes combine from the left, each modifying what follows:
`jr` = residual on a rate, `vt` = value of a tax (revenue), `nvt` = present value
of that revenue, `mr` = marginal rate, `sn` = structural number of persons,
`ft` = correction factor on a tax rate, `uv` = scale parameter on a value,
`jfp` = multiplicative residual on a price.

Counts of the 1 249 names in the release (most frequent first):

| Prefix | Names | Reading | Example |
| --- | --- | --- | --- |
| `v` | 291 | value | `vHhx` household wealth excl. pension and housing |
| `r` | 181 | rate or ratio | `rOffTilHhKap2BNP` |
| `q` | 89 | quantity | `qBNP` |
| `p` | 73 | price | `pBNP` |
| `vt` | 64 | tax revenue | `vtMoms` |
| `u` | 60 | scale parameter | `uBidragAK` |
| `t` | 45 | tax rate | `tAfg_y` |
| `nv` | 36 | present value | `nvBNP` |
| `rp` | 36 | relative lagged price (see below) | `rpC` |
| `jr` | 27 | residual on a rate | `jrHhAktRenter` |
| `nvt` | 27 | present value of a tax revenue | `nvtMoms` |
| `n` | 26 | number of persons | `nPop`, `nL` |
| `jv` | 19 | residual on a value | `jvHhxAfk` |
| `f` | 18 | factor | `fDisk` |
| `e` | 15 | elasticity / exponent | `eHh` |
| `d` | 14 | derivative | `dArv` |
| `ft` | 14 | correction factor, actual to implicit tax rate | `ftBund` |
| `sn` | 14 | structural number of persons | `snL` |
| `mr` | 13 | marginal rate / return | `mrHhxAfk` |
| `fu` | 10 | correction factor on scale parameters | `fuIO` |
| `jp` | 9 | residual on a price | `jpW` |
| `fp` | 8 | factor on a price; `fp` alone: inflation adjustment 1 + gp | `fpCPI` |
| `h` | 8 | hours | `hL2nL` hours per employed |
| `sr` | 8 | structural rate | `srJobFinding` |
| `dv`, `dn`, `dnv` | 11 | derivative of a value / a number | `dvHhAkt2dvBolig` |
| `jfp` | 7 | multiplicative residual on a price | `jfpIOy` |
| `mt` | 6 | marginal tax rate | `mtInd` |
| `up` | 6 | scale parameter for a price (inertia) | `upYTraeghed` |
| `uv` | 6 | scale parameter for a value | `uvGKol` |
| others | ≤ 5 each | read by stacking | `jsqBVT`, `smrMarkup`, `rvt...` |

`fq`, `fp`, `fv` alone are the one-year adjustment factors (1 + gq, 1 + gp,
(1 + gq)(1 + gp)); `fqt` is the cumulative factor `fq**(t - tBase)`, so its `t`
is time, not tax. `qtNetYOff` / `ptNetYOff` are the quantity and price of a tax
(`tNetYOff`), read by stacking.

## Prefixes not in the README

Seen in the 2026-September code, meaning taken from the variable texts:

| Prefix | Meaning | Names |
| --- | --- | --- |
| `rp` | relative lagged prices weighted with current quantities: the chained aggregate over the plain sum of its parts (`E_rpC`: `qC[cTot,t] = rpC[t] * sum(c, qC[c,t])`) – not a growth rate. Exception: `rpCInflSnit` is `r` + `pCInflSnit`, a moving average of consumer price inflation | `rpBNP`, `rpC`, `rpCGI` ... |
| `c` | additive term in an asset equation (`cHh_a` age-dependent, `cHh_t` time-varying) | `cHh_a`, `cHh_t` |
| `cr` | interest spread to a reference rate | `crRenteBank`, `crRenteFast` ... |
| `budgetfaktor` | no prefix: the cyclical sensitivity of general items in the budget | `budgetfaktor` |

Treat any other new combination as *stacked* and confirm with the text.

## Suffixes after `_`

The underscore inside a MAKRO name is part of the name (ModelFlow keeps it:
`cHh_a` → `CHH_A`). Do not confuse it with ModelFlow's `__` index separator.

| Suffix | Meaning | Example |
| --- | --- | --- |
| `_a` | age-dependent part of a variable or parameter | `ftBund_a`, `rSplurge_a` |
| `_t` | time-varying (age-independent) part | `ftBund_t`, `jrJobFinding_t` |
| `_s` | by the sector that uses it (e.g. investment by investing sector) | `qI_s`, `fpI_s` |
| `_y` | from domestic production | `tMoms_y`, `vtAfg_y` |
| `_m` | from imports | `tMoms_m`, `vtAfg_m` |
| `_k` | of capital goods (with `_y_k`, `_m_k`) | `tAfg_y_k` |
| `_vaekst` | growth factor | `snLHh_vaekst` |
| `_Over100` | persons over 100 | `nPop_Over100` |
| `_DA` | the Confederation of Danish Employers' area | `vhW_DA` |
| other | read from the text (`_NR` national accounts, `_gns` average, `_lag` lagged) | `qC_NR`, `pK_gns` |

## Things that are easy to get wrong

- A MAKRO `j` is a residual (zero or calibrated), not ADAM's `J` add factor and
  not ModelFlow's `_A`. In the ModelFlow translation `j` variables are ordinary
  exogenous variables.
- `t` is a tax rate, `vt` the revenue; `T` inside a word is part of the word.
- `E` is upper case and only in `EpC`, `EmUC`, `ErOverlev`.
- `m` alone in `mUC` is "marginal" (marginal utility of consumption), not imports;
  imports are the root `M` (`qM`, `pM`) or the suffix `_m`.
- `s` as prefix is "structural"; `s` as index is sector.
- Element and root share letters: `qC[cTot]` is consumption, `qI[iB]` building
  investment – the index element repeats the root's letter.
