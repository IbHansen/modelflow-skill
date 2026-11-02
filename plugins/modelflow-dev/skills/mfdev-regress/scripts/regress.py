# -*- coding: utf-8 -*-
"""
Compare a ModelFlow solver with a reference solver on the test models.

Run from the modelflow source folder (where modelclass.py is), in a fresh
Python process so the local modelclass is the one imported:

    python <path>/regress.py --solver newton_fbmin_ng --ref sim_ng
    python <path>/regress.py --solver sim_hoist_ng --ref sim_ng --ljit
    python <path>/regress.py --solver sim_ng --ref sim --models pak small \
        --extra C:/mfdemo/.../bol.pcim

Without --ljit the solutions must be bit-identical (np.array_equal) unless
--tolerance is given; with --ljit they are compared with np.isclose(rtol, atol).
Jit code is compiled in memory (stringjit=True), so no modelsource/ files are
written.  Prints one line per model and exits with status 1 if any model
differs or fails.
"""
import argparse
import gc
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path.cwd()
if not (HERE / "modelclass.py").exists():
    sys.exit("Run from the modelflow source folder (the one with modelclass.py).")
sys.path.insert(0, str(HERE))

import modelclass  # noqa: E402
from modelclass import model  # noqa: E402

DATA = HERE / "modeltest" / "data"

# the scenarios of modeltest/ng_dispatch_test.py and speedtest.py
PAK = dict(path=DATA / "pak.pcim",
           scenario="<2020 2100> PAKGGREVCO2CER PAKGGREVCO2GER PAKGGREVCO2OER = 30",
           per=(2020, 2100), opts={})
FRBUS = dict(path=DATA / "frbusmcetest.pcim",
             scenario="<2020q1 2020q1> rffintay_aerr + 1 ",
             per=None, opts=dict(nonlin=15, max_iterations=300))

SMALL_PER = (2001, 2048)
SMALL_INDEX = range(2000, 2051)
SMALL_MODELS = {
    "small acyclic": """
        FRML <> A = 2*B $
        FRML <> C = A + B(-1) $
        FRML <> D = 0.5*C + 0.5*D(-1) $
    """,
    "small simultaneous": """
        FRML <> C = 10 + 0.3*C(-1) + 0.5*Y $
        FRML <> I = 20 + 0.1*(Y-Y(-1)) $
        FRML <> Y = C + I + G $
    """,
    "small damped": """
        FRML <DAMP> C = 10 + 0.3*C(-1) + 0.5*Y $
        FRML <> I = 20 + 0.1*(Y-Y(-1)) $
        FRML <> Y = C + I + G $
    """,
}

# solve options a pcim may carry that this script sets itself
NOT_SAVED = {"solver", "ljit", "silent", "stringjit", "transpile_reset", "reset_options"}


def pcim_case(spec):
    def build():
        m, df = model.modelload(str(spec["path"]), run=0)
        saved = {k: v for k, v in m.oldkwargs.items() if k not in NOT_SAVED}
        df = df.upd(spec["scenario"]) if spec.get("scenario") else df
        return m, df, spec.get("per"), {**saved, **spec.get("opts", {})}
    return build


def small_case(text):
    def build():
        m = model(text)
        df = pd.DataFrame(100.0, index=SMALL_INDEX, columns=sorted(m.allvar))
        df.loc[2010:, [v for v in m.exogene if v in df.columns]] *= 1.1
        return m, df, SMALL_PER, {}
    return build


def solve(build, solver, ljit, extra):
    """Build a fresh model and solve once; returns (seconds, frame, periods)."""
    m, df, per, opts = build()
    span = list(per) if per else []
    gc.collect()
    gc.disable()
    try:
        t0 = time.perf_counter()
        res = m(df, *span, **{**opts, "solver": solver, "silent": 1,
                              "reset_options": True, "ljit": ljit,
                              "stringjit": True, **extra})
        seconds = time.perf_counter() - t0
    finally:
        gc.enable()
    return seconds, res, list(m.current_per)


