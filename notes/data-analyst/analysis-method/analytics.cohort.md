---
id: data-analyst.analytics.cohort
title: Cohort
domain: data-analyst
type: mechanism
tags: [analytics, analysis-method, cohort]
status: draft
ai_summary: A cohort groups users by when they started so behaviour is compared at the same age rather than on the same calendar date.
relationships:
  builds_on: [data-analyst.sql.grain]
  prerequisite_of: [data-analyst.analytics.retention-curve]
  commonly_confused_with: [data-analyst.analytics.survivorship-bias]
created: 2026-09-01
updated: 2026-09-01
version_sensitive: false
---

# Cohort

**Tóm tắt bản chất:** Cohort nhóm người dùng theo **thời điểm họ bắt đầu**, để so sánh hành vi ở cùng độ tuổi thay vì cùng ngày lịch. Nó tồn tại vì một chỉ số đo trên toàn bộ người dùng trộn lẫn hai thứ khác nhau: sản phẩm thay đổi thế nào, và thành phần người dùng thay đổi thế nào.

## Nỗi Đau & Động Lực

Tỉ lệ quay lại hàng tháng của sản phẩm giảm từ 42% xuống 31% trong sáu tháng. Đội sản phẩm kết luận trải nghiệm đang xấu đi và bắt đầu sửa. Sáu tháng sau nữa, con số vẫn giảm.

Nguyên nhân thật: một chiến dịch quảng cáo lớn đã kéo về lượng người dùng mới gấp bốn lần bình thường, và người dùng mới **luôn** có tỉ lệ quay lại thấp hơn người dùng cũ ở bất kỳ sản phẩm nào. Trải nghiệm không xấu đi chút nào. Thành phần người dùng đã đổi, và chỉ số tổng thể đo thành phần chứ không đo trải nghiệm.

Cái giá là sáu tháng công sức kỹ thuật đặt sai chỗ, cộng với một điều tệ hơn: đội ấy giờ tin rằng những thay đổi họ làm đã không hiệu quả, trong khi thực ra chưa ai đo được hiệu quả của chúng.

Chỉ số tổng thể trộn hai tín hiệu. Cohort tách chúng ra, và đó là toàn bộ lý do nó tồn tại.

## Cơ Chế Tác Động

Ba quyết định định nghĩa một cohort, và cả ba đều thay đổi kết luận:

**Một — mốc bắt đầu là gì.** Ngày đăng ký, ngày mua đầu tiên, ngày kích hoạt tính năng. Chúng cho ra ba bộ cohort khác nhau trên cùng dữ liệu, và không cái nào đúng sẵn. Chọn mốc gần nhất với sự kiện mà bạn muốn đo tác động.

**Hai — độ rộng của cohort.** Theo ngày, tuần, tháng, hay theo phiên bản sản phẩm. Cohort tháng mượt hơn nhưng che mất tác động của một thay đổi triển khai giữa tháng.

**Ba — trục thời gian là tuổi, không phải ngày.** Đây là phần cốt lõi. Cột không phải "tháng 1, tháng 2, tháng 3" mà là "tháng thứ 0, tháng thứ 1, tháng thứ 2 kể từ khi bắt đầu".

Cấu trúc truy vấn, ba tầng:

```sql
WITH cohort AS (
  SELECT customer_id,
         DATE_TRUNC('month', MIN(ordered_at)) AS thang_bat_dau
  FROM orders GROUP BY customer_id
), hoat_dong AS (
  SELECT o.customer_id, c.thang_bat_dau,
         DATE_TRUNC('month', o.ordered_at) AS thang_hoat_dong
  FROM orders o JOIN cohort c USING (customer_id)
  GROUP BY 1, 2, 3
)
SELECT thang_bat_dau,
       (EXTRACT(YEAR FROM thang_hoat_dong) - EXTRACT(YEAR FROM thang_bat_dau)) * 12
       + EXTRACT(MONTH FROM thang_hoat_dong) - EXTRACT(MONTH FROM thang_bat_dau) AS tuoi_thang,
       COUNT(DISTINCT customer_id) AS so_khach
FROM hoat_dong
GROUP BY 1, 2;
```

`GROUP BY 1, 2, 3` ở tầng giữa là bắt buộc: nó đưa grain về một-khách-một-tháng trước khi đếm, nếu không một khách đặt năm đơn trong tháng sẽ được đếm năm lần.

