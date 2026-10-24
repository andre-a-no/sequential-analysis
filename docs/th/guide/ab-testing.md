---
description: วิธีหยุดการทดสอบ A/B ก่อนกำหนดโดยไม่ทำให้ผลบวกลวงสูงขึ้น ใน Python การทดสอบที่ใช้ได้ทุกขณะ (anytime-valid) สำหรับอัตราคอนเวอร์ชันและรายได้ที่มีขอบเขต การตรวจ sample ratio mismatch และการควบคุมอัตราการค้นพบลวง (false discovery rate) เมื่อมีหลายตัวชี้วัด ด้วย sequential-analysis
language: th
---

# จะหยุดการทดสอบ A/B ก่อนกำหนดโดยไม่ทำให้ผลบวกลวงสูงขึ้นได้อย่างไร?

> นี่คือฉบับแปลของ[หน้าภาษาอังกฤษ](../../guide/ab-testing.md) ซึ่งยังไม่ได้รับการตรวจทานโดยเจ้าของภาษา หากสองฉบับมีเนื้อหาต่างกัน ให้ถือหน้าภาษาอังกฤษเป็นหลัก

**คำตอบสั้น ๆ** ให้ใช้การทดสอบที่ใช้ได้ทุกขณะ (anytime-valid) ค่า p (p-value) และช่วงความเชื่อมั่นของการทดสอบแบบนี้ยังใช้ได้ไม่ว่าคุณจะดูผลบ่อยเพียงใด คุณจึงหยุดได้ทันทีที่ผลชัดเจน ใน sequential-analysis:

| ตัวชี้วัด | กระบวนการ | การรับประกัน |
|---|---|---|
| อัตราคอนเวอร์ชัน (0/1) | `TwoProportionTest` | exact |
| ตัวชี้วัดใดก็ได้ที่มีขอบเขต (รายได้ที่ตัดเพดาน, สัดส่วน) | `BoundedABTest` | exact |
| จำนวนเหตุการณ์ต่อหน่วยการรับสัมผัส (exposure) | `RateRatioTest` | exact สำหรับข้อมูลนับแบบ Poisson |
| ตัวชี้วัดแบบอัตราส่วน (รายได้ต่อเซสชัน) | `RatioABTest` | asymptotic |
| ค่าเฉลี่ยร่วมกับตัวแปรร่วมก่อนการทดลอง (CUPED) | `ABTest` | asymptotic |
| ทราฟฟิกถูกแบ่งตามที่ตั้งใจหรือไม่? | `SampleRatioMismatch` | exact |
| หลายตัวชี้วัดหรือหลายกลุ่มพร้อมกัน | `MultipleTests` (e-BH) | อัตราการค้นพบลวง, exact |

ป้อนข้อมูลให้แต่ละกระบวนการทีละผู้ใช้: `state, out = test.step(state, {...})` แล้วตัดสินใจตาม `out.decision` เมื่อใดก็ได้ที่ต้องการ

## อัตราคอนเวอร์ชัน: หยุดเมื่อข้อมูลให้ข้อสรุปได้

กลุ่มควบคุมมีผู้ใช้คอนเวิร์ต 10% กลุ่มทดลอง 12% การทดสอบถูกดูผลหลังผู้ใช้ทุกคนและหยุดเมื่อได้การตัดสินใจครั้งแรก:

```python
import random

from sequential_analysis.procedures import TwoProportionTest

def users(n, rates=(0.10, 0.12), seed=1):
    """(arm, converted) per user; arm 1 is the treatment."""
    rnd = random.Random(seed)
    for _ in range(n):
        arm = int(rnd.random() < 0.5)
        yield arm, int(rnd.random() < rates[arm])

test = TwoProportionTest(alpha=0.05)
state = test.initial_state()
for arm, converted in users(60_000):
    state, out = test.step(state, {"arm": arm, "y": converted})
    if out.decision is not None:
        break
print(f"stopped after {out.n} users: conversion {out.rates[0]:.4f} (treatment) vs {out.rates[1]:.4f}, "
      f"anytime-valid p = {out.p_value:.4f}, decision: {out.decision}")
```

