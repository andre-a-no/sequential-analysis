---
description: Câu hỏi thường gặp về sequential-analysis, thư viện Python cho kiểm định tuần tự và suy luận hợp lệ tại mọi thời điểm - cài đặt, giấy phép và sử dụng thương mại, kiểm định A/B trong môi trường production, thử nghiệm lâm sàng, lực kiểm định, tốc độ, TypeScript, trích dẫn.
language: vi
---

# Câu hỏi thường gặp

> Đây là bản dịch của [trang tiếng Anh](../../guide/faq.md). Bản dịch chưa được người bản ngữ rà soát; nếu hai bản có chỗ khác nhau, trang tiếng Anh là bản có giá trị.

## Về thư viện

### sequential-analysis là gì?

Một thư viện Python cho suy luận thống kê tuần tự. Các kiểm định, dãy tin cậy
(confidence sequence) và bộ phát hiện của nó có thể được kiểm tra sau mỗi quan
sát và dừng vào bất kỳ lúc nào mà không mất các bảo đảm về sai lầm. Thư viện
gồm:

* SPRT;
* thiết kế tuần tự theo nhóm (group sequential design);
* kiểm định A/B hợp lệ tại mọi thời điểm (anytime-valid);
* bộ phát hiện điểm thay đổi;
* bộ lọc Kalman, bộ lọc hạt và bộ lọc Markov ẩn;
* dự báo và GARCH.

Tất cả đều chạy sau một giao diện duy nhất với điểm kiểm tra (checkpoint) JSON.
Thư viện được phát triển bởi Novikov Laboratories LLC.

### Cài đặt thế nào? Nó phụ thuộc vào những gì?

`pip install sequential-analysis`. Nó cần Python 3.8 trở lên (đã kiểm thử đến
3.14) và không cần gì khác. `pip install "sequential-analysis[fast]"` bổ sung
numpy cho các thủ tục làm việc trên mảng. pandas, polars, các client Kafka và
matplotlib chỉ được dùng nếu bạn gọi các adapter hoặc các hàm vẽ đồ thị.

### Có miễn phí cho mục đích thương mại không?

Thư viện được cấp phép kép theo AGPL-3.0 và một giấy phép thương mại. Các
trường hợp sử dụng sau là miễn phí theo AGPL:

* nghiên cứu và giảng dạy;
* các dự án mã nguồn mở theo AGPL hoặc GPL v3;
* sử dụng nội bộ trong một tổ chức, không trao bản sao cho người khác và không
  cho người ngoài tổ chức truy cập qua mạng.

