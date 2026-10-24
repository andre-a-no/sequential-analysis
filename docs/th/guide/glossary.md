---
description: อภิธานศัพท์การวิเคราะห์แบบลำดับและการอนุมานที่ใช้ได้ทุกขณะ - ค่า e (e-value), e-process, ลำดับช่วงความเชื่อมั่น, ค่า p ที่ใช้ได้เสมอ, mSPRT, การใช้จ่ายค่าแอลฟา, สัดส่วนสารสนเทศ, ARL, SRM, CUPED, e-BH - พร้อมคำพ้องความหมายและกระบวนการใน sequential-analysis ที่ใช้แต่ละแนวคิด
language: th
---

# อภิธานศัพท์

> นี่คือฉบับแปลของ[หน้าภาษาอังกฤษ](../../guide/glossary.md) ซึ่งยังไม่ได้รับการตรวจทานโดยเจ้าของภาษา หากสองฉบับมีเนื้อหาต่างกัน ให้ถือหน้าภาษาอังกฤษเป็นหลัก

ศัพท์ที่ใช้ในการวิเคราะห์แบบลำดับและในไลบรารีนี้ คำพ้องความหมายที่ใช้กันทั่วไปอยู่ในวงเล็บ

**การวิเคราะห์แบบลำดับ** (sequential analysis, sequential testing, sequential inference) สถิติที่ไม่ได้กำหนดจำนวนค่าสังเกตไว้ล่วงหน้า หลังแต่ละค่าสังเกตหรือแต่ละกลุ่มของค่าสังเกต กระบวนการจะตัดสินว่าจะหยุดหรือดำเนินต่อ ริเริ่มโดย Wald (1945)

**การแอบดูผล** (peeking, optional stopping, data peeking, continuous monitoring) การดูผลการทดสอบแบบขนาดตัวอย่างคงที่ซ้ำ ๆ แล้วหยุดเมื่อผลมีนัยสำคัญ ซึ่งทำให้อัตราผลบวกลวงสูงขึ้น ดู[การแอบดูผล](peeking.md)

**SPRT** (sequential probability ratio test, การทดสอบอัตราส่วนความน่าจะเป็นแบบลำดับ, การทดสอบของ Wald) สะสมลอการิทึมของอัตราส่วนภาวะน่าจะเป็น (log likelihood ratio) ของสมมติฐานเชิงเดียวสองข้อ และหยุดเมื่อค่านั้นออกนอกช่วง `SPRT` รุ่นที่มีการตัดปลาย (truncated) ได้แก่ `TwoSPRT` (2-SPRT ของ Lorden) และ `kiefer_weiss_plan` ดู [SPRT](sprt.md)

**แผนแบบลำดับกลุ่ม** (group sequential design, interim analyses, group sequential trial) การวิเคราะห์ตามแผนจำนวนไม่มาก แต่ละครั้งมีขอบเขตของตัวเอง ขอบเขตถูกเลือกให้ความคลาดเคลื่อนประเภทที่ 1 (type I error) โดยรวมเท่ากับแอลฟา `group_sequential_design` ดู[การทดลองทางคลินิก](clinical-trials.md)

**ฟังก์ชันการใช้จ่ายค่าแอลฟา** (alpha spending function, error spending, Lan–DeMets) ระบุว่าความคลาดเคลื่อนประเภทที่ 1 ถูกใช้ไปได้มากเท่าใด ณ แต่ละสัดส่วนสารสนเทศ การใช้จ่ายแบบ O'Brien–Fleming ใช้น้อยในช่วงแรก การใช้จ่ายแบบ Pocock ใช้อย่างสม่ำเสมอ `spending="obrien-fleming"`, `"pocock"`, ...

**สัดส่วนสารสนเทศ** (information fraction) สัดส่วนของสารสนเทศเชิงสถิติตามแผน (ผู้ป่วย เหตุการณ์) ที่ได้ ณ การวิเคราะห์ครั้งหนึ่ง

**ขอบเขตความไร้ประโยชน์** (futility boundary, non-binding futility) ขอบเขตล่าง ถ้าต่ำกว่านี้ แนะนำให้หยุดเพราะไม่มีผล ขอบเขตแบบไม่ผูกมัด (non-binding) สามารถเพิกเฉยได้โดยไม่ทำให้ความคลาดเคลื่อนประเภทที่ 1 สูงขึ้น

