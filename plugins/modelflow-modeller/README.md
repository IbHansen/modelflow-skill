# modelflow-modeller

Claude Code skills for people who build and maintain economic models in ModelFlow:
writing equations, building models with `Makemodel` / `%%Makemymodel`, estimating
equations, preparing data, understanding model structure, choosing and tuning
solvers, importing models from EViews, Gekko, GAMS or Excel, and debugging.

## Install

```
/plugin marketplace add IbHansen/modelflow-skill
/plugin install modelflow-modeller@modelflow
```

## Skills

| Skill | Use |
| --- | --- |
| `mf-dsl` | The equation language: FRML, lags, leads, fixed periods, functions, LIST/DO/sum |
| `mf-frml-options` | `<STOC>`, `<EXO>`, `<ADD>`, `<FIT>`, `<DAMP>`, `<ENDO=>`, `<IMPLICIT>`, `<DROP>`; add factors and fixing |
| `mf-normalize` | Equations with an expression on the left; choosing the variable; implicit form |
| `mf-build-model` | `model()`, `Makemodel`, `%%Makemymodel`, markdown models, saving |
| `mf-ode` | Models from differential equations: `<ODE>`, Runge–Kutta via `modelode`, `NO{list}`, N-body |
| `mf-estimation` | `<est=ols>`, `<est=nls_lmfit>`, `<smpl=...>`, estimator factories |
| `mf-data` | The dataframe, missing variables, `upd`, `mfcalc`, add factors from history |
| `mf-structure` | Prolog/core/epilog, feedback set, graphs, convergence problems, stability |
| `mf-solvers` | Which solver, and tuning (`alfa`, `jacobian`, `nonlin`, `ljit` ...) |
| `mf-naming` | Naming conventions of ADAM, MAKRO, FRB/US and MFMod; names on import; naming new variables |
| `mf-import` | EViews workfiles and text, Gekko, GAMS, Dynare, Excel |
| `mf-debug-model` | Runtime errors, NaN, wrong results |
| `/mf-check-model` | Structure and data report on a model file (bundled script) |
| `/mf-explain-error` | Explain a pasted error or warning |
| `/mf-new-equation` | Draft an equation from a description and check it builds |

## Agent

`model-reviewer` – reviews a model specification for modelling mistakes.

## Requirements

ModelFlow installed (`conda install modelflow -c ibh -c defaults -c conda-forge`)
or a source checkout. `modelflow-user` covers running scenarios
and reporting.
