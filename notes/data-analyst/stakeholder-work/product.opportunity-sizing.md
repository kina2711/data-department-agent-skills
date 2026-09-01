---
id: data-analyst.product.opportunity-sizing
title: Opportunity sizing
domain: data-analyst
type: pattern
tags: [product, stakeholder-work, opportunity, sizing]
status: draft
ai_summary: An estimate of what a change is worth, built from a chain of stated assumptions so the estimate can be argued with rather than believed or dismissed.
relationships:
  builds_on: [data-analyst.product.stakeholder-decision]
  prerequisite_of: [data-analyst.product.acceptance-criteria]
  commonly_confused_with: [data-analyst.analytics.statistical-power]
created: 2026-09-01
updated: 2026-09-01
version_sensitive: false
---

# Opportunity sizing

**Tóm tắt bản chất:** Ước lượng cơ hội là con số trả lời "thay đổi này đáng bao nhiêu", kèm chuỗi giả định dẫn tới nó. Giá trị nằm ở chuỗi giả định chứ không ở con số: một ước lượng có thể tranh luận được thì hữu ích, còn một con số không ai bẻ được thì không ai dùng được.

## Nỗi Đau & Động Lực

"Tính năng này sẽ mang về 8 tỉ mỗi năm." Câu ấy hoặc được tin hoàn toàn hoặc bị bác hoàn toàn, và cả hai phản ứng đều tệ như nhau. Không ai bẻ được nó vì không có chỗ nào để bẻ.

Bây giờ đổi cách trình bày: 120.000 người dùng đủ điều kiện, 25% sẽ dùng thử, 40% trong số đó chuyển thành trả tiền, mỗi người 550.000 đồng một năm. Cũng ra khoảng 6,6 tỉ, nhưng bây giờ có bốn chỗ để tranh luận. Trưởng nhóm bán hàng nhìn con số 40% và nói ở sản phẩm này tỉ lệ ấy chưa bao giờ vượt 15%. Cuộc trao đổi ấy mất ba phút và sửa được ước lượng xuống 2,5 tỉ.

Chi phí của con số không chuỗi giả định không phải sai số. Nó là việc **cuộc tranh luận không thể xảy ra**, nên tổ chức quyết định dựa trên việc ai tự tin hơn.

Có một hệ quả thứ hai, chậm hơn: khi ước lượng không có giả định ghi lại, không ai kiểm chứng được sau sáu tháng. Thứ đáng học nhất — giả định nào của chúng ta thường sai, và sai về phía nào — không bao giờ được học.

## Cơ Chế Tác Động

Cấu trúc là một chuỗi nhân, mỗi mắt xích là một giả định có nguồn:

```
quy mô tệp đủ điều kiện  × tỉ lệ tiếp nhận × tỉ lệ chuyển đổi × giá trị mỗi đơn vị
```

Mỗi mắt xích được gán một trong ba nhãn, và nhãn quan trọng ngang giá trị:

| Nhãn | Nghĩa | Ví dụ |
|---|---|---|
| đo được | truy vấn ra từ dữ liệu hiện có | 120.000 người dùng đủ điều kiện |
| suy từ tương tự | lấy từ một tính năng đã ra | tỉ lệ tiếp nhận 25%, theo tính năng X năm ngoái |
| phán đoán | không có dữ liệu, do người có kinh nghiệm đặt | tỉ lệ chuyển đổi 40% |

Sai số nhân lên qua chuỗi. Bốn mắt xích, mỗi mắt lệch 30%, cho khoảng dao động của tích lớn hơn nhiều so với trực giác. Đó là lý do ước lượng nên trình bày dưới dạng khoảng, không phải một điểm:

```
thấp:  120.000 × 15% × 20% × 450.000 =  1,62 tỉ
giữa:  120.000 × 25% × 30% × 550.000 =  4,95 tỉ
cao:   120.000 × 35% × 45% × 650.000 = 12,29 tỉ
```

Khoảng từ 1,6 tới 12,3 tỉ nghe kém dứt khoát hơn "8 tỉ", và nó trung thực hơn. Nếu ngưỡng ra quyết định là 3 tỉ, khoảng ấy nói rằng dữ liệu chưa đủ để quyết — một kết luận hữu ích mà con số điểm che mất.

