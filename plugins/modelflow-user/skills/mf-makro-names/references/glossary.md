# MAKRO glossary: Danish name parts and set elements

MAKRO's names and descriptions are Danish. The tables below give the English for
the parts that occur most often in the 2026-September release. `scripts/makro_name.py`
reads these tables, so keep the row format `` | `Code` | English | ``.

A translation here is a reading aid, not a definition: the variable's own text
(`.des`, or the `text` column of `scripts/makro_names.csv`) decides.

## Roots and words inside names

Words in a MAKRO name are CamelCase after the prefix (`jrHhAktRenter` =
`jr` + `Hh` + `Akt` + `Renter`). A lower-case `x` glued to a word means
"excluding" (`Hhx`, `BVTxudv`, `Gx`, `Cx`, `Renterx`), a `2` means "relative to"
or "with respect to" (`hL2nL` hours per employed person, `dY2dX` derivative).

### Sectors and agents

| Code | English |
| --- | --- |
| `Hh` | households |
| `Hhx` | households' wealth excluding pension, housing and mortgage debt |
| `Off` | general government (offentlig) |
| `Off13` | general government on the S.13 (national accounts) definition |
| `Virk` | firms, corporations (virksomheder) |
| `Udl` | rest of the world, foreign (udland) |
| `Pension` | pension funds (as a sector) |
| `Kol` | collective (pension schemes, public services) |
| `Selvst` | self-employed |
| `Loenmodtager` | employees (wage earners) |
| `FF` | trade union (fagforening) in the wage bargain |
| `DK` | resident in Denmark; `xDK` cross-border workers |
| `Soc` | socio-economic group (set `soc`) |
| `Pop` | population |
| `Boern` | children |
| `EU` | the European Union |

### National accounts and demand

| Code | English |
| --- | --- |
| `Y` | output (production) |
| `BVT` | gross value added (bruttoværditilvækst) |
| `BNP` | gross domestic product |
| `BNI` | gross national income |
| `C` | private consumption |
| `CDK` | private consumption including tourists' consumption in Denmark |
| `Cx` | consumption excluding housing and financial costs |
| `CGI` | domestic demand (C + G + I) |
| `CGIX` | total demand (C + G + I + X) |
| `G` | government consumption |
| `Gx` | government consumption excluding depreciation |
| `I` | investment |
| `Ib` | building investment |
| `Im` | machinery investment |
| `Lager` | inventories |
| `Stam` | livestock (stambesætninger) |
| `Vaerdi` | valuables |
| `X` | exports |
| `Xy` | exports from domestic production |
| `Xm` | exports from imports (re-exports) |
| `M` | imports |
| `R` | intermediate input of materials |
| `E` | energy input |
| `IO` | input-output delivery |
| `IOy` | input-output delivery from domestic production |
| `IOm` | input-output delivery from imports |
| `K` | capital |
| `B` | buildings (capital) |
| `L` | labour |
| `LUdn` | labour in efficiency units |
| `KUdn` | capital after capacity utilisation |
| `KEL` | CES nest of capital, energy and labour (also `KE`, `KELB`, `KELBR`) |
| `Handel` | trade (exports plus imports) |
| `Marked` | market (`XMarked` export market) |
| `Turist` | tourists |
| `Bil` | cars |
| `Land` | land |
| `Nordsoe` | the North Sea (oil and gas) |

### Prices, incomes and finance

| Code | English |
| --- | --- |
| `W` | wage |
| `Loen` | wage, wages (løn) |
| `Ind` | income or revenue (indkomst / indtægter) |
| `Ud` | expenditure (udgifter) |
| `Prim` | primary (before interest) |
| `Saldo` | balance, budget balance |
| `NFE` | net lending (nettofordringserhvervelse) |
| `Net` | net |
| `Netto` | net |
| `Brutto` | gross |
| `Formue` | wealth |
| `Akt` | assets (aktiver) |
| `Pas` | liabilities (passiver) |
| `Aktie` | shares, equity |
| `Obl` | bonds |
| `RealKred` | mortgage credit (realkredit) |
| `Kred` | credit |
| `Bank` | bank deposits and loans |
| `Laan` | loans |
| `Gaeld` | debt |
| `Ugaeld` | debt (in `OEMUgaeld`, EMU debt) |
| `OEMU` | EMU (Maastricht) |
| `Indskud` | deposits |
| `Rente` | interest rate |
| `Renter` | interest payments |
| `Afk` | return (afkast) |
| `Omv` | revaluation (omvurdering) |
| `Realiseret` | realised |
| `Udbytte` | dividends |
| `Dividender` | dividends |
| `Prem` | premium |
| `Accel` | (financial) accelerator |
| `Fin` | financial |
| `Disk` | discount, discounting |
| `Drift` | operations, operating |
| `FCFF` | free cash flow to the firm |
| `Fast` | fixed-rate |
| `Flex` | adjustable-rate |
| `Pris` | price |
| `Priser` | prices |
| `CPI` | consumer price index |
| `HICP` | harmonised index of consumer prices |
| `UC` | user cost |
| `Markup` | mark-up |
| `Indeks` | index |
| `Base` | base |

