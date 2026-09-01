---
id: data-analyst.modelling.conformed-dimension
title: Conformed dimension
domain: data-analyst
type: pattern
tags: [modelling, reading-the-model, conformed, dimension]
status: draft
ai_summary: One dimension shared by several facts with identical keys and meaning, which is the condition that makes two facts comparable at all.
relationships:
  builds_on: [data-analyst.modelling.dimensional-model]
  prerequisite_of: [data-analyst.modelling.semantic-layer]
  commonly_confused_with: [data-analyst.modelling.dimensional-model]
created: 2026-09-01
updated: 2026-09-01
version_sensitive: false
---

# Conformed dimension

**Tóm tắt bản chất:** Chiều dùng chung là một bảng chiều được nhiều bảng sự kiện tham chiếu với **cùng khóa và cùng ý nghĩa**. Điều kiện ấy là thứ khiến hai bảng sự kiện so sánh được với nhau; thiếu nó, hai con số đặt cạnh nhau trên một biểu đồ chỉ trông như có liên quan.

## Nỗi Đau & Động Lực

Đội marketing có `fct_chi_quang_cao` với chiều `dim_kenh`. Đội bán hàng có `fct_don_hang` với chiều `dim_nguon`. Cả hai đều liệt kê "Facebook", "Google", "Email".

Đặt hai con số cạnh nhau để tính chi phí trên mỗi đơn theo kênh, và kết quả sai — không nhiều, chỉ đủ để không ai nghi ngờ. Nguyên nhân: `dim_kenh` gọi Instagram là một kênh riêng, còn `dim_nguon` gộp nó vào "Facebook". Chi phí Instagram nằm ở dòng riêng còn doanh thu Instagram nằm trong dòng Facebook.

Cái giá không phải một phép chia sai. Nó là việc **không ai biết hai bảng ấy không so được**, vì cả hai đều có một cột tên "kênh" chứa những chuỗi trông giống nhau. Mô hình chiều đã được xây đúng ở cả hai phía, và nó vẫn không giúp gì cho câu hỏi bắc cầu giữa hai phía.

Đây là lý do "chiều dùng chung" là một điều kiện chứ không phải một loại bảng. Hai bảng cùng tên, cùng nội dung gần đúng, mà khác nhau ở một quy tắc gộp nhóm thì không phải chiều dùng chung.

## Cơ Chế Tác Động

Ba điều kiện, và phải đủ cả ba:

**Một — cùng khóa.** Cả hai bảng sự kiện tham chiếu cùng tập giá trị khóa. Không phải "khóa có thể ánh xạ được", mà là cùng khóa.

**Hai — cùng ý nghĩa.** Một giá trị khóa chỉ đúng một thực thể ở cả hai phía. "Facebook" phải bao gồm hay loại trừ Instagram một cách nhất quán.

**Ba — cùng độ mịn.** Nếu một bên có kênh chi tiết tới chiến dịch còn bên kia chỉ tới nền tảng, chúng chỉ so được ở mức nền tảng, và mức ấy phải được nói ra.

Kiểm bằng một truy vấn, chạy trước khi tin bất kỳ so sánh nào:

```sql
SELECT COALESCE(a.kenh_key, b.kenh_key) AS kenh,
       a.kenh_key IS NOT NULL AS co_trong_chi_phi,
       b.kenh_key IS NOT NULL AS co_trong_doanh_thu
FROM (SELECT DISTINCT kenh_key FROM fct_chi_quang_cao) a
FULL OUTER JOIN (SELECT DISTINCT kenh_key FROM fct_don_hang) b
  ON a.kenh_key = b.kenh_key
WHERE a.kenh_key IS NULL OR b.kenh_key IS NULL;
```

`FULL OUTER JOIN` ở đây có mục đích cụ thể: nó cho thấy giá trị nào chỉ tồn tại ở một phía. Kết quả rỗng là điều kiện một đã thỏa. Điều kiện hai và ba thì không có truy vấn nào kiểm được — chúng cần đọc định nghĩa và hỏi người sở hữu dữ liệu.

Cách so hai bảng sự kiện qua chiều dùng chung, gọi là drill-across: tổng hợp **từng bảng riêng** về cùng grain, rồi mới ghép:

```sql
WITH chi AS (
  SELECT kenh_key, thang_key, SUM(chi_phi) AS chi_phi
  FROM fct_chi_quang_cao GROUP BY 1, 2
), doanh_thu AS (
  SELECT kenh_key, thang_key, SUM(doanh_thu) AS doanh_thu
  FROM fct_don_hang GROUP BY 1, 2
)
SELECT k.ten_kenh, t.thang,
       chi.chi_phi, doanh_thu.doanh_thu
FROM chi FULL OUTER JOIN doanh_thu USING (kenh_key, thang_key)
JOIN dim_kenh k USING (kenh_key)
JOIN dim_thoi_gian t USING (thang_key);
```

Không bao giờ join hai bảng sự kiện trực tiếp. Làm vậy nhân dòng theo tích của hai bên — một kênh có 30 dòng chi phí và 4.000 dòng đơn hàng cho ra 120.000 dòng, và mọi tổng đều hỏng.

## Bản Đồ Quyết Định

| Tình huống | Việc phải làm | Hậu quả nếu bỏ qua |
|---|---|---|
| hai bảng sự kiện, chiều trùng tên | kiểm ba điều kiện trước | so sánh sai mà trông hợp lý |
| độ mịn khác nhau | gộp về mức chung, ghi rõ mức đó | so sánh ngầm ở mức không tồn tại |
| một phía thiếu giá trị | quyết định coi là 0 hay là thiếu | `COALESCE` bừa biến thiếu dữ liệu thành số 0 |
| không thể làm chung chiều | ánh xạ tường minh trong một bảng cầu | ánh xạ ngầm nằm rải trong từng truy vấn |
| hai đội sở hữu hai chiều | một chủ sở hữu duy nhất cho chiều dùng chung | hai bên sửa độc lập và lệch lại sau vài tháng |

Dòng cuối là vấn đề tổ chức chứ không phải kỹ thuật, và nó là vấn đề khó hơn. Chiều dùng chung đòi hai đội từ bỏ quyền tự quyết định danh mục của mình. Không có thiết kế nào thay thế được thỏa thuận ấy, và mọi giải pháp kỹ thuật cho vấn đề này đều là bảng ánh xạ — tức là chấp nhận rằng thỏa thuận đã thất bại.

Dòng thứ ba đáng chú ý riêng. Một kênh có chi phí mà không có đơn hàng nào là thông tin quan trọng — nó nghĩa là kênh ấy chưa từng chuyển đổi. Biến `NULL` thành `0` giữ nguyên con số nhưng xóa mất sự phân biệt giữa "chi tiền mà không thu được gì" và "chưa chạy kênh này".

## Case Study Thực Chiến: chi phí trên mỗi đơn sai 15% ở một kênh

Lược đồ tối thiểu:

```
fct_chi_quang_cao (chi_key, kenh_key, thang_key, chi_phi)
fct_don_hang      (don_key, kenh_key, thang_key, doanh_thu)
dim_kenh          (kenh_key, ten_kenh)
```

Chạy phép kiểm `FULL OUTER JOIN` ở trên và nhận ba dòng: `instagram` chỉ có ở phía chi phí; `email_promo` và `email_trans` chỉ có ở phía đơn hàng, trong khi phía chi phí chỉ có `email`.

Hai vấn đề khác nhau lộ ra cùng lúc. Instagram vi phạm điều kiện hai — cùng một thực tại được phân loại khác nhau. Email vi phạm điều kiện ba — một bên mịn hơn bên kia.

Cách xử lý cũng khác nhau. Với Instagram, phải sửa nguồn: một bên đang sai và cần thống nhất. Với email, cả hai bên đều đúng ở mức của mình, nên gộp về mức nền tảng và **ghi rõ trong tiêu đề báo cáo** rằng email được so ở mức gộp.

**Biến thể khó hơn, nơi cách hiểu trên gây hiểu lầm.** Đội xây một bảng cầu ánh xạ `instagram` sang `facebook` và coi vấn đề đã giải quyết.

Bảng cầu làm con số khớp lại, và nó **che mất** việc hai hệ thống vẫn đang bất đồng. Sáu tháng sau, đội marketing tách thêm "Facebook Reels" thành kênh riêng. Bảng cầu không biết, nên giá trị mới rơi ra ngoài mọi ánh xạ và biến mất khỏi báo cáo — lặng lẽ, vì `FULL OUTER JOIN` đã bị thay bằng `JOIN` khi người ta tin rằng ánh xạ là đầy đủ.

Quy tắc rút ra: bảng ánh xạ là nợ kỹ thuật có kỳ hạn, không phải giải pháp. Nó phải đi kèm một phép kiểm chạy định kỳ để phát hiện giá trị chưa được ánh xạ, nếu không nó sẽ hỏng đúng vào lúc không ai nhìn.

