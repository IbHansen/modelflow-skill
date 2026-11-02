# -*- coding: utf-8 -*-
"""
ModelFlow MCP server for the modelflow-user plugin.

start.cmd runs this file with the python of the selected conda environment:
the full path stored in ~/.modelflow_mcp_env by select_environment, or the
Miniforge environment 'modelflow' when nothing is selected.

Loaded models, baselines and scenarios stay in memory between tool calls.
Everything ModelFlow prints goes to stderr, because stdout carries the MCP
protocol.
"""
import ast
import contextlib
import functools
import sys
from pathlib import Path

try:                                    # mcp 2.x
    from mcp.server.mcpserver import MCPServer
    from mcp.server.mcpserver.exceptions import ToolError
except ImportError:                     # mcp 1.x
    from mcp.server.fastmcp import FastMCP as MCPServer
    from mcp.server.fastmcp.exceptions import ToolError

CONFIG = Path.home() / ".modelflow_mcp_env"
DEFAULT_ENV = "modelflow"
MAX_ROWS = 200

mcp = MCPServer(
    "modelflow",
    instructions=(
        "Load ModelFlow models (.pcim), run scenarios and look at results in a "
        "persistent Python process. Start with load_model. Scenarios are written "
        "as ModelFlow upd text. If a tool says ModelFlow can not be imported, use "
        "list_environments and select_environment."
    ),
)

_models = {}        # name -> {"m", "base", "baseline", "scenarios": {name: {"upd", "df"}}}
_model_class = None


def tool(fn):
    """Register a tool. Any exception becomes a ToolError, so its message reaches
    Claude (mcp 2.x hides the text of other exceptions)."""
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ToolError:
            raise
        except Exception as e:
            raise ToolError(f"{type(e).__name__}: {e}") from e
    return mcp.tool()(wrapper)


def quiet():
    """Send prints to stderr while ModelFlow works (stdout is the protocol)."""
    return contextlib.redirect_stdout(sys.stderr)


# ---------------------------------------------------------------- environment

def _conda_root():
    prefix = Path(sys.prefix)
    return prefix.parent.parent if prefix.parent.name.lower() == "envs" else prefix


def _site_packages(envdir):
    win = envdir / "Lib" / "site-packages"
    if win.is_dir():
        return win
    found = sorted(envdir.glob("lib/python3*/site-packages"))
    return found[-1] if found else None


def _check(envdir):
    sp = _site_packages(envdir)
    return {
        "python": any((envdir / p).exists() for p in ("python.exe", "bin/python")),
        "modelflow": bool(sp and (sp / "modelclass.py").exists()),
        "mcp": bool(sp and (sp / "mcp").is_dir()),
    }


def _environments():
    root = _conda_root()
    envs = [("base", root)]
    if (root / "envs").is_dir():
        envs += [(d.name, d) for d in sorted((root / "envs").iterdir()) if d.is_dir()]
    return envs


def _modelclass():
    global _model_class
    if _model_class is None:
        try:
            with quiet():
                from modelclass import model
        except ImportError as e:
            raise ToolError(
                f"ModelFlow can not be imported in {sys.prefix} ({e}).\n"
                f'Install it there with:  conda install -p "{sys.prefix}" -c ibh -c conda-forge modelflow\n'
                "or pick another environment with list_environments and select_environment."
            )
        _model_class = model
    return _model_class


@tool
def environment_status() -> str:
    """Show which Python environment the ModelFlow tools run in and the ModelFlow version."""
    lines = [f"Python:      {sys.executable} ({sys.version.split()[0]})",
             f"Selected in: {CONFIG if CONFIG.exists() else 'nothing saved, default ' + DEFAULT_ENV!r}"]
    try:
        model = _modelclass()
        import modelclass
        version = getattr(model, "__version__", None) or getattr(modelclass, "__version__", None)
        if not version:
            from importlib import metadata
            for dist in ("modelflow", "ModelFlowIb"):
                try:
                    version = metadata.version(dist)
                    break
                except metadata.PackageNotFoundError:
                    pass
        lines.append(f"ModelFlow:   {version or 'version unknown'} ({modelclass.__file__})")
    except ToolError as e:
        lines.append(f"ModelFlow:   not available. {e}")
    lines.append(f"Loaded models: {', '.join(_models) or 'none'}")
    return "\n".join(lines)


