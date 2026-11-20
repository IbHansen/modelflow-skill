---
name: mf-r-install
description: >
  This skill should be used when setting up R so ModelFlow can estimate with
  it: "install R", "R for ModelFlow", "RStudio", "CRAN", "Rscript",
  "Rscript.exe not found", "Could not find Rscript", "MODELFLOW_RSCRIPT",
  "R_HOME", "rpy2", "install sandwich / lmtest / ivreg / minpack.lm",
  "The R package ... is not installed", "conda install r-base",
  "gsl conflict when installing R", or before the first
  <estimator=r_lm> / <estimator=r_nls> / Estimate_r call.
metadata:
  version: "0.2.0"
---

# Installing R for ModelFlow estimation

ModelFlow's R estimators (`modelestimator_r`, see `mf-r-estimation`) don't
load R into Python. They write an R script and run it with `Rscript.exe` as a
separate process. So R is installed as an ordinary Windows program, R and
RStudio from their own installers, and never in the conda environment. R and
ModelFlow share no DLLs or packages, can't conflict, and are updated
separately.

`modelestimator_r` ships with the ModelFlow release after 2.94. Until then it
is only in a source checkout of the modelflow repo.

## Install R and RStudio

```
winget install -e --id RProject.R
winget install -e --id Posit.RStudio
```

or the installers from https://cran.r-project.org/bin/windows/base/ and
https://posit.co/download/rstudio-desktop/.

Then once, in the RStudio Console:

```r
install.packages(c("sandwich", "lmtest", "ivreg", "minpack.lm"))
```

Answer yes when R offers a personal library
(`Documents\R\win-library\4.x`); Rscript reads it too.

Nothing has to be set in ModelFlow. It finds R in the registry
(`SOFTWARE\R-core`), under `C:\Program Files\R\R-x.y.z` (all-users install) or
`%LOCALAPPDATA%\Programs\R\R-x.y.z` (install without admin rights); the newest
version wins. It runs Rscript with that R's own `R_HOME` and `bin\x64` first
on `PATH`.

Don't install R in the ModelFlow environment (`conda install r-base`): on
Windows conda-forge's R needs another `gsl` than `cvxopt`, and conda stops with
`RattlerUnsatisfiableError ... gsl`.

## R packages per method

| Method | R package |
| --- | --- |
| `lm` | none (base R) |
| `hac` | `sandwich` |
| `ivreg` | `ivreg` (or `AER`) |
| `nls` | none (base R) |
| `nlsLM` | `minpack.lm` |
| extra residual tests for `lm`/`hac` | `lmtest` (optional; without it only Jarque-Bera is run) |

Install all four: then every method works.

## Check that it works

```python
import modelestimator_r as mr
print(mr.find_rscript())   # e.g. C:\Program Files\R\R-4.6.2\bin\x64\Rscript.exe
```

```python
import os, modelestimator_r as mr
from pathlib import Path
d = Path(os.environ['TEMP'])
mr.run_r_script('for (p in c("sandwich","lmtest","ivreg","minpack.lm")) '
                'library(p, character.only = TRUE); cat("ok\\n")', d)
print((d / 'r_console.txt').read_text())          # ok
```

Write it in a `.py` file or a notebook cell. On the PowerShell command line
(`python -c ...`) the double quotes are stripped and R reports
`object 'sandwich' not found`. Package start-up messages from R ("Loading
required package: zoo") come after `ok`. They appear in the language of the
Windows locale, and non-ASCII letters may be garbled. That's harmless.

Full check against Python references (lm = `Estimate_ols`, hac = statsmodels,
ivreg = numpy 2SLS, nls/nlsLM = lmfit): `modeltest/rtest/r_estimation_test.py`
in the modelflow repo, ends with `ALL OK`.

## R in another folder

Only if R is installed somewhere ModelFlow doesn't look (a copy on another
drive, a portable R): point ModelFlow at its folder once, then restart Jupyter:

```
setx MODELFLOW_RSCRIPT "D:\R\R-4.6.2"
```

or per estimator, `rscript_path=r'D:\R\R-4.6.2'`. The search order is: the
`rscript_path=` argument, `MODELFLOW_RSCRIPT`, `R_HOME`, `PATH`, the registry,
then `C:\Program Files\R\R-*` and `%LOCALAPPDATA%\Programs\R\R-*`. A set
`MODELFLOW_RSCRIPT` wins over the installed R; remove it with
`reg delete HKCU\Environment /v MODELFLOW_RSCRIPT /f`.

## Messages

| Message | Fix |
| --- | --- |
| `Could not find Rscript.exe on PATH, in R_HOME, ...` | Install R (above). If it is installed in another folder, set `MODELFLOW_RSCRIPT`; restart Jupyter after `setx`. |
| `The R package 'sandwich' is not installed ...` | `install.packages('sandwich')` in the RStudio Console. |
| `RattlerUnsatisfiableError ... gsl` | R was being installed into the ModelFlow environment; install it from CRAN instead. |
| `Rscript did not finish within N seconds` | `r_timeout=` was given and too short. |

## rpy2

Not needed and not recommended on Windows: `backend='auto'` (the default)
always uses Rscript there, because an embedded R that crashes takes the Python
kernel with it. `backend='rpy2'` is only used when asked for, and needs
`pip install rpy2` in the ModelFlow environment.
