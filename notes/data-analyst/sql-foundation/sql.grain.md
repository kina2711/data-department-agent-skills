---
id: data-analyst.sql.grain
title: Grain
domain: data-analyst
type: mechanism
tags: [sql, sql-foundation, grain]
status: draft
ai_summary: Grain is the sentence stating what exactly one row of a table represents; every aggregate is correct only relative to a declared grain, and joins change it.
relationships:
  builds_on: []
  prerequisite_of: [data-analyst.sql.aggregation-grain-error]
  commonly_confused_with: [data-analyst.sql.join-semantics]
created: 2026-09-01
updated: 2026-09-01
version_sensitive: false
---

# Grain

**Tóm tắt bản chất:** Grain là câu trả lời cho "một dòng của bảng này là gì", viết ra thành một câu hoàn chỉnh. Mọi phép tổng hợp chỉ đúng khi đối chiếu với grain đã tuyên bố, và mọi phép join đều có khả năng đổi grain mà không báo lỗi.

## Nỗi Đau & Động Lực

Con số sai không đến từ cú pháp sai. Cú pháp sai thì cơ sở dữ liệu từ chối chạy, bạn sửa trong ba mươi giây. Con số sai đến từ một truy vấn chạy thành công, trả về một bảng gọn gàng, và không dòng nào trong đó có nghĩa như bạn tưởng.

Tình huống điển hình: doanh thu tháng báo cáo cao hơn thực tế 18%. Truy vấn không có lỗi cú pháp, không có cột nào để trống, tổng tiền khớp với định dạng tiền tệ. Sai ở chỗ bảng đầu vào đã bị join với `payments`, và một đơn trả góp ba lần xuất hiện ba dòng. `SUM(gross_amount)` cộng số tiền của đơn đó ba lần. Không có gì trong SQL cảnh báo điều này, vì với cơ sở dữ liệu thì cộng ba dòng giống nhau là một việc hoàn toàn hợp lệ.

Cái giá không nằm ở con số. Nó nằm ở chỗ con số ấy đã đi vào một cuộc họp, một quyết định ngân sách đã dựa vào nó, và khi phát hiện thì phải giải thích tại sao báo cáo tháng trước cũng sai theo cùng cách. Grain là thứ duy nhất bắt được lỗi này trước khi truy vấn chạy, bởi nó buộc bạn phát biểu ra điều bạn đang ngầm giả định.

## Cơ Chế Tác Động

Grain là một câu, không phải một danh sách cột. Viết đúng dạng: *"Một dòng của `payments` là một lần thu tiền cho một đơn hàng."* Không phải *"payments có order_id và amount"* — đó là mô tả cấu trúc, không nói được điều gì về nghĩa.

Kiểm tra grain đã viết đúng chưa bằng một phép thử máy móc:

```sql
SELECT order_id, COUNT(*) AS n
FROM payments
GROUP BY order_id
HAVING COUNT(*) > 1
LIMIT 5;
```

Nếu bạn tin grain là "một dòng cho một đơn hàng" mà truy vấn này trả về dòng nào, grain bạn tin là sai. Đây không phải kiểm tra chất lượng dữ liệu — dữ liệu hoàn toàn bình thường — mà là kiểm tra giả định của bạn về dữ liệu.

Thứ tự cần nhớ khi grain đổi trong một truy vấn:

1. `FROM` đặt grain ban đầu bằng grain của bảng gốc.
2. Mỗi `JOIN` có thể nhân grain lên, tùy số bản ghi khớp ở vế bên kia. Join tới bảng có khóa duy nhất trên cột join thì giữ nguyên grain; join tới bảng không duy nhất thì nhân lên.
3. `WHERE` lọc dòng nhưng không đổi grain.
4. `GROUP BY` đặt lại grain thành đúng tổ hợp cột trong mệnh đề đó. Sau `GROUP BY customer_id`, một dòng là một khách hàng — bất kể trước đó là gì.
5. Hàm cửa sổ **không** đổi grain; chúng thêm cột vào grain hiện hành.

Điểm 5 là chỗ nhiều người trượt: `SUM(...) OVER (PARTITION BY customer_id)` trông giống tổng hợp nhưng không gộp dòng nào cả.

## Bản Đồ Quyết Định

Trước khi viết `SUM`, `COUNT` hay `AVG`, trả lời hai câu hỏi theo thứ tự:

