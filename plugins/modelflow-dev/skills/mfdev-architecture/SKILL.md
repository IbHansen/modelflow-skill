---
name: mfdev-architecture
description: >
  This skill should be used when changing or reading ModelFlow framework code in the
  modelflow2 repo: "where is X implemented", "which mixin", "how does modelclass
  dispatch the solver", "legacy vs ng solver", or before touching modelclass.py,
  modelsolver_ng.py, modelnewton.py or any sibling module. It maps the jobs to the
  modules and mixins that own them.
metadata:
  version: "0.1.0"
---

# ModelFlow architecture map

Read `modelflow/CLAUDE.md` first: it holds the module table, the BLL basics and the
data flow from FRML text to result frame. This skill adds where things live inside
`modelclass.py` and how solving is wired.

## The `model` class

`modelclass.model` is an empty class assembled from mixins (end of `modelclass.py`):

```
model(Parquet_Mixin, Zip_Mixin, Json_Mixin, Model_help_Mixin, Solver_Mixin,
      Solver_ng_Mixin, Display_Mixin, Graph_Draw_Mixin, Graph_Mixin, Dekomp_Mixin,
      Org_model_Mixin, BaseModel, Description_Mixin, Excel_Mixin, Dash_Mixin,
      Modify_Mixin, Fix_Mixin, Stability_Mixin, Report_Mixin, Causality_Mixin)
```

| Job | Owner |
| --- | --- |
| Parse equations, `allvar`, endogene/exogene, `smpl`, `get_columnsnr`, options (`ng`, `use_preorder`, `use_fbmin`, `normalized`) | `BaseModel` (`__init__`, `analyzemodelnew`) |
| Dependency graph, `superblock()`, `preorder` / `coreorder` / `epiorder`, `fblist` / `daglist` | `Graph_Mixin` |
| Drawing graphs (graphviz) | `Graph_Draw_Mixin` |
| `__call__` (solver choice, options carried between calls, `keep`, `basedf` / `lastdf`) | `Solver_Mixin` |
| Legacy solvers (`sim`, `xgenr`, `newton*`, `newtonstack*`), legacy `makelos` / `outsolve2dcunk`, `is_newdata` | `Solver_Mixin` |
| ng solvers (`*_ng`, `solve_ng`, `NG_SOLVERS`) | `Solver_ng_Mixin` in `modelsolver_ng.py` |
| Newton Jacobians | `newton_diff` in `modelnewton.py`; symbolic parts in `modeldiff.py` |
| Attribution | `Dekomp_Mixin` + `modeldekom.py` |
| Fixing / exogenising | `Fix_Mixin` (`fix`); add-factor model via `Solver_Mixin.calc_add_factor`, called from `__call__` |
| Changing a model (`equpdate`, `eqdelete`, `eqflip`) | `Modify_Mixin` |
| Save / load `.pcim` (`modelload` in `Json_Mixin`, `modeldump` in `Zip_Mixin`), Parquet/Feather | `Json_Mixin`, `Zip_Mixin`, `Parquet_Mixin` (`model_parquet_mixin.py`) |
| `[]` variable queries, `vlist` | `Org_model_Mixin` |
| Display, `keep_plot`, plots | `Display_Mixin`, `modelvis.py` |
| Reports, dashboards | `Report_Mixin`, `Dash_Mixin`, `modelreport.py`, `modeldash*.py` |

Find a method's owner with `grep -n "^class \|    def <name>" modelclass.py`; the
class whose line range contains the method owns it.

Outside the class: `modelode.py`, the ODE → Runge–Kutta preprocessor, is a
standalone overlay that nothing in the core imports (`mfdev-ode`).

## Solver dispatch (`Solver_Mixin.__call__`)

1. Pick `solverguess` from the model's shape: leads (`maxlead >= 1`) give a stacked
   solver; otherwise `xgenr` if `istopo`, `sim` if simultaneous; hybrid and
   un-normalized models get Newton variants.
2. With `self.ng` or `self.fixed_periods`, map the guess to its ng name
   (`sim` → `sim_ng`, `xgenr` → `xgenr_ng`, ...). A normalized simultaneous model
   gets `sim_ng`; Newton must be asked for.
3. `solver=` overrides the guess; any `<name>_ng` attribute is callable.

The default solver is decided only here. Do not change it as a side effect of
other work.

## Legacy and ng solvers

- `Solver_Mixin` holds the legacy solvers. Leave them unchanged unless the task is
  about them.
- `modelsolver_ng.py` is the parallel ng framework: one template-method
  `SolverBase`, one `SolveContext`, concrete solvers, registry in
  `Solver_ng_Mixin.NG_SOLVERS`. See the `mfdev-ng-solvers` skill.
- Both share `import_transpiled` (from `modelsolver_ng`) for jit files: legacy
  `sim` and `sim_ng` write the same transpile file. See `mfdev-codegen`.

## Tests and data

- No pytest suite. Checks are `#%%` cell scripts in `modelflow/modeltest/`
  (`ng_dispatch_test.py`, `speedtest.py`, `jitfile_test.py`, `fixedperiod/`, `odetest/`).
- Test models: `modeltest/data/pak.pcim` (MFMod Pakistan) and
  `modeltest/data/frbusmcetest.pcim` (FRB/US with model-consistent expectations).
- See `mfdev-regress` for comparing a solver change.

## Notebook display code

Before changing code that injects JavaScript or CSS (`widescreen`, `scroll_off`,
`modelflow_auto`, widgets), read `references/jupyter-display.md`: classic
Notebook vs Notebook 7 / JupyterLab guards and selectors.
