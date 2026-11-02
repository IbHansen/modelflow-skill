# -*- coding: utf-8 -*-
"""
Structure and data report for a ModelFlow model.

    python check_model.py <model> [--data file.csv|file.xlsx] [--start 2020 --end 2030]
                          [--test] [--modelflow <folder with modelclass.py>]

<model> is a .pcim file (equations and data, loaded with model.modelload), a
text file with FRML statements (.frm, .txt, one equation per line also works)
or a markdown model (.md, built with Makemodel).  --data supplies the
dataframe for text and markdown models (index = periods, columns = variables).

Prints the size and shape of the model, its block structure, the equation
options in use, likely mistakes in the equations, and - when data is
available - variables missing from the data, NaN values in the solve span and
the solver ModelFlow will choose.  --test also runs model.test_model on the
data: every equation evaluated once on history, to show equations that do not
reproduce the data.
"""
import argparse
import sys
from collections import Counter
from pathlib import Path

import pandas as pd


def import_modelflow(folder):
    if folder:
        sys.path.insert(0, str(Path(folder).resolve()))
    elif (Path.cwd() / "modelclass.py").exists():
        sys.path.insert(0, str(Path.cwd()))     # run from a modelflow source folder
    try:
        from modelclass import model  # noqa: F401
        return model
    except ImportError as e:
        sys.exit(f"Can not import modelclass ({e}). Install modelflow or pass --modelflow <folder>.")


def read_data(path):
    p = Path(path)
    if p.suffix.lower() in (".xlsx", ".xls"):
        df = pd.read_excel(p, index_col=0)
    else:
        df = pd.read_csv(p, index_col=0)
    df.columns = [str(c).upper() for c in df.columns]
    return df


def load(model, path, datapath):
    p = Path(path)
    df = read_data(datapath) if datapath else None
    if p.suffix.lower() == ".pcim":
        m, saved = model.modelload(str(p), run=0)
        return m, (df if df is not None else saved)
    text = p.read_text(encoding="utf-8")
    if p.suffix.lower() == ".md":
        from modelconstruct_estimation import Makemodel
        mm = Makemodel(text, input_df=df) if df is not None else Makemodel(text)
        return mm.mmodel, df
    return model(text, modelname=p.stem), df


def section(title):
    print(f"\n{title}\n{'-' * len(title)}")


def names(items, n=12):
    items = sorted(items)
    return ", ".join(items[:n]) + (f" ... (+{len(items) - n})" if len(items) > n else "")


def default_solver(m):
    """The solver Solver_Mixin.__call__ picks when no solver= is given."""
    if m.maxlead >= 1:
        guess = "newtonstack" if m.normalized else "newtonstack_ng" if m.hybrid else "newtonstack_un_normalized"
    elif m.normalized:
        guess = "xgenr" if m.istopo else "sim"
    else:
        guess = "newton_ng" if m.hybrid else "newton_un_normalized"
    if getattr(m, "ng", False) or getattr(m, "fixed_periods", None):
        guess = {"xgenr": "xgenr_ng", "sim": "sim_ng", "newtonstack": "newtonstack_ng",
                 "newtonstack_un_normalized": "newtonstack_ng",
                 "newton_un_normalized": "newton_ng"}.get(guess, guess)
    return guess


def label(x, df):
    """A --start/--end value as an index label (an int for an integer index)."""
    if x is None:
        return None
    return int(x) if pd.api.types.is_integer_dtype(df.index.dtype) else x


