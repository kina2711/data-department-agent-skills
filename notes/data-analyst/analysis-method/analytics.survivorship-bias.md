---
id: data-analyst.analytics.survivorship-bias
title: Survivorship bias
domain: data-analyst
type: pitfall
tags: [analytics, analysis-method, survivorship, bias]
status: draft
ai_summary: Measuring only the entities that remained makes any average look better than the population, because the ones that failed left the table.
relationships:
  builds_on: [data-analyst.analytics.retention-curve]
  prerequisite_of: []
  commonly_confused_with: [data-analyst.analytics.sampling-bias]
created: 2026-09-01
updated: 2026-09-01
version_sensitive: false
---

# Survivorship bias

**Tóm tắt bản chất:** Đo chỉ những thực thể còn lại khiến mọi con số trung bình đẹp hơn thực tế, vì những thực thể thất bại đã rời khỏi bảng. Nó không phải lỗi truy vấn — dữ liệu đúng, phép tính đúng, và tập hợp đang được đo đã tự chọn chính nó.

## Nỗi Đau & Động Lực

"Khách hàng của chúng ta ở lại trung bình 14 tháng." Con số này tính từ bảng khách hàng hiện tại. Những người rời đi sau hai tháng không còn trong bảng ấy, nên họ không đóng góp vào trung bình.

Điều đáng lo là con số ấy **tăng dần theo thời gian** dù không có gì cải thiện. Càng nhiều tháng trôi qua, những người ở lại lâu càng tích lũy thêm tuổi thọ, còn những người rời sớm càng bị loại sạch. Một sản phẩm đang xấu đi vẫn có thể báo cáo tuổi thọ khách hàng tăng đều.

Cái giá rất cụ thể. Mô hình tài chính lấy con số 14 tháng để tính giá trị vòng đời, và chính giá trị vòng đời ấy đặt trần cho ngân sách quảng cáo. Nếu tuổi thọ thật của một khách mới là 5 tháng, công ty đang trả gấp gần ba lần mức nó có thể thu hồi — và bảng điều khiển sẽ trông ổn cho tới lúc hết tiền.

Không ai phải làm gì sai cả. Đây là hành vi mặc định của mọi truy vấn chạy trên một bảng trạng thái hiện tại, và nó im lặng.

## Cơ Chế Tác Động

Nguồn gốc là một `WHERE` không ai viết ra. Bảng `customers` chỉ chứa khách còn hoạt động, bởi hệ thống đã xóa hoặc chuyển kho những người đã rời từ lâu trước khi truy vấn của bạn chạy. Truy vấn sạch. Dữ liệu thì không.

Ba dạng thường gặp, cùng một cơ chế:

**Dạng một — bảng trạng thái hiện tại.** `customers`, `active_subscriptions`, `employees`. Mọi trung bình trên các bảng này đều là trung bình của người sống sót.

**Dạng hai — dữ liệu bị cắt phải.** Tính tuổi thọ trung bình khi nhiều khách vẫn đang hoạt động. Tuổi thọ của họ chưa kết thúc, nên bất kỳ cách xử lý nào cũng sai: bỏ họ ra thì chỉ còn người đã rời, giữ họ với tuổi hiện tại thì đánh giá thấp.

**Dạng ba — phân tích chỉ trên nhóm thành công.** "Khách hàng doanh nghiệp lớn của chúng ta dùng trung bình 4,2 tính năng." Câu này thường được dùng để suy ra rằng dùng nhiều tính năng khiến khách hàng lớn hơn, trong khi chiều nhân quả có thể ngược lại, hoặc không tồn tại.

Phép kiểm nhanh, một câu hỏi: **những thực thể không còn ở đây thì đi đâu?** Có bảng lịch sử thì dùng. Không có thì con số bạn vừa tính chỉ mô tả người sống sót, và điều đó phải được nói ra trong báo cáo chứ không để người đọc tự đoán.

Cách xử lý đúng cho dạng hai là phân tích sống còn: mỗi khách đóng góp khoảng thời gian họ đã được quan sát, và những người còn hoạt động được đánh dấu là **bị kiểm duyệt** thay vì bị bỏ đi hay bị coi như đã rời. Đường Kaplan-Meier là dạng phổ biến nhất, và nó tồn tại chính xác vì bài toán này.

