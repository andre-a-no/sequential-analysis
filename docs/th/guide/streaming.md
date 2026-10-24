---
description: วิธีคำนวณสถิติแบบลำดับบนสายข้อมูล (Kafka, SQL, pandas, เซนเซอร์) และรันต่อหลังระบบล่มจากจุดที่หยุดพอดี จุดบันทึกสถานะ JSON การส่งข้อมูลแบบตัดรายการซ้ำ ไดเจสต์ประวัติเพื่อการตรวจสอบ และการรันเดียวกันที่ทำต่อใน Python หรือ TypeScript ด้วย sequential-analysis
language: th
---

# จะคำนวณสถิติบนสายข้อมูลและรันต่อหลังระบบล่มได้อย่างไร?

> นี่คือฉบับแปลของ[หน้าภาษาอังกฤษ](../../guide/streaming.md) ซึ่งยังไม่ได้รับการตรวจทานโดยเจ้าของภาษา หากสองฉบับมีเนื้อหาต่างกัน ให้ถือหน้าภาษาอังกฤษเป็นหลัก

**คำตอบสั้น ๆ** ห่อกระบวนการไว้ใน `Run` จากนั้น:

1. ป้อนค่าสังเกตด้วย `run_sync` (หรือ `run_async` สำหรับผู้ผลิตข้อมูลหลายรายที่ทำงานพร้อมกัน)
2. บันทึก `run.checkpoint()` บ่อยเท่าที่ต้องการ มันเป็นค่า JSON ธรรมดาที่มีสถานะ สถานะของตัวสร้างเลขสุ่ม ตำแหน่งในแหล่งข้อมูล และไดเจสต์ SHA-256 ของประวัติ
3. หลังระบบล่ม `Run.restore(procedure, checkpoint)` จะรันต่ออย่างแม่นตรงทุกบิต เมื่อใช้ `Delivery("sequence")` ค่าสังเกตที่ถูกส่งซ้ำหลังการรีสตาร์ตจะถูกทิ้งในฐานะรายการซ้ำ
4. ตัวประมวลผล TypeScript สามารถรันต่อจากจุดบันทึกสถานะเดียวกันใน JavaScript ได้ โดยให้การตัดสินใจและไดเจสต์ประวัติเหมือนกัน และตัวเลขที่ตรงกันจนถึงบิตท้าย ๆ คือเหมือนกันทุกประการใน 34 จาก 108 กรณีทดสอบความสอดคล้อง (conformance cases) และต่างกันไม่เกิน 6·10⁻¹³ เชิงสัมพัทธ์ในกรณีที่เหลือ

## ล่ม รีสตาร์ต เล่นซ้ำ: ได้ผลเหมือนเดิม

การรันเพื่อติดตามค่าที่อ่าน 300 ค่าถูกขัดจังหวะหลังค่าที่ 120 แหล่งข้อมูลถูกเล่นซ้ำตั้งแต่ค่าที่ 100 ตามที่คิวข้อความ (message queue) มักทำหลังการรีสตาร์ต การรันที่กู้คืนมาจะทิ้งค่าที่อ่าน 20 ค่าที่เคยเห็นแล้ว และจบลงตรงจุดเดียวกับการรันที่ไม่ถูกขัดจังหวะ:

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

ไดเจสต์ประวัติ (history digest) คือสายโซ่แฮชของค่าสังเกตทุกค่าที่การรันใช้ การรันสองครั้งที่มีไดเจสต์เดียวกันได้เห็นข้อมูลเดียวกันในลำดับเดียวกัน ผู้ตรวจสอบ (auditor) สามารถคำนวณไดเจสต์ใหม่จากล็อกค่าสังเกตได้ตาม[ข้อกำหนด](../../spec.md)

## ค่าสังเกตมาจากที่ใด

| แหล่งข้อมูล | ฟังก์ชัน |
|---|---|
| ลิสต์หรือ generator ของค่า | `sources.from_values` |
| ไฟล์ CSV | `sources.from_csv` |
| DataFrame ของ pandas หรือ polars | `adapters.from_dataframe` |
| คำสั่ง SQL (การเชื่อมต่อ DB-API ใดก็ได้) | `adapters.from_sql` |
| ข้อความ Kafka พร้อม offset ที่ commit แล้ว | `adapters.from_kafka`, `adapters.kafka_offsets` |
| หลายแหล่งข้อมูลพร้อมกัน | `sources.interleave`, `sources.merge_ordered` |
| ล็อกค่าสังเกตที่บันทึกไว้ | `sources.replay` |

ข้อมูลนำเข้าจากแหล่งต่าง ๆ เชื่อมโยงกันด้วย**โทโพโลยี** (topology) `KeyJoin` จับคู่การสุ่มกลุ่มกับผลลัพธ์ตามผู้ใช้ `TimeAlign` จัดแนวเซนเซอร์สองตัวตามเวลา และ `AsOfJoin` ผูกเหตุการณ์เข้ากับแท่งข้อมูล (bars) ที่รู้เหตุการณ์นั้นแล้ว ดู[แหล่งข้อมูล](../../adapters.md)

## เมื่อกระบวนการเปลี่ยนไป

จุดบันทึกสถานะบันทึกชื่อ เวอร์ชัน และการกำหนดค่าของกระบวนการ `Run.restore` จะปฏิเสธจุดบันทึกสถานะที่สร้างโดยกระบวนการอื่น การกำหนดค่าอื่น หรือเวอร์ชันที่มีการคำนวณเชิงตัวเลขต่างกัน และยก `IncompatibleCheckpoint` ดังนั้นการรันจะไม่ถูกทำต่อด้วยตัวเลขชุดอื่นโดยไม่มีใครรู้

เพิ่มเติม: [จุดบันทึกสถานะ ล็อก และแบ็กเอนด์](../../checkpoints.md), [ตัวประมวลผล TypeScript](../../typescript.md), [ข้อกำหนดของรูปแบบข้อมูล](../../spec.md)
