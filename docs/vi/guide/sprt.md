---
description: Cách chạy kiểm định tỷ số xác suất tuần tự (SPRT) của Wald trong Python với sequential-analysis. Tỷ lệ sai lầm, cỡ mẫu trung bình so với kiểm định cỡ mẫu cố định, và các phương án có cắt cụt (2-SPRT, kế hoạch tối ưu Kiefer–Weiss).
language: vi
---

# Làm sao chạy SPRT của Wald trong Python?

> Đây là bản dịch của [trang tiếng Anh](../../guide/sprt.md). Bản dịch chưa được người bản ngữ rà soát; nếu hai bản có chỗ khác nhau, trang tiếng Anh là bản có giá trị.

**Trả lời ngắn.** `SPRT(family, theta0, theta1, alpha, beta)` trong
`sequential_analysis.procedures` cài đặt kiểm định tỷ số xác suất tuần tự
(sequential probability ratio test, SPRT) của Wald. Nó quyết định giữa hai giả
thuyết đơn với số quan sát trung bình ít nhất. Hãy đưa vào từng quan sát một và
dừng ở quyết định đầu tiên. Trong ví dụ dưới đây, nó cần khoảng một nửa số quan
sát của một kiểm định cỡ mẫu cố định có cùng tỷ lệ sai lầm: trung bình 65–76
sản phẩm thay vì 133. Nếu bạn cần cỡ mẫu tối đa được bảo đảm, hãy dùng `TwoSPRT`
hoặc một kế hoạch từ `kiefer_weiss_plan`.

## Ví dụ: tỷ lệ lỗi là 10% hay 20%?

Một lô hàng được chấp nhận nếu tỷ lệ lỗi là 10% và bị loại nếu là 20%, với cả
hai tỷ lệ sai lầm đều là 5%:

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

Trên nhiều lô hàng thì nó hoạt động tốt đến đâu?

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

Một kiểm định cỡ mẫu cố định với cùng tỷ lệ sai lầm kiểm tra khoảng 133 sản
phẩm ở mỗi lô (xấp xỉ chuẩn). SPRT kiểm tra trung bình ít hơn 43–51%. Tuy
nhiên, cỡ mẫu của nó là ngẫu nhiên và không có giới hạn trên, và một số lô mất
thời gian lâu hơn nhiều so với trung bình.

Các ngưỡng là của Wald: log((1 − β)/α) và log(β/(1 − α)). Chúng bảo đảm rằng,
với bất kỳ cỡ mẫu nào tại thời điểm dừng, các tỷ lệ sai lầm thực tế α′ và β′
thỏa mãn α′ ≤ α/(1 − β), β′ ≤ β/(1 − α) và α′ + β′ ≤ α + β. Tỷ số hợp lý vượt
quá ngưỡng khi dừng, nên trong thực tế các tỷ lệ thấp hơn giá trị danh nghĩa,
như ở đây. Đó là ý nghĩa của `SPRT.guarantee == "exact"`. Để có tỷ lệ sai lầm
được tính chính xác thay vì chỉ bị chặn trên, hãy dùng
`operating_characteristic` trên một kế hoạch (xem dưới đây).

## Khi bạn cần cỡ mẫu tối đa

* `TwoSPRT` (2-SPRT của Lorden) dừng trước một giới hạn (horizon) cố định và
  gần như cực tiểu hóa cỡ mẫu kỳ vọng trong trường hợp xấu nhất.
* `kiefer_weiss_plan(theta0, theta1, alpha0, alpha1, horizon, family=...)`
  trong `sequential_analysis.design` tính kế hoạch tối ưu với cỡ mẫu tối đa
  bằng quy nạp lùi (backward induction). `PlanTest` thực thi kế hoạch đó, và
  `operating_characteristic` cho tỷ lệ sai lầm chính xác cùng cỡ mẫu kỳ vọng
  mà không cần mô phỏng. Xem `examples/07_design_kiefer_weiss.py`.
* Để xem tại một vài thời điểm đã lên kế hoạch thay vì sau mỗi quan sát, hãy
  dùng [thiết kế tuần tự theo nhóm](clinical-trials.md).

## Khi SPRT là công cụ không phù hợp

* **Các giả thuyết không phải giả thuyết đơn.** "Tỷ lệ là 10%" đối với "tỷ lệ
  là bất kỳ giá trị nào khác" là một đối thuyết phức hợp (composite
  alternative). Hãy dùng SPRT hỗn hợp (`NormalMixtureSPRT`, `TMixtureSPRT`) hoặc
  kiểm định bằng đặt cược (`BettingMeanTest`), vốn hợp lệ tại mọi thời điểm đối
  với mọi đối thuyết.
* **Giá trị thật nằm giữa θ₀ và θ₁.** Khi đó SPRT chậm nhất, và cỡ mẫu kỳ vọng
  của nó có thể vượt quá cỡ mẫu cố định. Kế hoạch Kiefer–Weiss được xây dựng
  chính cho trường hợp này.

Các họ phân phối có sẵn cho thủ tục tỷ số hợp lý: `Gaussian` (phương sai đã
biết), `Bernoulli`, `Poisson`, `Exponential`.
