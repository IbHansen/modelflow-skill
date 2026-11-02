# ModelFlow plugins for Claude Code

[Claude Code](https://docs.claude.com/en/docs/claude-code) plugins for the
[ModelFlow](https://github.com/IbHansen/modelflow2) Python framework, one per
audience. This repo is a plugin marketplace named `modelflow`.

| Plugin | For | Skills |
| --- | --- | --- |
| `modelflow-user` | People who run existing models (World Bank MFMod, PAK) | install, load, scenarios, results, attribution, reports, `/mf-scenario`, `/mf-compare`, `/mf-explain` |
| `modelflow-modeller` | People who build and maintain models | equation language, FRML options, normalization, Makemodel, estimation, data, structure, solvers, import, debugging, `/mf-check-model`, `/mf-explain-error`, `/mf-new-equation`, `model-reviewer` agent |
| `modelflow-dev` | Developers of the ModelFlow framework | architecture, conventions, design notes, ng solvers, code generation, `/mfdev-regress` |
| `modelflow-onboarding` | People moving a model from Gekko, EViews or GAMS | planned |

Each layer assumes the one below it: a ModelFlow developer also writes models,
a model developer also runs them. Install the ones you need.

## Install

In Claude Code:

```
/plugin marketplace add IbHansen/modelflow-skill
/plugin install modelflow-user@modelflow
/plugin install modelflow-modeller@modelflow
/plugin install modelflow-dev@modelflow
```

From a local clone: `/plugin marketplace add C:\path\to\modelflow-skill`. A local
marketplace is read from its folder, so edits take effect at the next session
start or after `/reload-plugins` – no update step.

Update with `/plugin marketplace update modelflow`.

## Layout

```
.claude-plugin/marketplace.json
plugins/
  modelflow-user/
    .claude-plugin/plugin.json
    skills/<name>/SKILL.md          short, loaded when the skill triggers
    skills/<name>/references/*.md   deeper material, read on demand
    skills/<name>/scripts/*.py      bundled scripts for the slash commands
  modelflow-modeller/   (+ agents/)
  modelflow-dev/
```

Skill prefixes: `mf-` for the user and modeller plugins, `mfdev-` for the dev
plugin.

## Where the older single-skill material went

This repo used to be one skill (`SKILL.md` + `references/`). The reference files
now sit with the skill they deepen:

| Old file | Now |
| --- | --- |
| `usage.md`, `simulation-methods.md` | `modelflow-user/skills/mf-scenarios/references/` |
| `worldbank-onboarding.md` | `modelflow-user/skills/mf-load-model/references/` |
| `decomposition.md` | `modelflow-user/skills/mf-attribution/references/` |
| `makemodel.md`, `model-construction.md` (→ `modify-model.md`) | `modelflow-modeller/skills/mf-build-model/references/` |
| `estimation.md` | `modelflow-modeller/skills/mf-estimation/references/` |
| `gams-to-makemodel.md` | `modelflow-modeller/skills/mf-import/references/` (moves to `modelflow-onboarding`) |
| `installation.md` | install part → `mf-getting-started`; notebook JS/CSS part → `modelflow-dev/skills/mfdev-architecture/references/jupyter-display.md` |

`skills.ipynb` renders every skill and reference file for reading.

## Related

- ModelFlow source: https://github.com/IbHansen/modelflow2
- Install ModelFlow: `conda create -n modelflow -c ibh -c conda-forge modelflow` or `pip install ModelFlowIb`
- Manual: https://worldbank.github.io/MFMod-ModelFlow/content/introduction.html
