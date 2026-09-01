---
id: data-analyst.product.stakeholder-decision
title: Stakeholder decision
domain: data-analyst
type: pattern
tags: [product, stakeholder-work, stakeholder, decision]
status: draft
ai_summary: The decision a piece of analysis actually serves, named before work begins, together with who owns it and what result would change it.
relationships:
  builds_on: [data-analyst.modelling.semantic-layer]
  prerequisite_of: [data-analyst.product.opportunity-sizing]
  commonly_confused_with: [data-analyst.product.acceptance-criteria]
created: 2026-09-01
updated: 2026-09-01
version_sensitive: false
---

# Stakeholder decision

**Tóm tắt bản chất:** Quyết định của bên liên quan là hành động cụ thể mà một phân tích phục vụ, được gọi tên **trước khi** làm, cùng với ai là người ra quyết định và kết quả nào sẽ khiến họ chọn khác đi. Không trả lời được câu thứ ba thì phân tích ấy không cần tồn tại.

## Nỗi Đau & Động Lực

Yêu cầu đến dưới dạng: "Cho tôi xem dữ liệu về tỉ lệ rời bỏ." Người phân tích làm ba ngày, giao một bảng điều khiển đầy đủ, và không có gì xảy ra sau đó.

Bảng điều khiển không tệ. Nó trả lời một câu hỏi mà chẳng ai định làm gì với câu trả lời. Người yêu cầu muốn biết tỉ lệ rời bỏ vì họ cảm thấy nên biết, và cảm giác ấy không dẫn tới quyết định nào.

Phiên bản đắt hơn: yêu cầu **có** một quyết định phía sau, nhưng nó không được nói ra, nên phân tích trả lời sai câu hỏi. Người yêu cầu đang cân nhắc có nên đầu tư vào một tính năng giữ chân hay không; họ hỏi về tỉ lệ rời bỏ tổng thể; thứ họ cần là tỉ lệ rời bỏ của nhóm mà tính năng ấy nhắm tới, cùng ước lượng nó có thể giảm bao nhiêu. Ba ngày làm đúng, cho một câu hỏi lệch.

Cái giá không dừng ở ba ngày. Bên yêu cầu học được rằng đội dữ liệu giao thứ không dùng được, và lần sau họ tự kéo số trong công cụ BI — nơi không ai kiểm tra grain.

## Cơ Chế Tác Động

Hỏi ba câu này trước khi mở trình soạn thảo SQL:

**Một — quyết định nào?** Không phải "câu hỏi nào" mà "hành động nào". Câu trả lời hợp lệ có dạng động từ: tăng ngân sách, gỡ tính năng, đổi giá, không làm gì cả. "Hiểu rõ hơn về khách hàng" không phải quyết định.

**Hai — ai quyết?** Một người có tên. Nếu người yêu cầu không phải người quyết, phân tích phải phục vụ tiêu chí của người quyết, không phải của người yêu cầu.

**Ba — kết quả nào đổi được quyết định?** Trong ba câu, đây là câu mạnh nhất. Nếu người quyết sẽ làm cùng một việc bất kể kết quả ra sao, phân tích không có giá trị và nên nói thẳng điều đó. Nếu họ trả lời được — "nếu nhóm này chiếm dưới 5% doanh thu thì tôi bỏ qua" — thì bạn vừa nhận được cả phạm vi lẫn tiêu chí dừng.

Đó cũng là câu khó hỏi nhất, vì nghe như một lời thách thức. Hỏi thế này thì ít gây phản ứng hơn: "Giả sử con số ra rất thấp — anh sẽ làm gì? Còn nếu rất cao?" Hai câu trả lời khác nhau nghĩa là phân tích có giá trị. Hai câu trả lời giống nhau nghĩa là chưa.

Kết quả của ba câu hỏi được viết thành một đoạn ngắn và gửi lại để xác nhận trước khi bắt đầu:

```
Quyết định: có mở rộng gói doanh nghiệp sang thị trường Indonesia trong quý sau không
Người quyết: [tên], Giám đốc kinh doanh khu vực
Đổi quyết định khi: quy mô thị trường có thể tiếp cận dưới 40 tỉ, hoặc thời gian
                    hoàn vốn trên 18 tháng
Hạn cần: 12 tháng 9, trước phiên duyệt ngân sách
```

