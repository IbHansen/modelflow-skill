# FRB/US names

FRB/US has no fixed-position grammar like MFMod. Names are short codes
(`XGDP`, `PCPI`, `LUR`, `RFF`); their meaning comes from the Federal Reserve's
variable list for the chosen release and, in ModelFlow, from the model's
descriptions:

```python
mfr['XGDP PCPI LUR RFF'].des
# XGDP  GDP, cw 2012$
# PCPI  Consumer price index, total
# LUR   Civilian unemployment rate (break adjusted)
# RFF   Federal funds rate
```

Do not decode by first letter: the letters are loose hints at best.

## In ModelFlow

- Names are upper case (`xgdp` in the Federal Reserve files is `XGDP`).
- Every equation carries an add factor named `<VAR>_AERR` (FRB/US's own name,
  kept on import), not ModelFlow's `_A`.
- Expectation variables start with `Z` and have the frml option `<Z>`, e.g.
  `ZGAP05` "Expected output gap, for RG5 eq. (VAR exp.)". In the MCE model
  (`frbusmcetest.pcim`) the `Z` equation itself contains the leads.
  A `Z` in the frml options is also ModelFlow's marker for a damped equation, so
  these equations are damped when the solver uses `alfa`.

## The z / w / e rule

The Federal Reserve documents, for its EViews MCE set-up, that an expectation
`zFOO` has a forward-looking twin `wFOO` and an expectation error `zFOOe`. This
rule belongs to that set-up only. In the ModelFlow FRB/US models there are no
such `W` twins: `WPO`, `WPS`, `WPON`, `WPSN` are household wealth variables.
Never read a `W` name as an expectation without the description saying so.

## Workflow

1. Note which release the model comes from (Python package, EViews package and
   data release have separate dates).
2. Look the name up in the model (`.des`, `explain_variable`).
3. Use the description and equation for level vs rate, real vs nominal,
   annualized or not.
4. Not in the model → "unverified identifier"; any reading is a guess and must
   be labelled as such.
