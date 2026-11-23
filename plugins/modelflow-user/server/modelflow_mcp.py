# -*- coding: utf-8 -*-
"""
ModelFlow MCP server for the modelflow-user plugin.

start.cmd runs this file with the python of the selected conda environment:
the full path stored in ~/.modelflow_mcp_env by select_environment, or the
Miniforge environment 'modelflow' when nothing is selected.

Loaded models stay in memory between tool calls. Scenarios are kept the
standard ModelFlow way, in model.keep_solutions (solve with keep='name'), and
tables, charts, attribution and reports come from ModelFlow's own methods
(model.table, model.plot, model.get_att, model.reports) through the
modelinspect module, which the JupyterLab Model Workbench uses too.
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
        "as ModelFlow upd text and kept in model.keep_solutions; the baseline is kept "
        "as 'Baseline'. Tables, charts, attribution and reports are made with ModelFlow's "
        "own model.table, model.plot, model.get_att and model.reports, and every result "
        "ends with the notebook code that gives the same output - reuse it when writing "
        "notebooks. If a tool says ModelFlow can not be imported, use "
        "list_environments and select_environment."
    ),
)

_models = {}        # name -> {"m", "base", "span", "upd": {scenario: upd text}}
BASELINE = "Baseline"
OUT_DIR = "modelflow_output"
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
        try:
            import modelinspect  # noqa: F401
        except ImportError:
            raise ToolError(
                f"ModelFlow in {sys.prefix} is too old for this server (no modelinspect module).\n"
                f'Update it with:  conda update -p "{sys.prefix}" -c ibh -c conda-forge modelflow'
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

def _mi():
    _modelclass()
    import modelinspect
    return modelinspect


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


def _default_pat(m):
    if "Headline" in getattr(m, "var_groups", {}):
        return "#Headline"
    return " ".join(sorted(m.endogene)[:10])


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


def _names(text):
    return [s.strip() for s in text.replace("|", ",").split(",") if s.strip()]


def _scenarios(m, scenarios, reference, datatype):
    """The keepswitch selector for model.table/model.plot. Impact datatypes
    (dif*) compare with the first selected scenario, so the reference goes first."""
    kept = list(m.keep_solutions)
    chosen = _names(scenarios) if scenarios else [k for k in kept if k != reference]
    unknown = [s for s in chosen + [reference] if s not in kept]
    if unknown:
        raise ToolError(f"Unknown scenarios {unknown}. Kept solutions: {kept}.")
    if datatype.startswith("dif") or datatype.startswith("base"):
        if not chosen:
            raise ToolError("No scenarios run yet. Use run_scenario, or a level/growth datatype "
                            "for the baseline.")
        chosen = [reference] + [s for s in chosen if s != reference]
    elif not chosen:
        chosen = [reference]
    return "|".join(chosen)


def _code(call):
    return f"\n\nNotebook code: {call}"


DATATYPES = ("growth difgrowth level diflevel difpctlevel gdppct difgdppct qoq_ar difqoq_ar "
             "baselevel basegrowth basegdppct baseqoq_ar").split()


def _datatype(show):
    show = {"dif": "diflevel"}.get(show, show)          # name used by earlier versions
    if show not in DATATYPES:
        raise ToolError(f"datatype must be one of {', '.join(DATATYPES)}.")
    return show


def _out_dir(out_dir, *sub):
    d = Path(out_dir or OUT_DIR).resolve().joinpath(*sub)
    d.mkdir(parents=True, exist_ok=True)
    return d


@tool
def load_model(path: str, name: str = "", start: str = "", end: str = "") -> str:
    """Load a ModelFlow model from a .pcim file (path or URL; a bare name like 'pak' is also
    looked up in the ModelFlow model repository) and solve the baseline, kept as 'Baseline'.
    start/end set the solve period for this model's baseline and scenarios; default is the
    period saved with the model."""
    model = _modelclass()
    with quiet():
        m, base = model.modelload(path, run=0)
        span = [_label(start, base.index), _label(end, base.index)]
        if None in span:
            span = []
        m(base, *span, silent=1, keep=BASELINE)
    name = name or Path(path).stem
    _models[name] = {"m": m, "base": base, "span": span, "upd": {}}
    per = m.current_per
    pat = _default_pat(m)
    head = m.vlist(pat)
    return (f"Loaded {name!r}: {len(m.endogene)} endogenous and {len(m.exogene)} exogenous "
            f"variables. Baseline solved {per[0]}-{per[-1]} and kept as {BASELINE!r}.\n"
            f"Headline variables ({pat}):\n{_descriptions(m, head) or '  ' + ' '.join(head)}"
            + _code(f"m, base = model.modelload({path!r}, run=0); "
                    f"res = m(base{''.join(', ' + repr(s) for s in span)}, keep={BASELINE!r})"))


@tool
def list_models() -> str:
    """List the loaded models, their kept solutions (scenarios) and stored reports."""
    if not _models:
        return "No model loaded."
    mi = _mi()
    out = []
    for name, st in _models.items():
        m = st["m"]
        per = m.current_per
        out.append(f"{name}: {per[0]}-{per[-1]}")
        for s in mi.scenario_names(m):
            upd = st["upd"].get(s)
            out.append(f"  {s}" + (f": {upd.replace(chr(10), '; ')}" if upd else ""))
        if mi.report_names(m):
            out.append(f"  reports: {', '.join(mi.report_names(m))}")
    return "\n".join(out)


@tool
def find_variables(pattern: str, model: str = "") -> str:
    """Find variables by name pattern (wildcards like *GDP*), by description ('!*consumption*')
    or by group ('#Headline'). Shows each variable's description and whether it is endogenous."""
    _, st = _get(model)
    try:
        with quiet():
            rows = _mi().var_rows(st["m"], pattern)
    except Exception as e:
        raise ToolError(f"No variables match {pattern!r} ({e}).")
    if not rows:
        return f"No variables match {pattern!r}."
    out = "\n".join(f"{r['name']:<22} {r['kind']:<4}  {r['desc']}" for r in rows[:MAX_ROWS])
    more = f"\n... and {len(rows) - MAX_ROWS} more" if len(rows) > MAX_ROWS else ""
    return out + more + _code(f"m.vlist({pattern!r})")