@tool
def list_environments() -> str:
    """List the conda environments of this Miniforge installation and whether each has ModelFlow and mcp installed."""
    current = Path(sys.prefix).resolve()
    rows = []
    for name, d in _environments():
        c = _check(d)
        if not c["python"]:
            continue
        mark = "*" if d.resolve() == current else " "
        rows.append(f"{mark} {name:<24} modelflow: {'yes' if c['modelflow'] else 'no ':<3}  "
                    f"mcp: {'yes' if c['mcp'] else 'no ':<3}  {d}")
    return ("* = the environment the server runs in now. An environment needs both "
            "modelflow and mcp to run the tools.\n" + "\n".join(rows))


@tool
def select_environment(environment: str) -> str:
    """Make the ModelFlow tools use another conda environment (a name from list_environments or a full path).
    Takes effect when the MCP server is reconnected."""
    root = _conda_root()
    if Path(environment).is_dir():
        envdir = Path(environment)
    elif environment == "base":
        envdir = root
    else:
        envdir = root / "envs" / environment
    envdir = envdir.resolve()
    c = _check(envdir)
    if not c["python"]:
        raise ToolError(f"{envdir} is not a conda environment with Python. See list_environments.")
    CONFIG.write_text(str(envdir))
    msg = [f"Saved {envdir} in {CONFIG}."]
    missing = [p for p in ("modelflow", "mcp") if not c[p]]
    if missing:
        msg.append(f"It lacks {' and '.join(missing)}. Install with:\n"
                   f'  conda install -p "{envdir}" -c ibh -c conda-forge {" ".join(missing)}')
    msg.append("Reconnect the server to use it: /mcp, choose modelflow, Reconnect.")
    return "\n".join(msg)


# ---------------------------------------------------------------- models

def _get(name):
    if not _models:
        raise ToolError("No model loaded. Use load_model first.")
    if not name:
        if len(_models) == 1:
            return next(iter(_models.items()))
        raise ToolError(f"Several models are loaded ({', '.join(_models)}); give the model name.")
    if name not in _models:
        raise ToolError(f"No model called {name!r}. Loaded: {', '.join(_models)}.")
    return name, _models[name]


def _label(x, index):
    """Turn a period typed as text into the label type of the index."""
    if x in (None, ""):
        return None
    if index.dtype.kind in "iu":
        return int(x)
    return x


def _default_vars(m):
    if "Headline" in getattr(m, "var_groups", {}):
        return m.vlist("#Headline")
    return sorted(m.endogene)[:10]


def _pick_periods(per, periods, n=8):
    if periods:
        wanted = [_label(p, per) for p in periods.replace(",", " ").split()]
        return [p for p in wanted if p in per]
    per = list(per)
    if len(per) <= n:
        return per
    step = (len(per) - 1) / (n - 1)
    return [per[round(i * step)] for i in range(n)]


def _descriptions(m, names):
    desc = getattr(m, "var_description", {})
    return "\n".join(f"  {v:<22} {desc[v]}" for v in names if desc.get(v, v) != v)


@tool
def load_model(path: str, name: str = "", start: str = "", end: str = "") -> str:
    """Load a ModelFlow model from a .pcim file (path or URL; a bare name like 'pak' is also
    looked up in the ModelFlow model repository) and solve the baseline.
    start/end set the solve period for this model's baseline and scenarios; default is the
    period saved with the model."""
    model = _modelclass()
    with quiet():
        m, base = model.modelload(path, run=0)
        span = [_label(start, base.index), _label(end, base.index)]
        if None in span:
            span = []
        baseline = m(base, *span, silent=1)
    name = name or Path(path).stem
    _models[name] = {"m": m, "base": base, "baseline": baseline, "span": span,
                     "per": m.current_per, "scenarios": {}}
    per = m.current_per
    head = _default_vars(m)
    return (f"Loaded {name!r}: {len(m.endogene)} endogenous and {len(m.exogene)} exogenous "
            f"variables. Baseline solved {per[0]}-{per[-1]}.\n"
            f"Headline variables:\n{_descriptions(m, head) or '  ' + ' '.join(head)}")


