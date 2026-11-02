# -*- coding: utf-8 -*-
"""
Run one or more scenarios on a ModelFlow model file and print the results.

    python run_scenario.py <model.pcim> --scenario "Carbon tax=<2025 2050> PAKGGREVCO2CER = 30"
                           [--scenario "name=upd text" ...] [--start 2025 --end 2050]
                           [--vars "PAKNYGDPMKTPKN PAKNECONPRVTKN"] [--show difpctlevel]
                           [--periods 2025 2030 2040] [--csv results.csv]
                           [--modelflow <folder with modelclass.py>] [--opt key=value ...]

Each --scenario is "name=upd text"; several upd lines are separated by ';'.
The baseline is the model's saved data solved over the same span.  --show is
level, dif (scenario minus baseline), difpctlevel (percent of baseline, the
default) or growth.  --vars accepts ModelFlow patterns (wildcards, #group,
!description); the default is the #Headline group or, without it, the first
ten endogenous variables.
"""
import argparse
import sys
from pathlib import Path

import pandas as pd


def import_model(folder):
    if folder:
        sys.path.insert(0, str(Path(folder).resolve()))
    elif (Path.cwd() / "modelclass.py").exists():
        sys.path.insert(0, str(Path.cwd()))
    try:
        from modelclass import model
        return model
    except ImportError as e:
        sys.exit(f"Can not import modelclass ({e}). Install modelflow or pass --modelflow <folder>.")


def label(x, index):
    if x is None:
        return None
    return int(x) if pd.api.types.is_integer_dtype(index.dtype) else x


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("model")
    ap.add_argument("--scenario", action="append", required=True, help='"name=upd text", repeatable')
    ap.add_argument("--start")
    ap.add_argument("--end")
    ap.add_argument("--vars")
    ap.add_argument("--show", default="difpctlevel", choices=["level", "dif", "difpctlevel", "growth"])
    ap.add_argument("--periods", nargs="*")
    ap.add_argument("--csv")
    ap.add_argument("--modelflow")
    ap.add_argument("--opt", nargs="*", default=[], help="solve options key=value, e.g. alfa=0.5 solver=newton_fbmin_ng")
    a = ap.parse_args()

    model = import_model(a.modelflow)
    m, base = model.modelload(a.model, run=0)
    start, end = label(a.start, base.index), label(a.end, base.index)
    span = [start, end] if start is not None and end is not None else []
    opts = {}
    for kv in a.opt:
        k, v = kv.split("=", 1)
        try:
            opts[k] = eval(v, {})
        except Exception:
            opts[k] = v

    baseline = m(base, *span, silent=1, keep="Baseline", **opts)
    per = m.current_per

    if a.vars:
        names = m.vlist(a.vars)
    elif "Headline" in getattr(m, "var_groups", {}):
        names = m.vlist("#Headline")
    else:
        names = sorted(m.endogene)[:10]

    results = {}
    for i, spec in enumerate(a.scenario, 1):
        if spec.lstrip().startswith("<"):            # no name given
            name, text = f"Scenario {i}", spec
        else:
            name, text = spec.split("=", 1)
        updtext = "\n".join(line.strip() for line in text.split(";"))
        scen = base.upd(updtext)
        changed = [c for c in scen.columns if c in base.columns and not scen[c].equals(base[c])]
        new = [c for c in scen.columns if c not in base.columns]
        if new:
            print(f"Warning: {name}: new columns created by upd (misspelled?): {', '.join(new)}")
        if not changed and not new:
            print(f"Warning: {name}: upd changed nothing")
        results[name.strip()] = m(scen, *span, silent=1, keep=name.strip(), **opts)

    frames = {}
    for name, res in results.items():
        if a.show == "level":
            df = res.loc[per, names]
        elif a.show == "dif":
            df = res.loc[per, names] - baseline.loc[per, names]
        elif a.show == "growth":
            df = res.loc[:, names].pct_change().loc[per] * 100
        else:
            df = (res.loc[per, names] / baseline.loc[per, names] - 1) * 100
        frames[name] = df
    out = pd.concat(frames, axis=1)
    out.columns.names = ["scenario", "variable"]
    if a.periods:
        keep = [label(p, out.index) for p in a.periods]
        out = out.loc[[p for p in keep if p in out.index]]

    desc = getattr(m, "var_description", {})
    print(f"\n{m.name}: {a.show} over {per[0]}-{per[-1]}")
    for v in names:
        if desc.get(v, v) != v:
            print(f"  {v:<20} {desc[v]}")
    with pd.option_context("display.float_format", "{:,.3f}".format, "display.width", 200,
                           "display.max_columns", 50):
        print(out.T.to_string() if len(out) > len(out.columns) else out.to_string())
    if a.csv:
        out.to_csv(a.csv)
        print(f"\nWritten to {a.csv}")


if __name__ == "__main__":
    main()
