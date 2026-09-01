---
id: data-analyst.analytics.metric-definition-drift
title: Metric definition drift
domain: data-analyst
type: pitfall
tags: [analytics, analysis-method, metric, definition, drift]
status: draft
ai_summary: The same metric name computed differently over time, making a trend an artefact of its own definition rather than of the business.
relationships:
  builds_on: [data-analyst.analytics.sampling-bias]
  prerequisite_of: []
  commonly_confused_with: [data-analyst.sql.aggregation-grain-error]
created: 2026-09-01
updated: 2026-09-01
version_sensitive: false
---

# Metric definition drift

**Tóm tắt bản chất:** Cùng một tên chỉ số được tính theo cách khác nhau qua thời gian, khiến xu hướng trở thành hiện vật của chính định nghĩa chứ không phải của doanh nghiệp. Nó khác mọi lỗi khác ở một điểm: dữ liệu đúng, truy vấn đúng ở mọi thời điểm, và cái sai nằm ở việc đem hai con số đặt cạnh nhau.

## Nỗi Đau & Động Lực

Số người dùng hoạt động hằng tháng tăng 34% trong một quý. Đội ăn mừng. Ba tháng sau, một người mới vào tình cờ đọc mã và phát hiện định nghĩa "hoạt động" đã đổi từ "có đặt đơn" sang "có mở ứng dụng" ngay đầu quý ấy.

Không ai gian lận. Thay đổi được thực hiện có lý do chính đáng — đội sản phẩm muốn theo dõi cả người đang cân nhắc — và nó được ghi trong một pull request mà không ai ngoài hai người đọc. Biểu đồ thì không có chỗ nào để ghi.

Cái giá lớn hơn con số sai. Toàn bộ chuỗi thời gian trước và sau điểm đổi trở nên không so sánh được, vĩnh viễn, trừ khi có ai tính lại lịch sử theo định nghĩa mới. Ba năm dữ liệu trở thành hai đoạn rời rạc.

Và một chi phí thứ hai, khó gỡ hơn: các quyết định đã ra dựa trên "mức tăng 34%" ấy không tự động được xem lại. Chúng tiếp tục là tiền đề cho những quyết định sau.

## Cơ Chế Tác Động

Định nghĩa trôi qua bốn đường, và chỉ đường đầu tiên là cố ý:

**Một — thay đổi có chủ đích.** Ai đó sửa công thức, thường có lý do tốt. Đây là dạng dễ xử lý nhất vì có người biết nó đã xảy ra.

**Hai — thay đổi ở thượng nguồn.** Đội kỹ thuật đổi tên sự kiện, thêm một trạng thái đơn hàng, hoặc bắt đầu ghi thêm một loại giao dịch. Công thức chỉ số không đổi một ký tự, và con số vẫn đổi.

**Ba — thay đổi phạm vi.** Công ty mở một thị trường mới, hoặc mua lại một công ty khác, và dữ liệu của nó chảy vào cùng bảng. "Tổng doanh thu" giờ đo một doanh nghiệp khác.

**Bốn — trôi ngầm.** Bộ lọc `WHERE country IN (...)` liệt kê 12 nước và không ai cập nhật khi mở nước thứ 13. Định nghĩa đứng yên trong khi thực tại đi tiếp, và đó cũng là một dạng trôi.

Đường thứ hai và thứ tư nguy hiểm nhất, vì không có thay đổi nào trong mã chỉ số để rà soát.

Phép kiểm hồi cứu, chạy khi nghi ngờ:

```sql
-- tính lại chỉ số cho mọi tháng bằng định nghĩa hôm nay
SELECT DATE_TRUNC('month', ordered_at) AS thang,
       COUNT(DISTINCT customer_id) AS theo_dinh_nghia_moi
FROM orders
WHERE status IN ('completed', 'shipped')   -- định nghĩa hiện hành
GROUP BY 1 ORDER BY 1;
```

So chuỗi này với chuỗi đã báo cáo trong quá khứ. Chỗ hai đường tách nhau là thời điểm định nghĩa đổi, và độ rộng khe hở là mức ảnh hưởng. Đây là cách duy nhất định lượng được thiệt hại sau khi sự việc đã xảy ra, và nó chỉ khả thi khi dữ liệu thô còn nguyên.