Một sản phẩm mã nguồn đóng, hoặc một dịch vụ mạng mà bạn không công bố mã
nguồn, cần giấy phép thương mại. Bảng trong
[COMMERCIAL.md](https://github.com/andre-a-no/sequential-analysis/blob/main/COMMERCIAL.md)
quyết định các trường hợp cụ thể. Liên hệ về giấy phép: andrei@hobukob.ru.

### Trích dẫn thế nào?

Tệp [CITATION.cff](https://github.com/andre-a-no/sequential-analysis/blob/main/CITATION.cff)
trong kho mã cung cấp trích dẫn, và nút *Cite this repository* của GitHub
chuyển nó thành BibTeX hoặc APA. Các bản phát hành được lưu trữ trên Zenodo
với DOI. Các phương pháp và việc kiểm chứng chúng được mô tả trong
[bài báo](https://github.com/andre-a-no/sequential-analysis/blob/main/paper/main.pdf).

## Sử dụng

### Tôi có thể dùng nó cho kiểm định A/B trong môi trường production không?

Có, với vai trò engine thống kê. Nó cung cấp các kiểm định chính xác (exact)
cho:

* tỷ lệ chuyển đổi (`TwoProportionTest`);
* chỉ số bị chặn (`BoundedABTest`);
* tần suất (`RateRatioTest`);
* việc chia lưu lượng (`SampleRatioMismatch`);
* nhiều chỉ số với kiểm soát tỷ lệ phát hiện sai (false discovery rate) (`MultipleTests`).

Trong Python thuần, kiểm định chuyển đổi mất khoảng 10 micro giây cho mỗi người
dùng, kiểm tra việc chia lưu lượng 4 và kiểm định tần suất 40. Điểm kiểm tra
của mỗi thủ tục chiếm 2–4 kilobyte.
`BoundedABTest` duy trì một lưới và mất 0,1–0,5 ms.

Thư viện này không phải là một nền tảng thử nghiệm: việc phân nhóm, thu thập
sự kiện và bảng điều khiển là phần bạn tự xây dựng hoặc lấy từ một nền tảng.
Xem [kiểm định A/B](ab-testing.md).

### Tôi có thể xem trộm kết quả mỗi ngày không?

Có, với các thủ tục hợp lệ tại mọi thời điểm: chúng được tạo ra chính là để
làm điều đó. Với thiết kế tuần tự theo nhóm, chỉ xem tại các lần phân tích đã
lên kế hoạch. Với kiểm định cỡ mẫu cố định cổ điển, chỉ xem một lần. Xem
[nhìn trộm](peeking.md).

### Kiểm định hợp lệ tại mọi thời điểm có lực kiểm định thấp hơn kiểm định cỡ mẫu cố định không?

Tại mức hiệu ứng mà kiểm định cỡ mẫu cố định được lên kế hoạch, thì có. Để đạt
cùng lực kiểm định, một kiểm định hợp lệ tại mọi thời điểm cho hai tỷ lệ cần
1,3–1,6 lần số người dùng. Đổi lại, bạn có thể dừng sớm khi hiệu ứng lớn hơn,
và không cần ấn định cỡ mẫu từ trước. Một thiết kế tuần tự theo nhóm với vài
lần xem đã lên kế hoạch chỉ tốn thêm 1–20% so với một lần phân tích duy nhất.

### Tuần tự theo nhóm hay hợp lệ tại mọi thời điểm: tôi nên dùng cái nào?

* **Tuần tự theo nhóm** nếu số lần phân tích ít và được lên kế hoạch, như với
  một hội đồng giám sát dữ liệu hoặc một chu kỳ phát hành, và đặc biệt cho một
  thử nghiệm lâm sàng xác nhận.
* **Hợp lệ tại mọi thời điểm** nếu bạn muốn xem liên tục, hoặc không thể nói
  trước khi nào bạn sẽ xem hay dừng.

### Nó có làm kiểm định A/B theo Bayes không?

Các kiểm định A/B của nó theo trường phái tần suất, với bảo đảm về tỷ lệ sai
lầm. Các thành phần Bayes có sẵn ở những chỗ phù hợp:

* `ThompsonAllocation` phân bổ lưu lượng theo xác suất hậu nghiệm rằng mỗi nhánh
  là tốt nhất, với một quy tắc tổn thất kỳ vọng để triển khai;
* `BayesianChangePoint` phát hiện điểm thay đổi;
* các bộ dự báo học tham số của chúng bằng cập nhật Bayes.

### Nó có được thẩm định cho thử nghiệm lâm sàng không?

Các thiết kế tuần tự theo nhóm của nó (ngưỡng, lực kiểm định, cỡ mẫu, số biến
cố) được đối chiếu với rpact và gói survival của R trong bộ kiểm thử. Nó không
phải là phần mềm đã được thẩm định theo nghĩa quản lý dược. Nhà tài trợ dùng nó
cho hồ sơ nộp sẽ tự thẩm định nó như mọi công cụ khác. Xem
[thử nghiệm lâm sàng](clinical-trials.md).

### Chỉ số của tôi có đuôi nặng (doanh thu, độ trễ). Tôi nên dùng gì?

* Với một phân vị (trung vị, phân vị thứ 90), hãy dùng `QuantileTest` hoặc
  `QuantileConfidenceSequence`, vốn không cần giả định nào.
* Với trung bình, hãy giới hạn các giá trị ở một mức ấn định từ trước và dùng
  `BoundedABTest` hoặc `BettingConfidenceSequence` (exact).
* Hoặc, giả định một cận trên của độ lệch chuẩn và dùng
  `CatoniConfidenceSequence`.

Thư viện chưa có kiểm định hai mẫu cho trung vị.

### Nó nhanh đến đâu?

Các thủ tục đơn giản nhất mất 1–10 micro giây cho mỗi quan sát trong Python
thuần: SPRT, CUSUM, các kiểm định tuần tự theo nhóm và kiểm định hỗn hợp,
GARCH. Những thủ tục giữ một lưới hoặc toàn bộ mẫu mất 0,1–10 ms. Ví dụ là các
dãy tin cậy đặt cược và Catoni, kiểm định kernel và các bộ dự báo có học.
[Tốc độ](../../performance.md) liệt kê chi phí và kích thước điểm kiểm tra của
từng thủ tục.

### Tôi có thể chạy nó trong JavaScript hoặc trong trình duyệt không?

Có. Bộ thực thi TypeScript trong `ts/` chạy các thủ tục và tiếp tục các điểm
kiểm tra Python. Mã băm lịch sử và các quyết định là giống hệt nhau, và các con
số khớp đến những bit cuối cùng. Xem [bộ thực thi TypeScript](../../typescript.md).

### Một lượt chạy có thể sống sót qua sự cố không?

Có. `run.checkpoint()` là JSON thuần, và `Run.restore` tiếp tục chính xác đến
từng bit. Các quan sát được gửi lại sẽ bị loại bỏ. Xem
[luồng dữ liệu](streaming.md).

### "exact" và "asymptotic" trong tài liệu nghĩa là gì?

Thuộc tính `guarantee` của mọi thủ tục nêu rõ lời hứa của nó:

* `exact`: tỷ lệ sai lầm được giữ ở mọi cỡ mẫu dưới các giả định đã nêu;
* `asymptotic`: xấp xỉ, trong các lượt chạy dài;
* `model`: chính xác dưới mô hình đã nêu;
* `approximate`;
* `none`.

Tài liệu khuyến nghị thủ tục chính xác ở nơi có thủ tục phù hợp. Xem
[Phương pháp nào?](../../choosing.md).
