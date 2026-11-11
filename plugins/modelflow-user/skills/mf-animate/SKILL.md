---
name: mf-animate
description: >
  This skill should be used when making an animation of ModelFlow results in a
  notebook: "animate", "animation", "movie", "make it move", "FuncAnimation",
  "to_jshtml", "gif", "mp4", "animated orbit", "animated chart", "show the scenario
  unfolding over time", "rotating 3-D view", "trail", or when an animation is too
  big, does not show, or shows a static picture instead.
metadata:
  version: "0.1.0"
---

# Animations of model results

Solve first, animate afterwards. The model gives a dataframe with one row per
period (or time step); the animation draws a selection of those rows one by one
with matplotlib's `FuncAnimation`, and `to_jshtml()` turns it into a player that
works in JupyterLab, classic Notebook, VS Code and in a static Jupyter Book page.

## The pattern

1. **Pick the frames**: about 100–150. `sel = res.iloc[::max(1, len(res) // 120)]`.
2. **Draw the still parts once** (the full path in light grey, fixed points, axes
   limits, legend) and create empty artists for the moving parts:
   `dot, = ax.plot([], [], 'o')`.
3. **`draw(k)`** updates the moving artists for frame `k` and returns them.
4. `anim = animation.FuncAnimation(fig, draw, frames=len(sel), interval=50, blit=True)`
5. `plt.close(fig)` – otherwise a static copy of the first frame shows as well.
6. `HTML(anim.to_jshtml())` as the last line of the cell.

Fix the axis limits before animating (`ax.set(xlim=..., ylim=...)`); artists that
start empty do not set them.

## 2-D: bodies with trails

```python
from matplotlib import animation
from IPython.display import HTML
from modelode import pos

frames = 120
sel = res.iloc[::max(1, len(res) // frames)]
colors = ['tab:red', 'tab:green', 'tab:blue']
fig, ax = plt.subplots(figsize=(8, 3.6), dpi=72)
dots = [ax.plot([], [], 'o', color=c, ms=10)[0] for c in colors]
trails = [ax.plot([], [], '-', color=c, lw=1.5)[0] for c in colors]
ax.set(xlim=(-1.3, 1.3), ylim=(-0.5, 0.5), aspect='equal')
title = ax.set_title('')

def draw(k):
    lo = max(0, k - 12)                                  # trail: the last 12 frames
    for B, dot, trail in zip(bodies, dots, trails):
        x, y = sel[pos(B, 'X')], sel[pos(B, 'Y')]
        dot.set_data([x.iloc[k]], [y.iloc[k]])           # lists, also for one point
        trail.set_data(x.iloc[lo:k + 1], y.iloc[lo:k + 1])
    title.set_text(f't = {sel["T"].iloc[k]:.2f}')
    return dots + trails + [title]

anim = animation.FuncAnimation(fig, draw, frames=len(sel), interval=50, blit=True)
plt.close(fig)
HTML(anim.to_jshtml())
```

## 3-D with a turning camera

```python
fig = plt.figure(figsize=(6, 5), dpi=72)
ax = fig.add_subplot(projection='3d')
ax.plot(*xyz.T, color='lightgray', lw=.8)                # the whole path, n x 3 array
dot, = ax.plot([], [], [], 'o', color='tab:red', ms=8)
trail, = ax.plot([], [], [], '-', color='tab:red', lw=2)
lim = np.abs(xyz).max() * 1.05
ax.set(xlim=(-lim, lim), ylim=(-lim, lim), zlim=(-lim, lim))
sel = np.arange(0, len(xyz), max(1, len(xyz) // 120))

def draw(k):
    i = sel[k]
    lo = max(0, i - 50)
    dot.set_data_3d([xyz[i, 0]], [xyz[i, 1]], [xyz[i, 2]])
    trail.set_data_3d(xyz[lo:i + 1, 0], xyz[lo:i + 1, 1], xyz[lo:i + 1, 2])
    ax.view_init(elev=22, azim=-60 + 120 * k / len(sel))    # the camera turns 120 degrees
    return dot, trail

anim = animation.FuncAnimation(fig, draw, frames=len(sel), interval=50, blit=False)
plt.close(fig)
HTML(anim.to_jshtml())
```

