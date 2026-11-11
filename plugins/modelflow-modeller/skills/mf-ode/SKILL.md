---
name: mf-ode
description: >
  This skill should be used when building a ModelFlow model from differential equations
  (continuous time): "ODE", "differential equation", "laws of motion", "Runge-Kutta",
  "RK4", "Heun", "Euler step", "<ODE>", "ode_transform", "ode_makemodel", "modelode",
  "Butcher tableau", "time step DT", "N-body", "planets", "orbit", "projectile",
  "nbody_template", "NO{list}", "all the other elements", "dS/dt", or turning physics,
  epidemiology (SIR) or growth equations written as derivatives into a ModelFlow model.
metadata:
  version: "0.1.0"
---

# ODE models: from laws of motion to Runge–Kutta equations

ModelFlow solves difference equations, one dataframe row per period. The module
`modelode` lets a modeller write the **continuous** model — the derivatives — and
generates the equations of a one-step Runge–Kutta method (Euler, Heun, midpoint,
Ralston, RK4). Each row becomes one time step. Every generated equation is
recursive within the period, so the ordinary sweep solves a step without
iteration or Newton. Nothing in the solver knows about ODEs.

Use it for physics (projectiles, planets, satellites), epidemics (SIR), chemical
kinetics, continuous-time growth models: any system dS/dt = f(S, exogenous).
Not for: delays (lags ≥ 2), leads, or equations that need iteration inside a step.

## Two ways to write a state

| Form | Text | Meaning |
| --- | --- | --- |
| derivative | `FRML <ODE> S = f $` | dS/dt = f |
| Euler step | `FRML <> S = S(-1) + DT*f $` | the step form; `f` is extracted with sympy |

Both give the same generated model. The `<ODE>` form is preferred: it states the
physics and leaves the time step to the integrator. An Euler-step equation may be
explicit or semi-implicit; its lag pattern is discarded.

Every other equation is an **auxiliary** (`FRML <> SPEED = SQRT(VX**2+VY**2) $`).

```python
from modelclass import model
from modelode import ode_transform

laws_of_motion = '''
FRML <ODE> DISTANCE    = VELOCITY_X                                  $
FRML <ODE> HEIGHT      = VELOCITY_Y                                  $
FRML <ODE> VELOCITY_X  = -DRAG_FACTOR * VELOCITY_X                   $
FRML <ODE> VELOCITY_Y  = -DRAG_FACTOR * VELOCITY_Y - GRAVITY         $
FRML <ODE> ELAPSED_TIME = 1                                          $
FRML <>    SPEED       = SQRT(VELOCITY_X**2 + VELOCITY_Y**2)         $
FRML <>    DRAG_FACTOR = AIR_DENSITY * SPEED / (2 * BALLISTIC_COEF)  $
'''
text = ode_transform(laws_of_motion, method='rk4', dt='TIME_STEP', report=True)
m = model(text, modelname='Projectile, RK4')
```

`ode_transform(frml_text, method='rk4', dt='DT', funks=[], report=False)` returns FRML
text. `report=True` shows how each equation was read (state / aux / report, and the
derivative) – a bordered table in a notebook, text elsewhere; `report='text'` or
`'markdown'` chooses.

## The rules

- **No time step and no lags inside a derivative.** In `f` and in the auxiliaries it
  needs, `X` and `X(-1)` both mean "X at the current stage". A lag of 2 or more, a
  lead or a fixed period (`X(2020)`) is an error.
- **`DT` is a column** (name set with `dt=`, default `'DT'`). It may change from row to
  row. It must not appear inside an `<ODE>` equation or an auxiliary.
- **Exogenous variables** (masses, `G`, gravity, drag constants) are read at each
  stage's own time: start of step → `E(-1)`, end → `E`, in between → interpolated.
  They may vary over the rows.
- **Auxiliaries that a derivative needs** are recomputed at every stage; they must not
  be simultaneous among themselves. An auxiliary no derivative needs (a reporting
  variable such as kinetic energy) is computed once at the end of the step, as written.
- **A self-referencing auxiliary** (`T = T(-1) + 1`) is an error: make it a state
  (`<ODE> T = 1`).
- Each variable is determined once.

## Methods

`method=` is `'euler'` (1st order), `'heun'`, `'midpoint'`, `'ralston'` (2nd),
`'rk4'` (4th, the default), or your own explicit Butcher tableau:

```python
from fractions import Fraction
kutta3 = dict(a=[[], [0.5], [-1, 2]], b=[Fraction(1, 6), Fraction(2, 3), Fraction(1, 6)], c=[0, 0.5, 1])
text = ode_transform(laws, method=kutta3)
```

`a` is strictly lower triangular (explicit methods only). The tables are in
`modelode.BUTCHER`.

## What is generated

