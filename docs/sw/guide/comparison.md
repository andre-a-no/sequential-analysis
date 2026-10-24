---
description: Jinsi sequential-analysis inavyolinganishwa na maktaba nyingine za Python na R za majaribio ya mfuatano, majaribio ya A/B, miundo ya mfuatano wa vikundi, ugunduzi wa mabadiliko na uchujaji (statsmodels, scipy, confseq, rpact, gsDesign, safestats, ruptures, filterpy, arch, hmmlearn), na wakati wa kutumia ipi.
language: sw
---

# Inalinganishwaje na maktaba nyingine?

> Hii ni tafsiri ya [ukurasa wa Kiingereza](../../guide/comparison.md). Bado haijakaguliwa na mzungumzaji mzawa; pale ambapo hizi mbili zinatofautiana, ukurasa wa Kiingereza ndio wenye mamlaka.

**Jibu fupi.** Maktaba nyingi zinashughulikia familia moja ya mbinu
vizuri. sequential-analysis inaweka familia kuu za makisio ya mfuatano
(sequential inference) nyuma ya kiolesura kimoja:

* SPRT na mipango bora;
* miundo ya mfuatano wa vikundi (group sequential designs);
* majaribio halali wakati wowote (anytime-valid) na mifuatano ya uhakika
  (confidence sequences);
* ugunduzi wa mabadiliko;
* vichujio vya nafasi ya hali (state-space filters).

Inachoongeza zaidi ya mbinu zenyewe:

* kila utaratibu unataja hakikisho lake (`exact`, `asymptotic`, `model`,
  ...);
* kila uendeshaji unaweza kuhifadhiwa kama kituo cha ukaguzi na
  kuendelezwa biti kwa biti;
* fomati zimebainishwa na zinatekelezwa na utekelezaji wa pili katika
  TypeScript;
* hakuna utegemezi wa lazima.

Ikiwa unahitaji mbinu moja tu kati ya zilizo hapa chini na tayari
unatumia maktaba iliyobobea katika mbinu hiyo, endelea kutumia maktaba
hiyo. Jedwali linaonyesha mahali ambapo kila zana ndiyo chaguo la
kawaida. Maelezo yanahusu lengo kuu la kila maktaba, kufikia Oktoba 2026,
na si orodha kamili ya vipengele vyake.

| Hitaji | Machaguo ya kawaida | Kile sequential-analysis inachotoa |
|---|---|---|
| majaribio ya sampuli isiyobadilika, urejeshaji (regression), nguvu | scipy.stats, statsmodels | si lengo lake |
| miundo ya mfuatano wa vikundi kwa uwasilishaji kwa mamlaka ya udhibiti | rpact, gsDesign (R) | miundo ile ile, iliyokaguliwa dhidi ya rpact katika seti yake ya majaribio; inaendesha jaribio hatua kwa hatua kwa vituo vya ukaguzi |
| mifuatano ya uhakika, thamani-e | confseq (Python), safestats (R) | mifuatano ya uhakika kwa wastani, kwantili, vigawo vya urejeshaji, athari za sampuli mbili; e-BH na e-LOND kwa majaribio mengi |
| majaribio ya A/B kama jukwaa lenye UI | GrowthBook, Statsig, Eppo, Optimizely (majukwaa) | injini ya kupachika: majaribio kamili kwa ubadilishaji, vipimo vyenye mipaka na vya viwango, SRM, FDR kwa vipimo vingi |
| ugawaji wa sehemu za mabadiliko nje ya mtandao kwa mfululizo uliokamilika | ruptures (Python), changepoint (R) | ugunduzi mtandaoni data zinapowasili: CUSUM, Shiryaev–Roberts, vigunduzi-e, sehemu za mabadiliko za Bayesian mtandaoni |
| vichujio vya Kalman | filterpy, nafasi ya hali ya statsmodels | vichujio vya Kalman, Kalman imara, chembe na HMM, pamoja na ulainishaji na vituo vya ukaguzi |
| GARCH | arch | GARCH(1,1) na GJR zilizokadiriwa kwenye kiwango cha juu cha arch (kimekaguliwa katika majaribio), kisha kuendeshwa mtandaoni |
| modeli za Markov zilizofichika | hmmlearn | kichujio mtandaoni, Baum–Welch inayokubaliana na hmmlearn, EM mtandaoni |
| utabiri | statsmodels, nyinginezo | utabiri wa ETS na AR unaokubaliana na statsmodels, uliofunzwa mtandaoni, pamoja na vipindi vya conformal |

## Hali ambazo zana nyingine ni bora zaidi

* **Uwasilishaji kwa mamlaka ya udhibiti.** rpact inatumika sana kwa
  lengo hilo, na watengenezaji wake wanatoa nyaraka za uthibitishaji.
  sequential-analysis inakubaliana nayo kwa miundo inayoishughulikia,
  lakini mfadhili bado angehitaji kuithibitisha.
* **Chambuzi kubwa nje ya mtandao kwa safu (arrays).** Maktaba zinazotumia
  numpy ni za haraka zaidi kwa kila kipimo. sequential-analysis imejengwa
  kwa kipimo kimoja kwa wakati; tazama [Kasi](../../performance.md) kwa
  gharama ya kila utaratibu.
* **Mbinu ambazo haina.** Bado haina jaribio la sampuli mbili la wastani
  wa kati (median), haina michakato ya Hawkes ya vigeu vingi na haina
  modeli za ARIMA zenye vipengele vya wastani unaosonga (moving average).
  Tazama [kumbukumbu ya mabadiliko](../../changelog.md) kwa kile
  kinachoongezwa.
