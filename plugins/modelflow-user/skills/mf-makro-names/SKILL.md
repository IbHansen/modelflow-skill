---
name: mf-makro-names
description: >
  This skill should be used to read, check or find variable names of DREAM's MAKRO
  model (the Danish GAMS model) and its ModelFlow translation: "what does jvHhxAfk
  mean", "decode PC__CTOT", "MAKRO naming convention", "MAKRO prefixes", "pC[cTot,t]",
  "qBNP", "vtMoms", "what is the j in MAKRO", "J-led", "_a and _t", "what is the
  ModelFlow name of qI_s[iM,spTot,t]", "find the MAKRO variable for unemployment",
  "translate the Danish description", "what is CTOT / SPTOT / XVAR", "___RES in
  MAKRO", or "which ADAM series is behind this MAKRO variable".
metadata:
  version: "0.1.0"
---

# MAKRO variable names

MAKRO is DREAM's model of the Danish economy, written in GAMS. Its names follow
DREAM's own system – a short lower-case prefix, then CamelCase Danish words, then
GAMS indices – and the ModelFlow translation turns them into upper-case names
with `__` before each index element. This skill reads both forms.

A decoded name tells you what a name *probably* means. Always say which level
you reached:

| Level | Means | Evidence |
| --- | --- | --- |
| pattern | the name fits the prefix + words grammar | reading the parts |
| release list | the MAKRO name exists in the 2026-September release | `scripts/makro_names.csv` |
| in the model | the ModelFlow name exists in the loaded model | `name in mmakro.allvar` |
| defined | the meaning is confirmed | DREAM's text in the description, or the equation |

DREAM's texts are Danish. Translate them, and keep the Danish next to your
translation when the wording matters.

## Procedure

1. **Which form?** `pC`, `pC[cTot,t]` is GAMS; `PC__CTOT` is ModelFlow (upper
   case, `__` before each element, `t` is the row). Convert with
   `references/in-modelflow.md`.
2. **Decode** with the script (no model needed):

   ```
   python scripts/makro_name.py PC__CTOT "qI_s[iM,spTot,t]" JVHHXAFK
   ```

   It gives the MAKRO name (the CamelCase comes back from the release list),
   prefix, words, suffix, index elements, DREAM's Danish text and, where DREAM
   gives it, the ADAM series behind the data.
3. **Confirm** in the model you have:

   ```python
   mmakro['PC__CTOT'].des            # '... [CTOT] (MAKRO pC)'
   'PC__CTOT' in mmakro.allvar
   ```

   or `python scripts/makro_name.py NAME --model file.pcimz` (loads with
   `straight=True`, a few seconds). With the MCP server: `explain_variable`.
4. **Find a name for a concept**: search descriptions in Danish, the release
   list, or the English glossary:

   ```
   python scripts/makro_name.py --find unemployed       # English, via the glossary
   python scripts/makro_name.py --find forbrug          # Danish text
   ```
   ```python
   mmakro['!*ledig*'].names           # by Danish description
   mmakro['QC__*'].names              # all consumption quantities
   mmakro['#Headline'].names          # display groups, if the file has them
   ```

5. **Report** per name: the MAKRO and ModelFlow forms, the reading of each part,
   DREAM's text with a translation, and the level reached.

## The grammar in short

`<prefix><Words>[_suffix][index,...,t]`

- **Prefix** (lower case, details in `references/prefixes.md`): `p` price,
  `q` quantity, `v` value, `n` persons, `h` hours, `r` rate/ratio, `t` tax rate,
  `e` elasticity, `u` scale parameter, `f` factor, `j` additive residual,
  `jf` multiplicative residual, `s` structural, `m` marginal, `d` derivative,
  `E` expectation, `nv` present value. They stack: `vt` tax revenue, `jr`
  residual on a rate, `snL` structural employment.
- **Words**: CamelCase Danish (`Hh` households, `Off` government, `Udl` rest of
  the world, `BNP` GDP, `BVT` gross value added). A glued `x` means "excluding"
  (`BVTxudv`), a `2` "relative to" (`hL2nL` hours per employed person).
  `references/glossary.md` has the words.
- **Suffix**: `_a` age-dependent part, `_t` time-varying part, `_y`/`_m` from
  domestic production / imports, `_s` by using sector.
- **Indices**: GAMS sets; the last is always time. Totals: `TOT`, `CTOT`,
  `XTOT`, `ITOT`, `SPTOT`. Ages are numbers.

## Easy to get wrong

- `p`, `q`, `v` are growth- and inflation-adjusted, not national-accounts levels.
  Compare percentage deviations, or multiply by `fpt`/`fqt`/`fvt` first.
- MAKRO's `j` is a residual term (an ordinary exogenous variable in ModelFlow),
  not ModelFlow's `_A` add factor and not ADAM's `J`.
- Upper case hides where the prefix ends: `VTMOMS` is `vtMoms` (VAT revenue).
  Get the CamelCase from the description or the release list, never guess it.
- `mUC` is marginal *utility* of consumption; `UC` elsewhere is user cost.
- `rp` is not a growth rate: `rpC` is the chained aggregate over the plain sum
  of its parts.
- `X___RES`, `X_D`, `X_X`, `TEND`, `TVAL` come from the translation, not from
  DREAM.
- A stem alone (`JVUDLAKTRENTER`) is not a variable when MAKRO indexes it; the
  model has `JVUDLAKTRENTER__BANK` etc. The script says how many elements a
  name takes.

## Other naming families

MFMod and FRB/US names: `mf-variable-names`. ADAM names, and mapping MAKRO to
ADAM or MFMod: `mf-naming` in `modelflow-modeller`. Never carry one family's
rules over to another.

## References

- `references/prefixes.md`: the documented prefixes, the stacked ones with
  counts, undocumented ones (`rp`, `c`, `cr`), suffixes, pitfalls.
- `references/glossary.md`: Danish words and set elements in English.
- `references/in-modelflow.md`: GAMS → ModelFlow names, descriptions, totals,
  names the translation adds, searching.
- `references/sources.md`: sources and the release used.
- `scripts/makro_name.py`: decode, look up and search names.
- `scripts/makro_names.csv`: the 1 249 MAKRO names of the 2026-September
  release with ModelFlow stem, GAMS domain, instance counts, ADAM source and
  DREAM's text. `scripts/build_makro_names.py` rebuilds it from a newer
  translation.
