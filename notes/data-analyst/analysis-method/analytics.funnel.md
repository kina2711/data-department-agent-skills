---
id: data-analyst.analytics.funnel
title: Funnel
domain: data-analyst
type: mechanism
tags: [analytics, analysis-method, funnel]
status: draft
ai_summary: Ordered steps with drop-off between them, where the definition of a step, the attribution window and the ordering rule decide the conversion rate more than user behaviour does.
relationships:
  builds_on: [data-analyst.sql.window-function]
  prerequisite_of: []
  commonly_confused_with: [data-analyst.analytics.cohort]
created: 2026-09-01
updated: 2026-09-01
version_sensitive: false
---

# Funnel

**Tóm tắt bản chất:** Phễu là chuỗi bước có thứ tự cùng tỉ lệ rơi rụng giữa chúng. Ba lựa chọn kỹ thuật — định nghĩa bước, cửa sổ quy kết, và quy tắc thứ tự — quyết định tỉ lệ chuyển đổi nhiều hơn hành vi người dùng, và cả ba thường không được ghi lại ở đâu.

## Nỗi Đau & Động Lực

"Tỉ lệ chuyển đổi của chúng ta là 3,2%." Câu này không mang thông tin cho tới khi biết ba điều: chuyển đổi từ đâu, trong bao lâu, và bước nào tính là đã hoàn thành.

Cùng một tập dữ liệu, cùng một sản phẩm, thay đổi cửa sổ quy kết từ một phiên sang bảy ngày có thể đưa 3,2% lên 5,8%. Không ai gian lận và không có truy vấn nào sai — hai con số trả lời hai câu hỏi khác nhau, và cả hai đều được gọi là "tỉ lệ chuyển đổi".

Chi phí xuất hiện khi hai đội so sánh. Đội tăng trưởng đo bằng cửa sổ bảy ngày vì họ quan tâm tới cả hành trình; đội sản phẩm đo trong phiên vì họ quan tâm tới trải nghiệm màn hình. Hai con số lệch nhau, mỗi bên tin con số của mình, và cuộc thảo luận về việc nên sửa gì trở thành cuộc thảo luận về việc ai đo đúng.

Nguy hiểm hơn: phễu tạo ra ảo giác về nguyên nhân. Thấy 60% rơi ở bước thanh toán thì kết luận trang thanh toán có vấn đề — trong khi rất có thể những người ấy chưa từng có ý định mua, và họ rơi ở bước ấy đơn giản vì đó là bước cuối.

## Cơ Chế Tác Động

Ba lựa chọn, theo thứ tự ảnh hưởng:

**Một — cửa sổ quy kết.** Người xem sản phẩm hôm nay và mua sau năm ngày có tính là đã chuyển đổi không? Trong phiên, trong ngày, trong bảy ngày, hay không giới hạn. Càng rộng thì tỉ lệ càng cao, và không có lựa chọn nào đúng sẵn.

**Hai — có bắt buộc đúng thứ tự không.** Phễu nghiêm ngặt đòi người dùng đi qua các bước theo đúng trình tự. Phễu lỏng chỉ cần họ đã làm cả ba việc, thứ tự nào cũng được. Trên sản phẩm thật, người ta thêm vào giỏ rồi quay lại xem sản phẩm khác rồi mới thanh toán — phễu nghiêm ngặt loại họ ra.

**Ba — mẫu số của từng bước.** Tỉ lệ ở bước 3 tính trên số người vào bước 1 hay số người vào bước 2? Cái đầu là tỉ lệ tích lũy, cái sau là tỉ lệ từng bước, và chúng nói hai chuyện khác nhau. Tỉ lệ từng bước chỉ ra chỗ hỏng; tỉ lệ tích lũy cho biết quy mô thiệt hại.

Cấu trúc truy vấn cho phễu nghiêm ngặt, dùng hàm cửa sổ:

```sql
WITH su_kien AS (
  SELECT user_id, event_name, occurred_at,
         MIN(occurred_at) FILTER (WHERE event_name = 'view')
           OVER (PARTITION BY user_id) AS moc_bat_dau
  FROM events
)
SELECT
  COUNT(DISTINCT user_id) FILTER (WHERE event_name = 'view')     AS b1_xem,
  COUNT(DISTINCT user_id) FILTER (WHERE event_name = 'add_cart'
        AND occurred_at BETWEEN moc_bat_dau AND moc_bat_dau + INTERVAL '7 days') AS b2_gio,
  COUNT(DISTINCT user_id) FILTER (WHERE event_name = 'purchase'
        AND occurred_at BETWEEN moc_bat_dau AND moc_bat_dau + INTERVAL '7 days') AS b3_mua
FROM su_kien;
```

