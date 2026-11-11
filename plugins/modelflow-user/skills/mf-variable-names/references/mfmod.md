# MFMod names

## The 14-character core

```
PAK NY GDP MKTP K N
CCC AA MMM NNNN U C
```

| Part | Positions | Meaning |
| --- | --- | --- |
| `CCC` | 1–3 | ISO 3166-1 alpha-3 country code (`PAK`, `BOL`, `HRV`, `IRQ`, `NPL`, `TUR`) |
| `AA` | 4–5 | account / area (table below) |
| `MMM` | 6–8 | subject (`GDP`, `CON`, `IMP`, `REV` ...), meaning depends on the account |
| `NNNN` | 9–12 | detail (`MKTP` market prices, `PRVT` private, `GNFS` goods and non-factor services ...) |
| `U` | 13 | `K` real (constant prices), `C` current prices, `X` price, deflator or rate |
| `C` | 14 | `N` national currency, `D` US dollars, `P` PPP |

Examples (descriptions from `pak.pcim`):

| Name | Parts | Description in the model |
| --- | --- | --- |
| `PAKNYGDPMKTPKN` | PAK NY GDP MKTP K N | Real GDP |
| `PAKNYGDPMKTPXN` | PAK NY GDP MKTP X N | GDP, Marker Prices, LCU Price defl., 2000 = 1 |
| `PAKNECONPRVTXN` | PAK NE CON PRVT X N | Implicit LCU defl., Pvt. Cons., 2000 = 1 |
| `PAKNYGDPMKTPKD` | PAK NY GDP MKTP K D | GDP, Market Prices, 2000 US$ mn |
| `PAKBNCABFUNDCD` | PAK BN CAB FUND C D | Current Account Balance, US$ mn |
| `PAKFMLBLPOLYXN` | PAK FM LBL POLY X N | Key Policy Interest Rate (`X` here is a rate) |

## Account codes seen in `pak.pcim`

| Code | Area | Code | Area |
| --- | --- | --- | --- |
| `NY` | national income | `BX` | balance of payments, exports |
| `NE` | national expenditure | `BM` | balance of payments, imports |
| `NV` | value added (production) | `BN` | balance of payments, net |
| `GG` | general government | `BF` | balance of payments, financial account |
| `FM` | monetary / financial | `LM` | labour market |
| `SM`, `CE`, `MP`, `EX` | few names, mostly without descriptions | | |

Read the area of the less common codes from the descriptions; the list is not
closed and differs between country models.

## Unit endings seen in `pak.pcim`

`CN` 92, `KN` 63, `XN` 39, `CD` 23, then `SH` (share), `QN` (physical quantity,
e.g. ktoe), `GN`, `ER` (e.g. carbon tax per tonne), `KD`, `OD`, `PT`. Only the
first five follow the `U`+`C` reading; for the rest read the description.

## Names outside the grammar

In `pak.pcim` only 257 of the 686 `PAK...` names are plain 14-character
mnemonics. The rest:

- **Trailing `_`**: often a ratio in percent, e.g. `PAKBNCABFUNDCD_` = current
  account balance, % of GDP. Not guaranteed – check the description.
- **ModelFlow companions**: `_A`, `_X`, `_D`, `_FITTED` (one set per behavioural
  equation), `_VALUE_2010` (fixed-period value). See the table in `SKILL.md`.
- **Longer or shorter names**: climate and energy blocks (`PAKCCEMISCO2CKN`,
  `PAKBETAENGYOTHRT`, `PAKNVGASPRODCN2`) do not follow the 14-character layout.
- **Other countries and the world**: trading-partner series (`CHNNECONPRVTXN`,
  `DEUEXR05`), world commodity prices (`WLDFCRUDE_PETRO`), conversion constants
  (`CONVBBLTOE`), period dummies (`DURING_2008`).

Do not force these into the parser; it reports them as "not a plain mnemonic".

## Not the WDI code

MFMod mnemonics resemble the World Development Indicators codes
(`NY.GDP.MKTP.KN`) but are a separate convention: no dots, a country prefix and
model-specific series. A WDI code is a hint for the concept, not proof that the
model has that series.
