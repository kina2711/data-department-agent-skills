---
id: data-analyst.modelling.dimensional-model
title: Dimensional model
domain: data-analyst
type: pattern
tags: [modelling, reading-the-model, dimensional, model]
status: draft
ai_summary: Facts measured at a grain, described by conformed dimensions, arranged so a business question maps onto a join path instead of a debate.
relationships:
  builds_on: [data-analyst.sql.grain]
  prerequisite_of: [data-analyst.modelling.conformed-dimension]
  commonly_confused_with: [data-analyst.modelling.semantic-layer]
created: 2026-09-01
updated: 2026-09-01
version_sensitive: false
---

# Dimensional model

**Tóm tắt bản chất:** Mô hình chiều gồm các bảng sự kiện đo tại một grain xác định, được mô tả bởi các bảng chiều dùng chung, sắp xếp sao cho một câu hỏi kinh doanh ánh xạ thẳng thành một đường join. Giá trị của nó không nằm ở tốc độ mà ở chỗ nó buộc mọi người đồng ý về grain trước khi ai đó viết truy vấn.

## Nỗi Đau & Động Lực

Trên lược đồ giao dịch chuẩn hóa, câu hỏi "doanh thu theo danh mục sản phẩm và theo tháng" cần bảy phép join. Người viết phải biết bảng nào nối bảng nào, bảng nào có khóa không duy nhất, và bảng nào cần lọc theo trạng thái. Ba người viết ba truy vấn khác nhau và nhận ba con số.

Độ khó không phải vấn đề. Cái khó là **mỗi người tự quyết định một loạt lựa chọn ngầm** — tính đơn đã hủy hay không, lấy giá tại thời điểm đặt hay giá hiện tại, gán đơn vào tháng đặt hay tháng giao — và không lựa chọn nào được ghi ở đâu. Ba con số khác nhau, và cuộc thảo luận về chúng không thể kết thúc vì không ai biết mình đang so sánh cái gì với cái gì.

Cái giá tích lũy. Mỗi báo cáo mới lại tái tạo cùng những lựa chọn ấy, đôi khi khác đi, và sau hai năm tổ chức có bốn mươi định nghĩa doanh thu không tương thích, mỗi cái nằm trong một truy vấn không ai đọc. Bảy phép join ở đầu bài không phải con số tu từ: `orders`, `order_items`, `products`, `categories`, `customers`, `payments`, `refunds`.

## Cơ Chế Tác Động

Hai loại bảng, hai vai trò khác nhau:

**Bảng sự kiện (fact).** Chứa số đo và các khóa ngoại tới chiều. Grain của nó là câu quan trọng nhất trong toàn bộ mô hình, và phải được viết ra: "một dòng của `fct_don_hang` là một dòng hàng trong một đơn đã đặt".

**Bảng chiều (dimension).** Chứa thuộc tính mô tả để cắt lát. `dim_khach_hang`, `dim_san_pham`, `dim_ngay`. Khóa chính duy nhất, ít dòng hơn hẳn bảng sự kiện.

Mọi câu hỏi kinh doanh khi ấy rơi vào một mẫu cố định:

```sql
SELECT d.thang, s.danh_muc, SUM(f.doanh_thu)
FROM fct_don_hang f
JOIN dim_ngay      d ON d.ngay_key = f.ngay_key
JOIN dim_san_pham  s ON s.sp_key   = f.sp_key
GROUP BY 1, 2;
```

Mọi bảng chiều nối với bảng sự kiện bằng đúng một khóa duy nhất, nên **không phép join nào trong mô hình chiều gây fan-out**. Đó là bảo đảm cấu trúc, không phải may mắn, và nó là lý do chính người ta chấp nhận chi phí xây dựng mô hình.

Ba loại số đo, cư xử khác nhau khi cộng:

| Loại | Cộng được theo | Ví dụ |
|---|---|---|
| cộng đầy đủ | mọi chiều | doanh thu, số lượng |
| cộng một phần | vài chiều, trừ thời gian | số dư tài khoản |
| không cộng được | không chiều nào | tỉ lệ, phần trăm, đơn giá |

Dòng cuối bị vi phạm thường xuyên nhất. `AVG(ti_le_chuyen_doi)` trên bảng đã tổng hợp là trung bình của các tỉ lệ, không phải tỉ lệ tổng thể. Bảng sự kiện nên lưu tử số và mẫu số như hai cột riêng, để tầng trên tự chia — và đây là một quy tắc thiết kế chứ không phải mẹo truy vấn.

