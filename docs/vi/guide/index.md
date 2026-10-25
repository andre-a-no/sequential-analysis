---
description: Hướng dẫn sử dụng sequential-analysis, thư viện Python cho kiểm định tuần tự và suy luận hợp lệ tại mọi thời điểm (anytime-valid inference). Mỗi trang trả lời trực tiếp một câu hỏi, kèm mã chạy được và kết quả của nó.
language: vi
---

# Hướng dẫn sử dụng

> Đây là bản dịch của [trang tiếng Anh](../../guide/index.md). Bản dịch chưa được người bản ngữ rà soát; nếu hai bản có chỗ khác nhau, trang tiếng Anh là bản có giá trị.

Hướng dẫn này được sắp xếp theo những câu hỏi mà người dùng hay đặt ra. Mỗi
trang mở đầu bằng câu trả lời trực tiếp, sau đó đưa ra một chương trình ngắn
chạy được đúng như viết, kết quả của nó, bảo đảm (guarantee) đứng sau câu trả
lời, và những trường hợp phương pháp không áp dụng được. Các
[bài hướng dẫn chi tiết](../../tutorials/ab-test.md) đi sâu hơn vào từng chủ đề.

## Thư viện trong một đoạn

**sequential-analysis** là một thư viện Python cho suy luận thống kê trên dữ
liệu đến lần lượt từng quan sát một. Các kiểm định, khoảng tin cậy và bộ phát
hiện của nó có thể được xem sau mỗi quan sát và dừng lại vào bất kỳ lúc nào, mà
tỷ lệ sai lầm vẫn được giữ nguyên. Thư viện bao gồm:

* kiểm định tỷ số xác suất tuần tự (SPRT) của Wald và các kế hoạch tuần tự tối ưu;
* thiết kế tuần tự theo nhóm (group sequential design) cho thử nghiệm lâm sàng
  (hàm chi tiêu O'Brien–Fleming và Pocock, ngưỡng vô ích);
* kiểm định A/B hợp lệ tại mọi thời điểm với giá trị e (e-value) và dãy tin
  cậy (confidence sequence);
* phát hiện điểm thay đổi (change-point detection);
* bộ lọc Kalman, bộ lọc hạt và bộ lọc Markov ẩn;
* dự báo và biến động GARCH.

Mọi lượt chạy đều có thể lưu điểm kiểm tra (checkpoint) dưới dạng JSON và tiếp
tục lại chính xác đến từng bit trong Python, hoặc chạy tiếp trong bộ thực thi
TypeScript với cùng các quyết định.

| | |
|---|---|
| Cài đặt | `pip install sequential-analysis` |
| Import | `import sequential_analysis` |
| Python | 3.8 đến 3.14, không có phụ thuộc bắt buộc (numpy tùy chọn) |
| Giấy phép | AGPL-3.0, hoặc giấy phép thương mại từ Novikov Laboratories LLC |
| Mã nguồn | <https://github.com/andre-a-no/sequential-analysis> |
| Tài liệu | <https://andre-a-no.github.io/sequential-analysis/> |

## Câu hỏi

**Khái niệm**

* [Vì sao tôi không thể xem giá trị p mỗi ngày?](peeking.md) Việc nhìn trộm
  (peeking) và ba họ phương pháp tuần tự.
* [Bảng thuật ngữ](glossary.md): giá trị e, dãy tin cậy, chi tiêu alpha
  (alpha spending), ARL và các thuật ngữ khác, kèm từ đồng nghĩa.

**Tác vụ**

* [Làm sao dừng sớm một kiểm định A/B mà không làm tăng dương tính giả?](ab-testing.md)
* [Làm sao có khoảng tin cậy vẫn hợp lệ khi tôi xem đi xem lại?](confidence-sequences.md)
* [Làm sao chạy SPRT của Wald trong Python?](sprt.md)
* [Làm sao lập kế hoạch phân tích giữa kỳ cho thử nghiệm lâm sàng?](clinical-trials.md)
* [Làm sao phát hiện thay đổi trong một luồng phép đo?](change-detection.md)
* [Làm sao chạy thống kê trên luồng dữ liệu và tiếp tục sau sự cố?](streaming.md)

**Lựa chọn**

* [Phương pháp nào cho câu hỏi của tôi?](../../choosing.md): bảng đầy đủ.
* [So với các thư viện khác thì thế nào?](comparison.md)
* [Câu hỏi thường gặp](faq.md)

## Cách đọc các bảo đảm

Mọi thủ tục đều có thuộc tính `guarantee`. Hướng dẫn trích dẫn nó cùng với mỗi
câu trả lời:

* **exact:** tỷ lệ sai lầm được giữ ở mọi cỡ mẫu dưới các giả định đã nêu.
* **asymptotic:** được giữ xấp xỉ, và tốt hơn với mẫu lớn hơn.
* **model:** các xác suất là chính xác dưới mô hình đã nêu, nhưng không khẳng
  định gì ngoài mô hình đó.
* **approximate:** là xấp xỉ ngay cả dưới mô hình.
* **none:** thủ tục chỉ biến đổi dữ liệu và không khẳng định điều gì.
