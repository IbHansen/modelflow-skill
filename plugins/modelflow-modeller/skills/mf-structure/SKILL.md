---
name: mf-structure
description: >
  This skill should be used when analysing the structure of a ModelFlow model or a
  convergence problem: "simultaneous block", "prolog core epilog", "feedback
  variables", "fblist", "why does the model not converge", "oscillates", "slow
  convergence", "dependency graph", "what drives X", "tracepre", "draw the model",
  "eigenvalues", "stability", or "how big is the core".
metadata:
  version: "0.1.0"
---

# Model structure and convergence

Run `/mf-check-model` first: it prints the numbers below for a model file.

## The decomposition

`m.superblock()` (run automatically) splits the endogenous variables:

| Part | Attribute | Solved |
| --- | --- | --- |
| prolog | `m.preorder` | once per period, before the core – depends on no current core variable |
| core | `m.coreorder` | iterated – the simultaneous block(s) |
| epilog | `m.epiorder` | once per period, after the core – feeds nothing back |
| feedback set | `m.fblist` | the minimal set whose removal makes the core recursive |
| DAG part of core | `m.daglist` | the rest of the core, in topological order |

`m.istopo` is True for a recursive model (no core). Example – PAK: 378 equations,
prolog 27, core 104 in one block, epilog 247, feedback set of 6.

The size of the feedback set drives the cost of Newton on the feedback set
(`newton_fbmin_ng`): a Jacobian build costs `len(m.fblist) + 1` sweeps of the core.

## Seeing the structure

```python
mmodel.drawmodel()                          # whole dependency graph (small models)
mmodel.draw('PAKNYGDPMKTPKN', up=2, down=1) # neighbourhood of one variable
mmodel.PAKNYGDPMKTPKN.tracepre(up=2)        # what X depends on
mmodel.PAKNYGDPMKTPKN.tracedep(down=2)      # what depends on X
mmodel.plotadjacency()                      # adjacency matrix
```

Drawing needs graphviz installed and on PATH (on Windows it is often not added to
PATH by the installer).

## When the model does not converge

1. **Dump the whole core and find the origin.** To locate where the instability
   starts, dump **all** core variables (`dumpvar='*'`, the default pattern) with
   Gauss-Seidel, for the first failing period only, then rank the variables that
   have not settled. From a model file, the `mf-check-model` skill's
   `check_convergence.py` does all of it (finds the failing period, survives
   solver errors, ranks, names the origin). In a notebook:
   ```python
   import numpy as np, pandas as pd
   per = 2025                                         # the first period not converged
   res = mmodel(df, per, per, solver='sim', ldumpvar=True, dumpvar='*')
   it = mmodel.dumpdf.query('per == @per').set_index('iteration').drop(columns='per')
   step = it.diff().iloc[-10:]                        # the last iterations
   last = it.iloc[-1].abs()
   rank = pd.DataFrame({
       'rel_step':   (step.abs() / last.where(last != 0)).max(),   # still moving
       'sign_flips': (np.sign(step).diff().abs() > 0).sum(),       # oscillating
       'core_pos':   pd.Series({v: i for i, v in enumerate(mmodel.coreorder)}),
   }).dropna().sort_values('rel_step', ascending=False)
   rank.head(15)
   mmodel.show_iterations(' '.join(rank.index[:6]), per=per, change=True)
   ```
   Read the top of the ranking as a chain: the variables that move most and
   flip sign, and among them the earliest in solve order (`core_pos`), are where
   to start. Draw the loop between them (`mmodel.<VAR>.tracepre(up=2)`) and look
   at those equations: a coefficient above 1 on a current-period feedback, a
   ratio with a small denominator, a policy rule reacting too strongly.
   - Monotone and slow → more iterations or Newton.
   - Oscillating (`sign_flips` high) → damp (`alfa < 1`, `<DAMP>` on the
     oscillating equations).
   - Exploding → an equation or data problem, not a solver problem.

   Notes: only variables in the simultaneous core are dumped; prolog and epilog
   never are. Row `iteration 0` is the value before the period is solved.
   `newton_fbmin_ng` dumps only the feedback set (`mmodel.fblist`), so use `sim`
   or `sim_ng` for the full-core dump. On PAK (104 core variables) a one-period
   full dump takes a second; for a large core restrict `max_iterations` so the
   dump stays small.
2. **NaN or inf**: the solvers stop and name the variables. Find the first one in
   solve order and inspect its equation and inputs (`mf-debug-model`).
3. **Switch solver**: Newton on the feedback set (`newton_fbmin_ng`) converges
   where Gauss-Seidel oscillates (`mf-solvers`).
4. **Check the equation that should not be simultaneous**: a large core in a
   model that should be mostly recursive often comes from one wrong current-period
   reference (`X` instead of `X(-1)`). Trace the feedback variables with
   `tracepre`.

## Stability

`Stability_Mixin` computes the eigenvalues of the model's linearisation:
`mmodel.get_eigenvalues()`, `mmodel.eigenvalues_show()`,
`mmodel.eigenvalues_plot()`; `get_eigen_jackknife_df` and
`jack_largest_reduction` show which variables drive the largest eigenvalue. Use
them when a scenario diverges over time although each period converges.
