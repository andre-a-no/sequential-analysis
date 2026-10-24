---
description: Faharasa ya istilahi za uchambuzi wa mfuatano na makisio halali wakati wowote - thamani-e, mchakato-e, mfuatano wa uhakika, thamani-p halali daima, mSPRT, matumizi ya alfa, sehemu ya taarifa, ARL, SRM, CUPED, e-BH - pamoja na visawe na taratibu za sequential-analysis zinazotekeleza kila moja.
language: sw
---

# Faharasa

> Hii ni tafsiri ya [ukurasa wa Kiingereza](../../guide/glossary.md). Bado haijakaguliwa na mzungumzaji mzawa; pale ambapo hizi mbili zinatofautiana, ukurasa wa Kiingereza ndio wenye mamlaka.

Istilahi zinazotumika katika uchambuzi wa mfuatano na katika maktaba hii.
Visawe vinavyotumika kwa kawaida vimetolewa katika mabano.

**Uchambuzi wa mfuatano** (sequential analysis; sequential testing,
sequential inference). Takwimu ambazo idadi ya vipimo haijawekwa mapema.
Baada ya kila kipimo au kikundi cha vipimo, utaratibu unaamua kama
usimame au uendelee. Ulianzishwa na Wald (1945).

**Kuchungulia** (peeking; optional stopping, data peeking, continuous
monitoring). Kutazama jaribio la sampuli isiyobadilika mara kwa mara na
kusimama linapokuwa na umuhimu wa kitakwimu. Kunaongeza kiwango cha
chanya za uongo; tazama [kuchungulia](peeking.md).

**SPRT** (sequential probability ratio test, jaribio la mfuatano la
uwiano wa uwezekano, jaribio la Wald). Linakusanya logariti ya uwiano wa
uwezekano (likelihood ratio) wa nadharia tete mbili sahili na kusimama
linapotoka nje ya kipindi fulani. `SPRT`; matoleo yaliyokatwa `TwoSPRT`
(2-SPRT ya Lorden) na `kiefer_weiss_plan`. Tazama [SPRT](sprt.md).

**Muundo wa mfuatano wa vikundi** (group sequential design; interim
analyses, group sequential trial). Chambuzi chache zilizopangwa, kila
moja ikiwa na mpaka. Mipaka huchaguliwa ili kosa la aina ya kwanza (type
I error) la jumla liwe alfa.
`group_sequential_design`. Tazama [majaribio ya kliniki](clinical-trials.md).

**Kitendakazi cha matumizi ya alfa** (alpha spending function; error
spending, Lan–DeMets). Kinaeleza ni kiasi gani cha kosa la aina ya
kwanza kinaweza kutumika hadi kila sehemu ya taarifa. Matumizi ya aina
ya O'Brien–Fleming yanatumia kidogo mwanzoni, matumizi ya aina ya Pocock
yanatumia kwa usawa. `spending="obrien-fleming"`, `"pocock"`, ...

**Sehemu ya taarifa** (information fraction). Sehemu ya taarifa ya
kitakwimu iliyopangwa (wagonjwa, matukio) iliyofikiwa katika uchambuzi.

**Mpaka wa kutofaa** (futility boundary; non-binding futility). Mpaka wa
chini: chini yake, kusimama kwa sababu ya kukosekana kwa athari
kunapendekezwa. Mpaka usiolazimisha unaweza kupuuzwa bila kuongeza kosa
la aina ya kwanza.

**Makisio halali wakati wowote** (anytime-valid inference; always-valid
inference, safe anytime-valid inference, SAVI). Majaribio na vipindi
ambavyo hakikisho zake zinashikilia katika kila ukubwa wa sampuli kwa
wakati mmoja, kwa hiyo vinaweza kufuatiliwa mfululizo na kusimamishwa
kwa sababu yoyote.

**Thamani-e** (e-value; e-variable, betting score). Takwimu isiyo hasi
ambayo matarajio yake chini ya nadharia tete sifuri (null hypothesis) si
zaidi ya 1. Thamani-e kubwa ni ushahidi dhidi ya nadharia tete
sifuri: kukataa inapozidi 1/alpha kuna kosa la aina ya kwanza lisilozidi
alfa. Tokeo la `log_e_value` la taratibu nyingi.

