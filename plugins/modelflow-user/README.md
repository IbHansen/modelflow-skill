# modelflow-user

Claude Code skills for running existing ModelFlow models, such as the World Bank
MFMod country models: installing, loading a model, running scenarios, comparing
and explaining results, and making tables and charts.

## Install

```
/plugin marketplace add IbHansen/modelflow-skill
/plugin install modelflow-user@modelflow
```

## Skills

| Skill | Use |
| --- | --- |
| `mf-getting-started` | Install (conda, pip, Colab), Graphviz, first notebook cell |
| `mf-load-model` | `modelload`, the World Bank models, variable names, finding variables |
| `mf-scenarios` | `upd`, solving and keeping scenarios, fixing, add factors |
| `mf-results` | Differences from baseline, `keep_plot`, getting numbers out |
| `mf-attribution` | `totdif` (which shock) and `dekomp` (which input) |
| `mf-reports` | `mpak.table`, `mpak.plot`, combining, PDF/LaTeX/HTML, stored reports |
| `mf-variable-names` | Read and check names: MFMod mnemonics, FRB/US names, ModelFlow suffixes; parser script |
| `mf-ode-simulate` | Run ODE models (orbits, projectiles): the dataframe, events, checking the time step |
| `mf-animate` | Animations of results in a notebook: 2-D, 3-D, scenarios unfolding; size and saving |
| `mf-troubleshoot-run` | No effect, not converged, NaN, results that changed |
| `/mf-scenario` | Turn a described shock into a scenario and run it (bundled script) |
| `/mf-compare` | Compare scenarios: table, chart, short reading |
| `/mf-explain` | Explain a variable from the model itself |

## MCP server (Windows, Miniforge)

The plugin also starts an MCP server, `modelflow`, that keeps models in memory
between calls, so Claude can load a model once and then run and compare
scenarios directly:

| Tool | Use |
| --- | --- |
| `load_model` | Load a `.pcim` (path, URL or repository name) and solve the baseline |
| `find_variables` | Search by name pattern, `!description` or `#group` |
| `explain_variable` | Description, equation, options, where it is used |
| `run_scenario` | Apply `upd` text and solve; shows the headline effects |
| `show_results` | Levels, differences, percent differences or growth, chosen periods |
| `list_models` | Loaded models and their scenarios |
| `environment_status`, `list_environments`, `select_environment` | Which conda environment the server uses |

The server runs in the Miniforge environment `modelflow`, which needs ModelFlow
and the `mcp` package:

```
conda create -n modelflow -c ibh -c conda-forge modelflow mcp
```

or, for an existing environment, `conda install -n modelflow -c conda-forge mcp`.
To use another environment, ask Claude to list and select one
(`select_environment` saves its folder in `%USERPROFILE%\.modelflow_mcp_env`),
then reconnect with `/mcp` → modelflow → Reconnect. Deleting that file goes back
to the default.

At the start of each session a hook (`hooks/check_env.ps1`) checks that
Miniforge, the environment, ModelFlow and `mcp` are there, and if not tells
Claude what is missing so it can help install it. It prints nothing when all is
well.

Files: `.mcp.json`, `server/start.cmd` (finds the environment),
`server/modelflow_mcp.py` (the tools, works with mcp 1.x and 2.x),
`hooks/hooks.json`, `hooks/check_env.ps1`. Everything ModelFlow prints goes to
stderr, because stdout carries the MCP protocol.

## Requirements

ModelFlow installed (`conda install modelflow -c ibh -c conda-forge` or
`pip install ModelFlowIb`). Building or changing models is covered by
`modelflow-modeller`.
