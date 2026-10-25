---
description: So sánh sequential-analysis với các thư viện Python và R khác cho kiểm định tuần tự, kiểm định A/B, thiết kế tuần tự theo nhóm, phát hiện thay đổi và lọc (statsmodels, scipy, confseq, rpact, gsDesign, safestats, ruptures, filterpy, arch, hmmlearn), và khi nào nên dùng công cụ nào.
language: vi
---

# So với các thư viện khác thì thế nào?

> Đây là bản dịch của [trang tiếng Anh](../../guide/comparison.md). Bản dịch chưa được người bản ngữ rà soát; nếu hai bản có chỗ khác nhau, trang tiếng Anh là bản có giá trị.

**Trả lời ngắn.** Phần lớn các thư viện bao quát tốt một họ phương pháp.
sequential-analysis đặt các họ chính của suy luận tuần tự (sequential inference)
sau một giao diện duy nhất:

* SPRT và các kế hoạch tối ưu;
* thiết kế tuần tự theo nhóm (group sequential design);
* kiểm định hợp lệ tại mọi thời điểm (anytime-valid) và dãy tin cậy (confidence
  sequence);
* phát hiện thay đổi;
* bộ lọc không gian trạng thái.

Những gì nó bổ sung ngoài bản thân các phương pháp:

* mọi thủ tục đều nêu rõ bảo đảm của mình (`exact`, `asymptotic`, `model`,
  ...);
* mọi lượt chạy đều có thể lưu điểm kiểm tra và tiếp tục lại chính xác đến
  từng bit;
* các định dạng được đặc tả và được thực thi bởi một cài đặt thứ hai bằng
  TypeScript;
* không có phụ thuộc bắt buộc.

Nếu bạn chỉ cần một trong các phương pháp dưới đây và đã dùng thư viện chuyên
về nó, hãy tiếp tục dùng thư viện đó. Bảng cho biết mỗi công cụ là lựa chọn tự
nhiên ở đâu. Phần mô tả nói về mục đích chính của mỗi thư viện, tính đến tháng
10 năm 2026, và không phải là danh sách đầy đủ các tính năng của nó.

| Nhu cầu | Lựa chọn tự nhiên | sequential-analysis cung cấp gì |
|---|---|---|
| kiểm định cỡ mẫu cố định, hồi quy, lực kiểm định | scipy.stats, statsmodels | không phải mục đích của nó |
| thiết kế tuần tự theo nhóm cho hồ sơ nộp cơ quan quản lý | rpact, gsDesign (R) | cùng các thiết kế đó, được đối chiếu với rpact trong bộ kiểm thử; vận hành thử nghiệm từng bước với điểm kiểm tra |
| dãy tin cậy, giá trị e | confseq (Python), safestats (R) | dãy tin cậy cho trung bình, phân vị, hệ số hồi quy, hiệu ứng hai mẫu; e-BH và e-LOND cho nhiều kiểm định |
| kiểm định A/B dưới dạng nền tảng có giao diện | GrowthBook, Statsig, Eppo, Optimizely (nền tảng) | một engine để nhúng: kiểm định chính xác cho chuyển đổi, chỉ số bị chặn và chỉ số tần suất, SRM, FDR trên nhiều chỉ số |
| phân đoạn điểm thay đổi ngoại tuyến cho một chuỗi đã hoàn tất | ruptures (Python), changepoint (R) | phát hiện trực tuyến trong khi dữ liệu đang đến: CUSUM, Shiryaev–Roberts, bộ phát hiện e, điểm thay đổi trực tuyến Bayes |
| bộ lọc Kalman | filterpy, statsmodels state space | bộ lọc Kalman, Kalman bền vững, bộ lọc hạt và HMM, với làm trơn và điểm kiểm tra |
| GARCH | arch | GARCH(1,1) và GJR được khớp tới cùng điểm cực đại như arch (kiểm tra trong bộ kiểm thử), sau đó chạy trực tuyến |
| mô hình Markov ẩn | hmmlearn | bộ lọc trực tuyến, Baum–Welch khớp với hmmlearn, EM trực tuyến |
| dự báo | statsmodels, các thư viện khác | dự báo ETS và AR khớp với statsmodels, học trực tuyến, với khoảng conformal |

## Những trường hợp công cụ khác tốt hơn

* **Hồ sơ nộp cơ quan quản lý.** rpact được dùng rộng rãi cho mục đích đó, và
  các nhà phát triển của nó cung cấp tài liệu thẩm định. sequential-analysis
  khớp với rpact trên các thiết kế mà nó bao quát, nhưng nhà tài trợ vẫn phải
  tự thẩm định nó.
* **Phân tích ngoại tuyến quy mô lớn trên mảng.** Các thư viện dựa trên numpy
  nhanh hơn tính trên mỗi quan sát. sequential-analysis được xây dựng để xử lý
  từng quan sát một; xem [Tốc độ](../../performance.md) để biết chi phí của từng
  thủ tục.
* **Các phương pháp nó chưa có.** Nó chưa có kiểm định hai mẫu cho trung vị,
  chưa có quá trình Hawkes đa biến và chưa có mô hình ARIMA với các số hạng
  trung bình trượt. Xem [nhật ký thay đổi](../../changelog.md) để biết những gì
  được bổ sung.
