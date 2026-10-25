---
description: Mwongozo wa mtumiaji wa sequential-analysis, maktaba ya Python ya majaribio ya mfuatano (sequential testing) na makisio halali wakati wowote (anytime-valid inference). Kila ukurasa unajibu swali moja moja kwa moja, kwa msimbo unaoendeshwa pamoja na matokeo yake.
language: sw
---

# Mwongozo wa mtumiaji

> Hii ni tafsiri ya [ukurasa wa Kiingereza](../../guide/index.md). Bado haijakaguliwa na mzungumzaji mzawa; pale ambapo hizi mbili zinatofautiana, ukurasa wa Kiingereza ndio wenye mamlaka.

Mwongozo huu umepangwa kulingana na maswali ambayo watu huuliza. Kila
ukurasa unaanza na jibu la moja kwa moja, kisha unatoa programu fupi
inayoendeshwa kama ilivyoandikwa, matokeo yake, hakikisho lililo nyuma ya
jibu hilo, na hali ambazo mbinu hiyo haitumiki. [Mafunzo](../../tutorials/ab-test.md)
yanaingia ndani zaidi katika kila mada.

## Maktaba hii kwa aya moja

**sequential-analysis** ni maktaba ya Python ya makisio ya kitakwimu
(statistical inference) kwa data zinazowasili kipimo kimoja (observation)
baada ya kingine. Majaribio yake, vipindi vya uhakika (confidence
intervals) na vigunduzi vyake vinaweza kutazamwa baada ya kila kipimo na
kusimamishwa wakati wowote, na viwango vyake vya makosa bado vinashikilia.
Inashughulikia:

* SPRT ya Wald na mipango bora ya mfuatano;
* miundo ya mfuatano wa vikundi (group sequential designs) kwa majaribio
  ya kliniki (matumizi ya alfa ya O'Brien–Fleming na Pocock, mipaka ya
  kutofaa);
* majaribio ya A/B halali wakati wowote kwa thamani-e (e-values) na
  mifuatano ya uhakika (confidence sequences);
* ugunduzi wa sehemu za mabadiliko (change-point detection);
* vichujio vya Kalman, vichujio vya chembe (particle filters) na vichujio
  vya Markov vilivyofichika;
* utabiri na kubadilika-badilika kwa GARCH (volatility).

Kila uendeshaji unaweza kuhifadhiwa kama kituo cha ukaguzi (checkpoint)
cha JSON na kuendelezwa tena katika Python biti kwa biti, au kuendelezwa
katika kitekelezaji chake cha TypeScript kwa maamuzi yale yale.

| | |
|---|---|
| Usakinishaji | `pip install sequential-analysis` |
| Kuingiza | `import sequential_analysis` |
| Python | 3.8 hadi 3.14, hakuna utegemezi wa lazima (numpy ni hiari) |
| Leseni | AGPL-3.0, au leseni ya kibiashara kutoka Novikov Laboratories LLC |
| Msimbo chanzo | <https://github.com/andre-a-no/sequential-analysis> |
| Nyaraka | <https://andre-a-no.github.io/sequential-analysis/> |

## Maswali

**Dhana**

* [Kwa nini siwezi kutazama thamani-p kila siku?](peeking.md) Kuchungulia
  (peeking), na familia tatu za mbinu za mfuatano.
* [Faharasa](glossary.md): thamani-e, mfuatano wa uhakika, matumizi ya
  alfa, ARL na istilahi nyingine, pamoja na visawe vyake.

**Kazi**

* [Ninasimamishaje jaribio la A/B mapema bila kuongeza chanya za uongo?](ab-testing.md)
* [Ninapataje kipindi cha uhakika kinachobaki halali ninapoendelea kutazama?](confidence-sequences.md)
* [Ninaendeshaje SPRT ya Wald katika Python?](sprt.md)
* [Ninapangaje uchambuzi wa kati wa jaribio la kliniki?](clinical-trials.md)
* [Ninagunduaje mabadiliko katika mkondo wa vipimo?](change-detection.md)
* [Ninaendeshaje takwimu kwenye mkondo wa data na kuendelea baada ya mfumo kuanguka?](streaming.md)

**Kuchagua**

* [Mbinu ipi kwa swali langu?](../../choosing.md): jedwali kamili.
* [Inalinganishwaje na maktaba nyingine?](comparison.md)
* [Maswali yanayoulizwa mara kwa mara](faq.md)

## Jinsi ya kusoma hakikisho

Kila utaratibu una sifa ya `guarantee`. Mwongozo huu unainukuu pamoja na
kila jibu:

* **exact:** kiwango cha makosa kinashikilia katika kila ukubwa wa sampuli
  chini ya dhana zilizotajwa.
* **asymptotic:** kinashikilia kwa ukaribu, na vizuri zaidi kwa sampuli
  kubwa zaidi.
* **model:** uwezekano ni kamili chini ya modeli iliyotajwa, lakini
  hakuna kinachodaiwa nje yake.
* **approximate:** ni ukadiriaji hata chini ya modeli.
* **none:** utaratibu unabadilisha data na haudai chochote.