## Bản Đồ Quyết Định

| Tình huống | Đừng làm | Làm |
|---|---|---|
| tuổi thọ khách hàng | `AVG(tuoi)` trên bảng hiện tại | phân tích sống còn với dữ liệu bị kiểm duyệt |
| "tính năng nào giữ chân" | so người dùng nhiều với người dùng ít | so cohort trước và sau khi có tính năng |
| hiệu quả chương trình đào tạo | khảo sát người đã hoàn thành | tính cả người bỏ giữa chừng vào mẫu số |
| chất lượng nhà cung cấp | đánh giá của khách còn dùng | truy các khách đã chuyển đi |
| "chiến lược của công ty thành công" | học từ công ty còn tồn tại | tìm công ty đã áp dụng nó và đã chết |

Dòng cuối là hình thức phổ biến nhất ngoài đời và ít được nhận ra nhất trong công việc phân tích. Mọi bài học rút ra từ tập hợp những thứ còn tồn tại đều mang thiên lệch này, và tập hợp thất bại thường không được lưu ở đâu cả.

Hậu quả của việc bỏ qua luôn cùng một hướng: **ước lượng lạc quan**. Đây là điều khiến nó nguy hiểm hơn nhiễu ngẫu nhiên. Nhiễu sai về cả hai phía nên trung bình lại thì triệt tiêu. Thiên lệch này sai một phía, và nó tích lũy.

## Case Study Thực Chiến: giá trị vòng đời khách hàng bị thổi gần ba lần

Lược đồ tối thiểu:

```
customers         (customer_id, signed_up_at, churned_at)
customers_active  (customer_id, signed_up_at)     -- khung nhìn: churned_at IS NULL
```

Đội tài chính tính:

```sql
SELECT AVG(EXTRACT(EPOCH FROM (NOW() - signed_up_at)) / 2592000) AS tuoi_tb_thang
FROM customers_active;   -- 14,2
```

Con số 14,2 tháng đi vào mô hình LTV, và mô hình cho phép chi tới 2,4 triệu đồng để thu hút một khách.

Tính lại trên bảng đầy đủ, bao gồm cả khách đã rời:

```sql
SELECT AVG(EXTRACT(EPOCH FROM (COALESCE(churned_at, NOW()) - signed_up_at)) / 2592000)
FROM customers;          -- 5,1
```

5,1 tháng. Và con số này **vẫn còn lạc quan**, vì những khách chưa rời sẽ còn sống thêm — nhưng nó sai theo hướng ngược lại, tức là đánh giá thấp. Con số đúng nằm giữa, và tìm nó cần phân tích sống còn chứ không phải một phép trung bình.

**Biến thể khó hơn, nơi cách hiểu trên gây hiểu lầm.** Đội sửa truy vấn, dùng bảng đầy đủ, và báo cáo 5,1 tháng. Sáu tháng sau con số lên 6,3 và họ kết luận sản phẩm đã cải thiện.

Có thể không. Với dữ liệu bị cắt phải, chỉ riêng việc thời gian trôi qua đã làm con số tăng: các cohort cũ tích thêm tuổi, và cohort mới chưa kịp rời. Con số trung bình trên toàn bộ lịch sử là một hàm của độ dài lịch sử, không chỉ của chất lượng sản phẩm.

Cách so sánh đúng là cố định tuổi: tỉ lệ còn hoạt động **ở tháng thứ 6** của cohort tháng 1 so với cohort tháng 7. Đó là lý do đường giữ chân theo cohort tồn tại, và nó không phải một cách trình bày khác của cùng dữ liệu — nó là cách duy nhất khiến hai con số so sánh được với nhau.

## Góc Khuất & Ngộ Nhận

Bảng lịch sử thường tồn tại nhưng ở nơi khác: nhật ký thay đổi, kho lưu trữ, bản sao lưu. Câu hỏi "khách đã rời được lưu ở đâu" đáng hỏi trước khi kết luận rằng dữ liệu không có.

