---
name: mf-data
description: >
  This skill should be used when preparing data for a ModelFlow model: "databank",
  "dataframe for the model", "index", "annual or quarterly", "missing variables",
  "NaN", "starting values", "mfcalc", "upd", "insertModelVar", "baseline data",
  "matrix variable", or when a model solves to zeros or NaN because of its data.
metadata:
  version: "0.1.0"
---

# Data for a model

A model solves on a pandas DataFrame: rows are periods, columns are variables.

## Shape

- **Index**: integer years for annual models (`range(1980, 2101)`), or a
  `PeriodIndex` / period strings for other frequencies. Fixed-period references
  (`X(2002)`, `X('2001q2')`) look the period up in this index, so the label must
  match.
- **Columns**: upper-case variable names. Make them so with
  `df.columns = df.columns.str.upper()`.
- **Values**: float. Integer columns of `_X` / `_D` are converted when fixing.
- Lags need history: solving from 2020 with `X(-4)` reads 2016–2019.

## Missing variables

Every model variable missing from the frame is created as **0.0** when solving
(`insertModelVar`). That is right for add factors (`_A`), fix dummies (`_D`) and
values (`_X`), and wrong for a real exogenous variable: a forgotten `G` silently
becomes 0. Check with `/mf-check-model ... --data`, or

```python
missing = sorted(v for v in mmodel.exogene if v not in df.columns)
df = mmodel.insertModelVar(df)          # add them explicitly, then fill
```

NaN in an exogenous variable or in the history of an endogenous one propagates
through the solution; the solvers report NaN variables per period.

## Creating and changing data

`upd` changes values over a period:

```python
df.upd('<2020 2030> G = 100')        # set
df.upd('<2020 2030> G + 5')          # add
df.upd('<2020 2030> G * 1.1')        # multiply
df.upd('<2020 2030> G % 10')         # same as * 1.1 in each period
```

`mfcalc` runs equations on a frame (normalized first, so `DLOG` works); use it
to derive data:

```python
df = df.mfcalc('REALGDP = GDP / DEFL')
df = df.mfcalc('<2021 2030> dlog(POP) = 0.01')     # grow at 1 %
```

A growth equation like `dlog(X) = 0.01` needs a positive starting value in the
period before; with 0 the log fails (`math domain error`).

## Matrix variables

An equation marked `<MATRIX>` has a matrix-valued left-hand side; its column holds
objects (object dtype). The Newton solvers can not include matrix variables in
their Jacobian, so keep them out of simultaneous blocks solved by Newton.

## Baseline from history

For a model that should reproduce history:

1. `mmodel.test_model(df, start, end)` evaluates each equation once on the data
   and lists equations whose result differs (`/mf-check-model --test`).
   Identities should not differ; behavioural equations differ by their residual.
2. Compute the add factors that make the behavioural equations fit:

```python
df = mmodel.insertModelVar(df)
df = mmodel.calc_add_factor_model(df, 2001, 2025)   # X_A = residual, per period
res = mmodel(df, 2001, 2025)                        # reproduces the data
```

`calc_add_factor_model` exists when the model has `<STOC>` or `<ADD>` equations.

### Identities that do not hold in the data — `get_histmodel`

Add factors only fix behavioural equations. If an identity does not hold in the
data (rounding aside), the model can not reproduce history for that variable or
anything that depends on it. Recalculate those identities in history first:

1. Tag them `<IDENT>` (`<ident>` in Makemodel/`%%Makemymodel`), the same as `<>`
   for solving.
2. `mhist = mmodel.get_histmodel()` is a model of the `<IDENT>`/`<I>` equations
   only (`tags=` picks other frml names). Run it over the history:
   `df = mhist(df, start, end)`. The tagged variables now equal their identity.
3. Check again: identities that held with the old values can stop holding once
   their inputs are recalculated. Tag those too and repeat until nothing changes
   (Mona 2026: 11 failing identities grew to 108 tagged, including GDP aggregates
   that moved by < 0.1 %).
4. Then compute the add factors (`calc_add_factor_model`, or
   `init_addfactors` for a Makemodel) on the recalculated `df`. The model now
   reproduces history for every variable.

Values before `start` stay as in the data. Show the user the largest changes the
hist model makes, as they change the historic data.
