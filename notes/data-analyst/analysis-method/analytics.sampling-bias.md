---
id: data-analyst.analytics.sampling-bias
title: Sampling bias
domain: data-analyst
type: pitfall
tags: [analytics, analysis-method, sampling, bias]
status: draft
ai_summary: A sample whose selection is related to the outcome being measured, which no sample size fixes because the error is systematic rather than random.
relationships:
  builds_on: [data-analyst.analytics.statistical-power]
  prerequisite_of: []
  commonly_confused_with: [data-analyst.analytics.survivorship-bias]
created: 2026-09-01
updated: 2026-09-01
version_sensitive: false
---

# Sampling bias

**Tóm tắt bản chất:** Thiên lệch chọn mẫu xảy ra khi cách một đơn vị lọt vào mẫu có liên hệ với chính thứ đang được đo. Cỡ mẫu không sửa được nó — thêm dữ liệu chỉ làm con số sai trở nên chính xác hơn, với khoảng tin cậy hẹp hơn quanh giá trị sai.

## Nỗi Đau & Động Lực

Khảo sát mức hài lòng gửi qua email cho toàn bộ khách hàng, 2.400 người trả lời, điểm trung bình 4,3 trên 5. Cỡ mẫu lớn, sai số biên nhỏ, báo cáo trông vững chắc.

Ai trả lời khảo sát? Người còn mở email của công ty, tức người chưa rời bỏ. Người rất hài lòng muốn khen, và người rất bực muốn phàn nàn — nhóm ở giữa im lặng. Điểm 4,3 mô tả những người sẵn lòng trả lời, và không có phép tính nào chuyển nó thành điểm của toàn bộ khách hàng.

Chỗ khác biệt so với nhiễu: **nhiễu giảm khi tăng mẫu, thiên lệch thì không**. Gửi cho 24.000 người và nhận 24.000 câu trả lời vẫn cho ra cùng con số sai, chỉ với khoảng tin cậy hẹp hơn — tức là bạn tự tin hơn vào một con số sai.

Cái giá nằm ở sự tự tin ấy. Một ước lượng nhiễu được đối xử thận trọng; một ước lượng thiên lệch với sai số biên ±0,4% được đưa vào quyết định như thể nó là sự thật.

## Cơ Chế Tác Động

Chỉ có đúng một điều kiện tạo ra thiên lệch: **xác suất lọt vào mẫu tương quan với kết quả**. Nếu người hài lòng có xác suất trả lời cao hơn, mẫu nghiêng. Nếu xác suất trả lời như nhau ở mọi mức hài lòng, mẫu nhỏ vẫn không thiên lệch.

Chú ý cái không phải điều kiện: mẫu không cần phải nhỏ, không cần phải chọn cẩu thả, và không cần ai làm gì sai.

Bốn nguồn thường gặp trong công việc dữ liệu:

**Tự chọn.** Khảo sát, đánh giá sản phẩm, phỏng vấn người dùng. Ai chịu tham gia thì khác ai không tham gia, và khác ở đúng chiều đang đo.

**Sống sót.** Chỉ đo những gì còn lại. Trường hợp riêng, có ghi chú riêng.

**Mất mát dữ liệu không đồng đều.** Trình chặn quảng cáo chặn sự kiện ở một số trình duyệt nhiều hơn; người dùng bảo mật cao hơn thì thiếu dữ liệu nhiều hơn. Mẫu nghiêng về nhóm ít quan tâm tới quyền riêng tư.

**Ngưỡng của hệ thống.** Bảng chỉ lưu giao dịch trên 10.000 đồng, hoặc phiên dài hơn 3 giây. Ngưỡng nào cũng cắt mẫu theo một chiều liên quan tới hành vi.

Phép kiểm không phải kiểm mẫu — mẫu không tự tố cáo mình. Phải so mẫu với một nguồn độc lập biết tổng thể:

```sql
-- phân bố của người trả lời so với phân bố của toàn bộ khách hàng
SELECT c.segment,
       COUNT(*) FILTER (WHERE s.user_id IS NOT NULL) * 1.0 / COUNT(*) AS ti_le_tra_loi
FROM customers c
LEFT JOIN survey s ON s.user_id = c.customer_id
GROUP BY 1;
```

