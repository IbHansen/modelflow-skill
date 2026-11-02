---
name: mf-troubleshoot-run
description: >
  This skill should be used when a ModelFlow scenario run goes wrong from the
  user's side: "not converged", "the model does not solve", "NaN in the results",
  "Houston, we have a problem", "the result did not change", "the scenario has no
  effect", "results look strange", "error when I run the model", or "the numbers
  differ from last time".
metadata:
  version: "0.1.0"
---

# When a scenario run goes wrong

Work through the checks in order; most problems are in the scenario, not the
model.

## The scenario has no effect

- The shock is outside the solved periods: `upd('<2025 2050> ...')` but solved
  `mpak(scen, 2020, 2024)`.
- The variable name is wrong: `upd` creates a new column for an unknown name
  without complaint. Check `'PAKGGEXPCAPTCN' in mpak.exogene`.
- The variable is endogenous: changing it in the input only changes the starting
  value. Fix it (`mpak.fix`) or shift its add factor (`..._A`) instead
  (`mf-scenarios`).
- The variable is fixed (`_D = 1` in the data): it stays at `_X`.
- Compare with `mpak.exodif()` – it lists the exogenous variables that differ
  between `basedf` and `lastdf`.

## "not converged"

- `<period> not converged in N iterations`: try a smaller shock first; if that
  converges, the shock moves the model far from the baseline. Then
  `mpak(scen, 2025, 2050, alfa=0.5)` or `max_iterations=500`, or
  `solver='newton_fbmin_ng'`.
- Saved options carry over between calls: `reset_options=True` gives a clean
  run.
- Persistent non-convergence in a published model: hand it to the model's
  developer with the scenario (the `modelflow-modeller` plugin covers solver
  tuning).

## NaN or inf, or "Houston, we have a problem"

- The message names the equation and period and prints the inputs. A 0 or a
  negative value under `LOG` means a variable went negative or is missing.
- Shocks in levels that push a variable below zero (a tax larger than the base, a
  negative price) cause this. Shock in percent (`%`) or with smaller values.
- `mpak.errdump` holds the data at the failure.

## Results differ from an earlier run

- Another baseline: `basedf` is set by the first solve after loading; a second
  `modelload` or `setbase=True` changes it.
- Options left from an earlier call (`mpak.oldkwargs`).
- Another ModelFlow version: `import modelclass; modelclass.__file__` shows which
  installation is used.

## Before asking for help

Collect: the ModelFlow version or file location, the model file, the `upd`
text, the solve call, and the full message. `/mf-explain-error` in the
`modelflow-modeller` plugin explains most messages.