### Taxes, transfers and pensions

| Code | English |
| --- | --- |
| `Skat` | tax |
| `Kskat` | book value of capital for tax purposes |
| `Afg` | excise duties (afgifter) |
| `Moms` | VAT |
| `Reg` | registration duty (on cars) |
| `Sub` | subsidies |
| `Direkte` | direct taxes |
| `Bund` | bottom-bracket income tax |
| `Mellem` | middle-bracket income tax |
| `Top` | top-bracket income tax |
| `Kommune` | municipal income tax |
| `Kirke` | church tax |
| `AM` | labour market contribution (arbejdsmarkedsbidrag) |
| `Selskab` | corporate income tax |
| `Virksomhed` | business tax scheme (virksomhedsskat) |
| `Ejd` | property value tax (ejendomsværdiskat) |
| `Grund` | land tax (grundskyld) |
| `Kulbrinte` | hydrocarbon tax |
| `PAL` | pension yield tax |
| `Kilde` | withholding taxes (kildeskatter) |
| `Doedsbo` | estate tax |
| `Arv` | inheritance, bequest |
| `AUB` | employers' education contribution |
| `Jordrente` | land and resource rent |
| `Lukning` | closing tax (closes the long-run government budget; not in the balance) |
| `Fradrag` | tax deduction |
| `Pers` | personal |
| `Skattepl` | taxable |
| `Ubeskat` | untaxed |
| `Vaegt` | weight |
| `Ovf` | transfers (overførsler) |
| `Sats` | benefit rate |
| `Bidrag` | contributions |
| `AK` | unemployment insurance fund (a-kasse) |
| `EL` | voluntary early retirement scheme (efterløn) |
| `ATP` | ATP labour market supplementary pension |
| `Tjmp` | civil servants' pensions |
| `Fri` | voluntary |
| `Obl` | compulsory (in `BidragObl`; elsewhere bonds) |
| `OP` | compulsory saving (obligatorisk opsparing) |
| `Pens` | pension |
| `Indb` | payments in (contributions) |
| `Udb` | payouts |
| `Til` | to (`OffTilHh` government to households) |
| `Fra` | from |

### Labour market and households

| Code | English |
| --- | --- |
| `Besk` | employment |
| `Ledig` | unemployed |
| `Arbsty` | labour force (arbejdsstyrke) |
| `Deltag` | participation |
| `Soeg` | job search |
| `Opslag` | vacancies (job postings) |
| `Match` | matching |
| `Job` | job |
| `Finding` | finding (`JobFinding`) |
| `Fuldtid` | full-time |
| `Orlov` | leave |
| `Bolig` | housing |
| `Leje` | rent |
| `Nytte` | utility |
| `Splurge` | splurge (hand-to-mouth) consumption |
| `Overlev` | survival (rate) |
| `Migration` | migration |
| `Demo` | demographic |
| `Traek` | pressure, demand (`DemoTraek` demographic pressure) |
| `Prod` | productivity |

### Modelling words

