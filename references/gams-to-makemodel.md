---
name: gams-to-makemodel
description: How to translate a GAMS model (CGE or other set-indexed model) and its GDX data into Makemodel input — GDX import via modelgrabgdx (GdxStaticDataset, sets_to_lists, pair_list, static_to_frame), naming conventions, mapping GAMS $-conditions/SUM/ALIAS/MCP pairings to doable/sum/lists/endo tags, closures, complementarities, and the literate-markdown file layout.
---

# GAMS → Makemodel translation guide

This file describes the method for porting a GAMS model to ModelFlow via the
Makemodel literate-markdown format. It was developed on the JRC DEMETRA CGE
(single-country, MCP/PATH) — the worked example lives in
`C:\mfmodeller_raw\demetra cge\jrc-demetra-master\`:

| File | Role |
|---|---|
| `demetra_to_modelflow.md` | Strategy document (model anatomy, closure, solver, verification plan) |
| `demetra_modelflow_template.md` | Full translation in Makemodel format — the pattern to copy |
| `demetra_modelflow_template.txt` | Same content in classic BLL (`frml … $`) format |

The Python side lives in `modelgrabgdx.py` (static-GDX section at the bottom of
the file; the time-indexed API above it is legacy and unchanged).

## Core strategy: translate the *instantiated* model

A GAMS model file is a **family** of models: subsets, mappings and nesting
structures are derived from the data at run time, and `$`-conditions switch
equations on and off per set element. Do **not** translate the generic GAMS
code symbolically. Instead:

1. Run GAMS once with `execute_unload 'alldata.gdx';` placed **after**
   calibration and variable initialisation (and before the solve). This dumps
   every set, parameter, and variable base level in *resolved* form — including
   derived sets and calibrated parameters that don't exist in the raw data.
2. Generate ModelFlow `LIST` statements and the input DataFrame from that GDX.
3. Hand-write the equation template **once**, mirroring the GAMS equation
   section block by block. The template is country/data-independent — only the
   lists and the DataFrame change per dataset. This preserves a GAMS model's
   "one code, many datasets" design.
4. All `$`-conditions become list membership; all `VAR.FX(...)$(NOT set) = 0`
   structural zeros disappear because those variable instances are never
   generated.

## The data pipeline (`modelgrabgdx.py`)

Requires GAMS installed and `pip install "gamsapi[transfer]"`.

```python
from modelgrabgdx import GdxStaticDataset

g = GdxStaticDataset('10_gdx/alldata.gdx', years=range(2021, 2051))

basedf = g.df                                   # wide constant frame over the years
lists  = g.lists(['c', 'a', 'h', 'w', 'f'],     # base sets -> LIST statements
                 aliases={'CP': 'c', 'HP': 'h'},
                 condition_symbols=['cm', 'ce', 'FD0', 'FSI0'])  # sets AND parameters