Viết đoạn ấy mất mười phút, và nó chặn phần lớn các phân tích không dùng được.

## Bản Đồ Quyết Định

| Tình huống | Việc phải làm | Hậu quả nếu bỏ qua |
|---|---|---|
| yêu cầu không có quyết định phía sau | hỏi, và chấp nhận câu trả lời "không có" | ba ngày cho một bảng điều khiển không ai mở |
| người yêu cầu khác người quyết | tìm tiêu chí của người quyết | phân tích đúng, thuyết phục sai người |
| quyết định đã được ra rồi | nói rõ đây là phân tích hậu kiểm | bị dùng làm bằng chứng biện minh |
| mọi kết quả dẫn tới cùng hành động | báo lại và đề xuất dừng | tốn công cho một kết luận không đổi gì |
| hạn quyết định trước hạn phân tích | thu hẹp phạm vi cho vừa hạn | giao một phân tích hoàn hảo sau khi đã quyết |

Dòng thứ ba đáng nói riêng. Một yêu cầu đến sau khi quyết định đã ra vẫn có thể hợp lệ — để học cho lần sau, hoặc để báo cáo kết quả. Rắc rối chỉ đến khi người phân tích tưởng mình đang hỗ trợ quyết định, và khi kết quả trái với điều đã quyết thì bị yêu cầu "kiểm tra lại". Nói rõ vai trò từ đầu tránh được tình huống ấy.

Dòng cuối là đánh đổi mà người phân tích hay làm sai. Bản đủ tốt giao trước phiên duyệt ngân sách thì có giá trị. Phân tích hoàn chỉnh giao sau đó có giá trị bằng không. Hạn của quyết định, không phải hạn của công việc, mới là ràng buộc thật.

## Case Study Thực Chiến: bảng điều khiển tỉ lệ rời bỏ không ai mở

Yêu cầu ban đầu: "Cho tôi xem dữ liệu về tỉ lệ rời bỏ."

Hỏi ba câu và nhận được: quyết định là có nên xây tính năng nhắc gia hạn tự động hay không; người quyết là trưởng nhóm sản phẩm, không phải người đang hỏi; và quyết định sẽ đổi nếu nhóm khách rời bỏ **do quên gia hạn** chiếm trên 15% tổng số rời bỏ.

Phạm vi thu từ "dữ liệu về tỉ lệ rời bỏ" xuống một con số duy nhất kèm khoảng tin cậy. Thời gian từ ba ngày xuống bốn giờ. Kết quả 6%, khoảng tin cậy 95% từ 4,1% tới 8,3% — toàn bộ khoảng nằm dưới ngưỡng 15%, nên quyết định không xây được ra trong cùng tuần.

Bảng điều khiển đầy đủ vẫn có thể hữu ích một ngày nào đó. Chỉ là nó không phải thứ cần làm cho quyết định này.

**Biến thể khó hơn, nơi cách hiểu trên gây hiểu lầm.** Con số ra 6%, dưới ngưỡng 15%, nên đề xuất là không xây. Trưởng nhóm sản phẩm quyết định xây.

Chuyện này không phải thất bại của phân tích, và cũng không phải người quyết hành xử phi lý. Ngưỡng 15% được đặt ra khi chưa ai biết con số; sau khi thấy 6% kèm mô tả nhóm khách ấy, họ có thêm thông tin mà ngưỡng ban đầu không tính tới — chẳng hạn nhóm ấy toàn khách giá trị cao.

Ngưỡng đặt trước có hai công dụng, và chỉ một trong hai là ràng buộc người quyết. Chính yếu là **định hình phạm vi phân tích**: nó cho biết cần đo chính xác tới mức nào và không cần đo gì. Thứ yếu là làm cho việc đổi ý trở nên rõ ràng — người quyết vẫn có quyền đổi, nhưng bây giờ họ phải nói ra lý do, và lý do ấy được ghi lại.

Quy tắc rút ra: mục tiêu của việc hỏi trước không phải trói người quyết vào một quy tắc. Mục tiêu là làm cho lập luận hiện ra thay vì nằm trong đầu ai đó.

## Góc Khuất & Ngộ Nhận

