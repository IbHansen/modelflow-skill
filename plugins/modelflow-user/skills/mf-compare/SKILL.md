---
name: mf-compare
description: >
  This skill should be used to compare ModelFlow scenarios: "/mf-compare",
  "compare the scenarios", "baseline versus scenario", "table of differences",
  "plot the scenarios", "how do the scenarios differ for GDP", or "side by side
  results".
argument-hint: "<variable pattern> [scenarios] [periods]"
metadata:
  version: "0.1.0"
---

# /mf-compare

Produce a comparison of kept scenarios for the requested variables: a table of
differences and a chart, plus a short reading.

## In a notebook (scenarios already kept)

```python
pat = 'PAKNYGDPMKTPKN PAKNECONPRVTKN'
list(mpak.keep_solutions)                                    # which scenarios exist
mpak.keep_plot(pat, 2025, 2050, diffpct=True, legend=True)   # % of the first kept scenario
t = mpak.table(pat, datatype='growth', scenarios='Baseline|Carbon tax 30', smpl=(2025, 2030))
t
wide = mpak.keep_get_df(pat)                                 # numbers, variable x scenario
```

- `diffpct=True` and `diff=True` compare with the **first** kept scenario; keep
  the baseline first.
- For the last solve against the baseline only: `mpak[pat].difpctlevel.df`.
  (`.difpct` is a growth-rate difference, not percent of level.)

## From a model file

Run the scenarios with the script of the `mf-scenario` skill (in this plugin at
`skills/mf-scenario/scripts/run_scenario.py`), one `--scenario` per scenario:

```
python run_scenario.py pak.pcim --scenario "Carbon tax=<2025 2050> PAKGGREVCO2CER PAKGGREVCO2GER PAKGGREVCO2OER = 30" \
    --scenario "Carbon and GST=<2025 2050> PAKGGREVCO2CER PAKGGREVCO2GER PAKGGREVCO2OER = 30; <2025 2030> PAKGGREVGNFSXN + 1" \
    --start 2025 --end 2050 --vars "PAKNYGDPMKTPKN PAKNECONPRVTKN" --periods 2025 2030 2040 2050
```

## The reading

Two to four sentences: which scenario moves the variable most, the sign and size
at the start and end, and whether the effect fades or builds. Use the variable
descriptions, not only mnemonics. If two scenarios give identical numbers, check
that the second shock hit an exogenous variable (`mf-troubleshoot-run`).