## Góc Khuất & Ngộ Nhận

Về chiều thời gian: `dim_ngay` là chiều dùng chung dễ nhất và cũng hay bị bỏ qua nhất. Hai bảng sự kiện dùng hai định nghĩa "tuần" khác nhau — một bên bắt đầu thứ hai, một bên chủ nhật — cho hai đường xu hướng lệch pha một ngày, đủ để tạo ra tranh cãi về việc chiến dịch bắt đầu tác động khi nào.

Về chiều loại 2 dùng chung: nếu một chiều giữ lịch sử và các bảng sự kiện tham chiếu tới khóa thay thế, hai bảng phải chọn cùng một phiên bản của cùng một thực thể. Sai lệch ở đây rất khó thấy vì mọi khóa đều hợp lệ.

**Hiểu lầm:** "Hai bảng có cột cùng tên là chiều dùng chung."
**Thực tế:** Tên cột không mang ý nghĩa. Chiều dùng chung đòi cùng khóa, cùng ý nghĩa và cùng độ mịn, và hai trong ba điều kiện ấy không kiểm được bằng truy vấn. **Vì sao nghe hợp lý:** trong một mô hình do một người xây thì tên trùng thường kéo theo nghĩa trùng, và quy tắc rút ra từ đó không sống sót khi có đội thứ hai.

**Hiểu lầm:** "Join hai bảng sự kiện là cách so sánh chúng."
**Thực tế:** Nó nhân dòng theo tích của hai phía và làm hỏng mọi tổng. Cách đúng là drill-across: tổng hợp riêng từng bảng về cùng grain rồi mới ghép. **Vì sao nghe hợp lý:** join là công cụ mặc định để kết hợp hai bảng, và bảng sự kiện trông giống mọi bảng khác.

**Hiểu lầm:** "Bảng ánh xạ giải quyết được vấn đề chiều không đồng nhất."
**Thực tế:** Nó làm con số khớp và giữ nguyên nguyên nhân. Mỗi giá trị mới ở thượng nguồn lại rơi ra ngoài ánh xạ, và nếu không có phép kiểm định kỳ thì nó biến mất không dấu vết. **Vì sao nghe hợp lý:** bảng ánh xạ thực sự sửa được triệu chứng ngay lập tức, và triệu chứng biến mất là tín hiệu rất thuyết phục.

## Nếu Bạn Dạy Lại Điều Này...

Mở đầu bằng hai bảng chiều thật, cùng tên cột, khác nhau ở đúng một quy tắc gộp nhóm, và yêu cầu tính chi phí trên mỗi đơn. Sau khi có kết quả, chiếu phép kiểm `FULL OUTER JOIN`.

Hạt giống bài tập: cho một bảng ánh xạ đã dùng sáu tháng và một danh sách giá trị kênh hiện tại, yêu cầu tìm giá trị nào đang rơi ra ngoài.

## Tự Kiểm Tra Nhanh

**1. Ba điều kiện của một chiều dùng chung là gì, và cái nào kiểm được bằng truy vấn?**

<details><summary>Đáp án</summary>

Cùng khóa, cùng ý nghĩa, cùng độ mịn. Chỉ điều kiện đầu kiểm được bằng truy vấn, bằng một `FULL OUTER JOIN` giữa hai tập khóa phân biệt. Hai điều kiện còn lại cần đọc định nghĩa và hỏi người sở hữu dữ liệu.
</details>

**2. Vì sao không join trực tiếp hai bảng sự kiện?**

<details><summary>Đáp án</summary>

Vì cả hai đều có nhiều dòng cho mỗi tổ hợp khóa chiều, nên phép join tạo ra tích của hai bên. Một kênh với 30 dòng chi phí và 4.000 dòng đơn hàng cho 120.000 dòng. Tổng hợp từng bảng về cùng grain trước, rồi mới ghép.
</details>

**3. Một kênh có chi phí nhưng không có đơn hàng. Vì sao không nên `COALESCE` về 0?**

<details><summary>Đáp án</summary>

Vì `0` và "không có dữ liệu" là hai tình huống khác nhau: kênh chi tiền mà không chuyển đổi, so với kênh chưa từng được ghi nhận ở phía đơn hàng. Con số tổng giống nhau, nhưng hành động cần làm thì ngược nhau.
</details>

Ghi chú tiếp theo là [Tầng ngữ nghĩa](modelling.semantic-layer.md), nơi thỏa thuận về định nghĩa được đặt vào một chỗ thay vì trông chờ vào kỷ luật.
