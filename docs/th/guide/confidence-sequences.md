---
description: ลำดับช่วงความเชื่อมั่น (confidence sequences) คือช่วงความเชื่อมั่นที่ใช้ได้พร้อมกันทุกขนาดตัวอย่าง จึงติดตามผลได้อย่างต่อเนื่อง วิธีคำนวณใน Python สำหรับค่าเฉลี่ยที่มีขอบเขต มัธยฐานหรือควอนไทล์ และค่าเฉลี่ยที่มีหางหนา ด้วย sequential-analysis
language: th
---

# จะได้ช่วงความเชื่อมั่นที่ยังใช้ได้แม้ดูผลซ้ำไปเรื่อย ๆ ได้อย่างไร?

> นี่คือฉบับแปลของ[หน้าภาษาอังกฤษ](../../guide/confidence-sequences.md) ซึ่งยังไม่ได้รับการตรวจทานโดยเจ้าของภาษา หากสองฉบับมีเนื้อหาต่างกัน ให้ถือหน้าภาษาอังกฤษเป็นหลัก

**คำตอบสั้น ๆ** ให้ใช้**ลำดับช่วงความเชื่อมั่น** (confidence sequence) ซึ่งเป็นลำดับของช่วง หนึ่งช่วงหลังแต่ละค่าสังเกต ที่ครอบคลุมค่าจริงพร้อมกันทุกขนาดตัวอย่างด้วยความน่าจะเป็นอย่างน้อย 95% คุณติดตามดูได้ หยุดเมื่อช่วงแคบพอหรือไม่ครอบคลุมศูนย์ แล้วรายงานช่วง ณ จุดที่หยุด ส่วนช่วงความเชื่อมั่น 95% แบบทั่วไปให้คำสัญญา 95% เฉพาะที่ขนาดตัวอย่างเดียวซึ่งกำหนดไว้ล่วงหน้าเท่านั้น

| สิ่งที่ประมาณ | ข้อสมมติ | กระบวนการ | การรับประกัน |
|---|---|---|---|
| ค่าเฉลี่ยของข้อมูลที่มีขอบเขต (อัตรา, คะแนน, รายได้ที่ตัดเพดาน) | ค่าอยู่ใน `[lower, upper]` | `BettingConfidenceSequence` | exact |
| มัธยฐาน, เปอร์เซ็นไทล์ที่ 90, ควอนไทล์ใดก็ได้ | ไม่มี | `QuantileConfidenceSequence` | exact |
| ค่าเฉลี่ยที่มีหางหนาหรือค่าผิดปกติ | ขอบเขตบนของส่วนเบี่ยงเบนมาตรฐาน | `CatoniConfidenceSequence` | exact |
| ค่าเฉลี่ยของข้อมูลปกติ ไม่ทราบความแปรปรวน | ภาวะปกติ (normality) | `TMixtureSPRT` (`lower`, `upper`) | exact ภายใต้ภาวะปกติ |
| ค่าเฉลี่ยของข้อมูลใดก็ได้ เมื่อรันยาว | ความแปรปรวนจำกัด | `AsymptoticConfidenceSequence` | asymptotic |
| ผลต่างระหว่างสองกลุ่ม | ดู[การทดสอบ A/B](ab-testing.md) | `BoundedABTest`, `ABTest` | exact / asymptotic |

## ช่วงแบบทั่วไปล้มเหลวเมื่อถูกติดตามดู

สุ่มค่าสังเกต 500 ค่าของตัวแปร 0/1 ที่มีค่าเฉลี่ย 0.3 และตั้งแต่ค่าที่ 30 เป็นต้นไป ให้คำนวณช่วง 95% ตามตำราหลังทุกค่า คือค่าเฉลี่ย ± 1.96 เท่าของความคลาดเคลื่อนมาตรฐาน ในการรัน 100 ครั้ง มีกี่ครั้งที่ช่วงพลาดค่าเฉลี่ยจริง ณ จุดใดจุดหนึ่ง?

```python
import math
import random

def stream(seed, n=500, p=0.3):
    rnd = random.Random(seed)
    return [float(rnd.random() < p) for _ in range(n)]

def textbook_ever_misses(xs, truth=0.3):
    total = total2 = 0.0
    for n, x in enumerate(xs, start=1):
        total, total2 = total + x, total2 + x * x
        if n >= 30:
            mean = total / n
            se = math.sqrt(max(total2 / n - mean * mean, 1e-12) / n)
            if abs(mean - truth) > 1.96 * se:
                return True
    return False

runs = [stream(seed) for seed in range(100)]
print(f"textbook interval misses the truth at some n in {sum(map(textbook_ever_misses, runs)) / len(runs):.0%} of runs")
```

