---
description: Dãy tin cậy (confidence sequence) là các khoảng tin cậy hợp lệ đồng thời ở mọi cỡ mẫu, nên có thể giám sát liên tục. Cách tính chúng trong Python cho trung bình bị chặn, trung vị hoặc phân vị, và trung bình của phân phối đuôi nặng, với sequential-analysis.
language: vi
---

# Làm sao có khoảng tin cậy vẫn hợp lệ khi tôi xem đi xem lại?

> Đây là bản dịch của [trang tiếng Anh](../../guide/confidence-sequences.md). Bản dịch chưa được người bản ngữ rà soát; nếu hai bản có chỗ khác nhau, trang tiếng Anh là bản có giá trị.

**Trả lời ngắn.** Hãy dùng một **dãy tin cậy** (confidence sequence). Đó là một
dãy các khoảng, mỗi khoảng sau một quan sát, chứa giá trị thật đồng thời ở mọi
cỡ mẫu với xác suất ít nhất 95%. Bạn có thể theo dõi nó, dừng khi nó đủ hẹp
hoặc không còn chứa 0, và báo cáo khoảng tại thời điểm bạn dừng. Một khoảng tin
cậy 95% thông thường chỉ hứa 95% tại một cỡ mẫu duy nhất được ấn định từ trước.

| Đại lượng cần ước lượng | Giả định | Thủ tục | Bảo đảm |
|---|---|---|---|
| trung bình của dữ liệu bị chặn (tỷ lệ, điểm số, doanh thu có giới hạn trên) | giá trị nằm trong `[lower, upper]` | `BettingConfidenceSequence` | exact |
| trung vị, phân vị thứ 90, phân vị bất kỳ | không có | `QuantileConfidenceSequence` | exact |
| trung bình khi đuôi nặng hoặc có giá trị ngoại lai | một cận trên của độ lệch chuẩn | `CatoniConfidenceSequence` | exact |
| trung bình của dữ liệu chuẩn, chưa biết phương sai | tính chuẩn | `TMixtureSPRT` (`lower`, `upper`) | exact dưới giả định chuẩn |
| trung bình của dữ liệu bất kỳ, lượt chạy dài | phương sai hữu hạn | `AsymptoticConfidenceSequence` | asymptotic |
| chênh lệch giữa hai nhánh | xem [kiểm định A/B](ab-testing.md) | `BoundedABTest`, `ABTest` | exact / asymptotic |

## Khoảng thông thường thất bại khi bị theo dõi

Rút 500 quan sát của một biến 0/1 có trung bình 0,3, và từ quan sát thứ 30 trở
đi, sau mỗi quan sát tính khoảng 95% theo sách giáo khoa: trung bình ± 1,96 sai
số chuẩn. Trong bao nhiêu trên 100 lượt chạy, khoảng này bỏ lỡ trung bình thật
tại một thời điểm nào đó?

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

"95%" của nó chỉ đúng tại một cỡ mẫu ấn định từ trước. Dãy tin cậy cho cùng dữ
liệu, xây dựng bằng đặt cược (Waudby-Smith and Ramdas 2024), theo cách xây dựng
chỉ bỏ lỡ giá trị thật tại một n nào đó trong tối đa 5% số lượt chạy:

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

## Trung vị của độ trễ, không cần giả định nào

Độ trễ (latency) có phân phối lệch và đuôi nặng, nên khoảng trung bình ± sai số
chuẩn không đáng tin với chúng. `QuantileConfidenceSequence` bao phủ mọi phân
vị của mọi phân phối, kể cả khi có giá trị trùng nhau:

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

Giá trị thật là 120 ms và 258,8 ms. Cả hai khoảng đều đúng đồng thời tại tất cả
2.000 cỡ mẫu.

## Những điểm cần lưu ý

* **Các cận và giới hạn trên là một phần của giả định.** Hãy chọn `lower` và
  `upper` trước khi thấy dữ liệu. Giá trị nằm ngoài chúng sẽ bị từ chối.
* **Không phương pháp nào cho độ phủ chính xác với trung bình của dữ liệu không
  bị chặn bất kỳ.** Với dữ liệu như vậy, hãy dùng phân vị, giới hạn các giá
  trị, giả định một cận trên của độ lệch chuẩn (Catoni), hoặc chấp nhận một dãy
  tiệm cận.
* **Dãy tin cậy rộng hơn một khoảng đơn lẻ** tại cùng cỡ mẫu. Độ rộng đó là cái
  giá để hợp lệ đồng thời ở mọi cỡ mẫu.

Thêm: [Phương pháp nào?](../../choosing.md),
[tài liệu tham chiếu: hợp lệ tại mọi thời điểm và phi tham số](../../reference/anytime.md).
