# Changing an existing model

Most work starts from a loaded model, not a new one. `equpdate` and `eqdelete`
return a **new** model and a dataframe; the original model is untouched.
Writing equations, options and normalization are in `mf-dsl`, `mf-frml-options`
and `mf-normalize`; this file covers the modification calls and user functions.

## Replace or add equations: `.equpdate`

```python
new_eq = """
FRML <DAMP,STOC>
    PAKGGREVCO2CER = PAKGGREVCO2CER_TARGET * (PAKNYGDPMKTPXN / PAKNYGDPMKTPXN(2025)) + PAKGGREVCO2CER_A $
"""
mpak_v2, newdf = mpak.equpdate(new_eq, add_add_factor=True, calc_add=True,
                               newname='Pakistan real CT')
```

An equation for a variable that already has one replaces it; a new left-hand
side adds an equation.

| Option | Default | Purpose |
|---|---|---|
| `updateeq` | required | New equations separated by newline, each ending with `$` – or a `Makemodel` instance, whose normalized equations (with add factors and fitted equations) are used |
| `newfunks` | `[]` | Extra user functions needed by the new equations |
| `add_add_factor` | False | Generate the `_A` companion |
| `calc_add` | True | Calculate add factors so the new equation reproduces the original model's `lastdf` |
| `do_preprocess` | True | Run the preprocessing pipeline before insertion |
| `newname` | `''` | Name of the new model; default `'<old name> Updated'` |
| `silent` | True | Suppress diagnostics |

The returned dataframe starts from the original model's `lastdf`, with the
calculated add factors filled in.

## Remove equations: `.eqdelete`

```python
mpak_v3, df = mpak.eqdelete('PAKNECONPRVTKN', newname='Pakistan without C eq')
```

The variable becomes exogenous in the new model; its values come from the
input dataframe.

## User functions

A function the equations need that is not built in is passed with `funks=`
(`model(text, funks=[f])`, `Makemodel(..., funks=[f])`, `equpdate(..., newfunks=[f])`):

```python
def smooth(x, x_lag, a):
    return a * x + (1 - a) * x_lag

mmodel = model(eqs, funks=[smooth], modelname='custom')   # used as SMOOTH(Y, Y(-1), 0.7)
```

- The solver calls it with scalar values for one period, not series.
- For `ljit=True` it must be numba-compilable and importable from a module; a
  notebook lambda works without jit only.
- The name must not collide with built-ins (`LOG`, `EXP`, `DLOG`, `DIFF`, `SUM`, ...).
- `modelload` needs the same `funks=` when the saved model uses them.

`modeluserfunk.py` holds the bundled user functions and shows the expected shape.
