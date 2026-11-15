"""Rebuild makro_names.csv from a ModelFlow translation of MAKRO (for a new release).

    python build_makro_names.py MODEL.pcimz [--sets-gdx sets.gdx] [--out makro_names.csv]

Reads the descriptions of the model ('<text> [ELEMENTS] (MAKRO name)'). The GAMS
domains need DREAM's sets.gdx and gams.transfer (pip install gamsapi[transfer]
gamspy_base); without them the domain column is left empty.
"""
from __future__ import annotations

import argparse
import collections
import csv
import re
from pathlib import Path


def domains(sets_gdx):
    if not sets_gdx:
        return {}
    import gamspy_base
    import gams.transfer as gt
    c = gt.Container(str(sets_gdx), system_directory=gamspy_base.directory)
    out = {}
    for name, sym in c.data.items():
        try:
            out[name.lower()] = [d if isinstance(d, str) else d.name for d in sym.domain]
        except AttributeError:
            pass
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('model')
    ap.add_argument('--sets-gdx', help='DREAM sets.gdx or baseline.gdx (for the GAMS domains)')
    ap.add_argument('--out', default=str(Path(__file__).with_name('makro_names.csv')))
    a = ap.parse_args(argv)

    from modelclass import model as mc
    m, _ = mc.modelload(a.model, run=0, straight=True, silent=1)
    endo = set(m.endogene)
    dom = domains(a.sets_gdx)

    rows, count, nendo, example = {}, collections.Counter(), collections.Counter(), {}
    for k in sorted(m.allvar):
        v = m.var_description.get(k) or ''
        hit = re.search(r'\(MAKRO ([^)]+)\)\s*$', v)
        if not hit:
            continue
        o = hit.group(1)
        count[o] += 1
        nendo[o] += (k in endo) or (k + '___RES' in endo)
        example.setdefault(o, k)
        if o not in rows:
            text = v[:hit.start()].strip()
            if '__' in k:                                   # drop the trailing ' [ELEMENTS]'
                text = re.sub(r'\s+\[[^\]]*\]\s*$', '', text).strip()
            d = dom.get(o.lower())
            rows[o] = dict(makro=o, modelflow=re.sub(r'[^0-9A-Za-z_]', '_', o).upper(),
                           domain=','.join(d).lower() if d else '',
                           adam='; '.join(sorted(set(re.findall(r'ADAM\[[^\]]+\]', text)))), text=text)
    with open(a.out, 'w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=['makro', 'modelflow', 'domain', 'instances', 'endogenous', 'example', 'adam', 'text'])
        w.writeheader()
        for o, r in sorted(rows.items(), key=lambda x: x[0].lower()):
            w.writerow(dict(r, instances=count[o], endogenous=nendo[o], example=example[o]))
    print(f'{len(rows)} MAKRO names written to {a.out}')


if __name__ == '__main__':
    main()
