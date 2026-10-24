---
description: Maswali yanayoulizwa mara kwa mara kuhusu sequential-analysis, maktaba ya Python ya majaribio ya mfuatano na makisio halali wakati wowote - usakinishaji, leseni na matumizi ya kibiashara, majaribio ya A/B katika uzalishaji, majaribio ya kliniki, nguvu, kasi, TypeScript, jinsi ya kunukuu.
language: sw
---

# Maswali yanayoulizwa mara kwa mara

> Hii ni tafsiri ya [ukurasa wa Kiingereza](../../guide/faq.md). Bado haijakaguliwa na mzungumzaji mzawa; pale ambapo hizi mbili zinatofautiana, ukurasa wa Kiingereza ndio wenye mamlaka.

## Kuhusu maktaba

### sequential-analysis ni nini?

Ni maktaba ya Python ya makisio ya kitakwimu ya mfuatano (sequential
inference). Majaribio yake, mifuatano ya uhakika (confidence sequences)
na vigunduzi vyake vinaweza kukaguliwa baada ya kila kipimo
(observation) na kusimamishwa wakati wowote, bila kupoteza hakikisho
zake za makosa. Ina:

* SPRT;
* miundo ya mfuatano wa vikundi (group sequential designs);
* majaribio ya A/B halali wakati wowote (anytime-valid);
* vigunduzi vya sehemu za mabadiliko;
* vichujio vya Kalman, vichujio vya chembe na vichujio vya Markov
  vilivyofichika;
* utabiri na GARCH.

Vyote vinaendeshwa nyuma ya kiolesura kimoja chenye vituo vya ukaguzi
(checkpoints) vya JSON. Inatengenezwa na Novikov Laboratories LLC.

### Ninaisakinishaje? Inategemea nini?

`pip install sequential-analysis`. Inahitaji Python 3.8 au toleo jipya
zaidi (imejaribiwa hadi 3.14) na hakuna kingine. `pip install "sequential-analysis[fast]"`
inaongeza numpy kwa taratibu zinazofanya kazi kwenye safu (arrays).
pandas, polars, wateja wa Kafka na matplotlib vinatumika tu ukiita
adapta (adapters) au vitendakazi vya kuchora.

### Je, ni bure kwa matumizi ya kibiashara?

Ina leseni mbili: AGPL-3.0 na leseni ya kibiashara. Matumizi haya ni bure
chini ya AGPL:

* utafiti na ufundishaji;
* miradi ya chanzo huria chini ya AGPL au GPL v3;
* matumizi ya ndani katika shirika, bila nakala kutolewa kwa wengine na
  bila ufikiaji kupitia mtandao kwa watu walio nje ya shirika hilo.