def options_of(frmlname):
    inner = frmlname[frmlname.find("<") + 1: frmlname.rfind(">")] if "<" in frmlname else ""
    return [o.split("=", 1)[0].strip().upper() for o in inner.split(",") if o.strip()]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("model")
    ap.add_argument("--data")
    ap.add_argument("--start")
    ap.add_argument("--end")
    ap.add_argument("--test", action="store_true", help="run model.test_model on the data")
    ap.add_argument("--modelflow", help="folder with modelclass.py, if modelflow is not installed")
    a = ap.parse_args()

    model = import_modelflow(a.modelflow)
    m, df = load(model, a.model, a.data)
    endo, exo = set(m.endogene), set(m.exogene)

    section(f"Model {m.name}")
    res = [v for v in endo if v.endswith("___RES")]
    form = "normalized" if m.normalized else "implicit (all ___RES)" if m.implicit else "hybrid (normalized and ___RES)"
    print(f"Equations (endogenous)  : {len(endo):,}")
    print(f"Exogenous variables     : {len(exo):,}")
    print(f"Form                    : {form}" + (f", {len(res)} residual equations" if res else ""))
    print(f"Max lag / max lead      : {m.maxlag} / {m.maxlead}")
    if getattr(m, "fixed_periods", None):
        print(f"Fixed-period references : {', '.join(f'{v}({p})' for v, p in m.fixed_terms[:8])}")
    print(f"Simultaneous            : {'no (recursive)' if m.istopo else 'yes'}")

    section("Structure")
    if not m.istopo:
        core = m.coreorder
        blocks = [b for b in getattr(m, "_corestrongblock", []) if len(b)]
        sizes = sorted((len(b) for b in blocks), reverse=True)
        print(f"Prolog / core / epilog  : {len(m.preorder):,} / {len(core):,} / {len(m.epiorder):,}")
        print(f"Simultaneous blocks     : {len(blocks)}, sizes {sizes[:8]}{' ...' if len(sizes) > 8 else ''}")
        print(f"Feedback set (fblist)   : {len(m.fblist)} variables: {names(m.fblist, 8)}")
    else:
        print("Recursive: one pass in solve order, no iteration.")

    section("Equation options")
    opts = Counter(o for v in endo for o in options_of(m.allvar[v]["frmlname"]))
    print("Options used            : " + (", ".join(f"{k} {n}" for k, n in opts.most_common()) or "none"))
    fixable = sorted(getattr(m, "fix_endo", []))
    adds = sorted(v for v in exo if v.endswith("_A") and v[:-2] in endo)
    print(f"Fixable (_X/_D)         : {len(fixable):,}")
    print(f"With add factor (_A)    : {len(adds):,}")
    if getattr(m, "split_calc_add_factor", False):
        print("Add-factor model        : yes (CALC_ADD_FACTOR equations; run after a solve with fixed variables)")

    section("Possible problems")
    problems = 0
    zdamp = [v for v in endo if "Z" in m.allvar[v]["frmlname"].upper()
             and "DAMP" not in m.allvar[v]["frmlname"].upper()]
    if zdamp:
        problems += 1
        print(f"FRML name contains Z    : {len(zdamp)} equations are damped by the solver because their "
              f"FRML name contains the letter Z: {names(zdamp, 6)}")
    dropped = [v for v in m.allvar if m.allvar[v].get("dropfrml")]
    if dropped:
        problems += 1
        print(f"Extra LHS variables     : {names(dropped, 8)} (several variables left of =; only the first is solved)")
    if df is not None:
        missing = sorted(v for v in m.allvar if v not in df.columns)
        companion = lambda v: v[-2:] in ("_A", "_X", "_D") and v[:-2] in endo
        missing_exo = [v for v in missing if v in exo and not companion(v)]
        missing_comp = [v for v in missing if v in exo and companion(v)]
        if missing_exo:
            problems += 1
            print(f"Exogenous not in data   : {len(missing_exo)} - set to 0.0 when solving: {names(missing_exo)}")
        if missing_comp:
            print(f"Companions not in data  : {len(missing_comp)} _A/_X/_D variables, set to 0.0 (no adjustment, not fixed) - usually fine")
        start, end = label(a.start, df), label(a.end, df)
        if start is not None or end is not None:
            per = df.loc[start if start is not None else df.index[0]:
                         end if end is not None else df.index[-1]].index
        else:
            per = df.index[-m.maxlag if m.maxlag else 0:]
        span = df.loc[per, [v for v in sorted(exo) if v in df.columns]]
        nan_exo = [c for c in span.columns if span[c].isna().any()]
        if nan_exo:
            problems += 1
            print(f"NaN in exogenous        : {len(nan_exo)} in {per[0]}-{per[-1]}: {names(nan_exo)}")
        span_endo = df.loc[per, [v for v in sorted(endo) if v in df.columns]]
        nan_endo = [c for c in span_endo.columns if span_endo[c].isna().any()]
        if nan_endo:
            problems += 1
            print(f"NaN in endogenous       : {len(nan_endo)} in {per[0]}-{per[-1]} (starting values and lags): {names(nan_endo)}")
        if len(per) and m.maxlag:
            first = df.index.get_loc(per[0])
            lagrows = df.iloc[max(0, first + m.maxlag): first]
            lagged = [v for v in sorted(m.allvar) if v in lagrows.columns and lagrows[v].isna().any()]
            if lagged:
                problems += 1
                print(f"NaN in lag periods      : {len(lagged)} variables before {per[0]}: {names(lagged)}")
    if not problems:
        print("None found.")

    if df is not None:
        section("Solving")
        print(f"Data                    : {df.index[0]} to {df.index[-1]}, {df.shape[1]:,} columns")
        print(f"Default solver          : {default_solver(m)}")
        saved = {k: v for k, v in getattr(m, "oldkwargs", {}).items()}
        if saved:
            print(f"Saved solve options     : {saved}")

    if a.test:
        if df is None:
            print("\n--test needs data")
        else:
            section("test_model: equations evaluated once on the data")
            kw = {k: label(v, df) for k, v in (("start", a.start), ("end", a.end)) if v}
            if not kw and len(getattr(m, "current_per", [])):
                # the saved solve span; early data periods often lack the lags the equations need
                kw = {"start": m.current_per[0], "end": m.current_per[-1]}
                print(f"Span: {kw['start']} to {kw['end']} (saved in the model; --start/--end to change)")
            try:
                m.test_model(df, **kw)
            except Exception as e:
                print(f"\ntest_model stopped: {type(e).__name__}: {e}")
                print("The message above names the equation and period. If the period is before the "
                      "data has history for its lags, rerun with a later --start.")


if __name__ == "__main__":
    main()
