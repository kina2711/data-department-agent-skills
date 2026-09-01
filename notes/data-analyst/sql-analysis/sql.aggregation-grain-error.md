---
id: data-analyst.sql.aggregation-grain-error
title: Aggregation grain error
domain: data-analyst
type: pitfall
tags: [sql, sql-analysis, aggregation, grain, error]
status: draft
ai_summary: Aggregating at a grain finer or coarser than the question asked produces a number that is arithmetically correct and answers nothing.
relationships:
  builds_on: [data-analyst.sql.grain, data-analyst.sql.window-function]
  prerequisite_of: []
  commonly_confused_with: [data-analyst.sql.fan-out]
created: 2026-09-01
updated: 2026-09-01
version_sensitive: false
---

# Aggregation grain error

**Tóm tắt bản chất:** Tổng hợp ở một grain khác với grain mà câu hỏi yêu cầu cho ra con số đúng về số học và không trả lời gì cả. Khác với fan-out, ở đây không có dòng nào bị nhân — mọi phép tính đều chính xác, chỉ có điều chúng đang tính một thứ khác.

## Nỗi Đau & Động Lực

Fan-out ít nhất còn để lại dấu vết: số dòng tăng, tổng phồng lên, ai đó tinh ý sẽ thấy. Lỗi grain trong tổng hợp không để lại gì. Chẳng dòng nào thừa hay thiếu, chẳng cảnh báo nào, và con số nằm gọn trong khoảng hợp lý.

Ví dụ kinh điển: "giá trị đơn hàng trung bình". Có ít nhất bốn con số khác nhau đều có quyền mang cái tên ấy — trung bình trên mỗi đơn, trung bình trên mỗi khách của trung bình đơn của họ, tổng doanh thu chia số khách, tổng doanh thu chia số đơn đã thanh toán. Bốn con số, bốn grain. Case study phía dưới cho thấy hai trong số đó lệch nhau 12% trên cùng một bảng, và ví dụ hai khách ở phần cơ chế đẩy mức lệch lên gần ba lần.

Cái giá nằm ở chỗ không ai phát hiện. Hai đội báo cáo "AOV" ở hai grain, lệch nhau 12%, và cuộc họp thành cuộc tranh luận xem số của ai đúng. Cả hai đều đúng. Chưa ai viết ra câu hỏi mà mình đang trả lời.

Trung bình của trung bình là dạng nguy hiểm nhất, vì nó **luôn** khác trung bình có trọng số trừ khi mọi nhóm cùng kích thước, và nó trông giống hệt một phép tính hợp lý.

## Cơ Chế Tác Động

Ba grain phải khớp nhau, và lỗi xảy ra khi bất kỳ cặp nào lệch:

1. **Grain của câu hỏi** — đơn vị mà kết luận nói về. "Mỗi khách chi bao nhiêu" có grain khách hàng.
2. **Grain của bảng nguồn** — một dòng là gì.
3. **Grain của phép tổng hợp** — tổ hợp cột trong `GROUP BY`.

Kiểm bằng cách viết ba câu ra giấy trước khi viết SQL. Nghe thủ công, nhưng chẳng công cụ nào bắt được lỗi này: cả ba trạng thái đều là SQL hợp lệ.

Chỗ khác biệt với fan-out, nói rõ một lần:

| | Fan-out | Lỗi grain khi tổng hợp |
|---|---|---|
| Số dòng | bị nhân lên | không đổi |
| Phép tính | cộng lặp cùng một giá trị | cộng đúng từng giá trị |
| Con số | sai về số học | đúng về số học |
| Dấu hiệu | tổng phồng bất thường | không có |
| Cách phát hiện | đếm dòng trước/sau join | viết grain của câu hỏi ra |

Dòng cuối là lý do lỗi này sống dai hơn. Fan-out có phép kiểm máy móc; lỗi grain chỉ có phép kiểm bằng ngôn ngữ.

Công thức cho dạng phổ biến nhất — trung bình của trung bình:

```
AVG(AVG(x))  ≠  AVG(x)   trừ khi mọi nhóm cùng kích thước
```

Lấy số cụ thể: khách A một đơn 10 triệu, khách B chín đơn mỗi đơn 1 triệu. Tính trên mỗi đơn ra 19/10 = 1,9 triệu; tính trung bình của trung bình theo khách ra (10 + 1)/2 = 5,5 triệu. Cùng một tập dữ liệu, chênh gần ba lần.