Kết quả là một bảng tam giác. Cohort tháng 1 có dữ liệu cho tuổi 0 đến 7; cohort tháng 7 chỉ có tuổi 0 và 1. Hình tam giác ấy không phải khuyết dữ liệu — nó là hệ quả tất yếu của việc cohort mới chưa sống đủ lâu.

## Bản Đồ Quyết Định

| Câu hỏi | Trục thời gian | Hậu quả nếu chọn nhầm |
|---|---|---|
| "trải nghiệm đang tốt lên hay xấu đi" | tuổi (cohort) | dùng ngày lịch thì đo thành phần người dùng |
| "tháng này công ty thế nào" | ngày lịch | dùng cohort thì không có con số duy nhất để báo cáo |
| "thay đổi tháng 3 có tác dụng không" | cohort theo phiên bản | cohort theo tháng làm loãng tác động |
| "khách hàng nào sắp rời bỏ" | không phải cohort | cohort mô tả nhóm, không dự đoán cá nhân |

Dòng cuối đáng nhấn mạnh. Cohort là công cụ mô tả, và một cohort có tỉ lệ giữ chân 20% không nói gì về việc một khách cụ thể trong đó có thuộc 20% ấy hay không.

Sai lầm phổ biến nhất trong bảng này là dòng đầu bị dùng ngược: báo cáo cho ban lãnh đạo cần một con số cho tháng, nên người ta lấy con số tổng thể, rồi diễn giải sự thay đổi của nó như thể nó là tín hiệu về sản phẩm. Hai việc — báo cáo và chẩn đoán — cần hai chỉ số khác nhau, và ép một chỉ số làm cả hai là gốc rễ của tình huống ở phần đầu.

## Case Study Thực Chiến: tỉ lệ quay lại giảm mà sản phẩm không xấu đi

Lược đồ tối thiểu:

```
orders (order_id, customer_id, ordered_at)
```

Chỉ số tổng thể theo tháng lịch:

```sql
SELECT DATE_TRUNC('month', ordered_at) AS thang,
       COUNT(DISTINCT customer_id) AS khach_hoat_dong
FROM orders GROUP BY 1;
```

Con số này trộn khách cũ và khách mới. Khi chiến dịch quảng cáo đổ về lượng khách mới gấp bốn, tỉ trọng khách mới trong mẫu tăng vọt, và vì khách mới quay lại ít hơn, tỉ lệ tổng thể giảm — dù mỗi nhóm khách riêng lẻ không đổi chút nào.

Tách theo cohort thì thấy ngay: cohort tháng 1 giữ 42% ở tuổi 1, cohort tháng 4 giữ 41%, cohort tháng 7 giữ 42%. Ba cohort, cùng một hành vi. Sản phẩm không đổi; chỉ có tỉ lệ pha trộn đổi.

**Biến thể khó hơn, nơi cách hiểu trên gây hiểu lầm.** Bây giờ cohort tháng 4 giữ 41% còn cohort tháng 7 giữ 35%, và đội kết luận sản phẩm đã xấu đi từ tháng 7.

Có thể đúng. Nhưng cũng có thể chiến dịch quảng cáo tháng 7 đưa về một loại khách khác hẳn — mua một lần vì giảm giá, không có ý định quay lại. Cohort đã tách được yếu tố thời gian, nhưng **không** tách được yếu tố kênh thu hút.

Muốn kết luận về sản phẩm thì phải cắt cohort theo kênh:

```sql
SELECT thang_bat_dau, kenh, tuoi_thang, COUNT(DISTINCT customer_id)
FROM hoat_dong JOIN customers USING (customer_id)
GROUP BY 1, 2, 3;
```

Quy tắc rút ra: cohort loại bỏ đúng một biến gây nhiễu — thời điểm bắt đầu. Mọi biến khác vẫn còn nguyên đó, và mỗi lần bạn thấy hai cohort khác nhau, câu hỏi tiếp theo luôn là "chúng còn khác nhau ở chỗ nào nữa".

## Góc Khuất & Ngộ Nhận

