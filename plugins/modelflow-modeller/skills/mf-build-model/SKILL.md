---
name: mf-build-model
description: >
  This skill should be used when creating a ModelFlow model from equations and data:
  "build a model", "new model", "Makemodel", "%%Makemymodel", "markdown model",
  "model from equations", "model(text)", "Mexplode", "type_input", "string of
  equations", "equations from a file", "eq_start", "eq_end", "separator",
  "comment_start", "transform function", "other model format", "replacements",
  "input_df", "save the model", "modeldump", "pcim", "var_description", "equpdate",
  "eqdelete", "change an equation in a loaded model", "LaTeX model", "TLIST",
  "DOABLE", "init_addfactors", or turning a model write-up into a runnable model.
metadata:
  version: "0.1.0"
---

# Building a model

Three entry points, from simplest to most capable:

| Entry | Input | Normalizes, options, templates, estimation |
| --- | --- | --- |
| `model(text)` | normalized FRML text, or one equation per line | no |
| `Makemodel(text, ...)` | markdown with `>` model lines (default), or FRML / EViews / Gekko text | yes |
| `%%Makemymodel name ...` | a notebook cell, same as `Makemodel` | yes, and renders the model |

Use `Makemodel` (or the magic) for new models. `model()` is for finished,
normalized equations.

`Makemodel` reads two kinds of input. Both go through the same expansion
(LIST/DO/sum), normalization, options and estimation:

| Input | `type_input` | Equations are |
| --- | --- | --- |
| markdown: documentation with model lines | `'markdown'` (default) | lines starting with `>` |
| a plain string of equations | `'modelflow'` | every line (or `FRML ... $` statements) |
| one-line FRML string | `'single'` | `FRML ... $` statements on one line |

**Trap:** a plain string passed with the default `type_input='markdown'` has no
`>` lines, so the model is silently empty. Pass `type_input='modelflow'`.

## Markdown models

```markdown
# Consumption
Households smooth consumption.

><stoc> dlog(cons) = 0.5*dlog(y) + 0.1*(log(cons(-1))-log(y(-1)))
>y = cons + i + g
><exo> i = 0.2*y(-1)
```

- A line starting with `>` is an equation; `>>` continues the previous one.
- Every other line is documentation and is rendered, not parsed.
- `$$ ... $$` and `\begin{equation}` LaTeX blocks may hold `LIST` definitions and
  equations (`% @<options>` and `\label{eq:...}` lines).

```python
from modelconstruct_estimation import Makemodel
mm = Makemodel(text)                 # type_input='markdown' is the default
mm.show                              # the finished FRMLs
mmodel = mm.mmodel                   # a modelclass.model
```

## String models

The same equations without markdown – one statement per line, no `>`:

```python
text = '''
list sectors = sectors : agr ind ser
do sectors
  <stoc> {sectors}_y = 0.8*{sectors}_y(-1) + 0.1*gdp(-1)
enddo
gdp = sum(sectors, {sectors}_y)
<stoc> dlog(cons) = 0.5*dlog(gdp)
'''
mm = Makemodel(text, type_input='modelflow')
```

- Options go first on the line (`<stoc> ...`); `FRML` and `$` are optional.
- `FRML ... $` statements may span several lines; the `$` ends each one.
- `type_input='single'`: all statements on one line, each `FRML ... $`.
- Use a string model for generated equations, files read from disk
  (`Makemodel(open('model.frm').read(), type_input='modelflow')`), and scripts;
  use markdown when the model is documented alongside the equations.

Verified: the string above gives `AGR_Y`, `IND_Y`, `SER_Y` with add factors and
fix variables, `GDP = (AGR_Y+IND_Y+SER_Y)` and the normalized `CONS` equation –
the same as the markdown form with `>` on each line.

## Equations in any other format: separators, comments, transform

Four arguments read equations out of foreign text. Giving any of them overrides
the default markdown reading:

| Argument | Meaning |
| --- | --- |
| `eq_start` | marker(s) that start an equation, e.g. `'FRML'`, `['EQ', 'EQUATION']`; text outside start … end is ignored. `None`: an equation starts after the previous one |
| `eq_end` | marker(s) that end an equation, e.g. `'$'`, `';'`; equations may then span lines. `None`: one equation per line |
| `comment_start` | string(s) starting a comment to the end of the line, e.g. `'#'`, `"'"` |
| `transform` | a function called with each equation (markers removed, blanks collapsed) that returns it in ModelFlow form `'<opts> lhs = rhs'`; return `None` or `''` to drop it |

