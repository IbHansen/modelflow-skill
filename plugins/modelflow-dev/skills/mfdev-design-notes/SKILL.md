---
name: mfdev-design-notes
description: >
  This skill should be used before implementing a non-trivial ModelFlow framework change,
  or when asked to "write a design note", "plan this", "design X", "think before code",
  or to review a design note for modelflow2. It gives the design-note template, where
  notes live and the checks a note must pass before code is written.
metadata:
  version: "0.1.0"
---

# Design notes before code

Write a design note for any change that adds a solver, changes generated code, adds
DSL syntax, changes a data layout or touches more than one module. Do not write
implementation code until the note is agreed.

## Process

1. Read the code the change touches. Record findings with function names and what
   they do today; measure if the case rests on a performance claim.
2. Draft the note with the template in `references/template.md`.
3. Run the checklist below on the draft and fix what fails.
4. Hand the note over and stop. Implementation starts only after agreement; later
   sessions implement from the note, so it must stand on its own.

## Where notes live

- Save as a plain `.md` file named `<topic>_design.md`.
- In a claude.ai Project, write it to the project docs under `claude/`.
- On Google Drive, create it as plain markdown without conversion to a Google Doc.
- Name the note's path in the reply so a later session can find it.

## Checklist

- **Findings are from the code**: every function, attribute and file named exists
  (grep for each).
- **Invariants kept, or the break stated**: jit signature `(f8[:,:], f8[:,:], i8, f8)`;
  `values` column layout (positions `< ncol` unchanged); transpile stale-file check
  still sees every change in the generated text; `NG_SOLVERS` registration and
  `*_ng` methods; default solver choice in `Solver_Mixin.__call__` untouched.
- **Separate or option**: say whether the change is a new solver class or an option
  on an existing one, and why.
- **Edits to existing classes are listed** one by one, each as small as a hook.
- **Numerical equivalence is stated**: what must be bit-identical (non-jit), what
  only within tolerance (jit, `fastmath=True`), and the test models.
- **Phases** each end in something testable.
- **Out of scope** lists the tempting neighbours explicitly.
- **Decisions** records what the user settled, in their words.
- **Measured potential before effort**: if the note promises speed, it states how
  the gain was estimated and what the realistic ceiling is.