| Grain hiện tại của nguồn | Grain bạn cần cho kết quả | Việc phải làm | Hậu quả nếu bỏ qua |
|---|---|---|---|
| bằng nhau | bằng nhau | tổng hợp trực tiếp | — |
| mịn hơn kết quả | thô hơn | `GROUP BY` về grain đích | không có; đây là đường đúng |
| thô hơn kết quả | mịn hơn | join thêm bảng chi tiết, chấp nhận grain đổi | nếu tổng hợp sau đó mà quên, số bị thổi lên |
| đã bị join làm nhân lên | bất kỳ | khử trùng lặp **trước** khi tổng hợp, hoặc tổng hợp riêng từng nhánh rồi mới ghép | số bị thổi lên theo bội số nhân, âm thầm |

Dòng cuối là dòng đắt nhất. Cách khử phổ biến nhất là tổng hợp từng nhánh về cùng grain trước khi join, chứ không phải join trước rồi mới chữa bằng `DISTINCT`. `DISTINCT` chỉ loại được dòng trùng hoàn toàn; hai lần thu tiền khác nhau của cùng một đơn không phải dòng trùng, nên `DISTINCT` không chạm tới chúng.

## Case Study Thực Chiến: doanh thu tháng bị thổi 18%

Lược đồ tối thiểu cho tình huống này:

```
orders   (order_id, customer_id, ordered_at, gross_amount)
payments (payment_id, order_id, paid_at, amount)
```

Truy vấn đã chạy trong báo cáo:

```sql
SELECT DATE_TRUNC('month', o.ordered_at) AS thang,
       SUM(o.gross_amount) AS doanh_thu
FROM orders o
JOIN payments p ON p.order_id = o.order_id
WHERE p.paid_at IS NOT NULL
GROUP BY 1;
```

Người viết thêm `JOIN payments` để loại các đơn chưa thanh toán. Ý định đúng, hệ quả sai: sau join, grain không còn là một-dòng-một-đơn mà là một-dòng-một-lần-thu-tiền. Đơn trả góp ba kỳ đóng góp `gross_amount` ba lần. 18% chênh lệch chính là tỉ trọng đơn trả góp trong tháng đó.

Sửa bằng cách giữ grain ở mức đơn hàng, dùng `EXISTS` thay vì join:

```sql
SELECT DATE_TRUNC('month', o.ordered_at) AS thang,
       SUM(o.gross_amount) AS doanh_thu
FROM orders o
WHERE EXISTS (SELECT 1 FROM payments p
              WHERE p.order_id = o.order_id AND p.paid_at IS NOT NULL)
GROUP BY 1;
```

`EXISTS` lọc mà không nhân, nên grain đứng yên.

**Biến thể khó hơn, nơi cách hiểu trên gây hiểu lầm.** Giả sử câu hỏi đổi thành "doanh thu đã thực thu theo tháng". Bây giờ `SUM(p.amount)` trên bảng đã join lại **đúng**, vì mỗi dòng payment đóng góp đúng số tiền của chính nó, và grain một-dòng-một-lần-thu chính là grain phù hợp với câu hỏi. Cùng một phép join, cùng một bảng, một lần sai một lần đúng — khác nhau ở chỗ cột được tổng hợp thuộc về grain nào. Quy tắc rút ra: chỉ tổng hợp cột thuộc về grain hiện hành. `gross_amount` thuộc grain đơn hàng, `amount` thuộc grain lần thu tiền.

Và một cái bẫy nữa nằm trong biến thể ấy: `DATE_TRUNC('month', o.ordered_at)` gán tiền thực thu vào tháng **đặt hàng**, không phải tháng thu tiền. Với đơn trả góp, hai tháng đó khác nhau. Grain đúng nhưng chiều thời gian sai vẫn ra báo cáo sai.

## Góc Khuất & Ngộ Nhận

Về hiệu năng, một truy vấn giữ đúng grain thường nhanh hơn hẳn truy vấn phải chữa cháy sau join: tổng hợp trước rồi join xử lý ít dòng hơn nhiều, và `EXISTS` cho phép bộ tối ưu dừng ngay khi tìm thấy một bản ghi khớp thay vì vật chất hóa toàn bộ kết quả join. Chênh lệch này lớn dần theo bội số nhân, nên trên bảng nhỏ hai cách gần như nhau và trên bảng lớn thì một cách không chạy nổi.

