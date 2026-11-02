---
name: mf-solvers
description: >
  This skill should be used when choosing or tuning how a ModelFlow model is solved:
  "which solver", "solver=", "sim", "sim_ng", "newton", "newton_fbmin_ng",
  "newtonstack", "forward-looking", "leads", "Fair-Taylor", "alfa", "damping",
  "max_iterations", "relconv", "absconv", "nonlin", "jacobian=", "ljit", "speed up
  the solve", "not converged", or "the solve is slow".
metadata:
  version: "0.1.0"
---

# Choosing and tuning the solver

Solve options are passed in the call: `res = mmodel(df, 2020, 2030, solver='sim_ng',
alfa=0.7)`. Options **stick**: the next call reuses them until changed or
`reset_options=True`. A loaded `.pcim` may carry saved options
(`mmodel.oldkwargs`).

## Default choice

Without `solver=` the model picks by its shape:

| Model | Default | ng equivalent |
| --- | --- | --- |
| recursive (`istopo`) | `xgenr` | `xgenr_ng` |
| simultaneous, normalized | `sim` (Gauss-Seidel) | `sim_ng` |
| implicit / hybrid (`___RES`) | `newton_un_normalized` / `newton_ng` | `newton_ng` |
| with leads | `newtonstack` | `newtonstack_ng` |

`model(..., ng=True)` or `mmodel.ng = True` makes the ng solvers the default.
A model with fixed-period references (`X(2002)`) always uses ng solvers.

## Which solver when

| Solver | Use when |
| --- | --- |
| `sim_ng` | normalized simultaneous model that converges by Gauss-Seidel; the safe default |
| `newton_fbmin_ng` | normalized or hybrid model where Gauss-Seidel is slow or oscillates; Newton on the feedback set only. Usually the fastest per-period solver |
| `newton_ng` | Newton on the whole model per period; implicit models |
| `newtonstack_ng` | forward-looking models (leads): all periods solved together |
| `newtonstack_fbmin_ng` | large forward-looking models; stacked Newton on the feedback set |
| `res` / `res_ng` | evaluate each equation once (checking, not solving) |

Leads in a per-period solver are read as given within the period; Fair-Taylor
iteration (`fairopt={'fair_max_iterations': 10}`) repeats the sweep over the span.

## Tuning

Common to all solvers:

| Option | Default | Effect |
| --- | --- | --- |
| `max_iterations` | 200 (sim), 50 (fbmin outer), 20 (Newton) | iteration limit per period |
| `relconv` | 1e-7 | relative-change convergence criterion |
| `absconv` | 0.01 | variables smaller than this are not tested |
| `conv` | `'*'` | which variables are tested (pattern) |
| `ljit` | False | compile with numba: slow first solve, faster after; worth it for long spans or many scenarios |
| `silent` | 1 | 0 prints progress |
| `stats` | False | timing and iteration counts |
| `keep_residual` | False | equation residuals at convergence in `mmodel.ng_residual` |

Gauss-Seidel (`sim`, `sim_ng`):

| Option | Default | Effect |
| --- | --- | --- |
| `alfa` | 1.0 | damping of `<DAMP>` equations: `(1-alfa)*old + alfa*new`; 0.5–0.8 stops oscillation |
| `first_test` | 5 | iterations before testing convergence |
| `init` | False | start each period from the previous period's values |

Newton (`newton_ng`, `newton_fbmin_ng`, stacked):

| Option | Default | Effect |
| --- | --- | --- |
| `jacobian` | `'fd'` (fbmin), `'stack'` (stacked fbmin) | `'fd'` finite-difference reduced Jacobian; `'direct'` symbolic on the feedback equations; `'gauss'` no Jacobian, damped fixed point – the fallback for large or ill-conditioned feedback sets; converges only at the Gauss-Seidel rate, so raise `max_iterations` |
| `nonlin` | off; fbmin: size of feedback set | `N`: refresh the Jacobian every N iterations; `-N`: also before every period. Lower for strongly non-linear models |
| `newton_reset` | False | rebuild the Jacobian now (after changing the model or data a lot) |
| `newtonalfa`, `newtonnodamp` | 1.0, 0 | damp the Newton step by `newtonalfa` while iteration ≤ `newtonnodamp` |
| `newton_absconv` | 0.001 | absolute tolerance on `___RES` residuals |
| `forcenum` | False | numerical instead of symbolic derivatives |

## A tuning sequence

1. Solve a short span with `silent=0, stats=True`.
2. Not converged and oscillating → `alfa=0.7` (Gauss-Seidel) or
   `solver='newton_fbmin_ng'`.
3. Slow → `newton_fbmin_ng`, then `ljit=True` for repeated runs.
4. Newton diverges → `newtonalfa=0.5, newtonnodamp=5`, lower `nonlin`, or
   `jacobian='gauss'`.
5. Compare the solutions of two solvers on the scenario before trusting a switch;
   they agree to about `relconv`.

For what to look at when nothing converges, see `mf-structure`.
