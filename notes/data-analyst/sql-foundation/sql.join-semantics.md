---
id: data-analyst.sql.join-semantics
title: Join semantics
domain: data-analyst
type: mechanism
tags: [sql, sql-foundation, join, semantics]
status: draft
ai_summary: Which rows survive a join and how many copies each produces is decided by key cardinality on the join columns, not by the join keyword.
relationships:
  builds_on: []
  prerequisite_of: [data-analyst.sql.fan-out]
  commonly_confused_with: [data-analyst.sql.grain]
created: 2026-09-01
updated: 2026-09-01
version_sensitive: false
---

# Join semantics

**Tóm tắt bản chất:** Từ khóa join quyết định dòng nào **được giữ** khi không khớp. Số bản sao mỗi dòng sinh ra thì do lực lượng khóa trên cột join quyết định, và hai chuyện đó độc lập nhau. Đọc `LEFT` hay `INNER` không cho biết kết quả có bao nhiêu dòng.

## Nỗi Đau & Động Lực

Người ta học join qua biểu đồ Venn. Hai hình tròn, phần giao là `INNER`, cả hình tròn trái là `LEFT`. Biểu đồ ấy đúng về tập hợp và sai về bảng, vì tập hợp không có phần tử lặp còn bảng thì có. Nó không có chỗ nào để biểu diễn việc một dòng bên trái khớp với ba dòng bên phải và trở thành ba dòng.

Hậu quả cụ thể: một người viết `LEFT JOIN` vì được dạy rằng nó "an toàn hơn", chạy xong thấy kết quả nhiều dòng hơn bảng gốc, và kết luận rằng dữ liệu bị trùng lặp. Họ thêm `DISTINCT`. Bây giờ số dòng trông đúng, còn tổng tiền thì vẫn sai — vì `DISTINCT` chỉ gộp các dòng giống hệt nhau, và ba lần thu tiền khác nhau của cùng một đơn không giống hệt nhau.

Chi phí thật là ở chỗ người đó vẫn không biết vì sao. Lần sau gặp lại, họ lại thêm `DISTINCT`. Mô hình sai vẫn hoạt động đủ tốt để không bị bác bỏ, và đó là loại mô hình sai sống lâu nhất.

## Cơ Chế Tác Động

Một phép join thực hiện hai việc tách biệt, theo thứ tự này:

**Bước một — ghép cặp.** Với mỗi dòng bên trái, tìm mọi dòng bên phải thỏa điều kiện `ON`. Tìm được `k` dòng thì sinh ra `k` dòng kết quả; `k = 0` thì chưa sinh ra gì.

**Bước hai — xử lý phần không khớp.** Đây, và chỉ ở đây, từ khóa mới có tác dụng:

| Từ khóa | Dòng trái không khớp | Dòng phải không khớp |
|---|---|---|
| `INNER` | bỏ | bỏ |
| `LEFT` | giữ, cột phải là `NULL` | bỏ |
| `RIGHT` | bỏ | giữ, cột trái là `NULL` |
| `FULL` | giữ | giữ |

Chú ý bảng này không có cột nào nói về `k > 1`. Việc nhân bản đã xong ở bước một, trước khi từ khóa được xét đến. Đó là lý do `LEFT JOIN` và `INNER JOIN` cho ra số dòng **bằng nhau** trên phần dữ liệu khớp, và chỉ khác nhau ở phần không khớp.

Công thức số dòng, viết ra một lần cho rõ:

```
số dòng kết quả = Σ (với mỗi dòng trái) số dòng phải khớp
                + số dòng trái không khớp   (nếu LEFT hoặc FULL)
                + số dòng phải không khớp   (nếu RIGHT hoặc FULL)
```

Kiểm tra lực lượng trước khi viết join, bằng một truy vấn duy nhất trên bảng phải:

```sql
SELECT COUNT(*) AS tong_dong,
       COUNT(DISTINCT order_id) AS so_khoa
FROM payments;
```

Bằng nhau nghĩa là khóa duy nhất và join giữ nguyên grain. Khác nhau nghĩa là join sẽ nhân, với tỉ số giữa chúng chính là hệ số nhân trung bình.

## Bản Đồ Quyết Định

Từ khóa được chọn theo câu hỏi "dòng không khớp có thuộc về câu trả lời không", chứ không theo thói quen:

