---
name: mf-explain
description: >
  This skill should be used to explain a variable in a ModelFlow model:
  "/mf-explain", "what is PAKNYGDPMKTPKN", "what does this variable mean", "how is
  X determined", "what drives X", "show the equation for X", or "is X exogenous".
argument-hint: "<variable name or description> [model file]"
metadata:
  version: "0.1.0"
---

# /mf-explain

Explain one variable from the model itself – never from memory of what the
mnemonic usually means.

## Gather

With the model loaded (or load it: `mpak, base = model.modelload(file, run=0)`):

```python
v = 'PAKNECONPRVTKN'                    # or find it: mpak.vlist('!*consumption*')
mpak.var_description.get(v)             # description
v in mpak.endogene                      # endogenous or exogenous
mpak.allvar[v]['frml']                  # the equation (endogenous)
mpak.allvar[v]['frmlname']              # options: STOC = behavioural, can be fixed
[w for w in mpak.endogene                                        # equations that use it
 if v in {t.var for t in mpak.allvar[w]['terms'] if t.var} and w != v]
mpak[v].df.loc[2024:2026]               # values, if solved
```

Run these with Python when ModelFlow is available; otherwise ask the user to run
them or share the model file.

## Explain

1. **What it is**: description, unit from the mnemonic ending (`KN` real, `CN`
   nominal, `XN` deflator or rate, `CD` US$), exogenous or endogenous.
2. **How it is determined**: the equation in words – the main drivers and their
   lags, the form (log-linear, error correction, identity). Name the add factor
   `_A` and the fix variables `_X` / `_D` if present.
3. **Where it goes**: the equations that use it.
4. **How to move it in a scenario**: exogenous → `upd`; endogenous with `_X` →
   `fix` and change `_X`; otherwise through its drivers or add factor.

Keep it short. For a chart of the chain, suggest `mpak.PAKNECONPRVTKN.tracepre(up=2)`
(needs graphviz).
