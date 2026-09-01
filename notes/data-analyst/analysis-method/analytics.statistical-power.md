---
id: data-analyst.analytics.statistical-power
title: Statistical power
domain: data-analyst
type: mechanism
tags: [analytics, analysis-method, statistical, power]
status: draft
ai_summary: The chance of detecting an effect that is really there, fixed by sample size and effect size before the test runs; a non-significant result from an underpowered test says nothing.
relationships:
  builds_on: [data-analyst.analytics.simpson-paradox]
  prerequisite_of: []
  commonly_confused_with: [data-analyst.analytics.sampling-bias]
created: 2026-09-01
updated: 2026-09-01
version_sensitive: false
---

# Statistical power

**Tóm tắt bản chất:** Lực thống kê là xác suất phát hiện được một hiệu ứng thực sự tồn tại. Nó được quyết định **trước khi** thí nghiệm chạy, bởi cỡ mẫu và độ lớn hiệu ứng tối thiểu — và một kết quả "không có ý nghĩa thống kê" từ thí nghiệm thiếu lực không nói lên điều gì cả.

## Nỗi Đau & Động Lực

"Thí nghiệm không cho kết quả có ý nghĩa, nên tính năng này không có tác dụng." Câu này sai ở chỗ nó đọc sự vắng mặt của bằng chứng thành bằng chứng về sự vắng mặt — và mức độ sai phụ thuộc hoàn toàn vào lực thống kê, thứ hầu như không được tính.

Con số cụ thể: để phát hiện mức cải thiện tương đối 5% trên nền tỉ lệ chuyển đổi 4%, với lực 80% và mức ý nghĩa 5%, cần khoảng 63.000 người mỗi nhánh. Một thí nghiệm chạy với 5.000 người mỗi nhánh có lực khoảng 13%. Nghĩa là ngay cả khi hiệu ứng có thật đúng bằng 5%, thí nghiệm ấy vẫn bỏ sót nó gần chín lần trên mười.

Cái giá không dừng ở một tính năng bị loại oan. Đội đã học được rằng "chúng tôi đã thử và nó không hiệu quả", và kết luận ấy sống lâu hơn nhiều so với dữ liệu tạo ra nó. Không ai quay lại thử một ý tưởng đã bị bác bỏ.

Còn một chi phí thứ hai, ngược chiều: trong thí nghiệm thiếu lực, những kết quả **có** vượt ngưỡng ý nghĩa lại bị thổi phồng độ lớn. Chỉ hiệu ứng lớn bất thường mới đủ vượt ngưỡng với mẫu nhỏ, nên mọi hiệu ứng được công bố từ mẫu nhỏ đều lớn hơn sự thật.

## Cơ Chế Tác Động

Bốn đại lượng ràng buộc nhau; cố định ba thì cái thứ tư được xác định:

| Đại lượng | Ký hiệu | Thường chọn |
|---|---|---|
| mức ý nghĩa | α | 0,05 |
| lực | 1 − β | 0,80 |
| độ lớn hiệu ứng tối thiểu đáng quan tâm | MDE | do kinh doanh quyết định |
| cỡ mẫu mỗi nhánh | n | tính ra |

MDE là đại lượng duy nhất **không** phải lựa chọn kỹ thuật. Nó trả lời câu hỏi: mức cải thiện nhỏ nhất mà nếu đạt được thì công ty sẽ hành động khác đi. Cải thiện 0,3% trên tỉ lệ chuyển đổi có đáng để triển khai không? Nếu không, đừng thiết kế thí nghiệm để phát hiện nó.

Quan hệ quan trọng nhất cần thuộc: **cỡ mẫu tỉ lệ nghịch với bình phương MDE**. Muốn phát hiện hiệu ứng nhỏ bằng một nửa thì cần mẫu lớn gấp bốn. Đây là lý do các thí nghiệm nhắm tới cải thiện nhỏ trở nên bất khả thi rất nhanh.

Công thức xấp xỉ cho so sánh hai tỉ lệ:

```
n ≈ 16 × p × (1 − p) / (MDE tuyệt đối)²
```

Với p = 4% và MDE tương đối 5% — tức MDE tuyệt đối 0,002:

```
n ≈ 16 × 0,04 × 0,96 / 0,000004 ≈ 153.600
```

Con số này cao hơn ước lượng chính xác vì hằng số 16 là xấp xỉ thô cho α = 0,05 và lực 80%; dùng nó để biết bậc độ lớn, rồi tính lại bằng công cụ chuyên dụng trước khi cam kết.

