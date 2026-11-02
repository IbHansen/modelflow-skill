---
name: mf-results
description: >
  This skill should be used when looking at or comparing ModelFlow results:
  "compare scenarios", "difference from baseline", "percent difference", "plot the
  results", "keep_plot", "keep_solutions", "growth rates", "show a table", ".dif",
  ".difpct", "export to Excel", "get the numbers", or "how much did GDP change".
metadata:
  version: "0.1.0"
---

# Looking at results

## The last solve against the baseline

`mpak[pattern]` selects variables (patterns in `mf-load-model`) from
`mpak.lastdf`; the attributes transform them. `.df` gives the DataFrame, and in a
notebook the object displays itself.

```python
v = mpak['PAKNYGDPMKTPKN PAKNECONPRVTKN']
v.df            # levels, last solution
v.base.df       # levels, baseline (basedf)
v.dif.df          # last - baseline
v.difpctlevel.df  # (last / baseline - 1) * 100: percent of baseline
v.pct.df          # growth rate, %
v.difgrowth.df    # growth-rate difference, percentage points
v.plot()          # chart
v.rtable()        # formatted table
```

`.difpct` is **not** the percent difference of levels: it is the growth-rate
difference, the same as `.difgrowth`. Use `.difpctlevel` for "percent of
baseline".

Use a period slice on the frame: `v.difpct.df.loc[2025:2030]`.

## Comparing kept scenarios

```python
mpak.keep_plot('PAKNYGDPMKTPKN', 2025, 2050, diffpct=True, legend=True)
mpak.keep_plot('#Headline', 2025, 2050, showtype='growth')
```

- One chart per variable, one line per kept scenario. `diff=True` / `diffpct=True`
  show the difference from the **first** kept scenario (normally `Baseline`).
- `showtype`: `'level'`, `'growth'`, `'change'`.
- Others: `title`, `legend`, `mul`, `kind='bar'`, `samefig=True, ncol=2`,
  `vline=[(2025, 'Shock')]`, `dataonly=True` (returns the data instead of
  plotting).
- It returns a dict of matplotlib figures by variable. Save them with
  `fig.savefig(...)` or `model.savefigs(figs, location='./graph',
  experimentname='carbon', extensions=['png'])`. The `savefig=` argument of
  `keep_plot` is not used.
- `mpak.keep_viz('#Headline')` is an interactive widget for browsing scenarios.

## Getting the numbers out

```python
wide = mpak.keep_get_df('PAKNYGDPMKTPKN PAKNECONPRVTKN')   # columns: variable x scenario
wide.loc[2025:2030]
wide.to_excel('results.xlsx')

for name, df in mpak.keep_solutions.items():              # every kept solution
    df.loc[2025:2050, ['PAKNYGDPMKTPKN']].to_csv(f'{name}.csv')
```

`mpak.keep_print('PAKNYGDPMKTPKN', 2025, 2030)` prints the kept values
(differences by default).

## Reading the numbers

- Real variables (`...KN`) in local currency at constant prices; nominal (`...CN`)
  at current prices. Compare scenarios in percent of baseline for real
  variables, and in percentage points for rates and ratios (`.dif`).
- A large difference in the first period that fades is a temporary shock; one
  that grows points to a permanent change or an unstable path.

For tables and charts to hand over, see `mf-reports`.

`../mf-scenarios/references/usage.md` (sections 4–5) has the full `plot`
options and the `[]` selector transformations.
