---
name: mf-estimation
description: >
  This skill should be used when estimating ModelFlow equations: "estimate an
  equation", "<estimator=ols>", "<est=nls_lmfit>", "<smpl=...>", "OLS", "NLS",
  "lmfit", "EViews estimation", "c(1)", "coefficients", "param_names",
  "Estimate_ols", "Estimate_nls_lmfit", "with_defaults", "error correction",
  "estimation sample", "ST. constraints", "bounds on coefficients", "initial
  values", or building a model where some equations are estimated.
metadata:
  version: "0.1.0"
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

## Backends

| Name | Class | Fits |
| --- | --- | --- |
| `ols` | `Estimate_ols` | linear in the coefficients (statsmodels) |
| `nls_lmfit` | `Estimate_nls_lmfit` | non-linear, e.g. error-correction forms (lmfit) |
| `nls_eviews` | `Estimate_nls_eviews` | non-linear through an EViews installation |

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
