---
description: Cách phát hiện thay đổi trong một luồng số đọc cảm biến, độ trễ hay chỉ số bằng Python, với CUSUM, Shiryaev–Roberts, bộ phát hiện e phi tham số và phát hiện điểm thay đổi trực tuyến Bayes. Báo động giả được kiểm soát qua độ dài chạy trung bình (ARL), với sequential-analysis.
language: vi
---

# Làm sao phát hiện thay đổi trong một luồng phép đo?

> Đây là bản dịch của [trang tiếng Anh](../../guide/change-detection.md). Bản dịch chưa được người bản ngữ rà soát; nếu hai bản có chỗ khác nhau, trang tiếng Anh là bản có giá trị.

**Trả lời ngắn.** Hãy dùng một bộ phát hiện điểm thay đổi trực tuyến (online
change-point detector). Nó theo dõi luồng dữ liệu và phát báo động ngay khi
phân phối có vẻ đã thay đổi. Báo động giả (false alarm) của nó được kiểm soát
bằng **độ dài chạy trung bình** (average run length, ARL): số quan sát kỳ vọng
cho tới một báo động giả khi chưa có gì thay đổi. Trong sequential-analysis:

| Điều bạn biết trước khi thay đổi | Thủ tục | Bảo đảm |
|---|---|---|
| cả hai phân phối (ví dụ phân phối chuẩn, trung bình 70 → 71) | `CUSUM`, `ShiryaevRoberts` | exact: ARL ≥ e^threshold |
| chỉ trung bình, và các cận của giá trị | `MeanEDetector` | exact với mọi phân phối như vậy |
| chỉ một phân vị (ví dụ phân vị thứ 95 của độ trễ) | `QuantileEDetector` | exact với mọi phân phối |
| một mô hình có tham số chưa biết, trước và sau | `BayesianChangePoint` | dưới mô hình và phân phối tiên nghiệm |

## Một cảm biến có trung bình bị dịch chuyển

Một cảm biến nhiệt độ đọc 70,0 °C với nhiễu có độ lệch chuẩn 0,5. Từ số đọc
thứ 600 trở đi, trung bình là 70,4. CUSUM với ngưỡng log(1000) ≈ 6,9 có ARL ít
nhất 1.000 số đọc:

```python
import math
import random

from sequential_analysis.procedures import CUSUM, Gaussian

rnd = random.Random(1)
readings = [rnd.gauss(70.0, 0.5) for _ in range(600)] + [rnd.gauss(70.4, 0.5) for _ in range(400)]

detector = CUSUM(Gaussian(sigma=0.5), theta0=70.0, theta1=70.4, threshold=math.log(1000))
state = detector.initial_state()
for t, x in enumerate(readings, start=1):
    state, out = detector.step(state, {"x": x})
    if out.alarm:
        print(f"alarm at reading {t}, {t - 600} readings after the shift")
        break
```

```text
alarm at reading 615, 15 readings after the shift
```

Một dịch chuyển nhỏ hơn một độ lệch chuẩn là không thể thấy bằng mắt ở bất kỳ
số đọc đơn lẻ nào. CUSUM tích lũy bằng chứng và tìm ra nó.

## Khi các số đọc không có phân phối chuẩn

ARL của CUSUM chỉ đúng nếu các số đọc tuân theo các phân phối bạn đã cung cấp
cho nó. Với dữ liệu lệch (biên độ rung, độ trễ, độ dài hàng đợi), nó phát báo
động giả thường xuyên hơn nhiều so với kế hoạch. Các bộ phát hiện e (e-detector)
cần ít hơn nhiều:

* `MeanEDetector` cần trung bình trước khi thay đổi và các cận của giá trị.
* `QuantileEDetector` chỉ cần một phân vị trước khi thay đổi.

ARL của chúng ít nhất bằng mục tiêu với **mọi** phân phối có trung bình hoặc
phân vị đó:

```python
from sequential_analysis.procedures import QuantileEDetector

rnd = random.Random(2)
vibration = [rnd.lognormvariate(0.0, 0.8) for _ in range(800)] + [rnd.lognormvariate(0.5, 0.8) for _ in range(400)]
q95 = math.exp(0.8 * 1.6449)          # the 95th percentile before the change
p95 = QuantileEDetector(q0=q95, p=0.95, arl=1000, direction="increase", statistic="cusum")
state = p95.initial_state()
for t, x in enumerate(vibration, start=1):
    state, out = p95.step(state, {"x": x})
    if out.alarm:
        print(f"the 95th percentile rose: alarm at reading {t}, {t - 800} readings after the change")
        break
```

```text
the 95th percentile rose: alarm at reading 887, 87 readings after the change
```

Trong thực tế, phân vị trước khi thay đổi được ước lượng từ một giai đoạn ổn
định. Khi đó bảo đảm chỉ đúng xấp xỉ, và càng tốt khi giai đoạn đó càng dài.

## Chọn ARL

ARL đánh đổi giữa báo động giả và độ trễ phát hiện. Với một số đọc mỗi phút,
ARL 1.000 số đọc nghĩa là cứ khoảng 17 giờ vận hành bình thường lại có một báo
động giả, cho mỗi cảm biến. Với 50 cảm biến, con số đó là khoảng 70 lần một
ngày. Hãy chọn ARL theo số báo động giả mỗi ngày mà bạn có thể chấp nhận trên
toàn bộ các cảm biến cộng lại: ở đây, ARL 1.000.000 số đọc giảm 50 cảm biến
xuống còn khoảng một báo động giả mỗi hai tuần. Điều đó tốn ít hơn bạn tưởng,
vì độ trễ phát hiện chỉ tăng theo logarit của ARL. Với CUSUM, ngưỡng tăng từ
6,9 lên 13,8, và độ trễ tăng khoảng gấp đôi.

Các bộ phát hiện này là công cụ giám sát, không phải hệ thống an toàn. Đừng
dùng chúng thay cho một hệ thống an toàn có thiết bị đo lường (safety
instrumented system) đã được chứng nhận.

Thêm: [bài hướng dẫn: giám sát quy trình và phát hiện thay đổi](../../tutorials/monitoring.md),
[các chế độ với mô hình Markov ẩn](../../tutorials/regimes.md),
[tài liệu tham chiếu: phát hiện thay đổi](../../reference/detection.md).
