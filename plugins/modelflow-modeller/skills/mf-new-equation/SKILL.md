---
name: mf-new-equation
description: >
  This skill should be used to draft a ModelFlow equation from a description:
  "/mf-new-equation", "write an equation for", "add a consumption function",
  "error-correction equation", "add an identity", "translate this formula to
  ModelFlow", or "how do I write X depends on Y with a lag".
argument-hint: "<description of the relationship>"
metadata:
  version: "0.1.0"
---

# /mf-new-equation

Draft one or more ready-to-paste ModelFlow equations from the description, check
that they build, and show what they generate.

## Steps

1. **Classify** each relationship:
   - accounting identity → `<>` (or `<IDENT>` in models that mark identities);
   - behavioural with coefficients known → `<STOC>` (add factor and fixing);
   - to be estimated → `<est=ols>` (linear) or `<est=nls_lmfit>` (non-linear,
     error correction), plus `stoc` and `smpl=start end`;
   - cannot be normalized → `<IMPLICIT>`.
2. **Write it** in markdown model form (`>` lines) with the conventions of
   `mf-dsl`: `DLOG`/`DIFF` allowed, signed lags `X(-1)`, leads `X(+1)`,
   coefficients `c(1)`, `c(2)` for estimation. Use the model's existing variable
   names when they are known (read the model or ask); upper case.
   Error-correction template:
   `dlog(X) = c(1)*dlog(Y) + c(2)*(log(X(-1)) - log(Y(-1)) - c(3))`
3. **Check it builds**, when ModelFlow is available:
   ```python
   from modelconstruct_estimation import Makemodel
   mm = Makemodel(text)            # add input_df=df when estimating
   print(mm.normal_frml)
   ```
   Fix parse or normalization errors before showing the result.
4. **Show** the equation to paste, the normalized FRML it produces, and the new
   variables it introduces (endogenous, exogenous, `_A/_X/_D` companions) – the
   data must supply the new exogenous ones.

## Rules

- Never name a variable `C` in an estimated equation (clash with `c(n)`).
- Avoid the letter `Z` in FRML options (it switches on damping).
- One equation per endogenous variable; if the model already defines it, say so
  and offer the replacement with `<DROP>` on the old one or `mmodel.equpdate`.
- State any assumption about units (levels vs logs, rates in percent or
  fractions) in one line.
