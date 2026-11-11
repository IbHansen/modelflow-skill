---
name: mf-naming
description: >
  This skill should be used for variable naming conventions of the models brought
  into or built in ModelFlow: "naming convention", "what does fCp mean", "ADAM
  nomenclature", "MAKRO prefixes", "pC[c,t]", "FRB/US names", "MFMod mnemonic",
  "what is the ModelFlow name of this GAMS variable", "translate variable names",
  "map ADAM to MFMod", "name a new variable", or "which suffixes are reserved".
metadata:
  version: "0.1.0"
---

# Naming conventions

Four families, each with its own rules. Never carry one family's rules over to
another: `J` is an additive adjustment in ADAM, `j` a residual in MAKRO, and
nothing in MFMod.

| Family | Source | Reference |
| --- | --- | --- |
| MFMod (World Bank) | EViews → `GrabWfModel` | `mf-variable-names` (modelflow-user), summary below |
| FRB/US (Federal Reserve) | EViews / pyfrbus | `references/frbus.md` |
| ADAM (Statistics Denmark) | Gekko `.frm` → `Makemodel(type_input='gekko')` | `references/adam.md` |
| MAKRO (DREAM) | GAMS → `doable` + GDX | `references/makro.md` |

## Pattern versus fact

A decoded name is a guess about the meaning until the model or the source's own
variable list confirms it. Report the level reached: *pattern* (fits the
grammar), *in the model* (`name in m.allvar` or in the source's variable list),
*defined* (description, label or equation). Precedence: the model you have and
its descriptions > the release's variable list and equations > documentation >
examples > reading the pattern.

## What happens to names on import

| Source | In ModelFlow |
| --- | --- |
| any | upper case; only letters, digits, `_` |
| ADAM `fCp`, `pcp` | `FCP`, `PCP` – the case distinction of the nomenclature is gone, read the class from its position |
| ADAM FRML code `J` / `JR` / `D` / `Z` | `_A` add factor (JR becomes additive) / `_A` / `_D` fix dummy / `_X` fixed value |
| MAKRO / GAMS `pC[c,t]` | `PC__{C}` in a `doable`, `PC__CTOT` after expansion; `t` becomes the row index |
| FRB/US `xgdp`, add factor | `XGDP`, `XGDP_AERR`; expectations `Z...` with frml option `<Z>` |
| MFMod EViews | names kept; ModelFlow adds `_A`, `_X`, `_D`, `_FITTED` |

GAMS and Gekko are case-insensitive, so upper-casing loses nothing the source
model itself used – but descriptions copied from documentation may rely on case.

## Naming new variables

1. Follow the host model's convention: in an MFMod model build a 14-character
   name like its neighbours (`mf-variable-names`), in an ADAM-based model use
   the nomenclature, in a GAMS translation keep `NAME__INDEX`.
2. Check it is free: `name in m.allvar` and `m['PATTERN*'].names`.
3. Do not end a name in `_A`, `_X`, `_D`, `_FITTED`, `___RES`, `_AERR` or
   `_VALUE_<year>`; ModelFlow generates those. Use `__` only as the index
   separator of `doable` / lists.
4. Not a function name (`LOG`, `EXP`, `DIFF` ...), and not `C` in an estimated
   equation (clash with `c(n)`).
5. Give it a description (`var_description` / the markdown model text).

## Translating between models

Translate the economic concept, not the letters: coverage, real or nominal,
price base, units, currency, sector, frequency and transformation. ADAM `fCp`
(private consumption, chained volume) and MFMod `DNKNECONPRVTKN` describe the
same idea but need a check of the base year and definition. Say when there is
no exact counterpart.

## MFMod in short

`CCC AA MMM NNNN U C`: ISO-3 country, account (`NY` income, `NE` expenditure,
`NV` value added, `GG` government, `BX`/`BM`/`BN`/`BF` balance of payments, more
in practice), subject, detail, `K` real / `C` current / `X` price or rate,
`N` LCU / `D` US$ / `P` PPP. Only part of a model's names follow it – see the
user skill for the counts in PAK and the exceptions.

## References

- `references/adam.md`, `references/makro.md`, `references/frbus.md`
- `references/sources.md`: primary sources
