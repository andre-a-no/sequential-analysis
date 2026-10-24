---
description: Bảng thuật ngữ phân tích tuần tự và suy luận hợp lệ tại mọi thời điểm - giá trị e, quá trình e, dãy tin cậy, giá trị p luôn hợp lệ, mSPRT, chi tiêu alpha, tỷ lệ thông tin, ARL, SRM, CUPED, e-BH - kèm từ đồng nghĩa và các thủ tục sequential-analysis cài đặt từng khái niệm.
language: vi
---

# Bảng thuật ngữ

> Đây là bản dịch của [trang tiếng Anh](../../guide/glossary.md). Bản dịch chưa được người bản ngữ rà soát; nếu hai bản có chỗ khác nhau, trang tiếng Anh là bản có giá trị.

Các thuật ngữ dùng trong phân tích tuần tự và trong thư viện này. Các từ đồng
nghĩa thông dụng được ghi trong ngoặc.

**Phân tích tuần tự** (sequential analysis; sequential testing, sequential
inference). Thống kê trong đó số quan sát không được ấn định từ trước. Sau mỗi
quan sát hoặc nhóm quan sát, thủ tục quyết định dừng hay tiếp tục. Do Wald
(1945) khai sinh.

**Nhìn trộm** (peeking; optional stopping, data peeking, continuous
monitoring). Xem đi xem lại một kiểm định cỡ mẫu cố định và dừng khi nó có ý
nghĩa. Việc này làm tăng tỷ lệ dương tính giả; xem [nhìn trộm](peeking.md).

**SPRT** (sequential probability ratio test, kiểm định tỷ số xác suất tuần tự,
kiểm định Wald). Tích lũy logarit tỷ số hợp lý của hai giả thuyết đơn và dừng
khi nó ra khỏi một khoảng. `SPRT`; các phiên bản cắt cụt `TwoSPRT` (2-SPRT của
Lorden) và `kiefer_weiss_plan`. Xem [SPRT](sprt.md).

**Thiết kế tuần tự theo nhóm** (group sequential design; interim analyses,
group sequential trial). Một vài lần phân tích đã lên kế hoạch, mỗi lần có một
ngưỡng. Các ngưỡng được chọn sao cho sai lầm loại I tổng thể bằng alpha.
`group_sequential_design`. Xem [thử nghiệm lâm sàng](clinical-trials.md).

**Hàm chi tiêu alpha** (alpha spending function; error spending, Lan–DeMets).
Cho biết bao nhiêu phần sai lầm loại I có thể được dùng hết tính đến mỗi tỷ lệ
thông tin. Chi tiêu kiểu O'Brien–Fleming tiêu ít ở giai đoạn đầu, chi tiêu kiểu
Pocock tiêu đều. `spending="obrien-fleming"`, `"pocock"`, ...

**Tỷ lệ thông tin** (information fraction). Phần thông tin thống kê đã lên kế
hoạch (bệnh nhân, biến cố) đạt được tại một lần phân tích.

**Ngưỡng vô ích** (futility boundary; non-binding futility). Một ngưỡng dưới:
dưới nó, khuyến nghị dừng vì thiếu hiệu quả. Một ngưỡng không ràng buộc
(non-binding) có thể bị bỏ qua mà không làm tăng sai lầm loại I.

**Suy luận hợp lệ tại mọi thời điểm** (anytime-valid inference; always-valid
inference, safe anytime-valid inference, SAVI). Các kiểm định và khoảng có bảo
đảm đúng đồng thời ở mọi cỡ mẫu, nên có thể giám sát liên tục và dừng vì bất kỳ
lý do nào.

**Giá trị e** (e-value; e-variable, betting score). Một thống kê không âm có
kỳ vọng dưới giả thuyết không tối đa là 1. Giá trị e lớn là bằng chứng chống lại
giả thuyết không: bác bỏ khi nó vượt quá 1/alpha có sai lầm loại I tối đa là
alpha. Đầu ra `log_e_value` của nhiều thủ tục.

**Quá trình e** (e-process; test martingale, test supermartingale, wealth
process). Một dãy giá trị e vẫn hợp lệ tại các thời điểm dừng. Cực đại lũy
tiến của nó vượt 1/alpha với xác suất tối đa alpha dưới giả thuyết không (bất
đẳng thức Ville).

**Giá trị p luôn hợp lệ** (always-valid p-value; anytime-valid p-value,
sequential p-value). Một giá trị p hợp lệ tại mọi thời điểm dừng. Nó là nghịch
đảo của cực đại lũy tiến của một quá trình e. Đầu ra `p_value` của các thủ tục
hợp lệ tại mọi thời điểm.

**Dãy tin cậy** (confidence sequence; anytime-valid confidence interval,
always-valid confidence interval, time-uniform confidence interval). Một dãy
các khoảng chứa giá trị thật đồng thời ở mọi cỡ mẫu với xác suất ít nhất
1 − alpha. `BettingConfidenceSequence`, `QuantileConfidenceSequence`,
`CatoniConfidenceSequence`, `AsymptoticConfidenceSequence`, và các đầu ra
`lower` và `upper` của nhiều kiểm định. Xem
[dãy tin cậy](confidence-sequences.md).