```text
stopped after 16469 users: conversion 0.1259 (treatment) vs 0.1068, anytime-valid p = 0.0496, decision: reject_h0
```

เพื่อเปรียบเทียบ การทดสอบแบบขนาดตัวอย่างคงที่ (fixed-sample test) ที่มีอำนาจการทดสอบ (power) 80% สำหรับการเพิ่มขึ้นขนาดนี้ต้องใช้ผู้ใช้ประมาณ 3,850 คนต่อกลุ่ม รวม 7,700 คน และอ่านผลได้เพียงครั้งเดียวตอนสิ้นสุด การทดสอบที่ใช้ได้ทุกขณะต้องจ่ายราคาสำหรับอิสระนี้ คือเพื่อให้ได้อำนาจการทดสอบเท่ากัน ต้องใช้ผู้ใช้ 1.3–1.6 เท่าของการวิเคราะห์ครั้งเดียว และการรันครั้งนี้ใช้มากกว่านั้นอีก แลกกับการที่ไม่ต้องกำหนดขนาดตัวอย่างล่วงหน้า และคุณดูผลได้ทุกวันแล้วหยุดทันทีที่ผลชัดเจน เมื่อผลจริงมีขนาดใหญ่กว่าที่วางแผนไว้ สิ่งนั้นจะเกิดขึ้นเร็วกว่ามาก

## รายได้: ช่วงแบบแม่นตรงสำหรับตัวชี้วัดที่มีขอบเขต

`BoundedABTest` ต้องการเพียงขอบเขตของตัวชี้วัด ให้ตัดเพดานรายได้ไว้ที่ค่าที่คุณเลือกก่อนเริ่มการทดสอบ (ในที่นี้คือ 30) แล้วลำดับช่วงความเชื่อมั่น (confidence sequence) ของผลต่างของค่าเฉลี่ยจะเป็นแบบแม่นตรง (exact) สำหรับการแจกแจงใดก็ได้:

```python
from sequential_analysis.procedures import BoundedABTest

rnd = random.Random(2)
revenue = BoundedABTest(lower=0.0, upper=30.0, allocation=0.5, input="revenue", grid=300)
state = revenue.initial_state()
for _ in range(20_000):
    arm = int(rnd.random() < 0.5)
    spend = min(rnd.expovariate(1 / (5.0 if arm == 0 else 5.6)), 30.0)   # capped at 30
    state, out = revenue.step(state, {"arm": arm, "revenue": spend})
print(f"after {out.n} users: mean revenue {out.means[0]:.2f} (treatment) vs {out.means[1]:.2f}, "
      f"95% confidence sequence for the difference [{out.lower:.2f}, {out.upper:.2f}]")
```

```text
after 20000 users: mean revenue 5.47 (treatment) vs 4.99, 95% confidence sequence for the difference [-0.30, 1.30]
```

ช่วงนี้เป็นจริงพร้อมกันในการดูผลทั้ง 20,000 ครั้ง ไม่ใช่เฉพาะครั้งสุดท้าย ในที่นี้ช่วงยังครอบคลุม 0 อยู่ ผู้ใช้ 20,000 คนยังไม่พอจะยืนยันการเพิ่มขึ้นประมาณ 0.5 ในตัวชี้วัดที่มีสัญญาณรบกวนมากขนาดนี้ การทดลองจึงดำเนินต่อไป

## ตรวจการแบ่งทราฟฟิกก่อน

sample ratio mismatch (SRM) หมายถึงสัดส่วนการแบ่งทราฟฟิกต่างไปจากที่ตั้งค่าไว้ เช่น เพราะมีบั๊กในการสุ่มกลุ่มหรือในการบันทึกล็อก ค่าประมาณขนาดผลจากการทดลองเช่นนี้เชื่อถือไม่ได้ ความคลาดเคลื่อนจาก 50/50 เป็น 52/48 จะถูกตรวจพบขณะที่การทดลองยังดำเนินอยู่:

