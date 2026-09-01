---
id: data-analyst.analytics.simpson-paradox
title: Simpson's paradox
domain: data-analyst
type: pitfall
tags: [analytics, analysis-method, simpson, paradox]
status: draft
ai_summary: A trend present in every subgroup reverses when the groups are pooled, caused by uneven group sizes acting as a confounder.
relationships:
  builds_on: [data-analyst.sql.aggregation-grain-error]
  prerequisite_of: []
  commonly_confused_with: [data-analyst.analytics.sampling-bias]
created: 2026-09-01
updated: 2026-09-01
version_sensitive: false
---

# Simpson's paradox

**Tóm tắt bản chất:** Một xu hướng xuất hiện ở **mọi** nhóm con có thể đảo chiều khi gộp các nhóm lại. Nguyên nhân không phải lỗi số học mà là kích thước nhóm không đều, và nó khiến "nhìn tổng thể" và "nhìn chi tiết" cho ra hai kết luận đối nghịch, cả hai đều tính đúng.

## Nỗi Đau & Động Lực

Phiên bản B của trang đích thắng phiên bản A ở khách hàng doanh nghiệp: 8,1% so với 6,4%. B cũng thắng ở khách hàng cá nhân: 3,2% so với 2,6%. Gộp lại, A thắng B: 4,9% so với 4,1%.

Chẳng có lỗi nào ở đây. Ba con số đều tính đúng trên cùng một tập dữ liệu. B thắng ở cả hai nhóm và thua khi gộp, vì lưu lượng của B nghiêng nhiều hơn về nhóm cá nhân — nhóm vốn có tỉ lệ chuyển đổi thấp hơn ở cả hai phiên bản.

Điều nguy hiểm là **cả hai kết luận đều có thể được bảo vệ bằng số liệu**. Ai muốn chọn A sẽ chiếu bảng tổng. Ai muốn chọn B sẽ chiếu bảng cắt theo phân khúc. Chẳng bên nào gian lận, và cuộc họp cũng chẳng giải quyết được bằng cách yêu cầu tính lại.

Cái giá không chỉ là một quyết định sai. Đắt hơn là việc tổ chức học được rằng số liệu có thể chứng minh bất cứ điều gì, và niềm tin ấy đắt hơn nhiều so với việc chọn nhầm một trang đích.

## Cơ Chế Tác Động

Hai điều kiện phải cùng đúng thì nghịch lý mới xuất hiện:

1. Có một biến nhóm ảnh hưởng tới kết quả — ở đây, loại khách hàng.
2. Phân bố của biến ấy khác nhau giữa các nhánh so sánh — B nhận nhiều lưu lượng cá nhân hơn.

Điều kiện thứ hai làm biến nhóm thành **biến gây nhiễu**. Biến ấy ảnh hưởng cả tới việc bạn rơi vào nhánh nào lẫn tới kết quả.

Bằng số, để thấy nó không có gì huyền bí:

```
              A: chuyển đổi / lượt      B: chuyển đổi / lượt
doanh nghiệp     64 / 1.000  = 6,4%       81 / 1.000  = 8,1%
cá nhân           26 / 1.000  = 2,6%      288 / 9.000  = 3,2%
gộp               90 / 2.000  = 4,5%      369 / 10.000 = 3,7%
```

B tốt hơn ở từng dòng. Khi gộp, A có một nửa lưu lượng ở nhóm dễ chuyển đổi còn B chỉ có một phần mười. Trung bình có trọng số của B bị kéo về phía con số thấp, và trọng số mới là thứ quyết định.

Phép kiểm, chạy trước mọi so sánh:

```sql
SELECT nhanh, phan_khuc,
       COUNT(*) AS luot,
       COUNT(*) * 1.0 / SUM(COUNT(*)) OVER (PARTITION BY nhanh) AS ti_trong
FROM thi_nghiem
GROUP BY 1, 2;
```