pairs  = g.pairs('FD0', keynames=['FF', 'A'])   # pair list for a sparse domain
```

What each piece does:

- **`static_to_frame`** (behind `g.df`) — every variable *level* and every
  parameter *value*, any domain including scalars, flattened to
  `NAME__ELEM1__ELEM2` and broadcast as a constant column over `years`. This is
  the static-model replacement for `free_to_timeseries_t` (which only selects
  free variables with a trailing `t` dimension and returns nothing on a static
  dump).
- **`sets_to_lists`** — one `LIST` per base set. 1-dim subsets whose elements
  belong to the base become **0/1 sublists** (the GAMS `$`-condition). 2-dim
  sets become **per-element 0/1 sublists on both base lists**, named
  `<SET>_<element-of-the-other-dim>` (e.g. GAMS `cmR(w,c)` gives `CMR_MAIZE` on
  the `W` list and `CMR_ROW` on the `C` list). **Parameters** listed in
  `condition_symbols` contribute their *nonzero pattern* (GDX only stores
  nonzero records, so membership == `par(i) <> 0`). **Aliases** are full copies
  of the base list with the key sublist renamed — conditions keep working on
  the alias (`sum(CP CCESN=1, ...)`).
- **`pair_list`** — for sparse multi-dim domains: one LIST whose *parallel
  sublists* hold the active tuples, for `do PAIRS` loops. Works on sets and on
  nonzero parameters alike.
- **`clean_name`** — the sanitisation rules (strip `()`, whitespace→`_`, any
  other non-alphanumeric→`_`, uppercase). Same rules as the legacy
  `clean_columns` — keep them in sync; GAMS elements like `i-s` become `I_S`.
  The list generator and the DataFrame builder MUST use the same rules so
  template names and columns agree by construction.
- GAMS explanatory texts flow into `var_description` via
  `bytype_description_to_dict_t` — carry them over, they're free documentation.

Lists come out in classic `LIST NAME = ... $` form. For Makemodel, prefix each
generated line with `>` before concatenating with the template text.

## Naming convention

GAMS `X(i,j)` → `X__{I}__{J}` after expansion, e.g. `QMR("row","maize")` →
`QMR__ROW__MAIZE`. Double underscore is mandatory: it is what the `doable`
index detector matches (`__\{IDX\}` on the LHS) and what the GDX importers use
as separator. Set-element names are sanitised with `clean_name`.

## Translating equations — construct by construct

| GAMS | Makemodel |
|---|---|
| `EQ(i).. lhs =E= rhs;` | `> doable LHS__{I} = rhs` |
| `EQ(i)$cond(i)..` | `> doable [I COND=1] LHS__{I} = ...` |
| `EQ(i,j)$cond2(i,j)..` | `[I, J COND2_{I}=1]` — the 2-dim condition is a per-element sublist; a condition may contain an outer loop index |
| `SUM(j, x(j))` | `sum(J, X__{J})` |
| `SUM(j$cond(j), x)` | `sum(J COND=1, X__{J})` |
| `SUM(j$cond2(i,j), x)` | `sum(J COND2_{I}=1, ...)` — substituted by the enclosing loop before sum-unroll |
| `ALIAS(i,ip)` | second list `IP`, full copy incl. condition sublists |
| parameter `p(i)` | exogenous variable `P__{I}`, constant column in the DataFrame |
| sparse domain `eq(i,j)$p(i,j)` over many dims | `> do PAIRLIST` … `> enddo` over a pair list |
| `x**y` | `x**y` (unchanged) |
| `VAR.FX(...)$(NOT set) = 0` | not translated — instances never generated |
| closure `VAR.FX = VAR0` | no equation → VAR exogenous; use `<exo>` tag when the closure *sometimes* frees it (swap becomes data via `_D`/`_X`) |
| MCP pairing `EQ.VAR` in the model statement | `<endo=VAR__...>` (with `<implicit>` if not normalisable) |
| `=G=` / `=L=` + bounds (complementarity) | min-form residual: `<implicit, endo=...> 0 = min(SLACK, VAR - BOUND)`; fallback: regime-as-data |
| `POSITIVE VARIABLE` | usually ignore — safeguards for PATH iterates, non-binding at interior solutions |
| `LOOP(t, update; solve)` recursive dynamics | ordinary lagged FRMLs `X = f(X(-1), ...)`; ModelFlow's period solve replaces the loop |
| `LOOP(sim, ...)` experiments | scenario DataFrames / `keep_solutions` |

### Normalisation and the `endo` choice

Three cases:

1. **Already normalised** (LHS is the natural endogenous) — plain `>` line.
2. **Value identities** `P*Q =E= Σ...` — rearrange in the template
   (`P = (Σ...)/Q`) or tag `<endo=P__...>`.
3. **Not analytically normalisable** (FOCs where the unknown sits inside a sum
   over its own index) — keep un-normalised with `<implicit, endo=VAR__...>`;
   the Newton solvers handle residual form.

Where GAMS gives an explicit MCP pairing (`EQ.VAR` in the `Model /.../`
statement), use it — it is the authoritative source. Where GAMS leaves an
equation unpaired (PATH matches globally), *choose* a perfect matching and
**flag it DOUBTFUL**; any perfect matching gives the same solution, but the
choice must survive the degenerate cases. Verify with a square check
(#equations == #endogenous per generated instance).

### Degenerate variants and inline `$`

GAMS often has an equation pair like `CES-form$` (both flows nonzero) and
`linear-alt$` (one flow structurally zero). Split into normalised variants over
**combined sublists** computed by the generator (`CDE` = cd∧ce, `CD_NOT_CE`,
…); the structurally-zero side is never generated, so the linear alternative
usually collapses to `X__{I} = Y__{I}`.

A `$` on a *term inside* an equation (`+ SUM(h,QCD(c,h))$ccesn(c)`) either
splits the equation into variants per condition, or becomes a 0/1 indicator
*series* multiplying the term. Prefer variants: they avoid referencing
never-generated variables (ModelFlow silently treats unknown names as
exogenous zeros — a trap).

Multi-dimensional mapping sets (3-dim and up, e.g. `map(c,f,a)`) that select
single elements: emit those equation instances **per element from the
generator** rather than fighting the template. Mark them DOUBTFUL until done.

### Helpers

Adding helper variables with no GAMS counterpart is fine and encouraged for
readability (e.g. a committed-expenditure aggregate reused by several LES
equations, or a total-export-value denominator). Mark them "helper" in the
prose.

## The literate Makemodel file layout

Follow `demetra_modelflow_template.md`:

- One markdown heading per GAMS equation block; a sentence or two of economics
  per block.
- **Every GAMS equation quoted in a fenced ` ```gams ` block immediately above
  the `>` equations that translate it.** This is the review contract: any
  reader can diff source and translation line by line.
