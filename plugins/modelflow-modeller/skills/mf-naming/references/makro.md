# MAKRO names (DREAM)

Reading MAKRO names – the prefix system, the Danish words, the set elements,
the ModelFlow form, the decoder script and the list of all names in a release –
is the job of `mf-makro-names` in `modelflow-user`. This page keeps what matters
when *building* or extending a translation.

Authority: the README of DREAM's repository
(https://github.com/DREAM-DK/MAKRO/blob/main/README.md) and the GAMS code of the
chosen release. MAKRO is DREAM's model, not Danmarks Nationalbank's.

## Prefixes in one line

`p` price, `q` quantity, `v` value, `nv` present value, `n` persons, `h` hours,
`r` rate/ratio, `t` tax rate, `e` elasticity, `u` scale parameter, `f` factor,
`j` additive residual, `jf` multiplicative residual, `s` structural, `m` marginal,
`d` derivative, `E` expectation. They stack (`vt` tax revenue, `jr` residual on a
rate). `p`, `q`, `v` are growth- and inflation-adjusted. A MAKRO `j` is not an
ADAM `J` and not a ModelFlow `_A`.

## GAMS to ModelFlow

| GAMS | ModelFlow |
| --- | --- |
| `pC[c,t]` in an equation | `PC__{C}` in a `doable` line |
| `pC['cTot',t]` | `PC__CTOT` |
| `qI_s[iM,spTot,t]` | `QI_S__IM__SPTOT` (elements in domain order) |
| `t` | the DataFrame row index |
| `x[t-1]`, `x[tBase]` | `X(-1)`, `X(2020)` |
| an index symbol (`a`, `s`, `d_`) | a list of the same name (`A`, `S`, `D_`) |
| a `$`-condition | a 0/1 sublist, `S_IF_<condition>[_<OUTER>]` |
| `x[a-1,t]` | `X__{A_PREV}`; `NA` before the first age (a zero column) |

Element names are cleaned (`clean_name`: non-alphanumerics to `_`, upper case;
see `mf-import`, `references/gams-to-makemodel.md`). Total elements keep their
GAMS names: `TOT` (from `tot` and `Tot`), `CTOT`, `XTOT`, `ITOT`, `GTOT`,
`SPTOT`, `PENSTOT`. A sublist name must not equal a list name or another looped
list's sublist name.

## Names a translation adds

`X___RES` for equations kept implicit, the `X_D` / `X_X` switch where GAMS fixes
the variable in some years (and in the first year of a run for equations with
`$tx1[t]`), `TEND` for the terminal-year equation, `TVAL` for `t.val`. Keep them
out of the MAKRO namespace: they are not DREAM names.

## Descriptions

Write DREAM's text with the original name last:
`<text> [ELEMENTS] (MAKRO pC)`. Upper case loses the CamelCase, and that tail is
how `mf-makro-names` gets it back; its `build_makro_names.py` rebuilds the name
list from a translation that follows this format.