@tool
def explain_variable(variable: str, model: str = "") -> str:
    """Show a variable's description, whether it is exogenous, its equation and options,
    and the equations that use it."""
    _, st = _get(model)
    try:
        e = _mi().equation(st["m"], variable)
    except KeyError:
        raise ToolError(f"{variable.upper()} is not in the model. Use find_variables to search.")
    lines = [f"{e['var']}: {e['desc']}" if e["desc"] else e["var"]]
    if e["endo"]:
        lines += ["Endogenous.", f"Options:  {e['options']}", f"Equation: {e['frml']}"]
    else:
        lines.append("Exogenous: change it in a scenario with upd.")
    used = e["used_in"]
    if used:
        lines.append(f"Used in the equations for: {', '.join(used[:40])}"
                     + (f" and {len(used) - 40} more" if len(used) > 40 else ""))
    return "\n".join(lines) + _code(f"m.{e['var']}.show  (or m.print_eq({e['var']!r}))")


@tool
def dependencies(variable: str, up: int = 1, down: int = 1, model: str = "") -> str:
    """The dependency graph around a variable: its direct inputs, the variables that use it,
    and with up/down > 1 the links further out. Same graph as the Model Workbench panel and
    model.draw."""
    _, st = _get(model)
    mi = _mi()
    try:
        dep = mi.dependencies(st["m"], variable, up, down)
    except KeyError as e:
        raise ToolError(f"{e}. Use find_variables to search.")
    return mi.dependencies_text(dep) + _code(f"m.draw({dep['var']!r}, up={up}, down={down})")