## Bản Đồ Quyết Định

| Tình huống | Thiết kế | Hậu quả nếu chọn nhầm |
|---|---|---|
| số đo tại grain giao dịch | bảng sự kiện giao dịch | tổng hợp trước làm mất khả năng khoan sâu |
| chỉ cần số tổng theo ngày | bảng sự kiện tổng hợp | giữ grain giao dịch thì tốn kém không cần thiết |
| sự kiện không có số đo | bảng sự kiện không số đo | ép thêm cột `1` làm người đọc tưởng đó là số lượng |
| thuộc tính chiều thay đổi | chiều biến đổi chậm loại 2 | ghi đè làm lịch sử báo cáo tự đổi theo |
| tỉ lệ, phần trăm | lưu tử số và mẫu số riêng | không cộng dồn được ở bất kỳ tầng nào |

Dòng thứ tư là quyết định đắt nhất. Khách hàng chuyển từ phân khúc "cá nhân" sang "doanh nghiệp": ghi đè thuộc tính thì mọi báo cáo lịch sử đột nhiên cho thấy họ luôn là doanh nghiệp, và doanh thu năm ngoái tự dịch chuyển giữa các phân khúc. Chiều loại 2 giữ một dòng cho mỗi giai đoạn hiệu lực, nên báo cáo cũ đứng yên.

Loại 2 có chi phí thật: bảng chiều lớn hơn, mọi truy vấn phải chọn đúng phiên bản, và người viết truy vấn phải hiểu điều đó. Chọn nó cho các thuộc tính mà lịch sử thực sự quan trọng, không phải cho mọi cột.

## Case Study Thực Chiến: ba con số doanh thu và một mô hình

Lược đồ tối thiểu, sau khi mô hình hóa:

```
fct_don_hang (don_hang_key, ngay_key, khach_key, sp_key, so_luong, doanh_thu)
dim_ngay     (ngay_key, ngay, thang, quy, nam)
dim_san_pham (sp_key, sku, danh_muc)
```

Grain của `fct_don_hang` được ghi ngay trong tài liệu bảng: một dòng là một dòng hàng trong một đơn đã đặt, không tính đơn đã hủy, doanh thu là giá tại thời điểm đặt trừ giảm giá dòng.

Một câu như thế dập tắt cả ba tranh cãi ngầm ở phần đầu — trạng thái, thời điểm giá, và grain — trước khi ai viết truy vấn. Ba người bây giờ viết ba truy vấn khác nhau về cú pháp và nhận cùng một con số.

`dim_ngay` tồn tại dù có thể dùng trực tiếp cột ngày. Lý do: quý tài chính, ngày lễ, tuần bắt đầu thứ hai hay chủ nhật — những thứ ấy là dữ liệu, không phải hàm. Nhét chúng vào biểu thức trong từng truy vấn là cách chắc chắn để hai báo cáo bất đồng về việc tuần 1 bắt đầu ngày nào.

**Biến thể khó hơn, nơi cách hiểu trên gây hiểu lầm.** Doanh nghiệp cần theo dõi cả tiền hoàn. Trực giác mách: thêm cột `tien_hoan` vào `fct_don_hang`.

Sai, vì hoàn tiền xảy ra ở grain khác — một đơn có thể hoàn nhiều lần, vào những ngày khác ngày đặt. Nhét vào cùng bảng buộc phải chọn một trong hai điều tệ: hoặc nhân dòng đơn hàng lên theo số lần hoàn, hoặc gộp tiền hoàn về một cột và mất chiều thời gian của nó.

Đúng ra phải tạo bảng sự kiện thứ hai, `fct_hoan_tien`, ở grain riêng, dùng chung `dim_ngay` và `dim_khach_hang`. Hai bảng sự kiện không bao giờ join trực tiếp với nhau — chúng được so sánh qua các chiều dùng chung, mỗi bảng tổng hợp về cùng grain trước.

Quy tắc rút ra: mỗi grain một bảng sự kiện. Ép hai grain vào một bảng luôn tạo ra fan-out hoặc mất thông tin, và cả hai đều không sửa được ở tầng truy vấn.

## Góc Khuất & Ngộ Nhận