| Câu hỏi kinh doanh | Từ khóa | Vì sao |
|---|---|---|
| "Khách hàng nào đã mua?" | `INNER` | khách chưa mua không thuộc câu trả lời |
| "Mỗi khách hàng mua bao nhiêu, kể cả chưa mua?" | `LEFT` | số 0 là một câu trả lời hợp lệ |
| "Đơn nào có bản ghi thanh toán?" | `EXISTS` | chỉ cần lọc, không cần cột nào từ bảng phải |
| "Có bản ghi nào mồ côi ở cả hai phía không?" | `FULL` | kiểm toán toàn vẹn |
| "Đơn nào **không** có thanh toán?" | `LEFT` + `WHERE p.order_id IS NULL` | mẫu anti-join |

Dòng thứ ba đáng nhấn. Nếu bạn join chỉ để lọc và không lấy cột nào từ bảng phải, `EXISTS` là lựa chọn đúng — nó không nhân dòng và bộ tối ưu có thể dừng ở bản ghi khớp đầu tiên. Dùng `JOIN` cho việc này là nguyên nhân phổ biến nhất của grain bị đổi ngoài ý muốn.

Hậu quả của việc chọn sai không đối xứng. Lấy `INNER` khi cần `LEFT` thì mất dòng — dễ phát hiện, vì tổng nhỏ đi và ai đó sẽ hỏi. Chọn `JOIN` khi cần `EXISTS` làm thừa dòng — khó phát hiện, vì tổng lớn lên và số lớn ít khi bị nghi ngờ.

## Case Study Thực Chiến: danh sách khách hàng dài hơn bảng khách hàng

Lược đồ tối thiểu:

```
customers (customer_id, country, segment)
orders    (order_id, customer_id, gross_amount)
```

Yêu cầu: danh sách khách hàng kèm tổng chi tiêu, giữ cả khách chưa mua gì.

```sql
SELECT c.customer_id, c.country, SUM(o.gross_amount) AS tong_chi
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.country;
```

Truy vấn này **đúng**, và đây là điểm cần thấy: bảng trung gian sau join có số dòng bằng tổng số đơn hàng, không phải tổng số khách — mỗi khách có bao nhiêu đơn thì bấy nhiêu dòng — nhưng `GROUP BY` đưa grain trở về mức khách hàng trước khi kết quả ra ngoài. Nhân bản ở giữa không phải lỗi khi nó được gom lại.

Khách chưa mua có `o.gross_amount` là `NULL`, và `SUM` bỏ qua `NULL`, nên `tong_chi` của họ là `NULL` chứ không phải `0`. Báo cáo cần số `0` thì bọc `COALESCE(SUM(o.gross_amount), 0)` — và đây là chỗ ghi chú về `NULL` gặp lại ghi chú này.

**Biến thể khó hơn, nơi cách hiểu trên gây hiểu lầm.** Thêm một yêu cầu: kèm cả tổng tiền đã hoàn.

```sql
SELECT c.customer_id,
       SUM(o.gross_amount) AS tong_chi,
       SUM(r.amount)       AS tong_hoan
FROM customers c
LEFT JOIN orders  o ON o.customer_id = c.customer_id
LEFT JOIN refunds r ON r.order_id    = o.order_id
GROUP BY c.customer_id;
```

Bây giờ cả hai con số đều sai. Khách có 2 đơn, mỗi đơn 1 lần hoàn: sau join thứ hai có 2 dòng, `tong_chi` vẫn đúng. Nhưng khách có 1 đơn với 3 lần hoàn: 3 dòng, và `gross_amount` của đơn ấy được cộng 3 lần. Hai phép join nối tiếp nhau nhân chồng lên nhau.

Cách sửa không phải là `DISTINCT`. Tổng hợp từng nhánh về grain khách hàng **trước** rồi mới ghép:

```sql
WITH chi AS (
  SELECT customer_id, SUM(gross_amount) AS tong_chi
  FROM orders GROUP BY customer_id
), hoan AS (
  SELECT o.customer_id, SUM(r.amount) AS tong_hoan
  FROM refunds r JOIN orders o ON o.order_id = r.order_id
  GROUP BY o.customer_id
)
SELECT c.customer_id, chi.tong_chi, hoan.tong_hoan
FROM customers c
LEFT JOIN chi  ON chi.customer_id  = c.customer_id
LEFT JOIN hoan ON hoan.customer_id = c.customer_id;
```

Bây giờ cả `chi` và `hoan` đều có khóa duy nhất là `customer_id`, nên hai phép join cuối không nhân gì cả. Quy tắc rút ra: khi cần nhiều số đo từ nhiều bảng con, đưa từng số đo về grain đích trước khi ghép, đừng ghép trước rồi mới tổng hợp.

## Góc Khuất & Ngộ Nhận

