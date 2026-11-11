# Sources (checked 2026-11-09)

MFMod

- *The World Bank's MFMod Framework in Python with Modelflow* (mnemonic layout):
  https://documents1.worldbank.org/curated/en/099120125152010503/pdf/P507959-14dd767e-09b8-4e99-9246-d9c4993823eb.pdf
- Manual: https://worldbank.github.io/MFMod-ModelFlow/content/introduction.html
- Models: https://github.com/worldbank/MFMod-Python-Models
- WDI indicator codes (a different convention):
  https://datahelpdesk.worldbank.org/knowledgebase/articles/201175-how-does-the-world-bank-code-its-indicators

FRB/US

- Python package and data: https://www.federalreserve.gov/econres/us-models-python.htm
- EViews package: https://www.federalreserve.gov/econres/us-models-package.htm
- Technical Q&A (z/w/e expectation names): https://www.federalreserve.gov/econres/us-technical-qas.htm

The code tables in `mfmod.md` and the FRB/US facts in `frbus.md` were counted
from `pak.pcim` and `frbusmcetest.pcim` in the ModelFlow test data.

`scripts/iso3166_alpha3.csv`: ISO 3166-1 alpha-3 list from `pycountry`
(249 entries). A valid code does not mean an MFMod model exists for it.

These skills are not official products of the World Bank or the Federal Reserve.
