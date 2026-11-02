---
name: mf-reports
description: >
  This skill should be used when making tables, charts or reports from ModelFlow
  results to share: "make a table", "report", "mpak.table", "mpak.plot", "PDF
  report", "LaTeX", "HTML table", "headline table", "scenario table", "growth
  table", "save a report", "dashboard", or "present the results".
metadata:
  version: "0.1.0"
---

# Tables, charts and reports

`mpak.table(...)` and `mpak.plot(...)` build report objects that display
themselves in a notebook and can be combined, saved with the model, and exported.

## Tables

```python
t = mpak.table('#Headline', datatype='growth', title='Headline, growth', smpl=(2025, 2030))
t                                   # display in the notebook
print(t.df_str)                     # as text
```

- `pat`: variables or a group (`'#Headline'`, `'PAKNY* PAKNE*'`).
- `datatype`:

| Datatype | Shows |
| --- | --- |
| `growth`, `level`, `gdppct`, `qoq_ar` | last solution |
| `difgrowth`, `diflevel`, `difgdppct`, `difqoq_ar` | last minus baseline |
| `difpctlevel` | last in percent of baseline |
| `basegrowth`, `baselevel`, `basegdppct`, `baseqoq_ar` | baseline |

- `smpl=(start, end)` the periods; `dec=2` decimals; `mul=1.0` scaling;
  `custom_description={'VAR': 'Label'}` row labels; `transpose=True`.
- Across kept scenarios: `scenarios='Baseline|Carbon tax 30'` – one block per
  scenario (`scenario_layout='suffix'` puts the scenario in each row label).

## Charts

```python
p = mpak.plot('PAKNYGDPMKTPKN PAKNECONPRVTKN', datatype='difpctlevel', smpl=(2025, 2050),
              title='Impact, % of baseline')
```

Same `pat`, `datatype`, `smpl` and `scenarios` as tables; `by_var=False` draws
one chart with a line per variable.

## Combining and exporting

```python
report = mpak.text('## Carbon tax\nA tax of 30 from 2025.') + t + p
report                       # displays in order
report.pdf(pdfopen=True)     # needs LaTeX with xelatex on PATH (not on Colab)
t.latex                      # LaTeX source of a table
t.out_html                   # HTML of a table
```

`+` puts parts after each other. `t.pdf()` exports a single part.

## Saving reports with the model

```python
mpak.add_report(t)                       # stored under the table's name in mpak.reports
mpak.modeldump('pak_with_reports.pcim')
mpak.get_report('A_small_table')         # rebuilt on the current solutions
```

Give tables a name with `name='headline_growth'` to store several.

## Interactive

- `mpak.keep_viz('#Headline')` – browse kept scenarios.
- `mpak.modeldash('PAKNYGDPMKTPKN')` – a Dash app with the dependency graph and
  attribution around a variable (needs `dash_interactive_graphviz`).

For the numbers behind a table, see `mf-results`.

`../mf-scenarios/references/usage.md` (section 5) has the composition rules:
`|` joins tables with tables or plots with plots, `+` builds a report, transposed
tables only go in reports, `{cty_name}` placeholders, `set_options`.