## Bản Đồ Quyết Định

| Khi | Việc phải làm | Hậu quả nếu bỏ qua |
|---|---|---|
| đổi định nghĩa | tính lại toàn bộ lịch sử theo định nghĩa mới | hai đoạn chuỗi không so sánh được |
| không tính lại được | đổi tên chỉ số | tên cũ ngầm khẳng định tính liên tục |
| thượng nguồn báo thay đổi | chạy phép kiểm hồi cứu trước khi đổi | phát hiện sau ba tháng, khi đã có quyết định |
| chỉ số dùng danh sách cứng | thay bằng truy vấn động, hoặc đặt lịch rà soát | trôi ngầm không để lại dấu vết nào |
| thấy một bước nhảy bất thường | kiểm định nghĩa **trước** khi tìm nguyên nhân kinh doanh | vài tuần điều tra một hiện vật đo lường |

Dòng thứ hai là quy tắc quan trọng nhất và ít được tuân thủ nhất. Nếu không tính lại được lịch sử, chỉ số mới phải mang tên mới. `mau_hoat_dong` và `mau_hoat_dong_v2` là hai chỉ số, và việc đặt chúng cạnh nhau trên một biểu đồ là hành động phải có chủ đích chứ không phải mặc định.

Dòng cuối đáng thành phản xạ. Trước câu hỏi "vì sao con số nhảy", câu hỏi đầu tiên luôn là "công thức có đổi không", và nó rẻ hơn mọi giả thuyết kinh doanh.

Cơ chế phòng ngừa duy nhất hoạt động ở quy mô là **định nghĩa có phiên bản**: mỗi chỉ số có một tệp, một chủ sở hữu, một lịch sử thay đổi, và biểu đồ hiển thị phiên bản đang dùng. Tầng ngữ nghĩa tồn tại chủ yếu vì lý do này.

## Case Study Thực Chiến: mức tăng 34% không có thật

Lược đồ tối thiểu:

```
orders (order_id, customer_id, ordered_at, status)
```

Chỉ số báo cáo là số khách hoạt động hằng tháng. Định nghĩa cũ:

```sql
WHERE status = 'completed'
```

Định nghĩa mới, đổi vào tháng 4:

```sql
WHERE status IN ('completed', 'shipped', 'pending')
```

Lý do đổi hợp lý: đơn `pending` là đơn thật, chỉ chưa xong khâu thanh toán. Nhưng `pending` chiếm khoảng một phần ba số đơn, nên chỉ số nhảy một bậc ngay tháng 4 và không ai gán bước nhảy ấy cho việc đổi công thức.

Tính lại lịch sử bằng định nghĩa mới cho thấy mức tăng thật của quý là 4%, không phải 34%. Cả hai con số đều đúng với định nghĩa của chúng; chỉ có việc so sánh chúng là sai.

**Biến thể khó hơn, nơi cách hiểu trên gây hiểu lầm.** Đội tính lại toàn bộ lịch sử, công bố mức 4%, và coi vấn đề đã đóng.

Sáu tháng sau chỉ số lại nhảy. Lần này không ai đụng vào công thức — đội kỹ thuật đã thêm trạng thái `awaiting_stock`, và những đơn trước kia mang `pending` giờ mang trạng thái mới. Danh sách cứng trong mệnh đề `IN` không biết điều đó, nên nó lặng lẽ loại một nhóm đơn ra.

Đây là trôi kiểu thứ tư, và việc tính lại lịch sử lần trước không phòng được nó. Chỉ số dựa trên danh sách liệt kê sẽ trôi mỗi khi thượng nguồn thêm một giá trị, và cách chữa không nằm trong SQL: hoặc định nghĩa theo phủ định — `status NOT IN ('cancelled', 'test')` — hoặc có một hợp đồng với đội thượng nguồn rằng giá trị mới phải được thông báo.

Quy tắc rút ra: một chỉ số ổn định cần một hợp đồng, không chỉ một truy vấn.

## Góc Khuất & Ngộ Nhận

Về múi giờ: đổi từ UTC sang giờ địa phương làm ranh giới ngày dịch chuyển, và mọi chỉ số theo ngày nhảy một lần rồi ổn định lại. Đây là một trong những dạng trôi khó nhận ra nhất vì mức ảnh hưởng nhỏ và chỉ lộ ra ở các ngày biên.

