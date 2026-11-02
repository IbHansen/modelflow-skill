---
name: mfdev-conventions
description: >
  This skill should be used for any code change in the ModelFlow framework (modelflow2
  repo): editing modelclass.py, modelsolver_ng.py or any modelflow module, "fix this",
  "add an option", "refactor", "implement the design note". It sets how changes are
  made, tested and handed over in this repo.
metadata:
  version: "0.1.0"
---

# How changes are made in ModelFlow

## Before code

- Think before code. For anything beyond a small fix, write or follow a design note
  first (`mfdev-design-notes`) and wait for agreement.
- Read the code being changed and its callers. Name the functions and attributes
  that will change before changing them.

## Scope

- Make the narrowest change that solves the task. Prototype the minimal version,
  extend afterwards.
- Do not touch anything the task does not name: no drive-by refactors, renames,
  reformatting or docstring rewrites elsewhere.
- Prefer a small hook in an existing class over copying a method into a subclass
  (example: a no-op `_hook(ctx, values, row)` call in `iterate`, overridden in the
  new solver).
- Leave the legacy `Solver_Mixin` solvers and the default solver choice in
  `__call__` alone unless the task is about them.
- Breaking API changes are acceptable when the old name or behaviour was
  misleading. Say so explicitly when making one.

## Code style

- Diagnostics go through `print`, not `warnings.warn`.
- Fail fast: check inputs when objects are built, raise with a message that names
  the variable or equation and says what to do.
- Keep generated equations legal Python (the DSL depends on it).
- Watch object dtype: matrix-valued variables make columns object dtype; numeric
  solver paths must filter them out.

## Checking

- Run `python -c "import ast,sys; ast.parse(open(sys.argv[1]).read())" <file>` on
  every edited Python file.
- Add an inline smoke test (a few lines that import the module and exercise the
  change on a small model) and run it.
- For solver or codegen changes run `mfdev-regress`: bit-identical without jit,
  within tolerance with jit.
- There is no pytest suite; test scripts are `#%%` cell files in
  `modelflow/modeltest/`, runnable with `python <file>` or cell by cell.

## Git and hand-over

- Do not run `git` commands unless asked. Commits and branches are made in
  GitHub Desktop.
- Hand over targeted changes as a unified diff, or as edited files plus a short
  list of what changed and why.
- Keep explanations short; code and diffs should be copy-ready.

## Environment

- Users run Jupyter Notebook 7 and Google Colab, often in restricted institutional
  setups. Classic-notebook JavaScript APIs (`IPython` global, AMD `require`,
  `div#notebook-container`) do not exist in Notebook 7: guard with `typeof`
  checks and add `.jp-*` selectors.
- Numba is optional at runtime; code must still solve without it.
- Windows paths and a Danish locale are common on the developer's machine.