**การอนุมานที่ใช้ได้ทุกขณะ** (anytime-valid inference, always-valid inference, safe anytime-valid inference, SAVI) การทดสอบและช่วงที่การรับประกันเป็นจริงพร้อมกันทุกขนาดตัวอย่าง จึงติดตามได้อย่างต่อเนื่องและหยุดด้วยเหตุผลใดก็ได้

**ค่า e** (e-value, e-variable, betting score) ตัวสถิติที่ไม่เป็นลบซึ่งมีค่าคาดหวังภายใต้สมมติฐานว่างไม่เกิน 1 ค่า e ที่สูงเป็นหลักฐานคัดค้านสมมติฐานว่าง การปฏิเสธเมื่อค่านี้เกิน 1/alpha มีความคลาดเคลื่อนประเภทที่ 1 ไม่เกินแอลฟา คือเอาต์พุต `log_e_value` ของหลายกระบวนการ

**e-process** (test martingale, test supermartingale, wealth process; มาร์ทิงเกลสำหรับทดสอบ, กระบวนการความมั่งคั่ง) ลำดับของค่า e ที่ยังใช้ได้ ณ เวลาหยุด (stopping times) ค่าสูงสุดสะสมของมันจะข้าม 1/alpha ด้วยความน่าจะเป็นไม่เกินแอลฟาภายใต้สมมติฐานว่าง (อสมการของ Ville)

**ค่า p ที่ใช้ได้เสมอ** (always-valid p-value, anytime-valid p-value, sequential p-value) ค่า p ที่ใช้ได้ ณ เวลาหยุดใดก็ได้ เป็นส่วนกลับของค่าสูงสุดสะสมของ e-process คือเอาต์พุต `p_value` ของกระบวนการที่ใช้ได้ทุกขณะ

**ลำดับช่วงความเชื่อมั่น** (confidence sequence, anytime-valid confidence interval, always-valid confidence interval, time-uniform confidence interval) ลำดับของช่วงที่ครอบคลุมค่าจริงพร้อมกันทุกขนาดตัวอย่างด้วยความน่าจะเป็นอย่างน้อย 1 − alpha `BettingConfidenceSequence`, `QuantileConfidenceSequence`, `CatoniConfidenceSequence`, `AsymptoticConfidenceSequence` และเอาต์พุต `lower` กับ `upper` ของการทดสอบหลายตัว ดู[ลำดับช่วงความเชื่อมั่น](confidence-sequences.md)