For each state `S` and stage `i`: the stage value `S__S{i}`, the derivative
`S__K{i}`, and finally the update `S = S(-1) + DT*(b1*S__K1 + ...)`. Needed
auxiliaries get `A__S{i}`. The number of equations is

    stages × (2 × states + needed aux) + states + needed aux + reporting equations

e.g. RK4 with 13 states and no auxiliaries: 4 × 26 + 13 = 117. Names ending in
`__S1`, `__K1`, ... must not already exist in the model.

## Documented models: `ode_makemodel`

To write the model as a markdown document with lists and `doable` lines, use the
overlay on `Makemodel`:

```python
from modelode import ode_makemodel
m, mm = ode_makemodel(text, method='rk4')                        # markdown, '>' lines
m, mm = ode_makemodel(text, method='heun', type_input='modelflow')  # plain string
mm.render            # the documented model, with the generated lists shown
mm.expanded_frml     # the expanded <ODE> equations, before Runge-Kutta
```

It returns `(model, Makemodel)`. Other `Makemodel` arguments pass through.

### Loops over objects and coordinates

```
>list bodies = bodies : SUN EARTH MOON
>list dims   = dims : X Y Z
>list dd     = dd : X Y Z
>doable <ODE> pos__{bodies}__{dims} = v__{bodies}__{dims}
>doable <ODE> v__{bodies}__{dims} = G*sum(NO{bodies}, m__{NO{bodies}}*(pos__{NO{bodies}}__{dims} - pos__{bodies}__{dims})
>>   / (sum(dd, (pos__{NO{bodies}}__{dd} - pos__{bodies}__{dd})**2))**1.5)
><ODE> t = 1
```

- `doable` writes one equation per index combination on the left-hand side
  (`POS__EARTH__X`, `V__MOON__Z`, ...).
- **`NO{list}` means "all the other elements"**: inside a loop over `bodies`,
  `NO{bodies}` is the list of the other bodies and `{NO{bodies}}` runs over them.
  `exclusion_lists` generates `/ NO : NOSUN NOEARTH NOMOON` and `LIST NOSUN = NOSUN : EARTH MOON` etc.;
  `mm.render` shows them. The list must be written `LIST L = L : ...` (first sublist =
  list name).
- A second copy of a list (`dd`) is the summation index inside an equation that already
  loops over the first (`dims`).
- `NO{list}` works in `DO` loops and `sum(...)` of plain strings too.

The ready-made N-body template: `modelode.nbody_template(bodies, dims=2)` (the text),
`nbody_makemodel(bodies, dims, method)` → `(model, mm)`, `nbody_model(...)` → model.

## Traps

- `!=` in a `DO` condition or `sum` behaves like `==`. Use `NO{list}`.
- Nested braces `{NO{L}}` cannot go through `format_map`; `exclusion_lists` rewrites
  them. Do not write `{{{NO}}}` yourself.
- Makemodel's `$` is all-or-nothing: either every statement ends with `$` or none.
- In a markdown model a `$$ ... $$` block must close on its own line, or the `>` lines
  after it are dropped.
- Write time derivatives in the documentation as $\frac{dx}{dt}$.

## Choosing the step

- Halve `DT` and compare: the error should fall by 2^order (16 for RK4). Compare with
  `scipy.integrate.solve_ivp(method='DOP853', rtol=1e-12, atol=1e-12)` for a reference.
- For orbits watch the energy drift (`modelode.energy`).
- Close encounters need a smaller step only near the encounter: `DT` is a column, so
  give those rows a smaller step.
- An instantaneous event (a rocket burn, a vaccination campaign) is a jump in a state:
  solve up to the row, change the state in that row, solve on from the next row
  (`mf-ode-simulate` in modelflow-user).

## Errors (`OdeTransformError`)

All problems are listed before the exception:

| Message | Fix |
| --- | --- |
| `lag/lead X(-2) is not allowed` | only `X` and `X(-1)`; no delays |
| `DT inside an <ODE> equation` | write the derivative, not the step |
| `DT in an equation that is not a step` | `DT` only as `S = S(-1) + DT*f` |
| `auxiliary X refers to itself` | make it a state: `<ODE> X = ...` |
| `auxiliaries needed by a derivative are simultaneous` | solve the loop by hand or make one of them a state |
| `X is determined twice` | one equation per variable |
| `generated names already exist` | rename variables ending in `__S1`, `__K1`, ... |
| `no state equation found` | tag the derivatives `<ODE>` |

## Related

- Running, checking and animating ODE models: `mf-ode-simulate` and `mf-animate`
  (modelflow-user).
- Example notebooks: `modelflow/experiments/projecttile/` – projectile (Euler vs Heun),
  N-body (Sun–Earth–Moon, satellite transfer, figure-8), Webb at L2 (3-D).