Cohort gần nhất luôn thiếu dữ liệu ở các tuổi lớn, và nếu đem vẽ chung một biểu đồ mà không đánh dấu, đường của nó sẽ rơi xuống 0 ở phía phải — trông y hệt một cohort tệ hại. Cắt bỏ các ô chưa đủ tuổi, đừng vẽ chúng như số 0.

Về kích thước mẫu: cắt cohort càng mịn thì mỗi ô càng ít người, và một cohort 30 người cho tỉ lệ nhảy 3,3% mỗi khi một người thay đổi. Bảng cohort trông rất thuyết phục ngay cả khi từng ô không có ý nghĩa thống kê, vì màu sắc của heatmap không biết đến kích thước mẫu.

**Hiểu lầm:** "Cohort nghĩa là nhóm theo đặc điểm."
**Thực tế:** Nhóm theo quốc gia hay theo gói dịch vụ là **phân khúc**, không phải cohort. Cohort đặc trưng ở chỗ trục thời gian là tuổi tính từ mốc bắt đầu. Hai kỹ thuật kết hợp được, nhưng chúng khác nhau. **Vì sao nghe hợp lý:** cả hai đều chia người dùng thành nhóm và cùng được gọi là "cắt dữ liệu", nên từ ngữ hằng ngày gộp chúng lại.

**Hiểu lầm:** "Cohort loại bỏ được yếu tố gây nhiễu."
**Thực tế:** Nó loại bỏ đúng một yếu tố — thời điểm bắt đầu. Kênh thu hút, giá đã trả, thiết bị, chiến dịch: tất cả vẫn còn. **Vì sao nghe hợp lý:** cohort giải quyết yếu tố gây nhiễu nổi bật nhất một cách rất gọn, và cảm giác "đã kiểm soát" lan sang những yếu tố chưa hề được chạm tới.

**Hiểu lầm:** "Bảng cohort càng chi tiết càng tốt."
**Thực tế:** Chia mịn làm mỗi ô nhỏ đi, và dưới một ngưỡng thì mỗi ô là nhiễu chứ không phải tín hiệu. Một bảng 12 cohort × 12 tuổi trên 3.000 người dùng có ô trung bình 20 người. **Vì sao nghe hợp lý:** nhiều dữ liệu hơn thường tốt hơn, nhưng ở đây tổng dữ liệu không đổi — chỉ có mẫu số của từng ô nhỏ lại.

## Nếu Bạn Dạy Lại Điều Này...

Mở đầu bằng biểu đồ tỉ lệ quay lại tổng thể đang giảm, để cả lớp đề xuất giả thuyết trong vài phút, rồi chiếu bảng cohort cho thấy ba cohort giống hệt nhau. Khoảng cách giữa hai hình là bài học.

Hạt giống bài tập: cho một bảng cohort có cohort mới nhất chỉ đủ hai tuổi, và yêu cầu chỉ ra ô nào không được phép đọc.

## Tự Kiểm Tra Nhanh

**1. Vì sao bảng cohort có hình tam giác?**

<details><summary>Đáp án</summary>

Cohort bắt đầu muộn chưa sống đủ lâu để có dữ liệu ở các tuổi lớn. Đó là hệ quả tất yếu của thời gian, không phải dữ liệu bị thiếu, và các ô ấy phải để trống chứ không được điền 0.
</details>

**2. Nhóm người dùng theo quốc gia có phải cohort không?**

<details><summary>Đáp án</summary>

Không, đó là phân khúc. Cohort đòi hỏi trục thời gian là tuổi tính từ một mốc bắt đầu chung của nhóm. Có thể kết hợp cả hai — cohort tháng 3 tại Việt Nam — nhưng riêng quốc gia thì không tạo ra cohort.
</details>

**3. Hai cohort cho hai tỉ lệ giữ chân khác nhau. Kết luận được gì về sản phẩm?**

<details><summary>Đáp án</summary>

Chưa kết luận được gì. Cohort chỉ loại bỏ yếu tố thời điểm bắt đầu; kênh thu hút, khuyến mãi và loại khách vẫn có thể khác nhau giữa hai cohort. Câu hỏi tiếp theo luôn là hai cohort ấy còn khác nhau ở chỗ nào.
</details>

Ghi chú tiếp theo là [Đường giữ chân](analytics.retention-curve.md), nơi bảng cohort được đọc theo chiều ngang và hình dạng của đường quan trọng hơn từng con số.
