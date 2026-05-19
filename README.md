# ModelFlow Skill for Claude Code

A [Claude Code](https://docs.claude.com/en/docs/claude-code) skill that teaches Claude how to work with the [ModelFlow](https://github.com/IbHansen/modelflow2) Python framework — loading and building macro-structural models, running scenarios, estimating equations, decomposing impacts, and reporting results.

Install it once and Claude will automatically use it whenever you mention ModelFlow, MFMod, or any of the related APIs (`Makemodel`, `Estimate_*`, `.mfcalc`, `.upd`, `model.modelload`, …) — across every project on your machine.

## Install

```bash
git clone https://github.com/IbHansen/modelflow-skill ~/.claude/skills/modelflow
```

On Windows (Git Bash or PowerShell):

```powershell
git clone https://github.com/IbHansen/modelflow-skill $HOME\.claude\skills\modelflow
```

That's it — Claude Code picks up the skill on its next run.

## Update

```bash
cd ~/.claude/skills/modelflow && git pull
```

## What's inside

```
modelflow/
├── SKILL.md                                 router — Claude reads this first
└── references/
    ├── installation.md                      conda / pip setup, Jupyter quirks
    ├── usage.md                             loading models, .upd, .mfcalc, reports
    ├── simulation-methods.md                solver options, .fix, add factors
    ├── worldbank-onboarding.md              MFMod country models
    ├── model-construction.md                FRML strings, .equpdate
    ├── makemodel.md                         markdown / LaTeX model authoring
    ├── estimation.md                        OLS, NLS, constraints, ST. clause
    └── decomposition.md                     .dekomp, .totdif, causal tracing
```

`SKILL.md` is a routing table that points Claude at the right reference file for each kind of task. Claude reads the relevant file(s) before answering, so the guidance is grounded in the actual API rather than improvised from memory.

## How it works

Claude Code looks for skills in two locations:

1. **User-level:** `~/.claude/skills/<name>/` — available across every project
2. **Project-level:** `<project>/.claude/skills/<name>/` — only when working in that project

Installing this repo at `~/.claude/skills/modelflow/` enables the skill globally. No further configuration is needed.

## Updating the skill

This repo is the canonical source — edit here, commit, push. Users pull updates with `git pull`. The skill update cadence is independent of the ModelFlow package release cadence, so typo fixes and improved examples can ship the moment they're ready.

## Related

- **ModelFlow source:** https://github.com/IbHansen/modelflow2
- **Install ModelFlow:**
  ```
  conda create -n modelflow_test modelflow_test -c ibh -c conda-forge
  conda activate modelflow_test
  ```
  or `pip install modelflowib`
- **Manual (PDF):** see `MFMod_Python_Modelflow.pdf` in the ModelFlow repo