## Bản Đồ Quyết Định

| Câu hỏi thật sự | Grain kết quả | Viết |
|---|---|---|
| "một đơn trung bình bao nhiêu tiền" | đơn hàng | `AVG(gross_amount)` trên `orders` |
| "một khách trung bình chi bao nhiêu" | khách hàng | gom về khách trước, rồi `AVG` |
| "khách trung bình đặt đơn to cỡ nào" | khách hàng | `AVG` theo khách, rồi `AVG` lần nữa — có chủ đích |
| "doanh thu trên mỗi khách" | khách hàng | `SUM(all) / COUNT(DISTINCT customer_id)` |
| "tỉ lệ đơn được hoàn" | đơn hàng | đếm phân biệt ở cả tử và mẫu |

Dòng thứ ba tồn tại để nói rõ: trung bình của trung bình **không phải lúc nào cũng sai**. Nó sai khi bạn định hỏi câu ở dòng một và viết nhầm thành dòng ba. Khi câu hỏi thật sự là "khách điển hình đặt đơn cỡ nào", nó đúng — vì nó cho mỗi khách một phiếu bầu bằng nhau, bất kể họ đặt bao nhiêu đơn.

Hậu quả của chọn sai luôn cùng một hình dạng: con số hợp lý, không cảnh báo, và một quyết định dựa trên đơn vị sai. Phòng được nó chỉ bằng một cách: viết grain của kết luận ra trước khi gõ truy vấn.

Với tỉ lệ, thêm một quy tắc: **tử số và mẫu số phải cùng grain**. `COUNT(refund_id) / COUNT(*)` sau một join nhân bản vi phạm quy tắc này ngay cả khi cả hai con số đều "đúng" theo nghĩa số học.

## Case Study Thực Chiến: AOV lệch 12% giữa hai đội

Lược đồ tối thiểu:

```
orders (order_id, customer_id, gross_amount)
```

Đội A báo cáo:

```sql
SELECT AVG(gross_amount) AS aov FROM orders;   -- 1.870.000
```

Đội B báo cáo:

```sql
SELECT AVG(tong_khach) AS aov
FROM (SELECT customer_id, AVG(gross_amount) AS tong_khach
      FROM orders GROUP BY customer_id) t;      -- 2.094.000
```

Chênh 12%, và cả hai truy vấn đều không có lỗi. Đội A tính trung bình trên mỗi **đơn**; đội B tính trung bình trên mỗi **khách** của trung bình đơn của khách đó. Khách mua nhiều kéo con số của đội A xuống — vì họ đóng góp nhiều đơn nhỏ — trong khi ở đội B mỗi khách chỉ có một phiếu.

Chẳng con số nào sai. Sai ở chỗ cả hai cùng gọi nó là "AOV" mà bỏ qua grain, nên hai bảng điều khiển treo hai số dưới một nhãn.

Thuốc chữa nằm ngoài SQL: đặt tên theo grain. `aov_per_order` và `aov_per_customer` không thể nhầm lẫn với nhau, và cái tên buộc người viết phải quyết định grain trước khi gõ truy vấn.

**Biến thể khó hơn, nơi cách hiểu trên gây hiểu lầm.** Bây giờ thêm bộ lọc quốc gia và tính AOV theo từng nước:

```sql
SELECT c.country, AVG(o.gross_amount) AS aov_per_order
FROM orders o JOIN customers c USING (customer_id)
GROUP BY c.country;
```

Đúng grain, đúng tên. Nhưng nếu ai đó lấy trung bình của cột `aov_per_order` này để ra "AOV toàn cầu", họ vừa tạo ra một trung bình của trung bình mới: mỗi nước một phiếu, nên một nước có 40 đơn cân bằng với một nước có 400.000 đơn.

Lỗi grain có tính **lây lan**. Một bảng tổng hợp đúng ở grain của nó trở thành nguồn cho một tổng hợp sai ở tầng trên, và tầng trên không nhìn thấy dữ liệu gốc để nghi ngờ. Đây là lý do các bảng tổng hợp nên mang theo cột đếm — số đơn, số khách — để tầng sau còn có trọng số mà dùng.

## Góc Khuất & Ngộ Nhận