- **Wrap each `>`/`>>` equation group in a plain code fence.** Without the
  fence, markdown renders `>` as blockquote and mangles `__` into bold. The
  Makemodel extractor (`extract_model_from_markdown` in `modelconstruct.py`)
  reads line-by-line and does **not** track fences, so fenced `>` lines still
  parse. Corollary: inside `gams`/`text` example blocks, never start a line
  with `>` unless it is meant to be model input.
- Skeletons that cannot be templated yet (generator-emitted instances) go in
  ` ```text ` blocks so the parser cannot pick them up.
- Every uncertainty gets a bold **DOUBTFUL** paragraph in place, and all of
  them are collected in a **DOUBTFUL registry** section at the end — the
  tick-off list for the square check. Standard DOUBTFUL categories: unpaired
  endo choices, suspected GAMS typos (translate literally, flag, check the
  model's documentation), closure-dependent endo choices, 3-dim maps pending
  generator emission, data-level switches, non-smooth formulations.
- Assembly: `Makemodel(lists_text_with_>_prefixes + md_text)`. Inspect
  `mm.showlists` and count equations in `mm.normal_frml` as the first sanity
  check that nothing silently dropped out.

## Closures, bounds, and Newton domain safety

- A GAMS closure file is a list of `.FX` statements = the choice of exogenous
  variables. In ModelFlow: fixed-always → just exogenous; sometimes-swapped →
  generate the defining equation with `<exo>` so the swap is data (`_D`=1,
  supply `_X`), not a separate model build.
- Numeraire fixing plus Walras' law leaves one redundant equation; absorb it
  explicitly (e.g. WALRAS exogenous ≡ 0 with the savings-investment equation
  solving for the investment scalar) and document the bookkeeping — this is
  the classic square-count trap.
- Real inequality content of a typical CGE is tiny (often a single
  wage-floor/unemployment complementarity); grep for `=G=`, `=L=`, `.LO`,
  `.UP`, `POSITIVE VARIABLE` and treat only what actually binds.
- The *practical* problem is domain of definition, not constraints: PATH
  projects iterates into bounds, unconstrained Newton doesn't, and CGEs are
  dense with fractional powers and divisions. Mitigations, in order: good
  starting values (solve year-by-year from the previous solution, phase big
  shocks), damping/step control on NaN, log-substitution for unknowns under
  fractional powers or in denominators, keep the model's own scaling
  (SAM-scaling parameters), absolute-residual convergence for implicit
  equations (relative-change tests are blind to small-valued unknowns).

## Verification checklist

1. **Base replication** — solving on the base DataFrame must leave every
   endogenous variable at its calibrated level (GAMS does the same with
   `iterlim = 0`); implicit residuals ~1e-8 after scaling.
2. **Square check** — per generated instance, one equation per endogenous
   variable; this is where DOUBTFUL endo choices get settled.
3. **Balance identity** — rebuild the model's accounting identity (for a CGE:
   the SAM, row sums == column sums) from the solution post-solve.
4. **Homogeneity** — shock the numeraire: real quantities unchanged, prices
   scale.
5. **Experiment comparison** — run one shipped GAMS experiment in both systems
   and compare all variables. This is the acceptance test.

## Pitfalls

- `free_to_timeseries_t` returns an empty frame on a static dump (no `t`
  dimension) — use `static_to_frame`/`GdxStaticDataset`.
- GAMS is case-insensitive; a lowercase `howor(h,w)` in an equation may be the
  *variable* HOWOR, not a parameter. Check declarations, not casing.
- GAMS equations sometimes contain probable typos (an outer index used inside
  an inner sum, e.g. `ZETAER(c,w)` within a `wp`-sum). Translate literally so
  the port replicates GAMS, and flag DOUBTFUL — fixing silently breaks the
  base-replication test.
- Variable records in a GDX may omit zero-level entries; when a "base value
  nonzero" condition matters, take it from the calibrated *parameter*
  (`FD0`, `YH0`, …), which GAMS models conventionally keep.
- Sum conditions compare sublist values as strings — 0/1 sublists must
  literally hold `1`/`0`, and the condition is written `COND=1`.
- Blank lines flush the current `>` equation: a `>>` continuation must
  directly follow its `>` line.
