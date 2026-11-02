---
name: mf-load-model
description: >
  This skill should be used when opening an existing ModelFlow model: "load a model",
  "modelload", "pcim file", "World Bank models", "MFMod", "Worldbank_Models",
  "download the country models", "what is in this model", "find a variable",
  "variable names", "what does PAKNYGDPMKTPKN mean", "var_groups", "#Headline", or
  "search variables by description".
metadata:
  version: "0.1.0"
---

# Loading a model

## Load

```python
from modelclass import model
mpak, baseline = model.modelload('pak.pcim', run=1, keep='Baseline')
```

- A `.pcim` holds the equations, variable descriptions, groups, saved solve
  options and the baseline data.
- `run=1` solves the baseline once (sets `mpak.basedf` and `mpak.lastdf`);
  `keep='Baseline'` stores that solution for comparisons (`mf-results`).
- `run=0` only loads; the returned frame is the saved data. Without `run` the
  model solves only if it was saved to run on load.
- A URL works as the file; a name not found locally is looked up in the
  ModelFlow manual's model repository on GitHub.

## The World Bank MFMod models

```python
model.Worldbank_Models()      # downloads github.com/worldbank/MFMod-ModelFlow to ./WorldbankModels
```

It lists the notebooks it downloaded. Country models are `.pcim` files under
`WorldbankModels/models/<Country>/`.

## Variable names (MFMod)

Names follow the World Bank mnemonic: country ISO code, then the indicator, then
the unit. `PAKNYGDPMKTPKN` = Pakistan, GDP at market prices, real (constant local
currency). Common unit endings: `KN` real, `CN` nominal local currency, `XN`
deflator, `CD` current US$. Companion variables of behavioural equations:
`_A` add factor, `_X` fixed value, `_D` fix dummy, `_FITTED` fitted value.

## Finding variables

| Write | Selects |
| --- | --- |
| `mpak['PAKNYGDP*']` | wildcard on names (`*` and `?`), several patterns separated by blanks |
| `mpak['!*real GDP*']` | search in the descriptions |
| `mpak['#Headline']` | a variable group (`list(mpak.var_groups)` shows them) |
| `mpak['PAK* -*_X -*_D']` | a leading `-` removes matches |
| `mpak['#ENDO']` | all endogenous variables |

```python
mpak['PAKNECONPRVTKN'].des        # description
mpak['PAKNECONPRVTKN'].frml       # the equation
mpak.var_description['PAKNYGDPMKTPKN']
mpak.PAKNECONPRVTKN.tracepre(up=1)   # what it depends on (needs graphviz)
```

`/mf-explain <variable>` explains a variable from the model itself.

## Deeper reference

`references/worldbank-onboarding.md`: the available country models, the full
MFMod naming scheme and companion variables, what a `.pcim` holds, and the
climate-aware variants. Read it when working with a World Bank model.
