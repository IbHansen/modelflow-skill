---
name: mfdev-codegen
description: >
  This skill should be used when working on the Python/Numba source ModelFlow
  generates from model equations: "gen_2d", "parts", "make_gaussline2",
  "make_resline2", "makelos", "transpile", "jit", "modelsource", "stale jit file",
  "chunk", "errorfunk", "make_los_text", or any change to how equations become
  solver code in modelsolver_ng.py.
metadata:
  version: "0.1.0"
---

# Solver code generation

All ng solver source is generated in `modelsolver_ng.py` by `gen_2d`, `gen_1d`,
`gen_dag` and `gen_eqdict`. The legacy `Solver_Mixin.outsolve2dcunk` still exists for
the legacy solvers; do not route ng solvers through it.

## From equation to line (`gen_2d`)

- Each equation becomes one line built from `m.allvar[v]["terms"]` (tokens) and
  `m.allvar[v]["assigpos"]` (index of `=`).
- Variable references are `values[row<lag>, <col>]`, with `<col>` from
  `m.get_columnsnr(databank)`: `values[row,12]`, `values[row-1,12]`,
  `values[row+1,12]`. A fixed period `X(2002)` becomes a constant row
  (`values[37,12]`) via `fixed_rows` / `_cell`.
- `make_gaussline2(v, nodamp)` – in-place line. Equations whose FRML name has
  `DAMP` or `Z` get `(1-alfa)*(lhs)+alfa*(rhs)` unless `nodamp`; damping requires a
  single LHS.
- `make_resline2(v, nodamp)` – LHS written to `outvalues`, RHS read from `values`.
- `dropfrml` equations become `pass  # <var>`.

## Functions and `parts`

`gen_2d(m, databank, debug, chunk, ljit, type, parts)` returns the source of
`make_los(funks, errorfunk)`, which returns the generated functions.

- Default parts: `prolog` (`m.preorder`), `core` (`m.coreorder`), `epilog`
  (`m.epiorder`) when `m.use_preorder`; otherwise only `core` (`m.solveorder`).
- `parts=[(name, order, nodamp, kind), ...]` chooses the functions; `kind` is
  `"gauss"` or `"res"`. fbmin uses `prolog`, `dag`, `fb` (res), `epilog`.
- Every function: `def <name>(values, outvalues, row, alfa=1.0)`. With `ljit` each
  is decorated `@jit("(f8[:,:],f8[:,:],i8,f8)", fastmath=True, cache=False,
  nopython=True)`. Keep this signature; chunking, `errorfunk` and transpile
  caching depend on it.
- `chunk` (default 30) splits an order into sub-functions `<name>0`, `<name>1`,
  ... plus a master that calls them, keeping each function small for numba.
- `debug` (only without `ljit`) wraps each function in `try/except` calling
  `errorfunk(values, lineno, overhead=..., overeq=...)`, which maps a failing line
  back to its equation. Adding or removing lines before the functions shifts
  `overhead`; keep the bookkeeping in `makeafunk` consistent.
- `m.funks` (user functions) are passed in as `funks[i]`; `modeluserfunk` and
  `modelBLfunk` functions are imported by name in the generated source.

## Compile and cache (`SolverBase.makelos`)

| Path | When | Cached on the model as |
| --- | --- | --- |
| plain `exec` | `ljit=False` | `pro_/core_/epi_<model>_<flavour>_nojit` (fbmin: `ng_fbmin_<model>_nojit`) |
| `stringjit` | `ljit=True, stringjit=True` | same attribute scheme with `_jit`; source in `m.make_los_text_jit` |
| transpiled file | `ljit=True` | file `modelsource/<model>_<flavour>_jit_jitsolver.py`, imported |

- Regeneration happens when `newdata` (databank columns changed), `transpile_reset`,
  a changed fixed-period row layout (`_fixrow_changed`), or no cached attribute.
- `import_transpiled` always regenerates the text and compares it with the file:
  a different text rewrites the file and reloads the module, so numba recompiles;
  an identical text reuses the compiled cache. Anything that affects generated
  code must therefore appear in the text (column numbers do, so a layout change is
  caught).
- The model name is sanitised for file names (`re.sub(r"\W", "_", ...)`).
- Legacy `sim` and `sim_ng` share the same transpile file and attributes
  (`modeltest/jitfile_test.py` cell 7 checks this).

## Inspecting generated code

- Without jit, `m.make_los_text` holds the last generated source; print it.
- With a transpiled file, open `modelsource/<model>_<flavour>_jit_jitsolver.py`.
- To analyse it, `ast.parse` the source and walk the function bodies; variable
  access is always a `Subscript` on `values` / `outvalues` with a `(row±k, col)`
  index.

## Equivalence

- Without jit, generated code changes that keep the same float operations in the
  same order must give bit-identical results (`np.array_equal`).
- With jit, `fastmath=True` lets LLVM reassociate, so compare with a tolerance.
- See `mfdev-regress`.
