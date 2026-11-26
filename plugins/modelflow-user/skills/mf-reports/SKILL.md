---
name: mf-reports
description: >
  This skill should be used when making tables, charts or reports from ModelFlow
  results to share: "make a table", "report", "mpak.table", "mpak.plot", "PDF
  report", "LaTeX", "HTML table", "headline table", "scenario table", "growth
  table", "save a report", "add_report", "get_report", "set_scenarios",
  "reportdump", "reportload", ".rsim file", "use the report on another model",
  "dashboard", or "present the results".
metadata:
  version: "0.2.0"
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
report.pdf()                 # needs LaTeX with xelatex on PATH (not on Colab)
report.pdf(pdfopen=True)     # also opens the pdf in the pdf viewer
t.latex                      # LaTeX source of a table
t.out_html                   # HTML of a table
```

`+` puts parts after each other. `t.pdf()` exports a single part.
`with mpak.set_smpl(2025, 2050):` around the calls sets the periods of every
part made inside it.

From 2.97 `pdf()` shows the pdf inside Jupyter Notebook 7 too, and when xelatex
reports LaTeX errors but still writes the pdf, the pdf is shown and the first
errors from the log are printed. `{key}` in `mpak.text(...)` is replaced from
`mpak.substitution` in the pdf as in the html.

## Storing and reusing reports

A report is stored as a definition (variables, datatypes, titles, periods),
not as numbers, so it can be made again on other scenarios or on another
model with the same variable names.

```python
report = (mpak.text('Carbon tax') + t + p).set_name('carbon_tax')
mpak.add_report(report)                  # stored in mpak.reports under its name
mpak.modeldump('pak_with_reports.pcim', keep=True)   # saved with the model (and the kept scenarios)

mpak.get_report('carbon_tax')            # made again on the current basedf and lastdf
mpak.get_report('carbon_tax').set_scenarios('Baseline|Carbon tax 30|Carbon tax 60')
```

- `set_scenarios` selects kept scenarios as `scenarios=` does: exact names
  separated by `|`, the first one is the reference for impacts, so put the
  baseline first.
- `get_report` needs a `basedf` and a `lastdf`, also when `set_scenarios`
  follows. Load the model with `modelload(..., run=True)` (or set
  `mpak.basedf` / `mpak.lastdf` from `mpak.keep_solutions`) before it.
- `mpak.add_report(t)` also stores a single table or chart; give it a name
  with `name='headline_growth'` or `.set_name(...)` to store several.

### Report definitions in a file of their own

From 2.98:

```python
mpak.reportdump('pak_reports')           # all stored reports -> pak_reports.rsim
mpak.reportdump('pak_reports', 'carbon_tax')   # only some (list, or names separated by blanks)
mpak.reportdump('one', report)           # a report object, without storing it in the model

mother.reportload('pak_reports')         # into another model; returns the names loaded
mother.get_report('carbon_tax')
```

| Option | Effect |
| --- | --- |
| `reportload(file, names)` | load only the named reports |
| `reportload(file, replace=True)` (default) | all reports in the file; a report with the same name is replaced, the model's others are kept |
| `reportload(file, replace=False)` | a report the model already has is kept |
| `reportload(file, replace='all')` | the model gets exactly the reports in the file |
| `modeldump(file, reports=False)` | save the model without the report definitions |

The `.rsim` suffix is added when the name has none; the content is json (a dict
of report name and definition), so another suffix such as `.json` works too.
Before these functions, the same file was written with
`json.dump(mpak.reports, f)` and read with `mpak.reports |= json.load(f)`.

## Interactive

- `mpak.keep_viz('#Headline')` – browse kept scenarios.
- `mpak.modeldash('PAKNYGDPMKTPKN')` – a Dash app with the dependency graph and
  attribution around a variable (needs `dash_interactive_graphviz`).

For the numbers behind a table, see `mf-results`.

`../mf-scenarios/references/usage.md` (section 5) has the composition rules:
`|` joins tables with tables or plots with plots, `+` builds a report, transposed
tables only go in reports, `{cty_name}` placeholders, `set_options`.
