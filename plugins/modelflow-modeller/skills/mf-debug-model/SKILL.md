---
name: mf-debug-model
description: >
  This skill should be used when a ModelFlow model fails while solving or gives
  wrong numbers: "Houston, we have a problem", "math domain error", "NameError",
  "division by zero", "NaN", "inf", "errdump", "the result is zero", "the result
  is wrong", "an equation raises an error", "debug the model", or a traceback from
  solving a model.
metadata:
  version: "0.1.0"
---

# Debugging a model

For a pasted traceback or message, `/mf-explain-error` maps it to a cause. This
skill is the method.

## A runtime error in an equation

Without `ljit`, a failing equation prints:

```
Houston, we have a problem!
This equation raises an error:
>>: FRML <> W=EXP(LOG(W(-1))+0.1)$
In: 2003
>> Values of terms in used:
 term  value
W(-1)    0.0
>> This shows the arguments to LOG, they should be numbers > 0:
log(arg)  value           status
   W(-1)    0.0 Bad log argument
```

- The equation, the period and the input values are printed; arguments to `LOG`
  are checked.
- `mmodel.errdump` (and `mmodel.lastdf`) hold the data at the point of failure.
- With `ljit=True` there is no such report: rerun without `ljit` to locate the
  equation.

## Typical causes

| Symptom | Usual cause | Fix |
| --- | --- | --- |
| `math domain error`, bad log argument | a value ≤ 0 inside `LOG`; often a variable missing from the data (created as 0) or no starting value | supply the data; check `/mf-check-model --data` |
| `NaN or inf in N endogenous variables: X` with finite inputs | a denominator that is 0 (gives inf, no exception) – again often missing data | as above |
| `NameError: name 'dlog' is not defined` (also `diff`, `movavg`, `pct_growth`) | a shorthand in a model built with plain `model()` | build with `Makemodel`, or rewrite (`mf-normalize`) |
| `UPS X looks like a function call` / `X( : X is not a function` | `X(1)` instead of `X(+1)`, a blank in `X( -1 )`, or an unknown function | fix the lag, or pass the function in `funks` |
| NaN / inf in N variables | NaN in data or a diverging iteration | see below |
| result 0 for a variable | the variable is exogenous by mistake and missing from the data, or its equation is `<DROP>`ped or defined twice | `mmodel.allvar['X']['frml']`, check `X in mmodel.endogene` |
| `not converged in N iterations` | see `mf-structure` and `mf-solvers` | |

## Inspecting one variable

```python
mmodel.allvar['PAKNYGDPMKTPKN']['frml']         # the equation as solved
mmodel.PAKNYGDPMKTPKN.tracepre(up=1)            # its inputs
mmodel.get_eq_values('PAKNYGDPMKTPKN')          # input values of the equation
print(mmodel.make_los_text)                     # generated solver code (no jit)
```

`mmodel.test_model(df, start, end, showall=True, showinput=True)` evaluates every
equation once and shows each one that does not reproduce the data, with its inputs
– the quickest way to find a wrong equation in a model with known history.

## NaN

1. Find the earliest period and the first NaN variable in solve order
   (`mmodel.solveorder`).
2. Look at its equation and inputs in that period; the NaN usually enters from
   data (`df[cols].isna()` over the span and the lag periods).
3. If the inputs are finite, the equation itself produces it (log of a negative,
   0/0) – often after a large shock pushed a variable negative.

## Wrong but finite results

- Compare with a solve by another solver (`solver='sim_ng'` vs
  `'newton_fbmin_ng'`); a difference larger than `relconv` means one did not
  converge.
- Check options left over from an earlier call (`mmodel.oldkwargs`); pass
  `reset_options=True`.
- Check fixed variables: `_D = 1` keeps a variable at `_X` whatever the shock.
