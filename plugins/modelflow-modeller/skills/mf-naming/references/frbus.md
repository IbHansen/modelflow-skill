# FRB/US names (Federal Reserve)

No fixed-position grammar. Names are short codes (`xgdp`, `pcpi`, `lur`, `rff`)
whose meaning comes from the release's variable list and equation descriptions.
Do not decode by first letter.

## Expectations

The Federal Reserve's technical Q&A
(https://www.federalreserve.gov/econres/us-technical-qas.htm) documents, for the
EViews MCE set-up: expectation `zFOO` (backward-looking equation), forward-looking
twin `wFOO`, expectation error `zFOOe`. This holds for that set-up only.

## In ModelFlow (`frbusmcetest.pcim`)

- Upper case: `XGDP` "GDP, cw 2012$", `RFF` "Federal funds rate".
- Each equation has an add factor `<VAR>_AERR`, the FRB/US name, not `_A`.
- Expectations are `Z...` equations with option `<Z>` and the leads written in
  the equation, e.g. `ZRFF5 = 0.0548*RFF + 0.9452*ZRFF5(+1) + ZRFF5_AERR`.
  The `Z` option also marks the equation as damped (see `mf-frml-options`).
- No `W` twins: `WPO`, `WPS`, `WPON`, `WPSN` are household wealth.

## On import

Keep the names (upper-cased) and the `_AERR` add factors; carry the
descriptions across. Record the package and data date: the Python package,
EViews package and data release are dated separately.
