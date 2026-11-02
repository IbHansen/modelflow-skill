---
name: mf-frml-options
description: >
  This skill should be used when choosing or explaining the options in a ModelFlow
  FRML name: "<STOC>", "<EXO>", "<ADD>", "<FIT>", "<IDENT>", "<DAMP>", "<DROP>",
  "<ENDO=...>", "<IMPLICIT>", "<CALC_ADD_FACTOR>", "add factor", "_A", "_X", "_D",
  "_FITTED", "exogenize", "fix a variable", "make an equation fixable",
  "behavioral equation", or "what does this option generate".
metadata:
  version: "0.1.0"
---

# FRML options

Options sit in the `<...>` after `FRML`, separated by commas: `<STOC,DAMP>`,
`<ENDO=P>`, `<EST=OLS, STOC, SMPL=1995 2020>`. Case does not matter.

## When options act

Most options act when the model is **built** by `Makemodel` / `%%Makemymodel`
(through `modelnormalize.normal`). A plain `model(text)` only reads `DAMP`/`Z`,
`CALC_ADD_FACTOR`, `MATRIX` and `ENDO`; `<STOC>` there does nothing. Build with
`Makemodel` when equations need add factors or fixing.

## What each option generates (Makemodel)

| Option | Generates | Use for |
| --- | --- | --- |
| `<>` | the equation as written (normalized if needed) | identities |
| `<IDENT>` | same as `<>`; marks an identity (`get_histmodel` selects these) | identities in imported models |
| `<ADD>` | add factor `X_A` in the equation + `<CALC_ADD_FACTOR>` equation for `X_A` | judgement on an identity-like equation |
| `<EXO>` | `X = (rhs)*(1-X_D) + X_X*X_D` | equations that may be exogenized |
| `<STOC>` | `ADD` + `EXO`: `X_A`, `X_X`, `X_D` and the add-factor equation | behavioural (estimated) equations |
| `<FIT>` | an extra `X_FITTED = rhs` equation | comparing fit with history |
| `<ADD_SUFFIX=_AF>` | add factor named `X_AF` instead of `X_A` | |
| `<ENDO=P>` | normalize for `P` instead of the first LHS variable | `log(c/p) = ...` solved for P |
| `<ENDO=Y,ENDO_LHS=FALSE>` | normalize for a right-hand-side variable | inverting an equation |
| `<IMPLICIT>` | `X___RES = (rhs) - (lhs)`; solved by Newton | equations that can not be normalized |
| `<DROP>` | the equation is left out | a duplicate definition, a switched-off equation |
| `<EST=...>`, `<SMPL=...>` | the equation is estimated first (`mf-estimation`) | |

Read by the solver at run time:

| Option | Effect |
| --- | --- |
| `<DAMP>` | Gauss-Seidel damps this equation with `alfa`: `(1-alfa)*X + alfa*rhs`. Only for a single LHS. |
| `<CALC_ADD_FACTOR>` | moved to a separate add-factor model (`m.calc_add_factor_model`, must be recursive). After a solve where some `X_D` is non-zero it computes `X_A` for the fixed variables, so unfixing later continues from the same path. Generated, not written by hand. `do_calc_add_factor=False` in the call skips it. |
| `<MATRIX>` | the LHS is a matrix-valued (object) variable |
| `<ENDO=X>` | the declared unknown for the Newton solvers |

## Verified example

```
><stoc> dlog(c) = 0.5*dlog(y) + 0.1*(log(c(-1))-log(y(-1)))
>y = c + i + g
><exo> i = 0.2*y(-1)
```

builds

```
FRML <STOC> C = (C(-1)*EXP(C_A+ (0.5*((LOG(Y))-(LOG(Y(-1))))+0.1*(LOG(C(-1))-LOG(Y(-1)))) )) * (1-C_D)+ C_X*C_D $
FRML <> Y = C+I+G $
FRML <EXO> I = (0.2*Y(-1))* (1-I_D)+ I_X*I_D $
FRML <CALC_ADD_FACTOR> C_A = - ((0.5*((LOG(Y))-(LOG(Y(-1))))+0.1*(LOG(C(-1))-LOG(Y(-1))))) +LOG(C)-LOG(C(-1)) $
```

with exogenous `C_A, C_D, C_X, G, I_D, I_X`.

## Companion variables

| Variable | Meaning | Default |
| --- | --- | --- |
| `X_A` | add factor (residual) added to the equation | 0 = no adjustment |
| `X_D` | 1 = X is fixed to `X_X` in that period | 0 |
| `X_X` | the value X is fixed to | |
| `X_FITTED` | the equation's fitted value | |

A model finds its fixable variables from the data structure: every endogenous X
with both `X_X` and `X_D` exogenous is in `m.fix_endo`. `m.fix(df, 'pattern',
start, end)` sets `_D = 1` and `_X` to the current values; `m.unfix(...)` sets
`_D = 0`. Missing companion columns are created as 0.0 when solving.

## Traps

- **Any FRML name containing the letter Z is damped** – the solver treats `Z` as
  the old damping marker. `<ZONE>` or `<EST=MYZ>` damp the equation silently.
  `/mf-check-model` reports these.
- `<DAMP>` with several LHS variables raises an assertion.
- `<STOC>` on an identity adds a meaningless add factor; use `<>`.
