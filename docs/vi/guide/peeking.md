---
description: Vì sao việc kiểm tra giá trị p mỗi ngày làm tăng dương tính giả trong kiểm định A/B và thử nghiệm lâm sàng (vấn đề nhìn trộm, peeking problem), và ba họ phương pháp tuần tự khắc phục điều đó, bằng Python với sequential-analysis.
language: vi
---

# Vì sao tôi không thể xem giá trị p mỗi ngày?

> Đây là bản dịch của [trang tiếng Anh](../../guide/peeking.md). Bản dịch chưa được người bản ngữ rà soát; nếu hai bản có chỗ khác nhau, trang tiếng Anh là bản có giá trị.

**Trả lời ngắn.** Một kiểm định cỡ mẫu cố định (fixed-sample test) chỉ hứa tỷ
lệ dương tính giả (false-positive rate) 5% nếu bạn xem kết quả một lần, tại cỡ
mẫu đã lên kế hoạch. Nếu bạn xem nhiều lần và dừng ở lần đầu tiên p < 0,05, bạn
có nhiều cơ hội bị đánh lừa. Với 20 lần xem, tỷ lệ dương tính giả tăng lên
khoảng 25%. Các phương pháp tuần tự (sequential methods) được xây dựng để xem
nhiều lần. Với chúng, tỷ lệ này luôn ở mức 5% hoặc thấp hơn, dù bạn xem thường
xuyên đến đâu và dừng vào lúc nào.

## Đo lường vấn đề nhìn trộm

Hai nhánh có cùng tỷ lệ chuyển đổi 10% (một kiểm định A/A), 2.000 người dùng,
200 lần lặp. "Nhìn trộm" (peeking) chạy kiểm định z thông thường cho hai tỷ lệ
sau mỗi 100 người dùng và dừng ở lần đầu tiên p < 0,05. Kiểm định tuần tự
`TwoProportionTest` được kiểm tra sau từng người dùng một:

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

Một lần xem duy nhất giữ đúng lời hứa. Hai mươi lần xem nhân tỷ lệ sai lầm lên
khoảng sáu lần. Kiểm định tuần tự, được xem sau từng người trong 2.000 người
dùng, giữ nó ở 5%. Đó chính là lời hứa: bảo đảm của nó là **exact**
(`TwoProportionTest.guarantee == "exact"`), tức tỷ lệ dương tính giả tối đa 5%
ở mọi cỡ mẫu, dù bạn xem thường xuyên đến đâu. Với 200 lần lặp, 10 dương tính
giả đúng là con số mà mức 5% chính xác cho ra.

## Ba họ phương pháp tuần tự

| Họ | Bạn có thể xem | Ứng dụng điển hình | Trong sequential-analysis |
|---|---|---|---|
| **Kiểm định tỷ số xác suất tuần tự (sequential probability ratio test)** (Wald 1945) | sau mỗi quan sát | một giả thuyết đơn đối với một giả thuyết đơn khác, trung bình ít quan sát nhất: kiểm soát chất lượng, mô phỏng, tâm vật lý học | `SPRT`, `TwoSPRT`, `kiefer_weiss_plan` |
| **Thiết kế tuần tự theo nhóm (group sequential design)** (Pocock 1977, O'Brien and Fleming 1979, Lan and DeMets 1983) | tại một vài phân tích giữa kỳ đã lên kế hoạch | thử nghiệm lâm sàng có hội đồng giám sát dữ liệu | `group_sequential_design`, `GroupSequentialTest`, `GroupSequentialProportions`, `GroupSequentialLogRank` |
| **Suy luận hợp lệ tại mọi thời điểm (anytime-valid inference)**: giá trị e, dãy tin cậy, SPRT hỗn hợp (Robbins 1970, Howard et al. 2021, Ramdas et al. 2023) | sau mỗi quan sát, dừng vì bất kỳ lý do nào | kiểm định A/B trực tuyến, bảng điều khiển giám sát | `TwoProportionTest`, `BoundedABTest`, `NormalMixtureSPRT`, `BettingConfidenceSequence`, `MultipleTests` |

**Cái giá phải trả.** Xem thường xuyên hơn đòi hỏi nhiều dữ liệu hơn tại mức
hiệu ứng bạn đã lên kế hoạch:

* một thiết kế tuần tự theo nhóm với bốn lần phân tích cần nhiều hơn 1–20% số
  bệnh nhân so với một lần phân tích duy nhất;
* một kiểm định hợp lệ tại mọi thời điểm cho hai tỷ lệ cần 1,3–1,6 lần số người
  dùng của một lần phân tích duy nhất.

Đổi lại, một hiệu ứng lớn sẽ khiến thí nghiệm dừng sớm, và không ai phải ấn
định cỡ mẫu từ trước.

## Khi nào đây không phải là vấn đề

Việc nhìn trộm chỉ làm tăng sai lầm khi điều bạn làm phụ thuộc vào điều bạn đã
thấy. Nếu bạn xem bảng điều khiển nhưng luôn chạy thí nghiệm đến cỡ mẫu đã lên
kế hoạch và chỉ kiểm định một lần, thì kiểm định cỡ mẫu cố định là hợp lệ.
Trong trường hợp đó, nó cũng là lựa chọn hiệu quả nhất.

Tiếp theo: [dừng sớm một kiểm định A/B](ab-testing.md),
[dãy tin cậy](confidence-sequences.md),
[bảng thuật ngữ](glossary.md).
