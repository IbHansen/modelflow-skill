---
name: mf-variable-names
description: >
  This skill should be used to read, check or find variable names (mnemonics) in a
  ModelFlow model: "what does this mnemonic mean", "decode PAKNECONPRVTXN", "naming
  convention", "is this a valid variable name", "what is the name for real GDP in the
  Bolivia model", "KN CN XN CD", "what is the _ at the end", "_VALUE_2010",
  "FRB/US variable names", "XGDP", "_AERR", or "ZGAP05".
metadata:
  version: "0.1.0"
---

# Variable names

A naming pattern tells you what a name *probably* means. Only the model itself
tells you what it *is*. Always say which of the two you are reporting:

| Level | Means | Evidence |
| --- | --- | --- |
| pattern | the name fits the family's grammar | parser / reading the parts |
| in the model | the name exists in the loaded model | `name in mpak.allvar` |
| defined | the meaning is confirmed | the model's description or equation |

Never present a decoded mnemonic as the definition, and never claim a suggested
name exists until it is found in the model.

## Procedure

1. **Which model family?** The loaded model decides, not the look of the name.
   MFMod (World Bank country models): `references/mfmod.md`.
   FRB/US (Federal Reserve): `references/frbus.md`. ADAM, MAKRO and naming in
   imported models are covered by `mf-naming` in `modelflow-modeller`.
2. **Explain**: split the name into its parts, then confirm in the model:

   ```python
   mpak['PAKNECONPRVTXN'].des          # description
   mpak.var_description.get(v)         # same, None if there is none
   'PAKNECONPRVTXN' in mpak.allvar     # is it in the model at all
   ```

   With the MCP server: `explain_variable` / `find_variables`. `/mf-explain`
   goes on to the equation and drivers.
3. **Find a name for a concept**: search descriptions first, then patterns:

   ```python
   mpak['!*private cons*'].des         # by description
   mpak['PAKNECON*KN'].names           # by pattern: all real expenditure on consumption
   ```

   A name built from parts is a *candidate* until found this way.
4. **Check a name**: `scripts/parse_mnemonic.py` splits MFMod names and, with
   `--model`, looks them up in a `.pcim`:

   ```
   python scripts/parse_mnemonic.py PAKNYGDPMKTPKN PAKBNCABFUNDCD_ --model pak.pcim
   ```

5. **Report** per name: parts, meaning, level reached (pattern / in the model /
   defined), and the description that confirms it.

## Names ModelFlow adds

Not part of any family's convention. Read the base name first, then the suffix.

| Suffix | Meaning |
| --- | --- |
| `_A` | add factor of a behavioural equation |
| `_X` | value used when the equation is fixed (exogenized) |
| `_D` | fix dummy: 1 = use `_X`, 0 = use the equation |
| `_FITTED` | fitted value of the estimated equation |
| `_VALUE_2010` | the variable's value in a fixed period (here 2010) |
| `___RES` | residual of an implicit (unnormalized) equation |
| `_AERR` | FRB/US add factor (FRB/US's own naming, kept on import) |

## Translating between models

Map the economic concept (coverage, real/nominal, units, currency, frequency,
transformation), never the spelling. Say when there is no exact counterpart.

## References

- `references/mfmod.md`: the 14-character grammar, the codes seen in the PAK
  model, names outside the grammar.
- `references/frbus.md`: FRB/US names in ModelFlow, `Z` expectations, `_AERR`.
- `references/sources.md`: primary sources.
- `scripts/iso3166_alpha3.csv`: ISO country codes (a valid code does not mean a
  model exists for that country).