Phép kiểm cuối cùng, luôn chạy: **phân tích độ nhạy**. Mắt xích nào thay đổi thì kết quả đổi nhiều nhất? Ở ví dụ trên là tỉ lệ chuyển đổi, và nó cũng là mắt xích mang nhãn "phán đoán". Cặp đôi ấy — ảnh hưởng lớn nhất và bằng chứng yếu nhất — chính là chỗ nên bỏ một tuần đi tìm dữ liệu, và thường là thứ duy nhất đáng làm tiếp.

## Bản Đồ Quyết Định

| Tình huống | Việc phải làm | Hậu quả nếu bỏ qua |
|---|---|---|
| cần con số cho phiên duyệt ngân sách | khoảng ba kịch bản, kèm nhãn từng giả định | con số điểm bị tin hoặc bị bác, không được bàn |
| một mắt xích không có dữ liệu | ghi nhãn phán đoán, hỏi người có kinh nghiệm | phán đoán trôi thành sự thật sau hai lần trình bày |
| khoảng ước lượng vắt qua ngưỡng quyết định | nói rõ chưa đủ để quyết | chọn điểm giữa và trình bày như thể chắc chắn |
| nhiều cơ hội cần xếp hạng | dùng cùng một cấu trúc chuỗi cho tất cả | so sánh các ước lượng xây theo cách khác nhau |
| ước lượng cho thứ chưa từng tồn tại | tìm loại tương tự gần nhất, ghi rõ nó khác chỗ nào | ngoại suy từ không có gì |

Dòng thứ hai là nơi ước lượng thoái hóa nhanh nhất. Một con số phán đoán được nói ra trong cuộc họp, được ghi vào slide, và tới lần trình bày thứ ba thì nhãn đã rơi mất. Giữ nhãn đi cùng con số qua mọi lần sao chép là việc thủ công và không có công cụ nào làm hộ.

Dòng thứ tư đáng nhấn khi xếp hạng danh mục. Hai cơ hội ước lượng bởi hai người theo hai cấu trúc khác nhau không so được, kể cả khi cả hai đều cẩn thận. Xếp hạng cần cùng một bộ khung, và cùng một mức lạc quan.

## Case Study Thực Chiến: từ 8 tỉ xuống 2,5 tỉ trong ba phút

Bối cảnh: đề xuất xây tính năng nâng cấp gói tự động. Ước lượng ban đầu 8 tỉ một năm, không có chuỗi.

Viết lại thành chuỗi, mỗi mắt xích có nguồn:

```
120.000 người dùng gói cơ bản hoạt động        [đo được: truy vấn ngày 28/8]
×  25% sẽ thấy và mở luồng nâng cấp            [tương tự: tính năng X, 2025]
×  40% trong số đó hoàn tất nâng cấp           [phán đoán: chưa có dữ liệu]
×  550.000 đồng chênh lệch giá mỗi năm         [đo được: bảng giá hiện hành]
= 6,6 tỉ
```

Trưởng nhóm bán hàng nhìn mắt xích thứ ba: mọi luồng nâng cấp tự phục vụ ở sản phẩm này chưa bao giờ vượt 15%. Thay 40% bằng 15% cho ra 2,48 tỉ.

Ba phút, và con số đổi 2,7 lần. Điều làm cuộc trao đổi ấy khả thi không phải kỹ năng phân tích — mà là mắt xích thứ ba đã được viết ra thành một dòng riêng, mang nhãn phán đoán, để một người có kiến thức khác nhìn thấy và phản đối.

**Biến thể khó hơn, nơi cách hiểu trên gây hiểu lầm.** Với 2,48 tỉ, tính năng vẫn vượt ngưỡng 2 tỉ, nên đề xuất được duyệt.

Ước lượng này chỉ tính phần tăng. Nó không trừ đi phần khách hàng lẽ ra đã nâng cấp qua đội bán hàng — những người sẽ dùng luồng tự động thay vì gọi điện, và đóng góp đúng số tiền ấy dù có tính năng hay không. Nếu một nửa trong số họ thuộc nhóm này, giá trị **gia tăng** chỉ còn 1,24 tỉ, dưới ngưỡng.

Đây là lỗi phổ biến nhất trong ước lượng cơ hội và nó không nằm ở số học: chuỗi nhân tính **tổng** thay vì tính **phần chênh so với việc không làm gì**. Mọi mắt xích đều đúng và kết quả vẫn trả lời sai câu hỏi.

Quy tắc rút ra: kịch bản nền — điều gì xảy ra nếu không làm gì — phải được ước lượng riêng và trừ đi. Bỏ qua nó thì mọi cơ hội đều trông đáng làm.