Về dữ liệu đến muộn: chỉ số tính cho tháng vừa qua thay đổi trong vài ngày sau khi tháng kết thúc, vì giao dịch còn về. Chụp ảnh chỉ số vào ngày 1 và ngày 5 cho hai con số khác nhau — không phải trôi định nghĩa, nhưng gây ra đúng loại tranh cãi ấy, nên đáng ghi rõ thời điểm chốt số.

**Hiểu lầm:** "Có tài liệu mô tả chỉ số là đủ."
**Thực tế:** Tài liệu mô tả ý định, mã tính ra con số, và hai thứ lệch nhau ngay lần sửa đầu tiên không ai cập nhật tài liệu. Chỉ có định nghĩa thực thi được — nơi tài liệu **là** mã — mới không lệch. **Vì sao nghe hợp lý:** viết tài liệu là hành động có thật và tốn công, và công sức bỏ ra tạo cảm giác vấn đề đã được xử lý.

**Hiểu lầm:** "Trôi định nghĩa là vấn đề của tổ chức lớn."
**Thực tế:** Một người viết truy vấn cho chính mình vẫn quên mất đã lọc gì sau ba tháng. Quy mô làm vấn đề tệ hơn, không tạo ra nó. **Vì sao nghe hợp lý:** hậu quả chỉ đủ đau để được kể lại khi nhiều người bị ảnh hưởng, nên các câu chuyện đều đến từ tổ chức lớn.

**Hiểu lầm:** "Bước nhảy trong biểu đồ nghĩa là có gì đó xảy ra trong kinh doanh."
**Thực tế:** Nguyên nhân phổ biến nhất của một bước nhảy sắc nét là thay đổi trong cách đo. Sự kiện kinh doanh thường tạo ra đường cong, còn thay đổi định nghĩa tạo ra bậc thang. **Vì sao nghe hợp lý:** biểu đồ được dựng để kể chuyện kinh doanh, nên người xem đọc mọi thứ trên đó theo ngôn ngữ ấy.

## Nếu Bạn Dạy Lại Điều Này...

Mở đầu bằng biểu đồ có một bậc thang rõ ràng và hỏi chuyện gì đã xảy ra. Để cả lớp đưa giả thuyết kinh doanh vài phút, rồi chiếu lịch sử thay đổi của mã.

Hạt giống bài tập: cho một chỉ số dùng `status IN (...)` với danh sách cứng, và yêu cầu viết lại sao cho một trạng thái mới ở thượng nguồn không âm thầm làm thay đổi con số.

## Tự Kiểm Tra Nhanh

**1. Vì sao định nghĩa dùng danh sách liệt kê nguy hiểm hơn định nghĩa dùng phủ định?**

<details><summary>Đáp án</summary>

Danh sách liệt kê loại bỏ mọi giá trị mới ở thượng nguồn mà không báo gì. Định nghĩa phủ định — loại trừ những trạng thái đã biết là không hợp lệ — thì tự động bao gồm giá trị mới, nên sai lệch nếu có sẽ theo hướng dễ phát hiện hơn.
</details>

**2. Đổi định nghĩa mà không tính lại được lịch sử thì phải làm gì?**

<details><summary>Đáp án</summary>

Đổi tên chỉ số. Giữ nguyên tên là ngầm khẳng định hai đoạn chuỗi so sánh được với nhau, trong khi chúng không. Hai tên khác nhau buộc người đọc phải có chủ đích khi đặt chúng cạnh nhau.
</details>

**3. Thấy một bước nhảy sắc nét trong biểu đồ, câu hỏi đầu tiên là gì?**

<details><summary>Đáp án</summary>

Công thức hoặc dữ liệu thượng nguồn có đổi không. Sự kiện kinh doanh thường tạo đường cong; thay đổi cách đo tạo bậc thang. Kiểm định nghĩa rẻ hơn hẳn việc điều tra một giả thuyết kinh doanh trong vài tuần.
</details>

Ghi chú tiếp theo mở module `reading-the-model`, nơi câu hỏi chuyển từ cách đo sang cách dữ liệu được tổ chức trước khi ai đo nó.
