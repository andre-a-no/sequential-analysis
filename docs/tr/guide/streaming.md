---
description: Bir veri akışı (Kafka, SQL, pandas, sensörler) üzerinde ardışık istatistik çalıştırma ve bir çökmeden sonra tam kaldığı yerden sürdürme. JSON kontrol noktaları, tekilleştirilmiş teslimat, denetim için geçmiş özeti ve aynı çalıştırmanın Python'da ya da TypeScript'te sürdürülmesi, sequential-analysis ile.
language: tr
---

# Bir veri akışı üzerinde istatistik nasıl çalıştırılır ve çökmeden sonra nasıl sürdürülür?

> Bu sayfa [İngilizce sayfanın](../../guide/streaming.md) çevirisidir. Henüz anadili Türkçe olan biri tarafından gözden geçirilmemiştir; iki metin arasında fark olduğunda İngilizce sayfa esas alınır.

**Kısa yanıt.** Prosedürü bir `Run` içine sarın. Ardından:

1. Gözlemleri `run_sync` ile (eşzamanlı üreticiler için `run_async` ile)
   verin.
2. `run.checkpoint()` değerini istediğiniz sıklıkta kaydedin. Bu, durumu,
   rastgele sayı üretecinin durumunu, kaynak konumlarını ve geçmişin
   SHA-256 özetini içeren düz bir JSON değeridir.
3. Bir çökmeden sonra `Run.restore(procedure, checkpoint)` bit bit aynı
   biçimde, tam olarak kaldığı yerden devam eder. `Delivery("sequence")`
   ile yeniden başlatmadan sonra tekrar teslim edilen gözlemler yinelenen
   kayıt olarak atılır.
4. TypeScript yürütücüsü aynı kontrol noktasını (checkpoint)
   JavaScript'te sürdürebilir. Aynı kararları ve aynı geçmiş özetini
   (history digest) verir; sayılar son bitlere kadar uyuşur: 108 uyum
   (conformance) vakasının 34'ünde aynıdır, diğerlerinde göreli olarak
   6·10⁻¹³ içindedir.

## Çökme, yeniden başlatma, yeniden oynatma: aynı sonuç

300 okuma üzerindeki bir izleme çalıştırması 120 okumadan sonra kesintiye
uğruyor. Kaynak, bir mesaj kuyruğunun yeniden başlatmadan sonra
genellikle yaptığı gibi, 100. okumadan itibaren yeniden oynatılıyor.
Geri yüklenen çalıştırma daha önce gördüğü 20 okumayı atıyor ve tam
olarak kesintisiz bir çalıştırmanın bitireceği yerde bitiyor:

```python
import json
import random

from sequential_analysis import Delivery, Observation, Run, run_sync
from sequential_analysis.procedures import BettingConfidenceSequence

rnd = random.Random(5)
readings = [Observation("x", rnd.betavariate(2, 5), seq=i, source="sensor-7") for i in range(300)]

def procedure():
    return BettingConfidenceSequence(lower=0.0, upper=1.0, grid=200)

run = Run(procedure(), delivery=Delivery("sequence"), run_id="sensor-7")
run_sync(run, readings[:120])
saved = json.dumps(run.checkpoint())        # to a file, a database, object storage
del run                                     # the process dies

run = Run.restore(procedure(), json.loads(saved), delivery=Delivery("sequence"))
run_sync(run, readings[100:])               # the source replays from reading 100
print(f"resumed run: {run.t} readings, {run.delivery.duplicates} duplicates dropped")

uninterrupted = Run(procedure(), delivery=Delivery("sequence"), run_id="sensor-7")
run_sync(uninterrupted, readings)
print("same state as an uninterrupted run:", run.state == uninterrupted.state)
print("same history digest:", run.checkpoint()["history_digest"] == uninterrupted.checkpoint()["history_digest"])
print(f"checkpoint size: {len(saved)} bytes")
```

```text
resumed run: 300 readings, 20 duplicates dropped
same state as an uninterrupted run: True
same history digest: True
checkpoint size: 9606 bytes
```

Geçmiş özeti, çalıştırmanın kullandığı her gözlem üzerinde kurulan bir
özet zinciridir (hash chain). Özeti aynı olan iki çalıştırma aynı verileri
aynı sırada görmüştür. Bir denetçi bu özeti, [spesifikasyonu](../../spec.md)
izleyerek gözlem kaydından yeniden hesaplayabilir.

## Gözlemler nereden gelir

| Kaynak | Fonksiyon |
|---|---|
| bir değerler listesi ya da üreteci | `sources.from_values` |
| bir CSV dosyası | `sources.from_csv` |
| bir pandas ya da polars DataFrame'i | `adapters.from_dataframe` |
| bir SQL sorgusu (herhangi bir DB-API bağlantısı) | `adapters.from_sql` |
| onaylanmış (committed) ofsetlerle Kafka mesajları | `adapters.from_kafka`, `adapters.kafka_offsets` |
| aynı anda birkaç kaynak | `sources.interleave`, `sources.merge_ordered` |
| kaydedilmiş bir gözlem kaydı | `sources.replay` |

Farklı kaynaklardan gelen girdiler bir **topoloji** ile ilişkilendirilir.
`KeyJoin` bir atamayı ve bir sonucu kullanıcıya göre birleştirir,
`TimeAlign` iki sensörü zamanda hizalar, `AsOfJoin` ise olayları
onlardan haberdar olan çubuklara (bars) bağlar. Bkz.
[veri kaynakları](../../adapters.md).

## Prosedür değiştiğinde

Bir kontrol noktası prosedürün adını, sürümünü ve yapılandırmasını
kaydeder. `Run.restore`, farklı bir prosedür, farklı bir yapılandırma ya
da aritmetiği farklı bir sürüm tarafından oluşturulmuş bir kontrol
noktasını reddeder ve `IncompatibleCheckpoint` hatası yükseltir. Böylece
bir çalıştırma hiçbir zaman sessizce başka sayılarla sürdürülmez.

Daha fazlası: [kontrol noktaları, kayıtlar ve arka uçlar](../../checkpoints.md),
[TypeScript yürütücüsü](../../typescript.md),
[biçimlerin spesifikasyonu](../../spec.md).
