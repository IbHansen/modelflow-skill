---
name: mf-r-install
description: >
  This skill should be used when setting up R so ModelFlow can estimate with
  it: "install R", "R for ModelFlow", "r-base", "conda R", "Rscript",
  "Rscript.exe not found", "Could not find Rscript", "MODELFLOW_RSCRIPT",
  "R_HOME", "rpy2", "install sandwich / lmtest / ivreg / minpack.lm",
  "The R package ... is not installed", "conda can not install r-base",
  "gsl conflict when installing R", "mfr environment", or before the first
  <estimator=r_lm> / <estimator=r_nls> / Estimate_r call.
metadata:
  version: "0.1.0"
---

# Installing R for ModelFlow estimation

ModelFlow's R estimators (`modelestimator_r`, see `mf-r-estimation`) don't
load R into Python. They write a script and run it with `Rscript`, so R can be
any R installation on the PC, even one in another conda environment. ModelFlow
needs only to find `Rscript`.

`modelestimator_r` ships with the ModelFlow release after 2.94. Until then it
is only in a source checkout of the modelflow repo.

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

## Route 1 – conda, R in an environment of its own (tested on Windows)

R can **not** go into the ModelFlow environment on Windows. conda-forge's
Windows R 4.5 needs `gsl 2.7`, while `cvxopt` (a ModelFlow dependency) needs
`gsl 2.8`. R 4.6 has no Windows builds of the packages. The attempt fails with
`RattlerUnsatisfiableError ... gsl`. conda-forge's `rpy2` depends on `r-base`
and fails the same way. Make a separate environment instead (checked
2026-11-18, gives R 4.5.3):

```
conda create -n mfr -c conda-forge --override-channels r-base=4.5 r-sandwich r-lmtest r-ivreg r-minpack.lm
```

Then point ModelFlow at it, once, and restart the terminal / Jupyter:

```
setx MODELFLOW_RSCRIPT %USERPROFILE%\miniforge3\envs\mfr
```

Use the real path of the environment (`conda env list` shows it). The variable
may name the environment folder. ModelFlow then finds
`<env>\Lib\R\bin\x64\Rscript.exe` and runs it with that environment's R home
and DLL folders first on `PATH`, so it does not pick up the DLLs of the
ModelFlow environment. The environment doesn't need to be activated.

Inside a notebook, for this session only:

```python
import os
os.environ['MODELFLOW_RSCRIPT'] = r'C:\Users\<you>\miniforge3\envs\mfr'
```

More packages later: `conda install -n mfr -c conda-forge --override-channels r-aer`
(conda-forge names are `r-` + the CRAN name in lower case).

## Route 2 – R from CRAN

Install R from https://cran.r-project.org (or `winget install RProject.R`),
then once, in R or RStudio:

```r
install.packages(c("sandwich", "lmtest", "ivreg", "minpack.lm"))
```

No variable needed: ModelFlow finds R in the registry or under
`C:\Program Files\R\R-x.y.z` (newest version wins).

## Check that it works

```python
import modelestimator_r as mr
print(mr.find_rscript())   # e.g. ...\envs\mfr\Lib\R\bin\x64\Rscript.exe
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
in the modelflow repo. It sets `MODELFLOW_RSCRIPT` to `~/miniforge3/envs/mfr`
if the variable is unset, and ends with `ALL OK`.

## How Rscript is found

In order: the `rscript_path=` argument of the estimator, `MODELFLOW_RSCRIPT`,
`R_HOME`, `PATH`, the Windows registry (`SOFTWARE\R-core`), then
`C:\Program Files\R\R-*` and `%LOCALAPPDATA%\Programs\R\R-*`.
Each place may be the executable, an R home (`bin`, `bin\x64`) or a conda
environment (`Lib\R`). A conda launcher in `<env>\Scripts` is swapped for the
real `Lib\R\bin\x64\Rscript.exe`.

## Messages

| Message | Fix |
| --- | --- |
| `Could not find Rscript.exe on PATH, in R_HOME, ...` | Set `MODELFLOW_RSCRIPT` (route 1) or install R (route 2); restart Jupyter after `setx`. |
| `The R package 'sandwich' is not installed ...` | conda: `conda install -n mfr -c conda-forge --override-channels r-sandwich`; CRAN R: `install.packages('sandwich')`. |
| `RattlerUnsatisfiableError ... gsl` | You tried to put R into the ModelFlow environment; use route 1. |
| `Rscript did not finish within N seconds` | `r_timeout=` was given and too short. |

## rpy2

Not needed and not recommended on Windows: `backend='auto'` (the default)
always uses Rscript there, because an embedded R that crashes takes the Python
kernel with it. `backend='rpy2'` is only used when asked for, and needs
`pip install rpy2` in the ModelFlow environment plus an R it can load.
