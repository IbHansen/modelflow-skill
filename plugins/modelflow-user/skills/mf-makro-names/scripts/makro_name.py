"""Decode MAKRO variable names, as GAMS names or as ModelFlow names, and find names.

    python makro_name.py NAME [NAME ...] [--model file.pcimz] [--json]
    python makro_name.py --find TEXT [--limit 30]

NAME can be a ModelFlow name (PC__CTOT, CHH_A__BANK__40, VTMOMS_Y___RES) or a GAMS
name (pC, pC[cTot,t], jvHhxAfk). Without --model the names are checked against
makro_names.csv (MAKRO 2026-September). With --model they are looked up in the
model and its description is shown; only that confirms a meaning.

--find searches the MAKRO names, DREAM's Danish texts and the English glossary.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
GLOSSARY_MD = HERE.parent / 'references' / 'glossary.md'

with (HERE / 'makro_names.csv').open(encoding='utf-8') as f:
    NAMES = list(csv.DictReader(f))
BY_MF = {r['modelflow']: r for r in NAMES}
BY_LOW = {r['makro'].lower(): r for r in NAMES}


def read_glossary():
    """roots and elements from the tables in glossary.md: | `Code` | English |"""
    roots, elements, section = {}, {}, ''
    for line in GLOSSARY_MD.read_text(encoding='utf-8').splitlines():
        if line.startswith('## '):
            section = line
        m = re.match(r'\|\s*`([^`]+)`\s*\|\s*(.+?)\s*\|\s*$', line)
        if m:
            (elements if 'Set elements' in section else roots).setdefault(m.group(1), m.group(2))
    return roots, elements


ROOTS, ELEMENTS = read_glossary()

PREFIX = {
    'j': 'additive residual', 'f': 'factor', 'E': 'expectation', 'd': 'derivative',
    's': 'structural', 'm': 'marginal', 'u': 'scale parameter', 't': 'tax rate',
    'r': 'rate or ratio', 'e': 'elasticity/exponent', 'p': 'price (inflation-adjusted)',
    'q': 'quantity (growth-adjusted)', 'v': 'value (growth- and inflation-adjusted)',
    'n': 'number of persons', 'h': 'hours', 'c': 'additive term / spread (not in the README)',
}
ATOMIC = {'nv': 'present value', 'jf': 'multiplicative residual'}
COMPOUND = {  # prefix combinations with a reading of their own (checked longest first)
    'nvt': 'present value of tax revenue', 'vt': 'tax revenue', 'rp': 'relative lagged prices (chain ratio of the aggregate)',
    'cr': 'interest spread to a reference rate', 'ft': 'correction factor on a tax rate', 'mt': 'marginal tax rate',
    'mr': 'marginal rate or return',
}
SPECIAL = {   # whole names with their own reading
    'fq': 'one-year growth adjustment factor 1+gq', 'fp': 'one-year inflation adjustment factor 1+gp',
    'fv': 'one-year value adjustment factor (1+gq)(1+gp)', 'fqt': 'cumulative growth factor fq**(t-tBase)',
    'budgetfaktor': 'cyclical sensitivity of general budget items (no prefix)',
    'mUC': 'marginal utility of consumption (U = utility, not user cost)',
    'EmUC': 'expected marginal utility of consumption',
    'rpCInflSnit': 'rate: moving average of consumer price inflation (r + pCInflSnit, not the rp chain ratio)',
}
SUFFIX = {'a': 'age-dependent part', 't': 'time-varying part', 's': 'by using sector',
          'y': 'from domestic production', 'm': 'from imports', 'k': 'of capital goods',
          'vaekst': 'growth factor', 'Over100': 'persons over 100'}
COMPANION = {'___RES': 'residual of an implicit equation (solves the base variable)',
             '_D': 'fix dummy (1 = use _X)', '_X': 'fixed value used when _D = 1'}
GENERATED = {'TEND': 'terminal-year dummy', 'TEND2': 'terminal-years dummy', 'TVAL': 'the year (t.val)'}


def split_prefix(name: str):
    """(prefix parts, rest) of a CamelCase MAKRO name"""
    if name in SPECIAL:
        return [name], ''
    m = re.match(r'(E?[a-z]*)(.*)$', name)
    pre, rest = m.group(1), m.group(2)
    if not rest:                       # all lower case, e.g. 'eh', 'uh'
        pre, rest = pre[:1], pre[1:]
    parts, i = [], 0
    while i < len(pre):
        two = pre[i:i + 2]
        if two in ATOMIC:
            parts.append(two); i += 2
        else:
            parts.append(pre[i]); i += 1
    return parts, rest


ROOT_KEYS = sorted(ROOTS, key=len, reverse=True)
LOWER_ELEMENTS = {'udv': 'extraction', 'sp': 'private sectors', 'spxudv': 'private sectors excluding extraction',
                  'h': 'hours'}


def lower_word(run: str) -> str:
    """reading of a lower-case run inside a name ('udv', 'bidrag', 'gaeld')"""
    if run in LOWER_ELEMENTS:
        return LOWER_ELEMENTS[run]
    return ROOTS.get(run.capitalize(), '?')


def readable_lower(run: str) -> bool:
    return run.startswith('x') or lower_word(run) != '?'


def words(rest: str):
    """[(word, reading)] of the CamelCase part and the suffix after '_'.
    Glossary words are matched longest first; a glued 'x' is 'excluding', a '2' is
    'relative to', and a lower-case run after '2' is a prefix ('2dvBolig')."""
    stem, _, suffix = rest.partition('_')
    out, i, after2 = [], 0, False
    while i < len(stem):
        ch = stem[i]
        if ch.isdigit():
            j = i
            while j < len(stem) and stem[j].isdigit():
                j += 1
            num = stem[i:j]
            out.append((num, 'relative to / with respect to' if num == '2' else 'number'))
            i, after2 = j, num == '2'
            continue
        if ch.islower():
            j = i
            while j < len(stem) and stem[j].islower():
                j += 1
            run = stem[i:j]
            elem = re.match(r'[a-z]+[A-Z][a-z]*', stem[i:])
            if elem and elem.group(0).upper() in ELEMENTS:   # a set element glued in: '2iL', 'cTot'
                out.append((elem.group(0), ELEMENTS[elem.group(0).upper()]))
                i, after2 = i + len(elem.group(0)), False
                continue
            if after2 and all(c in PREFIX for c in run):
                out.append((run, prefix_reading(split_prefix(run + 'X')[0])))
            elif run.startswith('x'):
                out.append(('x', 'excluding'))
                if run[1:]:
                    out.append((run[1:], lower_word(run[1:])))
            else:
                out.append((run, lower_word(run)))
            i, after2 = j, False
            continue
        for k in ROOT_KEYS:
            if not stem.startswith(k, i):
                continue
            j = i + len(k)
            run = re.match(r'[a-z]*', stem[j:]).group(0)
            if not run or readable_lower(run):          # a whole word, or followed by a readable glued word
                out.append((k, ROOTS[k]))
                i = j
                break
        else:
            m = re.match(r'[A-Z]{2,}(?![a-z])|[A-Z][a-z]*', stem[i:])
            out.append((m.group(0), '?'))
            i += len(m.group(0))
        after2 = False
    return out, suffix


def prefix_reading(parts):
    pre, out, i = ''.join(parts), [], 0
    while i < len(pre):
        for k in sorted(COMPOUND, key=len, reverse=True):
            if pre.startswith(k, i):
                out.append(COMPOUND[k]); i += len(k); break
        else:
            for k in ATOMIC:
                if pre.startswith(k, i):
                    out.append(ATOMIC[k]); i += len(k); break
            else:
                out.append(PREFIX.get(pre[i], '?')); i += 1
    return ' + '.join(out)


def decode_makro(name: str) -> dict:
    if name in SPECIAL:
        return {'prefix': '', 'prefix_reading': '', 'words': [], 'meaning': SPECIAL[name]}
    parts, rest = split_prefix(name)
    ws, suffix = words(rest)
    out = {'prefix': ''.join(parts), 'prefix_reading': prefix_reading(parts), 'words': ws}
    if suffix:
        out['suffix'] = (suffix, ' + '.join(SUFFIX.get(s, '?') for s in suffix.split('_')))
    return out


def element(e: str) -> str:
    if e.isdigit():
        return f'age {e}'
    if e == 'NA':
        return 'outside the set (before age 0, zero)'
    return ELEMENTS.get(e, '?')


def split_mf(name: str):
    """ModelFlow name -> (stem, elements, companion suffix)"""
    for suf in COMPANION:
        if name.endswith(suf):
            base = name[:-len(suf)]
            if base.split('__')[0] in BY_MF:
                stem, *els = base.split('__')
                return stem, els, suf
    stem, *els = name.split('__')
    return stem, els, None


def parse_gams(name: str):
    m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)(?:\[(.*)\])?$", name.strip())
    if not m:
        return None
    els = [e.strip().strip("'\"") for e in (m.group(2) or '').split(',') if e.strip()]
    els = [e for e in els if e.lower() != 't']
    return m.group(1), els


def explain(name: str, model=None) -> dict:
    res = {'input': name}
    gams = None
    if '[' in name or (any(c.islower() for c in name) and '__' not in name):
        gams = parse_gams(name)
    if gams:
        row = BY_LOW.get(gams[0].lower())
        els = [re.sub(r'[^0-9A-Za-z_]', '_', e).upper() for e in gams[1]]
        companion = None
        mf = '__'.join([row['modelflow'] if row else gams[0].upper()] + els)
    else:
        stem, els, companion = split_mf(name.upper())
        row = BY_MF.get(stem)
        mf = name.upper()
    res['modelflow'] = mf
    if row is None:
        stem = mf.split('__')[0]
        if stem in GENERATED:
            res.update(level='generated', meaning=GENERATED[stem])
        else:
            res.update(level='unknown', meaning='not in the MAKRO 2026-September list')
    else:
        res['makro'] = row['makro']
        res['gams_domain'] = row['domain'] or '(constant)'
        res.update(decode_makro(row['makro']))
        res['text'] = row['text']
        if row['adam']:
            res['adam'] = row['adam']
        res['level'] = 'release list'
    if els:
        res['elements'] = [(e, element(e)) for e in els]
    if companion:
        res['companion'] = (companion, COMPANION[companion])
    if model is not None:
        if mf in model.allvar:
            res['level'] = 'in the model'
            des = model.var_description.get(mf)
            if des and des != mf:
                res['level'] = 'defined'
                res['description'] = des
            res['endogenous'] = mf in model.endogene
        else:
            res['level'] = 'not in the model'
            stem = mf.split('__')[0]
            res['candidates'] = sorted(v for v in model.allvar if v.split('__')[0] == stem)[:12]
    if row is not None and not companion:
        need = len([d for d in row['domain'].split(',') if d and d != 't'])
        if need != len(els):
            res['note'] = f"{row['makro']} takes {need} index element(s) here, e.g. {row['example']}"
    return res


def show(r: dict):
    print(r['modelflow'] + (f"   (MAKRO {r['makro']}, domain {r['gams_domain']})" if 'makro' in r else ''))
    if r.get('prefix') or r.get('prefix_reading'):
        print(f"  prefix  {r['prefix']:6} {r['prefix_reading']}")
    for w, e in r.get('words', []):
        print(f"  word    {w:6} {e}")
    if 'suffix' in r:
        print(f"  suffix  _{r['suffix'][0]:5} {r['suffix'][1]}")
    for e, m in r.get('elements', []):
        print(f"  index   {e:6} {m}")
    if 'companion' in r:
        print(f"  added   {r['companion'][0]:6} {r['companion'][1]}")
    if 'meaning' in r:
        print(f"  {r['meaning']}")
    if 'text' in r:
        print(f"  DREAM:  {r['text']}")
    if 'adam' in r:
        print(f"  ADAM:   {r['adam']}")
    if 'description' in r:
        print(f"  model:  {r['description']}")
    if 'endogenous' in r:
        print(f"  endogenous: {r['endogenous']}")
    if 'note' in r:
        print(f"  note:   {r['note']}")
    if r.get('candidates'):
        print(f"  in the model: {' '.join(r['candidates'])}")
    print(f"  level:  {r['level']}")
    print()


def find(text: str, limit: int):
    t = text.lower()
    eng = {k for k, v in ROOTS.items() if t in v.lower()}
    hits = []
    for r in NAMES:
        _, rest = split_prefix(r['makro'])
        ws, _ = words(rest)
        if t in r['makro'].lower() or t in r['text'].lower() or eng & {w for w, _ in ws}:
            hits.append(r)
    if eng:
        print(f"glossary words for '{text}': {', '.join(sorted(eng))}")
    for r in hits[:limit]:
        print(f"{r['modelflow']:24} {r['makro']:22} [{r['domain']}]  {r['text'][:90]}")
    if len(hits) > limit:
        print(f'... {len(hits) - limit} more (--limit)')


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('names', nargs='*')
    ap.add_argument('--model', help='pcim/pcimz file to look the names up in')
    ap.add_argument('--find', help='search names, Danish texts and the English glossary')
    ap.add_argument('--limit', type=int, default=30)
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args(argv)
    if a.find:
        find(a.find, a.limit)
    model = None
    if a.model and a.names:
        from modelclass import model as mc
        model, _ = mc.modelload(a.model, run=0, straight=True, silent=1)
    out = [explain(n, model) for n in a.names]
    if a.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
    else:
        for r in out:
            show(r)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
