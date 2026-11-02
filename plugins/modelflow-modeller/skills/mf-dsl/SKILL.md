---
name: mf-dsl
description: >
  This skill should be used when writing, reading or fixing ModelFlow model equations:
  "write an equation", "FRML", "the model language", "BLL", "lags and leads",
  "X(-1)", "X(+1)", "X(2002)", "DLOG", "DIFF", "MOVAVG", "PCT_GROWTH", "which functions
  can I use", "LIST", "DO ... ENDDO", "sum(", "user function", "funks", or when an
  equation will not parse.
metadata:
  version: "0.1.0"
---

# The ModelFlow equation language

## One equation

```
FRML <options> LHS = expression $
```

- `FRML` and the terminating `$` may be left out when equations are written one
  per line; `model(text)` and `Makemodel` add them.
- `<options>` may be left out; `<>` is added. Options are listed in
  `mf-frml-options`.
- Names are upper-cased. Letters, digits and `_`; start with a letter.
- Comments start with `£` (FRML text) or are any non-model line in markdown.
- Each equation must be legal Python after translation, so `**` is the power
  operator and `^` is not.

## Time

| Write | Means |
| --- | --- |
| `X` | current period |
| `X(-1)`, `X(-4)` | lag |
| `X(+1)` | lead – the sign is required; `X(1)` is an error |
| `X(2002)` | X in the year 2002, wherever the model is solved |
| `X('2001q2')` | X in a fixed non-annual period, written as the dataframe index key |

No blanks inside the parentheses. Fixed periods are evaluated only by the ng solvers
and may not appear on the left-hand side. Leads make the model forward-looking and
change the solver (`mf-solvers`).

## Functions

Callable in an equation (evaluated by the solver):
`LOG`, `EXP`, `SQRT`, `ABS`, `MIN`, `MAX`, `FLOAT`, `TANH`, `ERF`, `LOGIT`,
`LOGIT_INVERSE`, `NORMCDF`, `CLOGNORM`, `QGAMMA`, `SUM_EXCEL`, `RECODE`, plus any
function passed with `funks=[...]`.

Shorthands that must be **normalized away** before solving: `DLOG(X)`,
`DIFF(X)`, `MOVAVG(X,n)`, `PCT_GROWTH(X)`. `Makemodel`, `%%Makemymodel` and
`df.mfcalc` rewrite them (`DLOG(X)` → `LOG(X)-LOG(X(-1))`). A plain `model(text)`
does not: solving fails with `NameError: name 'dlog' is not defined`. Write them in
a `Makemodel` model, or rewrite by hand.

A name followed by `(` that is not a function raises `X( : X is not a function`.

## User functions

```python
def smooth(x, x_lag, a):
    return a * x + (1 - a) * x_lag

m = model(text, funks=[smooth])          # used as SMOOTH(Y, Y(-1), 0.7)
```

Functions get scalars (one period) and return a scalar. With `ljit=True` they must
be compilable by numba. `modeluserfunk.py` holds the shipped ones.

## Templates: LIST, DO, sum

```
>list sectors = sectors : agr ind ser / market : 0 1 1
>do sectors
>  <stoc> {sectors}_y = 0.8*{sectors}_y(-1) + 0.1*gdp(-1)
>enddo
>do sectors market = 1
>  {sectors}_tax = 0.2*{sectors}_y
>enddo
>gdp = sum(sectors, {sectors}_y)
>tax = sum(sectors market = 1, {sectors}_tax)
```

The `>` marks model lines in a markdown model; in a string model
(`type_input='modelflow'`) write the same lines without it.

- `LIST name = sublist : items / sublist2 : values` – the first sublist names
  the elements; later sublists attach values used in conditions and substitutions
  (`{market}`).
- Ranges: `age0 * age4` gives `AGE0 … AGE3` – the end is **excluded**.
- `TLIST` is the transposed form (header row, then one row per element).
- `do list` … `enddo` repeats the block; `do list sub = value` only for matching
  elements. Loops nest.
- `sum(list, expr)` and `sum(list sub = value, expr)` expand to a parenthesised sum.

`Makemodel` expands all of this; inspect each stage with `.showpost_do`,
`.showpost_sum`, `.showexpanded_frml` (see `mf-build-model`).

## Several equations for one variable

The last one wins and a warning names them. Mark the unused ones `<DROP>`.

For equation options (`<STOC>`, `<EXO>`, `<DAMP>`, ...) see `mf-frml-options`; for
turning `log(c/p) = ...` into `C = ...` see `mf-normalize`.