Xóa mềm không cứu được: hệ thống dùng `deleted_at` giữ đủ lịch sử, nhưng khung nhìn mặc định thường đã lọc sẵn, và thiên lệch quay lại qua cửa sau. Kiểm định nghĩa của khung nhìn, đừng chỉ kiểm tên bảng.

**Hiểu lầm:** "Thêm dữ liệu là hết thiên lệch."
**Thực tế:** Thêm dữ liệu về những người sống sót chỉ làm ước lượng sai trở nên chính xác hơn. Cỡ mẫu không sửa được thiên lệch chọn mẫu; chỉ có việc đưa nhóm bị thiếu trở lại mới sửa được. **Vì sao nghe hợp lý:** với sai số ngẫu nhiên thì thêm dữ liệu đúng là cách chữa, và người ta chuyển quy tắc ấy sang một loại sai khác hẳn.

**Hiểu lầm:** "Thiên lệch sống sót và thiên lệch chọn mẫu là một."
**Thực tế:** Thiên lệch sống sót là trường hợp riêng, nơi tiêu chí chọn là "còn tồn tại tại thời điểm đo". Thiên lệch chọn mẫu rộng hơn và không cần yếu tố thời gian. **Vì sao nghe hợp lý:** cả hai đều là mẫu không đại diện, và trong nhiều tài liệu chúng được đặt cạnh nhau trong cùng một mục.

**Hiểu lầm:** "Bỏ những người chưa rời ra là cách xử lý an toàn."
**Thực tế:** Làm vậy tạo ra thiên lệch ngược: mẫu chỉ còn người đã rời, tức chỉ còn người có tuổi thọ ngắn hơn trung bình. Cả hai cách bỏ đều sai; dữ liệu bị kiểm duyệt phải được xử lý như dữ liệu bị kiểm duyệt. **Vì sao nghe hợp lý:** loại bỏ dữ liệu chưa hoàn chỉnh nghe như một hành động thận trọng, và sự thận trọng ấy che mất việc nó cũng là một lựa chọn có hậu quả.

## Nếu Bạn Dạy Lại Điều Này...

Mở đầu bằng câu hỏi: "Trung bình một khách hàng ở lại bao lâu?" và để cả lớp viết truy vấn. Gần như tất cả sẽ chạy trên bảng khách hàng hiện tại. Sau đó hỏi những khách đã rời đang ở đâu.

Hạt giống bài tập: cho một chỉ số tuổi thọ tăng đều qua bốn quý và yêu cầu chứng minh rằng nó tăng ngay cả khi sản phẩm không đổi.

## Tự Kiểm Tra Nhanh

**1. Vì sao tuổi thọ khách hàng trung bình tính trên bảng hiện tại tăng dần theo thời gian?**

<details><summary>Đáp án</summary>

Người ở lại lâu tích lũy thêm tuổi, còn người rời sớm bị loại khỏi bảng. Mẫu ngày càng nghiêng về nhóm sống lâu, nên trung bình tăng ngay cả khi hành vi không đổi chút nào.
</details>

**2. Bỏ những khách chưa rời ra khỏi phép tính có sửa được thiên lệch không?**

<details><summary>Đáp án</summary>

Không, nó tạo thiên lệch ngược: mẫu chỉ còn người đã rời, tức toàn người có tuổi thọ ngắn. Dữ liệu bị cắt phải cần phân tích sống còn, nơi người còn hoạt động được đánh dấu là bị kiểm duyệt thay vì bị loại hoặc bị coi như đã rời.
</details>

**3. Cỡ mẫu lớn hơn có làm giảm thiên lệch sống sót không?**

<details><summary>Đáp án</summary>

Không. Cỡ mẫu giảm sai số ngẫu nhiên, không giảm thiên lệch có hệ thống. Mười nghìn người sống sót vẫn cho ước lượng lạc quan y hệt một nghìn người sống sót, chỉ là với khoảng tin cậy hẹp hơn quanh con số sai.
</details>

Ghi chú tiếp theo là [Nghịch lý Simpson](analytics.simpson-paradox.md), nơi dữ liệu đầy đủ vẫn dẫn tới kết luận ngược nếu gộp các nhóm lại.
