---
name: mf-r-estimation
description: >
  This skill should be used when estimating ModelFlow equations with R as the
  engine: "estimate in R", "<estimator=r_lm>", "<estimator=r_nls>",
  "Estimate_r", "Estimate_r_lm", "Estimate_r_nls", "modelestimator_r", "lm",
  "Newey-West", "HAC standard errors", "robust standard errors", "ivreg",
  "2SLS", "TSLS", "instrumental variables", "instruments", "nls", "nlsLM",
  "minpack.lm", "Levenberg-Marquardt", "Breusch-Godfrey", "Breusch-Pagan",
  "RESET", "Jarque-Bera", "weak instruments", "Sargan", "Wu-Hausman",
  "R summary", "the R script", "keep_r_files", "residuals from R differ",
  or "same results as EViews TSLS / HAC".
metadata:
  version: "0.1.0"
---

# Estimating with R

`modelestimator_r` gives ModelFlow estimators that run the statistics in R.
Python does the time-series algebra (DLOG, lags, the regressor columns). R
gets plain data columns and fits them. The classes are ordinary estimator
backends: everything in `mf-estimation` works the same way: `coef_ser`,
`tvalues`, `af_df`, `af_level_df`, the HTML report and Makemodel tags.

Needs R plus the R packages. See `mf-r-install` (normally
`MODELFLOW_RSCRIPT` pointing at the conda environment `mfr`). Ships with the
ModelFlow release after 2.94; until then use a source checkout.

## Methods

| `method=` | Class | R | Gives |
| --- | --- | --- | --- |
| `lm` | `Estimate_r_lm` | `stats::lm` | OLS; same numbers as `Estimate_ols` |
| `hac` | `Estimate_r_lm` | `lm` + `sandwich::NeweyWest` | OLS coefficients, Newey-West standard errors |
| `ivreg` | `Estimate_r_lm` | `ivreg::ivreg` (or `AER::ivreg`) | 2SLS with instruments |
| `nls` | `Estimate_r_nls` | `stats::nls` (`port` when bounds are given) | non-linear least squares |
| `nlsLM` | `Estimate_r_nls` | `minpack.lm::nlsLM` | NLS, Levenberg-Marquardt; robust to poor starting values |

`Estimate_r(eq, method=...)` picks the class. The linear methods take any
equation `Estimate_ols` takes. The non-linear ones take what
`Estimate_nls_lmfit` takes, with the limits under Traps.

## In Python

```python
from modelestimator_r import Estimate_r
r = Estimate_r.with_defaults(input_df=df, smpl=(1975, 2023))

EQ = "DLOG(CON) = C(1) + C(2)*DLOG(INC) + C(3)*(LOG(CON(-1)) - LOG(INC(-1)))"
ols = r(EQ)                                    # method='lm'
hac = r(EQ, method="hac", hac_lag=2)           # hac_lag=None: automatic (bwNeweyWest)
iv  = r(EQ, method="ivreg",
        instruments=["DLOG(GOV)", "DLOG(GOV(-1))", "LOG(CON(-1)) - LOG(INC(-1))"])
nls = r("DLOG(CON) = C(1) + C(2)*DLOG(INC) - C(3)*(LOG(CON(-1)) - C(4)*LOG(INC(-1)))"
        " ST. C(3)~0.2; C(4)~1", method="nlsLM")

ols.coef_ser, ols.tvalues                      # as for every estimator
ols                                            # HTML report in a notebook
```

Checked 2026-11-18 against Python on synthetic data
(`modeltest/rtest/r_estimation_test.py`):
- `lm` coefficients and t-values equal `Estimate_ols` to 1e-14.
- `hac` standard errors equal statsmodels HAC (Bartlett, `maxlags=2`, scaled
  by n/(n-k)) to 6e-15.
- `ivreg` equals a numpy 2SLS to 2e-14.
- `nls` and `nlsLM` equal `Estimate_nls_lmfit` to 1e-8.

## In Makemodel

```
><estimator=r_lm, stoc, smpl=1975 2023> dlog(con) = c(1) + c(2)*dlog(inc) + c(3)*(log(con(-1)) - log(inc(-1)))
><estimator=r_nls, stoc, smpl=1975 2023> dlog(con) = c(1) + c(2)*dlog(inc) - c(3)*(log(con(-1)) - c(4)*log(inc(-1))) ST. c(3)~0.2; c(4)~1
```

`r_lm` is always `method='lm'` and `r_nls` always `method='nls'`. The tag
can't carry a method. For `hac`, `ivreg` or `nlsLM`, make a factory and use
its name. Makemodel finds it in the notebook namespace:

```python
rhac = Estimate_r.with_defaults(input_df=df, method='hac', hac_lag=2)
riv  = Estimate_r.with_defaults(input_df=df, method='ivreg',
                                instruments='DLOG(GOV) DLOG(GOV(-1)) LOG(CON(-1)) - LOG(INC(-1))')
# ><est=rhac, stoc, smpl=1975 2023> dlog(con) = ...
```

