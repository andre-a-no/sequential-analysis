---
description: Cách dừng sớm một kiểm định A/B mà không làm tăng dương tính giả, bằng Python. Kiểm định hợp lệ tại mọi thời điểm cho tỷ lệ chuyển đổi và doanh thu bị chặn, kiểm tra lệch tỷ lệ mẫu (SRM) và kiểm soát tỷ lệ phát hiện sai (FDR) trên nhiều chỉ số, với sequential-analysis.
language: vi
---

# Làm sao dừng sớm một kiểm định A/B mà không làm tăng dương tính giả?

> Đây là bản dịch của [trang tiếng Anh](../../guide/ab-testing.md). Bản dịch chưa được người bản ngữ rà soát; nếu hai bản có chỗ khác nhau, trang tiếng Anh là bản có giá trị.

**Trả lời ngắn.** Hãy dùng một kiểm định hợp lệ tại mọi thời điểm
(anytime-valid): giá trị p và khoảng tin cậy của nó vẫn hợp lệ dù bạn xem
thường xuyên đến đâu, nên bạn có thể dừng ngay khi kết quả đã rõ. Trong
sequential-analysis:

| Chỉ số | Thủ tục | Bảo đảm |
|---|---|---|
| tỷ lệ chuyển đổi (0/1) | `TwoProportionTest` | exact |
| mọi chỉ số bị chặn (doanh thu có giới hạn trên, tỷ phần) | `BoundedABTest` | exact |
| số sự kiện trên một đơn vị phơi nhiễm | `RateRatioTest` | exact với số đếm Poisson |
| chỉ số dạng tỷ số (doanh thu mỗi phiên) | `RatioABTest` | asymptotic |
| trung bình với biến đồng hành trước thí nghiệm (CUPED) | `ABTest` | asymptotic |
| lưu lượng có được chia như dự định không? | `SampleRatioMismatch` | exact |
| nhiều chỉ số hoặc nhiều nhánh cùng lúc | `MultipleTests` (e-BH) | tỷ lệ phát hiện sai, exact |

Đưa vào mỗi thủ tục từng người dùng một: `state, out = test.step(state, {...})`.
Hành động theo `out.decision` bất cứ khi nào bạn muốn.

## Tỷ lệ chuyển đổi: dừng khi dữ liệu đã đủ kết luận

Nhóm đối chứng chuyển đổi 10% người dùng, nhóm can thiệp 12%. Kiểm định được
xem sau mỗi người dùng và dừng ở quyết định đầu tiên:

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

Để so sánh, một kiểm định cỡ mẫu cố định có lực kiểm định (power) 80% cho mức
tăng này cần khoảng 3.850 người dùng mỗi nhánh, tổng cộng 7.700, và chỉ được
đọc một lần, vào lúc cuối. Kiểm định hợp lệ tại mọi thời điểm phải trả giá cho
sự tự do của nó: để đạt cùng lực kiểm định, nó cần 1,3–1,6 lần số người dùng
của một lần phân tích duy nhất, và lượt chạy này còn tốn nhiều hơn thế. Đổi
lại, không cần ấn định cỡ mẫu từ trước, và bạn có thể xem kết quả hằng ngày rồi
dừng ngay khi nó đã rõ. Khi hiệu ứng lớn hơn dự kiến, điều đó xảy ra sớm hơn
nhiều.

## Doanh thu: một khoảng chính xác cho chỉ số bị chặn

`BoundedABTest` chỉ cần các cận của chỉ số. Hãy giới hạn doanh thu ở một giá
trị bạn chọn trước khi kiểm định (ở đây là 30), khi đó dãy tin cậy (confidence
sequence) cho hiệu hai trung bình là chính xác với mọi phân phối:

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

Khoảng này đúng đồng thời tại tất cả 20.000 lần xem, không chỉ ở lần cuối. Ở
đây nó vẫn chứa 0: 20.000 người dùng là chưa đủ để xác lập mức tăng khoảng 0,5
trên một chỉ số nhiễu như thế này, nên thí nghiệm tiếp tục.

## Kiểm tra việc chia lưu lượng trước tiên

Lệch tỷ lệ mẫu (sample ratio mismatch) nghĩa là cách chia khác với cấu hình, chẳng
hạn do lỗi trong khâu phân nhóm hoặc ghi log. Các ước lượng hiệu ứng từ một
thí nghiệm như vậy không đáng tin. Một độ lệch từ 50/50 thành 52/48 được phát
hiện ngay khi thí nghiệm đang chạy:

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

## Nhiều chỉ số cùng lúc

Kiểm định mười chỉ số độc lập, mỗi chỉ số ở mức 5%, cho xác suất khoảng 40% có
ít nhất một phát hiện sai. `MultipleTests` kết hợp giá trị e (e-value) của tất
cả các kiểm định bằng thủ tục e-BH, nên tỷ lệ phát hiện sai (false discovery
rate) được giữ ở `alpha` tại mọi thời điểm dừng:

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

## Những điểm cần lưu ý

* **Ngẫu nhiên hóa chính đơn vị bạn phân tích.** Nếu người dùng được ngẫu nhiên
  hóa, hãy đưa vào một bản ghi cho mỗi người dùng, không phải cho mỗi lượt xem
  trang. Với các chỉ số theo phiên, hãy dùng `RatioABTest`, thủ tục làm việc
  trên tổng theo người dùng.
* **Ấn định giới hạn trên của chỉ số bị chặn trước khi kiểm định.** Chọn nó sau
  khi đã thấy dữ liệu sẽ làm mất hiệu lực bảo đảm.
* **Các thủ tục tiệm cận cần mẫu lớn.** Với `ABTest` và `RatioABTest`, khoảng
  chỉ hợp lệ xấp xỉ trong các lượt chạy dài. Hãy ưu tiên các thủ tục chính xác
  khi chúng phù hợp.
* **Phân bổ lưu lượng thích ứng** (bandit) cần một kiểm định vẫn hợp lệ khi
  cách chia phụ thuộc vào kết quả:
  `TwoProportionTest(method="universal")` hoặc
  `BoundedABTest(propensity_input=...)`. Xem
  [bài hướng dẫn §10](../../tutorials/ab-test.md).

Thêm: [bài hướng dẫn kiểm định A/B](../../tutorials/ab-test.md) (CUPED, chỉ số
dạng tỷ số, tần suất, lập kế hoạch thời lượng) và
[một chương trình thí nghiệm](../../tutorials/experiment-programme.md)
(tỷ lệ phát hiện sai trên nhiều thí nghiệm).
