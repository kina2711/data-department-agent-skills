---
id: data-analyst.sql.set-operations
title: Set operations
domain: data-analyst
type: mechanism
tags: [sql, sql-foundation, set, operations]
status: draft
ai_summary: Union, intersect and except treat rows as set members, which is why union deduplicates and union all does not, and why they match by column position rather than by name.
relationships:
  builds_on: [data-analyst.sql.null-semantics]
  prerequisite_of: []
  commonly_confused_with: [data-analyst.sql.join-semantics]
created: 2026-09-01
updated: 2026-09-01
version_sensitive: false
---

# Set operations

**Tóm tắt bản chất:** `UNION`, `INTERSECT` và `EXCEPT` coi mỗi dòng là một phần tử của tập hợp, nên chúng khử trùng lặp theo định nghĩa — `UNION ALL` là phiên bản từ chối làm việc đó. Chúng ghép cột theo **vị trí**, không theo tên, và đây là nguồn gốc của loại lỗi im lặng nhất trong nhóm này.

## Nỗi Đau & Động Lực

Ghép hai truy vấn bằng `UNION`, mỗi truy vấn chọn `customer_id, country`. Một hôm ai đó sửa truy vấn thứ hai thành `country, customer_id` — đảo hai cột, một thay đổi trông vô hại vì cả hai đều là chuỗi. SQL không báo lỗi. Kết quả có `customer_id` chứa tên quốc gia và `country` chứa mã khách hàng, trộn lẫn với dữ liệu đúng từ truy vấn thứ nhất.

Chẳng ràng buộc nào bắt được việc này. Kiểu dữ liệu tương thích, số cột khớp, cú pháp hợp lệ. Cả hai cột cùng là `INTEGER` thì càng tệ — mã khách hàng và mã bưu chính lẫn vào nhau và trông y hệt dữ liệu thật.

Chi phí thứ hai, âm thầm hơn: `UNION` khử trùng lặp, và việc khử ấy có thể xóa mất dữ liệu hợp lệ. Giả sử hai giao dịch khác nhau tình cờ cùng khách hàng, cùng ngày, cùng số tiền — đó là hai dòng giống hệt nhau — `UNION` gộp thành một, và số giao dịch báo cáo ít hơn thực tế. Người viết truy vấn thường không có ý định khử trùng; họ chỉ gõ `UNION` vì đó là từ họ nhớ.

## Cơ Chế Tác Động

Ba toán tử, cùng một cơ chế nền:

| Toán tử | Giữ dòng nào | Khử trùng |
|---|---|---|
| `UNION` | có ở A hoặc B | có |
| `UNION ALL` | có ở A hoặc B | không |
| `INTERSECT` | có ở cả A và B | có |
| `EXCEPT` | có ở A, không có ở B | có |

Ba quy tắc ghép cột, tất cả đều là nguồn lỗi:

1. **Số cột phải bằng nhau.** Đây là điều kiện duy nhất được kiểm tra và báo lỗi.
2. **Kiểu dữ liệu phải tương thích theo vị trí.** Cột 1 của A ghép với cột 1 của B. Tên cột không được xét đến; tên của kết quả lấy theo truy vấn đầu tiên.
3. **Không có kiểm tra nào về ngữ nghĩa.** `customer_id` ghép với `postal_code` là hợp lệ nếu cả hai là số nguyên.

Về `NULL`: ở đây các `NULL` được coi là **giống nhau**, đúng như trong `GROUP BY` và `DISTINCT`. Dòng nào cùng có `NULL` ở cột `segment` và giống nhau ở mọi cột khác đều bị `UNION` gộp lại — dù `NULL = NULL` không bao giờ đúng. Quy tắc này dùng khái niệm *not distinct*, không dùng phép so sánh bằng, và đó là lý do hai hành vi tưởng như mâu thuẫn cùng tồn tại trong một ngôn ngữ.

Việc khử trùng tốn kém hơn vẻ ngoài của nó: cơ sở dữ liệu phải sắp xếp hoặc băm toàn bộ kết quả. `UNION ALL` chỉ nối hai luồng và thường nhanh hơn nhiều lần trên dữ liệu lớn.

## Bản Đồ Quyết Định

