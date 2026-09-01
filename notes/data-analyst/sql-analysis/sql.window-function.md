---
id: data-analyst.sql.window-function
title: Window function
domain: data-analyst
type: mechanism
tags: [sql, sql-analysis, window, function]
status: draft
ai_summary: A window function computes over a set of rows related to the current row without collapsing them, so it adds a column while keeping the grain unchanged.
relationships:
  builds_on: [data-analyst.sql.grain]
  prerequisite_of: [data-analyst.sql.aggregation-grain-error]
  commonly_confused_with: [data-analyst.sql.cte-vs-subquery]
created: 2026-09-01
updated: 2026-09-01
version_sensitive: false
---

# Window function

**Tóm tắt bản chất:** Hàm cửa sổ tính toán trên một tập dòng liên quan tới dòng hiện tại mà **không gộp** chúng lại. Nó thêm một cột và giữ nguyên số dòng — đó là toàn bộ điểm khác biệt với `GROUP BY`, và cũng là lý do nó giải được lớp bài toán mà `GROUP BY` không chạm tới.

## Nỗi Đau & Động Lực

Câu hỏi nghe đơn giản: mỗi đơn hàng chiếm bao nhiêu phần trăm tổng chi tiêu của khách hàng đó. Với `GROUP BY` thì không viết được trong một truy vấn, vì bạn cần đồng thời hai grain — chi tiết từng đơn để hiển thị, và tổng theo khách để làm mẫu số. `GROUP BY` chỉ cho bạn một grain, và nó là grain thô.

Cách người ta xoay xở trước khi biết hàm cửa sổ: viết một truy vấn tổng hợp, viết một truy vấn chi tiết, rồi join hai cái lại. Ba lượt quét bảng thay vì một, một phép join có thể gây fan-out nếu khóa không duy nhất, và một truy vấn dài gấp ba mà người đọc phải giữ hai nhánh trong đầu cùng lúc.

Chi phí không dừng ở độ dài. Mỗi lần cấu trúc ấy được sao chép cho một câu hỏi tương tự — xếp hạng trong nhóm, so với dòng trước, tổng lũy kế — lại là một cơ hội để hai nhánh lệch nhau ở điều kiện lọc. Lỗi hay gặp nhất không phải sai công thức mà là `WHERE` của nhánh tổng hợp khác `WHERE` của nhánh chi tiết một chút.

## Cơ Chế Tác Động

Cú pháp đầy đủ có ba phần, và mỗi phần trả lời một câu hỏi khác nhau:

```sql
SUM(amount) OVER (
  PARTITION BY customer_id      -- chia dữ liệu thành các nhóm độc lập
  ORDER BY ordered_at           -- xác định thứ tự bên trong nhóm
  ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW   -- chọn dòng nào thuộc cửa sổ
)
```

`PARTITION BY` giống `GROUP BY` ở chỗ chia nhóm, khác ở chỗ không gộp. Bỏ nó đi thì cả bảng là một nhóm.

`ORDER BY` bên trong `OVER` **không** sắp xếp kết quả cuối; nó chỉ định nghĩa thứ tự để khung cửa sổ trượt theo. Đây là nguồn nhầm lẫn thường xuyên: một truy vấn có `ORDER BY` trong `OVER` mà không có `ORDER BY` ở ngoài vẫn trả về dòng theo thứ tự tùy ý.

Mệnh đề khung là phần bị bỏ qua nhiều nhất, và nó có một mặc định gây bất ngờ. Khi có `ORDER BY` mà không viết khung, mặc định là `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`. Chú ý `RANGE`, không phải `ROWS`: `RANGE` gộp mọi dòng **cùng giá trị sắp xếp** vào cùng một bậc. Hai giao dịch cùng ngày sẽ thấy tổng lũy kế bao gồm cả nhau, không phải chỉ dòng trước.

Thứ tự thực thi quyết định bạn được phép viết gì ở đâu:

```
FROM → WHERE → GROUP BY → HAVING → hàm cửa sổ → SELECT → ORDER BY → LIMIT
```

Hàm cửa sổ chạy **sau** `GROUP BY` và **trước** `SELECT`. Hai hệ quả cụ thể: bạn không thể lọc theo kết quả hàm cửa sổ trong `WHERE` (nó chưa tồn tại), và bạn **có thể** dùng hàm cửa sổ trên kết quả đã tổng hợp — `SUM(SUM(amount)) OVER (...)` là hợp lệ và không phải lỗi đánh máy.

## Bản Đồ Quyết Định