- Use `blit=False` in 3-D: with a moving camera everything is redrawn anyway.
- A grey "shadow" of the path on the floor (`z = -lim`) helps reading the depth.

## Economic results: a scenario unfolding

The same pattern draws lines growing year by year, e.g. kept scenarios
(`mpak.keep_solutions`) for one variable:

```python
runs = {name: df.loc[2025:2050, 'PAKNYGDPMKTPKN'] for name, df in mpak.keep_solutions.items()}
years = next(iter(runs.values())).index
fig, ax = plt.subplots(figsize=(8, 4), dpi=72)
lines = {name: ax.plot([], [], lw=2, label=name)[0] for name in runs}
ax.set(xlim=(years[0], years[-1]),
       ylim=(min(s.min() for s in runs.values()) * .98, max(s.max() for s in runs.values()) * 1.02))
ax.legend(loc='upper left')

def grow(k):
    for name, s in runs.items():
        lines[name].set_data(s.index[:k + 1], s.iloc[:k + 1])
    return list(lines.values())

anim = animation.FuncAnimation(fig, grow, frames=len(years), interval=150, blit=True)
plt.close(fig)
HTML(anim.to_jshtml(default_mode='once'))     # play once and stop; 'loop' / 'reflect'
```

Bars (contributions from `dekomp`, sectors) work the same way: create the bars once
with `ax.bar` and change their heights with `bar.set_height(...)` in `draw`.

## Size, speed and saving

- `to_jshtml` stores every frame as a PNG inside the notebook. Measured: 120 frames
  at `dpi=72` are about 1.7 MB in 2-D and 6.5 MB in 3-D. Keep `dpi=72`, a modest
  `figsize` and ≈120 frames.
- Above 20 MB the animation is cut, with a warning. Raise the limit with
  `plt.rcParams['animation.embed_limit'] = 50` (MB), or use fewer frames.
- `interval` is milliseconds between frames (50 → 20 frames per second).
- Building takes a few seconds per 100 frames (longer in 3-D).
- Save a file: `anim.save('orbit.gif', writer='pillow', fps=20)` works out of the box;
  `.mp4` needs ffmpeg (`conda install -c conda-forge ffmpeg`), then
  `anim.save('orbit.mp4', fps=20, dpi=100)`.
- For PowerPoint, save an `.mp4` or `.gif` and insert it as a video or picture.
- A notebook that may also run where there is no ffmpeg (JupyterLite) should guard
  the save, and print a relative path (a published book shows the output):

  ```python
  if animation.writers.is_available('ffmpeg'):
      Path('mp4').mkdir(exist_ok=True)
      anim.save('mp4/orbit.mp4', fps=20, dpi=100)
  else:
      print('ffmpeg is not available here - the animation above still works')
  ```

## In Jupyter Book and JupyterLite

- **Jupyter Book 2** (tested with 2.1.6) shows the stored output: the `to_jshtml`
  player works with all its buttons, `HTML(anim.to_html5_video())` gives a video
  player, and `![](mp4/orbit.mp4)` in a markdown cell is copied into the site and
  plays as a silent looping video – the lightest page. Execute the notebook first.
- **JupyterLite** (Pyodide, not tested yet): `to_jshtml` should work but build slowly;
  there is no ffmpeg, so `.mp4` saving and `to_html5_video()` fail; `.gif` with pillow
  should work.

## When it does not work

| Symptom | Cause |
| --- | --- |
| a still picture as well as the player | `plt.close(fig)` missing |
| only a still picture | `HTML(anim.to_jshtml())` not the last line, or the `anim` object went out of scope (keep a reference) |
| empty axes | axis limits not set before animating |
| `set_data` error about sequences | pass lists: `dot.set_data([x], [y])` |
| "Animation size has reached ..." | more than `animation.embed_limit` MB: fewer frames, lower dpi |
| `%matplotlib widget` / `notebook` backends | not needed; `to_jshtml` works with the default inline backend |

## Related

`mf-ode-simulate` (running ODE models), `mf-results` and `mf-reports` (static charts
and tables). Worked examples: the animated figure-8 in `nbody_modelflow.ipynb` and the
3-D halo orbit in `webb_l2_modelflow.ipynb` (`modelflow/experiments/projecttile/`).