**mSPRT** (mixture SPRT, Robbins' mixture) SPRT ที่สมมติฐานแย้งถูกเฉลี่ยตามการแจกแจงก่อน (prior) ทำให้ใช้ได้ทุกขณะเมื่อเทียบกับสมมติฐานแย้งทุกค่า `NormalMixtureSPRT` (ทราบความแปรปรวน), `TMixtureSPRT` (ไม่ทราบความแปรปรวน)

**การทดสอบด้วยการเดิมพัน** (testing by betting) การสร้าง e-process ในรูปความมั่งคั่งของนักพนันที่เดิมพันคัดค้านสมมติฐานว่าง `BettingMeanTest`, `BettingConfidenceSequence`, `KernelTwoSampleTest`

**GROW** (growth-rate optimal; เหมาะสมที่สุดด้านอัตราการเติบโต) ค่า e ที่เลือกให้ค่าคาดหวังของการเติบโตเชิงลอการิทึมของหลักฐานภายใต้สมมติฐานแย้งสูงสุด `TwoProportionTest(method="grow")`

**การอนุมานสากล** (universal inference) ค่า e จากอัตราส่วนภาวะน่าจะเป็น โดยประมาณสมมติฐานแย้งจากข้อมูลในอดีตเท่านั้น ยังใช้ได้ภายใต้แผนแบบปรับตัว (adaptive designs) `TwoProportionTest(method="universal")`

**e-BH** (e-Benjamini–Hochberg) ควบคุมอัตราการค้นพบลวง (false discovery rate) เมื่อมีค่า e จำนวนมาก ภายใต้ความขึ้นต่อกันแบบใดก็ได้ `MultipleTests`, `e_bh`

**e-LOND, FDR ออนไลน์** (online FDR) การควบคุมอัตราการค้นพบลวงสำหรับชุดของสมมติฐานที่ตัดสินทีละข้อ `OnlineFDR`

**SRM** (sample ratio mismatch; สัดส่วนตัวอย่างไม่ตรงตามที่กำหนด) สัดส่วนทราฟฟิกที่สังเกตได้ระหว่างกลุ่มต่างไปจากที่ตั้งค่าไว้ ซึ่งเป็นสัญญาณของบั๊กในการทดลอง `SampleRatioMismatch`

**CUPED** (controlled experiments using pre-experiment data, covariate adjustment, regression adjustment; การปรับด้วยตัวแปรร่วม, การปรับด้วยการถดถอย) ลดความแปรปรวนของขนาดผลในการทดสอบ A/B ด้วยตัวแปรร่วมที่วัดก่อนการทดลอง `ABTest(covariate=True)`, `AnytimeLinearModel`

**ตัวชี้วัดแบบอัตราส่วน** (ratio metric, delta method; วิธีเดลตา) ตัวชี้วัดที่เป็นอัตราส่วนของผลรวมสองค่าต่อผู้ใช้ เช่น รายได้ต่อเซสชัน `RatioABTest`

**การตรวจจับจุดเปลี่ยน** (change-point detection, change detection, quickest detection, online anomaly detection) การส่งสัญญาณเตือนไม่นานหลังจากที่การแจกแจงของสายข้อมูลเปลี่ยนไป `CUSUM`, `ShiryaevRoberts`, `MeanEDetector`, `QuantileEDetector`, `BayesianChangePoint` ดู[การตรวจจับการเปลี่ยนแปลง](change-detection.md)

**ARL** (average run length, ARL₀, mean time to false alarm; ความยาวรันเฉลี่ย, เวลาเฉลี่ยจนถึงสัญญาณเตือนลวง) จำนวนค่าสังเกตที่คาดหวังจนถึงสัญญาณเตือนลวงเมื่อไม่มีอะไรเปลี่ยนแปลง เป็นตัวควบคุมสัญญาณเตือนลวงของตัวตรวจจับการเปลี่ยนแปลง

**E-detector** ตัวตรวจจับการเปลี่ยนแปลงที่สร้างจาก e-process โดยเริ่ม e-process หนึ่งตัว ณ ทุกเวลาที่อาจเกิดการเปลี่ยนแปลง ARL ของมันได้รับการรับประกันภายใต้สมมติฐานว่างแบบไม่อิงพารามิเตอร์ (nonparametric) `MeanEDetector`, `QuantileEDetector`

**ปัญหา Kiefer–Weiss** (Kiefer–Weiss problem) การหาการทดสอบแบบลำดับที่มีขนาดตัวอย่างสูงสุดจำกัด ซึ่งทำให้ขนาดตัวอย่างคาดหวังที่มากที่สุดมีค่าน้อยที่สุด `kiefer_weiss_plan`

**คุณลักษณะการดำเนินงาน** (operating characteristic) ความน่าจะเป็นของความคลาดเคลื่อนและการแจกแจงของขนาดตัวอย่างของแผนหนึ่ง ในรูปฟังก์ชันของพารามิเตอร์จริง `operating_characteristic`

**จุดบันทึกสถานะ** (checkpoint) ค่า JSON ที่การรันสามารถดำเนินต่อได้อย่างแม่นตรง `Run.checkpoint`, `Run.restore` ดู[สายข้อมูล](streaming.md)

**ไดเจสต์ประวัติ** (history digest) สายโซ่แฮช SHA-256 ของค่าสังเกตที่การรันใช้ไป เก็บไว้ในทุกจุดบันทึกสถานะเพื่อการตรวจสอบ (audit)

**การรับประกัน** (guarantee; `exact`, `asymptotic`, `model`, `approximate`, `none`) แอตทริบิวต์ที่ทุกกระบวนการในไลบรารีนี้ใช้ระบุว่าตนสัญญาอะไร ดู[วิธีใด?](../../choosing.md)