def compare(a, b, per, rtol, atol, exact):
    """(identical/close, max rel diff, max abs diff, where, n outside)."""
    cols = [c for c in a.columns if c in b.columns
            and a[c].dtype != object and b[c].dtype != object]
    x = a.loc[per, cols].to_numpy(dtype=float)
    y = b.loc[per, cols].to_numpy(dtype=float)
    absdiff = np.abs(y - x)
    rel = absdiff / (np.abs(x) + 1e-8)
    if rel.size == 0 or np.isnan(rel).all() or np.nanmax(rel) == 0:
        where, maxrel, maxabs = "-", 0.0, 0.0
    else:
        i, j = np.unravel_index(np.nanargmax(rel), rel.shape)
        where = f"{cols[j]} {per[i]}"
        maxrel, maxabs = float(np.nanmax(rel)), float(np.nanmax(absdiff))
    if exact:
        same = np.array_equal(x, y, equal_nan=True)
        outside = int((~((x == y) | (np.isnan(x) & np.isnan(y)))).sum())
    else:
        close = np.isclose(y, x, rtol=rtol, atol=atol, equal_nan=True)
        same, outside = bool(close.all()), int((~close).sum())
    return same, maxrel, maxabs, where, outside


def main():
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--solver", required=True, help="solver under test, e.g. sim_hoist_ng")
    p.add_argument("--ref", default="sim_ng", help="reference solver (default sim_ng)")
    p.add_argument("--models", nargs="*", default=["pak", "small"],
                   help="pak, frbus, small (default: pak small)")
    p.add_argument("--extra", nargs="*", default=[], help="more .pcim files (saved frame solved)")
    p.add_argument("--ljit", action="store_true", help="compile with numba; compare with tolerance")
    p.add_argument("--tolerance", action="store_true", help="tolerance compare also without jit")
    p.add_argument("--rtol", type=float, default=1e-5)
    p.add_argument("--atol", type=float, default=1e-6)
    p.add_argument("--opt", nargs="*", default=[],
                   help="extra solve options key=value, e.g. jacobian=fd max_iterations=300")
    a = p.parse_args()

    extra = {}
    for kv in a.opt:
        k, v = kv.split("=", 1)
        try:
            extra[k] = eval(v, {})
        except Exception:
            extra[k] = v

    cases = {}
    if "pak" in a.models:
        cases["pak"] = pcim_case(PAK)
    if "frbus" in a.models:
        cases["frbus mce"] = pcim_case(FRBUS)
    if "small" in a.models:
        cases.update({k: small_case(t) for k, t in SMALL_MODELS.items()})
    for path in a.extra:
        if Path(path).exists():
            cases[Path(path).stem] = pcim_case(dict(path=Path(path)))
        else:
            print(f"skipped, file not found: {path}")

    exact = not (a.ljit or a.tolerance)
    print(f"modelclass from {modelclass.__file__}")
    print(f"{a.solver} vs {a.ref}, ljit={a.ljit}, "
          + ("bit-identical" if exact else f"rtol={a.rtol} atol={a.atol}"))
    header = f"{'model':20} {'result':10} {'ref s':>8} {'test s':>8} {'max rel':>10} {'max abs':>10} {'outside':>8}  where"
    print(header)
    print("-" * len(header))

    failed = False
    for label, build in cases.items():
        try:
            tref, ref, per = solve(build, a.ref, a.ljit, extra)
        except Exception as e:
            print(f"{label:20} {'REF FAIL':10} {type(e).__name__}: {e}"[:160])
            failed = True
            continue
        try:
            ttest, test, _ = solve(build, a.solver, a.ljit, extra)
        except Exception as e:
            print(f"{label:20} {'FAIL':10} {type(e).__name__}: {e}"[:160])
            failed = True
            continue
        same, maxrel, maxabs, where, outside = compare(ref, test, per, a.rtol, a.atol, exact)
        result = ("identical" if exact else "close") if same else "DIFFERS"
        failed |= not same
        print(f"{label:20} {result:10} {tref:8.2f} {ttest:8.2f} {maxrel:10.2e} {maxabs:10.2e} {outside:8d}  {where}")

    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