## Góc Khuất & Ngộ Nhận

Về sự chính xác giả: viết 6.647.000.000 thay vì "khoảng 6,6 tỉ" khiến người đọc tin vào độ chính xác mà chuỗi giả định không hề có. Số chữ số có nghĩa nên khớp với mắt xích yếu nhất, và mắt xích yếu nhất thường chỉ có một chữ số.

Về chi phí: ước lượng cơ hội hay chỉ tính doanh thu. Một tính năng mang về 2,5 tỉ và tốn 1,8 tỉ chi phí xây dựng cùng vận hành năm đầu là một quyết định khác hẳn, và phía chi phí thường không được đưa vào cùng bảng.

**Hiểu lầm:** "Ước lượng chi tiết hơn thì chính xác hơn."
**Thực tế:** Thêm mắt xích vào chuỗi thường làm khoảng dao động rộng ra, vì mỗi mắt xích mang thêm bất định. Chuỗi bốn bước với ba nguồn tốt đáng tin hơn chuỗi mười bước toàn phán đoán. **Vì sao nghe hợp lý:** chi tiết là dấu hiệu của sự cẩn thận trong hầu hết công việc, và ở đây nó là dấu hiệu của việc tích lũy thêm giả định.

**Hiểu lầm:** "Ước lượng sai thì vô dụng."
**Thực tế:** Mục đích của nó là phân biệt cơ hội 200 triệu với cơ hội 20 tỉ, và một ước lượng lệch hai lần vẫn làm được việc đó. Nó chỉ vô dụng khi khoảng ước lượng vắt qua ngưỡng quyết định — và khi ấy điều cần làm là nói ra, không phải chọn điểm giữa. **Vì sao nghe hợp lý:** "sai" nghe như hỏng, trong khi ở đây tiêu chuẩn là đủ tốt để chọn giữa các phương án.

**Hiểu lầm:** "Con số tổng là giá trị của cơ hội."
**Thực tế:** Giá trị là phần chênh so với việc không làm gì. Doanh thu vẫn đến qua đường khác thì không được tính vào. **Vì sao nghe hợp lý:** tổng dễ tính hơn phần gia tăng, và nó luôn là con số lớn hơn — hai lý do khiến nó được chọn mà không ai bàn.

## Nếu Bạn Dạy Lại Điều Này...

Mở đầu bằng "tính năng này đáng 8 tỉ" và hỏi cả lớp phản đối thế nào. Sau vài phút bế tắc, viết chuỗi bốn mắt xích lên bảng và hỏi lại. Số lượng câu hỏi bật ra ngay lập tức là bài học.

Hạt giống bài tập: cho một chuỗi ước lượng đã hoàn chỉnh và yêu cầu tìm phần doanh thu sẽ đến kể cả khi không xây gì.

## Tự Kiểm Tra Nhanh

**1. Vì sao chuỗi giả định quan trọng hơn con số cuối?**

<details><summary>Đáp án</summary>

Vì nó tạo ra chỗ để người khác phản đối. Con số không chuỗi chỉ có thể được tin hoặc bị bác, nên quyết định rơi về việc ai tự tin hơn. Chuỗi cũng là thứ duy nhất cho phép kiểm chứng lại sau sáu tháng để biết giả định nào của mình hay sai.
</details>

**2. Khoảng ước lượng từ 1,6 tới 12,3 tỉ, ngưỡng quyết định là 3 tỉ. Kết luận gì?**

<details><summary>Đáp án</summary>

Rằng dữ liệu chưa đủ để quyết, vì khoảng vắt qua ngưỡng. Việc cần làm là tìm dữ liệu cho mắt xích nhạy nhất — thường là mắt xích vừa ảnh hưởng lớn nhất vừa mang nhãn phán đoán — chứ không phải chọn điểm giữa và trình bày như thể chắc chắn.
</details>

**3. Lỗi phổ biến nhất trong ước lượng cơ hội là gì?**

<details><summary>Đáp án</summary>

Tính tổng thay vì tính phần chênh so với việc không làm gì. Doanh thu vốn đã đến qua đường khác không phải giá trị mới. Mọi mắt xích trong chuỗi có thể đúng và kết quả vẫn trả lời sai câu hỏi.
</details>

Ghi chú tiếp theo là [Tiêu chí nghiệm thu](product.acceptance-criteria.md), nơi ước lượng trở thành điều kiện mà người khác kiểm được.
