---
id: data-analyst.product.acceptance-criteria
title: Acceptance criteria
domain: data-analyst
type: pattern
tags: [product, stakeholder-work, acceptance, criteria]
status: draft
ai_summary: Conditions checkable by someone who did not write them, fixed before implementation starts, so that "done" is a fact rather than an opinion.
relationships:
  builds_on: [data-analyst.product.opportunity-sizing]
  prerequisite_of: []
  commonly_confused_with: [data-analyst.product.stakeholder-decision]
created: 2026-09-01
updated: 2026-09-01
version_sensitive: false
---

# Acceptance criteria

**Tóm tắt bản chất:** Tiêu chí nghiệm thu là các điều kiện mà **người không viết ra chúng** vẫn kiểm được, chốt trước khi bắt tay làm. Chúng biến "xong chưa" từ một ý kiến thành một dữ kiện, và phép thử của một tiêu chí tốt là hai người kiểm độc lập cho cùng kết luận.

## Nỗi Đau & Động Lực

Bảng điều khiển được giao. Người yêu cầu nói "gần được rồi, nhưng...", và vòng lặp bắt đầu. Ba tuần sau nó vẫn "gần được", đã qua bảy vòng sửa, và không ai nói được còn thiếu gì.

Yêu cầu không hề thay đổi. Chưa bao giờ có một điều kiện nào để đối chiếu, nên "xong" được quyết bằng cảm giác. Cảm giác không hội tụ.

Với công việc dữ liệu, vấn đề còn một tầng nữa. "Bảng điều khiển hiển thị doanh thu" là điều kiện có vẻ kiểm được, cho tới khi hai người nhìn cùng một bảng và bất đồng về việc con số ấy có đúng không. Tiêu chí phải nói tới **giá trị đối chiếu**, không chỉ tới sự tồn tại của cột.

Thiếu tiêu chí không làm hỏng lần giao đầu. Cái giá rơi vào vòng thứ tư trở đi, khi cả hai bên đã mệt và bắt đầu nhượng bộ đúng những thứ lẽ ra không nên nhượng bộ.

## Cơ Chế Tác Động

Một tiêu chí kiểm được có ba thành phần:

**Một — điều kiện quan sát được.** Không phải "chính xác" mà "khớp với truy vấn đối chứng trong khoảng ±0,5%".

**Hai — người kiểm không phải người làm.** Nếu chỉ người xây kiểm được, đó không phải tiêu chí mà là ghi chú cá nhân.

**Ba — chốt trước khi bắt đầu.** Tiêu chí viết sau khi giao hàng là biện minh, không phải tiêu chí.

Với sản phẩm dữ liệu, bốn nhóm tiêu chí thường cần đủ:

| Nhóm | Ví dụ tiêu chí |
|---|---|
| tính đúng | tổng doanh thu tháng 8 khớp truy vấn đối chứng trong ±0,5% |
| độ mới | dữ liệu không cũ quá 6 giờ tại thời điểm mở |
| phạm vi | bao gồm cả 13 thị trường, kiểm bằng danh sách mã quốc gia |
| khả dụng | một người ngoài đội mở được và trả lời đúng ba câu hỏi mẫu |

Nhóm cuối hay bị bỏ nhất, và bắt được nhiều vấn đề nhất. "Một người chưa từng thấy bảng này trả lời được ba câu hỏi trong năm phút" là điều kiện kiểm được, và nó phát hiện những thứ mà kiểm tra số liệu không chạm tới.

Với tính đúng, truy vấn đối chứng phải được viết **bởi người khác** và **trước khi** xây. Viết sau thì nó có xu hướng sao chép cùng những giả định, và hai truy vấn cùng sai theo cùng một cách sẽ khớp nhau hoàn hảo.

Dung sai phải nêu rõ. `±0,5%` là một tiêu chí; "khớp" thì không, vì dữ liệu đến muộn và làm tròn tiền tệ khiến hai con số hiếm khi trùng tới từng đồng, và không có dung sai thì mọi lần kiểm đều thành một cuộc thương lượng.

## Bản Đồ Quyết Định

