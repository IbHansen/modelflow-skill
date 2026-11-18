# The linear solver of a Newton step (`factorizer=`, `permc_spec=`)

Every Newton iteration solves `J dx = -F` with the sparse Jacobian J. For a per-period
model J is small and the default (SuperLU) is always right. For a **stacked** solve
(`newtonstack_ng`, forward-looking models) J has variables x periods rows, and the
choice of linear solver decides whether the model can be solved at all, how much memory
it takes and most of the time.

The options apply to `newton_ng` and `newtonstack_ng`. They are sticky like all solve
options; when they change, the cached factorization is dropped.

## The choices

| `factorizer=` | Method | Needs | Fits |
| --- | --- | --- | --- |
| `None` / `'superlu'` | SuperLU (scipy), ordering from `permc_spec` | - | the default; banded stacked systems up to some 10^5 unknowns (FRB/US) |
| `'umfpack'` | UMFPACK (cvxopt), one symbolic analysis reused | cvxopt | per-period Newton with many periods of the same pattern |
| `'pardiso'` | MKL PARDISO LU, multi-threaded, **static pivoting** + refinement against J | pypardiso | large, well-conditioned systems with a strong diagonal |
| `'normal'` | normal equations J'J x = J'b, PARDISO Cholesky, scaled, refined against J | pypardiso | very large stacked systems where LU fill explodes (MAKRO, 1.5 mill. unknowns) |
| `'mumps'` | MUMPS LU, real pivoting, METIS ordering; in-process or helper process | python-mumps or `MODELFLOW_MUMPS_PYTHON` | large systems that need pivoting; slower than PARDISO |
| a function | `f(J)` returns `solve(b) -> x` | - | experiments |
| `modelfactorize.pardiso(...)`, `modelfactorize.normal(...)` | as `'pardiso'`/`'normal'`, with options (below) | pypardiso | tuning large solves |

`permc_spec=` is the SuperLU column ordering. The stacked solver defaults to
`'NATURAL'`, which keeps the period band (FRB/US: 1.8 s against 9.4 s with `'COLAMD'`);
the per-period solver keeps scipy's `'COLAMD'`. A stacked span cut short of the model's
terminal period can need `'COLAMD'` (MAKRO, 10-20 years). Never `'MMD_AT_PLUS_A'` on a
stacked Jacobian: it hangs.

## Options of `modelfactorize.pardiso` / `modelfactorize.normal`

```python
import modelfactorize
FACT = modelfactorize.normal(iparm={1: 13}, krylov=False, refine_tol=1e-9)   # make it once
res = mmodel(df, first, last, solver='newtonstack_ng', factorizer=FACT)
```

| Option | Effect |
| --- | --- |
| `iparm={i: v}` | PARDISO settings, 0-based as in the MKL C documentation; unset entries keep MKL's defaults. `{1: 13}` = parallel nested dissection with oneMKL 2026's aggressive factorization at level 1 (tens digit 1-9). Needs MKL >= 2026 (book314 has 2026.2) |
| `krylov=True` | GMRES preconditioned (from the right) by the factorization instead of repeated correction. Fewer solves with the factors when the factorization is far from exact |
| `refine_tol=1e-9` | accuracy the linear solve aims for (relative max-norm residual, default 1e-11). Newton converges as well with 1e-9 and needs fewer solves with the factors |

Make the factorizer **once** (a module constant) and pass the same object every call:
ModelFlow keeps the stacked factorization between calls only while `factorizer` is the
same object - a new `modelfactorize.normal(...)` in every call refactorizes every time.
`modeldump` cannot store a function and leaves the option out (with a printed note).

Every refined solve stops at its target or when the residual stops falling (its rounding
floor), raises when the residual stays above 1e-2 ("can not solve this linear system: use
another factorizer") and prints a warning above 1e-8.

## Measured (2026-11-17, book314, AMD Ryzen AI 9 HX 370, 64 GB)

FRB/US MCE, 404 quarters, stacked core 95 748 unknowns, `split=1`, `ljit=True`:

| factorizer | new Jacobian | later shocks |
| --- | --- | --- |
| SuperLU NATURAL (default) | 1.8 s | 0.20 s |
| SuperLU COLAMD | 9.4 s | 0.25-0.30 s |
| UMFPACK | 2.5 s | 0.41-0.47 s |
| MUMPS (helper process) | 4.4 s | 0.36-0.45 s |
| PARDISO, normal, with or without iparm/krylov | fail: condition number ~1e18, static pivoting and J'J too inaccurate | |

MAKRO 2026 (DREAM), 100 years, 1.5 mill. unknowns, one DREAM shock: SuperLU fails beyond
~20-30 years (fill), PARDISO LU fails (26 300 zero diagonals), `'normal'` 3.3 min,
`normal(iparm={1: 13})` 2.9 min, `+ refine_tol=1e-9` 2.65 min, all the same solution;
factorization 54 -> 37 s, 16 GB of factors, peak ~25 GB. `'mumps'` also solves it (~10 min).

## How to choose

1. Start with the default. If the stacked solve is fast enough, stop.
2. Out of memory or very slow factorization (fill) on a large stacked system → `'normal'`
   (then `modelfactorize.normal(iparm={1: 13}, refine_tol=1e-9)` on MKL 2026).
3. `'normal'`/`'pardiso'` raise "can not solve this linear system" → the Jacobian is too
   badly conditioned for them: `'mumps'` (pivoting), or SuperLU with a shorter span.
4. Many shocks on the same model: keep the Jacobian (`newton_reset=0`, the default after
   the first solve) - the factorization is then made once and each shock costs only
   back-substitutions. `ljit=True` speeds the model evaluations, not the linear algebra.
5. Compare the solution with the default solver's on one scenario before trusting a new
   factorizer: they agree to about `relconv`.
