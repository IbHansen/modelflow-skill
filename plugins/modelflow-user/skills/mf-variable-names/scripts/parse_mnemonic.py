"""Split MFMod variable names into their parts and optionally look them up in a model.

    python parse_mnemonic.py NAME [NAME ...] [--model file.pcim] [--json]

Without --model only the pattern is checked. With --model the names are looked up
in the model and its description is shown; only that confirms a meaning.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
with (HERE / 'iso3166_alpha3.csv').open(encoding='utf-8') as f:
    ISO3 = {row['alpha3']: row['country_name'] for row in csv.DictReader(f)}

ACCOUNTS = {'NY': 'national income', 'NE': 'national expenditure', 'NV': 'value added',
            'GG': 'general government', 'BX': 'BOP exports', 'BM': 'BOP imports',
            'BN': 'BOP net', 'BF': 'BOP financial account', 'FM': 'monetary/financial',
            'LM': 'labour market'}
MEASURES = {'K': 'real (constant prices)', 'C': 'current prices', 'X': 'price, deflator or rate'}
CURRENCIES = {'N': 'national currency', 'D': 'US dollars', 'P': 'PPP'}
COMPANIONS = ['_FITTED', '___RES', '_AERR', '_A', '_X', '_D']   # longest first
COMPANION_MEANING = {'_FITTED': 'fitted value', '___RES': 'residual of implicit equation',
                     '_AERR': 'FRB/US add factor', '_A': 'add factor',
                     '_X': 'fixed (exogenized) value', '_D': 'fix dummy'}


def split_suffix(name: str) -> tuple[str, str | None]:
    """Strip one ModelFlow companion suffix or a _VALUE_<year> suffix."""
    if '_VALUE_' in name:
        base, _, year = name.rpartition('_VALUE_')
        if year.isdigit():
            return base, f'_VALUE_{year}'
    for suf in COMPANIONS:
        if name.endswith(suf) and len(name) > len(suf):
            return name[:-len(suf)], suf
    return name, None


def parse(name: str) -> dict:
    n = name.upper()
    base, suffix = split_suffix(n)
    ratio = base.endswith('_')
    core = base[:-1] if ratio else base
    out = {'name': name, 'base': base, 'suffix': suffix,
           'suffix_meaning': (COMPANION_MEANING.get(suffix) or
                              (f'value in {suffix[7:]}' if suffix else None)),
           'trailing_underscore': ratio}
    if len(core) != 14 or not core.isalnum():
        out.update(plain_mnemonic=False,
                   reason='not a 14-character mnemonic: read the description')
        return out
    ccc, aa, mmm, nnnn, u, c = core[:3], core[3:5], core[5:8], core[8:12], core[12], core[13]
    out.update(plain_mnemonic=True, country=ccc, country_name=ISO3.get(ccc),
               account=aa, account_meaning=ACCOUNTS.get(aa), subject=mmm, detail=nnnn,
               measure=u, measure_meaning=MEASURES.get(u),
               currency=c, currency_meaning=CURRENCIES.get(c))
    out['pattern_ok'] = all(out[k] is not None for k in
                            ('country_name', 'measure_meaning', 'currency_meaning'))
    if ratio:
        out['note'] = 'trailing _ is often a ratio in percent (of GDP): check the description'
    return out


def lookup(results: list[dict], pcim: str) -> None:
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        from modelclass import model
        mmodel, _ = model.modelload(pcim, run=0)
    for r in results:
        n = r['name'].upper()
        r['in_model'] = n in mmodel.allvar
        r['description'] = mmodel.var_description.get(n) if r['in_model'] else None
        if r['in_model']:
            r['endogenous'] = n in mmodel.endogene
        elif r['suffix'] is None:
            stem = r['base'][:8]
            r['similar_in_model'] = sorted(v for v in mmodel.allvar if v.startswith(stem))[:15]


def show(r: dict) -> str:
    lines = [r['name']]
    if r.get('plain_mnemonic'):
        lines.append(f"  {r['country']} {r['account']} {r['subject']} {r['detail']} "
                     f"{r['measure']} {r['currency']}")
        lines.append(f"  country {r['country_name'] or '? (not ISO)'}, "
                     f"account {r['account_meaning'] or '? (read description)'}, "
                     f"{r['measure_meaning'] or '?'}, {r['currency_meaning'] or '?'}")
    else:
        lines.append(f"  {r['reason']}")
    if r['suffix']:
        lines.append(f"  suffix {r['suffix']}: {r['suffix_meaning']} of {r['base']}")
    if r.get('note'):
        lines.append(f"  {r['note']}")
    if 'in_model' in r:
        if r['in_model']:
            kind = 'endogenous' if r['endogenous'] else 'exogenous'
            lines.append(f"  IN MODEL ({kind}): {r['description'] or '(no description)'}")
        else:
            lines.append('  NOT IN MODEL')
            if r.get('similar_in_model'):
                lines.append('  similar: ' + ' '.join(r['similar_in_model']))
    else:
        lines.append('  pattern only: not checked against a model')
    return '\n'.join(lines)


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('names', nargs='+')
    ap.add_argument('--model', help='.pcim file to look the names up in')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args(argv)
    results = [parse(n) for n in a.names]
    if a.model:
        lookup(results, a.model)
    if a.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print('\n'.join(show(r) for r in results))


if __name__ == '__main__':
    main()
