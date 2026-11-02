# Notebook display code (JS/CSS injection)

Background for changing the parts of ModelFlow that inject JavaScript or CSS into notebooks (`widescreen`, `scroll_off`, `scroll_on`, `modelflow_auto`, widgets). User-side install and first-cell setup are in the `mf-getting-started` skill of `modelflow-user`.

`model.plain_html` (since 2026-10) switches the `mpak[...]` viewer and `rplot` to plain HTML tabs/details instead of ipywidgets, for front ends that cannot show Tab/Accordion widgets (RISE).

## Notebook display setup

Every notebook should open with these two lines after the import:

```python
from modelclass import model
model.widescreen()
model.scroll_off()
```

`widescreen()` injects CSS that widens the cell output area; `scroll_off()` disables the auto-scroll on long outputs (important for big tables). Both are no-ops on backends that don't recognize them, so they're safe to leave in.

## Jupyter Notebook 7 / JupyterLab compatibility

This is an active area of churn. `modelclass.py` historically targeted classic Jupyter Notebook (≤6) and the JS guards plus CSS selectors that worked there can fail silently under Notebook 7 (which is JupyterLab under the hood). Things to know:

- **`IPython` and the AMD `base/js/namespace` module are gone in JN7.** Classic JS that did `IPython.notebook...` or `require(['base/js/namespace'], ...)` throws a `ReferenceError` in the *browser*. A Python `try/except` around the cell will not catch this — the cell looks like it succeeded but the JS did nothing.
- **The DOM structure changed.** CSS selectors that targeted `.container`, `#notebook`, or `div.output_scroll` in classic Jupyter don't match JupyterLab's layout. Look for `.jp-Notebook`, `.jp-OutputArea`, `.jp-Cell` instead.

The fixes that Ib has been applying take the form of two guards plus an updated selector. Reuse this pattern when patching `scroll_off`, `scroll_on`, `widescreen`, `modelflow_auto`, or anything else that injects JS or CSS:

```python
from IPython.display import display, HTML, Javascript

js = """
if (typeof IPython !== 'undefined' && typeof require !== 'undefined') {
    // classic Notebook path
    IPython.OutputArea.prototype._should_scroll = function(){ return false; };
} else {
    // Notebook 7 / JupyterLab — use CSS instead
    var style = document.createElement('style');
    style.innerHTML = '.jp-OutputArea-output { max-height: none !important; overflow: visible !important; }';
    document.head.appendChild(style);
}
"""
display(Javascript(js))
```

The guard `typeof IPython !== 'undefined' && typeof require !== 'undefined'` correctly identifies classic JN; everything else (JN7, JupyterLab, VS Code, nbconvert HTML) falls through to the CSS path.

When the user asks "why doesn't `scroll_off()` work in my new JupyterLab" — this is the answer.

## Checking which installation is used

A two-line smoke test:

```python
from modelclass import model
print(model.__module__)   # should print 'modelclass'
```

If the import fails, ninety percent of the time it's because the wrong conda environment is active. Suggest `conda info --envs` to confirm.
