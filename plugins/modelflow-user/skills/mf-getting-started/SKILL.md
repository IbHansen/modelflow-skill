---
name: mf-getting-started
description: >
  This skill should be used when installing or setting up ModelFlow, or starting a
  first notebook: "install modelflow", "conda", "pip install", "Google Colab",
  "set up the environment", "update modelflow", "graphviz not found", "Jupyter
  Notebook 7", "first steps", "import modelclass", or "the notebook looks wrong".
metadata:
  version: "0.1.0"
---

# Getting started

## Install

Conda (Windows, macOS, Linux), in its own environment:

```
conda create -n modelflow -c ibh -c conda-forge modelflow -y
conda activate modelflow
pip install dash_interactive_graphviz
```

Pip (also Colab): `pip install ModelFlowIb`.

Update: `conda update -n modelflow -c ibh -c conda-forge modelflow`, or
`pip install -U ModelFlowIb`.

Optional extras: EViews link `conda install pyeviews -c conda-forge` (Windows,
needs EViews); LaTeX (MiKTeX or TeX Live) for PDF reports.

## Claude's ModelFlow tools (MCP server)

The plugin's `modelflow` MCP server runs in the conda environment `modelflow`
and also needs the `mcp` package, so for use with Claude create it as:

```
conda create -n modelflow -c ibh -c conda-forge modelflow mcp -y
```

(or add it to an existing environment: `conda install -n modelflow -c conda-forge mcp`).
Then reconnect the server: `/mcp` → modelflow → Reconnect. To use another
environment, use the `list_environments` and `select_environment` tools and
reconnect. Miniforge must be installed in the default place (per user or all
users) for the server to find the `modelflow` environment.

## Google Colab

```python
import os
os.system('apt -qqq install graphviz')
os.system('pip -qqq install ModelFlowIb')
```

Colab has no LaTeX, so `.pdf()` on reports does not work there.

## Graphviz

Dependency graphs (`draw`, `tracepre`, `explain`) need the Graphviz program
`dot`. If it is missing, install it (`conda install graphviz -c conda-forge`, or
the installer from graphviz.org). On Windows the installer often does not put it
on PATH – add `C:\Program Files\Graphviz\bin` to PATH and restart Jupyter.
Check with `dot -V` in a terminal.

## First notebook cell

```python
from modelclass import model
model.widescreen()
model.scroll_off()
```

`widescreen()` widens the output area and `scroll_off()` stops long output being
put in a scroll box.

## Where to go next

- Load a model: `mf-load-model`.
- Run a scenario: `mf-scenarios`.
- Look at results: `mf-results`.
