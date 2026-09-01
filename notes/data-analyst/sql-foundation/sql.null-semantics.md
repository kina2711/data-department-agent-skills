---
id: data-analyst.sql.null-semantics
title: Null semantics
domain: data-analyst
type: pitfall
tags: [sql, sql-foundation, null, semantics]
status: draft
ai_summary: Null means unknown rather than empty, so it propagates through arithmetic, is never equal to anything including itself, and is silently skipped by aggregates.
relationships:
  builds_on: []
  prerequisite_of: [data-analyst.sql.set-operations]
  commonly_confused_with: []
created: 2026-09-01
updated: 2026-09-01
version_sensitive: false
---

# Null semantics

**Tóm tắt bản chất:** `NULL` nghĩa là *không biết*, không phải *rỗng* và không phải *bằng không*. Từ một chữ đó suy ra ba hệ quả: nó lan qua mọi phép tính, nó không bằng bất cứ thứ gì kể cả chính nó, và hàm tổng hợp lặng lẽ bỏ qua nó.

## Nỗi Đau & Động Lực

Một bộ lọc loại mất 4.000 dòng mà không ai để ý. Điều kiện là `WHERE discount_amount != 0`, ý định là "lấy các dòng hàng không giảm giá ra khỏi phân tích". Kết quả trả về ít hơn dự kiến đúng bằng số dòng hàng chưa từng có giảm giá — vì với những dòng ấy `discount_amount` là `NULL`, và `NULL != 0` không cho ra `TRUE`, cũng không cho ra `FALSE`. Nó cho ra `NULL`, và `WHERE` chỉ giữ dòng khi điều kiện là `TRUE`.

Không có cảnh báo nào. Truy vấn chạy, bảng kết quả trông hợp lý, chỉ có điều nó mô tả một tập con mà không ai chọn. Đây là loại lỗi tệ nhất trong phân tích: nó không làm hỏng con số một cách lộ liễu, nó thu hẹp mẫu.

Cái giá thật nằm ở chỗ khác nữa. Khi hai người cùng phân tích một bảng và một người dùng `!= 0`, người kia dùng `IS DISTINCT FROM 0`, hai kết quả lệch nhau và không ai sai cú pháp. Cuộc tranh luận sau đó tốn nhiều thời gian hơn hẳn việc hiểu `NULL` ngay từ đầu.

## Cơ Chế Tác Động

Logic của SQL có ba giá trị, không phải hai: `TRUE`, `FALSE`, `UNKNOWN`. Mọi phép so sánh có `NULL` tham gia đều trả về `UNKNOWN`.

```sql
SELECT NULL = NULL;      -- NULL, không phải TRUE
SELECT NULL != NULL;     -- NULL, không phải FALSE
SELECT NULL IS NULL;     -- TRUE  ← chỉ IS mới hỏi được
```

Bảng chân trị cần thuộc, vì đây là chỗ trực giác Boole hai giá trị dẫn sai đường:

| A | B | `A AND B` | `A OR B` |
|---|---|---|---|
| `TRUE` | `NULL` | `NULL` | `TRUE` |
| `FALSE` | `NULL` | `FALSE` | `NULL` |
| `NULL` | `NULL` | `NULL` | `NULL` |

Đọc hai dòng đầu cho kỹ. `FALSE AND NULL` ra `FALSE` vì dù giá trị chưa biết là gì thì kết quả vẫn sai. `TRUE OR NULL` ra `TRUE` vì cùng lý do đối xứng. Ở hai ô còn lại, giá trị chưa biết quyết định kết quả, nên kết quả cũng chưa biết.

Ba nơi `NULL` cư xử khác nhau, và đây là nguồn gốc của phần lớn nhầm lẫn:

1. **Số học:** `5 + NULL` ra `NULL`. Bất kỳ biểu thức nào chạm vào `NULL` đều thành `NULL`.
2. **Hàm tổng hợp:** `SUM`, `AVG`, `COUNT(cot)` **bỏ qua** `NULL` thay vì lan truyền. `AVG(amount)` chia cho số dòng có giá trị, không chia cho tổng số dòng.
3. **`GROUP BY`, `DISTINCT`, `UNION`:** ở đây các `NULL` được coi là **giống nhau** và gộp thành một nhóm — trái ngược hẳn với quy tắc `NULL != NULL` ở trên.

Điểm 3 mâu thuẫn với điểm ở đầu bài, và mâu thuẫn ấy là có thật trong chuẩn SQL chứ không phải tôi diễn đạt nhầm: so sánh dùng logic ba giá trị, còn gom nhóm dùng khái niệm *not distinct*. Hai cơ chế khác nhau, tình cờ cùng gặp `NULL`.

