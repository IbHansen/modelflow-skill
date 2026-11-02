---
name: mf-scenario
description: >
  This skill should be used to turn a plain-language policy or shock into a
  ModelFlow scenario: "/mf-scenario", "set up a scenario where...", "simulate a
  carbon tax of 30", "what happens if the tax rate rises", "write the upd for",
  "run this shock on the PAK model", or "give me the notebook cells for a scenario".
argument-hint: "<description of the shock> [model file]"
metadata:
  version: "0.1.0"
---

# /mf-scenario

Translate the description into ModelFlow code, check it against the model, and
run it when a model file is at hand.

## Steps

1. **Find the variables.** With the model available, search by description:
   `mpak.vlist('!*carbon tax*')`, `mpak['!*tax rate*'].des`. Without it, ask for
   the model file or the variable names. Never guess a mnemonic.
2. **Check each is exogenous** (`v in mpak.exogene`). An endogenous instrument is
   shocked by fixing it and changing `V_X` (`mf-scenarios`). An endogenous
   variable with no `_X` cannot be shocked directly – say so and offer its add
   factor `V_A` or an exogenous driver.
3. **Write the `upd`** with the period and operator matching the description
   (`=` set, `+` add, `%` percent, `=growth` growth rate; `mf-scenarios` has the
   table). State the unit assumption in one line (percentage points vs percent,
   millions of local currency).
4. **Produce the cells**:
   ```python
   mpak, baseline = model.modelload('<model>.pcim', run=1, keep='Baseline')
   scen = baseline.upd('''
   <2025 2050> VAR1 VAR2 = 30
   ''')
   res = mpak(scen, 2025, 2050, keep='<scenario name>')
   mpak.keep_plot('#Headline', 2025, 2050, diffpct=True, legend=True)
   ```
5. **Run it** when the model file is available, with the bundled script:
   ```
   python "<skill base directory>/scripts/run_scenario.py" <model.pcim> \
       --scenario "<name>=<upd line>; <upd line>" --start 2025 --end 2050 \
       [--vars "<pattern>"] [--periods 2025 2030 2040] [--show difpctlevel]
   ```
   `<skill base directory>` is the folder this SKILL.md was loaded from. The
   script warns when `upd` created a new column (a misspelled name) or changed
   nothing. `--opt alfa=0.5` passes solve options.
6. **Report** the headline effects in a few lines: sign and size in the first
   year and at the end, in percent of baseline for real variables, percentage
   points for rates. Suggest `/mf-compare` or `mf-attribution` as the next step.
