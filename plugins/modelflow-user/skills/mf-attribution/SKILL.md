---
name: mf-attribution
description: >
  This skill should be used when explaining why a ModelFlow result changed: "why did
  GDP change", "attribution", "decomposition", "dekomp", "totdif", "contribution of
  each shock", "which input drives", "explain the difference between scenarios",
  "what explains consumption", or "impact of each policy".
metadata:
  version: "0.1.0"
---

# Explaining a difference

Attribution compares the last solution (`mpak.lastdf`) with the baseline
(`mpak.basedf`). Solve the scenario first.

## Model-wide: which shock caused it (`totdif`)

```python
scen = baseline.upd('''
<2025 2035> PAKGGREVCO2CER PAKGGREVCO2GER PAKGGREVCO2OER = 30
<2025 2035> PAKGGREVGNFSXN + 1
''')
res = mpak(scen, 2025, 2035, keep='Carbon and GST')

td = mpak.totdif(summaryvar='PAKNYGDPMKTPKN PAKNECONPRVTKN',
                 experiments={'Carbon tax': ['PAKGGREVCO2CER', 'PAKGGREVCO2GER', 'PAKGGREVCO2OER'],
                              'GST': ['PAKGGREVGNFSXN']})
td.totexplain('PAKNYGDPMKTPKN', vtype='all')     # every period, stacked bars
td.totexplain('PAKNYGDPMKTPKN', vtype='last')    # the last period
td.totexplain('PAKNYGDPMKTPKN', vtype='sum')     # summed over the span
```

- `experiments` groups exogenous changes: name → list of variables. Without it,
  every changed exogenous variable is its own experiment (`mpak.exodif()` lists
  them).
- Each experiment is reset to baseline in turn and the model re-solved, so the
  bars are the contribution of each group of shocks. They need not add up exactly
  to the total in a non-linear model.
- `use='growth'` attributes growth rates instead of levels. `td.res['level']` and
  `td.res['growth']` hold the numbers.

## One equation: which inputs moved it (`dekomp`)

```python
d = mpak.dekomp('PAKNECONPRVTKN', 2025, 2027, lprint=False)
d.att_pct      # contribution of each right-hand-side term, % of the change
d.att_level    # in levels
mpak['PAKNECONPRVTKN'].dekomp()          # print it
mpak.dekomp_plot('PAKNECONPRVTKN')       # chart
```

Rows are the equation's input variables with their lag (`-1` = last period's
value). It explains one equation, not the chain behind it; follow the largest
contributor with another `dekomp`, or draw the chain with
`mpak.PAKNECONPRVTKN.tracepre(up=2)`.

## Reading attribution

- Start with `totdif` to name the shocks that matter, then `dekomp` on the key
  equations to show the channel.
- A large contribution from the variable's own lag is persistence: the effect of
  earlier periods carrying on.
- Contributions of fixed variables (`_D = 1`) are not attributed through their
  equation – the variable is exogenous while fixed.

## Deeper reference

`references/decomposition.md`: `time_att=True`, `get_att_pct` / `get_att_level`,
`dekomp_plot_per`, the `explain_*` displays of `totdif`, what is in `.res`,
`exodif`, combining `tracepre` with attribution, the interactive widgets, and
pitfalls.
