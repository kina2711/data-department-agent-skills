---
id: data-analyst.modelling.semantic-layer
title: Semantic layer
domain: data-analyst
type: pattern
tags: [modelling, reading-the-model, semantic, layer]
status: draft
ai_summary: The single governed definition of a metric, expressed as executable code, so two dashboards asking the same question return the same number.
relationships:
  builds_on: [data-analyst.modelling.conformed-dimension]
  prerequisite_of: []
  commonly_confused_with: [data-analyst.analytics.metric-definition-drift]
created: 2026-09-01
updated: 2026-09-01
version_sensitive: true
---

# Semantic layer

**Tóm tắt bản chất:** Tầng ngữ nghĩa là nơi định nghĩa chỉ số tồn tại **một lần**, dưới dạng mã chạy được, để hai bảng điều khiển hỏi cùng một câu nhận cùng một con số. Không phải tài liệu. Không phải quy ước đặt tên. Không phải một cuộc họp — cả ba đã được thử ở đủ mọi tổ chức, và cả ba đều trôi.

## Nỗi Đau & Động Lực

Bốn bảng điều khiển hiển thị "doanh thu", bốn con số khác nhau. Không cái nào sai theo nghĩa kỹ thuật: một cái loại đơn hủy, một cái loại cả đơn thử nghiệm nội bộ, một cái tính theo ngày giao thay vì ngày đặt, một cái quên loại đơn hoàn tiền toàn phần.

Mỗi lựa chọn ấy đều hợp lý ở thời điểm nó được viết. Vấn đề là chúng được viết bốn lần, bởi bốn người, vào bốn thời điểm, và không có nơi nào để đối chiếu.

Phản xạ thông thường là viết tài liệu định nghĩa chỉ số. Cách ấy không hoạt động, vì một lý do rất cụ thể: tài liệu không chạy. Người thứ năm cần một con số sẽ mở công cụ BI, kéo thả vài trường, và nhận một con số — không ai đi đọc tài liệu trước khi kéo thả, và không có gì ngăn họ lại.

Cái giá dài hạn nghiêm trọng hơn bốn con số: tổ chức mất khả năng dùng số liệu để giải quyết bất đồng. Khi mọi con số đều có thể bị hỏi lại "anh tính thế nào", các cuộc họp quay về dựa vào ý kiến, và toàn bộ khoản đầu tư vào dữ liệu trở thành chi phí chìm.

## Cơ Chế Tác Động

Tầng ngữ nghĩa nằm giữa kho dữ liệu và công cụ hiển thị. Nhận vào một yêu cầu dạng "chỉ số này, cắt theo các chiều này, lọc thế này", nó sinh ra SQL.

Một định nghĩa gồm bốn phần:

```yaml
metric: doanh_thu_thuan
  description: Doanh thu sau khi trừ hoàn tiền, không tính đơn hủy và đơn nội bộ
  source: fct_don_hang
  expression: SUM(doanh_thu - tien_hoan)
  filters:
    - status NOT IN ('cancelled', 'internal_test')
  grain: don_hang
  dimensions: [dim_ngay, dim_khach_hang, dim_san_pham]
  owner: analytics@
```

Mỗi phần trong bốn phần ấy làm một việc riêng. `expression` là công thức. `filters` là những lựa chọn ngầm được viết ra. `grain` cho phép công cụ từ chối các phép tổng hợp không hợp lệ. `dimensions` liệt kê những chiều mà chỉ số này có nghĩa khi cắt theo — và việc liệt kê ấy ngăn người dùng cắt doanh thu theo một chiều không nối được với bảng nguồn.

Cơ chế quan trọng nhất không nằm trong tệp mà nằm ở chỗ **công cụ hiển thị không được phép viết SQL thô**. Nếu người dùng vẫn có đường vòng, tầng ngữ nghĩa trở thành một trong nhiều nguồn thay vì nguồn duy nhất, và nó không giải quyết được gì.

Tệp định nghĩa nằm trong hệ quản lý phiên bản. Mỗi thay đổi là một pull request có người rà soát, và lịch sử thay đổi trả lời được câu hỏi "con số này đổi vì sao" — chính là câu hỏi mà trôi định nghĩa chỉ số khiến không ai trả lời được.