| Câu hỏi | Hàm | Bẫy |
|---|---|---|
| xếp hạng, đồng hạng chiếm chỗ | `RANK()` | 1,2,2,4 — mất số 3 |
| xếp hạng, đồng hạng không chiếm chỗ | `DENSE_RANK()` | 1,2,2,3 — hai người cùng hạng 2 |
| đúng một dòng mỗi nhóm | `ROW_NUMBER()` | đồng hạng bị phá vỡ tùy ý nếu `ORDER BY` không đủ chặt |
| so với dòng trước | `LAG(x)` | dòng đầu nhóm trả `NULL`, không phải 0 |
| tỉ trọng trong nhóm | `x / SUM(x) OVER (PARTITION BY ...)` | mẫu số có thể là 0 |
| tổng lũy kế | `SUM(x) OVER (ORDER BY ...)` | mặc định `RANGE` gộp dòng cùng giá trị |
| trung bình trượt 7 dòng | `AVG(x) OVER (ORDER BY ... ROWS 6 PRECEDING)` | `ROWS` đếm dòng, không đếm ngày |

Dòng cuối là chỗ dễ sai nhất trong thực tế. `ROWS 6 PRECEDING` lấy sáu **dòng** trước, không phải sáu **ngày** trước. Nếu dữ liệu thiếu ngày — cuối tuần không có giao dịch — thì "trung bình 7 ngày" thực ra trải qua chín hoặc mười ngày lịch. Muốn đúng theo thời gian phải dùng `RANGE BETWEEN INTERVAL '6 days' PRECEDING AND CURRENT ROW`, và không phải hệ nào cũng hỗ trợ.

Dòng thứ ba cũng cần cẩn thận: `ROW_NUMBER()` luôn trả về đúng một dòng số 1, kể cả khi có hai dòng ngang nhau hoàn toàn. Nó chọn một cách tùy ý, và "tùy ý" nghĩa là có thể khác nhau giữa hai lần chạy. Khi cần tính lặp lại được, `ORDER BY` phải chứa đủ cột để phá thế hòa một cách xác định.

## Case Study Thực Chiến: tìm đơn hàng đầu tiên của mỗi khách

Lược đồ tối thiểu:

```
orders (order_id, customer_id, ordered_at, gross_amount)
```

Cách viết cũ, hai lượt quét và một phép join:

```sql
SELECT o.*
FROM orders o
JOIN (SELECT customer_id, MIN(ordered_at) AS dau_tien
      FROM orders GROUP BY customer_id) f
  ON f.customer_id = o.customer_id AND f.dau_tien = o.ordered_at;
```

Truy vấn này có một lỗi nằm im: khách đặt hai đơn cùng một dấu thời gian sẽ khớp cả hai, và bạn nhận hai "đơn đầu tiên". Trên dữ liệu có độ chính xác đến giây thì hiếm; trên dữ liệu chỉ có ngày thì thường xuyên.

Với hàm cửa sổ, một lượt quét và không có phép join:

```sql
SELECT * FROM (
  SELECT o.*,
         ROW_NUMBER() OVER (PARTITION BY customer_id
                            ORDER BY ordered_at, order_id) AS thu_tu
  FROM orders o
) t
WHERE thu_tu = 1;
```

`order_id` trong `ORDER BY` là thứ phá thế hòa một cách xác định. Thiếu nó, hai đơn cùng dấu thời gian được chọn tùy ý và kết quả có thể đổi giữa các lần chạy.

Lớp bọc ngoài là bắt buộc, không phải để cho đẹp: hàm cửa sổ chạy sau `WHERE`, nên `WHERE thu_tu = 1` ở cùng tầng sẽ báo lỗi cột không tồn tại.

**Biến thể khó hơn, nơi cách hiểu trên gây hiểu lầm.** Đổi câu hỏi thành: mỗi đơn chiếm bao nhiêu phần trăm chi tiêu cả đời của khách đó.

```sql
SELECT order_id, customer_id, gross_amount,
       gross_amount * 100.0 / SUM(gross_amount) OVER (PARTITION BY customer_id) AS ti_trong
FROM orders
WHERE ordered_at >= '2026-01-01';
```

Con số này sai, và sai một cách khó thấy. `WHERE` chạy **trước** hàm cửa sổ, nên mẫu số chỉ là tổng chi tiêu **từ 2026** chứ không phải cả đời. Mỗi tỉ trọng đều bị thổi lên, và các tỉ trọng trong một khách vẫn cộng đủ 100% nên không có dấu hiệu nào bất thường.

Muốn mẫu số là cả đời thì phải tính cửa sổ trước rồi mới lọc:

```sql
SELECT * FROM (
  SELECT order_id, customer_id, ordered_at, gross_amount,
         gross_amount * 100.0 / SUM(gross_amount) OVER (PARTITION BY customer_id) AS ti_trong
  FROM orders
) t
WHERE ordered_at >= '2026-01-01';
```

Quy tắc rút ra: vị trí của `WHERE` so với hàm cửa sổ quyết định phạm vi của mẫu số, và hai cách viết trông gần giống nhau trả lời hai câu hỏi khác nhau.

## Góc Khuất & Ngộ Nhận

