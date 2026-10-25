---
description: چگونه آمار دنباله‌ای را روی یک جریان داده (Kafka، SQL، pandas، حسگرها) اجرا کنیم و پس از خرابی دقیقاً از همان جایی که متوقف شد از سر بگیریم. نقاط بازیابی JSON، تحویل بدون تکرار، چکیدهٔ تاریخچه برای ممیزی، و ادامهٔ همان اجرا در Python یا TypeScript، با sequential-analysis.
language: fa
---

# چگونه روی یک جریان داده آمار اجرا کنم و پس از خرابی از سر بگیرم؟

> این صفحه ترجمه‌ای از [صفحهٔ انگلیسی](../../guide/streaming.md) است. این ترجمه هنوز توسط یک گویشور بومی بازبینی نشده است؛ هر جا این دو با هم تفاوت داشته باشند، صفحهٔ انگلیسی معتبر است.

**پاسخ کوتاه.** روال را در یک `Run` بپیچید. سپس:

1. مشاهدات را با `run_sync` (یا `run_async` برای تولیدکننده‌های هم‌روند) به آن
   بدهید.
2. `run.checkpoint()` را هر چند وقت یک بار که خواستید ذخیره کنید. این یک
   مقدار JSON ساده است که حالت، حالت مولد تصادفی، موقعیت‌های منابع و یک
   چکیدهٔ SHA-256 از تاریخچه را در بر دارد.
3. پس از خرابی، `Run.restore(procedure, checkpoint)` دقیقاً، بیت‌به‌بیت، ادامه
   می‌دهد. با `Delivery("sequence")`، مشاهداتی که پس از راه‌اندازی مجدد دوباره
   تحویل داده شوند به‌عنوان تکراری کنار گذاشته می‌شوند.
4. اجراکنندهٔ TypeScript می‌تواند همان نقطهٔ بازیابی را در JavaScript ادامه
   دهد. همان تصمیم‌ها و همان چکیدهٔ تاریخچه را به دست می‌دهد، و اعدادی که تا
   آخرین بیت‌ها مطابقت دارند: در 34 مورد از 108 مورد انطباق یکسان، و در بقیه
   با اختلاف نسبی حداکثر 6·10⁻¹³.

## خرابی، راه‌اندازی مجدد، بازپخش: همان نتیجه

یک اجرای پایش روی 300 خوانش پس از 120 خوانش قطع می‌شود. منبع از خوانش 100
دوباره پخش می‌شود، همان‌طور که یک صف پیام معمولاً پس از راه‌اندازی مجدد
بازپخش می‌کند. اجرای بازیابی‌شده 20 خوانشی را که قبلاً دیده کنار می‌گذارد و
دقیقاً همان جایی تمام می‌شود که یک اجرای بی‌وقفه تمام می‌شد:

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

چکیدهٔ تاریخچه (history digest) یک زنجیرهٔ هش روی هر مشاهده‌ای است که اجرا به
کار برده است. دو اجرا با چکیدهٔ یکسان، داده‌های یکسانی را به ترتیب یکسان
دیده‌اند. یک ممیز می‌تواند آن را با پیروی از
[مشخصات](../../spec.md) از روی گزارش مشاهدات دوباره محاسبه کند.

## مشاهدات از کجا می‌آیند

| منبع | تابع |
|---|---|
| یک فهرست یا مولد از مقادیر | `sources.from_values` |
| یک فایل CSV | `sources.from_csv` |
| یک DataFrame در pandas یا polars | `adapters.from_dataframe` |
| یک پرس‌وجوی SQL (هر اتصال DB-API) | `adapters.from_sql` |
| پیام‌های Kafka، با آفست‌های ثبت‌شده (committed offsets) | `adapters.from_kafka`، `adapters.kafka_offsets` |
| چند منبع به‌طور هم‌زمان | `sources.interleave`، `sources.merge_ordered` |
| یک گزارش ضبط‌شده از مشاهدات | `sources.replay` |

ورودی‌های منابع مختلف با یک **توپولوژی** (topology) به هم مرتبط می‌شوند.
`KeyJoin` تخصیص و نتیجه را بر اساس کاربر به هم پیوند می‌دهد، `TimeAlign` دو
حسگر را در زمان هم‌تراز می‌کند، و `AsOfJoin` رویدادها را به میله‌هایی (bars)
که از آن‌ها آگاه بودند الصاق می‌کند. ببینید [منابع داده](../../adapters.md).

## وقتی روال تغییر می‌کند

یک نقطهٔ بازیابی نام، نسخه و پیکربندی روال را ثبت می‌کند. `Run.restore` نقطهٔ
بازیابی‌ای را که یک روال دیگر، پیکربندی دیگر یا نسخه‌ای با محاسبات عددی
متفاوت ساخته باشد رد می‌کند و `IncompatibleCheckpoint` را برمی‌انگیزد. بنابراین
یک اجرا هرگز بی‌سروصدا با اعداد دیگری ادامه نمی‌یابد.

بیشتر: [نقاط بازیابی، گزارش‌ها و بک‌اندهای ذخیره‌سازی](../../checkpoints.md)،
[اجراکنندهٔ TypeScript](../../typescript.md)،
[مشخصات قالب‌ها](../../spec.md).