| Ý định | Viết | Hậu quả nếu chọn nhầm |
|---|---|---|
| gộp hai nguồn, biết chắc không trùng | `UNION ALL` | dùng `UNION` thì mất dòng hợp lệ trùng giá trị, và chậm hơn |
| gộp hai nguồn, có thể trùng, muốn khử | `UNION` | dùng `UNION ALL` thì đếm hai lần |
| tìm phần chung | `INTERSECT` | viết bằng `IN` thì đúng, nhưng khác về xử lý `NULL` |
| tìm phần chỉ có ở A | `EXCEPT` | dùng `NOT IN` với danh sách chứa `NULL` thì trả về rỗng |
| ghép thêm **cột**, không phải thêm dòng | `JOIN` | nhầm sang `UNION` là nhầm chiều của phép ghép |

Dòng cuối là nhầm lẫn khái niệm chứ không phải nhầm cú pháp. `JOIN` ghép theo chiều ngang — thêm cột cho cùng một thực thể. Phép toán tập hợp ghép theo chiều dọc — thêm dòng cùng cấu trúc. Khi ai đó hỏi "join hay union", câu hỏi thật sự là "tôi cần thêm thuộc tính hay thêm bản ghi".

Dòng thứ tư đáng nhớ riêng, vì nó nối ghi chú này với ghi chú về `NULL`. Toán tử `EXCEPT` xử lý `NULL` theo *not distinct* nên hoạt động đúng như trực giác. `NOT IN` xử lý theo logic ba giá trị nên trả về tập rỗng ngay khi danh sách con truy vấn chứa một `NULL`. Cùng một ý định, hai cách viết: một an toàn, một có bẫy.

## Case Study Thực Chiến: hợp nhất danh sách khách hàng từ hai hệ thống

Lược đồ tối thiểu, hai nguồn sau một lần sáp nhập công ty:

```
customers      (customer_id, email, country)
customers_bnew (customer_id, email, country)
```

Yêu cầu: một danh sách khách hàng duy nhất cho toàn công ty.

```sql
SELECT customer_id, email, country FROM customers
UNION
SELECT customer_id, email, country FROM customers_bnew;
```

Truy vấn này khử được các dòng trùng hoàn toàn. Nó **không** khử được cùng một người xuất hiện ở hai hệ thống với `customer_id` khác nhau — mà đó chính là tình huống phổ biến nhất sau sáp nhập. `UNION` khử trùng theo toàn bộ dòng, không theo khóa nghiệp vụ.

Muốn khử theo email thì phải nói ra điều đó:

```sql
SELECT DISTINCT ON (email) customer_id, email, country
FROM (
  SELECT customer_id, email, country FROM customers
  UNION ALL
  SELECT customer_id, email, country FROM customers_bnew
) t
ORDER BY email, customer_id;
```

Chú ý `UNION ALL` ở trong: khử trùng hai lần bằng hai tiêu chí khác nhau là lãng phí, và tiêu chí ở ngoài mới là tiêu chí đúng.

**Biến thể khó hơn, nơi cách hiểu trên gây hiểu lầm.** Bây giờ cần đếm số khách hàng chỉ tồn tại ở hệ thống cũ:

```sql
SELECT COUNT(*) FROM (
  SELECT email FROM customers
  EXCEPT
  SELECT email FROM customers_bnew
) t;
```

Con số này **không** phải số khách hàng chỉ có ở hệ cũ. Phép `EXCEPT` khử trùng ở cả hai vế trước khi trừ, nên nếu một email xuất hiện ba lần trong `customers` — dữ liệu bẩn, nhưng có thật — nó được đếm một lần. Đó có thể đúng ý bạn hoặc không, và cú pháp không hỏi. Muốn giữ bội số thì một số hệ có `EXCEPT ALL`; nơi không có, phải tự đếm rồi trừ.

Bẫy cuối: nếu `email` có `NULL`, `EXCEPT` coi mọi `NULL` là một giá trị và so khớp được — trong khi viết cùng ý định bằng `NOT IN` sẽ trả về tập rỗng. Cùng một câu hỏi, hai cách viết, hai kết quả, không cách nào báo lỗi.

## Góc Khuất & Ngộ Nhận

