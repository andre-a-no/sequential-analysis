---
description: Cách chạy thống kê tuần tự trên luồng dữ liệu (Kafka, SQL, pandas, cảm biến) và tiếp tục chính xác từ chỗ đã dừng sau sự cố. Điểm kiểm tra JSON, truyền nhận có loại bỏ trùng lặp, mã băm lịch sử để kiểm toán, và cùng một lượt chạy được tiếp tục trong Python hoặc TypeScript, với sequential-analysis.
language: vi
---

# Làm sao chạy thống kê trên luồng dữ liệu và tiếp tục sau sự cố?

> Đây là bản dịch của [trang tiếng Anh](../../guide/streaming.md). Bản dịch chưa được người bản ngữ rà soát; nếu hai bản có chỗ khác nhau, trang tiếng Anh là bản có giá trị.

**Trả lời ngắn.** Bọc thủ tục trong một `Run`. Sau đó:

1. Đưa quan sát vào bằng `run_sync` (hoặc `run_async` khi có nhiều nguồn sinh
   dữ liệu đồng thời).
2. Lưu `run.checkpoint()` thường xuyên tùy ý. Đó là một giá trị JSON thuần
   chứa trạng thái, trạng thái ngẫu nhiên, vị trí trong các nguồn và một mã băm
   SHA-256 của lịch sử.
3. Sau sự cố, `Run.restore(procedure, checkpoint)` tiếp tục chính xác, đến
   từng bit. Với `Delivery("sequence")`, các quan sát được gửi lại sau khi khởi
   động lại sẽ bị loại bỏ như bản trùng lặp.
4. Bộ thực thi TypeScript có thể tiếp tục cùng điểm kiểm tra đó trong
   JavaScript. Nó cho cùng các quyết định và cùng mã băm lịch sử, và các con số
   khớp đến những bit cuối cùng: giống hệt nhau ở 34 trên 108 trường hợp kiểm
   tra tuân thủ (conformance), và sai khác tương đối trong phạm vi 6·10⁻¹³ ở
   các trường hợp còn lại.

## Sự cố, khởi động lại, phát lại: cùng một kết quả

Một lượt chạy giám sát trên 300 số đọc bị gián đoạn sau 120 số đọc. Nguồn được
phát lại từ số đọc thứ 100, như một hàng đợi thông điệp thường làm sau khi khởi
động lại. Lượt chạy được khôi phục loại bỏ 20 số đọc nó đã thấy và kết thúc
đúng tại nơi một lượt chạy không bị gián đoạn sẽ kết thúc:

```python
import json
import random

from sequential_analysis import Delivery, Observation, Run, run_sync
from sequential_analysis.procedures import BettingConfidenceSequence

rnd = random.Random(5)
readings = [Observation("x", rnd.betavariate(2, 5), seq=i, source="sensor-7") for i in range(300)]

def procedure():
    return BettingConfidenceSequence(lower=0.0, upper=1.0, grid=200)

run = Run(procedure(), delivery=Delivery("sequence"), run_id="sensor-7")
run_sync(run, readings[:120])
saved = json.dumps(run.checkpoint())        # to a file, a database, object storage
del run                                     # the process dies

run = Run.restore(procedure(), json.loads(saved), delivery=Delivery("sequence"))
run_sync(run, readings[100:])               # the source replays from reading 100
print(f"resumed run: {run.t} readings, {run.delivery.duplicates} duplicates dropped")

uninterrupted = Run(procedure(), delivery=Delivery("sequence"), run_id="sensor-7")
run_sync(uninterrupted, readings)
print("same state as an uninterrupted run:", run.state == uninterrupted.state)
print("same history digest:", run.checkpoint()["history_digest"] == uninterrupted.checkpoint()["history_digest"])
print(f"checkpoint size: {len(saved)} bytes")
```

```text
resumed run: 300 readings, 20 duplicates dropped
same state as an uninterrupted run: True
same history digest: True
checkpoint size: 9606 bytes
```

Mã băm lịch sử (history digest) là một chuỗi băm trên mọi quan sát mà lượt
chạy đã dùng. Hai lượt chạy có cùng mã băm đã thấy cùng dữ liệu theo cùng thứ
tự. Kiểm toán viên có thể tính lại nó từ nhật ký quan sát, theo
[đặc tả](../../spec.md).

## Các quan sát đến từ đâu

| Nguồn | Hàm |
|---|---|
| một danh sách hoặc generator các giá trị | `sources.from_values` |
| một tệp CSV | `sources.from_csv` |
| một DataFrame pandas hoặc polars | `adapters.from_dataframe` |
| một truy vấn SQL (mọi kết nối DB-API) | `adapters.from_sql` |
| thông điệp Kafka, với offset đã commit | `adapters.from_kafka`, `adapters.kafka_offsets` |
| nhiều nguồn cùng lúc | `sources.interleave`, `sources.merge_ordered` |
| một nhật ký quan sát đã ghi | `sources.replay` |

Đầu vào từ các nguồn khác nhau được liên kết bằng một **cấu trúc liên kết** (topology).
`KeyJoin` ghép phân nhóm và kết quả theo người dùng, `TimeAlign` căn chỉnh hai
cảm biến theo thời gian, và `AsOfJoin` gắn các sự kiện vào những thanh (bar)
đã biết về chúng. Xem [nguồn dữ liệu](../../adapters.md).

## Khi thủ tục thay đổi

Một điểm kiểm tra ghi lại tên, phiên bản và cấu hình của thủ tục. `Run.restore`
từ chối điểm kiểm tra được tạo bởi một thủ tục khác, một cấu hình khác hoặc
một phiên bản có số học khác, và phát sinh `IncompatibleCheckpoint`. Vì vậy, một
lượt chạy không bao giờ âm thầm được tiếp tục với những con số khác.

Thêm: [điểm kiểm tra, nhật ký và backend](../../checkpoints.md),
[bộ thực thi TypeScript](../../typescript.md),
[đặc tả các định dạng](../../spec.md).
