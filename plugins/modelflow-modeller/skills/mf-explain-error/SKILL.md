---
name: mf-explain-error
description: >
  This skill should be used when the user pastes a ModelFlow error, warning or
  traceback and wants to know what it means: "/mf-explain-error", "what does this
  error mean", "why did my model fail", "Houston, we have a problem", "not
  converged", "Problem normalizing", "is not a function", or any message printed
  while building or solving a model.
argument-hint: "<pasted error message or traceback>"
metadata:
  version: "0.1.0"
---

# /mf-explain-error

Map the message to its cause and the fix. Answer in this shape: what happened (one
sentence), the equation or variable involved, the fix, and how to check it is fixed.
Quote the equation from the message. If the message names a period, say it.

## Messages while building

| Message | Meaning | Fix |
| --- | --- | --- |
| `No FRML statements found in the model text` | text with `$` but no `FRML`, or empty input | one equation per line without `$`, or `FRML <> ... $` |
| `X( : X is not a function. Lags and leads are written with a sign ...` | `X(1)` for a lead, a blank inside `X( -1 )`, `X(2002Q1)` without quotes, or an unknown function | `X(+1)`, `X(-1)`, `X('2002Q1')`, or pass the function in `funks` |
| `A variable at a fixed period (like X(2002)) can not be on the left hand side` | `X(2002) = ...` | write the equation for `X` |
| `On the left hand side several times: X` / `X is defined by N equations ...` | duplicate definitions; the last is used | `<DROP>` the unwanted ones |
| `Problem normalizing:` + equation | SymPy can not solve for the chosen variable | `mf-normalize`: `<ENDO=>`, `<IMPLICIT>`, or rewrite |
| `You can not dampen equations with several left hand sides` | `<DAMP>` (or a `Z` in the FRML name) on a multi-LHS equation | remove the option; check names containing `Z` |
| `The add factor calculation model should be recursive` | a `<CALC_ADD_FACTOR>` equation depends on another add factor in the same period | rewrite the add-factor equations |
| `input_df is required when any equation has an <estimator=...>` | tagged equations but no data | `Makemodel(..., input_df=df)` |
| `ValueError: invalid literal for int() with base 10: ''` during estimation | a variable named `C` with a lag, read as a coefficient | rename the variable (`mf-estimation`) |
| `The feedback variables are not directly connected, so the feedback order is left as found` | information only | nothing |
| `FRML does not match required pattern` | a malformed FRML after template expansion | inspect `mm.showexpanded_frml` |

## Messages while solving

| Message | Meaning | Fix |
| --- | --- | --- |
| `Houston, we have a problem! This equation raises an error:` | an equation failed; the report shows equation, period and input values; data at failure in `mmodel.errdump` | read the values: a 0 or negative under `LOG`, missing data (`mf-debug-model`) |
| `math domain error` | `LOG` or `SQRT` of a value ≤ 0 | supply data / starting values; check the scenario did not push the variable negative |
| `NameError: name 'dlog' is not defined` (or `diff`, `movavg`, `pct_growth`) | shorthand in a model built with plain `model()` | build with `Makemodel` or rewrite |
| `UPS X looks like a function call, but it is not an allowed function name` | `X(...)` with an unknown function | pass the function in `funks` |
| `<period> not converged in N iterations` | Gauss-Seidel did not meet `relconv` | `mf-solvers`: `alfa`, `max_iterations`, `newton_fbmin_ng` |
| `<period> not converged in N outer iterations (last outer res~R)` | `newton_fbmin_ng` did not converge | more `max_iterations`, another `jacobian`, damping |
| `<period> not converged, NaN or inf in N variables after K iterations: ...` | the iteration produced NaN | the first named variable's equation and inputs (`mf-debug-model`) |
| `<period> NaN or inf in N endogenous variables: ...` | NaN or inf after the period, e.g. division by 0 | as above |
| `... refers to an endogenous variable at a fixed period inside the solve span` | `X(2025)` with X endogenous, solved period by period | a stacked solver, another span, or an exogenous copy |
| `The period P in a reference like X(P) is not a row in the dataframe index` | fixed period missing from the data | extend the data or fix the label |
| `Unknown ng solver` | misspelled solver | the message lists the valid names |

If the message is not listed, read the traceback's last ModelFlow frame, find the
function in the source, and explain from there. Ask for the full traceback when
only the last line was pasted.