| Code | English |
| --- | --- |
| `Rest` | residual part, the rest |
| `Gab` | gap |
| `Traeghed` | inertia, stickiness (adjustment cost) |
| `Inst` | installation (costs) |
| `Omk` | cost |
| `Effekt` | effect |
| `Skala` | scale |
| `Sqr` | squared |
| `Ref` | reference |
| `Ny` | new |
| `Oevrig` | other |
| `Dir` | direct |
| `Indir` | indirect |
| `Pos` | positive |
| `Neg` | negative |
| `Lag` | lagged (previous year) |
| `Lead` | next year |
| `Marginal` | marginal |
| `Input` | input |
| `Salg` | sales |
| `Erhverv` | business sector |
| `Inv` | investment |
| `Komp` | compensation (replacement rate) |
| `Korrektion` | correction |
| `Kor` | correction |
| `Friktion` | friction |
| `Persistens` | persistence |
| `Matching` | matching |
| `Error` | error |
| `Rigid` | rigid (slow-moving) |
| `Traeg` | inertia |
| `Snit` | average (gennemsnit) |
| `Lsnit` | labour, moving average (`2hLsnit`) |
| `Alternativ` | alternative (outside option) |
| `Nash` | Nash bargaining |
| `Vaekst` | growth |
| `Diskripans` | discrepancy |
| `Res` | residual |
| `Def` | definition |
| `Inkl` | including |
| `Over` | over (`InklOver100`) |
| `Tot` | total |
| `Mv` | and more (m.v.) |
| `Af` | of |
| `U` | utility |

### More words

| Code | English |
| --- | --- |
| `Kap` | capital (capital transfers, capital income, capital pensions) |
| `Afskr` | depreciation (afskrivninger) |
| `Invest` | investment |
| `Investtilskud` | investment grant |
| `Koeb` | purchases |
| `Salg` | sales |
| `Loensum` | wage bill |
| `Loenkvote` | wage share |
| `Arb` | labour (arbejds-) |
| `Opsp` | saving (opsparing) |
| `Merafkast` | excess return |
| `Realisering` | realisation |
| `Urealiseret` | unrealised |
| `Aktier` | shares |
| `Praemie` | premium |
| `Spaend` | spread |
| `Kurs` | exchange rate, price of a security |
| `Dollar` | US dollar |
| `Olie` | oil |
| `Brent` | Brent oil price |
| `Grus` | gravel (extraction that is not phased out) |
| `Industri` | manufacturing industry |
| `Told` | customs duties |
| `Indirekte` | indirect taxes |
| `Bidrags` | contribution (`BidragsSats` mortgage contribution rate) |
| `Tillaeg` | supplement |
| `Bistand` | (development) aid |
| `Tidlig` | early |
| `Separation` | job separation |
| `Prog` | progression (tax bracket thresholds) |
| `Medie` | media cheque |
| `Oev` | other |
| `Tjm` | civil servants (tjenestemænd) |
| `Pl` | liable (`SkatPl` taxable) |
| `Biler` | cars |
| `Menergi` | imports of energy |
| `Mvarer` | imports of goods |
| `Mtjenester` | imports of services |
| `Xvarer` | exports of goods |
| `Xtjenester` | exports of services |
| `Cturisme` | tourists' consumption |
| `Ibm` | building and machinery investment |
| `IOe` | input-output delivery of energy |
| `IOym` | input-output delivery, domestic and imported |
| `Yfixed` | fixed costs of production |
| `Yoff` | public output |
| `HBI` | fiscal sustainability indicator (holdbarhedsindikator) |
| `NPISH` | non-profit institutions serving households |
| `FO` | the Faroe Islands |
| `WACC` | weighted average cost of capital |
| `EBITDA` | earnings before interest, taxes, depreciation and amortisation |
| `EBT` | earnings before taxes |
| `FCFE` | free cash flow to equity |
| `CO2` | CO2 (emission allowances) |
| `Ep` | expected price (`EpC`) |
| `Pal` | pension yield tax (PAL) |
| `Realkredit` | mortgage credit |
| `Realkred` | mortgage credit |
| `Udv` | extraction |
| `Givet` | given |
| `Udgift` | expenditure |
| `Disp` | disposable |
| `Outside` | outside (option) |
| `Option` | option |
| `Efter` | after |
| `Ejer` | owner (`EjerBolig` owner-occupied housing) |
| `Nulvaekst` | zero growth |
| `Indkomst` | income |
| `Statsgaeld` | central government debt |
| `Portf` | portfolio |
| `Udstedelser` | issues (of shares) |
| `Aar` | year(s) (`5aarSnit` five-year average) |
| `Handelsbalance` | trade balance |
| `Betalingsbalance` | current account (balance of payments) |

## Set elements (the parts after `__`)

Ages are plain numbers (`NPOP__45`); `NA` is the element before age 0 and holds
zeros. Element names are upper case in ModelFlow; the GAMS spelling is given in
brackets where it differs in more than case.

### Sectors (`s`, `sp`, and the `s` part of `d`)