Điều kiện `BETWEEN moc_bat_dau AND ...` là cửa sổ quy kết viết thành mã. Bỏ nó đi thì phễu tính cả những lần mua không liên quan gì tới lần xem ấy — kể cả lần mua từ năm ngoái.

Truy vấn này vẫn **chưa** kiểm tra thứ tự: một người mua rồi mới thêm vào giỏ vẫn được đếm ở cả hai bước. Muốn nghiêm ngặt thì mỗi bước phải so mốc thời gian với bước trước, không phải với bước đầu.

## Bản Đồ Quyết Định

| Câu hỏi | Kiểu phễu | Hậu quả nếu chọn nhầm |
|---|---|---|
| "màn hình nào gây khó khăn" | nghiêm ngặt, cửa sổ trong phiên | cửa sổ rộng làm loãng tín hiệu về giao diện |
| "bao nhiêu người cuối cùng cũng mua" | lỏng, cửa sổ rộng | phễu nghiêm ngặt bỏ sót người mua theo đường vòng |
| "chiến dịch có hiệu quả không" | quy kết theo chiến dịch, cửa sổ hợp với chu kỳ mua | cửa sổ ngắn hơn chu kỳ cân nhắc thì báo cáo thất bại giả |
| "so với tháng trước" | bất kỳ, miễn **không đổi** | đổi định nghĩa giữa hai kỳ tạo ra xu hướng giả |

Dòng cuối quan trọng hơn ba dòng trên cộng lại. Định nghĩa nào cũng chấp nhận được nếu nó nhất quán; thay đổi định nghĩa giữa hai kỳ tạo ra một xu hướng hoàn toàn là hiện vật của chính phép đo.

Về mẫu số, quy tắc thực dụng: báo cáo **cả hai**. Tỉ lệ từng bước để tìm chỗ hỏng, tỉ lệ tích lũy để biết sửa nó đáng bao nhiêu tiền. Một bước rơi 60% nghe kinh khủng, nhưng nếu chỉ 2% người dùng tới được bước đó thì sửa nó gần như không đổi gì.

## Case Study Thực Chiến: 60% rơi ở bước thanh toán

Lược đồ tối thiểu:

```
events (event_id, user_id, event_name, occurred_at)
```

Phễu ba bước cho ra 100% → 34% → 14%. Bước 2 sang bước 3 mất 60%, và đội kết luận trang thanh toán có vấn đề.

Trước khi sửa, cắt phễu theo nguồn truy cập. Kết quả: người đến từ tìm kiếm tự nhiên chuyển đổi 74% ở bước cuối; người đến từ quảng cáo hiển thị chuyển đổi 9%. Con số tổng 40% là trung bình có trọng số của hai nhóm hoàn toàn khác nhau về ý định.

Trang thanh toán không có vấn đề gì với nhóm có ý định mua. Vấn đề nằm ở chỗ quảng cáo hiển thị đang mang về lưu lượng không có ý định, và không có thay đổi giao diện nào sửa được điều đó.

**Biến thể khó hơn, nơi cách hiểu trên gây hiểu lầm.** Đội tắt quảng cáo hiển thị. Tỉ lệ chuyển đổi tổng nhảy từ 14% lên 31%, và mọi người ăn mừng.

Doanh thu tuyệt đối thì giảm. 9% của một lượng lớn vẫn là một số dương, và nó vừa bị bỏ đi. Tỉ lệ chuyển đổi cải thiện vì mẫu số nhỏ lại, không vì tử số lớn lên.

Quy tắc rút ra: mọi tỉ lệ đều có thể cải thiện bằng cách thu hẹp mẫu số, và cách ấy hầu như luôn dễ hơn cách làm tăng tử số. Một chỉ số tỉ lệ không kèm số tuyệt đối là một chỉ số có thể tối ưu theo hướng có hại — và người tối ưu nó thường không hề có ý định ấy.

## Góc Khuất & Ngộ Nhận

Về `COUNT(DISTINCT)` ở mỗi bước: nó không cộng dồn được giữa các ngày, nên một phễu tổng hợp trước theo ngày không cho ra phễu của tháng. Phải tính lại từ sự kiện chi tiết.

