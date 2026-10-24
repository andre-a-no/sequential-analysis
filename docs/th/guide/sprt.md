---
description: วิธีรันการทดสอบอัตราส่วนความน่าจะเป็นแบบลำดับ (SPRT) ของ Wald ใน Python ด้วย sequential-analysis อัตราความคลาดเคลื่อน ขนาดตัวอย่างเฉลี่ยเทียบกับการทดสอบแบบขนาดตัวอย่างคงที่ และทางเลือกแบบตัดปลาย (2-SPRT, แผนที่เหมาะสมที่สุดของ Kiefer–Weiss)
language: th
---

# จะรัน SPRT ของ Wald ใน Python ได้อย่างไร?

> นี่คือฉบับแปลของ[หน้าภาษาอังกฤษ](../../guide/sprt.md) ซึ่งยังไม่ได้รับการตรวจทานโดยเจ้าของภาษา หากสองฉบับมีเนื้อหาต่างกัน ให้ถือหน้าภาษาอังกฤษเป็นหลัก

**คำตอบสั้น ๆ** `SPRT(family, theta0, theta1, alpha, beta)` จาก `sequential_analysis.procedures` คือการทดสอบอัตราส่วนความน่าจะเป็นแบบลำดับ (sequential probability ratio test, SPRT) ของ Wald ซึ่งตัดสินระหว่างสมมติฐานเชิงเดียว (simple hypotheses) สองข้อโดยใช้ค่าสังเกตน้อยที่สุดโดยเฉลี่ย ป้อนค่าสังเกตทีละค่าและหยุดเมื่อได้การตัดสินใจครั้งแรก ในตัวอย่างด้านล่าง SPRT ใช้ค่าสังเกตราวครึ่งหนึ่งของการทดสอบแบบขนาดตัวอย่างคงที่ที่มีอัตราความคลาดเคลื่อนเท่ากัน คือเฉลี่ย 65–76 ชิ้นแทนที่จะเป็น 133 ชิ้น หากคุณต้องการขนาดตัวอย่างสูงสุดที่รับประกันได้ ให้ใช้ `TwoSPRT` หรือแผนจาก `kiefer_weiss_plan` แทน

## ตัวอย่าง: อัตราของเสียเป็น 10% หรือ 20%?

ล็อตสินค้าจะถูกยอมรับหากอัตราของเสียเป็น 10% และถูกปฏิเสธหากเป็น 20% โดยอัตราความคลาดเคลื่อนทั้งสองแบบเท่ากับ 5%:

```python
import random

from sequential_analysis.procedures import SPRT, Bernoulli

test = SPRT(Bernoulli(), theta0=0.10, theta1=0.20, alpha=0.05, beta=0.05)

def inspect_items(rate, seed):
    """Inspect items until the test decides; returns (decision, items inspected)."""
    rnd = random.Random(seed)
    state = test.initial_state()
    while state.decision is None:
        state, out = test.step(state, {"x": int(rnd.random() < rate)})
    return state.decision, state.n

decision, n = inspect_items(0.10, seed=1)
print(f"a good batch: {decision} after {n} items")
```

```text
a good batch: accept_h0 after 108 items
```

เมื่อทดสอบหลายล็อต ผลเป็นอย่างไร?

```python
for rate in (0.10, 0.20):
    results = [inspect_items(rate, seed) for seed in range(2000)]
    wrong = sum(d == ("reject_h0" if rate == 0.10 else "accept_h0") for d, _ in results) / len(results)
    average = sum(n for _, n in results) / len(results)
    longest = max(n for _, n in results)
    print(f"defect rate {rate:.0%}: wrong decision {wrong:.1%}, average {average:.0f} items, longest {longest}")
```

```text
defect rate 10%: wrong decision 3.5%, average 76 items, longest 370
defect rate 20%: wrong decision 4.3%, average 65 items, longest 315
```