## Bản Đồ Quyết Định

| Bạn muốn | Viết | Không viết | Hậu quả nếu viết sai |
|---|---|---|---|
| lọc dòng có giá trị | `WHERE x IS NOT NULL` | `WHERE x != NULL` | không dòng nào qua được |
| so sánh coi `NULL` như một giá trị | `WHERE x IS DISTINCT FROM 0` | `WHERE x != 0` | mất toàn bộ dòng `NULL` |
| thay `NULL` bằng 0 khi cộng | `COALESCE(x, 0)` | `x` trần | tổng thành `NULL` nếu dùng trong biểu thức |
| đếm dòng | `COUNT(*)` | `COUNT(cot)` | đếm thiếu đúng bằng số `NULL` |
| trung bình coi `NULL` là 0 | `SUM(x) / COUNT(*)` | `AVG(x)` | mẫu số sai, trung bình bị đẩy lên |
| nối chuỗi an toàn | `CONCAT(a, b)` | `a \|\| b` | một `NULL` làm cả chuỗi thành `NULL` |

Dòng áp chót là chỗ tinh vi nhất. `AVG(x)` không sai — nó trả lời câu hỏi "trung bình của những giá trị đã biết". Nếu câu hỏi kinh doanh là "giảm giá trung bình trên mỗi dòng hàng", và dòng không giảm giá được ghi là `NULL` thay vì `0`, thì `AVG` trả lời một câu hỏi khác câu bạn hỏi. Quyết định nằm ở chỗ `NULL` trong cột ấy nghĩa là "không có giảm giá" hay "chưa biết có giảm giá hay không". Lược đồ không nói cho bạn biết; chỉ người vận hành hệ thống nguồn mới nói được.

## Case Study Thực Chiến: tỉ lệ hoàn tiền tính ra 0%

Lược đồ tối thiểu:

```
orders  (order_id, gross_amount)
refunds (refund_id, order_id, refunded_at, amount)
```

Câu hỏi: bao nhiêu phần trăm đơn hàng đã bị hoàn tiền trong tháng? Truy vấn đã dùng:

```sql
SELECT COUNT(r.refund_id) * 100.0 / COUNT(*) AS ti_le_hoan
FROM orders o
LEFT JOIN refunds r ON r.order_id = o.order_id;
```

Kết quả ra một con số nhỏ đến vô lý, và với một tập dữ liệu nhất định thì ra đúng `0`. Nguyên nhân không phải `NULL` ở đây — `COUNT(r.refund_id)` bỏ qua `NULL` là đúng ý định. Nguyên nhân là mẫu số: `COUNT(*)` đếm dòng **sau** join, mà đơn hoàn hai lần cho hai dòng. Mẫu số phồng lên, tử số cũng phồng nhưng theo tỉ lệ khác.

Sửa bằng cách đưa cả hai vế về grain đơn hàng:

```sql
SELECT COUNT(DISTINCT r.order_id) * 100.0 / COUNT(DISTINCT o.order_id) AS ti_le_hoan
FROM orders o
LEFT JOIN refunds r ON r.order_id = o.order_id;
```

**Biến thể khó hơn.** Bây giờ đổi câu hỏi thành "tỉ lệ đơn đã hoàn tiền **xong**", và điều kiện là `refunded_at IS NOT NULL`. Nếu đặt điều kiện ấy vào `WHERE`, `LEFT JOIN` bị biến thành `INNER JOIN` một cách âm thầm: dòng không khớp có `r.refunded_at` là `NULL`, `NULL IS NOT NULL` cho `FALSE`, và toàn bộ đơn chưa từng hoàn tiền biến mất khỏi mẫu số. Tỉ lệ nhảy lên gần 100%.

Điều kiện ấy phải nằm trong `ON`, không phải `WHERE`:

```sql
LEFT JOIN refunds r
  ON r.order_id = o.order_id
 AND r.refunded_at IS NOT NULL
```

Đây là lý do một quy tắc thường được dạy dưới dạng mẹo — "đừng lọc bảng phải của LEFT JOIN trong WHERE" — thực chất chỉ là hệ quả của logic ba giá trị.

## Góc Khuất & Ngộ Nhận

Về chỉ mục: phần lớn cơ sở dữ liệu quan hệ **không** đưa `NULL` vào B-tree index theo mặc định trong một số trường hợp, hoặc đưa vào nhưng ở một đầu của thứ tự sắp xếp. Hệ quả thực tế là `WHERE x IS NULL` có thể quét toàn bảng trong khi `WHERE x = 5` dùng chỉ mục. Nếu một truy vấn lọc `IS NULL` trên bảng lớn chạy chậm bất thường, đây là chỗ nhìn đầu tiên. Hành vi cụ thể khác nhau giữa các hệ, nên kiểm bằng kế hoạch thực thi thay vì tin một quy tắc chung.

