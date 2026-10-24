---
description: วิธีวางแผนและดำเนินการวิเคราะห์ระหว่างกาล (interim analysis) ของการทดลองทางคลินิกใน Python ด้วยแผนแบบลำดับกลุ่ม (O'Brien–Fleming, Pocock, การใช้จ่ายค่าแอลฟาแบบ Lan–DeMets, ขอบเขตความไร้ประโยชน์) ขนาดตัวอย่างสำหรับค่าเฉลี่ย สัดส่วน และการรอดชีพ ตรวจสอบเทียบกับ rpact ด้วย sequential-analysis
language: th
---

# จะวางแผนการวิเคราะห์ระหว่างกาลของการทดลองทางคลินิกได้อย่างไร?

> นี่คือฉบับแปลของ[หน้าภาษาอังกฤษ](../../guide/clinical-trials.md) ซึ่งยังไม่ได้รับการตรวจทานโดยเจ้าของภาษา หากสองฉบับมีเนื้อหาต่างกัน ให้ถือหน้าภาษาอังกฤษเป็นหลัก

**คำตอบสั้น ๆ** ให้ใช้แผนแบบลำดับกลุ่ม (group sequential design) `group_sequential_design(alpha, fractions, spending=...)` จาก `sequential_analysis.group_sequential` คำนวณ:

* ขอบเขตประสิทธิผล (efficacy boundaries) ด้วยการใช้จ่ายค่าแอลฟา (alpha spending) แบบ Lan–DeMets (แบบ O'Brien–Fleming แบบ Pocock และแบบอื่น ๆ)
* ขอบเขตความไร้ประโยชน์ (futility boundaries) แบบไม่ผูกมัด
* อำนาจการทดสอบ (power) และขนาดตัวอย่างคาดหวัง
* ขนาดตัวอย่างสูงสุดสำหรับค่าเฉลี่ยและสัดส่วน หรือจำนวนเหตุการณ์ (events) สำหรับการรอดชีพ

ขอบเขตและขนาดตัวอย่างตรงกับแพ็กเกจ R ชื่อ rpact จากนั้นกระบวนการทดสอบ (`GroupSequentialTest`, `GroupSequentialTwoMeans`, `GroupSequentialProportions`, `GroupSequentialLogRank`) จะดำเนินการทดลองทีละผู้ป่วยหรือทีละเหตุการณ์ และทำการวิเคราะห์ระหว่างกาลแต่ละครั้งเมื่อถึงสัดส่วนสารสนเทศ (information fraction) ของครั้งนั้น

## แผน: วิเคราะห์สี่ครั้ง ใช้จ่ายค่าแอลฟาแบบ O'Brien–Fleming

α ด้านเดียว = 0.025 วิเคราะห์ที่ 25%, 50%, 75% และ 100% ของผู้ป่วย อำนาจการทดสอบ 90% พร้อมขอบเขตความไร้ประโยชน์:

```python
from sequential_analysis.group_sequential import group_sequential_design

design = group_sequential_design(0.025, [0.25, 0.5, 0.75, 1.0], spending="obrien-fleming",
                                 futility="obrien-fleming", power=0.9)
for k, (t, b, f) in enumerate(zip(design.fractions, design.bounds, design.futility), start=1):
    print(f"analysis {k} at {t:.0%}: efficacy if Z >= {b:.3f}, futility if Z <= {f:.3f}")
print("patients for an effect of 0.3 standard deviations:", design.max_sample_size(effect=0.3, sigma=1.0))
print(f"expected share of the patients used: {design.expected_fraction(0.0):.2f} with no effect, "
      f"{design.expected_fraction(design.drift):.2f} with the planned effect")
```

```text
analysis 1 at 25%: efficacy if Z >= 4.333, futility if Z <= -1.403
analysis 2 at 50%: efficacy if Z >= 2.963, futility if Z <= 0.325
analysis 3 at 75%: efficacy if Z >= 2.359, futility if Z <= 1.291
analysis 4 at 100%: efficacy if Z >= 2.014, futility if Z <= 2.014
patients for an effect of 0.3 standard deviations: 127
expected share of the patients used: 0.59 with no effect, 0.73 with the planned effect
```

## จุดยุติแบบทวิภาคและแบบการรอดชีพ

```python
binary = group_sequential_design(0.025, [1 / 3, 2 / 3, 1.0], spending="obrien-fleming")
print("patients, response 10% vs 12%, 80% power:",
      binary.max_sample_size_two_proportions(p_control=0.10, p_treatment=0.12, power=0.8))
print("events for a hazard ratio of 0.7, 80% power:", binary.max_events(hazard_ratio=0.7, power=0.8))
print(f"inflation factor over a single analysis: {binary.inflation_factor(0.8):.3f}")
```

```text
patients, response 10% vs 12%, 80% power: 7780
events for a hazard ratio of 0.7, 80% power: 250
inflation factor over a single analysis: 1.013
```

เมื่อใช้จ่ายค่าแอลฟาแบบ O'Brien–Fleming การวิเคราะห์สามครั้งใช้ผู้ป่วยมากกว่าการวิเคราะห์สุดท้ายเพียงครั้งเดียว 1.3%

## การดำเนินการทดลอง

```python
import random

from sequential_analysis.procedures import GroupSequentialProportions

n_max = binary.max_sample_size_two_proportions(p_control=0.10, p_treatment=0.12, power=0.8)
test = GroupSequentialProportions.from_design(binary, n_max)
state, rnd = test.initial_state(), random.Random(3)
for patient in range(n_max):
    arm = patient % 2                                         # 1 treatment, 0 control
    state, out = test.step(state, {"arm": arm, "y": int(rnd.random() < (0.12 if arm else 0.10))})
    if out.analysis:
        print(f"analysis {out.analysis} after {out.n} patients: Z = {out.z:.2f}, bound {out.bound:.2f}")
    if out.decision:
        print("decision:", out.decision)
        break
```

```text
analysis 1 after 2594 patients: Z = 2.14, bound 3.71
analysis 2 after 5187 patients: Z = 2.64, bound 2.51
decision: reject_h0
```

การทดลองหยุดเพราะพบประสิทธิผลที่การวิเคราะห์ครั้งที่สอง หลังจากใช้ผู้ป่วยไปสองในสามของจำนวนตามแผน

## เมื่อการวิเคราะห์ไม่เป็นไปตามแผน

คณะกรรมการกำกับดูแลข้อมูล (data monitoring committee) แทบไม่เคยประชุมตรงที่ 25% ของสารสนเทศพอดี:

* `design.at(fractions)` คำนวณขอบเขตใหม่สำหรับสารสนเทศที่ได้จริง การใช้จ่ายค่าแอลฟาช่วยรักษาระดับนัยสำคัญโดยรวมไว้
* `GroupSequentialMonitor` รับตัวสถิติใดก็ได้ที่คุณคำนวณเอง (แบบจำลอง Cox, แบบจำลองผสม) เป็นค่า Z พร้อมสารสนเทศของมันในการประชุมแต่ละครั้ง

## แล้วถ้าต้องการดูผลหลังผู้ป่วยทุกราย?

แผนแบบลำดับกลุ่มอนุญาตให้ดูผลได้ตามจำนวนครั้งที่วางแผนไว้เท่านั้น หากต้องการติดตามหลังผู้ป่วยหรือเหตุการณ์ทุกครั้ง ให้ใช้กระบวนการที่ใช้ได้ทุกขณะ (anytime-valid): `AnytimeLogRankTest` สำหรับการรอดชีพ `TwoProportionTest` สำหรับอัตราการตอบสนอง `TMixtureSPRT` สำหรับค่าเฉลี่ย กระบวนการเหล่านี้ต้องใช้ผู้ป่วยมากกว่า ณ ขนาดผลที่วางแผนไว้ ดู[บทเรียน: การทดลองด้านการรอดชีพ](../../tutorials/survival.md)

## แนวปฏิบัติด้านกฎระเบียบ

แผนแบบลำดับกลุ่มที่ใช้การใช้จ่ายค่าแอลฟาเป็นแนวทางที่ได้รับการยอมรับในการทดลองเพื่อยืนยันผล (confirmatory trials) ตามที่อธิบายไว้ในแนวทาง ICH E9 และคำแนะนำของ FDA เรื่องแผนแบบปรับตัว (2019) ไลบรารีนี้คำนวณแผนและเก็บบันทึกของการวิเคราะห์แต่ละครั้งที่ตรวจสอบได้และรันต่อได้ (จุดบันทึกสถานะและไดเจสต์ประวัติของมัน) ไลบรารีนี้ไม่ใช่ซอฟต์แวร์ที่ผ่านการตรวจสอบความถูกต้อง (validated) ในความหมายด้านกฎระเบียบ ผู้สนับสนุนการวิจัย (sponsor) ที่ใช้ไลบรารีนี้ในการยื่นเอกสารต้องตรวจสอบความถูกต้องของมันเช่นเดียวกับเครื่องมืออื่นใด

เพิ่มเติม: [บทเรียน: การทดลองแบบลำดับกลุ่ม](../../tutorials/group-sequential.md) ซึ่งเปรียบเทียบตัวเลขกับ rpact; [เอกสารอ้างอิง: การออกแบบและการวางแผน](../../reference/design.md)