Về quyết định không làm gì: "không làm gì" là một quyết định hợp lệ và thường là quyết định đúng, nhưng nó hiếm khi được kể lại. Một phân tích dẫn tới việc không xây một tính năng đã tiết kiệm ba tháng kỹ thuật; chẳng chỉ số nào ghi nhận điều đó.

Về nhiều bên liên quan: khi ba người cùng cần một phân tích cho ba quyết định khác nhau, đó là ba phân tích. Ép chúng vào một bản giao thường cho ra một tài liệu dài mà mỗi người chỉ đọc một phần và không ai đủ tin để hành động.

**Hiểu lầm:** "Hỏi về quyết định là làm khó người yêu cầu."
**Thực tế:** Phần lớn người yêu cầu biết rõ quyết định của mình và chỉ chưa nghĩ tới việc nói ra, vì họ tưởng đội dữ liệu cần câu hỏi chứ không cần bối cảnh. Câu hỏi thường được đón nhận tốt. **Vì sao nghe hợp lý:** nó nghe như đòi hỏi biện minh, và người ta hình dung phản ứng phòng thủ trước khi thử.

**Hiểu lầm:** "Phân tích khám phá không cần quyết định."
**Thực tế:** Khám phá cần một câu hỏi và một hạn mức thời gian, và câu hỏi ấy nên là "chúng ta có nên đầu tư sâu hơn vào hướng này không" — bản thân nó là một quyết định. Khám phá không giới hạn là cách một tuần trở thành một tháng. **Vì sao nghe hợp lý:** khám phá thật sự khác với phân tích phục vụ quyết định, và sự khác biệt ấy bị mở rộng thành sự miễn trừ.

**Hiểu lầm:** "Đổi ý nghĩa là phân tích đã thất bại."
**Thực tế:** Ngưỡng đặt trước dùng để định hình phạm vi, không để trói người quyết. Đổi ý sau khi có thêm thông tin là hành vi hợp lý; điều cần có là lý do được nói ra và ghi lại. **Vì sao nghe hợp lý:** người phân tích đã bỏ công theo một tiêu chí, nên việc tiêu chí ấy bị bỏ qua cảm giác như công sức bị phí.

## Nếu Bạn Dạy Lại Điều Này...

Mở đầu bằng một yêu cầu thật, mơ hồ, và để học viên bắt tay vào thiết kế phân tích. Sau năm phút, dừng lại và hỏi ba câu. Phần lớn sẽ nhận ra họ đang thiết kế cho một quyết định họ tự tưởng tượng.

Hạt giống bài tập: cho một yêu cầu và bắt viết đoạn xác nhận bốn dòng ở trên trước khi được phép viết bất kỳ dòng SQL nào.

## Tự Kiểm Tra Nhanh

**1. Ba câu hỏi phải trả lời trước khi bắt đầu phân tích là gì?**

<details><summary>Đáp án</summary>

Quyết định nào — dưới dạng một động từ, không phải một chủ đề. Ai quyết — một người có tên. Và kết quả nào sẽ khiến họ chọn khác đi. Câu thứ ba là câu mạnh nhất: nếu mọi kết quả dẫn tới cùng một hành động thì phân tích không có giá trị.
</details>

**2. Người yêu cầu không phải người ra quyết định. Phục vụ tiêu chí của ai?**

<details><summary>Đáp án</summary>

Của người ra quyết định. Kết quả thuyết phục đúng người yêu cầu nhưng không chạm tới tiêu chí của người quyết sẽ dừng lại ở bàn của người trung gian, và công sức bỏ ra vẫn không dẫn tới hành động nào.
</details>

**3. Ngưỡng đặt trước để làm gì, nếu người quyết vẫn có quyền đổi ý?**

<details><summary>Đáp án</summary>

Để định hình phạm vi — nó cho biết cần đo chính xác tới đâu và không cần đo gì. Thứ yếu là buộc việc đổi ý phải kèm lý do được nói ra và ghi lại, thay vì diễn ra âm thầm trong đầu ai đó.
</details>

Ghi chú tiếp theo là [Ước lượng cơ hội](product.opportunity-sizing.md), nơi câu "đáng bao nhiêu" được trả lời bằng những giả định có thể tranh luận được.
