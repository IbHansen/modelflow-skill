# MAKRO names in the ModelFlow translation

Facts counted on the 2026-September translation (`makro26_baseline.pcimz`,
39 034 names: 20 474 endogenous, 18 560 exogenous, from 1 249 MAKRO names).
Another release or another translation can differ – check the model you have.

## From GAMS to ModelFlow

| GAMS | ModelFlow | Rule |
| --- | --- | --- |
| `qBNP[t]` | `QBNP` | upper case; `t` becomes the row of the DataFrame |
| `pC[cTot,t]` | `PC__CTOT` | `__` before each index element |
| `qI_s[iM,spTot,t]` | `QI_S__IM__SPTOT` | elements in the GAMS domain order; the `_s` belongs to the name |
| `tAfg_y_k[i_,ds,s,t]` | `TAFG_Y_K__IB__BOL__TJE` | up to three index elements |
| `nPop[a,t]` | `NPOP__45` | ages are numbers 0-101 |
| `eHh` (no `t`) | `EHH` | constants become constant columns |
| `x[t-1]`, `x[t+1]` | `X(-1)`, `X(+1)` | lags and leads are not part of the name |
| `x[tBase]` | `X(2020)` | fixed-year reference, no new name |

Characters other than letters, digits and `_` become `_`. GAMS is
case-insensitive, so upper case loses nothing for the model – but the CamelCase
that shows where the prefix ends is gone: `VTMOMS` could be read `v` + `tMoms`
or `vt` + `Moms`. The original name is kept at the end of the description.

Index counts: 17 371 names with one element, 16 757 with two, 594 with three
(only the `_m_k` / `_y_k` tax and subsidy variables).

## Descriptions

```
Imputeret prisindeks for forbrugskomponenter ... [CTOT] (MAKRO pC)
<DREAM's Danish text>                            [elements] (MAKRO original name)
```

- The text is DREAM's own, in Danish. Search in Danish:
  `mmakro['!*forbrug*']`, `mmakro['!*BNP*']`.
- `Kilde: ADAM[fY]` names the ADAM series the data comes from (235 MAKRO names
  carry one). This is the bridge to ADAM names, see `mf-naming`.
- Names ModelFlow or the translator generated have English texts (`TEND`,
  `TVAL`) or none (`_D`, `_X`).

## Totals and special elements

| Element | Meaning |
| --- | --- |
| `TOT` | total of the set: sectors (`sTot`, `rTot`), portfolio (`Tot`), ages (`tot`), transfers (`tot`) |
| `SPTOT`, `SBYTOT` | private sectors, private urban industries |
| `CTOT`, `XTOT`, `ITOT`, `GTOT`, `DTOT` | demand totals, keep their GAMS names |
| `PENSTOT`, `HHTOT`, `UDLTOT` | all pensions, all transfers to households / abroad |
| `NA` | the element before age 0 (`x[a-1]` at the first age): 8 names, all zero |

`QBNP` (GDP), `VSALDO` (government balance), `VHW` (hourly wage) and other
national totals have no index at all.

## Names the translation adds

| Name | Meaning |
| --- | --- |
| `X___RES` | residual of an equation kept implicit (374 endogenous, from 34 GAMS equations). `X` itself is solved through it but is listed among the exogenous variables |
| `X_D`, `X_X` | ModelFlow's fix switch (1 652 pairs): `_D` = 1 uses `_X`. Used where GAMS fixes the variable in some years, in the terminal year, and for the 39 variables GAMS leaves out in the first year of a run (`rAktieDrift`, `rVirkDisk` ...) |
| `TEND`, `TEND2` | 1 in the terminal year(s), else 0: selects the terminal-year equation |
| `TVAL` | the year (`t.val` in GAMS) |
| `FQ`, `FP`, `FV`, `FQT` | MAKRO's own growth adjustment factors, kept as variables |

Lists in the model source (`A_PREV`, `S_IF_D1IOY_CTJE`, `<L>_VAL`) are
sublists of `doable`, not variables.

## Finding a name

```python
mmakro['QC__*'].names              # all consumption quantities
mmakro['QC__CTOT'].des             # the Danish text and the MAKRO name
mmakro['!*forbrug*'].names         # by Danish description
mmakro['#Headline'].names          # the display groups (if the file has them)
```

The variable groups saved with the translation (`#Headline`,
`#Prices_and_wages`, `#Labour_market`, `#Public_finances`, ...) are a good start
for a user who does not read Danish.

## Units

`P`, `Q`, `V` variables are growth- and inflation-adjusted (see
`prefixes.md`). A percentage deviation from a baseline is the same in adjusted
and ordinary units; a level or a growth rate is not.
