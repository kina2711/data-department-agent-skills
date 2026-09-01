---
id: data-analyst.sql.cte-vs-subquery
title: CTE vs subquery
domain: data-analyst
type: pattern
tags: [sql, sql-analysis, cte, vs, subquery]
status: draft
ai_summary: A CTE is a named intermediate result that may or may not be materialised; it changes readability always and performance only sometimes, depending on the engine's inlining behaviour.
relationships:
  builds_on: [data-analyst.sql.window-function]
  prerequisite_of: []
  commonly_confused_with: [data-analyst.sql.window-function]
created: 2026-09-01
updated: 2026-09-01
version_sensitive: true
---

# CTE vs subquery

**Tóm tắt bản chất:** CTE là một kết quả trung gian có tên. Nó luôn thay đổi khả năng đọc, và **đôi khi** thay đổi hiệu năng — tùy vào việc bộ tối ưu có nội tuyến nó hay vật chất hóa nó, một quyết định khác nhau giữa các hệ và giữa các phiên bản.

## Nỗi Đau & Động Lực

Một truy vấn phân tích thật hiếm khi có một tầng. Nó lọc, rồi tổng hợp, rồi xếp hạng, rồi lọc theo thứ hạng — bốn bước, mỗi bước cần kết quả của bước trước. Viết bằng subquery lồng nhau thì bước cuối nằm ngoài cùng và bước đầu nằm sâu nhất, tức là **thứ tự đọc ngược với thứ tự xảy ra**.

Người đọc phải bắt đầu từ trong ra ngoài, giữ bốn tầng trong đầu, và không có chỗ nào để đặt tên cho ý nghĩa của từng tầng. Sáu tháng sau, chính người viết cũng phải giải mã lại từ đầu.

Chi phí thật xuất hiện lúc sửa. Khi cần thêm một điều kiện vào tầng thứ hai, phải đếm dấu ngoặc để tìm đúng chỗ, và một dấu ngoặc đặt sai vẫn có thể cho ra truy vấn hợp lệ trả về số khác. Đây là loại thay đổi mà việc rà soát không bắt được, vì diff trông nhỏ trong khi ngữ nghĩa đã đổi tầng.

## Cơ Chế Tác Động

CTE khai báo trước, dùng sau:

```sql
WITH don_2026 AS (
  SELECT * FROM orders WHERE ordered_at >= '2026-01-01'
), theo_khach AS (
  SELECT customer_id, SUM(gross_amount) AS tong FROM don_2026 GROUP BY customer_id
)
SELECT * FROM theo_khach WHERE tong > 10000000;
```

Thứ tự đọc bây giờ trùng thứ tự xảy ra, và mỗi bước có một cái tên nói lên nó là gì.

Về mặt ngữ nghĩa, CTE và subquery tương đương. Điểm khác nằm ở chỗ bộ tối ưu xử lý chúng thế nào, và có hai chiến lược:

**Nội tuyến (inline).** Bộ tối ưu thay tên CTE bằng thân của nó rồi tối ưu toàn bộ như một truy vấn phẳng. Điều kiện lọc ở ngoài có thể được đẩy vào trong, chỉ mục được dùng, và kết quả thường ngang bằng subquery.

**Vật chất hóa (materialise).** CTE được tính một lần, kết quả lưu vào bảng tạm, các nơi dùng đọc từ bảng ấy. Lợi khi CTE được tham chiếu nhiều lần và tốn kém; hại khi nó chỉ được dùng một lần và điều kiện lọc ở ngoài lẽ ra đã cắt được 99% dữ liệu.

Hành vi mặc định **khác nhau giữa các hệ và đã thay đổi theo phiên bản**. PostgreSQL từng luôn vật chất hóa CTE và điều đó tạo ra cả một thế hệ lời khuyên "CTE chậm hơn subquery"; các phiên bản sau cho phép nội tuyến khi CTE không có tác dụng phụ và chỉ được dùng một lần, đồng thời bổ sung `MATERIALIZED` / `NOT MATERIALIZED` để ép. Vì lời khuyên cũ vẫn lan truyền lâu hơn hành vi cũ tồn tại, hãy kiểm bằng kế hoạch thực thi trên chính hệ và phiên bản bạn đang chạy thay vì tin bất kỳ quy tắc chung nào, kể cả câu này.

## Bản Đồ Quyết Định