Trong ví dụ ở trên, nhóm doanh nghiệp chiếm 50% lưu lượng của A và 10% của B — lệch năm lần, và đủ để đảo chiều kết luận. Bất kỳ mức lệch nào cũng làm con số gộp bớt so sánh được; mức lệch bao nhiêu là quá nhiều thì phụ thuộc khoảng cách giữa các nhóm, nên hãy đọc cả hai bảng chứ đừng đặt một ngưỡng. Phép kiểm này rẻ, và gần như không ai chạy nó.

## Bản Đồ Quyết Định

| Tình huống | Tin con số nào | Vì sao |
|---|---|---|
| thí nghiệm ngẫu nhiên hóa đúng | con số gộp | ngẫu nhiên hóa làm phân bố nhóm bằng nhau |
| phân bố nhóm lệch giữa hai nhánh | con số theo nhóm | con số gộp đo cả thành phần lẫn hiệu quả |
| biến nhóm nằm **sau** can thiệp | con số gộp | cắt theo nó là cắt theo kết quả, làm hỏng so sánh |
| không biết biến nhóm nào quan trọng | chưa kết luận | dữ liệu không tự nói ra biến gây nhiễu |

Dòng thứ ba là bẫy ngược, và nó ít được nói tới. Nếu phiên bản B khiến nhiều người đăng ký dùng thử hơn, thì cắt kết quả theo "đã đăng ký thử hay chưa" là cắt theo một hệ quả của chính can thiệp. Việc cắt ấy tạo ra nghịch lý chứ không phát hiện ra nó.

Quy tắc phân biệt: chỉ cắt theo các biến đã tồn tại **trước** khi can thiệp xảy ra. Loại khách hàng, quốc gia, thiết bị thì được. Hành vi sau khi thấy trang thì không.

Dòng cuối là câu trả lời trung thực trong phần lớn trường hợp thực tế. Chẳng thuật toán nào tìm ra biến gây nhiễu; nó đến từ hiểu biết về lĩnh vực, và một biến chưa ai nghĩ tới vẫn đang gây nhiễu bất kể bạn cắt bao nhiêu chiều.

## Case Study Thực Chiến: A/B test kết luận ngược

Lược đồ tối thiểu:

```
thi_nghiem (user_id, nhanh, phan_khuc, da_chuyen_doi)
```

Số liệu như bảng ở trên. Đội tăng trưởng chiếu con số gộp và đề xuất giữ A. Đội sản phẩm chiếu con số theo phân khúc và đề xuất chọn B.

Câu hỏi đúng không phải "số nào đúng" mà là **vì sao phân bố lệch**. Kiểm ra thì thấy: thí nghiệm phân nhánh theo nguồn truy cập chứ không ngẫu nhiên hóa theo người dùng, và nguồn quảng cáo — chủ yếu là khách cá nhân — được đẩy hết vào nhánh B.

Thí nghiệm này không đo được gì về trang đích. Nó bị hỏng từ khâu phân nhánh, và không phép phân tích hậu kỳ nào sửa được. Kết luận đúng là chạy lại với ngẫu nhiên hóa theo người dùng.

**Biến thể khó hơn, nơi cách hiểu trên gây hiểu lầm.** Giả sử thí nghiệm ngẫu nhiên hóa đúng, phân bố phân khúc bằng nhau, nhưng khi cắt theo thiết bị thì B thắng trên di động và thua trên máy tính để bàn.

Trường hợp này **không** phải nghịch lý Simpson — con số gộp không đảo chiều, nó chỉ là trung bình của hai hiệu ứng trái dấu. Hiện tượng này gọi là tương tác, và cách xử lý khác hẳn: Simpson đòi bạn sửa phép so sánh, còn tương tác đòi bạn thừa nhận rằng một câu trả lời duy nhất không tồn tại.

Với ngẫu nhiên hóa đúng, con số gộp **là** ước lượng không thiên lệch của hiệu ứng trung bình. Ước lượng ấy vẫn có thể vô dụng, khi hiệu ứng trung bình che mất hai nhóm cần hai quyết định khác nhau. Đúng và hữu ích là hai chuyện.

## Góc Khuất & Ngộ Nhận