```text
textbook interval misses the truth at some n in 28% of runs
```

"95%" ของมันเป็นจริงเฉพาะที่ขนาดตัวอย่างซึ่งกำหนดไว้ล่วงหน้า ส่วนลำดับช่วงความเชื่อมั่นสำหรับข้อมูลชุดเดียวกัน ซึ่งสร้างด้วยการเดิมพัน (by betting; Waudby-Smith และ Ramdas 2024) จะพลาด ณ n ใด n หนึ่งในไม่เกิน 5% ของการรันโดยโครงสร้างของมันเอง:

```python
from sequential_analysis.procedures import BettingConfidenceSequence

def sequence_ever_misses(xs, truth=0.3):
    cs = BettingConfidenceSequence(lower=0.0, upper=1.0, alpha=0.05, grid=100)
    state = cs.initial_state()
    for x in xs:
        state, out = cs.step(state, {"x": x})
        if not out.lower <= truth <= out.upper:
            return True
    return False

print(f"confidence sequence misses the truth at some n in {sum(map(sequence_ever_misses, runs)) / len(runs):.0%} of runs")
```

```text
confidence sequence misses the truth at some n in 1% of runs
```

## มัธยฐานของเวลาแฝง โดยไม่มีข้อสมมติใดเลย

เวลาแฝง (latency) มีการแจกแจงเบ้และหางหนา ช่วงแบบค่าเฉลี่ย ± ความคลาดเคลื่อนมาตรฐานจึงเชื่อถือไม่ได้สำหรับข้อมูลแบบนี้ `QuantileConfidenceSequence` ครอบคลุมควอนไทล์ใดก็ได้ของการแจกแจงใดก็ได้ รวมถึงกรณีที่มีค่าซ้ำกัน (ties):

```python
from sequential_analysis.procedures import QuantileConfidenceSequence

rnd = random.Random(7)
median = QuantileConfidenceSequence(p=0.5, alpha=0.05)
p90 = QuantileConfidenceSequence(p=0.9, alpha=0.05)
m_state, q_state = median.initial_state(), p90.initial_state()
for _ in range(2000):
    latency = rnd.lognormvariate(math.log(120.0), 0.6)   # milliseconds; true median 120
    m_state, m = median.step(m_state, {"x": latency})
    q_state, q = p90.step(q_state, {"x": latency})
print(f"median: {m.estimate:.1f} ms, 95% confidence sequence [{m.lower:.1f}, {m.upper:.1f}]")
print(f"90th percentile: {q.estimate:.1f} ms, [{q.lower:.1f}, {q.upper:.1f}]")
```

```text
median: 117.3 ms, 95% confidence sequence [111.3, 122.6]
90th percentile: 252.7 ms, [237.9, 272.5]
```

ค่าจริงคือ 120 ms และ 258.8 ms ทั้งสองช่วงเป็นจริงพร้อมกันที่ขนาดตัวอย่างทั้ง 2,000 ขนาด

## ข้อผิดพลาดที่พบบ่อย

* **ขอบเขตและเพดานเป็นส่วนหนึ่งของข้อสมมติ** เลือก `lower` และ `upper` ก่อนเห็นข้อมูล ค่าที่อยู่นอกขอบเขตจะถูกปฏิเสธ
* **ไม่มีวิธีใดให้ความครอบคลุมแบบแม่นตรงสำหรับค่าเฉลี่ยของข้อมูลที่ไม่มีขอบเขตแบบใดก็ได้** สำหรับข้อมูลเช่นนี้ ให้ใช้ควอนไทล์ ตัดเพดานค่า สมมติขอบเขตบนของส่วนเบี่ยงเบนมาตรฐาน (Catoni) หรือยอมรับลำดับแบบ asymptotic
* **ลำดับช่วงความเชื่อมั่นกว้างกว่าช่วงเดี่ยว** ที่ขนาดตัวอย่างเท่ากัน ความกว้างนี้คือราคาของการใช้ได้พร้อมกันทุกขนาดตัวอย่าง

เพิ่มเติม: [วิธีใด?](../../choosing.md), [เอกสารอ้างอิง: วิธีที่ใช้ได้ทุกขณะและวิธีไม่อิงพารามิเตอร์](../../reference/anytime.md)