Về hiệu năng: lợi ích của mô hình chiều với các động cơ cột hiện đại nhỏ hơn nhiều so với thời kỳ nó ra đời. Lý do giữ nó bây giờ là ngữ nghĩa — grain được tuyên bố, join không nhân, thuật ngữ thống nhất — chứ không phải tốc độ. Biện minh cho nó bằng hiệu năng là biện minh bằng lý do yếu nhất.

Về chiều rác và chiều suy biến: mã đơn hàng không có thuộc tính nào để mô tả, nên nó nằm thẳng trong bảng sự kiện như một chiều suy biến thay vì tạo một bảng chiều chỉ có một cột. Chi tiết nhỏ; người mới vẫn hay tạo bảng chiều cho mọi thứ.

**Hiểu lầm:** "Mô hình chiều là để chạy nhanh."
**Thực tế:** Trên kho cột hiện đại, chuẩn hóa hay không chuẩn hóa thường chênh nhau ít. Giá trị thật là mọi người đồng ý grain và định nghĩa trước khi viết truy vấn. **Vì sao nghe hợp lý:** lý do hiệu năng đúng vào thập niên 1990 và các tài liệu kinh điển nhấn mạnh nó, nên lập luận ấy được truyền lại nguyên vẹn.

**Hiểu lầm:** "Một bảng sự kiện lớn chứa mọi thứ thì tiện hơn."
**Thực tế:** Bảng chứa nhiều grain buộc mọi truy vấn phải lọc đúng loại dòng, và quên một lần là sai số. Mỗi grain một bảng làm cho việc lọc trở thành cấu trúc chứ không phải kỷ luật. **Vì sao nghe hợp lý:** một bảng nghe đơn giản hơn ba bảng, và sự đơn giản ấy có thật — nó chỉ nằm ở chỗ khác với chỗ chi phí xuất hiện.

**Hiểu lầm:** "Chiều loại 2 luôn tốt hơn."
**Thực tế:** Chỉ tốt hơn khi lịch sử của thuộc tính có ý nghĩa cho báo cáo. Với thuộc tính như số điện thoại, giữ lịch sử chỉ làm bảng phình ra và truy vấn phức tạp hơn mà không ai từng hỏi tới. **Vì sao nghe hợp lý:** mất dữ liệu nghe luôn tệ, nên "giữ tất cả" cảm giác là lựa chọn an toàn — trong khi chi phí của nó rơi vào mọi truy vấn về sau.

## Nếu Bạn Dạy Lại Điều Này...

Mở đầu bằng câu hỏi "doanh thu tháng trước là bao nhiêu" trên lược đồ giao dịch, và để ba người viết ba truy vấn độc lập. So ba kết quả trước khi nói bất cứ điều gì về mô hình chiều.

Hạt giống bài tập: cho một yêu cầu thêm tiền hoàn vào mô hình, và chấm cao câu trả lời tạo bảng sự kiện thứ hai thay vì thêm cột.

## Tự Kiểm Tra Nhanh

**1. Vì sao không phép join nào trong mô hình chiều gây fan-out?**

<details><summary>Đáp án</summary>

Vì mọi bảng chiều có khóa chính duy nhất trên cột được join, nên mỗi dòng sự kiện khớp đúng một dòng chiều. Đó là bảo đảm cấu trúc do thiết kế, không phải đặc điểm của dữ liệu, và nó mất đi ngay khi ai đó join hai bảng sự kiện với nhau.
</details>

**2. Vì sao không lưu tỉ lệ chuyển đổi thành một cột trong bảng sự kiện?**

<details><summary>Đáp án</summary>

Vì tỉ lệ không cộng dồn được theo bất kỳ chiều nào. Tổng hợp lên tầng trên sẽ cho trung bình của các tỉ lệ thay vì tỉ lệ tổng thể. Lưu tử số và mẫu số thành hai cột, để tầng trên chia sau khi đã cộng.
</details>

**3. Khi nào cần bảng sự kiện thứ hai thay vì thêm cột?**

<details><summary>Đáp án</summary>

Khi số đo mới nằm ở grain khác. Tiền hoàn xảy ra nhiều lần cho một đơn và vào ngày khác, nên nhét vào bảng đơn hàng sẽ hoặc nhân dòng lên hoặc làm mất chiều thời gian. Mỗi grain một bảng sự kiện, so sánh với nhau qua các chiều dùng chung.
</details>

Ghi chú tiếp theo là [Chiều dùng chung](modelling.conformed-dimension.md), nơi "dùng chung `dim_ngay`" được nói rõ là điều kiện gì.
