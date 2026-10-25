---
description: Jinsi ya kugundua mabadiliko katika mkondo wa vipimo vya vihisi, muda wa kuchelewa au vipimo vingine katika Python, kwa CUSUM, Shiryaev–Roberts, vigunduzi-e visivyo vya kiparamita na ugunduzi wa Bayesian wa sehemu za mabadiliko mtandaoni. Tahadhari za uongo zinadhibitiwa kupitia wastani wa urefu wa mfululizo (ARL), kwa sequential-analysis.
language: sw
---

# Ninagunduaje mabadiliko katika mkondo wa vipimo?

> Hii ni tafsiri ya [ukurasa wa Kiingereza](../../guide/change-detection.md). Bado haijakaguliwa na mzungumzaji mzawa; pale ambapo hizi mbili zinatofautiana, ukurasa wa Kiingereza ndio wenye mamlaka.

**Jibu fupi.** Tumia kigunduzi cha sehemu ya mabadiliko mtandaoni (online
change-point detector). Kinafuatilia mkondo wa data na kutoa tahadhari
mara tu mgawanyo (distribution) unapoonekana kuwa umebadilika. Tahadhari
zake za uongo (false alarms) zinadhibitiwa na **wastani wa urefu wa
mfululizo** (average run length, ARL): idadi inayotarajiwa ya vipimo hadi
tahadhari ya uongo wakati hakuna kilichobadilika. Katika sequential-analysis:

| Unachojua kabla ya mabadiliko | Utaratibu | Hakikisho |
|---|---|---|
| migawanyo yote miwili (k.m. wa kawaida, wastani 70 → 71) | `CUSUM`, `ShiryaevRoberts` | exact: ARL ≥ e^threshold |
| wastani tu, na mipaka ya thamani | `MeanEDetector` | exact kwa kila mgawanyo wa aina hiyo |
| kwantili moja tu (k.m. pasentaili ya 95 ya muda wa kuchelewa) | `QuantileEDetector` | exact kwa kila mgawanyo |
| modeli yenye paramita zisizojulikana, kabla na baada | `BayesianChangePoint` | chini ya modeli na mgawanyo wa awali (prior) |

## Kihisi ambacho wastani wake unahama

Kihisi cha joto kinasoma 70.0 °C chenye kelele ya mkengeuko sanifu
(standard deviation) 0.5. Kuanzia kipimo cha 600, wastani ni 70.4. CUSUM
yenye kizingiti log(1000) ≈ 6.9 ina ARL ya angalau vipimo 1,000:

```python
import math
import random

from sequential_analysis.procedures import CUSUM, Gaussian

rnd = random.Random(1)
readings = [rnd.gauss(70.0, 0.5) for _ in range(600)] + [rnd.gauss(70.4, 0.5) for _ in range(400)]

detector = CUSUM(Gaussian(sigma=0.5), theta0=70.0, theta1=70.4, threshold=math.log(1000))
state = detector.initial_state()
for t, x in enumerate(readings, start=1):
    state, out = detector.step(state, {"x": x})
    if out.alarm:
        print(f"alarm at reading {t}, {t - 600} readings after the shift")
        break
```

```text
alarm at reading 615, 15 readings after the shift
```

Mhamo wa chini ya mkengeuko sanifu mmoja hauonekani kwa macho katika
kipimo chochote kimoja. CUSUM inakusanya ushahidi na kuugundua.

## Vipimo visipofuata mgawanyo wa kawaida

ARL ya CUSUM inashikilia tu ikiwa vipimo vinafuata migawanyo uliyoipa.
Kwa data zilizopinda (ukubwa wa mitetemo, muda wa kuchelewa, urefu wa
foleni) inatoa tahadhari za uongo mara nyingi zaidi sana kuliko
ilivyopangwa. Vigunduzi-e (e-detectors) vinahitaji kidogo zaidi sana:

* `MeanEDetector` inahitaji wastani kabla ya mabadiliko na mipaka ya
  thamani.
* `QuantileEDetector` inahitaji kwantili moja tu kabla ya mabadiliko.

ARL yao ni angalau lengo kwa **kila** mgawanyo wenye wastani au kwantili
hiyo:

```python
from sequential_analysis.procedures import QuantileEDetector

rnd = random.Random(2)
vibration = [rnd.lognormvariate(0.0, 0.8) for _ in range(800)] + [rnd.lognormvariate(0.5, 0.8) for _ in range(400)]
q95 = math.exp(0.8 * 1.6449)          # the 95th percentile before the change
p95 = QuantileEDetector(q0=q95, p=0.95, arl=1000, direction="increase", statistic="cusum")
state = p95.initial_state()
for t, x in enumerate(vibration, start=1):
    state, out = p95.step(state, {"x": x})
    if out.alarm:
        print(f"the 95th percentile rose: alarm at reading {t}, {t - 800} readings after the change")
        break
```

```text
the 95th percentile rose: alarm at reading 887, 87 readings after the change
```

Kiutendaji, kwantili ya kabla ya mabadiliko hukadiriwa kutoka kipindi
tulivu. Hakikisho basi linashikilia kwa ukaribu, na vizuri zaidi kadiri
kipindi hicho kinavyokuwa kirefu.

## Kuchagua ARL

ARL inabadilishana tahadhari za uongo na ucheleweshaji. Kwa kipimo kimoja
kwa dakika, ARL ya vipimo 1,000 inamaanisha tahadhari moja ya uongo kila
takriban saa 17 za uendeshaji wa kawaida, kwa kila kihisi. Kwa vihisi 50
hiyo ni takriban 70 kwa siku. Chagua ARL kutokana na idadi ya tahadhari
za uongo kwa siku unazoweza kumudu kwa vihisi vyote kwa pamoja: hapa, ARL
ya vipimo 1,000,000 inashusha vihisi 50 hadi takriban tahadhari moja ya
uongo kila wiki mbili. Gharama yake ni ndogo kuliko inavyoonekana, kwa
sababu ucheleweshaji wa ugunduzi unakua tu kwa logariti ya ARL. Kwa
CUSUM kizingiti kinatoka 6.9 hadi 13.8, na ucheleweshaji unakaribia
kuongezeka maradufu.

Vigunduzi hivi ni zana za ufuatiliaji, si mifumo ya usalama. Usivitumie
badala ya mfumo wa usalama wa vyombo uliothibitishwa.

Zaidi: [mafunzo: ufuatiliaji wa michakato na ugunduzi wa mabadiliko](../../tutorials/monitoring.md),
[hali (regimes) kwa modeli za Markov zilizofichika](../../tutorials/regimes.md),
[marejeo: ugunduzi wa mabadiliko](../../reference/detection.md).
