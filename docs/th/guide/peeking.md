---
description: ทำไมการดูค่า p ทุกวันจึงทำให้ผลบวกลวงในการทดสอบ A/B และการทดลองสูงขึ้น (ปัญหาการแอบดูผล หรือ peeking problem) และวิธีแบบลำดับสามตระกูลที่แก้ปัญหานี้ ใน Python ด้วย sequential-analysis
language: th
---

# ทำไมจึงดูค่า p ทุกวันไม่ได้?

> นี่คือฉบับแปลของ[หน้าภาษาอังกฤษ](../../guide/peeking.md) ซึ่งยังไม่ได้รับการตรวจทานโดยเจ้าของภาษา หากสองฉบับมีเนื้อหาต่างกัน ให้ถือหน้าภาษาอังกฤษเป็นหลัก

**คำตอบสั้น ๆ** การทดสอบแบบขนาดตัวอย่างคงที่ (fixed-sample test)
รับประกันอัตราผลบวกลวง (false positive) 5% ก็ต่อเมื่อคุณดูผลเพียงครั้งเดียวที่ขนาดตัวอย่างตามแผน หากคุณดูซ้ำหลายครั้งและหยุดทันทีที่พบ p < 0.05 เป็นครั้งแรก คุณก็มีโอกาสถูกหลอกหลายครั้ง เมื่อดู 20 ครั้ง อัตราผลบวกลวงจะเพิ่มเป็นประมาณ 25%
วิธีแบบลำดับ (sequential methods) ถูกสร้างมาให้ดูผลซ้ำได้ อัตรานี้จึงอยู่ที่ไม่เกิน 5%
ไม่ว่าจะดูบ่อยเพียงใดและหยุดเมื่อใด

## วัดขนาดของปัญหาการแอบดูผล

สองกลุ่มที่มีอัตราคอนเวอร์ชัน (conversion rate) เท่ากันที่ 10% (การทดสอบ A/A)
ผู้ใช้ 2,000 คน ทำซ้ำ 200 รอบ "การแอบดูผล" (peeking) คือการรันการทดสอบ z สำหรับสองสัดส่วนแบบที่ใช้กันทั่วไปทุก ๆ 100 คน และหยุดเมื่อ p < 0.05 ครั้งแรก
ส่วน `TwoProportionTest` แบบลำดับจะถูกตรวจสอบหลังผู้ใช้ทุกคน:

```python
import math
import random

from sequential_analysis.procedures import TwoProportionTest

def a_a_test(seed, users=2000):
    """Alternating arms, both converting 10% of the time: any 'effect' is a false positive."""
    rnd = random.Random(seed)
    return [(user % 2, int(rnd.random() < 0.10)) for user in range(users)]

def peeking(data, looks):
    """The z-test for two proportions after every len(data) / looks users; True if it ever rejects."""
    successes, trials, every = [0, 0], [0, 0], len(data) // looks
    for i, (arm, y) in enumerate(data, start=1):
        successes[arm] += y
        trials[arm] += 1
        if i % every == 0:
            pooled = sum(successes) / sum(trials)
            se = math.sqrt(pooled * (1 - pooled) * (1 / trials[0] + 1 / trials[1]))
            if se > 0 and abs(successes[1] / trials[1] - successes[0] / trials[0]) / se > 1.96:
                return True
    return False

def sequential(data):
    """The anytime-valid test, looked at after every user; True if it ever rejects."""
    test = TwoProportionTest(alpha=0.05)
    state = test.initial_state()
    for arm, y in data:
        state, out = test.step(state, {"arm": arm, "y": y})
        if out.decision is not None:
            return True
    return False

runs = [a_a_test(seed) for seed in range(200)]
print(f"z-test, one look at the end:   {sum(peeking(r, 1) for r in runs) / len(runs):.1%} false positives")
print(f"z-test, 20 looks:              {sum(peeking(r, 20) for r in runs) / len(runs):.1%}")
print(f"TwoProportionTest, 2000 looks: {sum(sequential(r) for r in runs) / len(runs):.1%}")
```

```text
z-test, one look at the end:   4.5% false positives
z-test, 20 looks:              28.0%
TwoProportionTest, 2000 looks: 5.0%
```