| Tình huống | Việc phải làm | Hậu quả nếu bỏ qua |
|---|---|---|
| trước khi bắt đầu xây | viết tiêu chí, gửi xác nhận | vòng lặp "gần được rồi" không có điểm dừng |
| tiêu chí về tính đúng | truy vấn đối chứng do người khác viết trước | hai truy vấn cùng sai theo cùng một cách |
| yêu cầu mới xuất hiện giữa chừng | thêm tiêu chí, dời hạn tương ứng | phạm vi trôi mà lịch không đổi |
| không nghĩ ra cách kiểm | yêu cầu chưa đủ rõ để làm | xây một thứ không ai xác nhận được |
| tiêu chí phụ thuộc ý kiến | đổi thành câu hỏi có đáp án đúng | "trực quan" không kiểm được |

Dòng thứ tư là công cụ chẩn đoán mạnh nhất trong bảng. Nếu không viết được cách kiểm một yêu cầu, vấn đề nằm ở yêu cầu chứ không ở người viết tiêu chí. "Bảng điều khiển phải trực quan" không kiểm được, và việc nó không kiểm được cho biết người yêu cầu chưa xác định được họ muốn gì.

Dòng thứ năm là cách sửa dòng thứ tư. "Trực quan" đổi thành "một người ngoài đội trả lời đúng câu hỏi *doanh thu tháng nào cao nhất* trong vòng một phút". Câu ấy kiểm được, và nó ép người yêu cầu nói ra bảng điều khiển này để làm gì.

Dòng thứ ba đáng nói vì nó là nơi tiêu chí phát huy tác dụng ngoài dự kiến. Khi có tiêu chí, yêu cầu mới trở thành một dòng thêm vào danh sách chứ không phải một sự bất đồng về việc công việc đã xong hay chưa — và cuộc trao đổi về lịch trở nên đơn giản hơn nhiều.

## Case Study Thực Chiến: bảy vòng sửa và một danh sách năm dòng

Bối cảnh: bảng điều khiển doanh thu cho đội bán hàng khu vực, giao lần đầu sau hai tuần, và bảy vòng sửa trong ba tuần tiếp theo.

Bảy vòng ấy rơi vào bốn loại: 2 vòng vì số liệu lệch báo cáo tài chính 1,8%, 2 vòng vì thiếu 3 trong 13 thị trường, 1 vòng vì dữ liệu cũ 30 giờ, 2 vòng về cách trình bày. Không vòng nào là yêu cầu mới — tất cả đều là những kỳ vọng chưa từng được nói ra.

Năm dòng lẽ ra đã viết trước:

```
1. Tổng doanh thu tháng gần nhất khớp báo cáo tài chính trong ±0,5%,
   đối chứng bằng truy vấn của [tên], viết trước ngày bắt đầu.
2. Có đủ 13 thị trường; kiểm bằng cách so danh sách mã quốc gia hiển thị
   với dim_thi_truong.
3. Dấu thời gian cập nhật hiển thị trên trang, và không cũ quá 6 giờ
   trong giờ làm việc.
4. Một quản lý khu vực chưa từng thấy bảng này trả lời đúng ba câu hỏi
   mẫu trong năm phút.
5. Định nghĩa doanh thu lấy từ tầng ngữ nghĩa, không viết SQL riêng.
```

Năm dòng, hai mươi phút để viết — đổi lấy ba tuần. Chúng không làm việc nhanh hơn. Bản giao đầu vẫn mất hai tuần. Nhưng ba tuần mơ hồ phía sau thu lại thành một lần kiểm có kết luận.

**Biến thể khó hơn, nơi cách hiểu trên gây hiểu lầm.** Bảng điều khiển đạt cả năm tiêu chí. Sáu tuần sau, không ai mở nó.

Cả năm tiêu chí đều được thỏa mãn, và sản phẩm vẫn thất bại. Tiêu chí nghiệm thu kiểm được rằng thứ đã xây khớp với thứ đã yêu cầu; chúng không kiểm được rằng thứ đã yêu cầu là thứ đáng xây. Câu hỏi ấy thuộc về quyết định của bên liên quan, và nó phải được trả lời trước — nếu không thì tiêu chí nghiệm thu chỉ đảm bảo bạn xây đúng một thứ sai.

Quy tắc rút ra: tiêu chí nghiệm thu là điều kiện cần cho một bản giao tốt, không phải điều kiện đủ. Chúng chặn được vòng lặp mơ hồ. Về giá trị thì chúng im lặng. Ghi chú đầu module trả lời câu còn lại, và hai ghi chú ấy chỉ có tác dụng khi đi cùng nhau.

## Góc Khuất & Ngộ Nhận