Về hiệu năng, thứ tự join do bộ tối ưu chọn chứ không do thứ tự bạn viết, trừ khi bảng quá nhiều và bộ tối ưu bỏ cuộc tìm kiếm. Nhưng dạng truy vấn thì bạn kiểm soát: gom trước rồi join xử lý ít dòng hơn hẳn join rồi mới gom, và chênh lệch tăng theo hệ số nhân. Trên vài nghìn dòng hai cách như nhau; trên vài trăm triệu dòng một cách không chạy nổi.

Điều kiện `ON` với hàm bọc quanh cột — `ON UPPER(a.ma) = UPPER(b.ma)` — thường vô hiệu hóa chỉ mục và biến hash join thành quét toàn bảng. Cần chuẩn hóa để ghép thì làm lúc nạp dữ liệu, không phải lúc truy vấn.

**Hiểu lầm:** "`LEFT JOIN` không bao giờ làm mất dòng."
**Thực tế:** nó không làm mất ở bước join, nhưng một điều kiện trên bảng phải đặt trong `WHERE` sẽ loại các dòng có cột phải là `NULL`, tức là đúng những dòng không khớp mà `LEFT` vừa giữ lại. Kết quả tương đương `INNER JOIN`. **Vì sao nghe hợp lý:** lời hứa của `LEFT` là thật — chỉ là nó hết hiệu lực ở mệnh đề tiếp theo.

**Hiểu lầm:** "Nhiều dòng hơn sau join nghĩa là dữ liệu bẩn."
**Thực tế:** một đơn có ba lần thu tiền là dữ liệu hoàn toàn đúng. Việc nhân dòng là hệ quả của lực lượng khóa, không phải triệu chứng chất lượng. **Vì sao nghe hợp lý:** trong nhiều bài học nhập môn, các bảng ví dụ đều 1:1 và nhân bản chỉ xuất hiện khi có lỗi thật.

**Hiểu lầm:** "`JOIN` và `EXISTS` chỉ khác nhau về cách viết."
**Thực tế:** `JOIN` nhân dòng theo số bản ghi khớp, `EXISTS` không nhân dòng nào. Chúng cho cùng kết quả **chỉ khi** bảng phải có khóa duy nhất trên cột ghép. **Vì sao nghe hợp lý:** trong trường hợp 1:1 — trường hợp người ta thử nghiệm — hai cách thật sự tương đương.

## Nếu Bạn Dạy Lại Điều Này...

Mở đầu bằng cách xóa biểu đồ Venn khỏi bảng và thay bằng hai bảng nhỏ trên giấy: bảng trái 2 dòng, bảng phải 3 dòng trong đó 2 dòng cùng khóa. Yêu cầu học viên viết tay kết quả `INNER JOIN`. Ai đếm ra 3 dòng đã hiểu; ai đếm ra 2 vẫn đang nghĩ bằng tập hợp.

Hạt giống bài tập: cho một truy vấn hai tầng `LEFT JOIN` như biến thể ở trên, cùng kết quả sai, và yêu cầu chỉ ra hệ số nhân của từng khách hàng trước khi sửa.

## Tự Kiểm Tra Nhanh

**1. Bảng trái 100 dòng, bảng phải 50 dòng, mọi dòng trái đều khớp đúng 1 dòng phải. `LEFT JOIN` cho bao nhiêu dòng?**

<details><summary>Đáp án</summary>

100. Mỗi dòng trái khớp đúng một lần nên không có nhân bản, và không có dòng trái nào không khớp nên `LEFT` không thêm gì. 50 dòng phải không được dùng tới là chuyện bình thường — một dòng phải có thể khớp nhiều dòng trái, hoặc không khớp dòng nào.
</details>

**2. Vì sao `SELECT DISTINCT` không sửa được lỗi tổng tiền sau join nhân bản?**

<details><summary>Đáp án</summary>

`DISTINCT` chỉ gộp các dòng giống nhau ở mọi cột được chọn. Ba lần thu tiền của một đơn khác nhau ở `payment_id`, `paid_at` và `amount`, nên chúng không phải dòng trùng. Ngay cả khi bạn không chọn các cột đó, `DISTINCT` chạy **sau** khi tổng hợp trong nhiều trường hợp, nên số đã hỏng từ trước.
</details>

**3. Khi nào `JOIN` và `EXISTS` cho kết quả khác nhau?**

<details><summary>Đáp án</summary>

Khi bảng phải có nhiều hơn một dòng khớp cho một dòng trái. `JOIN` sinh ra một dòng cho mỗi lần khớp; `EXISTS` giữ đúng một dòng trái. Nếu khóa ghép là duy nhất ở bảng phải thì hai cách tương đương.
</details>

Ghi chú tiếp theo là [Join fan-out](sql.fan-out.md), nơi việc nhân bản này được đặt tên và đo bằng con số.