Tỉ lệ trả lời khác nhau giữa các phân khúc là bằng chứng thiên lệch. Bằng nhau thì chưa chứng minh được gì — mẫu vẫn có thể nghiêng theo một biến bạn chưa đo.

## Bản Đồ Quyết Định

| Nguồn | Cách giảm | Cách **không** giảm được |
|---|---|---|
| tự chọn trong khảo sát | tái cân theo phân bố đã biết | tăng số người được gửi |
| mất mát sự kiện phía trình duyệt | đo ở phía máy chủ | lọc bỏ dữ liệu "bất thường" |
| ngưỡng của hệ thống | lấy dữ liệu trước khi cắt ngưỡng | ngoại suy từ phần trên ngưỡng |
| chỉ có khách hàng hiện tại | tìm bảng lịch sử | trung bình lâu hơn |
| không xác định được nguồn | công bố giới hạn cùng con số | làm tròn cho gọn rồi báo cáo |

Trong bảng này, tái cân là công cụ mạnh nhất và bị hiểu nhầm nhiều nhất. Phép ấy sửa được thiên lệch theo các biến bạn **biết** phân bố tổng thể — tuổi, phân khúc, quốc gia. Biến không quan sát được thì nó bó tay, và biến quan trọng nhất thường nằm đúng nhóm ấy: mức độ gắn bó, ý định rời bỏ, mức độ bực bội.

Dòng cuối là lựa chọn trung thực khi các dòng trên không khả thi. Kèm câu "mẫu này gồm người còn mở email, nên nghiêng về nhóm gắn bó" thì con số vẫn dùng được. Không kèm gì thì nó gây hại.

## Case Study Thực Chiến: điểm hài lòng 4,3 và tỉ lệ rời bỏ tăng

Lược đồ tối thiểu:

```
customers (customer_id, segment, churned_at)
survey    (response_id, customer_id, diem, tra_loi_luc)
```

Điểm khảo sát 4,3 và ổn định qua ba quý. Cùng lúc, tỉ lệ rời bỏ tăng từ 3,1% lên 5,8% mỗi tháng. Hai chỉ số mâu thuẫn nhau, và đội tin vào chỉ số có cỡ mẫu lớn hơn.

Chạy phép kiểm tỉ lệ trả lời theo phân khúc: khách gắn bó trả lời 31%, khách đang giảm hoạt động trả lời 4%. Mẫu khảo sát gần như chỉ chứa nhóm hài lòng, và nó ổn định qua ba quý vì nhóm ấy vẫn hài lòng — trong khi nhóm không được đại diện đang rời đi.

Con số 4,3 không sai. Con số ấy trả lời câu hỏi "khách gắn bó nghĩ gì", trong khi câu hỏi cần trả lời là "khách sắp rời nghĩ gì" — và những người ấy, theo định nghĩa, không trả lời khảo sát.

**Biến thể khó hơn, nơi cách hiểu trên gây hiểu lầm.** Đội tái cân theo phân khúc hoạt động. Điểm điều chỉnh xuống 3,6, và họ coi đó là con số thật.

Phép tái cân đứng trên một giả định: **trong cùng một phân khúc**, người trả lời đại diện cho người không trả lời. Giả định ấy gần như chắc chắn sai, và sai theo đúng chiều đã tạo ra vấn đề. Ngay trong nhóm đang giảm hoạt động, người bực nhất vẫn ít trả lời nhất.

Con số 3,6 tốt hơn 4,3 và vẫn lạc quan. Tái cân thu hẹp thiên lệch xuống phần nằm trong từng ô. Nó không xóa.

Quy tắc rút ra: khi câu hỏi là về nhóm không trả lời, không có phép hiệu chỉnh nào thay thế được việc đi tìm họ. Phỏng vấn khách đã rời tốn kém và phiền, và nó là cách duy nhất trả lời câu hỏi ấy.

## Góc Khuất & Ngộ Nhận