Về hiệu năng: `UNION` trên hai bảng lớn buộc phải sắp xếp hoặc băm toàn bộ để khử trùng, và chi phí ấy tỉ lệ với tổng số dòng đầu vào chứ không với số dòng kết quả. Biết chắc không có trùng lặp — chẳng hạn hai nguồn phân vùng theo thời gian không chồng lấn — thì `UNION ALL` là lựa chọn đúng cả về nghĩa lẫn về tốc độ.

`ORDER BY` chỉ được đặt một lần, ở cuối toàn bộ biểu thức, và áp lên kết quả cuối. Đặt trong nhánh con thường bị bỏ qua hoặc bị từ chối tùy hệ.

**Hiểu lầm:** "`UNION` ghép theo tên cột."
**Thực tế:** nó ghép theo vị trí. Tên chỉ dùng để đặt nhãn cho kết quả, lấy từ truy vấn đầu tiên. **Vì sao nghe hợp lý:** trong mọi ví dụ được viết cẩn thận, tên và vị trí trùng nhau — nên quy tắc thật không bao giờ lộ ra cho tới lúc ai đó đảo cột.

**Hiểu lầm:** "`UNION ALL` là phiên bản tối ưu của `UNION`."
**Thực tế:** chúng trả lời hai câu hỏi khác nhau. `UNION` khẳng định "tôi muốn tập hợp các giá trị phân biệt", `UNION ALL` khẳng định "tôi muốn mọi bản ghi". Nhanh hơn chỉ là hệ quả. **Vì sao nghe hợp lý:** lời khuyên "dùng `UNION ALL` cho nhanh" được lặp lại nhiều đến mức phần ngữ nghĩa rơi mất.

**Hiểu lầm:** "`INTERSECT` tương đương `INNER JOIN` trên mọi cột."
**Thực tế:** `INTERSECT` khử trùng còn `JOIN` thì nhân bản. Bảng A có một dòng, bảng B có ba dòng giống hệt nó: `INTERSECT` cho một dòng, `INNER JOIN` cho ba. **Vì sao nghe hợp lý:** trên dữ liệu không trùng lặp — trường hợp người ta thử — hai cách cho cùng kết quả.

## Nếu Bạn Dạy Lại Điều Này...

Mở đầu bằng hai truy vấn `UNION` có cột bị đảo, chạy thật, và để học viên nhìn kết quả trước khi nói cho họ biết chuyện gì xảy ra. Việc SQL im lặng chấp nhận là bài học chính, không phải cú pháp.

Hạt giống bài tập: cho hai bảng nhỏ có dòng trùng, yêu cầu dự đoán số dòng của `UNION`, `UNION ALL`, `INTERSECT` và `EXCEPT` trước khi chạy, rồi đối chiếu.

## Tự Kiểm Tra Nhanh

**1. A có 5 dòng trong đó 2 dòng giống hệt nhau, B có 3 dòng khác hoàn toàn A. `A UNION B` và `A UNION ALL B` cho bao nhiêu dòng?**

<details><summary>Đáp án</summary>

`UNION` cho 7 — hai dòng trùng trong A bị gộp thành một. `UNION ALL` cho 8, giữ nguyên mọi bản ghi. Chú ý `UNION` khử trùng cả bên trong từng nhánh, không chỉ giữa hai nhánh.
</details>

**2. Vì sao `UNION` không báo lỗi khi hai truy vấn có cột bị đảo thứ tự?**

<details><summary>Đáp án</summary>

Vì phép ghép dựa trên vị trí và kiểu dữ liệu, không dựa trên tên. Với SQL, hai cột cùng kiểu ở cùng vị trí là hợp lệ, dù chúng mang ý nghĩa hoàn toàn khác nhau. Không có tầng nào trong ngôn ngữ kiểm tra ngữ nghĩa của cột.
</details>

**3. Khi nào `EXCEPT` và `NOT IN` cho kết quả khác nhau?**

<details><summary>Đáp án</summary>

Khi tập bên phải chứa `NULL`. `EXCEPT` coi các `NULL` là not distinct nên so khớp bình thường; `NOT IN` dùng logic ba giá trị nên toàn bộ điều kiện thành `UNKNOWN` và kết quả là tập rỗng.
</details>

Ghi chú tiếp theo mở module `sql-analysis` với [Hàm cửa sổ](../sql-analysis/sql.window-function.md), nơi phép tính chạy trên từng dòng mà không gộp dòng nào.