Điều phải làm **trước** khi chạy: tính n, rồi đối chiếu với lưu lượng thực tế. Nếu cần 63.000 mỗi nhánh mà sản phẩm chỉ có 8.000 lượt mỗi tuần, thí nghiệm cần 16 tuần. Biết điều đó trước cho phép chọn: chờ, tăng MDE, hoặc không chạy. Biết sau khi chạy hai tuần thì chỉ còn một lựa chọn tệ.

## Bản Đồ Quyết Định

| Tình huống | Việc phải làm | Hậu quả nếu bỏ qua |
|---|---|---|
| trước mọi A/B test | tính n từ MDE do kinh doanh đặt | chạy một thí nghiệm không thể kết luận |
| lưu lượng không đủ cho MDE mong muốn | nâng MDE, hoặc đừng chạy | kết quả âm tính vô nghĩa bị đọc thành bằng chứng |
| kết quả không có ý nghĩa | báo cáo kèm lực và khoảng tin cậy | "không tác dụng" bị ghi vào trí nhớ tổ chức |
| kết quả có ý nghĩa từ mẫu nhỏ | nghi ngờ độ lớn, không nghi ngờ chiều | triển khai dựa trên hiệu ứng bị thổi phồng |
| muốn dừng sớm khi thấy thắng | dùng thiết kế tuần tự đã định trước | nhìn liên tục làm tỉ lệ dương tính giả vượt xa 5% |

Dòng cuối là sai lầm phổ biến nhất và ít bị coi là sai lầm nhất. Kiểm tra kết quả mỗi ngày rồi dừng khi p-value lần đầu xuống dưới 0,05 đẩy tỉ lệ dương tính giả lên trên 20% trong nhiều tình huống thực tế. Nếu cần dừng sớm, phải chọn phương pháp tuần tự **trước khi bắt đầu**, không phải quyết định giữa chừng rằng mình sẽ dừng.

Dòng thứ ba đáng viết vào mẫu báo cáo. "Không có ý nghĩa thống kê, lực 13%, khoảng tin cậy 95% từ −4% đến +9%" nói đúng những gì đã biết. "Không có tác dụng" thì không.

## Case Study Thực Chiến: tính năng bị loại vì thí nghiệm quá nhỏ

Lược đồ tối thiểu:

```
thi_nghiem (user_id, nhanh, da_chuyen_doi, ngay_vao)
```

Thí nghiệm chạy hai tuần, 5.100 người mỗi nhánh. Nhánh A chuyển đổi 4,0%, nhánh B chuyển đổi 4,3%. p = 0,41. Đội kết luận tính năng không có tác dụng và gỡ bỏ.

Tính ngược lực: với n = 5.100 mỗi nhánh và nền 4%, thí nghiệm này chỉ phát hiện được hiệu ứng tương đối từ khoảng 21% trở lên với lực 80%. Hiệu ứng thật cần đạt tới 4,84% mới có cơ hội bị phát hiện — mà không ai kỳ vọng một thay đổi giao diện tạo ra mức đó.

Khoảng tin cậy 95% của chênh lệch là khoảng −0,4% đến +1,0% tuyệt đối. Nó chứa cả 0, và cũng chứa cả mức cải thiện 0,8% mà nếu có thật sẽ rất đáng triển khai. Dữ liệu không phân biệt được hai khả năng ấy.

Kết luận đúng: thí nghiệm không đưa ra được thông tin. Không phải "không có tác dụng", mà "chúng ta chưa biết".

**Biến thể khó hơn, nơi cách hiểu trên gây hiểu lầm.** Đội chạy lại với 70.000 mỗi nhánh. Kết quả: B hơn A 0,15% tuyệt đối, p = 0,03, có ý nghĩa thống kê.

Có ý nghĩa thống kê không đồng nghĩa với đáng làm. Mức 0,15% có thể thấp hơn hẳn MDE mà đội đã đặt lúc thiết kế, và nếu tính năng ấy tốn ba tháng bảo trì mỗi năm thì con số ấy không trả nổi chi phí.

Mẫu đủ lớn phát hiện được **mọi** hiệu ứng khác 0, kể cả hiệu ứng không có giá trị thực tiễn. Đó là lý do MDE phải được đặt trước bởi kinh doanh: nó là ranh giới giữa "phát hiện được" và "đáng quan tâm", và chỉ có một trong hai ranh giới ấy nằm trong thống kê.

