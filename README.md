# ModelFlow plugins for Claude Code

[Claude Code](https://docs.claude.com/en/docs/claude-code) plugins for the
[ModelFlow](https://github.com/IbHansen/modelflow2) Python framework, one per
audience. This repo is a plugin marketplace named `modelflow`.

> [!WARNING]
> **This is highly experimental.** The plugins, skills and MCP server are new,
> have been tried by very few people and will change without notice. Check the
> results Claude gives you against ModelFlow itself before relying on them.
>
> **Feedback is very welcome**: what worked, what did not, and what you would
> like added. Please open an
> [issue](https://github.com/IbHansen/modelflow-skill/issues) or contact Ib Hansen.

| Plugin | For | Skills |
| --- | --- | --- |
| `modelflow-user` | People who run existing models (World Bank MFMod, PAK) | install, load, variable names, scenarios, results, ODE simulations, animations, attribution, reports, `/mf-scenario`, `/mf-compare`, `/mf-explain` |
| `modelflow-modeller` | People who build and maintain models | equation language, FRML options, naming conventions, normalization, Makemodel, ODE models (Runge–Kutta), estimation, data, structure, solvers, import, debugging, `/mf-check-model`, `/mf-explain-error`, `/mf-new-equation`, `model-reviewer` agent |
| `modelflow-dev` | Developers of the ModelFlow framework | architecture, conventions, design notes, ng solvers, code generation, the ODE preprocessor, `/mfdev-regress` |
| `modelflow-onboarding` | People moving a model from Gekko, EViews or GAMS | planned |

Each layer assumes the one below it: a ModelFlow developer also writes models,
a model developer also runs them. Install the ones you need.

## Quick start (Windows)

You need [Claude Code](https://code.claude.com/docs),
[Miniforge](https://conda-forge.org/download/) and, to install from GitHub,
[Git](https://git-scm.com/download/win): Claude Code uses Git to fetch the
plugins. Without Git, use the ZIP route in B. The `modelflow-user` plugin
includes an MCP server that runs ModelFlow in the conda environment `modelflow`,
so Claude can load a model, run scenarios and show results directly.

### A. From GitHub (no clone)

In a terminal:

```
winget install Git.Git
winget install CondaForge.Miniforge3
conda create -n modelflow -c ibh -c conda-forge modelflow mcp
claude plugin marketplace add IbHansen/modelflow-skill
claude plugin install modelflow-user@modelflow
```

Open a new terminal after installing Git and Miniforge, so `git` and `conda` are
found (or use the Miniforge Prompt). If `claude` is not recognized, its installer
left `%USERPROFILE%\.local\bin` off your PATH: add that folder to the user PATH,
or use route B, which finds it there. Add `modelflow-modeller@modelflow` and `modelflow-dev@modelflow`
the same way if you need them. Update later with
`claude plugin marketplace update modelflow`.

### B. From a clone

```
git clone https://github.com/IbHansen/modelflow-skill
cd modelflow-skill
setup.cmd
```

No Git? On GitHub use **Code → Download ZIP**, unzip it, and run `setup.cmd` in
the unzipped folder.

`setup.cmd` checks Miniforge and Claude Code, creates or completes the
`modelflow` environment, adds the marketplace and installs `modelflow-user`. Run
it again at any time; it skips what is already in place.

- `setup.cmd` installs the plugins from GitHub (updates come with
  `claude plugin marketplace update modelflow`). If Git is not installed it says
  so and installs from its own folder instead: everything works, but there are
  no automatic updates. To switch to GitHub later, install Git, run
  `claude plugin marketplace remove modelflow` and run `setup.cmd` again.
- `setup.cmd local` installs them from the clone itself. A local marketplace is
  read from its folder, so your edits take effect at the next session start or
  after `/reload-plugins`, with no update step.
- Add `modeller` and/or `dev` to install those plugins too, for example
  `setup.cmd local modeller`.

### Check that it works

Start `claude`, type `/mcp` and look for `plugin:modelflow-user:modelflow` as
connected. Then ask, for example, *load the PAK model and run a carbon tax of 30*.
If something is missing, a check at session start tells Claude what it is.

### C. Only the MCP server (no skills)

With a clone, the server can be registered on its own. `start.cmd` finds the
`modelflow` environment by itself.

Claude Code:

```
claude mcp add --scope user modelflow -- cmd /c C:\path\to\modelflow-skill\plugins\modelflow-user\server\start.cmd
```

Claude Desktop (chat app): Settings → Developer → Edit Config, then add to
`claude_desktop_config.json` and restart the app:

```json
{
  "mcpServers": {
    "modelflow": {
      "command": "cmd",
      "args": ["/c", "C:\\path\\to\\modelflow-skill\\plugins\\modelflow-user\\server\\start.cmd"]
    }
  }
}
```

Do not register it this way and also install the `modelflow-user` plugin, or
the same tools appear twice.

### D. Other AI tools: VS Code Copilot and Cursor

MCP is an open standard, so the server also works with other tools that can
start a local MCP server. They get the tools (`load_model`, `run_scenario`,
`show_results`, ...) but not the Claude skills or the session-start check, so if
the `modelflow` environment is missing you will only see a tool error. Set up the
environment first (section A, first two lines) and use a clone.

**VS Code with GitHub Copilot.** Run *MCP: Open User Configuration* from the
Command Palette (or create `.vscode\mcp.json` in a workspace to use it there
only) and add:

```json
{
  "servers": {
    "modelflow": {
      "type": "stdio",
      "command": "cmd",
      "args": ["/c", "C:\\path\\to\\modelflow-skill\\plugins\\modelflow-user\\server\\start.cmd"]
    }
  }
}
```

Start the server from the *Start* link shown above it in the file (or *MCP: List
Servers*), then open Copilot Chat in **Agent** mode. The ModelFlow tools are
listed under the tools button.

**Cursor.** Open Settings → MCP → Add new global MCP server. That opens
`%USERPROFILE%\.cursor\mcp.json`; use `.cursor\mcp.json` in a project to use it
there only. Add:

```json
{
  "mcpServers": {
    "modelflow": {
      "command": "cmd",
      "args": ["/c", "C:\\path\\to\\modelflow-skill\\plugins\\modelflow-user\\server\\start.cmd"]
    }
  }
}
```

The server shows a green dot in the MCP settings when it is running. Use it from
the chat in Agent mode.

In both, replace `C:\path\to\modelflow-skill` with your clone, using double
backslashes in JSON. To run the server in another conda environment, see
`plugins/modelflow-user/README.md` (`%USERPROFILE%\.modelflow_mcp_env`).

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

To read all the skills and their reference files in one place, open
[`skills.ipynb`](skills.ipynb). It renders every one of them.

## Related

- ModelFlow source: https://github.com/IbHansen/modelflow2
- Install ModelFlow: `conda create -n modelflow -c ibh -c conda-forge modelflow` or `pip install ModelFlowIb`
- Manual: https://worldbank.github.io/MFMod-ModelFlow/content/introduction.html