Markers match case-insensitively; word-like markers only as whole words (`'EQ'`
does not match inside `'FREQ'`).

```python
import re
src = '''
# a model in another format
EQ cons: log(cons[t]) = 0.5*log(y[t]) + 0.4*log(cons[t-1]);   # behavioural
EQ y:    y[t] = cons[t] + i[t]
              + g[t];
not an equation, ignored
'''
def my_transform(stmt):
    name, body = stmt.split(':', 1)                       # equation name, equation
    body = re.sub(r'\[t\]', '', body)                     # x[t]   -> x
    body = re.sub(r'\[t([+-]\d+)\]', r'(\1)', body)       # x[t-1] -> x(-1)
    return ('<stoc> ' if name.strip() == 'cons' else '<> ') + body

mm = Makemodel(src, eq_start='EQ', eq_end=';', comment_start='#', transform=my_transform)
```

Verified result: `CONS` normalized with add factor and fix variables, and
`Y = CONS+I+G`. `type_input='gekko'` and `'eviews'` are presets of these four
arguments with ready-made transforms (`mf-import`); an explicit argument
overrides the preset, e.g. `transform=functools.partial(gekko_to_modelflow,
code_map={...})`.

## Text replacements and separate lists

- `replacements=[(old, new), ...]` (or one tuple) – plain string replacements on
  the extracted text, applied **before** upper-casing, so they are
  case-sensitive. Use them for constants (`('SHARE', '0.5')`), renaming, or
  expanding a placeholder into a template (`('__dim', '__{banks}__{country}')`).
  Not regular expressions; use `transform` for patterns.
- `list_defs='list sectors = sectors : agr ind'` – LIST definitions kept apart
  from the equations, e.g. shared by several models. In markdown mode write
  them as model lines (`'>list ...'`).

The order of processing: extract (markdown `>` lines, or the four arguments
above) → `replacements` → upper-case, `FRML`/`$` added → DOABLE → `DO` → lists →
`sum` → estimation → normalization.

## Other arguments

`funks`, `var_description`, `modelname`, and the estimation arguments in
`mf-estimation`.

Inspect each stage with `show<stage>`: `showclean_frml_statements`,
`showpost_do`, `showpost_sum`, `showexpanded_frml`, `shownormal_main`,
`shownormal_calc_add`. `mm.showx` with an unknown name lists them all.
`mm.render` displays the documented model; `mm.draw` the dependency graph.

## The notebook magic

```
%%Makemymodel mymodel input_df=df estimator=ols smpl="(2000, 2019)"
... markdown model ...
```

The first word names the result (a `Makemodel` in the notebook as `mymodel`).
The cell is always read as markdown, so model lines need `>`; for a plain string
of equations call `Makemodel(text, type_input='modelflow')` in a code cell.
Options: `input_df`, `estimator`/`est`, `smpl`, `param_names`, `funks`,
`replacements`, `show`, `draw`, `latex`, `display`, `spec`,
`render_est=0 render=0` (no rendering of the cell), and
`segment=<name>` to build one model from several cells (segments starting with
`list` hold lists, `text` only documentation). Values may be literals or names in
the notebook. Load the magics with `import modeljupytermagic`.

## From model to scenario

```python
mmodel = mm.mmodel
df = mmodel.insertModelVar(data)        # adds missing model columns as 0.0
res = mmodel(df, 2020, 2030)            # solve
```

Add descriptions before saving: `mmodel.var_description = {...}`, groups in
`mmodel.var_groups['#Headline'] = [...]`.

## Saving

```python
mmodel.modeldump('mymodel.pcim')                   # equations, descriptions, lastdf
mmodel.modeldump('mymodel.pcim', keep=True)        # also keep_solutions
mmodel2, df2 = model.modelload('mymodel.pcim', run=1)
```

Check a new model with `/mf-check-model` before using it.

## Deeper reference

- `references/makemodel.md`: the full `Makemodel` guide – LaTeX input, every
  tag, LIST/TLIST/DO/DOABLE and `[sublist=value]` filtering, `replacements=`
  templating, estimation kwargs, `init_addfactors`, combining models with `+`,
  the `%%Makemymodel` magic line and segments, recipes.
- `references/modify-model.md`: changing a loaded model with `equpdate` /
  `eqdelete`, and user functions (`funks=`).
