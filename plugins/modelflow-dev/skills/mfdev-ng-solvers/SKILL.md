---
name: mfdev-ng-solvers
description: >
  This skill should be used when adding, changing or debugging a solver in ModelFlow's
  modelsolver_ng.py: "new ng solver", "add a solver option", "change sim_ng /
  newton_fbmin_ng / newtonstack_ng", "register a solver", "SolverBase",
  "SolveContext", "iterate", "prepare", "build_evaluator", "NG_SOLVERS".
metadata:
  version: "0.1.0"
---

# The ng solver framework (`modelsolver_ng.py`)

Read the module docstring at the top of `modelsolver_ng.py` before changing a
solver; it is kept current and describes every ported solver.

## Template method

`SolverBase.__call__(databank, start, end, **opts)` is the fixed skeleton and is
never overridden:

1. `_setup_data` – sample, `is_newdata` (adds missing model columns, object dtype
   for matrix columns), fixed-period checks, `build_evaluator(ctx)`, then
   `ctx.values = databank.values.copy()` and `ctx.outvalues` when needed.
2. `prepare(ctx)` – solver-specific setup (Jacobian, index arrays). Default no-op.
3. `_setup_conv(ctx)` – `convplace`, `endoplace`, dump positions from `conv_order`.
4. `iterate(ctx)` – the algorithm; updates `ctx.values` in place.
5. `_finalize(ctx)` – result frame from `ctx.values`, dump frame, `m.ng_residual`,
   stats.

All shared state travels in the `SolveContext` dataclass, not on `self` or the model.

## Hooks a solver overrides

| Hook / attribute | Default | Override when |
| --- | --- | --- |
| `solvename` | `"sim"` | the solver needs another `makelos` flavour |
| `needs_outvalues` | `False` | the core writes residuals to `outvalues` (Newton) |
| `conv_order_attr` / `conv_order(ctx)` | `coreorder` | convergence is tested on other variables (fbmin: the feedback unknowns) |
| `dump_order(ctx)` | `conv_order` | dump order differs |
| `fixed_in_span_ok` | `False` | the solver solves all periods at once (stacked) |
| `DEFAULT_SILENT` | `1` | |
| `build_evaluator(ctx)` | `makelos(solvename)` → `ctx.pro, ctx.solve, ctx.epi` | other functions are needed (fbmin unpacks four) |
| `_place(ctx, var)` | databank column | values are not in databank layout (`sim1d`) |
| `prepare`, `iterate`, `stats_lines` | | always `iterate`; the others as needed |

Read options with `self._opt(ctx, name, default)`. Use `SolverBase._relconv` for
convergence so every solver stops on the same criterion. Record residuals with
`_record_residual` only when `keep_residual` is set.

## Generated functions

Every generated function has the signature `f(values, outvalues, row, alfa)`.
Gauss flavours write in place (`ctx.pro(values, values, row, 1.0)`); res flavours
write the LHS to `outvalues`. Per period the Gauss-Seidel solver does
`pro` once → `solve` × iterations → `epi` once. `newton_fbmin` does `pro`, then per
outer iteration one `dag` sweep plus `fb` evaluation(s), a final `dag` sweep, then
`epi`. Code generation is described in `mfdev-codegen`.

## Adding a solver – checklist

1. Write a design note first (`mfdev-design-notes`) unless the change is trivial.
2. Subclass the closest solver, not `SolverBase`, when the loop is the same; add a
   no-op hook in the parent's `iterate` rather than copying `iterate`.
3. New generated code: add a `makelos` flavour with its own cache attribute and
   transpile name (`f"{m.name}_<flavour>_jit"`) so it never collides with existing
   files.
4. Register it:
   - `Solver_ng_Mixin.NG_SOLVERS["<name>"] = <Class>`
   - a `<name>_ng(self, databank=None, *args, **kwargs)` method that defaults
     `databank` to `self.basedf`, like the existing ones.
5. Do not change `Solver_Mixin.__call__`'s default solver choice.
6. Update the module docstring's "Ported solvers" list.
7. Check with `mfdev-regress` against the solver it derives from.

## Things that bite

- `m.coreorder` is a property: accessing it runs `superblock()` and builds
  `m.fblist` / `m.daglist`. fbmin's `build_evaluator` touches it on purpose.
- `use_preorder=False` puts everything in `core` with empty prolog/epilog.
- Per-period solvers raise for an endogenous `X(2025)` inside the span; only the
  stacked solvers (`fixed_in_span_ok = True`) and `res` accept it.
- Leads: per-period solvers read them as fixed within a period (Fair-Taylor loops
  via `fair_max_iterations`); stacked solvers solve them exactly.
- Matrix (object dtype) columns break dense linear algebra; filter them out of
  Newton unknowns and convergence tests.
- `NewtonStackImplicitSolver` is an alias of `NewtonStackSolver`.
