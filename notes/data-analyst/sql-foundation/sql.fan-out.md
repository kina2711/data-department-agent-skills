---
id: data-analyst.sql.fan-out
title: Join fan-out
domain: data-analyst
type: pitfall
tags: [sql, sql-foundation, fan, out]
status: draft
ai_summary: Fan-out is row multiplication from joining to a table whose join key is not unique, which silently inflates every downstream sum by a per-row factor.
relationships:
  builds_on: [data-analyst.sql.join-semantics]
  prerequisite_of: []
  commonly_confused_with: [data-analyst.sql.grain]
created: 2026-09-01
updated: 2026-09-01
version_sensitive: false
---

# Join fan-out

**Tóm tắt bản chất:** Fan-out là hiện tượng một dòng bị nhân thành nhiều dòng vì khóa ghép ở bảng bên kia không duy nhất. Nó không gây lỗi, không cảnh báo, và thổi phồng mọi phép cộng phía sau theo một hệ số khác nhau cho từng dòng.

## Nỗi Đau & Động Lực

Điều làm fan-out nguy hiểm hơn hẳn các lỗi SQL khác là nó **không đồng đều**. Nếu mọi dòng đều bị nhân đúng ba lần, tổng sẽ gấp ba, ai đó sẽ thấy con số vô lý và tìm ra ngay. Trên dữ liệu thật, đơn trả một lần nhân một, đơn trả góp ba kỳ nhân ba, đơn đổi hàng có thu bổ sung nhân hai. Tổng bị lệch một tỉ lệ nhỏ và trông hoàn toàn hợp lý.

Còn một biểu hiện khó chịu hơn nữa: sai số **thay đổi theo thời gian**. Tỉ lệ đơn trả góp tăng dần theo quý, nên mức thổi phồng cũng tăng dần. Biểu đồ tăng trưởng cho thấy một xu hướng đi lên đẹp đẽ, mà phần lớn độ dốc ấy là fan-out chứ không phải doanh thu.

Cái giá không đo bằng con số sai. Nó đo bằng việc một đội đã ra quyết định dựa trên xu hướng ấy suốt bốn quý, và khi phát hiện thì không chỉ báo cáo tháng này sai mà cả câu chuyện họ kể về mình cũng sai.

## Cơ Chế Tác Động

Hệ số fan-out của một dòng bên trái bằng đúng số dòng bên phải khớp với nó. Viết thành công thức:

```
tổng bị thổi = Σ (giá trị của dòng i × số lần dòng i được nhân)
```

Vì hệ số khác nhau theo từng dòng, mức sai lệch tổng thể là một **trung bình có trọng số** — trọng số chính là giá trị của dòng. Đơn giá trị lớn bị nhân ba gây hại nhiều hơn mười đơn nhỏ bị nhân hai.

Phát hiện fan-out bằng ba bước, làm trước khi tin bất kỳ con số nào:

**Bước 1 — kiểm lực lượng khóa của bảng sắp join tới.**

```sql
SELECT COUNT(*) AS tong_dong, COUNT(DISTINCT order_id) AS so_khoa
FROM payments;
```

Khác nhau nghĩa là fan-out sẽ xảy ra. Tỉ số `tong_dong / so_khoa` là hệ số nhân trung bình.

**Bước 2 — đếm dòng trước và sau join.**

```sql
SELECT COUNT(*) FROM orders;                                    -- ví dụ: 12.480
SELECT COUNT(*) FROM orders o JOIN payments p USING (order_id); -- ví dụ: 14.732
```

Chênh lệch 2.252 dòng là số bản sao thừa. Rẻ nhất trong ba bước, và ít người làm nhất.

**Bước 3 — tìm dòng bị nhân nhiều nhất, để biết rủi ro tập trung ở đâu.**

```sql
SELECT order_id, COUNT(*) AS he_so
FROM payments
GROUP BY order_id
ORDER BY he_so DESC
LIMIT 10;
```

Dòng đầu bảng có hệ số 40 nghĩa là một đơn duy nhất đang đóng góp 40 lần vào tổng.

## Bản Đồ Quyết Định

Bốn cách xử lý, và chúng không tương đương nhau:

| Cách | Khi nào dùng | Khi nào sai | Hậu quả nếu chọn nhầm |
|---|---|---|---|
| Tổng hợp trước rồi join | cần số đo từ bảng nhiều-dòng | hầu như không bao giờ sai | — |
| `EXISTS` / `IN` | chỉ cần lọc, không lấy cột nào | khi cần cột từ bảng phải | phải viết lại |
| Khử trùng bằng `ROW_NUMBER()` | cần đúng một dòng đại diện | khi mọi dòng đều mang thông tin | mất dữ liệu thật, âm thầm |
| `SUM(DISTINCT ...)` | gần như không bao giờ | khi hai dòng khác nhau tình cờ cùng giá trị | mất một dòng hợp lệ |

Dòng cuối đáng cảnh báo riêng. `SUM(DISTINCT amount)` nghe như một cách chữa fan-out, nhưng nó loại bỏ các giá trị **bằng nhau** chứ không loại bỏ các bản sao. Hai đơn khác nhau cùng trị giá 500.000 đồng sẽ bị tính thành một. Cách này biến một lỗi thổi phồng thành một lỗi thiếu hụt, và lỗi thiếu hụt còn khó phát hiện hơn.

Dòng thứ ba cũng cần tỉnh táo. `ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY paid_at) = 1` giữ lần thu tiền đầu tiên — hợp lý nếu câu hỏi là "khi nào đơn được thanh toán lần đầu", nhưng sai nếu câu hỏi là "đơn thu được bao nhiêu tiền". Kỹ thuật khử trùng đúng phụ thuộc vào câu hỏi, không phải vào hình dạng dữ liệu.

## Case Study Thực Chiến: xu hướng doanh thu dốc lên nhờ trả góp

Lược đồ tối thiểu:

```
orders   (order_id, ordered_at, gross_amount)
payments (payment_id, order_id, paid_at, amount)
```

Báo cáo quý đang chạy truy vấn này:

```sql
SELECT DATE_TRUNC('quarter', o.ordered_at) AS quy,
       SUM(o.gross_amount) AS doanh_thu
FROM orders o
JOIN payments p ON p.order_id = o.order_id
GROUP BY 1 ORDER BY 1;
```

Bốn quý cho ra mức tăng 6%, 9%, 14%, 19%. Trông như tăng trưởng gia tốc.

Đo lại hệ số fan-out theo từng quý:

```sql
SELECT DATE_TRUNC('quarter', o.ordered_at) AS quy,
       COUNT(*) * 1.0 / COUNT(DISTINCT o.order_id) AS he_so_nhan
FROM orders o
JOIN payments p ON p.order_id = o.order_id
GROUP BY 1 ORDER BY 1;
```

Hệ số ra lần lượt 1,04 / 1,09 / 1,15 / 1,22. Toàn bộ phần "gia tốc" là tỉ lệ đơn trả góp tăng lên, không phải doanh thu. Doanh thu thật, tính lại bằng `EXISTS`, gần như đi ngang.

**Biến thể khó hơn, nơi cách hiểu trên gây hiểu lầm.** Bây giờ đổi câu hỏi: "tiền thực thu theo quý". Ở đây `SUM(p.amount)` trên chính bảng đã join là **đúng** — mỗi dòng payment đóng góp số tiền của riêng nó, không có bản sao nào. Cùng một phép join gây fan-out cho cột này và không gây cho cột kia.

Quy tắc rút ra: fan-out không phải thuộc tính của phép join, mà là quan hệ giữa phép join và **cột đang được tổng hợp**. Cột thuộc bảng bị nhân thì an toàn; cột thuộc bảng bị nhân *bởi* bảng kia thì không. Cùng một truy vấn vì thế có thể vừa đúng vừa sai, tùy cột bạn nhìn.

Và bẫy cuối trong biến thể ấy: `ordered_at` là ngày đặt, `paid_at` là ngày thu. Tiền thực thu quý IV của đơn đặt quý III thuộc về quý nào? Câu trả lời phụ thuộc câu hỏi kinh doanh, và không có cách viết SQL nào chọn hộ bạn.

## Góc Khuất & Ngộ Nhận

Về hiệu năng, fan-out làm phình bảng trung gian trước khi `GROUP BY` gom lại, nên chi phí bộ nhớ và spill ra đĩa tăng theo hệ số nhân chứ không theo kích thước kết quả. Một truy vấn trả về 12 dòng vẫn có thể sập vì bảng giữa có 400 triệu dòng. Suy luận "kết quả nhỏ nên chắc nhanh" hỏng ở đúng chỗ này.