## Bản Đồ Quyết Định

| Tình huống | Việc phải làm | Hậu quả nếu bỏ qua |
|---|---|---|
| chỉ số dùng ở nhiều nơi | định nghĩa trong tầng ngữ nghĩa | mỗi nơi tái tạo một biến thể |
| phân tích một lần, khám phá | SQL thô, không đưa vào tầng | tầng phình ra vì chỉ số dùng một lần |
| hai đội cần hai định nghĩa | hai chỉ số, hai tên | một tên hai nghĩa là tình huống tệ nhất |
| cần đổi định nghĩa | pull request, tính lại lịch sử | xu hướng trở thành hiện vật của thay đổi |
| công cụ BI cho phép SQL thô | đóng đường đó lại | tầng thành một nguồn trong nhiều nguồn |

Dòng thứ ba là chỗ tầng ngữ nghĩa hay bị dùng sai. Khi tài chính và tăng trưởng cần hai cách tính doanh thu khác nhau, cám dỗ là ép một định nghĩa chung để "thống nhất". Kết quả là một định nghĩa không phục vụ ai. Hai chỉ số với hai cái tên rõ ràng — `doanh_thu_ke_toan` và `doanh_thu_ghi_nhan` — trung thực hơn và tránh được cuộc tranh cãi.

Dòng thứ hai đáng nhắc vì hướng ngược lại cũng có hại. Đưa mọi truy vấn vào tầng ngữ nghĩa biến nó thành một lớp quan liêu mà người phân tích phải đi vòng để làm việc, và khi họ đi vòng thì dòng cuối bảng xảy ra.

## Case Study Thực Chiến: bốn con số doanh thu

Lược đồ tối thiểu:

```
fct_don_hang (don_key, ngay_key, khach_key, status, doanh_thu, tien_hoan)
```

Bốn bảng điều khiển, bốn truy vấn, viết rải ra trong mười tám tháng. Cao nhất hơn thấp nhất 11%.

Bước đầu tiên là **không** chọn ngay một định nghĩa đúng. Viết cả bốn ra cạnh nhau, rồi hỏi từng chủ sở hữu bảng điều khiển: anh cần con số nào, cho quyết định nào? Kết quả thường là: hai bảng cần cùng một thứ và khác nhau do sơ suất, một bảng cần thứ khác thật, và một bảng không còn ai dùng.

Sau bước đó mới có hai chỉ số trong tầng ngữ nghĩa thay vì bốn truy vấn, và một bảng điều khiển bị xóa.

**Biến thể khó hơn, nơi cách hiểu trên gây hiểu lầm.** Tầng ngữ nghĩa được triển khai, mọi bảng điều khiển chuyển sang dùng nó, và con số thống nhất. Sáu tháng sau, một người phân tích cần một phép cắt mà tầng không hỗ trợ, nên họ viết SQL thô trong một sổ tay và chia sẻ kết quả trong một cuộc họp.

Con số ấy lệch, vì họ quên bộ lọc `internal_test` — bộ lọc mà tầng ngữ nghĩa vốn áp tự động và vì thế không ai còn nhớ nó tồn tại.

Tập trung hóa có một chi phí ẩn. Nó làm các lựa chọn ngầm trở nên vô hình, chứ không làm chúng biến mất. Ai làm việc ngoài tầng sẽ không biết mình đang bỏ sót gì, và họ càng ít biết khi tầng càng chạy tốt.

Quy tắc rút ra: tầng ngữ nghĩa phải xuất được định nghĩa dưới dạng SQL mà người đọc được. Không phải để người ta sao chép, mà để người buộc phải làm việc bên ngoài nó còn biết mình đang bỏ qua điều gì.

## Góc Khuất & Ngộ Nhận

Về hiệu năng: tầng ngữ nghĩa sinh SQL, và SQL sinh ra thường dài hơn SQL viết tay. Với động cơ cột hiện đại điều đó ít quan trọng, nhưng một định nghĩa liệt kê cả tám chiều khi truy vấn chỉ cần hai vẫn sinh ra sáu phép nối thừa. Đọc SQL sinh ra ít nhất một lần cho mỗi chỉ số quan trọng.