@tool
def run_scenario(scenario: str, upd: str, model: str = "", options: str = "") -> str:
    """Run a scenario: apply ModelFlow upd text to the model's input data, solve, and keep
    the result in model.keep_solutions under the scenario name.
    upd lines look like '<2025 2030> PAKGGREVCO2CER = 30' or '<2025 2050> PAKNEGDIKSTKKN * 1.02';
    separate several lines with ';' or newlines. options are solve options such as
    'alfa=0.5 solver=newton'. Returns the headline table in percent of the baseline."""
    mname, st = _get(model)
    m, base = st["m"], st["base"]
    mi = _mi()
    if scenario == BASELINE:
        raise ToolError(f"{BASELINE!r} is the baseline; choose another scenario name.")
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
        m(scen, *st["span"], silent=1, keep=scenario, **_parse_options(options))
        st["upd"][scenario] = updtext
        sel = f"{BASELINE}|{scenario}"
        tab = mi.table(m, _default_pat(m), "difpctlevel", sel)
        body = mi.table_text(tab, _pick_periods(m.current_per, ""))
    head = (f"Solved {scenario!r} on {mname} and kept it. Changed inputs: "
            f"{', '.join(changed[:20]) or 'none'}" + (" ..." if len(changed) > 20 else ""))
    return "\n".join([head, *warnings, "", body]) + _code(
        f"res = m(base.upd({updtext!r}), keep={scenario!r}); "
        f"m.table({_default_pat(m)!r}, datatype='difpctlevel', scenarios={sel!r})")


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
def show_results(variables: str = "", datatype: str = "difpctlevel", scenarios: str = "",
                 reference: str = BASELINE, periods: str = "", title: str = "",
                 model: str = "") -> str:
    """Table of results made with model.table. variables: names, patterns or a group like
    '#Headline' (default the headline variables). datatype: growth, level, gdppct, qoq_ar
    (values), difgrowth, diflevel, difpctlevel, difgdppct, difqoq_ar (impact against the
    reference) or baselevel, basegrowth ... (the reference). scenarios: comma-separated kept
    solutions (default all). periods: e.g. '2025 2030 2040' (default about 8 across the span)."""
    _, st = _get(model)
    m = st["m"]
    mi = _mi()
    datatype = _datatype(datatype)
    pat = variables or _default_pat(m)
    sel = _scenarios(m, scenarios, reference, datatype)
    try:
        with quiet():
            tab = mi.table(m, pat, datatype, sel, **({"title": title} if title else {}))
    except Exception as e:
        raise ToolError(f"model.table failed: {e}")
    cols = _pick_periods(m.current_per, periods)
    if not cols:
        raise ToolError(f"None of the periods {periods!r} are in the solve period.")
    return mi.table_text(tab, cols) + _code(
        f"m.table({pat!r}, datatype={datatype!r}, scenarios={sel!r}"
        + (f", title={title!r}" if title else "") + ")")


@tool
def plot_results(variables: str = "", datatype: str = "difpctlevel", scenarios: str = "",
                 reference: str = BASELINE, title: str = "", start: str = "", end: str = "",
                 by_var: bool = True, out_dir: str = "", model: str = "") -> str:
    """Charts made with model.plot, saved as PNG files (one per variable, or one chart with
    a line per variable when by_var is false). Same variables, datatype and scenarios as
    show_results; start/end limit the periods. Returns the file paths - open them to see
    the charts."""
    _, st = _get(model)
    m = st["m"]
    mi = _mi()
    datatype = _datatype(datatype)
    pat = variables or _default_pat(m)
    sel = _scenarios(m, scenarios, reference, datatype)
    opts = {"by_var": by_var}
    if title:
        opts["title"] = title
    if start or end:
        per = m.current_per
        lo, hi = _label(start, per) or per[0], _label(end, per) or per[-1]
        opts["smpl"] = tuple(getattr(x, "item", lambda: x)() for x in (lo, hi))
    try:
        with quiet():
            p = mi.plot(m, pat, datatype, sel, **opts)
            paths = mi.save_figs(p.figs, _out_dir(out_dir, "charts"), prefix=f"{datatype}_")
    except Exception as e:
        raise ToolError(f"model.plot failed: {e}")
    import matplotlib.pyplot as plt
    plt.close("all")
    extra = "".join(f", {k}={v!r}" for k, v in opts.items() if k != "by_var" or not v)
    return "Saved:\n" + "\n".join(paths) + _code(
        f"m.plot({pat!r}, datatype={datatype!r}, scenarios={sel!r}{extra})")


