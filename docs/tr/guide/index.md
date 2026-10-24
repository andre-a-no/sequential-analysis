---
description: Ardışık testler ve her an geçerli çıkarım için bir Python kütüphanesi olan sequential-analysis'in kullanıcı kılavuzu. Her sayfa tek bir soruyu doğrudan yanıtlar ve çalışan kodu çıktısıyla birlikte verir.
language: tr
---

# Kullanıcı kılavuzu

> Bu sayfa [İngilizce sayfanın](../../guide/index.md) çevirisidir. Henüz anadili Türkçe olan biri tarafından gözden geçirilmemiştir; iki metin arasında fark olduğunda İngilizce sayfa esas alınır.

Bu kılavuz, insanların sorduğu sorulara göre düzenlenmiştir. Her sayfa
doğrudan bir yanıtla açılır; ardından yazıldığı gibi çalışan kısa bir
program, bu programın çıktısı, yanıtın dayandığı garanti ve yöntemin
uygulanamadığı durumlar gelir. [Eğitimler](../../tutorials/ab-test.md)
her konuyu daha ayrıntılı ele alır.

## Tek paragrafta kütüphane

**sequential-analysis**, verilerin birer gözlem hâlinde geldiği
durumlarda istatistiksel çıkarım yapmak için bir Python kütüphanesidir.
Testlerine, güven aralıklarına ve dedektörlerine her gözlemden sonra
bakılabilir, istenen her an durdurulabilirler ve hata oranları yine de
geçerliliğini korur. Kapsadığı konular:

* Wald'ın ardışık olasılık oranı testi (SPRT) ve optimal ardışık planlar;
* klinik araştırmalar için grup ardışık tasarımlar (group sequential
  designs) (O'Brien–Fleming ve Pocock harcama fonksiyonları, yararsızlık
  sınırları);
* e-değerleri (e-values) ve güven dizileri (confidence sequences) ile her
  an geçerli (anytime-valid) A/B testleri;
* değişim noktası tespiti (change-point detection);
* Kalman, parçacık ve gizli Markov filtreleri;
* tahminleme (forecasting) ve GARCH oynaklığı.

Her çalıştırma JSON olarak kontrol noktasına (checkpoint) kaydedilebilir
ve Python'da bit bit aynı biçimde sürdürülebilir ya da TypeScript
yürütücüsünde aynı kararlarla devam ettirilebilir.

| | |
|---|---|
| Kurulum | `pip install sequential-analysis` |
| İçe aktarma | `import sequential_analysis` |
| Python | 3.8 ile 3.14 arası, zorunlu bağımlılık yok (numpy isteğe bağlı) |
| Lisans | AGPL-3.0 ya da Novikov Laboratories LLC'den ticari lisans |
| Kaynak kod | <https://github.com/andre-a-no/sequential-analysis> |
| Belgeler | <https://andre-a-no.github.io/sequential-analysis/> |

## Sorular

**Kavramlar**

* [p-değerine neden her gün bakamam?](peeking.md) Gözetleme (peeking)
  sorunu ve ardışık yöntemlerin üç ailesi.
* [Sözlük](glossary.md): e-değeri, güven dizisi, alfa harcama, ARL ve
  diğer terimler, eş anlamlılarıyla birlikte.

**Görevler**

* [Bir A/B testini yanlış pozitifleri artırmadan nasıl erken durdururum?](ab-testing.md)
* [Bakmaya devam ettiğimde de geçerli kalan bir güven aralığını nasıl elde ederim?](confidence-sequences.md)
* [Wald'ın SPRT'sini Python'da nasıl çalıştırırım?](sprt.md)
* [Bir klinik araştırmanın ara analizlerini nasıl planlarım?](clinical-trials.md)
* [Bir ölçüm akışındaki değişimi nasıl tespit ederim?](change-detection.md)
* [Bir veri akışı üzerinde istatistik nasıl çalıştırılır ve çökmeden sonra nasıl sürdürülür?](streaming.md)

**Seçim**

* [Sorum için hangi yöntem?](../../choosing.md): tam tablo.
* [Diğer kütüphanelerle karşılaştırıldığında nasıl?](comparison.md)
* [Sık sorulan sorular](faq.md)

## Garantiler nasıl okunur

Her prosedürün bir `guarantee` özniteliği vardır. Kılavuz bunu her
yanıtla birlikte belirtir:

* **exact (kesin):** hata oranı, belirtilen varsayımlar altında her
  örneklem büyüklüğünde geçerlidir.
* **asymptotic (asimptotik):** yaklaşık olarak geçerlidir; örneklem
  büyüdükçe daha iyi geçerli olur.
* **model:** olasılıklar belirtilen model altında kesindir, ancak modelin
  ötesinde hiçbir iddiada bulunulmaz.
* **approximate (yaklaşık):** model altında bile bir yaklaşıklıktır.
* **none (yok):** prosedür veriyi dönüştürür ve hiçbir iddiada bulunmaz.