Verified: `<estimator=r_lm>`, `<estimator=r_nls>` and `<est=rhac>` give the
same baked equation as `<estimator=ols>` / lmfit.

## Options

| Option | Default | Meaning |
| --- | --- | --- |
| `instruments` | – | `ivreg`: list of ModelFlow expressions, or one string separated by blanks/commas (`"DLOG(GOV) LOG(Z(-1))"`, see Traps). As in EViews, list the exogenous regressors too. The constant is added by itself. |
| `hac_lag` | `None` | `hac`: truncation lag; `None` = automatic |
| `diagnostics` | `True` | residual tests (below) |
| `bg_order` | `2` | lag order of Breusch-Godfrey |
| `fit_kws` | `{}` | extra arguments to the R function. Strings are inserted **as R code**: `{'control': 'nls.control(maxiter = 500)'}`. An R string needs its own quotes: `{'algorithm': '"port"'}`. |
| `default_params` | `{}` | NLS starting values, `{'C__3': {'value': 0.2}}` (default start 0.1) |
| `check_residuals` | `True` | compare R's residuals with ModelFlow's |
| `keep_r_files` | `False` | keep the folder with script, data and output |
| `backend` | `'auto'` | `'rscript'`; `'rpy2'` only when asked for (`'auto'` = Rscript on Windows) |
| `rscript_path` | – | R location, if not found by itself (see `mf-r-install`) |
| `r_timeout` | – | seconds before Rscript is stopped |

Constraints (inline `ST.` or `constraints=`), NLS only: starting values
`C(3)~0.2`, fixed `C(4)=1`, bounds `C(3)=[0, 0.25]` / `>` / `<`. The linear
methods take no constraints, like `Estimate_ols`.

## What R returns

`est.regression_model` is an `RFitResult`:

| Attribute | Content |
| --- | --- |
| `summary_text` | R's own printed `summary()` |
| `coef_table` | Estimate, Std. Error, t value, Pr(>\|t\|), indexed `C__1` ... |
| `params`, `bse`, `tvalues`, `pvalues` | columns of `coef_table` as Series |
| `vcov` | coefficient covariance (Newey-West for `hac`) |
| `stats` | `nobs`, `r_squared`, `adj_r_squared`, `se_regression`, `ssr`, `log_likelihood`, `akaike`, `schwarz` (per observation, as EViews), `durbin_watson`, `mean_dependent`, `sd_dependent`; NLS also `converged` (1/0), `iterations` |
| `diagnostics` | test, statistic, p_value, note |
| `fitted`, `resid` | on the time index of the sample used |
| `call` | the R call, with the instrument definitions for `ivreg` |
| `script`, `workdir` | the R script (rerun it in R to reproduce); folder if `keep_r_files=True` |

Diagnostics: Jarque-Bera always. With `lmtest`, for `lm`/`hac`:
Breusch-Godfrey, Breusch-Pagan and Ramsey RESET. For `ivreg`: weak
instruments, Wu-Hausman and Sargan.

## Traps

- **"WARNING: the residuals from R differ from ModelFlow's residuals"** – R
  estimated another equation than ModelFlow will simulate. It should never
  happen. Rerun with `keep_r_files=True` and read `est.regression_model.script`.
  `est.residual_check_max_diff` holds the difference (≈1e-15 normally).
- **NLS translation**: the normalized right-hand side becomes an R formula.
  Allowed: `+ - * / **`, `LOG`, `EXP`, `ABS`, `SQRT`, lags `X(-k)`, leads
  `X(+k)`, and whatever normalization expands into these (`DLOG`, `DIFF`,
  `MOVAVG`, `PCT_GROWTH` ...). Anything else is refused before R runs, with
  the term named. Use `Estimate_nls_lmfit` for it.
- NLS coefficients must be on the right-hand side only.
- `:=` relations (and `expr` in `default_params` or `constraints`) are refused
  by the R backends. Use `Estimate_nls_lmfit`, or substitute the relation into
  the equation.
- `ivreg` instruments **as one string**: commas and semicolons always
  separate. Blanks separate too, except next to an operator, so
  `"DLOG(GOV) LOG(CON(-1)) - LOG(INC(-1))"` is two instruments. A blank-only
  list therefore can't hold a unary minus as a separate instrument
  (`"X -Y"` is `X - Y`). Use a comma or the list form for that; the sign of an
  instrument doesn't matter anyway.
- `ivreg`: an instrument list without the exogenous regressors gives a wrong
  2SLS. A constant written as `-C(1)`, or in another slot than `C(1)`, is
  still used as its own instrument.
- `ivreg` and lags in the instruments: the sample shrinks to where every
  instrument exists, and a sample message is printed (twice).
- `with_defaults` keywords override per call: `r(EQ, method='hac')` on an `lm`
  factory works.
- Every fit starts an `Rscript` process (about 0.2 s for a small OLS, measured
  2026-11-18). A model with many R-estimated equations pays that on every
  `Makemodel` rebuild.