## Góc Khuất & Ngộ Nhận

Về đơn vị ngẫu nhiên hóa: nếu ngẫu nhiên hóa theo người dùng nhưng phân tích theo phiên, cỡ mẫu hiệu dụng gần với số **người** hơn là số phiên, vì các phiên của cùng một người tương quan với nhau. Ở sản phẩm có trung bình bốn phiên mỗi người, đếm theo phiên thổi cỡ mẫu lên khoảng bốn lần và lực thực tế thấp hơn hẳn lực đã tính.

Về nhiều chỉ số: kiểm định mười chỉ số ở mức α = 0,05 cho xác suất có ít nhất một dương tính giả khoảng 40%. Chọn một chỉ số chính trước khi chạy, và coi phần còn lại là thăm dò chứ không phải bằng chứng.

**Hiểu lầm:** "p > 0,05 nghĩa là không có hiệu ứng."
**Thực tế:** Nó nghĩa là dữ liệu không đủ để bác bỏ giả thuyết không có hiệu ứng. Với lực 13%, kết quả ấy là điều được kỳ vọng ngay cả khi hiệu ứng tồn tại đúng như mong đợi. **Vì sao nghe hợp lý:** p-value được dạy như một ngưỡng nhị phân, và ngưỡng nhị phân mời gọi cách đọc nhị phân.

**Hiểu lầm:** "Chạy thêm cho tới khi có ý nghĩa."
**Thực tế:** Nhìn liên tục rồi dừng khi thấy kết quả mong muốn phá vỡ giả định của kiểm định. Tỉ lệ dương tính giả không còn là 5% mà cao hơn nhiều lần. **Vì sao nghe hợp lý:** thêm dữ liệu thường làm ước lượng tốt hơn, và trực giác ấy đúng — chỉ là nó không cho phép chọn thời điểm dừng dựa trên chính dữ liệu.

**Hiểu lầm:** "Lực là chuyện tính sau khi có kết quả."
**Thực tế:** Lực tính sau — lực quan sát — là một hàm của p-value và không mang thông tin mới. Lực chỉ có ích khi được tính trước, từ MDE, để quyết định có nên chạy hay không. **Vì sao nghe hợp lý:** công cụ thống kê sẵn sàng in ra lực quan sát, và thứ gì được in ra thì trông như thứ đáng đọc.

## Nếu Bạn Dạy Lại Điều Này...

Mở đầu bằng một kết quả p = 0,41 và câu hỏi "kết luận gì". Sau khi cả lớp kết luận không có tác dụng, chiếu lực 13%. Khoảng lặng ấy là bài học.

Hạt giống bài tập: cho lưu lượng thực tế mỗi tuần và một MDE do kinh doanh đặt, yêu cầu tính số tuần cần chạy — rồi hỏi nên làm gì khi con số ra 16 tuần.

## Tự Kiểm Tra Nhanh

**1. Muốn phát hiện hiệu ứng nhỏ bằng một nửa thì cần mẫu lớn gấp mấy?**

<details><summary>Đáp án</summary>

Gấp bốn. Cỡ mẫu tỉ lệ nghịch với bình phương độ lớn hiệu ứng, nên chia đôi MDE thì nhân bốn n. Đây là lý do các thí nghiệm nhắm tới cải thiện rất nhỏ trở nên bất khả thi về lưu lượng rất nhanh.
</details>

**2. Kết quả p = 0,41 với lực 13% nói lên điều gì?**

<details><summary>Đáp án</summary>

Rằng thí nghiệm không đưa ra được thông tin. Với lực 13%, một hiệu ứng có thật vẫn bị bỏ sót gần chín lần trên mười, nên kết quả âm tính là điều được kỳ vọng dù hiệu ứng tồn tại hay không. Kết luận đúng là "chưa biết", không phải "không có tác dụng".
</details>

**3. Vì sao mẫu rất lớn có thể cho kết quả có ý nghĩa mà không đáng làm?**

<details><summary>Đáp án</summary>

Vì mẫu đủ lớn phát hiện được mọi hiệu ứng khác 0, kể cả những hiệu ứng quá nhỏ để có giá trị thực tiễn. Ý nghĩa thống kê nói về khả năng hiệu ứng khác 0; MDE do kinh doanh đặt mới nói về việc nó có đáng để hành động hay không.
</details>

Ghi chú tiếp theo là [Thiên lệch chọn mẫu](analytics.sampling-bias.md), nơi cỡ mẫu lớn tới đâu cũng không cứu được.