การทดสอบแบบขนาดตัวอย่างคงที่ที่มีอัตราความคลาดเคลื่อนเท่ากันต้องตรวจราว 133 ชิ้นในทุกล็อต (การประมาณด้วยการแจกแจงปกติ) SPRT ตรวจน้อยกว่านั้น 43–51% โดยเฉลี่ย อย่างไรก็ตาม ขนาดตัวอย่างของ SPRT เป็นค่าสุ่มและไม่มีขีดจำกัดบน และบางล็อตใช้เวลานานกว่าค่าเฉลี่ยมาก

ค่าเกณฑ์ (thresholds) เป็นของ Wald คือ log((1 − β)/α) และ log(β/(1 − α)) ซึ่งรับประกันว่า สำหรับขนาดตัวอย่างใดก็ตาม ณ เวลาหยุด อัตราความคลาดเคลื่อนจริง α′ และ β′ เป็นไปตาม α′ ≤ α/(1 − β), β′ ≤ β/(1 − α) และ α′ + β′ ≤ α + β อัตราส่วนภาวะน่าจะเป็น (likelihood ratio) จะเลยค่าเกณฑ์ไปเล็กน้อยเมื่อหยุด ในทางปฏิบัติอัตราจริงจึงต่ำกว่าค่าที่กำหนด ดังเช่นในที่นี้ นี่คือความหมายของ `SPRT.guarantee == "exact"` หากต้องการอัตราความคลาดเคลื่อนที่คำนวณได้แม่นตรงแทนที่จะเป็นเพียงขอบเขต ให้ใช้ `operating_characteristic` กับแผน (ดูด้านล่าง)

## เมื่อต้องการขนาดตัวอย่างสูงสุด

* `TwoSPRT` (2-SPRT ของ Lorden) หยุดภายในขอบฟ้าเวลา (horizon) ที่กำหนด และเกือบทำให้ขนาดตัวอย่างคาดหวังในกรณีเลวร้ายที่สุดมีค่าน้อยที่สุด
* `kiefer_weiss_plan(theta0, theta1, alpha0, alpha1, horizon, family=...)` ใน `sequential_analysis.design` คำนวณแผนที่เหมาะสมที่สุดซึ่งมีขนาดตัวอย่างสูงสุดจำกัดด้วยการอุปนัยย้อนกลับ (backward induction) `PlanTest` ใช้รันแผนนั้น และ `operating_characteristic` ให้อัตราความคลาดเคลื่อนแบบแม่นตรงและขนาดตัวอย่างคาดหวังโดยไม่ต้องจำลอง ดู `examples/07_design_kiefer_weiss.py`
* หากต้องการดูผลตามแผนเพียงไม่กี่ครั้งแทนที่จะดูทุกค่าสังเกต ให้ใช้[แผนแบบลำดับกลุ่ม](clinical-trials.md)

## เมื่อ SPRT ไม่ใช่เครื่องมือที่เหมาะ

* **สมมติฐานไม่ใช่สมมติฐานเชิงเดียว** "อัตราเป็น 10%" เทียบกับ "อัตราเป็นค่าอื่นใดก็ได้" คือสมมติฐานแย้งเชิงประกอบ (composite alternative) ให้ใช้ mixture SPRT (`NormalMixtureSPRT`, `TMixtureSPRT`) หรือการทดสอบด้วยการเดิมพัน (`BettingMeanTest`) ซึ่งใช้ได้ทุกขณะ (anytime-valid) เมื่อเทียบกับสมมติฐานแย้งทุกค่า
* **ค่าจริงอยู่ระหว่าง θ₀ และ θ₁** เมื่อนั้น SPRT จะช้าที่สุด และขนาดตัวอย่างคาดหวังอาจเกินขนาดตัวอย่างคงที่ แผนของ Kiefer–Weiss ถูกสร้างมาสำหรับกรณีนี้โดยเฉพาะ

ตระกูลการแจกแจงที่ใช้ได้กับกระบวนการอัตราส่วนภาวะน่าจะเป็น: `Gaussian` (ทราบความแปรปรวน), `Bernoulli`, `Poisson`, `Exponential`