Fan-out cũng ẩn kỹ hơn khi đi qua nhiều tầng. Qua hai phép join nối tiếp, mỗi phép nhân trung bình 1,2 lần, hệ số tổng thành 1,44 — và không tầng nào trông đáng ngờ khi xét riêng.

**Hiểu lầm:** "Fan-out chỉ xảy ra với `LEFT JOIN`."
**Thực tế:** từ khóa không liên quan. `INNER JOIN` tới một bảng có khóa không duy nhất nhân dòng y hệt. **Vì sao nghe hợp lý:** `LEFT JOIN` hay được dùng để nối bảng chi tiết, nên người ta gặp fan-out ở đó nhiều hơn — tương quan bị nhớ thành nhân quả.

**Hiểu lầm:** "Đếm dòng trước và sau join là đủ để yên tâm."
**Thực tế:** số dòng bằng nhau không loại trừ fan-out. Với 100 dòng trái mà 20 dòng khớp 2 lần và 20 dòng không khớp trong một `INNER JOIN`, kết quả vẫn là 100 dòng — nhưng 20 dòng đã bị nhân đôi và 20 dòng đã biến mất. **Vì sao nghe hợp lý:** phép đếm bắt được đa số trường hợp, và đa số không phải tất cả.

**Hiểu lầm:** "Khóa ngoại đảm bảo không có fan-out."
**Thực tế:** khóa ngoại đảm bảo giá trị tồn tại ở bảng cha, không đảm bảo tính duy nhất ở bảng con. `payments.order_id` là khóa ngoại hợp lệ và vẫn lặp lại nhiều lần — đó chính là ý nghĩa của quan hệ một-nhiều. **Vì sao nghe hợp lý:** cả hai đều là ràng buộc toàn vẹn, và người học gộp chúng làm một.

## Nếu Bạn Dạy Lại Điều Này...

Mở đầu bằng biểu đồ bốn quý với xu hướng dốc lên, hỏi học viên nó nói lên điều gì, để họ diễn giải một lúc. Sau đó chiếu hệ số fan-out theo quý bên cạnh. Sự im lặng lúc ấy dạy nhiều hơn bất kỳ định nghĩa nào.

Hạt giống bài tập: đưa hai truy vấn trên cùng bảng, một tổng `gross_amount` và một tổng `amount`, cùng một phép join. Yêu cầu chỉ ra cái nào bị fan-out và giải thích tại sao cái kia không.

## Tự Kiểm Tra Nhanh

**1. `orders` có 1.000 dòng, `payments` có 1.300 dòng với 1.000 `order_id` phân biệt. `INNER JOIN` cho bao nhiêu dòng, và `SUM(gross_amount)` sai bao nhiêu?**

<details><summary>Đáp án</summary>

1.300 dòng. `SUM(gross_amount)` bị thổi thêm 300 lần cộng — nhưng mức sai lệch theo tiền phụ thuộc giá trị của đúng những đơn bị nhân, không phải 30%. Phải đo bằng tiền chứ không suy từ số dòng.
</details>

**2. Vì sao `SUM(DISTINCT amount)` là cách chữa tệ hơn cả bệnh?**

<details><summary>Đáp án</summary>

Nó loại các giá trị bằng nhau chứ không loại các bản sao. Hai giao dịch thật cùng trị giá bị tính thành một, biến lỗi thổi phồng thành lỗi thiếu hụt — khó phát hiện hơn vì không ai nghi ngờ một con số nhỏ hơn kỳ vọng.
</details>

**3. Cùng một phép join, vì sao `SUM(o.gross_amount)` sai mà `SUM(p.amount)` đúng?**

<details><summary>Đáp án</summary>

Bảng `orders` bị nhân bởi `payments`, nên cột của `orders` xuất hiện lặp. Cột của `payments` thì mỗi dòng là một bản ghi riêng, không có bản sao nào. Fan-out là quan hệ giữa phép join và cột được tổng hợp, không phải thuộc tính của phép join.
</details>

Ghi chú tiếp theo là [Phép toán tập hợp](sql.set-operations.md), nơi việc ghép bảng diễn ra theo chiều dọc và bài toán trùng lặp mang một hình dạng khác.