Số lượng nên nằm trong khoảng ba tới bảy. Dưới ba thì thường sót một nhóm nguy hiểm — độ mới hoặc phạm vi. Trên mười thì không ai kiểm hết, và danh sách thành nghi thức.

Về tiêu chí âm tính: đôi khi thứ quan trọng nhất là điều **không** được xảy ra — "không hiển thị dữ liệu của thị trường mà người xem không có quyền". Loại này hay bị bỏ vì nó không mô tả tính năng nào, và nó thường là loại đắt nhất khi vi phạm.

**Hiểu lầm:** "Tiêu chí nghiệm thu là việc của quản lý dự án."
**Thực tế:** Với sản phẩm dữ liệu, phần khó nhất là tiêu chí về tính đúng, và chỉ người hiểu dữ liệu mới viết được nó. Truy vấn đối chứng và dung sai là quyết định kỹ thuật. **Vì sao nghe hợp lý:** hình thức của tiêu chí — một danh sách gạch đầu dòng trong phiếu công việc — trông giống công cụ quản lý.

**Hiểu lầm:** "Viết tiêu chí làm chậm việc bắt đầu."
**Thực tế:** Hai mươi phút đổi lấy việc loại bỏ các vòng sửa không có điểm dừng. Chi phí xuất hiện ngay và lợi ích xuất hiện muộn, nên đánh đổi này luôn cảm thấy tệ hơn thực tế. **Vì sao nghe hợp lý:** chậm lúc bắt đầu là chuyện quan sát được, còn ba tuần mơ hồ tránh được thì không bao giờ được đếm.

**Hiểu lầm:** "Đạt hết tiêu chí nghĩa là thành công."
**Thực tế:** Chỉ nghĩa là bạn đã xây đúng thứ được yêu cầu. Thứ được yêu cầu có đáng xây hay không là câu hỏi khác, thuộc về giai đoạn trước. **Vì sao nghe hợp lý:** tiêu chí là thứ duy nhất có thể đánh dấu hoàn thành, và cái gì đánh dấu được thì dễ bị nhầm là mục tiêu.

## Nếu Bạn Dạy Lại Điều Này...

Mở đầu bằng yêu cầu "làm cho tôi một bảng điều khiển doanh thu trực quan và chính xác" và hỏi làm sao biết khi nào xong. Để lớp vật lộn với chữ "trực quan" một lúc trước khi giới thiệu quy tắc người-kiểm-không-phải-người-làm.

Hạt giống bài tập: cho một danh sách tiêu chí toàn tính từ và yêu cầu viết lại thành điều kiện mà người thứ ba kiểm được, kèm dung sai.

## Tự Kiểm Tra Nhanh

**1. Vì sao truy vấn đối chứng phải do người khác viết, và viết trước?**

<details><summary>Đáp án</summary>

Viết bởi cùng người thì nó sao chép cùng những giả định, và hai truy vấn cùng sai theo cùng một cách sẽ khớp nhau hoàn hảo. Viết sau khi đã xây thì nó có xu hướng được điều chỉnh cho vừa với kết quả đã có.
</details>

**2. "Bảng điều khiển phải trực quan" — sửa thành tiêu chí kiểm được thế nào?**

<details><summary>Đáp án</summary>

Đổi thành một câu hỏi có đáp án đúng và một người kiểm không thuộc đội: "một quản lý khu vực chưa từng thấy bảng này trả lời đúng câu hỏi *thị trường nào giảm mạnh nhất quý vừa rồi* trong vòng một phút". Việc phải viết như vậy cũng ép người yêu cầu nói ra bảng này dùng để làm gì.
</details>

**3. Đạt hết tiêu chí nhưng sáu tuần sau không ai dùng. Tiêu chí sai ở đâu?**

<details><summary>Đáp án</summary>

Chúng không sai. Tiêu chí nghiệm thu kiểm rằng thứ đã xây khớp thứ đã yêu cầu; chúng không kiểm rằng thứ đã yêu cầu đáng xây. Câu hỏi đó thuộc về quyết định của bên liên quan và phải được trả lời trước khi có tiêu chí nào.
</details>

Đây là ghi chú cuối của corpus Data Analyst. Đường đọc khép lại ở chỗ nó bắt đầu: [Grain](../sql-foundation/sql.grain.md) hỏi một dòng nghĩa là gì, và ghi chú này hỏi một bản giao xong nghĩa là gì — cùng một kỷ luật, ở hai đầu của công việc.
