---
description: Gabay sa paggamit ng sequential-analysis, isang Python library para sa sequential testing at anytime-valid inference. Bawat pahina ay direktang sumasagot sa isang tanong, kasama ang code na tumatakbo at ang output nito.
language: tl
---

# Gabay sa paggamit

> Ito ay salin ng [pahina sa Ingles](../../guide/index.md). Hindi pa ito nasusuri ng isang katutubong tagapagsalita ng wika; kung saan magkaiba ang dalawa, ang pahina sa Ingles ang masusunod.

Nakaayos ang gabay na ito ayon sa mga tanong na madalas itanong ng mga
tao. Nagsisimula ang bawat pahina sa direktang sagot, saka nagbibigay ng
maikling programang tumatakbo nang ayon sa pagkakasulat, ang output nito,
ang garantiya (guarantee) sa likod ng sagot, at ang mga kaso kung saan
hindi angkop ang pamamaraan. Mas pinalalalim ng mga
[tutorial](../../tutorials/ab-test.md) ang bawat paksa.

## Ang library sa isang talata

Ang **sequential-analysis** ay isang Python library para sa statistical
inference sa datos na dumarating nang paisa-isang obserbasyon. Ang mga
test, confidence interval at detector nito ay maaaring tingnan pagkatapos
ng bawat obserbasyon at ihinto sa anumang sandali, at nananatili pa rin
ang kanilang mga error rate. Saklaw nito ang:

* ang SPRT ni Wald at mga optimal na sequential plan;
* mga group sequential design para sa mga clinical trial (O'Brien–Fleming
  at Pocock spending, mga futility bound);
* mga anytime-valid na A/B test na may e-value at confidence sequence;
* change-point detection;
* mga Kalman filter, particle filter at hidden Markov filter;
* forecasting at GARCH volatility.

Bawat run ay maaaring i-checkpoint bilang JSON at ituloy nang eksakto
hanggang sa huling bit sa Python, o ituloy sa TypeScript executor nito
nang may parehong mga desisyon.

| | |
|---|---|
| Pag-install | `pip install sequential-analysis` |
| Pag-import | `import sequential_analysis` |
| Python | 3.8 hanggang 3.14, walang kailangang dependency (opsyonal ang numpy) |
| Lisensiya | AGPL-3.0, o commercial licence mula sa Novikov Laboratories LLC |
| Source | <https://github.com/andre-a-no/sequential-analysis> |
| Dokumentasyon | <https://andre-a-no.github.io/sequential-analysis/> |

## Mga tanong

**Mga konsepto**

* [Bakit hindi ko puwedeng tingnan ang p-value araw-araw?](peeking.md) Ang
  pagsilip (peeking), at ang tatlong pamilya ng mga sequential method.
* [Glosaryo](glossary.md): e-value, confidence sequence, alpha spending,
  ARL at iba pang termino, kasama ang kanilang mga kasingkahulugan.

**Mga gawain**

* [Paano ihinto nang maaga ang isang A/B test nang hindi lumalaki ang false positives?](ab-testing.md)
* [Paano makakuha ng confidence interval na nananatiling valid kahit paulit-ulit akong tumitingin?](confidence-sequences.md)
* [Paano patakbuhin ang SPRT ni Wald sa Python?](sprt.md)
* [Paano magplano ng mga interim analysis ng isang clinical trial?](clinical-trials.md)
* [Paano matukoy ang pagbabago sa isang stream ng mga sukat?](change-detection.md)
* [Paano magpatakbo ng estadistika sa isang stream at magpatuloy pagkatapos ng crash?](streaming.md)

**Pagpili**

* [Aling pamamaraan para sa tanong ko?](../../choosing.md): ang buong talahanayan.
* [Paano ito ihahambing sa ibang mga library?](comparison.md)
* [Mga madalas itanong](faq.md)

## Paano basahin ang mga garantiya

Bawat procedure ay may attribute na `guarantee`. Sinisipi ito ng gabay
kasama ng bawat sagot:

* **exact:** nananatili ang error rate sa bawat sample size, sa ilalim ng
  mga nakasaad na assumption.
* **asymptotic:** nananatili ito nang humigit-kumulang, at mas mahusay
  kapag mas malaki ang sample.
* **model:** eksakto ang mga probabilidad sa ilalim ng nakasaad na model,
  pero walang inaangkin lampas dito.
* **approximate:** isang approximation kahit sa ilalim ng model.
* **none:** binabago lamang ng procedure ang datos at wala itong
  inaangking anuman.
