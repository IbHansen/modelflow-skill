---
name: mfdev-ode
description: >
  This skill should be used when changing or debugging ModelFlow's ODE preprocessor,
  modelode.py: "ode_transform", "exclusion_lists", "ode_makemodel", "BUTCHER",
  "add an integrator", "leapfrog", "symplectic", "adaptive step", "stage_map",
  "__S1 / __K1 names", "NO{list} expansion", "_classify", "Euler-form detection",
  "nbody_template", "report table", or when an ODE model generates wrong equations.
metadata:
  version: "0.1.0"
---

# The ODE preprocessor (`modelode.py`)

`modelode.py` (repo root, in `pyproject.toml` py-modules under *onboard*) turns
differential equations into ordinary FRML text: the equations of one explicit
Runge–Kutta step per row. It is an **overlay**: no core module imports it and the
core has no ODE hooks. Keep it that way – the earlier version with hooks in
`modelclass` / `modelconstruct_estimation` was reverted on purpose ("the core is
getting very complicated"). Everything ODE-specific goes in `modelode.py`.

Tests are in `modelflow/modeltest/odetest/`; design notes and example notebooks in
`modelflow/experiments/projecttile/` (`nbody_rk4_design.md`, `ode_transform_design.md`).

## Layout

| Part | What |
| --- | --- |
| `BUTCHER` | explicit tableaux `a`, `b`, `c` (euler, heun, midpoint, ralston, rk4); `Fraction` where exact |
| `_Eq` | one parsed equation: `lhs`, `rhs`, tokens (`modelpattern.udtryk_parse`), `kind`, `f_tokens` |
| `_classify` | `<ODE>` → state; DT absent → aux; DT present → must be `S = S(-1) + DT*f`, `f` from sympy |
| `_check_lags` | only `X` and `X(-1)` in states and needed auxiliaries |
| `exclusion_lists(text, display=False)` | `NO{list}` → sublist `NO` + lists `NOA` …; `display=True` is the readable version for `mm.render` |
| `ode_transform(text, method, dt, funks, report)` | the transformation, returns FRML text |
| `_show_report` | `report=True`: HTML table with borders (notebook) / markdown / text |
| `ode_makemodel(text, ...)` | `exclusion_lists` → `Makemodel` → `ode_transform` → `model`; returns `(model, mm)` |
| N-body section | `nbody_template`, `nbody_makemodel`, `nbody_model`, `make_df`, `zero_momentum`, `energy`, `orbital_period`, `pos`/`vel`/`mass`, constants |

## `ode_transform`, step by step

1. `mp.explode(exclusion_lists(text))` – LIST/DO/sum expansion, with `NO{list}` made
   expandable first.
2. Parse every FRML into `_Eq`; collect duplicate left-hand sides as errors.
3. `_classify`: states and auxiliaries. Euler form: sympy on the tokens with lags
   collapsed, `g = cancel(expand((expr - S)/DT))` must be free of `DT`; `f` is
   re-tokenised from `sstr(g)`.
4. Auxiliary graph (networkx): an aux is **needed** if it is an ancestor of a
   variable in some derivative. Needed auxes must be acyclic. Not needed → `report`
   (written once at the end, lags and FRML name kept).
5. All checks append to `errors`; at the end they are printed together and
   `OdeTransformError` is raised. Keep that: users fix all problems in one go.
6. Emit, per stage `i`: `S__S{i} = S(-1) + DT*(Σ a_ij S__K{j})`, the needed auxes as
   `A__S{i}` (topological order), `S__K{i} = f` with `stage_map(i)`; then the
   updates `S = S(-1) + DT*(Σ b_i S__K{i})`; then the auxes at the end of the step and
   the report equations.

`stage_map(i)` maps each variable in `f` / an aux: states and needed auxes → their
`__S{i}` name; anything else (exogenous) by the stage time `c_i`: `0` → `E(-1)`,
`1` → `E`, else `((1-c)*E(-1)+c*E)`.

Equation count: `stages × (2 × states + needed aux) + states + needed aux + report`.

## `exclusion_lists`

Text-level rewrite, before Makemodel/`mp.explode`, because `format_map` cannot take
nested braces and `!=` in DO/sum conditions acts as `==`:

- `LIST L = L : A B C` gets `/ NO : NOA NOB NOC`, plus `LIST NOA = NOA : B C`, ...
- `{NO{L}}` → `{{{NO}}}` (element), bare `NO{L}` → `{NO}` (list name).
- A `DOABLE` with `{NO{L}}` on the left (pair equations) becomes an explicit nested
  `DO L / DO NO{L}` block.
- The `$` style is judged on model lines only (`>` lines in markdown), since LaTeX
  prose is full of `$`.
- `display=True` replaces only the list line by the aligned list + sublist + `NO…`
  lists and, in markdown, a one-line note; equations stay as written.

## Rules for changes

- **Overlay only.** Do not add ODE options to `modelclass`, `Makemodel`, or the
  solvers. If Makemodel needs a hook, prefer pre/post-processing text here.
- **Import order:** `import modelmanipulation as mp` before `import modelpattern as pt`
  (they import each other; only this order works cold). `modelclass` and
  `modelconstruct_estimation` are imported inside `ode_makemodel`.
- **Explicit methods only.** Every generated equation must be recursive within the
  period, so the ordinary sweep solves a step. An implicit method would make the
  stage equations simultaneous – a different design.
- **No delays.** Lags ≥ 2 would need the stage history of earlier rows.
- `report` output: HTML with inline cell borders (JupyterLab's stylesheet draws
  markdown tables without lines), markdown for latex/pdf exports, text outside a
  notebook.
- Documentation and LaTeX: time derivatives as `\frac{dx}{dt}`, not `\dot x`.
  `nbody_template` is an f-string: double the braces.

## Adding an integrator

- A new explicit RK method: add a tableau to `BUTCHER` (`a` strictly lower
  triangular, `len(a) == len(b) == len(c)`), check the order on the convergence test.
- A method that is not one-step RK (leapfrog / velocity Verlet, symplectic) needs
  its own emitter: it must know which states are positions and which velocities.
  Plan it with a design note (`mfdev-design-notes`) – it is on the open list.
- Adaptive steps do not fit one row per step with a fixed sweep; the current
  answer is a per-row `DT` column.

## Tests

In `modelflow/modeltest/odetest/` (scripts, no pytest; each puts the modelflow folder on
`sys.path`, so they run from any directory: `python modeltest/odetest/nbody_test.py`):

| Script | Checks |
| --- | --- |
| `ode_transform_test.py` | projectile: Euler-form vs `<ODE>` input, all methods' convergence order (1, 2, 2, 2, 3.95) against `solve_ivp`, the error messages |
| `nbody_test.py` | template vs the hand-written reference `nbody_rk4_probe.py`: **bit-identical** (max diff 0.0), 117 equations for 3 bodies in 2-D, figure-8 error 7e-9, 4 bodies 3-D = 225 equations |
| `ode_makemodel_test.py` | markdown, plain string and DO/ENDDO versions give identical results; lag errors through Makemodel |
| `nbody_rk4_probe.py` | the reference: RK4 N-body equations written out by hand (imported by `nbody_test.py`); run alone it times 3- and 10-body solves |

After any change: all three must pass with unchanged numbers. The notebooks
(`projectile_`, `nbody_`, `webb_l2_modelflow.ipynb`, in `experiments/projecttile/`) are built by `build_*.py`
and executed with nbconvert (~10 min for the N-body one); rebuilding overwrites
outputs and any cells added by hand – merge instead of rebuilding when the notebook
has been edited.

## Related

`mf-ode` (modelflow-modeller) is the modeller's guide; `mf-ode-simulate` and
`mf-animate` (modelflow-user) cover running and animating. `mfdev-architecture` for
the rest of the repo.