| Tình huống | Chọn | Vì sao |
|---|---|---|
| ba tầng trở lên | CTE | thứ tự đọc trùng thứ tự xảy ra |
| kết quả trung gian dùng nhiều lần | CTE | subquery buộc lặp lại toàn bộ định nghĩa |
| một tầng, một chỗ dùng | subquery | thêm một tên không làm gì rõ hơn |
| cần lọc theo cột hàm cửa sổ | CTE hoặc subquery bọc | hàm cửa sổ chạy sau `WHERE` |
| kiểm tra tồn tại | `EXISTS`, không phải CTE | không cần cột nào, không nên nhân dòng |
| đệ quy | `WITH RECURSIVE` | subquery không làm được |

Hậu quả của việc chọn sai không đối xứng. Dùng CTE ở chỗ chỉ cần subquery làm truy vấn dài hơn vài dòng — chi phí thẩm mỹ. Dùng subquery lồng bốn tầng ở chỗ cần CTE tạo ra một đoạn mã mà lần sửa sau sẽ đặt điều kiện vào nhầm tầng — chi phí là một con số sai không ai truy được nguồn.

Một hệ quả ít được nói: CTE làm cho việc **kiểm thử từng bước** trở nên khả thi. Muốn biết tầng thứ hai trả về gì, chỉ cần đổi `SELECT` cuối thành `SELECT * FROM theo_khach`. Với subquery lồng nhau, phải copy đoạn giữa ra ngoài và sửa dấu ngoặc — đủ phiền để người ta bỏ qua bước kiểm.

## Case Study Thực Chiến: khách hàng có đơn đầu tiên trên 5 triệu

Lược đồ tối thiểu:

```
orders (order_id, customer_id, ordered_at, gross_amount)
```

Viết bằng subquery lồng, đọc từ trong ra:

```sql
SELECT customer_id, gross_amount
FROM (SELECT customer_id, gross_amount,
             ROW_NUMBER() OVER (PARTITION BY customer_id
                                ORDER BY ordered_at, order_id) AS thu_tu
      FROM (SELECT * FROM orders WHERE ordered_at >= '2026-01-01') a) b
WHERE thu_tu = 1 AND gross_amount > 5000000;
```

Ba tầng, hai bí danh vô nghĩa là `a` và `b`, và điều kiện thời gian nằm sâu nhất trong khi nó là điều kiện đầu tiên người đọc cần biết.

Cùng một truy vấn với CTE:

```sql
WITH don_2026 AS (
  SELECT * FROM orders WHERE ordered_at >= '2026-01-01'
), xep_thu_tu AS (
  SELECT customer_id, gross_amount,
         ROW_NUMBER() OVER (PARTITION BY customer_id
                            ORDER BY ordered_at, order_id) AS thu_tu
  FROM don_2026
)
SELECT customer_id, gross_amount
FROM xep_thu_tu
WHERE thu_tu = 1 AND gross_amount > 5000000;
```

Cùng kế hoạch thực thi trên hệ có nội tuyến, cùng kết quả, và người đọc tiếp theo không phải giải mã gì.

**Biến thể khó hơn, nơi cách hiểu trên gây hiểu lầm.** Giả sử `don_2026` được tham chiếu ở hai CTE khác nhau, và bảng `orders` có ba trăm triệu dòng.

Nếu hệ **nội tuyến**, thân CTE được thực thi hai lần — hai lần quét ba trăm triệu dòng cho một kết quả giống hệt nhau. Ở đây vật chất hóa mới đúng, và phải nói ra:

```sql
WITH don_2026 AS MATERIALIZED (
  SELECT * FROM orders WHERE ordered_at >= '2026-01-01'
)
```

Nhưng đảo ngược tình huống: CTE chỉ dùng một lần và truy vấn ngoài có `WHERE customer_id = 42`. Nếu hệ **vật chất hóa**, điều kiện ấy không đẩy được vào trong, nên bảng tạm chứa toàn bộ đơn của mọi khách rồi mới lọc còn một. Ở đây `NOT MATERIALIZED` mới đúng.

Quy tắc rút ra: không có lựa chọn nào đúng sẵn. Số lần tham chiếu và khả năng đẩy điều kiện xuống quyết định, và cách duy nhất để biết là đọc kế hoạch thực thi.

## Góc Khuất & Ngộ Nhận