Về dữ liệu sự kiện: sự kiện mất mát không đồng đều giữa các bước. Trình chặn quảng cáo chặn sự kiện xem nhiều hơn sự kiện thanh toán, vì bước thanh toán thường được ghi ở phía máy chủ. Hệ quả là mẫu số bị thiếu nhiều hơn tử số, và tỉ lệ chuyển đổi bị thổi lên. Phễu trộn sự kiện phía trình duyệt với sự kiện phía máy chủ hầu như luôn lạc quan hơn thực tế.

**Hiểu lầm:** "Bước rơi nhiều nhất là chỗ cần sửa."
**Thực tế:** Bước rơi nhiều nhất thường là bước tự nhiên nhất để rơi — bước cuối, nơi người không có ý định mua dừng lại. Chỗ đáng sửa là bước có tỉ lệ rơi lệch nhiều nhất so với phân khúc tương đương. **Vì sao nghe hợp lý:** con số lớn nhất thu hút sự chú ý, và biểu đồ phễu được thiết kế để làm đúng việc đó.

**Hiểu lầm:** "Tỉ lệ chuyển đổi là một thuộc tính của sản phẩm."
**Thực tế:** Nó là thuộc tính của bộ ba sản phẩm, lưu lượng và định nghĩa đo. Đổi nguồn lưu lượng mà không đụng vào sản phẩm đã đủ làm nó thay đổi gấp đôi. **Vì sao nghe hợp lý:** nó được báo cáo như một con số duy nhất cho cả sản phẩm, và cách trình bày ấy che mất hai thành phần kia.

**Hiểu lầm:** "Phễu cho biết người dùng bỏ đi vì sao."
**Thực tế:** Phễu cho biết họ bỏ đi ở **đâu**. Lý do không nằm trong dữ liệu sự kiện, và mọi câu trả lời "vì sao" rút ra từ một biểu đồ phễu đều là giả thuyết. **Vì sao nghe hợp lý:** vị trí và nguyên nhân trùng nhau đủ thường xuyên để thói quen suy diễn ấy được củng cố nhiều lần trước khi nó sai một lần đắt giá.

## Nếu Bạn Dạy Lại Điều Này...

Mở đầu bằng cùng một tập dữ liệu chạy qua ba cửa sổ quy kết khác nhau, cho ra ba tỉ lệ chuyển đổi khác nhau, không nói trước rằng chúng cùng dữ liệu. Để lớp tranh luận xem con số nào đúng.

Hạt giống bài tập: cho một phễu tổng có tỉ lệ 14% và yêu cầu cắt theo nguồn truy cập, rồi hỏi hành động nào nên làm — và hành động ấy có làm doanh thu tăng hay không.

## Tự Kiểm Tra Nhanh

**1. Ba lựa chọn nào quyết định tỉ lệ chuyển đổi nhiều hơn hành vi người dùng?**

<details><summary>Đáp án</summary>

Cửa sổ quy kết, quy tắc thứ tự nghiêm ngặt hay lỏng, và mẫu số của từng bước. Cả ba đều là lựa chọn kỹ thuật, thường không được ghi lại, và mỗi cái đều có thể làm con số thay đổi gấp rưỡi trở lên.
</details>

**2. Tỉ lệ chuyển đổi tăng từ 14% lên 31% sau khi tắt một kênh quảng cáo. Đó có phải cải thiện không?**

<details><summary>Đáp án</summary>

Không nhất thiết. Mẫu số nhỏ lại chứ tử số chưa chắc lớn lên; doanh thu tuyệt đối có thể đã giảm. Mọi chỉ số tỉ lệ cần đi kèm số tuyệt đối, nếu không nó có thể được tối ưu theo hướng có hại.
</details>

**3. Vì sao phễu trộn sự kiện trình duyệt và sự kiện máy chủ thường lạc quan?**

<details><summary>Đáp án</summary>

Vì mất mát sự kiện không đồng đều: trình chặn quảng cáo và lỗi mạng làm mất sự kiện phía trình duyệt — thường là các bước đầu — nhiều hơn sự kiện phía máy chủ ở bước cuối. Mẫu số thiếu nhiều hơn tử số nên tỉ lệ bị thổi lên.
</details>

Ghi chú tiếp theo là [Thiên lệch sống sót](analytics.survivorship-bias.md), nơi những người đã rơi khỏi phễu biến mất khỏi mọi phép trung bình.