@tool
def list_models() -> str:
    """List the loaded models and their scenarios."""
    if not _models:
        return "No model loaded."
    out = []
    for name, st in _models.items():
        per = st["per"]
        out.append(f"{name}: {per[0]}-{per[-1]}")
        for s, info in st["scenarios"].items():
            out.append(f"  {s}: {info['upd'].replace(chr(10), '; ')}")
    return "\n".join(out)


@tool
def find_variables(pattern: str, model: str = "") -> str:
    """Find variables by name pattern (wildcards like *GDP*), by description ('!*consumption*')
    or by group ('#Headline'). Shows each variable's description and whether it is endogenous."""
    _, st = _get(model)
    m = st["m"]
    try:
        with quiet():
            names = m.vlist(pattern)
    except Exception as e:
        raise ToolError(f"No variables match {pattern!r} ({e}).")
    if not names:
        return f"No variables match {pattern!r}."
    desc = getattr(m, "var_description", {})
    rows = [f"{v:<22} {'endo' if v in m.endogene else 'exo '}  {desc.get(v, '')}"
            for v in names[:MAX_ROWS]]
    more = f"\n... and {len(names) - MAX_ROWS} more" if len(names) > MAX_ROWS else ""
    return "\n".join(rows) + more


@tool
def explain_variable(variable: str, model: str = "") -> str:
    """Show a variable's description, whether it is exogenous, its equation and options,
    and the equations that use it."""
    _, st = _get(model)
    m = st["m"]
    v = variable.upper()
    if v not in m.allvar:
        raise ToolError(f"{v} is not in the model. Use find_variables to search.")
    desc = getattr(m, "var_description", {}).get(v, "")
    lines = [f"{v}: {desc}" if desc else v]
    if v in m.endogene:
        lines += ["Endogenous.",
                  f"Options:  {m.allvar[v].get('frmlname', '')}",
                  f"Equation: {m.allvar[v].get('frml', '')}"]
    else:
        lines.append("Exogenous: change it in a scenario with upd.")
    used = sorted(w for w in m.endogene if w != v and
                  v in {t.var for t in m.allvar[w]["terms"] if t.var})
    if used:
        lines.append(f"Used in the equations for: {', '.join(used[:40])}"
                     + (f" and {len(used) - 40} more" if len(used) > 40 else ""))
    return "\n".join(lines)


def _parse_options(options):
    opts = {}
    for kv in options.split():
        k, _, v = kv.partition("=")
        try:
            opts[k] = ast.literal_eval(v)
        except (ValueError, SyntaxError):
            opts[k] = v
    return opts


@tool
def run_scenario(scenario: str, upd: str, model: str = "", options: str = "") -> str:
    """Run a scenario: apply ModelFlow upd text to the model's input data and solve.
    upd lines look like '<2025 2030> PAKGGREVCO2CER = 30' or '<2025 2050> PAKNEGDIKSTKKN * 1.02';
    separate several lines with ';' or newlines. options are solve options such as
    'alfa=0.5 solver=newton'. Returns the effect on the headline variables in percent of baseline."""
    mname, st = _get(model)
    m, base = st["m"], st["base"]
    updtext = "\n".join(line.strip() for line in upd.replace(";", "\n").splitlines() if line.strip())
    try:
        with quiet():
            scen = base.upd(updtext)
    except Exception as e:
        raise ToolError(f"ModelFlow could not read the upd text ({e}). Each line should look like "
                        "'<2025 2030> VARIABLE = 30' (operators: = + * % =growth +growth =diff, "
                        "with spaces around the operator).\n"
                        f"Text was:\n{updtext}")
    warnings = []
    new = [c for c in scen.columns if c not in base.columns]
    changed = [c for c in scen.columns if c in base.columns and not scen[c].equals(base[c])]
    if new:
        warnings.append(f"Warning: upd created new columns (misspelled names?): {', '.join(new)}")
    if not changed and not new:
        warnings.append("Warning: upd changed nothing in the data.")
    with quiet():
        res = m(scen, *st["span"], silent=1, **_parse_options(options))
    st["scenarios"][scenario] = {"upd": updtext, "df": res}
    head = (f"Solved {scenario!r} on {mname}. Changed inputs: {', '.join(changed[:20]) or 'none'}"
            + (" ..." if len(changed) > 20 else ""))
    return "\n".join([head, *warnings, "",
                      _table(st, _default_vars(m), "difpctlevel", [scenario], "")])