```python
from sequential_analysis.procedures import SampleRatioMismatch

srm = SampleRatioMismatch(weights=(0.5, 0.5), alpha=0.001)
state = srm.initial_state()
rnd = random.Random(3)
for _ in range(50_000):
    state, out = srm.step(state, {"arm": int(rnd.random() < 0.52)})
    if out.decision is not None:
        break
print(f"mismatch detected after {out.n} users: split {out.proportions[0]:.3f} / {out.proportions[1]:.3f}")
```

```text
mismatch detected after 4927 users: split 0.470 / 0.530
```

## หลายตัวชี้วัดพร้อมกัน

การทดสอบตัวชี้วัดอิสระสิบตัวที่ระดับ 5% แต่ละตัว ทำให้มีโอกาสประมาณ 40% ที่จะเกิดการค้นพบลวงอย่างน้อยหนึ่งครั้ง `MultipleTests` รวมค่า e (e-values) ของทุกการทดสอบด้วยกระบวนการ e-BH เพื่อให้อัตราการค้นพบลวง (false discovery rate) อยู่ที่ `alpha` ณ เวลาหยุดใดก็ได้:

```python
from sequential_analysis.procedures import MultipleTests

metrics = MultipleTests({
    "conversion": TwoProportionTest(input="converted"),
    "revenue": BoundedABTest(lower=0.0, upper=30.0, input="revenue", grid=100),
    "traffic split": SampleRatioMismatch((0.5, 0.5)),
}, alpha=0.05)
state = metrics.initial_state()
rnd = random.Random(4)
for _ in range(15_000):
    arm = int(rnd.random() < 0.5)
    converted = int(rnd.random() < (0.10, 0.13)[arm])
    spend = min(rnd.expovariate(1 / 5.0), 30.0)                          # no effect on revenue
    state, out = metrics.step(state, {"arm": arm, "converted": converted, "revenue": spend})
print("discoveries:", out.rejected)
```

```text
discoveries: ('conversion',)
```

## ข้อผิดพลาดที่พบบ่อย

* **สุ่มหน่วยเดียวกับที่คุณวิเคราะห์** หากสุ่มที่ระดับผู้ใช้ ให้ป้อนหนึ่งระเบียนต่อผู้ใช้ ไม่ใช่ต่อการดูหน้าเว็บ สำหรับตัวชี้วัดระดับเซสชันให้ใช้ `RatioABTest` ซึ่งทำงานกับยอดรวมต่อผู้ใช้
* **กำหนดเพดานของตัวชี้วัดที่มีขอบเขตก่อนเริ่มการทดสอบ** การเลือกเพดานหลังเห็นข้อมูลแล้วทำให้การรับประกันเป็นโมฆะ
* **กระบวนการแบบ asymptotic ต้องใช้ตัวอย่างขนาดใหญ่** สำหรับ `ABTest` และ `RatioABTest` ช่วงที่ได้ใช้ได้เพียงโดยประมาณเมื่อรันยาว ควรเลือกกระบวนการแบบ exact เมื่อใช้ได้
* **การจัดสรรทราฟฟิกแบบปรับตัว** (bandits) ต้องใช้การทดสอบที่ยังใช้ได้เมื่อสัดส่วนการแบ่งขึ้นกับผลลัพธ์: `TwoProportionTest(method="universal")` หรือ `BoundedABTest(propensity_input=...)` ดู[บทเรียน §10](../../tutorials/ab-test.md)

เพิ่มเติม: [บทเรียนการทดสอบ A/B](../../tutorials/ab-test.md) (CUPED, ตัวชี้วัดแบบอัตราส่วน, อัตราเหตุการณ์, การวางแผนระยะเวลา) และ[ชุดการทดลองต่อเนื่อง](../../tutorials/experiment-programme.md) (อัตราการค้นพบลวงเมื่อมีการทดลองจำนวนมาก)
