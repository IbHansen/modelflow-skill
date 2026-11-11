---
name: mf-import
description: >
  This skill should be used when bringing a model from another system into ModelFlow:
  "convert an EViews model", "wf1", "wf2", "import from Gekko", "GAMS gdx",
  "Dynare", "Excel model", "translate equations", "CGE", "MCP", "modelgrabgdx", "GrabWfModel", "World Bank model
  from EViews", "type_input='eviews'", or "translate this equation to ModelFlow".
metadata:
  version: "0.1.0"
---

# Importing models

| Source | Tool | Gives |
| --- | --- | --- |
| EViews workfile `.wf1` / `.wf2` (World Bank MFMod) | `modelgrabwf2.GrabWfModel` | model + data + descriptions, add factors, fitted model; needs EViews on Windows for `.wf1` |
| EViews equation text | `Makemodel(text, type_input='eviews')` | equations only |
| World Bank text + Excel data (older) | `modelgrab.GrapWbModel` | model, add-factor model, fitted model |
| World Bank macro text | `modelmacrograb.GrabMacroModel` | model, no Excel needed |
| Gekko `.frm` text | `Makemodel(text, type_input='gekko')` | equations |
| Gekko databank `.gbk` | `modelgrabgekkobank.read_gbk(path)` | annual data only |
| GAMS `.gdx` | `modelgrabgdx.model_grab_gdx(files, gams_dir=...)` | data (scenarios bundled); needs `gamsapi[transfer]` and GAMS |
| Dynare `.mod` | `model_dynare.grap_modfile` | main, residual and parameter models |
| Excel workbook | `modelgrabexcel.getexcelmodel(name)` | cell formulas as equations; array formulas not supported |

## EViews workfiles

```python
from modelgrabwf2 import GrabWfModel
grab = GrabWfModel(filename='pak.wf1', modelname='pakmodel', freq='A',
                   make_fitted=True, start=2000, end=2022)
mmodel, df = grab()
grab.test_model()            # does the imported model reproduce the data?
```

Behavioural equations become `<DAMP,STOC>`, identities `<IDENT>`, quasi-identities
`<QUASIIDENT>`. `country_trans` and `country_df_trans` take functions that patch
the equation text and the dataframe before processing – the place for
country-specific fixes. `print_frml(pat)` shows translated equations.

## Equation text from EViews or Gekko

```python
import functools
from modelconstruct_estimation import Makemodel, eviews_to_modelflow

mm = Makemodel(eviews_text, type_input='eviews')    # every equation gets <>
mm = Makemodel(eviews_text, type_input='eviews',    # behavioural equations get <STOC>
               transform=functools.partial(eviews_to_modelflow, behavioral_opts='<STOC>'))
mm = Makemodel(gekko_text,  type_input='gekko')     # FRML codes: J -> add factor, D -> dummy
```

EViews text: one equation per line, `'` starts a comment, `@IDENTITY` marks
identities. Gekko text: `FRML <code> ... $`.

Translations done: EViews `D(` → `DIFF(`, `@PC` → `PCT_GROWTH`, `^` → `**`;
Gekko `x[-1]` → `x(-1)`, `dif(` → `DIFF(`, `pch(` → `PCT_GROWTH(`. Gekko codes map
to `<STOC>` (J and D), `<ADD>` (J), `<EXO>` (D). Override with
`transform=functools.partial(gekko_to_modelflow, code_map={...})`. Other formats:
pass `eq_start`, `eq_end`, `comment_start` and a `transform` function to
`Makemodel` – `mf-build-model` has a worked example.

## After importing

1. `/mf-check-model` on the result.
2. `test_model` on history: identities must reproduce the data exactly; a
   difference is a translation error.
3. Compare a scenario with the source system before relying on the model.

Common translation problems: an EViews function with no ModelFlow equivalent
(write it as a user function, `mf-dsl`), lags written without a sign, and
variable names that collide with function names. How names change on import
(upper case, GAMS indices → `NAME__ELEM`, Gekko J/D/Z → `_A`/`_D`/`_X`, FRB/US
`_AERR`) and the source models' naming conventions (ADAM, MAKRO, FRB/US, MFMod)
are in `mf-naming`. `replacements=[(old, new)]` on
`Makemodel` fixes text before parsing.

## GAMS models

For a GAMS model (CGE, MCP/PATH) read `references/gams-to-makemodel.md` first:
translate the instantiated model, GDX data with `modelgrabgdx`
(`GdxStaticDataset`, `static_to_frame`, `sets_to_lists`, `pair_list`), GAMS
`$`-conditions/SUM/ALIAS → `doable`/`sum`/lists, MCP pairings → `endo=`,
closures, and the verification checklist.