Về sắp xếp: `ORDER BY` phải quyết định `NULL` đứng trước hay sau, và các hệ chọn mặc định khác nhau. Một truy vấn lấy "bản ghi mới nhất" bằng `ORDER BY updated_at DESC LIMIT 1` có thể trả về đúng dòng có `updated_at` là `NULL`, tùy hệ. Viết rõ `NULLS LAST` khi thứ tự có ý nghĩa.

**Hiểu lầm:** "`NULL` bằng chuỗi rỗng."
**Thực tế:** `'' = NULL` cho `NULL`, và trong hầu hết hệ hiện đại `''` là một giá trị đã biết còn `NULL` thì không. Ngoại lệ lịch sử là Oracle, nơi chuỗi rỗng được lưu thành `NULL` — điều này khiến ngộ nhận sống dai, vì nó từng đúng ở một hệ mà nhiều người học đầu tiên. **Vì sao nghe hợp lý:** cả hai đều hiển thị là ô trống trên giao diện.

**Hiểu lầm:** "`COUNT(*)` và `COUNT(cot)` chỉ khác nhau về hiệu năng."
**Thực tế:** chúng trả lời hai câu hỏi khác nhau. `COUNT(*)` đếm dòng, `COUNT(cot)` đếm giá trị đã biết trong cột đó. Trên bảng không có `NULL` thì bằng nhau, và đó chính là lý do ngộ nhận tồn tại: người ta kiểm chứng trên dữ liệu sạch rồi khái quát hóa.

**Hiểu lầm:** "Cứ `COALESCE` hết là an toàn."
**Thực tế:** `COALESCE(x, 0)` biến "không biết" thành "bằng không", tức là bịa ra một dữ kiện. Với `discount_amount` thì thường vô hại. Với `refunds.amount` chưa xử lý xong, nó khẳng định số tiền hoàn là 0 trong khi thực tế chưa ai biết. **Vì sao nghe hợp lý:** nó làm mọi cảnh báo biến mất — mà cảnh báo biến mất không đồng nghĩa với vấn đề được giải quyết.

## Nếu Bạn Dạy Lại Điều Này...

Mở đầu bằng `SELECT NULL = NULL;` chạy trực tiếp trước mặt học viên. Gần như ai cũng đoán `TRUE`, một số đoán `FALSE`, và kết quả `NULL` tạo ra đúng khoảnh khắc cần thiết để giải thích logic ba giá trị.

Hạt giống bài tập: đưa một bảng 10 dòng có 3 `NULL` ở cột số, yêu cầu tính trung bình bằng hai cách — `AVG(x)` và `SUM(x)/COUNT(*)` — rồi giải thích tình huống kinh doanh nào thì mỗi cách là câu trả lời đúng.

## Tự Kiểm Tra Nhanh

**1. `WHERE segment NOT IN ('A', 'B')` trên bảng có `segment` là `NULL`. Dòng `NULL` có được trả về không?**

<details><summary>Đáp án</summary>

Không. `NULL NOT IN ('A','B')` được đánh giá thành `NULL AND NULL`, cho ra `NULL`, và `WHERE` chỉ giữ `TRUE`. Đây cũng là lý do `NOT IN` với một danh sách con truy vấn có chứa `NULL` trả về tập rỗng — một trong những bẫy khó thấy nhất của SQL.
</details>

**2. Bảng có 100 dòng, cột `amount` có 30 dòng `NULL`. `AVG(amount)` chia cho bao nhiêu?**

<details><summary>Đáp án</summary>

70. Hàm tổng hợp bỏ qua `NULL` ở cả tử số lẫn mẫu số. Nếu ý định là coi `NULL` như 0 thì phải viết `SUM(amount) / COUNT(*)` hoặc `AVG(COALESCE(amount, 0))`.
</details>

**3. `GROUP BY segment` trên cột có nhiều `NULL` cho ra bao nhiêu nhóm `NULL`?**

<details><summary>Đáp án</summary>

Một. Gom nhóm dùng khái niệm *not distinct* chứ không dùng phép so sánh bằng, nên mọi `NULL` rơi vào cùng một nhóm — dù `NULL = NULL` không bao giờ đúng.
</details>

Ghi chú tiếp theo là [Phép toán tập hợp](sql.set-operations.md), nơi quy tắc gộp `NULL` ở `GROUP BY` xuất hiện lại dưới một cái tên khác.