**mSPRT** (mixture SPRT, SPRT hỗn hợp, Robbins' mixture). Một SPRT có đối
thuyết được lấy trung bình theo một phân phối tiên nghiệm, nhờ đó nó hợp lệ tại
mọi thời điểm đối với mọi đối thuyết. `NormalMixtureSPRT` (phương sai đã biết),
`TMixtureSPRT` (phương sai chưa biết).

**Kiểm định bằng đặt cược** (testing by betting). Xây dựng quá trình e như tài
sản của một người chơi đặt cược chống lại giả thuyết không. `BettingMeanTest`,
`BettingConfidenceSequence`, `KernelTwoSampleTest`.

**GROW** (growth-rate optimal, tối ưu tốc độ tăng trưởng). Một giá trị e được
chọn để cực đại hóa tăng trưởng logarit kỳ vọng của bằng chứng dưới đối thuyết.
`TwoProportionTest(method="grow")`.

**Suy luận phổ quát** (universal inference). Một giá trị e từ tỷ số hợp lý với
đối thuyết chỉ được ước lượng từ dữ liệu quá khứ. Nó vẫn hợp lệ dưới các thiết
kế thích ứng. `TwoProportionTest(method="universal")`.

**e-BH** (e-Benjamini–Hochberg). Kiểm soát tỷ lệ phát hiện sai (false
discovery rate) trên nhiều giá trị e, dưới mọi cấu trúc phụ thuộc.
`MultipleTests`, `e_bh`.

**e-LOND, FDR trực tuyến** (online FDR). Kiểm soát tỷ lệ phát hiện sai trên
một chuỗi giả thuyết được quyết định lần lượt từng cái một. `OnlineFDR`.

**SRM** (sample ratio mismatch, lệch tỷ lệ mẫu). Tỷ lệ chia lưu lượng quan sát
được giữa các nhánh khác với cấu hình, một dấu hiệu của lỗi trong thí nghiệm.
`SampleRatioMismatch`.

**CUPED** (controlled experiments using pre-experiment data; covariate
adjustment, regression adjustment, hiệu chỉnh theo biến đồng hành, hiệu chỉnh
hồi quy). Giảm phương sai của hiệu ứng A/B bằng một biến đồng hành được đo
trước thí nghiệm. `ABTest(covariate=True)`, `AnytimeLinearModel`.

**Chỉ số dạng tỷ số** (ratio metric; delta method, phương pháp delta). Một chỉ
số là tỷ số của hai tổng theo người dùng, chẳng hạn doanh thu mỗi phiên.
`RatioABTest`.

**Phát hiện điểm thay đổi** (change-point detection; change detection,
quickest detection, online anomaly detection). Phát báo động ngay sau khi phân
phối của một luồng dữ liệu thay đổi. `CUSUM`, `ShiryaevRoberts`,
`MeanEDetector`, `QuantileEDetector`, `BayesianChangePoint`. Xem
[phát hiện thay đổi](change-detection.md).

**ARL** (average run length, độ dài chạy trung bình; ARL₀, mean time to false
alarm). Số quan sát kỳ vọng cho tới một báo động giả khi chưa có gì thay đổi.
Cách kiểm soát báo động giả của các bộ phát hiện thay đổi.

**Bộ phát hiện e** (e-detector). Một bộ phát hiện thay đổi được xây dựng từ
các quá trình e, mỗi quá trình bắt đầu tại một thời điểm thay đổi khả dĩ. ARL
của nó được bảo đảm dưới một giả thuyết không phi tham số. `MeanEDetector`,
`QuantileEDetector`.

**Bài toán Kiefer–Weiss** (Kiefer–Weiss problem). Tìm kiểm định tuần tự có cỡ
mẫu tối đa sao cho cực tiểu hóa cỡ mẫu kỳ vọng lớn nhất. `kiefer_weiss_plan`.

**Đặc trưng vận hành** (operating characteristic). Các xác suất sai lầm và
phân phối của cỡ mẫu của một kế hoạch, dưới dạng hàm của tham số thật.
`operating_characteristic`.

**Điểm kiểm tra** (checkpoint). Một giá trị JSON mà từ đó một lượt chạy tiếp
tục chính xác. `Run.checkpoint`, `Run.restore`. Xem [luồng dữ liệu](streaming.md).

**Mã băm lịch sử** (history digest). Một chuỗi băm SHA-256 trên các quan sát mà
một lượt chạy đã dùng, được lưu trong mọi điểm kiểm tra, phục vụ kiểm toán.

**Bảo đảm** (guarantee; `exact`, `asymptotic`, `model`, `approximate`, `none`).
Thuộc tính mà qua đó mọi thủ tục trong thư viện này nêu rõ điều nó hứa. Xem
[Phương pháp nào?](../../choosing.md).
