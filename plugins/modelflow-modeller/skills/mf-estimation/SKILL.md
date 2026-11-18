---
name: mf-estimation
description: >
  This skill should be used when estimating ModelFlow equations: "estimate an
  equation", "<estimator=ols>", "<est=nls_lmfit>", "<smpl=...>", "OLS", "NLS",
  "fitted values", "actual vs fitted", "residuals of the estimation",
  "static or dynamic fit", "_FITTED", "af_df", "af_level_df", "actual_fitted",
  "fit of the level when the equation is in dlog", "FRML <est=...>",
  "lmfit", "EViews estimation", "c(1)", "coefficients", "param_names",
  "Estimate_ols", "Estimate_nls_lmfit", "with_defaults", "error correction",
  "estimation sample", "ST. constraints", "bounds on coefficients", "initial
  values", or building a model where some equations are estimated.
metadata:
  version: "0.1.1"
---

# Estimating equations while building a model

`Makemodel` estimates every equation whose options contain `estimator=` (or
`est=`), bakes the coefficients into the equation, then normalizes it like any
other. Untagged equations stay as written. Backends live in `modelestimator_new.py`.

## Tagging an equation

```
><estimator=ols, smpl=1995 2020> cons = c(1) + c(2)*y
><est=nls_lmfit, stoc, smpl=1995 2020> dlog(cons) = c(1)*dlog(y) + c(2)*(log(cons(-1)) - log(y(-1)) - c(3))
>y = cons + i + g
```

```python
mm = Makemodel(text, input_df=df)
mm.show
mm.estimation_records      # per equation: estimator, smpl, original and baked expression, estimator_object
mm.render_est              # the model with estimation tables
```

Verified result of the first line:
`FRML <ESTIMATOR=OLS, SMPL=1995 2020> CONS = (0.1622358202)+(0.5979574145)*Y $`.

- `c(1)`, `c(2)` ... are coefficients. Write the constant as `c(1)`; without one
  OLS fits through the origin and warns.
- `<smpl=start end>` – blank-separated inside the tag (a comma would split the
  options). The labels must exist in the data index; an end past the data is
  truncated with a warning.
- `<est>` without a value uses the model-wide `estimator=`; `smpl=` on
  `Makemodel` is the default sample.
- Combine with `stoc` to get add factors and fixing on the estimated equation.

The same tags work in plain FRML text (no markdown) – tell `Makemodel` where
equations start and end (verified, same coefficients as the markdown form):

```python
text = '''
FRML <est=nls_lmfit, stoc, fit, smpl=1995 2020> dlog(cons) = c(1)*dlog(y) + c(2)*(log(cons(-1)) - log(y(-1)) - c(3)) $
FRML <> y = cons + i + g $
'''
mm = Makemodel(text, eq_start='FRML', eq_end='$', input_df=df)
```

## Backends

| Name | Class | Fits |
| --- | --- | --- |
| `ols` | `Estimate_ols` | linear in the coefficients (statsmodels) |
| `nls_lmfit` | `Estimate_nls_lmfit` | non-linear, e.g. error-correction forms (lmfit) |
| `nls_eviews` | `Estimate_nls_eviews` | non-linear through an EViews installation |
| `r_lm` / `r_nls` | `Estimate_r_lm` / `Estimate_r_nls` | in R: lm, Newey-West HAC, ivreg (2SLS), nls, nlsLM – see `mf-r-estimation`; R setup in `mf-r-install` |

Custom settings through a factory, referenced by name. `Makemodel` finds it in
the caller's namespace (or pass `estimator_namespace={'ls': ls}`):

```python
from modelestimator_new import Estimate_nls_lmfit
ls = Estimate_nls_lmfit.with_defaults(input_df=df, smpl=(1995, 2020))
# then in the model:  ><est=ls, stoc> dlog(cons) = ...
```

Named coefficients instead of `c(n)`: `param_names=['lambda', 'beta']` (magic
option or `estimator_kwargs={'param_names': [...]}`) allows `lambda(1)`,
`beta(1)`.

## Fitted values

