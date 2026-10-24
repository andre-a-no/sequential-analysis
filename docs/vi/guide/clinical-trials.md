---
description: Cách lập kế hoạch và thực hiện phân tích giữa kỳ cho thử nghiệm lâm sàng trong Python, với thiết kế tuần tự theo nhóm (O'Brien–Fleming, Pocock, hàm chi tiêu alpha Lan–DeMets, ngưỡng vô ích), cỡ mẫu cho trung bình, tỷ lệ và sống còn, được đối chiếu với rpact, với sequential-analysis.
language: vi
---

# Làm sao lập kế hoạch phân tích giữa kỳ cho thử nghiệm lâm sàng?

> Đây là bản dịch của [trang tiếng Anh](../../guide/clinical-trials.md). Bản dịch chưa được người bản ngữ rà soát; nếu hai bản có chỗ khác nhau, trang tiếng Anh là bản có giá trị.

**Trả lời ngắn.** Hãy dùng một thiết kế tuần tự theo nhóm (group sequential
design). `group_sequential_design(alpha, fractions, spending=...)` trong
`sequential_analysis.group_sequential` tính:

* các ngưỡng hiệu quả (efficacy boundary), với hàm chi tiêu alpha (alpha
  spending) Lan–DeMets (kiểu O'Brien–Fleming, kiểu Pocock và các kiểu khác);
* các ngưỡng vô ích không ràng buộc (non-binding futility boundary);
* lực kiểm định và cỡ mẫu kỳ vọng;
* cỡ mẫu tối đa cho trung bình và tỷ lệ, hoặc số biến cố cho phân tích sống
  còn.

Các ngưỡng và cỡ mẫu khớp với gói R rpact. Sau đó các thủ tục kiểm định
(`GroupSequentialTest`, `GroupSequentialTwoMeans`,
`GroupSequentialProportions`, `GroupSequentialLogRank`) vận hành thử nghiệm,
từng bệnh nhân hoặc từng biến cố một. Chúng thực hiện mỗi phân tích giữa kỳ
(interim analysis) khi đạt tới tỷ lệ thông tin (information fraction) tương ứng.

## Thiết kế: bốn lần phân tích, chi tiêu O'Brien–Fleming

α một phía = 0,025, phân tích tại 25%, 50%, 75% và 100% số bệnh nhân, lực kiểm
định 90%, có ngưỡng vô ích:

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

## Tiêu chí đánh giá nhị phân và sống còn

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

Với chi tiêu O'Brien–Fleming, ba lần phân tích tốn thêm 1,3% số bệnh nhân so
với một lần phân tích cuối cùng duy nhất.

## Vận hành thử nghiệm

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

Thử nghiệm dừng vì hiệu quả ở lần phân tích thứ hai, sau hai phần ba số bệnh
nhân dự kiến.

## Khi các lần phân tích không diễn ra như kế hoạch

Hội đồng giám sát dữ liệu (data monitoring committee) hiếm khi họp đúng tại
25% lượng thông tin:

* `design.at(fractions)` tính lại các ngưỡng cho lượng thông tin thực tế đã
  đạt được. Hàm chi tiêu alpha giữ nguyên mức ý nghĩa tổng thể.
* `GroupSequentialMonitor` nhận bất kỳ thống kê nào bạn tự tính (mô hình Cox,
  mô hình hỗn hợp) dưới dạng giá trị Z cùng lượng thông tin của nó tại mỗi
  cuộc họp.

## Còn nếu bạn muốn xem sau mỗi bệnh nhân?

Một thiết kế tuần tự theo nhóm chỉ cho phép số lần xem đã lên kế hoạch. Để
giám sát sau mỗi bệnh nhân hoặc biến cố, hãy dùng một thủ tục hợp lệ tại mọi
thời điểm (anytime-valid): `AnytimeLogRankTest` cho sống còn,
`TwoProportionTest` cho tỷ lệ đáp ứng, `TMixtureSPRT` cho trung bình. Chúng cần
nhiều bệnh nhân hơn tại mức hiệu ứng đã lên kế hoạch. Xem
[bài hướng dẫn: thử nghiệm sống còn](../../tutorials/survival.md).

## Thực tiễn quản lý dược

Thiết kế tuần tự theo nhóm với hàm chi tiêu alpha là cách tiếp cận đã được
thiết lập trong các thử nghiệm xác nhận (confirmatory trial), được mô tả trong
hướng dẫn ICH E9 và hướng dẫn của FDA về thiết kế thích ứng (2019). Thư viện này
tính toán các thiết kế và lưu một bản ghi có thể kiểm toán và tiếp tục lại cho
từng lần phân tích (điểm kiểm tra và mã băm lịch sử của nó). Nó không phải là
phần mềm đã được thẩm định (validated) theo nghĩa quản lý dược: nhà tài trợ dùng
nó trong hồ sơ nộp phải tự thẩm định nó như mọi công cụ khác.

Thêm: [bài hướng dẫn: thử nghiệm tuần tự theo nhóm](../../tutorials/group-sequential.md),
có so sánh các con số với rpact;
[tài liệu tham chiếu: thiết kế và lập kế hoạch](../../reference/design.md).