**Mchakato-e** (e-process; test martingale, test supermartingale, wealth
process). Mfuatano wa thamani-e unaobaki halali katika nyakati za
kusimama. Kiwango chake cha juu kinachoendelea kinavuka 1/alpha kwa
uwezekano usiozidi alfa chini ya nadharia tete sifuri (ukosefu wa usawa wa
Ville, Ville's inequality).

**Thamani-p halali daima** (always-valid p-value; anytime-valid p-value,
sequential p-value). Thamani-p iliyo halali katika wakati wowote wa
kusimama. Ni kinyume (inverse) cha kiwango cha juu kinachoendelea cha
mchakato-e. Tokeo la `p_value` la taratibu halali wakati wowote.

**Mfuatano wa uhakika** (confidence sequence; anytime-valid confidence
interval, always-valid confidence interval, time-uniform confidence
interval). Mfuatano wa vipindi unaojumuisha thamani halisi katika ukubwa
wote wa sampuli kwa wakati mmoja kwa uwezekano wa angalau 1 − alpha.
`BettingConfidenceSequence`, `QuantileConfidenceSequence`,
`CatoniConfidenceSequence`, `AsymptoticConfidenceSequence`, na matokeo ya
`lower` na `upper` ya majaribio mengi. Tazama
[mifuatano ya uhakika](confidence-sequences.md).

**mSPRT** (mixture SPRT, SPRT ya mchanganyiko, mchanganyiko wa Robbins).
SPRT ambayo nadharia tete mbadala yake inachukuliwa wastani juu ya
mgawanyo wa awali (prior), jambo linaloifanya kuwa halali wakati wowote
dhidi ya kila mbadala. `NormalMixtureSPRT` (variansi inayojulikana),
`TMixtureSPRT` (variansi isiyojulikana).

**Kujaribu kwa kuweka dau** (testing by betting). Kujenga michakato-e
kama utajiri wa mcheza kamari anayeweka dau dhidi ya nadharia tete sifuri.
`BettingMeanTest`, `BettingConfidenceSequence`, `KernelTwoSampleTest`.

**GROW** (growth-rate optimal, bora kwa kiwango cha ukuaji). Thamani-e
iliyochaguliwa ili kuongeza hadi kiwango cha juu ukuaji wa logariti
unaotarajiwa wa ushahidi chini ya nadharia tete mbadala.
`TwoProportionTest(method="grow")`.

**Makisio ya kiulimwengu** (universal inference). Thamani-e kutoka kwa
uwiano wa uwezekano ambapo mbadala unakadiriwa kutoka kwa data za awali
pekee. Inabaki halali chini ya miundo inayojirekebisha.
`TwoProportionTest(method="universal")`.

**e-BH** (e-Benjamini–Hochberg). Inadhibiti kiwango cha ugunduzi wa
uongo (false discovery rate) kwa thamani-e nyingi, chini ya utegemeano
wowote. `MultipleTests`, `e_bh`.

**e-LOND, FDR mtandaoni** (online FDR). Udhibiti wa kiwango cha ugunduzi
wa uongo kwa mfululizo wa nadharia tete zinazoamuliwa moja baada ya
nyingine. `OnlineFDR`.

**SRM** (sample ratio mismatch, kutolingana kwa uwiano wa sampuli).
Mgawanyo wa trafiki ulioonekana kati ya makundi unatofautiana na ule
uliosanidiwa, ishara ya hitilafu katika jaribio. `SampleRatioMismatch`.

**CUPED** (controlled experiments using pre-experiment data; covariate
adjustment, regression adjustment). Inapunguza variansi ya athari ya A/B
kwa kigezo shirikishi (covariate) kilichopimwa kabla ya jaribio.
`ABTest(covariate=True)`, `AnytimeLinearModel`.

**Kipimo cha uwiano** (ratio metric; delta method). Kipimo ambacho ni
uwiano wa jumla mbili kwa kila mtumiaji, kama mapato kwa kila kipindi
cha matumizi (session). `RatioABTest`.

**Ugunduzi wa sehemu ya mabadiliko** (change-point detection; change
detection, quickest detection, online anomaly detection). Kutoa
tahadhari muda mfupi baada ya mgawanyo wa mkondo wa data kubadilika.
`CUSUM`, `ShiryaevRoberts`, `MeanEDetector`, `QuantileEDetector`,
`BayesianChangePoint`. Tazama [ugunduzi wa mabadiliko](change-detection.md).

**ARL** (average run length, wastani wa urefu wa mfululizo, ARL₀, mean
time to false alarm). Idadi inayotarajiwa ya vipimo hadi tahadhari ya
uongo wakati hakuna kilichobadilika. Udhibiti wa tahadhari za uongo wa
vigunduzi vya mabadiliko.

**Kigunduzi-e** (e-detector). Kigunduzi cha mabadiliko kilichojengwa
kutoka kwa michakato-e, mmoja ukianzishwa katika kila wakati
unaowezekana wa mabadiliko. ARL yake imehakikishwa chini ya nadharia tete
sifuri isiyo ya kiparamita. `MeanEDetector`, `QuantileEDetector`.

**Tatizo la Kiefer–Weiss** (Kiefer–Weiss problem). Kutafuta jaribio la
mfuatano lenye ukubwa wa juu wa sampuli linalopunguza hadi kiwango cha
chini ukubwa mkubwa zaidi wa sampuli unaotarajiwa.
`kiefer_weiss_plan`.

**Sifa ya utendaji** (operating characteristic). Uwezekano wa makosa na
mgawanyo wa ukubwa wa sampuli wa mpango, kama vitendakazi vya paramita
halisi. `operating_characteristic`.

**Kituo cha ukaguzi** (checkpoint). Thamani ya JSON ambayo kutoka kwayo
uendeshaji unaendelea kwa usahihi kamili. `Run.checkpoint`,
`Run.restore`. Tazama [mikondo ya data](streaming.md).

**Muhtasari wa historia** (history digest). Mnyororo wa hash wa SHA-256
juu ya vipimo ambavyo uendeshaji umetumia, unaohifadhiwa katika kila
kituo cha ukaguzi, kwa ajili ya ukaguzi wa hesabu (audit).

**Hakikisho** (guarantee; `exact`, `asymptotic`, `model`, `approximate`,
`none`). Sifa ambayo kupitia kwayo kila utaratibu katika maktaba hii
unataja kile unachoahidi. Tazama [Mbinu ipi?](../../choosing.md).
