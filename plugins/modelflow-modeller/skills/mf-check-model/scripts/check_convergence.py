# -*- coding: utf-8 -*-
"""
Find where a ModelFlow model fails to converge: dump every core variable's iterations.

    python check_convergence.py <model> [--data file.csv|file.xlsx] [--upd "<2025 2050> X = 30; ..."]
                                [--start 2020 --end 2030] [--period 2025] [--solver sim]
                                [--opt key=value ...] [--last 10] [--top 15]
                                [--plot iterations.png] [--csv dump.csv]
                                [--modelflow <folder with modelclass.py>]

The model is solved over the span (default: the span saved in the model) on its
data, after the optional --upd lines (separated by ';') are applied.  The first
period that does not converge is then solved again on its own, starting from the
same values, with every core variable dumped (ldumpvar=True, dumpvar='*').
--period skips the search.  When every period converges, the period that took
the most iterations is analysed instead.

The variables are ranked by how much they still move over the last --last
iterations, relative to their starting level.  For each the report shows the
number of sign changes in the steps (oscillation), whether the steps grow or
shrink, for growing steps the onset (the iteration from which the step stays
above 0.1 % of the level), its position in the solve order, and its
current-period inputs from the core (top-ranked ones marked *) - the loop that
carries the instability.  In a diverging solve the variable that takes off first
is where to start.

A solve that stops with an error (LOG of a negative number, division by zero)
is analysed the same way: the period comes from the solver and the dump runs up
to the failing iteration.  With ModelFlow 2.92 or older only the legacy sim keeps
the dump when a solve raises; newer versions keep it for sim_ng too.

Only the simultaneous core is dumped.  Gauss-Seidel (sim, sim_ng) dumps the whole
core; newton_fbmin_ng only the feedback set, so it is not the default here.
"""
import argparse
import contextlib
import io
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_model import import_modelflow, label, load, section  # noqa: E402


ONSET = 1e-3      # a step above this share of the starting level counts as taking off


def parse_opts(pairs):
    opts = {}
    for kv in pairs:
        k, v = kv.split("=", 1)
        try:
            opts[k] = eval(v, {})
        except Exception:
            opts[k] = v
    return opts


def solve_captured(m, df, start, end, **kw):
    """Solve and return (result, printed text, error); the solver reports convergence by
    printing.  When the solve raises, result is None and the text printed so far is kept."""
    buf, res, err = io.StringIO(), None, None
    try:
        with contextlib.redirect_stdout(buf):
            res = m(df, start, end, silent=0, **kw)
    except Exception as e:
        err = e
    return res, buf.getvalue(), err


def solve_dump(m, df, per, **kw):
    """Solve one period with every core variable dumped.

    Returns (iterations frame, printed text, error or None).  When the solve raises,
    the error handler (errfunk) has already put the iterations so far in m.dumpdf
    (for the ng solvers only in ModelFlow newer than 2.92).
    """
    buf, err = io.StringIO(), None
    m.dumpdf = None                          # so a dump from an earlier solve is not read
    try:
        with contextlib.redirect_stdout(buf):
            m(df, per, per, silent=0, ldumpvar=True, dumpvar="*", **kw)
    except Exception as e:
        err = e
    dump = m.dumpdf
    if dump is None:
        return None, buf.getvalue(), err
    it = dump[dump["per"] == per].set_index("iteration").drop(columns=["per", "fair"], errors="ignore")
    return it.replace([np.inf, -np.inf], np.nan), buf.getvalue(), err