Về trung vị: không cộng dồn được. Trung vị của các trung vị theo nhóm không phải trung vị toàn bộ, và không có cột trọng số nào cứu được — phải tính lại từ dữ liệu chi tiết. Lý do ấy áp luôn cho phân vị và cho `COUNT(DISTINCT)`: tổng của các `COUNT(DISTINCT)` theo nhóm lớn hơn hoặc bằng `COUNT(DISTINCT)` toàn bộ, và bằng chỉ khi không phần tử nào xuất hiện ở hai nhóm.

Hệ quả thực tế: một bảng tổng hợp trước theo ngày không phục vụ được câu hỏi "bao nhiêu khách duy nhất trong tháng". Phải tính lại từ chi tiết, hoặc chấp nhận một cấu trúc xấp xỉ.

**Hiểu lầm:** "Con số hợp lý nghĩa là truy vấn đúng."
**Thực tế:** Lỗi grain sinh ra con số nằm đúng trong khoảng kỳ vọng — đó chính là điều làm nó nguy hiểm. Fan-out cho số vô lý và bị bắt; lỗi grain cho số hợp lý và đi vào báo cáo. **Vì sao nghe hợp lý:** kiểm tra tính hợp lý bắt được phần lớn lỗi, và người ta khái quát từ tỉ lệ thành công ấy.

**Hiểu lầm:** "`AVG` luôn là trung bình."
**Thực tế:** `AVG` là trung bình **của các dòng đang có mặt**, ở grain hiện hành, bỏ qua `NULL`. Ba điều kiện ấy đều có thể lệch khỏi ý định mà không có dấu hiệu nào. **Vì sao nghe hợp lý:** tên hàm là một từ tiếng Anh thông dụng, nên người ta gán cho nó nghĩa thông dụng thay vì nghĩa kỹ thuật.

**Hiểu lầm:** "Lỗi grain là một dạng của fan-out."
**Thực tế:** Chúng độc lập. Một truy vấn không có phép join nào vẫn mắc lỗi grain. Fan-out là chuyện số dòng, lỗi grain là chuyện đơn vị của kết luận. **Vì sao nghe hợp lý:** cả hai cho ra số sai và cả hai liên quan tới từ "grain", nên người học gộp chúng làm một chương.

## Nếu Bạn Dạy Lại Điều Này...

Mở đầu bằng cách đưa bốn truy vấn cùng nhãn "AOV" với bốn kết quả khác nhau, không nói cái nào đúng, và hỏi cái nào sai. Câu trả lời — không cái nào — là bài học.

Hạt giống bài tập: cho một bảng tổng hợp theo ngày và yêu cầu tính số khách duy nhất trong tháng từ nó. Học viên sẽ tìm ra rằng không làm được, và lý do là bài học thật.

## Tự Kiểm Tra Nhanh

**1. Khách A có 1 đơn 10 triệu, khách B có 9 đơn mỗi đơn 1 triệu. Hai cách tính AOV cho ra bao nhiêu?**

<details><summary>Đáp án</summary>

Trên mỗi đơn: 19 triệu chia 10 đơn bằng 1,9 triệu. Trên mỗi khách của trung bình đơn: (10 + 1) chia 2 bằng 5,5 triệu. Chênh gần ba lần, và cả hai đều đúng với câu hỏi riêng của nó.
</details>

**2. Vì sao không tính được số khách duy nhất trong tháng từ bảng đã tổng hợp theo ngày?**

<details><summary>Đáp án</summary>

`COUNT(DISTINCT)` không cộng dồn được. Một khách mua cả 30 ngày sẽ được đếm 30 lần khi cộng các con số ngày lại. Phải tính lại từ dữ liệu chi tiết, hoặc lưu một cấu trúc xấp xỉ hỗ trợ hợp nhất.
</details>

**3. Khác biệt cốt lõi giữa fan-out và lỗi grain khi tổng hợp?**

<details><summary>Đáp án</summary>

Fan-out làm sai số học vì cùng một giá trị bị cộng nhiều lần; số dòng thay đổi và có thể đếm được. Lỗi grain giữ số học hoàn toàn đúng và làm sai đơn vị của kết luận; không có dấu hiệu máy móc nào, chỉ phát hiện được bằng cách viết grain của câu hỏi ra thành lời.
</details>

Ghi chú tiếp theo mở module `analysis-method`, nơi câu hỏi được đặt trước khi có truy vấn nào.