Về hiệu năng: mỗi `PARTITION BY`/`ORDER BY` khác nhau thường buộc một lần sắp xếp riêng. Ba hàm cửa sổ dùng chung một mệnh đề `OVER` chỉ tốn một lần sắp xếp; ba hàm với ba mệnh đề khác nhau tốn ba. Đặt tên cửa sổ bằng `WINDOW w AS (...)` rồi dùng lại giúp người đọc thấy điều đó, dù bộ tối ưu thường tự nhận ra.

`ROWS` chỉ đếm dòng, còn `RANGE` phải dò biên của các giá trị bằng nhau ở mỗi bước, nên `RANGE` làm thêm việc trên mọi cửa sổ có giá trị sắp xếp trùng lặp. Mức chênh cụ thể tùy hệ và tùy dữ liệu; đo bằng kế hoạch thực thi thay vì giả định. Khi hai cách cho cùng kết quả — tức là không có giá trị sắp xếp trùng nhau — chọn `ROWS`.

**Hiểu lầm:** "Hàm cửa sổ là cách viết gọn của `GROUP BY`."
**Thực tế:** Chúng cho ra số dòng khác nhau. `GROUP BY` gộp, hàm cửa sổ không. Một truy vấn thay `GROUP BY` bằng `OVER` sẽ trả về đủ số dòng gốc kèm giá trị lặp lại trong mỗi nhóm. **Vì sao nghe hợp lý:** cả hai đều dùng tên hàm giống hệt — `SUM`, `AVG`, `COUNT` — nên người học gán chúng vào cùng một ngăn.

**Hiểu lầm:** "`ORDER BY` trong `OVER` sắp xếp kết quả."
**Thực tế:** Nó chỉ định nghĩa thứ tự để khung cửa sổ trượt theo. Thứ tự dòng trả về vẫn không xác định nếu không có `ORDER BY` ở tầng ngoài cùng. **Vì sao nghe hợp lý:** trong nhiều trường hợp kết quả tình cờ ra đúng thứ tự ấy, vì bộ thực thi đã sắp xếp sẵn để tính cửa sổ và không buồn xáo lại.

**Hiểu lầm:** "Không viết mệnh đề khung thì cửa sổ là toàn bộ phân vùng."
**Thực tế:** Chỉ đúng khi không có `ORDER BY`. Có `ORDER BY` mà thiếu khung thì mặc định là từ đầu phân vùng tới dòng hiện tại — tức tổng lũy kế, không phải tổng toàn phân vùng. **Vì sao nghe hợp lý:** với `PARTITION BY` đơn thuần thì đúng là toàn phân vùng, và người ta thử ở đó trước rồi khái quát hóa.

## Nếu Bạn Dạy Lại Điều Này...

Mở đầu bằng cách viết `SELECT customer_id, SUM(amount) FROM ... GROUP BY customer_id` rồi đổi đúng một chỗ thành `SUM(amount) OVER (PARTITION BY customer_id)`, chạy cả hai cạnh nhau. Số dòng khác nhau là bài học, và nó hiện ra trước khi có bất kỳ định nghĩa nào.

Hạt giống bài tập: cho một truy vấn tính tỉ trọng có `WHERE` đặt sai tầng, kèm kết quả trông hợp lý. Yêu cầu chỉ ra mẫu số đang là gì trước khi sửa.

## Tự Kiểm Tra Nhanh

**1. Vì sao `WHERE thu_tu = 1` báo lỗi khi `thu_tu` là kết quả `ROW_NUMBER()`?**

<details><summary>Đáp án</summary>

Hàm cửa sổ được tính sau `WHERE` trong thứ tự thực thi, nên tại thời điểm `WHERE` chạy thì cột ấy chưa tồn tại. Phải bọc truy vấn lại một tầng, hoặc dùng `QUALIFY` ở các hệ có hỗ trợ.
</details>

**2. `SUM(x) OVER (ORDER BY ngay)` trên dữ liệu có hai giao dịch cùng ngày cho ra gì ở dòng đầu tiên của ngày đó?**

<details><summary>Đáp án</summary>

Tổng bao gồm **cả hai** giao dịch của ngày đó, vì mặc định là `RANGE` chứ không phải `ROWS`, và `RANGE` gộp mọi dòng cùng giá trị sắp xếp vào một bậc. Muốn tổng lũy kế theo từng dòng thì viết rõ `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`.
</details>

**3. Khác nhau giữa `RANK()` và `DENSE_RANK()` khi có hai người đồng hạng nhì?**

<details><summary>Đáp án</summary>

`RANK()` cho 1, 2, 2, 4 — bỏ qua hạng 3 vì hai người đã chiếm hai chỗ. `DENSE_RANK()` cho 1, 2, 2, 3 — không để trống hạng nào. Chọn cái nào phụ thuộc câu hỏi có coi "hạng ba" là người xếp sau hai người đó hay không.
</details>

Ghi chú tiếp theo là [CTE và subquery](sql.cte-vs-subquery.md), nơi lớp bọc bắt buộc ở ví dụ trên có tên gọi và có hệ quả về hiệu năng.
