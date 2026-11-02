---
name: mf-scenarios
description: >
  This skill should be used when defining and running a scenario with a ModelFlow
  model: "scenario", "shock", "what if", "simulate", "upd", "change an exogenous
  variable", "carbon tax", "increase government spending", "fix a variable",
  "exogenize", "keep consumption unchanged", "add factor", "judgement", "solve
  the model", "keep the solution", "run several scenarios", "targeting",
  "invert", "hit a target path", "instruments", "set_smpl", or "mfcalc".
metadata:
  version: "0.1.0"
---

# Running scenarios

A scenario is the baseline data with some inputs changed, solved by the model,
and kept under a name so it can be compared.

```python
mpak, baseline = model.modelload('pak.pcim', run=1, keep='Baseline')

scen = baseline.upd('<2025 2050> PAKGGREVCO2CER PAKGGREVCO2GER PAKGGREVCO2OER = 30')
res = mpak(scen, 2025, 2050, keep='Carbon tax 30')
```

`mpak(df, start, end, keep=name)` solves and stores the result in
`mpak.keep_solutions[name]`; it also sets `mpak.lastdf`. The first solve sets
`mpak.basedf`, the reference for differences.

## Changing inputs with `upd`

One line per change: `<start end> VARIABLES operator values [--kg]`.

| Operator | Effect |
| --- | --- |
| `= 30` | set to 30 (several values, one per period: `= 1 2 3`) |
| `+ 5` | add 5 |
| `* 1.1` | multiply by 1.1 |
| `% 10` | increase by 10 % |
| `=growth 5` | set the growth rate to 5 % per period |
| `+growth 1` | add 1 percentage point to the growth rate |
| `=diff 3` | set the change from the previous period to 3 |
| `--kg` | keep the growth rate of the original after the period (with level changes) |

```python
scen = baseline.upd('''
<2025 2050> PAKGGREVCO2CER PAKGGREVCO2GER PAKGGREVCO2OER = 30   # carbon tax
<2025 2030> PAKGGREVGNFSXN + 1                                  # goods and services tax rate +1
''')
```

`<2025>` is one period; without `<...>` the whole frame is changed. `#` starts a
comment. Several variables on one line get the same change.

**Only exogenous variables are shocked this way.** Changing an endogenous
variable in the input only changes its starting value; the model recomputes it.
Check with `'PAKGGEXPCAPTCN' in mpak.exogene`. In MFMod models many policy
instruments (government spending, the policy rate) are endogenous – shock them
by fixing (below).

## Holding an endogenous variable fixed

Behavioural equations can be exogenized: the variable follows its `_X` value
while `_D = 1`.

```python
fixed = mpak.fix(scen, 'PAKNECONPRVTKN', 2025, 2030)   # hold consumption at its current values
res = mpak(fixed, 2025, 2050, keep='Carbon tax, consumption fixed')
again = mpak.unfix(res, 'PAKNECONPRVTKN', 2025, 2030)
```

`mpak.fix_endo` lists the variables that can be fixed. After a solve with fixed
variables, ModelFlow computes their add factors, so unfixing continues from the
same path.

To shock an endogenous instrument, fix it and change its `_X` value:

```python
fixed = mpak.fix(baseline, 'PAKGGEXPCAPTCN', 2025, 2030)        # public investment
scen = fixed.upd('<2025 2030> PAKGGEXPCAPTCN_X % 10')           # 10 % above baseline
res = mpak(scen, 2025, 2030, keep='Public investment +10%')
```

## Judgement through add factors

`X_A` shifts a behavioural equation without fixing it:
`scen = baseline.upd('<2025 2027> PAKNECONPRVTKN_A + 0.01')`. Its unit follows
the equation: look at `mpak['PAKNECONPRVTKN'].frml`. Inside `EXP(...)` (log
form) 0.01 is about 1 %; added to a level (`... + X_A`) it is in the variable's
own units, so it must be of that size to matter.

## Good practice

- Solve options stick between calls; pass `reset_options=True` to start clean.
- Name every kept scenario; `mpak.keep_solutions` is a dict, delete with
  `del mpak.keep_solutions['name']`.
- Keep only some variables to save memory: `keep_variables='PAKNY* PAKNE*'`.
- Check what changed: `mpak.exodif()` shows exogenous differences between
  `basedf` and `lastdf`.

For comparing and plotting kept scenarios see `mf-results`; for what explains a
difference, `mf-attribution`.

## Deeper reference

- `references/usage.md`: `upd` gotchas (spaces around operators, time scope
  carried between lines, `create=False`, `lprint`, `scale`), `mfcalc` for
  shocks that depend on other variables, `plot`/`table` objects and how they
  combine.
- `references/simulation-methods.md`: the solve call and persistent options,
  `smpl`/`set_smpl`, `keep_solutions` and `scenarios=`, the `_D`/`_X`/`_A`
  mechanics, and **targeting with `mpak.invert`** (instruments, targets,
  convergence tuning).