def _table(st, names, show, scenarios, periods):
    m, baseline, per = st["m"], st["baseline"], st["per"]
    names = [n for n in names if n in baseline.columns]
    if not names:
        raise ToolError("None of the variables are in the model.")
    rows = _pick_periods(per, periods)
    if not rows:
        raise ToolError(f"None of the periods {periods!r} are in the solve period {per[0]}-{per[-1]}.")
    note = ""
    if periods and len(rows) < len(periods.replace(",", " ").split()):
        note = f"(periods outside {per[0]}-{per[-1]} are left out)\n"
    frames = {}
    if show == "level":
        frames["Baseline"] = baseline.loc[rows, names]
    for s in scenarios:
        res = st["scenarios"][s]["df"]
        if show == "level":
            df = res.loc[rows, names]
        elif show == "dif":
            df = res.loc[rows, names] - baseline.loc[rows, names]
        elif show == "growth":
            df = (res.loc[:, names].pct_change() * 100).loc[rows]
        else:
            df = (res.loc[rows, names] / baseline.loc[rows, names] - 1) * 100
        frames[s] = df
    import pandas as pd
    out = pd.concat(frames, axis=1)
    out.columns.names = ["scenario", "variable"]
    out = out.swaplevel(axis=1).sort_index(axis=1, level=0, sort_remaining=False)
    unit = {"level": "levels", "dif": "scenario minus baseline",
            "growth": "growth in percent", "difpctlevel": "percent difference from baseline"}[show]
    with pd.option_context("display.float_format", "{:,.3f}".format, "display.width", 250,
                           "display.max_columns", 60):
        body = out.T.to_string() if len(out.columns) > len(out) else out.to_string()
    desc = _descriptions(m, names)
    return f"{unit}\n{desc}\n\n{note}{body}" if desc else f"{unit}\n\n{note}{body}"


@tool
def show_results(variables: str = "", show: str = "difpctlevel", scenarios: str = "",
                 periods: str = "", model: str = "") -> str:
    """Table of results. variables: names or patterns (default the headline variables).
    show: 'difpctlevel' (percent of baseline, default), 'dif' (scenario minus baseline),
    'level' (also shows the baseline) or 'growth'. scenarios: comma-separated names
    (default all). periods: e.g. '2025 2030 2040' (default about 8 periods across the span)."""
    _, st = _get(model)
    m = st["m"]
    if show not in ("difpctlevel", "dif", "level", "growth"):
        raise ToolError("show must be difpctlevel, dif, level or growth.")
    if scenarios:
        chosen = [s.strip() for s in scenarios.split(",") if s.strip()]
        unknown = [s for s in chosen if s not in st["scenarios"]]
        if unknown:
            raise ToolError(f"Unknown scenarios {unknown}. Run so far: {list(st['scenarios'])}.")
    else:
        chosen = list(st["scenarios"])
    if not chosen and show != "level":
        raise ToolError("No scenarios run yet. Use run_scenario, or show='level' for the baseline.")
    with quiet():
        names = m.vlist(variables) if variables else _default_vars(m)
    return _table(st, names, show, chosen, periods)


if __name__ == "__main__":
    mcp.run()