**Hiểu lầm:** "Thêm `DISTINCT` là an toàn."
**Thực tế:** `DISTINCT` chỉ gộp các dòng giống nhau ở mọi cột được chọn. Nếu bạn chọn `order_id, gross_amount` thì ba lần thu tiền của một đơn cho ra ba dòng y hệt và `DISTINCT` gộp lại được — nhưng chỉ vì bạn tình cờ không chọn cột nào phân biệt chúng. Chọn thêm `payment_id` là `DISTINCT` mất tác dụng ngay. **Vì sao nghe hợp lý:** trong đa số ví dụ nhỏ nó có vẻ hiệu quả, và người ta ghi nhớ kết quả chứ không ghi nhớ điều kiện khiến nó hiệu quả.

**Hiểu lầm:** "Grain là khóa chính."
**Thực tế:** khóa chính đảm bảo tính duy nhất, grain phát biểu ý nghĩa. Chúng trùng nhau ở bảng nguồn nhưng tách nhau ngay khi có truy vấn. Kết quả của một `GROUP BY` có grain rõ ràng mà không có khóa chính nào cả. Ngược lại, một bảng có khóa chính tổng hợp `(order_id, payment_id)` vẫn cần bạn nói ra một dòng nghĩa là gì. Ngộ nhận này nghe hợp lý vì ở bảng chuẩn hóa tốt hai khái niệm thường trùng, nên người học rút ra quy tắc từ trường hợp riêng.

**Hiểu lầm:** "`LEFT JOIN` an toàn hơn `INNER JOIN` về mặt grain."
**Thực tế:** `LEFT JOIN` bảo toàn dòng bên trái khi không khớp, nhưng khi có khớp nhiều thì nhân lên y hệt `INNER JOIN`. Nó bảo vệ bạn khỏi mất dòng, không bảo vệ khỏi thừa dòng. **Vì sao nghe hợp lý:** "left" gợi cảm giác vế trái được giữ nguyên, mà giữ nguyên tập hợp không có nghĩa là giữ nguyên số lượng.

## Nếu Bạn Dạy Lại Điều Này...

Mở đầu bằng cách đưa học viên một truy vấn đã chạy xong và một con số, rồi hỏi: "Một dòng trong bảng này là gì?" Phần lớn sẽ mô tả các cột thay vì trả lời câu hỏi. Khoảng lặng ngay sau đó là lúc khái niệm bám vào.

Hạt giống bài tập: cho hai truy vấn cùng trả về một cột `doanh_thu`, chênh nhau 18%, không nói cái nào đúng. Yêu cầu viết grain của bảng trung gian trong mỗi truy vấn thành một câu, rồi mới kết luận.

## Tự Kiểm Tra Nhanh

**1. Sau `GROUP BY customer_id, DATE_TRUNC('month', ordered_at)`, một dòng của kết quả là gì?**

<details><summary>Đáp án</summary>

Một khách hàng trong một tháng. Grain của kết quả `GROUP BY` luôn là đúng tổ hợp các biểu thức trong mệnh đề đó, không phụ thuộc grain của bảng nguồn.
</details>

**2. `orders` join `refunds` bằng `order_id`, rồi `SUM(orders.gross_amount)`. Khi nào kết quả đúng?**

<details><summary>Đáp án</summary>

Chỉ khi mỗi đơn có nhiều nhất một bản ghi hoàn tiền. Vì `refunds.order_id` không duy nhất theo lược đồ, đơn hoàn hai lần sẽ được cộng `gross_amount` hai lần. Kiểm tra bằng `GROUP BY order_id HAVING COUNT(*) > 1` trên `refunds` trước khi tin kết quả.
</details>

**3. Hàm cửa sổ có đổi grain không?**

<details><summary>Đáp án</summary>

Không. `SUM(...) OVER (...)` thêm một cột vào từng dòng và giữ nguyên số dòng. Nó trông giống tổng hợp vì dùng cùng tên hàm, nhưng không có dòng nào bị gộp.
</details>

Ghi chú tiếp theo là [Lỗi tổng hợp sai grain](../sql-analysis/sql.aggregation-grain-error.md), nơi grain sai không còn là giả định mà đã thành con số trong báo cáo.
