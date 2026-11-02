---
name: mfdev-regress
description: >
  This skill should be used to check a ModelFlow solver or code-generation change
  against a reference solver: "/mfdev-regress", "regression test", "is it
  bit-identical", "compare sim_ng and my new solver", "check against PAK", "did my
  change alter the results", or after editing modelsolver_ng.py or the generated
  solver code.
argument-hint: "<solver> [reference] [--ljit] [--models pak frbus small] [--extra file.pcim]"
metadata:
  version: "0.1.0"
---

# Solver regression check

Compare a solver with a reference on the test models with
`scripts/regress.py`, bundled with this skill.

## Run it

Run from the `modelflow/` source folder, in a fresh Python process (a stale
`modelclass` from another location must not be imported):

```
cd <repo>/modelflow
python "<skill base directory>/scripts/regress.py" --solver <solver> --ref <reference>
```

`<skill base directory>` is the folder this SKILL.md was loaded from (shown when the
skill loads). Use the absolute path.

Arguments:

- `--solver` – the solver under test, by its `__call__` name (`sim_ng`,
  `newton_fbmin_ng`, a new `<name>_ng`).
- `--ref` – reference solver, default `sim_ng`. Use the solver the change derives
  from (a refactor of `sim_ng` is compared with `sim_ng`; a new `sim_hoist_ng` with
  `sim_ng`).
- `--models` – any of `pak` (MFMod Pakistan, carbon-tax scenario 2020–2100),
  `frbus` (FRB/US MCE, federal-funds shock; needs a solver that handles leads),
  `small` (three small models incl. a `DAMP` equation). Default `pak small`.
- `--extra` – more `.pcim` files, solved on their saved frame (the World Bank
  country models listed in `modeltest/ng_dispatch_test.py` are good candidates when
  present).
- `--ljit` – compile with numba (in memory, `stringjit=True`); compares with
  tolerance.
- `--tolerance`, `--rtol`, `--atol` – tolerance compare without jit (defaults
  1e-5 / 1e-6, as in `ng_dispatch_test.py`).
- `--opt key=value ...` – extra solve options, e.g. `jacobian=fd`.

The exit status is 1 if any model differs or fails.

## What to expect

- A refactor or an equivalent code-generation change (same float operations in the
  same order): **bit-identical** without jit. Anything else is a bug until explained.
- The same change with `--ljit`: close within tolerance, not necessarily identical
  (`fastmath=True`).
- A different algorithm (e.g. `newton_fbmin_ng` vs `sim_ng`): converges to a
  different point inside the convergence tolerance. Use `--tolerance` with `--rtol`
  near the solver's `relconv`; a bit-identical check will report `DIFFERS`.

## Reporting

Report the table as printed: per model the result, the reference and test times
(cold, codegen included), the largest relative and absolute difference, the number
of values outside, and where the largest difference is. For a `DIFFERS` on an
expected-identical change, find the first period and variable that differ and show
the generated lines for that equation from both solvers (`m.make_los_text`).

Timings here include code generation. For speed, time warm runs separately; the
fuller benchmark is `modeltest/speedtest.py`.