Về chỉ số phái sinh: tỉ lệ và tỉ trọng phải được định nghĩa như phép chia hai chỉ số cơ sở, không phải như một cột. Khai báo nó thành cột kéo bài toán không-cộng-dồn-được quay lại đúng chỗ mà mô hình chiều đã tránh.

**Hiểu lầm:** "Tầng ngữ nghĩa là tài liệu chỉ số."
**Thực tế:** Tài liệu mô tả ý định và trôi khỏi mã ngay lần sửa đầu tiên. Tầng ngữ nghĩa **là** thứ sinh ra con số, nên nó không thể lệch với con số. **Vì sao nghe hợp lý:** cả hai đều là nơi ghi định nghĩa, và điểm khác biệt — thứ nào thực sự chạy — không lộ ra cho tới khi hai bên bắt đầu lệch.

**Hiểu lầm:** "Có tầng ngữ nghĩa thì hết bất đồng về số."
**Thực tế:** Bất đồng chuyển từ chỗ vô hình sang chỗ nhìn thấy được, thế thôi. Hai đội vẫn cần hai định nghĩa; khác biệt là bây giờ họ phải đặt tên cho chúng và tranh luận trong một pull request thay vì trong một cuộc họp về con số. **Vì sao nghe hợp lý:** con số thống nhất là kết quả dễ thấy nhất, nên người ta gán cho công cụ khả năng giải quyết cả bất đồng nằm dưới nó.

**Hiểu lầm:** "Chuyển hết vào tầng ngữ nghĩa là xong."
**Thực tế:** Chừng nào còn đường viết SQL thô, tầng chỉ là một nguồn trong nhiều nguồn. Và đóng đường đó lại quá chặt sẽ đẩy người phân tích ra ngoài hệ thống hoàn toàn. **Vì sao nghe hợp lý:** phần kỹ thuật của việc di chuyển là phần đo đếm được, nên nó trông giống toàn bộ công việc.

## Nếu Bạn Dạy Lại Điều Này...

Mở đầu bằng bốn con số doanh thu từ bốn bảng điều khiển thật và hỏi cái nào đúng. Sau khi lớp tranh luận, hỏi câu thứ hai: mỗi con số phục vụ quyết định nào. Câu thứ hai mới là câu dẫn tới thiết kế.

Hạt giống bài tập: cho một định nghĩa chỉ số trong tầng ngữ nghĩa và yêu cầu viết SQL tương đương bằng tay, rồi so hai kết quả — và giải thích mọi khác biệt.

## Tự Kiểm Tra Nhanh

**1. Vì sao tài liệu định nghĩa chỉ số không thay được tầng ngữ nghĩa?**

<details><summary>Đáp án</summary>

Vì tài liệu không chạy. Con số được sinh ra bởi mã, và mã có thể sửa mà tài liệu không đổi. Tầng ngữ nghĩa là thứ sinh ra con số, nên nó không thể lệch với con số theo cách tài liệu vẫn lệch.
</details>

**2. Hai đội cần hai cách tính doanh thu. Nên làm gì?**

<details><summary>Đáp án</summary>

Định nghĩa hai chỉ số với hai tên rõ ràng. Ép một định nghĩa chung tạo ra con số không phục vụ ai, còn để một tên mang hai nghĩa là tình huống tệ nhất trong ba lựa chọn.
</details>

**3. Chi phí ẩn của việc tập trung hóa định nghĩa là gì?**

<details><summary>Đáp án</summary>

Các lựa chọn ngầm trở nên vô hình thay vì biến mất. Người phải làm việc ngoài tầng sẽ bỏ sót những bộ lọc mà tầng vốn áp tự động, và họ càng dễ bỏ sót khi tầng càng chạy tốt. Vì thế tầng phải xuất được định nghĩa dưới dạng SQL đọc được.
</details>

Ghi chú tiếp theo mở module `stakeholder-work` với [Quyết định của bên liên quan](../stakeholder-work/product.stakeholder-decision.md), nơi câu hỏi không còn là dữ liệu nói gì mà là ai sẽ làm gì khác đi.