def as_period(text, index):
    """A period printed by the solver as an index label, or None."""
    for p in index:
        if str(p) == text:
            return p
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("model")
    ap.add_argument("--data")
    ap.add_argument("--upd", help="upd lines applied to the data before solving, separated by ';'")
    ap.add_argument("--start")
    ap.add_argument("--end")
    ap.add_argument("--period", help="the period to analyse (skip the search)")
    ap.add_argument("--solver", default="sim", help="default sim; sim_ng also dumps the whole core")
    ap.add_argument("--opt", nargs="*", default=[], help="solve options key=value, e.g. alfa=0.5 max_iterations=100")
    ap.add_argument("--last", type=int, default=10, help="iterations looked at for still-moving variables")
    ap.add_argument("--top", type=int, default=15, help="variables shown")
    ap.add_argument("--plot", help="save show_iterations of the top 6 variables to this file")
    ap.add_argument("--csv", help="save the dump of the analysed period")
    ap.add_argument("--modelflow", help="folder with modelclass.py, if modelflow is not installed")
    a = ap.parse_args()

    model = import_modelflow(a.modelflow)
    m, df = load(model, a.model, a.data)
    if df is None:
        sys.exit("No data: pass --data for text and markdown models.")
    if a.upd:
        df = df.upd("\n".join(line.strip() for line in a.upd.split(";")))
    if m.istopo:
        sys.exit(f"{m.name} is recursive (no simultaneous core): nothing to iterate.")

    start, end = label(a.start, df), label(a.end, df)
    saved = list(getattr(m, "current_per", []))
    if start is None:
        start = saved[0] if saved else df.index[0]
    if end is None:
        end = saved[-1] if saved else df.index[-1]
    opts = {"solver": a.solver, **parse_opts(a.opt)}
    opts.pop("ldumpvar", None), opts.pop("dumpvar", None)

    # 1. solve the span, read the solver's own verdict per period
    _, log, error = solve_captured(m, df, start, end, **opts)
    printed = re.findall(r"^(\S+) (?:not converged|NaN or inf)", log, re.M)
    failed = sorted({p for p in (as_period(t, df.index) for t in printed) if p is not None},
                    key=df.index.get_loc)
    stopped = getattr(m, "periode", None) if error is not None else None
    if stopped is not None and stopped in df.index and stopped not in failed:
        failed.append(stopped)              # the period the solve stopped in
    iterations = {as_period(p, df.index): int(n) for p, n in re.findall(r"^(\S+) Solved in (\d+) iterations", log, re.M)}
    nan_lines = [line for line in log.splitlines() if "NaN or inf" in line]

    section(f"{m.name}: solving {start} to {end} with {a.solver}")
    used = {k: v for k, v in getattr(m, "oldkwargs", {}).items() if k in ("alfa", "max_iterations", "relconv", "absconv")}
    if used:
        print(f"Options in use          : {used}")
    print(f"Core variables          : {len(m.coreorder)}")
    if error is not None:
        print(f"Solve stopped           : {type(error).__name__}: {error}"
              + (f" in {stopped}" if stopped is not None else " (period unknown, give --period)"))
    if failed:
        print(f"Not converged           : {len(failed)} periods, first {failed[0]}: "
              + " ".join(str(p) for p in failed[:12]) + (" ..." if len(failed) > 12 else ""))
    else:
        print("Not converged           : none")
    if iterations:
        it_s = pd.Series(iterations)
        print(f"Iterations per period   : min {it_s.min()}, max {it_s.max()} ({it_s.idxmax()}), mean {it_s.mean():.0f}")
    for line in nan_lines[:5]:
        print(f"NaN                     : {line.strip()}")

    # 2. the period to analyse
    if a.period:
        per = label(a.period, df)
        why = "requested"
    elif failed:
        per = failed[0]
        why = "the solve stopped here" if per == stopped else "first period not converged"
    elif iterations:
        per, why = max(iterations, key=iterations.get), "all converged; the slowest period"
    else:
        per, why = end, "no convergence messages; the last period"
    if per not in df.index:
        sys.exit(f"Period {per} is not in the data.")

    # earlier periods solved again, this period and later as in the input
    inp = df.copy()
    pos, first = df.index.get_loc(per), df.index.get_loc(start)
    if pos > first:
        prev, _, err0 = solve_captured(m, df, start, df.index[pos - 1], **opts)
        if prev is None:
            sys.exit(f"Solving {start} to {df.index[pos - 1]} raised {err0}; analyse an earlier --period.")
        before = df.index[:pos]
        inp.loc[before, prev.columns] = prev.loc[before, prev.columns]
    it, log1, err1 = solve_dump(m, inp, per, **opts)
    if it is None or it.shape[1] == 0 or len(it) < 3:
        n = 0 if it is None else len(it)
        sys.exit(f"Too few iterations dumped in {per} to analyse ({n})"
                 + (f"; the solve raised {err1}" if err1 is not None else "") + "."
                 + (" ModelFlow 2.92 and older keep the dump after an error only with --solver sim."
                    if it is None and err1 is not None and a.solver != "sim" else ""))

    # 3. rank the variables that still move, on the iterations before any value turns NaN/inf
    finite = it.notna().all(axis=1)
    nan_from = None if finite.all() else finite.idxmin()     # first iteration with a NaN/inf
    if nan_from is not None:
        it = it.loc[:nan_from].iloc[:-1]
        if len(it) < 3:
            sys.exit(f"Values in {per} are NaN/inf from iteration {nan_from}: too few iterations before to analyse.")
    last = min(a.last, len(it) - 1)
    steps = it.diff().iloc[1:]
    tail = steps.iloc[-last:]
    start_level, end_level = it.iloc[0].abs(), it.iloc[-1].abs()
    level = start_level.where(start_level > 1e-12, end_level)       # a diverging end level would hide the step
    rel_step = (tail.abs() / level.where(level > 1e-12)).max()
    flips = (np.sign(tail).diff().abs() > 0).sum()
    first_abs, last_abs = tail.abs().iloc[0], tail.abs().iloc[-1]
    trend = last_abs / first_abs.where(first_abs > 0)
    corepos = pd.Series({v: i for i, v in enumerate(m.coreorder)})
    # onset: the iteration from which the step stays above ONSET of the starting level
    rel_all = steps.abs().div(level.where(level > 1e-12))
    onset = rel_all.apply(lambda c: (c[c < ONSET].index.max() + 1) if (c < ONSET).any() else c.index[0])
    rank = pd.DataFrame({"rel_step": rel_step, "sign_flips": flips, "step_trend": trend,
                         "onset": onset, "core_pos": corepos}).dropna(subset=["rel_step"])
    rank = rank.sort_values("rel_step", ascending=False)
    top = rank.head(a.top)

    def kind(r):
        oscillating, growing = r.sign_flips >= max(2, last // 2), r.step_trend > 1.05
        if oscillating:
            return "growing oscillation" if growing else "oscillating"
        return "growing" if growing else "slow"

    section(f"Iterations in {per} ({why}): {len(it) - 1} iterations, {it.shape[1]} variables dumped")
    verdict = re.search(rf"^{re.escape(str(per))} (not converged.*|Solved in \d+ iterations)", log1, re.M)
    if verdict:
        print(f"Solver                  : {verdict.group(0)}")
    if err1 is not None:
        print(f"Solver                  : stopped after {len(it) - 1} iterations: {type(err1).__name__}: {err1}")
    if nan_from is not None:
        print(f"NaN/inf                 : from iteration {nan_from}; the iterations before it are analysed")
    print(f"Looked at               : the last {last} iterations; rel_step = largest step / starting level\n")
    desc = getattr(m, "var_description", {})
    topset, coreset = set(top.index), set(m.coreorder)
    rows = []
    for v, r in top.iterrows():
        inputs = {t.var for t in m.allvar[v]["terms"] if t.var and t.var != v and t.lag == ""} & coreset
        uses = [f"*{w}" for w in sorted(inputs & topset)] + sorted(inputs - topset)
        rows.append({"variable": v, "rel_step": f"{r.rel_step:.2e}", "flips": int(r.sign_flips),
                     "trend": "" if pd.isna(r.step_trend) else f"{r.step_trend:.2f}", "type": kind(r),
                     "onset": "" if pd.isna(r.onset) or r.step_trend <= 1.05 else int(r.onset),
                     "core_pos": int(r.core_pos), "core inputs, current period (* = in this list)": " ".join(uses[:5]) + (" ..." if len(uses) > 5 else "")})
    with pd.option_context("display.width", 250, "display.max_colwidth", 80):
        print(pd.DataFrame(rows).set_index("variable").to_string())

    # 4. where to start
    kinds = [kind(r) for _, r in top.head(5).iterrows()]
    growing_top = top.head(10)[top.head(10).step_trend > 1.05]
    if len(growing_top):                    # diverging: the one whose steps took off first
        origin = growing_top.sort_values(["onset", "core_pos"]).index[0]
        origin_why = (f"the first of the top 10 to take off: steps above {ONSET:.1%} of its level "
                      f"from iteration {int(growing_top.loc[origin, 'onset'])}")
    else:
        origin = top.head(5).sort_values("core_pos").index[0]
        origin_why = "earliest in solve order among the top 5"
    section("Reading")
    if "growing oscillation" in kinds:
        print("Steps change sign and grow: the iteration oscillates and diverges. Lower alfa (damping) "
              "or use newton_fbmin_ng; if that does not help, look for an equation that over-reacts "
              "to a current-period variable in the loop.")
    elif "growing" in kinds or err1 is not None or nan_from is not None:
        print("Steps are growing: the iteration diverges. Usually an equation or data problem "
              "(a coefficient above 1 in a current-period loop, a small denominator), not a solver setting.")
    elif "oscillating" in kinds:
        print("Steps change sign: the iteration oscillates. Damp the oscillating equations "
              "(alfa < 1 with <DAMP>) or use newton_fbmin_ng.")
    else:
        print("Steps shrink without changing sign: slow, monotone convergence. Raise max_iterations "
              "or use newton_fbmin_ng.")
    print(f"Start with {origin} - {desc.get(origin, '')}")
    print(f"  ({origin_why})")
    print(f"  {m.allvar[origin]['frml']}")
    print(f"Draw the loop: <model>.{origin}.tracepre(up=2)")

    if a.csv:
        it.to_csv(a.csv)
        print(f"\nDump written to {a.csv}")
    if a.plot:
        import matplotlib
        matplotlib.use("Agg")
        fig = m.show_iterations(" ".join(top.index[:6]), per=per, change=True)
        if fig is not None:
            fig.savefig(a.plot, dpi=80)
            print(f"Plot written to {a.plot}")


if __name__ == "__main__":
    main()