@tool
def attribution(variable: str, scenario: str = "", reference: str = BASELINE, type: str = "pct",
                lag: bool = False, threshold: float = 0.5, periods: str = "",
                model: str = "") -> str:
    """Attribution with model.get_att: how much each input contributes to the difference in a
    variable between a scenario (default the last one run) and the reference. type 'pct'
    (share of the difference in percent), 'level' or 'growth'. lag true splits by lag.
    Rows below threshold are left out."""
    _, st = _get(model)
    m = st["m"]
    mi = _mi()
    kept = mi.scenario_names(m)
    scenario = scenario or next((s for s in reversed(kept) if s != reference), "")
    if not scenario:
        raise ToolError("No scenario run yet. Use run_scenario first.")
    try:
        with quiet():
            df = mi.attribution(m, variable, reference, scenario, type=type, lag=lag,
                                threshold=threshold)
    except KeyError as e:
        raise ToolError(str(e))
    except Exception as e:
        raise ToolError(f"Attribution failed: {e}")
    import pandas as pd
    cols = [c for c in _pick_periods(m.current_per, periods) if c in df.columns] or list(df.columns)
    with pd.option_context("display.float_format", "{:,.2f}".format, "display.width", 250,
                           "display.max_columns", 60, "display.max_rows", MAX_ROWS):
        body = df.loc[:, cols].to_string()
    v = variable.strip().upper()
    return (f"{v}: attribution ({type}) of {scenario!r} against {reference!r}\n\n{body}"
            + _code(f"import modelinspect\nwith modelinspect.compare(m, {reference!r}, {scenario!r}): "
                    f"m.get_att({v!r}, type={type!r}, lag={lag}, threshold={threshold})"))


@tool
def list_reports(model: str = "") -> str:
    """List the reports stored with the model (model.reports)."""
    _, st = _get(model)
    names = _mi().report_names(st["m"])
    return ("Stored reports: " + ", ".join(names)) if names else "No reports stored with the model."


@tool
def show_report(report: str, save_html: bool = True, out_dir: str = "", model: str = "") -> str:
    """Show a report: a name from list_reports or a report spec in JSON (as made by
    report.save_spec). Returns the tables as text and, with save_html, writes a
    self-contained HTML page with the tables and charts."""
    _, st = _get(model)
    m = st["m"]
    mi = _mi()
    try:
        with quiet():
            rep = mi.get_report(m, report)
            text = mi.report_text(rep)
            page = mi.report_html(rep) if save_html else ""
    except KeyError as e:
        raise ToolError(str(e))
    except Exception as e:
        raise ToolError(f"The report failed: {e}")
    import matplotlib.pyplot as plt
    plt.close("all")
    out = text
    if save_html:
        name = (report.strip() if not report.strip().startswith("{")
                else getattr(rep, "name", "") or "report")
        path = _out_dir(out_dir) / f"{name}.html"
        path.write_text(page, encoding="utf-8")
        out += f"\n\nSaved HTML: {path}"
    call = (f"m.get_report({report!r})" if not report.strip().startswith("{")
            else "m.report_from_spec(spec)")
    return out + _code(call)


@tool
def save_report(name: str, spec: str, model: str = "") -> str:
    """Store a report with the model (model.reports) from a JSON spec, after checking that it
    builds. Stored reports are saved with the model by modeldump."""
    _, st = _get(model)
    m = st["m"]
    try:
        with quiet():
            m.report_from_spec(spec)
    except Exception as e:
        raise ToolError(f"The spec does not build a report: {e}")
    m.reports = (getattr(m, "reports", {}) or {}) | {name: spec}
    return f"Stored report {name!r}." + _code(f"m.add_report(report.set_name({name!r}))")


if __name__ == "__main__":
    mcp.run()
