---
name: mf-check-model
description: >
  This skill should be used to get a structure and data report on a ModelFlow model:
  "/mf-check-model", "check my model", "is the model ok", "how big is the model",
  "what is in this pcim", "which variables are missing from the data", "does the
  model reproduce history", "the model does not converge", "where does the
  instability come from", "dump the iterations", "ldumpvar", "oscillates",
  "diverges", or before solving a newly built or imported model.
argument-hint: "<model.pcim | model.frm | model.md> [--data file.csv] [--start 2020 --end 2030] [--test] | convergence <model> [--upd ...] [--period P]"
metadata:
  version: "0.1.0"
---

# /mf-check-model

Two bundled scripts:

- `check_model.py` – structure and data report (below).
- `check_convergence.py` – when a solve does not converge or blows up: dumps
  every core variable's iterations in the failing period and ranks where the
  instability starts (see *Convergence*).

Run the one that fits the request, then explain the report.

## Run

```
python "<skill base directory>/scripts/check_model.py" <model> [options]
```

`<skill base directory>` is the folder this SKILL.md was loaded from. Use the
absolute path. ModelFlow must be importable: installed, or run from a `modelflow`
source folder, or pass `--modelflow <folder with modelclass.py>`.

| Argument | Meaning |
| --- | --- |
| `<model>` | `.pcim` (equations and data), FRML text (`.frm`, `.txt`), or a markdown model (`.md`, built with `Makemodel`) |
| `--data` | CSV or Excel with periods in the first column, for text and markdown models (overrides the data in a `.pcim`) |
| `--start`, `--end` | the span checked for NaN and used by `--test` |
| `--test` | also run `test_model`: each equation evaluated once on the data |

If the model only exists in the notebook, write its equations to a file first
(`open('m.frm','w').write(mmodel.equations)`) and the data to CSV.

## The report

- **Model** – equations, exogenous count, normalized / implicit / hybrid, max lag
  and lead, fixed-period references, simultaneous or recursive.
- **Structure** – prolog / core / epilog sizes, simultaneous blocks, feedback set.
- **Equation options** – counts of each FRML option, fixable variables, add
  factors, whether there is an add-factor model.
- **Possible problems** – FRML names containing `Z` (silently damped), extra LHS
  variables, exogenous variables missing from the data (solved as 0.0), missing
  `_A/_X/_D` companions (usually fine), NaN in exogenous or endogenous values in
  the span and the lag periods.
- **Solving** – data span, the default solver and saved solve options.
- **test_model** – equations whose value differs from the data.

## Explaining it

Lead with the problems, most serious first: missing real exogenous data and NaN
break the solve; `Z` damping changes results quietly. Then summarise the
structure in one or two lines (for example: "378 equations, 104 in one
simultaneous block, feedback set of 6 – a good fit for `newton_fbmin_ng`").
For `test_model` differences, separate identities (a definite error) from
behavioural equations (a residual, fixed by add factors – `mf-data`). Point to
`mf-structure`, `mf-solvers` or `mf-debug-model` for the next step.

## Convergence

```
python "<skill base directory>/scripts/check_convergence.py" <model> [options]
```

| Argument | Meaning |
| --- | --- |
| `<model>`, `--data` | as for `check_model.py` |
| `--upd "<2025 2050> X = 30; ..."` | the scenario that fails: `upd` lines applied to the data, separated by `;` |
| `--start`, `--end` | the span solved; default the span saved in the model |
| `--period` | analyse this period instead of searching for the first failure |
| `--solver` | `sim` (default) or `sim_ng`; both dump the whole core |
| `--opt key=value ...` | solve options, e.g. `alfa=0.5 max_iterations=100` |
| `--last`, `--top` | iterations looked at (10), variables shown (15) |
| `--plot file.png`, `--csv file.csv` | `show_iterations` of the top 6; the dump of the period |

What it does: solves the span and reads the solver's own messages (not
converged, NaN, or an exception such as LOG of a negative number); takes the
first failing period, solves the periods before it, then solves that period alone
with `ldumpvar=True, dumpvar='*'`. If the solve raised, the partial dump made by
ModelFlow's error handler is used (with `sim_ng` only in ModelFlow newer than
2.92). Iterations after values turn NaN are dropped.

The table, per variable: `rel_step` (largest step over the last iterations /
starting level), `flips` (sign changes of the steps), `trend` (last step / first
step in the window), `type` (slow, oscillating, growing, growing oscillation),
`onset` (diverging only: iteration from which the step stays above 0.1 % of the
level), `core_pos` (position in the solve order) and the variable's
current-period core inputs (`*` = also in the table).

Explaining it: name the type first (slow → more iterations or Newton;
oscillating → damping; growing → an equation or data problem). Then the origin
the script names – in a diverging solve the variable that took off first – with
its equation, and follow its starred inputs to describe the loop. Verified on
PAK: a slow carbon-tax solve points at the output gap → policy rate → interest
payments chain; an over-relaxed solve (`alfa=1.9`) diverges from the domestic
interest rate (`PAKINTRDXN`, onset 20) into private investment.