Về dữ liệu quan sát nói chung: mọi bảng sự kiện đều là một mẫu của hành vi, không phải toàn bộ hành vi. Chặn theo dõi, dùng nhiều thiết bị, thao tác ngoài sản phẩm — mỗi thứ tạo ra một khoảng trống có hệ thống, không phải ngẫu nhiên.

Về A/B test: ngẫu nhiên hóa loại được thiên lệch chọn mẫu **giữa hai nhánh**, nên so sánh A với B là hợp lệ. Điều đó không làm mẫu trở nên đại diện cho toàn bộ người dùng, nên độ lớn hiệu ứng đo được chỉ áp cho nhóm đã tham gia thí nghiệm.

**Hiểu lầm:** "Mẫu lớn thì đại diện."
**Thực tế:** Kích thước và tính đại diện là hai thuộc tính độc lập. Một triệu người tự chọn vẫn không đại diện; một nghìn người chọn ngẫu nhiên thì có. **Vì sao nghe hợp lý:** cỡ mẫu là thứ duy nhất trong hai thuộc tính ấy được in ra cạnh con số, nên nó trở thành thước đo độ tin cậy.

**Hiểu lầm:** "Thiên lệch chọn mẫu và thiên lệch sống sót là một."
**Thực tế:** Sống sót là trường hợp riêng, nơi tiêu chí chọn là còn tồn tại tại thời điểm đo. Tự chọn trong khảo sát không liên quan tới thời gian và vẫn là thiên lệch chọn mẫu. **Vì sao nghe hợp lý:** cả hai cho ra mẫu không đại diện và thường xuất hiện cạnh nhau trong tài liệu.

**Hiểu lầm:** "Tái cân sửa được thiên lệch."
**Thực tế:** Phép ấy sửa được phần thiên lệch nằm trong các biến bạn biết phân bố tổng thể, và để nguyên phần nằm trong biến không quan sát được. Phần còn lại thường là phần quan trọng. **Vì sao nghe hợp lý:** tái cân là một phép toán rõ ràng cho ra một con số mới, và một con số mới trông như một vấn đề đã được giải quyết.

## Nếu Bạn Dạy Lại Điều Này...

Mở đầu bằng hai chỉ số mâu thuẫn — hài lòng ổn định, rời bỏ tăng — và hỏi tin cái nào. Đa số chọn cái có cỡ mẫu lớn hơn. Sau đó chiếu tỉ lệ trả lời theo phân khúc.

Hạt giống bài tập: cho một khảo sát 2.400 câu trả lời và bảng khách hàng đầy đủ, yêu cầu tính tỉ lệ trả lời theo phân khúc và nói rõ con số trung bình đang mô tả nhóm nào.

## Tự Kiểm Tra Nhanh

**1. Vì sao tăng cỡ mẫu không sửa được thiên lệch chọn mẫu?**

<details><summary>Đáp án</summary>

Vì sai lệch có hệ thống chứ không ngẫu nhiên. Thêm dữ liệu từ cùng một cơ chế chọn thiên lệch chỉ làm ước lượng hội tụ chính xác hơn về giá trị sai, với khoảng tin cậy hẹp hơn quanh nó.
</details>

**2. Tỉ lệ trả lời khảo sát bằng nhau giữa các phân khúc. Mẫu có đại diện không?**

<details><summary>Đáp án</summary>

Chưa kết luận được. Nó loại trừ thiên lệch theo phân khúc, nhưng mẫu vẫn có thể nghiêng theo một biến chưa được đo — mức bực bội, ý định rời bỏ. Phép kiểm chỉ bác bỏ được thiên lệch theo biến bạn đã kiểm.
</details>

**3. Ngẫu nhiên hóa trong A/B test loại bỏ thiên lệch chọn mẫu tới mức nào?**

<details><summary>Đáp án</summary>

Nó loại bỏ thiên lệch giữa hai nhánh, nên so sánh A với B là hợp lệ. Điều đó không khiến những người tham gia thí nghiệm đại diện cho toàn bộ người dùng, nên độ lớn hiệu ứng chỉ áp cho nhóm đã tham gia.
</details>

Ghi chú tiếp theo là [Trôi định nghĩa chỉ số](analytics.metric-definition-drift.md), nơi mẫu không đổi nhưng thước đo thì có.