การดูครั้งเดียวรักษาคำสัญญาไว้ได้ การดูยี่สิบครั้งทำให้อัตราความคลาดเคลื่อนเพิ่มขึ้นราวหกเท่า การทดสอบแบบลำดับซึ่งดูผลหลังผู้ใช้ทุกคนจากทั้งหมด 2,000 คน
รักษาไว้ที่ 5% นั่นคือคำสัญญา การรับประกันของมันเป็นแบบ
**exact** (`TwoProportionTest.guarantee == "exact"`) คืออัตราผลบวกลวงไม่เกิน 5%
ที่ทุกขนาดตัวอย่าง ไม่ว่าจะดูบ่อยเพียงใด เมื่อทำซ้ำ 200 รอบ
ผลบวกลวง 10 ครั้งก็คือสิ่งที่ระดับ 5% แบบแม่นตรงให้ผล

## วิธีแบบลำดับสามตระกูล

| ตระกูล | ดูผลได้เมื่อใด | การใช้งานทั่วไป | ใน sequential-analysis |
|---|---|---|---|
| **การทดสอบอัตราส่วนความน่าจะเป็นแบบลำดับ** (sequential probability ratio tests, Wald 1945) | หลังทุกค่าสังเกต | สมมติฐานเชิงเดียวหนึ่งข้อเทียบกับอีกข้อ ใช้ค่าสังเกตน้อยที่สุดโดยเฉลี่ย: การควบคุมคุณภาพ การจำลอง จิตฟิสิกส์ | `SPRT`, `TwoSPRT`, `kiefer_weiss_plan` |
| **แผนแบบลำดับกลุ่ม** (group sequential designs; Pocock 1977, O'Brien และ Fleming 1979, Lan และ DeMets 1983) | ที่การวิเคราะห์ระหว่างกาลจำนวนไม่มากตามแผน | การทดลองทางคลินิกที่มีคณะกรรมการกำกับดูแลข้อมูล | `group_sequential_design`, `GroupSequentialTest`, `GroupSequentialProportions`, `GroupSequentialLogRank` |
| **การอนุมานที่ใช้ได้ทุกขณะ** (anytime-valid inference): ค่า e, ลำดับช่วงความเชื่อมั่น, mixture SPRT (Robbins 1970, Howard et al. 2021, Ramdas et al. 2023) | หลังทุกค่าสังเกต หยุดด้วยเหตุผลใดก็ได้ | การทดสอบ A/B ออนไลน์ แดชบอร์ดติดตามผล | `TwoProportionTest`, `BoundedABTest`, `NormalMixtureSPRT`, `BettingConfidenceSequence`, `MultipleTests` |

**ต้นทุน** การดูผลบ่อยขึ้นต้องใช้ข้อมูลมากขึ้น ณ ขนาดผลที่วางแผนไว้:

* แผนแบบลำดับกลุ่มที่มีการวิเคราะห์สี่ครั้งต้องใช้ผู้ป่วยมากกว่าการวิเคราะห์ครั้งเดียว 1–20%
* การทดสอบสองสัดส่วนที่ใช้ได้ทุกขณะต้องใช้ผู้ใช้ 1.3–1.6 เท่าของการวิเคราะห์ครั้งเดียว

ในทางกลับกัน ผลขนาดใหญ่จะทำให้การทดลองหยุดได้เร็ว และไม่มีใครต้องกำหนดขนาดตัวอย่างไว้ล่วงหน้า

## เมื่อใดที่สิ่งนี้ไม่ใช่ปัญหา

การแอบดูผลทำให้ความคลาดเคลื่อนสูงขึ้นเฉพาะเมื่อสิ่งที่คุณทำขึ้นอยู่กับสิ่งที่คุณเห็น
หากคุณดูแดชบอร์ดแต่ยังรันการทดลองจนถึงขนาดตามแผนเสมอและทดสอบเพียงครั้งเดียว
การทดสอบแบบขนาดตัวอย่างคงที่ก็ยังใช้ได้ และในกรณีนั้นยังเป็นทางเลือกที่มีประสิทธิภาพที่สุดด้วย

ต่อไป: [หยุดการทดสอบ A/B ก่อนกำหนด](ab-testing.md),
[ลำดับช่วงความเชื่อมั่น](confidence-sequences.md),
[อภิธานศัพท์](glossary.md)