Hiện tượng không giới hạn ở hai nhóm hay ở tỉ lệ. Hiện tượng này xảy ra với ba nhóm trở lên, với trung bình, với hệ số hồi quy, và có thể đảo chiều nhiều lần khi thêm dần các biến vào. Chẳng số chiều nào là "đủ".

Về hồi quy: thêm một biến vào mô hình có thể đảo dấu hệ số của biến khác, và đó chính là nghịch lý Simpson dưới dạng liên tục. Một hệ số đổi dấu khi thêm biến kiểm soát là tín hiệu cần dừng lại chứ không phải kết quả cần báo cáo.

**Hiểu lầm:** "Cắt càng nhiều chiều càng gần sự thật."
**Thực tế:** Mỗi lần cắt làm mẫu nhỏ đi, và dưới một ngưỡng thì bạn đang đọc nhiễu. Cắt tới khi tìm được kết quả mong muốn có tên riêng, và nó không phải phân tích. **Vì sao nghe hợp lý:** cắt đúng một chiều đã cứu được kết luận một lần, và bài học ấy được khái quát thành "cắt thì tốt".

**Hiểu lầm:** "Nghịch lý Simpson là một lỗi thống kê hiếm gặp."
**Thực tế:** Đây là hệ quả số học của trung bình có trọng số, không phải lỗi, và xuất hiện bất cứ khi nào kích thước nhóm lệch — tức là gần như mọi dữ liệu quan sát. **Vì sao nghe hợp lý:** cái tên nghe như một nghịch lý, và nghịch lý gợi ý thứ gì đó lạ thường.

**Hiểu lầm:** "Có dữ liệu chi tiết thì tránh được."
**Thực tế:** Dữ liệu chi tiết cho phép bạn cắt, nhưng không nói cho bạn biết nên cắt theo biến nào. Biến gây nhiễu quan trọng nhất thường là biến chưa được ghi lại. **Vì sao nghe hợp lý:** trong các ví dụ dạy học, biến gây nhiễu luôn có sẵn trong bảng — vì người ra ví dụ đã đặt nó ở đó.

## Nếu Bạn Dạy Lại Điều Này...

Mở đầu bằng bảng ba dòng ở phần cơ chế, che dòng "gộp", và hỏi phiên bản nào tốt hơn. Cả lớp sẽ chọn B. Sau đó bỏ tấm che.

Hạt giống bài tập: cho một kết quả A/B test có phân bố phân khúc lệch, và yêu cầu quyết định — nhưng chấm điểm câu trả lời "thí nghiệm này hỏng, phải chạy lại" cao hơn mọi câu chọn A hoặc B.

## Tự Kiểm Tra Nhanh

**1. Hai điều kiện nào phải cùng đúng để nghịch lý xuất hiện?**

<details><summary>Đáp án</summary>

Một biến nhóm ảnh hưởng tới kết quả, và phân bố của biến ấy lệch giữa các nhánh so sánh. Thiếu điều kiện thứ hai thì con số gộp là trung bình có trọng số hợp lệ và không đảo chiều.
</details>

**2. Vì sao không được cắt theo một biến xảy ra sau can thiệp?**

<details><summary>Đáp án</summary>

Vì biến ấy là hệ quả của can thiệp, nên cắt theo nó là so sánh hai nhóm đã được chọn bởi chính thứ đang được đo. Việc cắt tạo ra sai lệch chứ không phát hiện ra nó. Chỉ cắt theo biến tồn tại trước can thiệp.
</details>

**3. B thắng trên di động, thua trên máy tính, con số gộp không đảo chiều. Đây có phải Simpson không?**

<details><summary>Đáp án</summary>

Không, đó là tương tác. Simpson đòi con số gộp đảo ngược so với mọi nhóm con. Tương tác thì con số gộp là trung bình đúng của hai hiệu ứng trái dấu — nó không sai, nó chỉ che mất việc hai nhóm cần hai quyết định khác nhau.
</details>

Ghi chú tiếp theo là [Lực thống kê](analytics.statistical-power.md), nơi câu hỏi chuyển từ "kết luận có đúng chiều không" sang "mẫu có đủ để kết luận gì không".