| Code | English |
| --- | --- |
| `TJE` | private services excluding shipping |
| `FRE` | manufacturing excluding energy |
| `BYG` | construction |
| `LAN` | agriculture and fishing |
| `SOE` | shipping |
| `BOL` | housing |
| `ENE` | energy |
| `UDV` | extraction (oil and gas) |
| `OFF` | public sector |
| `TOT` | total (of the set the index runs over) |
| `SPTOT` | total of private sectors (`spTot`) |
| `SBYTOT` | total of private urban industries (`sByTot`) |

### Demand components (`d`, `c`, `x`, `i`, `g`)

| Code | English |
| --- | --- |
| `DTOT` | total demand (`dTot`) |
| `CTOT` | total private consumption (`cTot`) |
| `CBOL` | consumption: housing |
| `CBIL` | consumption: cars |
| `CENE` | consumption: energy |
| `CVAR` | consumption: goods |
| `CTJE` | consumption: services |
| `CTUR` | consumption: tourism |
| `CX` | consumption excluding housing and financial costs (`Cx`, a CES nest) |
| `CTURTJEX` | nest: tourism and services |
| `CTURTJEXVAR` | nest: tourism, services and goods |
| `CTURTJEXVARENE` | nest: tourism, services, goods and energy |
| `XTOT` | total exports (`xTot`) |
| `XVAR` | goods exports excluding energy |
| `XENE` | energy exports (SITC 3) |
| `XSOE` | shipping exports |
| `XTJE` | services exports excluding shipping and tourism |
| `XTUR` | tourism exports (foreign tourists in Denmark) |
| `ITOT` | total investment (`iTot`) |
| `IB` | building investment (`iB`) |
| `IM` | machinery investment, incl. transport and intangibles (`iM`) |
| `IL` | inventory investment incl. valuables and livestock (`iL`) |
| `GTOT` | total government consumption (`gTot`) |
| `G` | government consumption (the one group) |

### Financial portfolio (`portf`) and pensions (`pens`)

| Code | English |
| --- | --- |
| `OBL` | bonds excluding mortgage bonds |
| `REALKRED` | mortgage bonds |
| `INDLAKTIER` | Danish shares |
| `UDLAKTIER` | foreign shares |
| `BANK` | other claims, mainly bank deposits and loans |
| `GULD` | monetary gold and SDRs |
| `PENSTOT` | pension wealth, all pension types |
| `PENSX` | annuity pensions, taxed at payout |
| `KAP` | lump-sum (capital) pensions |
| `ALDER` | old-age savings, taxed at payment |

### Age groups (`a_`)

| Code | English |
| --- | --- |
| `A0T17` | ages 0-17 |
| `A15T100` | ages 15-100 (can be in the labour force) |
| `A18T100` | ages 18-100 (consumption is modelled) |

### Socio-economic groups and transfers (`soc`, `ovf`)

The labour-market status set of the Ministry of Finance (about 50 elements) and
the transfer types. The most common:

| Code | English |
| --- | --- |
| `BESK` | employed n.e.c. |
| `LEDDAG` | unemployed, insured |
| `LEDKONT` | unemployed, not insured |
| `DLEDDAG` | partly unemployed, insured |
| `AKTDAG` | in activation, insured |
| `KONTHJ` | cash benefit recipients |
| `SYGE` | sickness benefit recipients |
| `BARSEL` | parental leave |
| `ORLOV` | labour market leave |
| `UDDSU` | students with student grant |
| `UDDXSU` | students without student grant |
| `FORTID` | early (disability) pensioners |
| `EFTERL` | voluntary early retirement |
| `FLEKSYD` | flexible early retirement |
| `PENSION` | public old-age pensioners |
| `SENIORPENS` | senior pension |
| `TIDLPENS` | early retirement (from 2020) |
| `TJMAND` | civil servant pensioners |
| `OVRIGE` | others outside the labour force |
| `BOERN` | children aged 0-14 |
| `HHTOT` | total transfers to households |
| `UDLTOT` | total transfers abroad |
| `BOLIGST` | housing benefit |
| `BOERNYD` | child benefit |
| `GROEN` | green cheque |

Elements starting `BESK` are employed persons in a group, `SBESK` persons in
subsidised employment, `UDL` transfers paid abroad. The full list with Danish
texts is in `MAKRO_src\Model\Sets\befolkning.sets.gms`.
