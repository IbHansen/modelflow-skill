---
name: mf-ode-simulate
description: >
  This skill should be used when running or checking a ModelFlow model built from
  differential equations (an ODE model made with modelode): "simulate the orbit",
  "run the N-body model", "projectile", "planets", "satellite", "make_df", "initial
  state", "time step", "DT", "one row per step", "rocket burn", "event during the
  simulation", "energy drift", "is the time step small enough", "compare with
  solve_ivp", "orbital period", "plot the trajectory", or "rotating frame".
metadata:
  version: "0.1.0"
---

# Running an ODE model

An ODE model (built with `modelode`, see `mf-ode` in modelflow-modeller) is an
ordinary ModelFlow model in which **each row is one time step** of a Runge–Kutta
method. Running it is filling a dataframe with the starting state and the inputs,
and solving from row 1.

## The dataframe

| Column | Rows | Content |
| --- | --- | --- |
| the step, `DT` (or the name given with `dt=`) | every row | the time step; may differ by row |
| exogenous inputs (`G`, masses, gravity, drag constants ...) | every row | constants or paths; read inside each step |
| the states (positions, velocities, `T` ...) | row 0 | the starting state |
| everything else (`…__S1`, `…__K1`, auxiliaries) | – | 0; the model computes them |

- The index counts steps `0 … N`; row 0 is the starting state and is not solved.
- Rows 1 … N of the states can hold anything: each step is one ordered sweep, no
  iteration, no starting guesses.
- Inputs must be in row 0 too: a step reads them at the start and the end.
- Units are whatever the numbers are in, as long as they are consistent.
- A clock state `<ODE> T = 1` gives the time of each row in `T`.

```python
import pandas as pd
n = int(round(t_max / dt))
df = pd.DataFrame(0.0, index=range(n + 1), columns=sorted(m.allvar))
df['DT'], df['GRAVITY'] = dt, 9.81                  # inputs, every row
df.loc[0, ['VELOCITY_X', 'VELOCITY_Y']] = 212.1, 212.1   # starting state, row 0
res = m(df, 1, df.index[-1], silent=1)
```

## N-body models

`modelode` has the helpers:

```python
from modelode import nbody_makemodel, make_df, zero_momentum, energy, orbital_period, pos, vel, G_AU_DAY
bodies = ['SUN', 'EARTH', 'MOON']
m, mm = nbody_makemodel(bodies, dims=2, method='rk4')
masses = {'SUN': 1.0, 'EARTH': 3.003e-6, 'MOON': 3.694e-8}          # solar masses
pos0 = {'SUN': (0, 0), 'EARTH': (1.0, 0), 'MOON': (1.00257, 0)}       # AU
vel0 = zero_momentum(bodies, masses, {'SUN': (0, 0), 'EARTH': (0, 0.0172), 'MOON': (0, 0.0178)}, 'SUN')
df = make_df(m, bodies, masses, pos0, vel0, G_AU_DAY, dt=0.25, t_max=730)   # AU, days
res = m(df, 1, df.index[-1], silent=1)
res[pos('EARTH', 'X')]                    # 'POS__EARTH__X'
```

- Names: `POS__<BODY>__<X|Y|Z>`, `V__<BODY>__<X|Y|Z>`, `M__<BODY>`, `G`, `DT`, `T`.
- Units: AU, days, solar masses with `G_AU_DAY`; or km, s with `G = 1` and the mass
  set to `MU_EARTH_KM` (GM of the Earth). A body with mass 0 feels gravity but does
  not pull (a spacecraft).
- `zero_momentum` gives one body the velocity that makes the total momentum zero, so
  the system does not drift.
- `energy(res, bodies, masses, g, dims)` is the total energy by row;
  `orbital_period(res, body, centre)` the mean period from the turning angle.

## Events: burns, switches, interventions

An instantaneous event is a jump in a state. Solve up to the row, change the state
in that row, solve on from the next row:

```python
sat = m(df, 1, n1, silent=1)                 # up to the burn
sat.loc[n1, [vel('SAT', 'X'), vel('SAT', 'Y')]] *= 1.3     # the burn
sat = m(sat, n1 + 1, n2, silent=1)           # on from the next row
```

A change in an input (thrust, a policy) is just its column changing over the rows.
To stop at an event (impact), solve the whole horizon, find the first row past the
event and interpolate between that row and the one before.

## Is the step small enough?

- **Halve `DT`** and compare: the change should shrink by 2^order (16 for RK4, 4 for
  Heun, 2 for Euler).
- **A reference**: `scipy.integrate.solve_ivp(rhs, ..., method='DOP853', rtol=1e-12,
  atol=1e-12, dense_output=True)` on the same equations, evaluated at `res['T']`.
- **Conserved quantities**: for orbits the energy drift `abs(e.iloc[-1]/e.iloc[0]-1)`
  should be tiny (1e-10 or less with RK4 and a sensible step).
- **Close encounters** blow the error up: use a smaller step, or a smaller `DT` only
  in the rows around the encounter.
- Some systems are unstable (L2 halo orbits, chaotic three-body): two runs drift apart
  however small the step. That is physics, not numerics: compare with a perturbed run.

## Plotting

```python
fig, ax = plt.subplots()
ax.plot(res[pos('EARTH', 'X')], res[pos('EARTH', 'Y')], label='Earth')
ax.set(aspect='equal')                                   # orbits need equal axes
rel = res[pos('MOON', 'X')] - res[pos('EARTH', 'X')]     # motion relative to another body
```

A frame turning with angular rate `n` (to see the Lagrange points or a halo orbit):
rotate positions by `-n*t`: `x' = cos(nt) x + sin(nt) y`, `y' = -sin(nt) x + cos(nt) y`.

Animations: `mf-animate`.

## Speed

Each row is one sweep: a 3-body RK4 model in 3-D does about 1 400 steps in 0.25 s.
Ten bodies (≈ 900 equations) at 10 000 steps take seconds. Parameter sweeps are loops
over `make_df` and `m(...)`; sliders with `ipywidgets.interact` work well.

## Examples

`modelflow/experiments/projecttile/`: `projectile_modelflow.ipynb` (drag, Euler vs
Heun, sliders), `nbody_modelflow.ipynb` (Sun–Earth–Moon, a Hohmann transfer with two
burns, the figure-8, close encounters), `webb_l2_modelflow.ipynb` (3-D, the Webb
telescope's halo orbit and why it needs station keeping).