`WITH RECURSIVE` là năng lực mà subquery không có: duyệt cây tổ chức, mở rộng khoảng ngày, lần theo chuỗi giới thiệu. Nó cần một nhánh neo và một nhánh đệ quy hợp bằng `UNION ALL`, và thiếu điều kiện dừng thì chạy vô hạn — nhiều hệ có giới hạn số vòng lặp, nhưng đừng dựa vào đó.

CTE không phải bảng tạm: nó chỉ tồn tại trong phạm vi một câu lệnh. Cần dùng lại ở nhiều câu lệnh thì phải là bảng tạm thật, và khi ấy quyền, khóa và vòng đời trở thành chuyện phải nghĩ tới.

**Hiểu lầm:** "CTE luôn chậm hơn subquery."
**Thực tế:** Lời khuyên này bắt nguồn từ hành vi vật chất hóa bắt buộc của một số hệ ở các phiên bản cũ, và không còn đúng phổ quát. Trên hệ có nội tuyến, hai cách thường cho cùng kế hoạch. **Vì sao nghe hợp lý:** nó từng đúng, đúng rất rõ ràng, trên hệ mà nhiều người học SQL đầu tiên — và lời khuyên sống lâu hơn điều kiện sinh ra nó.

**Hiểu lầm:** "Đặt tên CTE là chuyện thẩm mỹ."
**Thực tế:** Tên là nơi duy nhất trong SQL để nói *tại sao* một bước tồn tại. `don_2026` nói lên ý định; `b` thì không. Trong một truy vấn bốn tầng, tên là thứ giữ cho lần sửa sau đặt điều kiện đúng chỗ. **Vì sao nghe hợp lý:** cả hai chạy giống nhau, nên chi phí của tên tồi chỉ hiện ra ở lần sửa chứ không ở lần chạy.

**Hiểu lầm:** "CTE chạy tuần tự từ trên xuống."
**Thực tế:** Thứ tự khai báo là thứ tự đọc, không phải thứ tự thực thi. Bộ tối ưu có thể sắp xếp lại, đẩy điều kiện qua các tầng, hoặc bỏ hẳn một CTE không được dùng tới. **Vì sao nghe hợp lý:** cú pháp trông giống một chuỗi phép gán, mà SQL là ngôn ngữ khai báo chứ không phải ngôn ngữ mệnh lệnh.

## Nếu Bạn Dạy Lại Điều Này...

Mở đầu bằng cách chiếu truy vấn ba tầng subquery ở trên và hỏi: "Điều kiện thời gian áp ở bước nào?" Thời gian mọi người mất để tìm ra chính là lập luận cho CTE, và nó thuyết phục hơn bất kỳ câu nào về khả năng đọc.

Hạt giống bài tập: cho cùng một truy vấn viết theo hai cách, yêu cầu chạy `EXPLAIN` cả hai trên hệ đang dùng và so sánh kế hoạch — rồi giải thích vì sao chúng giống nhau hoặc khác nhau.

## Tự Kiểm Tra Nhanh

**1. Khi nào CTE thực sự chậm hơn subquery tương đương?**

<details><summary>Đáp án</summary>

Khi hệ vật chất hóa nó, nó chỉ được dùng một lần, và truy vấn ngoài có điều kiện lọc lẽ ra đã đẩy được xuống. Bảng tạm khi ấy chứa nhiều dữ liệu hơn hẳn mức cần thiết. Kiểm bằng kế hoạch thực thi, không suy từ quy tắc chung.
</details>

**2. Vì sao không thể dùng CTE thay cho bảng tạm giữa hai câu lệnh?**

<details><summary>Đáp án</summary>

Phạm vi của CTE là một câu lệnh. Câu lệnh kết thúc thì nó biến mất. Bảng tạm tồn tại theo phiên hoặc theo giao dịch, và đi kèm những chuyện CTE không có: quyền truy cập, khóa, và dọn dẹp.
</details>

**3. `WITH RECURSIVE` cần những gì để không chạy vô hạn?**

<details><summary>Đáp án</summary>

Một nhánh neo trả về tập khởi đầu hữu hạn, và một nhánh đệ quy có điều kiện khiến tập kết quả nhỏ dần về rỗng. Dữ liệu có chu trình — cây tổ chức bị nhập sai thành vòng — vẫn chạy mãi dù truy vấn viết đúng, nên thường phải mang theo một cột đếm độ sâu và chặn nó.
</details>

Ghi chú tiếp theo là [Lỗi tổng hợp sai grain](sql.aggregation-grain-error.md), nơi mọi thứ trong hai module này gặp nhau ở một con số sai.