- **Static (one-step-ahead) fit** – every right-hand side value, lagged
  endogenous included, is the actual data; this is the fit the estimator
  minimized.
  - `rec['estimator_object'].af_df` (Actual, Fitted) and `.residuals_df` –
    in left-hand-side units (`dlog(cons)`, not `cons`), estimation sample only.
    Plain column names, because the left-hand side can be an expression.
  - `.af_level_df` – the variable itself (`CONS`, not `dlog(cons)`): columns
    `CONS__Actual`, `CONS__Fitted`, `CONS__Residuals` (variable name + `__`),
    estimation sample only, residual in the units of `CONS`. It is the estimated
    equation solved for the variable and evaluated with the actual lags, so it
    needs no `fit` tag. When the left-hand side is the variable itself it holds
    the numbers of `af_df`/`residuals_df`. `None` (with a message) if the
    equation can't be solved for the variable. All equations at once:
    `mm.actual_fitted()` (columns `(CONS, Actual)` ...; `level=False` gives the
    left-hand-side units). `plot_actual_vs_fitted(est, level=True)` draws it,
    and the estimation report shows it too.
  - In levels for any period: tag the equation `fit` (`><est=ols, stoc, fit> ...`); Makemodel
    adds `CONS_FITTED = <rhs without the add factor>` (`mm.normal_fit`). Then
    `df.mfcalc(mm.normal_fit)`, or `mm.mmodel(base, solver='res')` / `'res_ng'`
    (each equation once on the input data, no iteration). Both verified to match.
    `res` also overwrites `CONS` with the fit when `CONS_A` is 0 – take actuals
    from the input.
- **Dynamic fit** – a normal multi-period solve: `CONS(-1)` is the model's own
  solved value, so errors accumulate. With add factors set to the residuals,
  solved `CONS` is actual and `CONS_FITTED` equals the static fit again.

Worked example, two estimated equations in FRML form (run 2026-11-15 on
synthetic data):

```python
text = '''
FRML <est=nls_lmfit, stoc, fit, smpl=1995 2020> dlog(cons) = c(1)*dlog(y) + c(2)*(log(cons(-1)) - log(y(-1)) - c(3)) $
FRML <est=ols,       stoc, fit, smpl=1995 2020> inv = c(1) + c(2)*y $
'''
mm = Makemodel(text, eq_start='FRML', eq_end='$', input_df=df)

for rec in mm.estimation_records:          # 1. static fit, estimation sample
    est = rec['estimator_object']
    print(est.endo_var, est.af_df, est.residuals_df)   # left-hand-side units
    print(est.af_level_df)                             # CONS__Actual, CONS__Fitted, CONS__Residuals

mm.actual_fitted()                         # all equations, columns (CONS, Actual) ...

mfit = mm.mmodel                           # 2. static fit in levels, any period
base = mfit.insertModelVar(df)
r = mfit(base, 1995, 2020, solver='res_ng')
r[['CONS_FITTED', 'INV_FITTED']]
```

`mm.normal_fit` holds the generated fitted equations (rounded):

```
CONS_FITTED = CONS(-1)*EXP( 1.091*(LOG(Y)-LOG(Y(-1))) - 1.167*(LOG(CONS(-1))-LOG(Y(-1)) + 0.514) )
INV_FITTED  = -0.583 + 0.204*Y
```

`af_df` is `dlog(cons)` for the first equation and `inv` for the second;
`af_level_df` is `CONS` and `INV`. Over the estimation sample
`af_level_df['CONS__Fitted']` equals `CONS_FITTED` from `res_ng` (checked
2026-11-17 on the toy model consumption equation,
`modeltest/estimation/toymodel_consumption_fit.py` in the modelflow repo).

## Traps

- **A variable named `C`** in an estimated equation: `c(-1)` is read as a
  coefficient and estimation fails with `ValueError: invalid literal for int()`.
  `C(...)` is always a coefficient, even with another `est_param`, so rename the
  variable (`CONS`).
- `input_df` is required when any equation is tagged, unless the estimator factory
  carries its own.
- The baked coefficients are fixed numbers in the model; re-estimating means
  rebuilding the model.
- Estimation runs when `Makemodel` is created – a large model with many tagged
  equations takes time on every rebuild.

## Deeper reference

`references/estimation.md`: backend choice, the inline `ST.` constraint syntax
(`=[lo,hi]`, `>`, `<`, `=`, `~`, `:=`), the three ways to give initial values,
inspecting an estimator object, recipes (bounded ECM speed, pinned or tied
coefficients) and writing a new backend.
