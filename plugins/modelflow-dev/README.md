# modelflow-dev

Claude Code skills for working on the ModelFlow framework in the `modelflow2` repo.

Use it together with the repo's own `modelflow/CLAUDE.md`, which Claude Code loads automatically. The skills add what that file does not cover: the ng solver pattern, the code generator, the design-note workflow and how to check a solver change.

## Install

```
/plugin marketplace add IbHansen/modelflow-skill
/plugin install modelflow-dev@modelflow
```

## Skills

| Skill | Use |
| --- | --- |
| `mfdev-architecture` | Where a job lives: `modelclass` mixins, sibling modules, legacy vs ng solvers, solver dispatch |
| `mfdev-conventions` | How changes are made in this repo (always applies) |
| `mfdev-design-notes` | Write a design note before code; template and review checklist |
| `mfdev-ng-solvers` | Add or change a solver in `modelsolver_ng.py` |
| `mfdev-codegen` | The generated solver source: `gen_2d`, `parts`, jit, transpile cache |
| `mfdev-regress` | `/mfdev-regress <solver> [reference]` – compare a solver with a reference on PAK and other test models |

## Planned

`mfdev-newton-diff`, `mfdev-dsl-parser`, `mfdev-io`, `mfdev-jupyter`, `/mfdev-bench`, `/mfdev-transpile-clean`, `/mfdev-release`, the `design-reviewer` and `regression-runner` agents, and a post-edit `ast.parse` hook.

## Requirements

- A local clone of `modelflow2`, with Claude Code started in the repo (or `modelflow/`) folder.
- A Python environment where `import modelclass` works from the `modelflow/` folder.
- `modelflow-modeller` installed alongside (DSL and solver-option reference).
