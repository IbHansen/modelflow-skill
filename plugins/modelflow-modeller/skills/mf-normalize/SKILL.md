---
name: mf-normalize
description: >
  This skill should be used when a ModelFlow equation is not written as
  "variable = expression": "normalize", "normalise", "log(c/p) = ...", "dlog on the
  left", "solve for another variable", "implicit equation", "___RES",
  "modelnormalize", "Problem normalizing", or when choosing which variable an
  equation determines.
metadata:
  version: "0.1.0"
---

# Normalization

The solvers need each equation as `X = F(...)`. `modelnormalize.normal` rewrites an
equation with an expression on the left (`DLOG(C) = ...`, `LOG(C/P) = ...`) by
solving it for one variable with SymPy. `Makemodel`, `%%Makemymodel` and
`df.mfcalc` call it for every equation; a plain `model(text)` does not.

## Which variable

| Write | Normalized for |
| --- | --- |
| `log(c/p) = 0.5*log(y)` | `C`, the first variable on the left |
| `<endo=p> log(c/p) = 0.5*log(y)` | `P` |
| `<endo=y,endo_lhs=false> c = 0.6*y` | `Y`, a right-hand-side variable |
| `<implicit> c + s = y` | nothing: `C___RES = (Y) - (C+S)`, solved by Newton |

Verified output:

```
FRML <> C = P*EXP( (0.5*LOG(Y)) ) $
FRML <ENDO=P> P = C*EXP(- (0.5*LOG(Y)) ) $
FRML <ENDO=Y,ENDO_LHS=FALSE> Y = 1.66666666666667*C $
FRML <IMPLICIT> C___RES = ( Y ) - ( C+S ) $
```

The current-period endogenous variable must not appear on both sides after
choosing; lags of it may (`DLOG(C)` uses `C(-1)`).

## Calling it directly

```python
import modelnormalize as nz
r = nz.normal('dlog(c) = 0.5*dlog(y)', add_add_factor=True, make_fixable=True)
r.normalized        # C = (C(-1)*EXP(C_A+ ...)) * (1-C_D)+ C_X*C_D
r.calc_add_factor   # C_A = ...
r.fitted            # with make_fitted=True
```

Arguments: `the_endo`, `add_add_factor`, `add_suffix`, `endo_lhs`,
`make_fixable`, `make_fitted`, `implicit`. They are what the FRML options map to
(`mf-frml-options`).

## Implicit and hybrid models

- An all-`___RES` model is *implicit*; a mix is *hybrid*. Both are solved by the
  Newton solvers; the default choice handles it (`mf-solvers`).
- `X___RES` is the residual; X itself is the unknown.
- Use implicit form only when normalizing fails or the equation has several
  solutions; normalized equations solve faster and support Gauss-Seidel.

## When normalizing fails

`Problem normalizing:` followed by the equation means SymPy could not isolate the
variable. Usual causes:

- the variable appears inside a user function or `MIN`/`MAX`/`ABS`;
- the equation is not invertible for that variable (quadratic, periodic);
- a typo creates a variable that shadows the intended one.

Fixes: rewrite by hand into `X = ...`, choose another variable with `<ENDO=>`, or
use `<IMPLICIT>`.