Bidhaa ya chanzo kilichofungwa, au huduma ya mtandao ambayo msimbo chanzo
wake hauuchapishi, inahitaji leseni ya kibiashara. Jedwali lililo katika
[COMMERCIAL.md](https://github.com/andre-a-no/sequential-analysis/blob/main/COMMERCIAL.md)
linaamua kesi hizo. Maswali kuhusu leseni: andrei@hobukob.ru.

### Ninainukuuje?

[CITATION.cff](https://github.com/andre-a-no/sequential-analysis/blob/main/CITATION.cff)
katika hazina (repository) inatoa unukuu, na kitufe cha GitHub *Cite
this repository* kinaugeuza kuwa BibTeX au APA. Matoleo yanahifadhiwa
kwenye Zenodo pamoja na DOI. Mbinu na ukaguzi wake zimeelezwa katika
[makala](https://github.com/andre-a-no/sequential-analysis/blob/main/paper/main.pdf).

## Kuitumia

### Je, ninaweza kuitumia kwa majaribio ya A/B katika uzalishaji?

Ndiyo, kama injini ya kitakwimu. Inatoa majaribio kamili kwa:

* ubadilishaji (`TwoProportionTest`);
* vipimo vyenye mipaka (`BoundedABTest`);
* viwango (`RateRatioTest`);
* mgawanyo wa trafiki (`SampleRatioMismatch`);
* vipimo vingi pamoja na udhibiti wa kiwango cha ugunduzi wa uongo
  (false discovery rate) (`MultipleTests`).

Katika Python tupu, jaribio la ubadilishaji linachukua takriban
mikrosekunde 10 kwa kila mtumiaji, ukaguzi wa mgawanyo 4 na jaribio la
viwango 40. Kituo cha ukaguzi cha kila kimoja kinachukua kilobaiti 2–4.
`BoundedABTest` inahifadhi gridi na inachukua 0.1–0.5 ms.

Maktaba hii si jukwaa la majaribio: ugawaji, ukusanyaji wa matukio na
dashibodi ni vyako kujenga au kuchukua kutoka kwa jukwaa. Tazama
[majaribio ya A/B](ab-testing.md).

### Je, ninaweza kuchungulia matokeo kila siku?

Ndiyo, kwa taratibu halali wakati wowote: hilo ndilo lengo lake. Kwa
muundo wa mfuatano wa vikundi, tazama tu katika chambuzi zilizopangwa.
Kwa jaribio la kawaida la sampuli isiyobadilika, tazama mara moja.
Tazama [kuchungulia](peeking.md).

### Je, jaribio halali wakati wowote lina nguvu ndogo kuliko jaribio la sampuli isiyobadilika?

Katika athari ambayo jaribio la sampuli isiyobadilika limepangwa kwayo,
ndiyo. Ili kufikia nguvu ile ile, jaribio halali wakati wowote la uwiano
miwili linahitaji mara 1.3–1.6 ya watumiaji. Kwa malipo yake unaweza
kusimama mapema athari inapokuwa kubwa zaidi, na huhitaji ukubwa wa
sampuli uliowekwa mapema. Muundo wa mfuatano wa vikundi wenye matazamo
machache yaliyopangwa unagharimu 1–20% tu zaidi ya uchambuzi mmoja.

### Mfuatano wa vikundi au halali wakati wowote: nitumie kipi?

* **Mfuatano wa vikundi** ikiwa chambuzi ni chache na zimepangwa, kama
  ilivyo kwa kamati ya ufuatiliaji wa data au mzunguko wa matoleo, na
  hasa kwa jaribio la kliniki la uthibitisho.
* **Halali wakati wowote** ikiwa unataka kutazama mfululizo, au huwezi
  kusema mapema ni lini utatazama au kusimama.

### Je, inafanya majaribio ya A/B ya Bayesian?

Majaribio yake ya A/B ni ya kifrikwensia (frequentist), yenye hakikisho
kuhusu viwango vya makosa. Vipengele vya Bayesian vinapatikana pale
vinapofaa:

* `ThompsonAllocation` inapeleka trafiki kulingana na uwezekano wa
  posterior kwamba kila kundi ndilo bora, pamoja na kanuni ya hasara
  inayotarajiwa kwa ajili ya kusambaza;
* `BayesianChangePoint` inagundua sehemu za mabadiliko;
* vitabiri hujifunza paramita zao kwa usasishaji wa Bayesian.

### Je, imethibitishwa kwa majaribio ya kliniki?

Miundo yake ya mfuatano wa vikundi (mipaka, nguvu, ukubwa wa sampuli,
idadi ya matukio) inakaguliwa dhidi ya rpact na kifurushi cha survival
cha R katika seti ya majaribio. Si programu iliyothibitishwa kwa maana
ya kisheria (regulatory). Mfadhili anayeitumia kwa uwasilishaji
anaithibitisha kama zana nyingine yoyote. Tazama
[majaribio ya kliniki](clinical-trials.md).

### Kipimo changu kina mikia mizito (mapato, muda wa kuchelewa). Nitumie nini?

* Kwa kwantili (wastani wa kati, pasentaili ya 90), tumia `QuantileTest`
  au `QuantileConfidenceSequence`, ambazo hazihitaji dhana yoyote.
* Kwa wastani, weka kikomo kwa thamani katika kiwango kilichowekwa mapema
  na tumia `BoundedABTest` au `BettingConfidenceSequence` (exact).
* Vinginevyo, chukulia mpaka wa mkengeuko sanifu na tumia
  `CatoniConfidenceSequence`.

Jaribio la sampuli mbili la wastani wa kati (median) bado halipo katika
maktaba.

### Ina kasi kiasi gani?

Taratibu rahisi zaidi zinachukua mikrosekunde 1–10 kwa kila kipimo
katika Python tupu: SPRT, CUSUM, majaribio ya mfuatano wa vikundi na ya
mchanganyiko, GARCH. Zile zinazohifadhi gridi au sampuli nzima
zinachukua 0.1–10 ms. Mifano ni mifuatano ya uhakika ya kuweka dau na ya
Catoni, jaribio la kernel na vitabiri vinavyojifunza.
[Kasi](../../performance.md) inaorodhesha gharama na ukubwa wa kituo cha
ukaguzi kwa kila utaratibu.

### Je, ninaweza kuiendesha katika JavaScript au kwenye kivinjari?

Ndiyo. Kitekelezaji cha TypeScript katika `ts/` kinaendesha taratibu na
kuendeleza vituo vya ukaguzi vya Python. Muhtasari wa historia (history
digest) na maamuzi vinafanana kabisa, na namba zinakubaliana hadi biti za
mwisho. Tazama [kitekelezaji cha TypeScript](../../typescript.md).

### Je, uendeshaji unaweza kunusurika mfumo ukianguka?

Ndiyo. `run.checkpoint()` ni JSON ya kawaida, na `Run.restore` inaendelea
biti kwa biti. Vipimo vinavyowasilishwa tena vinatupwa. Tazama
[mikondo ya data](streaming.md).

### "exact" na "asymptotic" zina maana gani katika nyaraka?

Sifa ya `guarantee` ya kila utaratibu inataja ahadi yake:

* `exact`: kiwango cha makosa kinashikilia katika kila ukubwa wa sampuli
  chini ya dhana zilizotajwa;
* `asymptotic`: kwa ukaribu, katika uendeshaji mrefu;
* `model`: kamili chini ya modeli iliyotajwa;
* `approximate`;
* `none`.

Nyaraka zinapendekeza utaratibu kamili pale unapofaa. Tazama
[Mbinu ipi?](../../choosing.md).
