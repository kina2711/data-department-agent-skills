---
id: data-analyst.analytics.retention-curve
title: Retention curve
domain: data-analyst
type: mechanism
tags: [analytics, analysis-method, retention, curve]
status: draft
ai_summary: The share of a cohort still active at each period; whether the curve flattens or decays to zero decides if the product has a viable base.
relationships:
  builds_on: [data-analyst.analytics.cohort]
  prerequisite_of: []
  commonly_confused_with: [data-analyst.analytics.survivorship-bias]
created: 2026-09-01
updated: 2026-09-01
version_sensitive: false
---

# Retention curve

**Tóm tắt bản chất:** Đường giữ chân là tỉ lệ cohort còn hoạt động ở từng kỳ tuổi. Câu hỏi quan trọng nhất về nó không phải nó cao hay thấp, mà là nó **có phẳng ra hay không** — một đường phẳng ở 12% là sản phẩm có nền tảng, một đường mượt mà trôi về 0 thì không.

## Nỗi Đau & Động Lực

Hai sản phẩm cùng giữ được 40% sau tháng đầu. Sản phẩm A tháng thứ sáu còn 22%; sản phẩm B còn 4%. Chỉ số "giữ chân tháng 1" bằng nhau và hai doanh nghiệp hoàn toàn khác nhau.

Đo giữ chân bằng một con số duy nhất là đánh mất đúng thông tin quyết định. Con số đơn lẻ nói được mức, không nói được hình dạng, và hình dạng mới là thứ trả lời câu hỏi liệu tiền bỏ ra thu hút khách có quay lại hay không.

Hệ quả tài chính cụ thể: nếu đường phẳng ở 22%, mỗi khách thu hút được sẽ đóng góp doanh thu vô hạn kỳ về mặt mô hình, và chi phí thu hút có thể hoàn vốn. Nếu đường về 0, mỗi khách có một giá trị hữu hạn và biết trước, và tăng trưởng chỉ tồn tại chừng nào còn tiền đổ vào quảng cáo. Cùng một chỉ số tháng đầu, hai kết luận đối nghịch về việc có nên tiếp tục đầu tư.

## Cơ Chế Tác Động

Đường giữ chân là một hàng của bảng cohort, đọc theo chiều ngang:

```
tuổi:      0     1     2     3     4     5     6
cohort A: 100%  40%   31%   27%   25%   23%   22%
cohort B: 100%  40%   22%   13%    8%    5%    4%
```

Ba phần của đường mang ba ý nghĩa khác nhau:

**Cú rơi đầu tiên (tuổi 0 → 1).** Đây là bài toán kích hoạt: người dùng chưa từng nhận được giá trị của sản phẩm. Đa số đường giữ chân mất nhiều nhất ở đây.

**Đoạn dốc (tuổi 1 → 3).** Người dùng đã thử và đang quyết định. Đây là nơi trải nghiệm sản phẩm có tác động lớn nhất.

**Đuôi (tuổi 4 trở đi).** Chỗ này quyết định. Tiệm cận dương nghĩa là tồn tại một nhóm coi sản phẩm là thói quen. Đường tiếp tục giảm đều nghĩa là không có nhóm ấy.

Phân biệt hai hình dạng cần ít nhất năm tới sáu kỳ. Chỉ ba điểm dữ liệu thì mọi đường giảm đều trông giống nhau, và đây là lý do các báo cáo giữ chân sớm hầu như không kết luận được gì.

Định nghĩa "còn hoạt động" quyết định toàn bộ hình dạng đường:

```sql
-- "hoạt động" = có đơn hàng trong tháng đó
SELECT thang_bat_dau, tuoi_thang,
       COUNT(DISTINCT customer_id) * 1.0 /
       MAX(COUNT(DISTINCT customer_id)) OVER (PARTITION BY thang_bat_dau) AS ti_le
FROM hoat_dong GROUP BY 1, 2;
```

`MAX(...) OVER (PARTITION BY ...)` lấy kích thước cohort ở tuổi 0 làm mẫu số cho mọi tuổi — mẫu số phải cố định, nếu không đường sẽ đo một thứ khác.

## Bản Đồ Quyết Định

Định nghĩa "hoạt động" là quyết định lớn nhất và ít được ghi lại nhất:

| Định nghĩa | Đường sẽ | Phù hợp khi |
|---|---|---|
| có bất kỳ tương tác nào | cao và phẳng sớm | sản phẩm dùng hằng ngày |
| có hành động cốt lõi (đặt đơn) | thấp hơn, thật hơn | thương mại |
| có hành động tạo giá trị lặp lại | thấp nhất, khắt khe nhất | đăng ký định kỳ |
| còn tài khoản chưa hủy | gần như phẳng ở 100% | vô dụng để chẩn đoán |

Dòng cuối tồn tại vì nó phổ biến hơn mức đáng có. "Chưa hủy" không phải giữ chân — nó đo ma sát của quy trình hủy.

| Hình dạng đuôi | Nghĩa | Việc phải làm |
|---|---|---|
| phẳng dương | có nhóm coi đây là thói quen | mở rộng thu hút |
| về 0 chậm | không có nhóm ấy | sửa sản phẩm, đừng tăng chi quảng cáo |
| tăng trở lại | dấu hiệu đo sai, hoặc sản phẩm theo mùa | kiểm định nghĩa trước khi ăn mừng |

Dòng cuối bảng thứ hai là chỗ dễ tự lừa nhất. Đường giữ chân **không** tăng trở lại một cách tự nhiên, vì mẫu số cố định và tử số chỉ có thể đến từ những người từng rời đi rồi quay lại. Thấy nó tăng thì kiểm định nghĩa trước, mừng sau.

## Case Study Thực Chiến: hai sản phẩm cùng chỉ số tháng đầu

Lược đồ tối thiểu:

```
customers (customer_id, signed_up_at)
orders    (order_id, customer_id, ordered_at)
```

Cả hai đội báo cáo "giữ chân tháng 1 là 40%" và xin thêm ngân sách quảng cáo. Vẽ đủ sáu kỳ thì đường của A phẳng ở 22%, đường của B trôi về 4%.

Quyết định khác nhau hoàn toàn. Ở A, mỗi đồng quảng cáo mua về một khách còn ở lại lâu dài, nên tăng chi là hợp lý. Ở B, tăng chi chỉ mua thêm những người sẽ rời đi trong nửa năm — tiền nên đi vào sản phẩm, không vào thu hút.

**Biến thể khó hơn, nơi cách hiểu trên gây hiểu lầm.** Sáu tháng sau, đường của B đã phẳng ở 4% và đội B nói đó là nền tảng của họ.

Xét hình dạng thì đúng: 4% ấy là một nhóm thật, có thói quen thật. Nhưng nền tảng ở 4% và nền tảng ở 22% khác nhau về bậc, không phải về mức độ. Giữ chi phí thu hút cố định, mô hình chỉ hoàn vốn nếu giá trị vòng đời của 4% ấy đủ bù cho 96% còn lại — điều kiện gần như chỉ đúng với sản phẩm giá rất cao.

Hình dạng đường trả lời "có nền tảng hay không". Nó **không** trả lời "nền tảng ấy có đủ lớn để kinh doanh được không", và câu thứ hai cần chi phí thu hút cùng giá trị vòng đời, không nằm trong biểu đồ.

Một bẫy nữa trong cùng biến thể: đường của B phẳng ở 4% có thể là hệ quả của việc 96% kia đã rời đi hết. Cái phẳng ấy không chứng minh sản phẩm đã cải thiện — nó chỉ chứng minh những người dễ rời đã rời xong. Đây chính là chỗ ghi chú về thiên lệch sống sót gặp lại ghi chú này.

## Góc Khuất & Ngộ Nhận

Sản phẩm có tính mùa cho ra đường giữ chân gợn sóng theo chu kỳ 12 tháng, và một cohort bắt đầu vào mùa cao điểm sẽ có đường khác hẳn cohort bắt đầu mùa thấp. So sánh hai cohort cách nhau sáu tháng trong sản phẩm mùa vụ là so sánh hai thứ khác nhau.

Tỉ lệ giữ chân của cohort 40 người nhảy 2,5% mỗi khi một người thay đổi trạng thái. Cohort nhỏ cho đường gợn sóng, và người ta diễn giải các gợn sóng ấy — nên đặt ngưỡng kích thước tối thiểu trước khi vẽ.

**Hiểu lầm:** "Giữ chân cao hơn thì tốt hơn."
**Thực tế:** Chỉ so sánh được trong cùng một loại sản phẩm và cùng một định nghĩa "hoạt động". Sản phẩm dùng hằng ngày và sản phẩm mua theo quý có đường khác nhau về bản chất; so sánh trực tiếp là vô nghĩa. **Vì sao nghe hợp lý:** đó là một con số phần trăm, và số phần trăm mời gọi việc so sánh bất kể chúng đo gì.

**Hiểu lầm:** "Đường phẳng nghĩa là sản phẩm tốt."
**Thực tế:** Nó nghĩa là tồn tại một nhóm coi sản phẩm là thói quen. Nhóm ấy có thể chiếm 2% và mô hình kinh doanh vẫn không chạy được. **Vì sao nghe hợp lý:** hình dạng phẳng thật sự là tín hiệu tốt và nó là tín hiệu khó có được, nên người ta coi nó là điều kiện đủ thay vì điều kiện cần.

**Hiểu lầm:** "Đường giữ chân tăng trở lại là tin vui."
**Thực tế:** Mẫu số đã cố định thì đường chỉ tăng khi người đã rời quay lại — có thật nhưng hiếm. Phổ biến hơn nhiều là mẫu số bị tính lại theo từng kỳ, hoặc định nghĩa "hoạt động" đã đổi giữa chừng. **Vì sao nghe hợp lý:** một đường đi lên trên biểu đồ trông tốt, và ít ai dừng lại hỏi liệu nó có khả thi về mặt toán học hay không.

## Nếu Bạn Dạy Lại Điều Này...

Mở đầu bằng hai đường có cùng điểm tuổi 1 và khác hẳn ở tuổi 6, che phần đuôi lại, và hỏi nên đầu tư vào sản phẩm nào. Sau đó bỏ tấm che.

Hạt giống bài tập: cho một đường giữ chân tăng trở lại ở tuổi 4, và yêu cầu liệt kê ba nguyên nhân kỹ thuật có thể tạo ra nó trước khi chấp nhận nó là thật.

## Tự Kiểm Tra Nhanh

**1. Hai sản phẩm cùng giữ chân 40% ở tháng 1. Cần thêm gì để so sánh?**

<details><summary>Đáp án</summary>

Hình dạng đuôi, tức ít nhất năm tới sáu kỳ. Một con số cho biết mức, không cho biết đường có phẳng ra hay trôi về 0, mà đó mới là điều quyết định chi phí thu hút có hoàn vốn hay không.
</details>

**2. Vì sao mẫu số phải cố định ở kích thước cohort tại tuổi 0?**

<details><summary>Đáp án</summary>

Vì đường đo tỉ lệ của nhóm ban đầu còn hoạt động. Nếu mẫu số tính lại theo từng kỳ, con số trở thành "tỉ lệ của người còn lại vẫn còn lại" — một đại lượng luôn cao và có thể tăng, đo một thứ hoàn toàn khác.
</details>

**3. Đường giữ chân phẳng ở 4% nói lên điều gì?**

<details><summary>Đáp án</summary>

Rằng có một nhóm nhỏ coi sản phẩm là thói quen. Nó không nói nhóm ấy đủ lớn để kinh doanh được — câu đó cần chi phí thu hút và giá trị vòng đời, không có trong biểu đồ. Cái phẳng cũng có thể chỉ là hệ quả của việc những người dễ rời đã rời hết.
</details>

Ghi chú tiếp theo là [Phễu](analytics.funnel.md), nơi thay vì hỏi ai còn ở lại, ta hỏi họ rơi rụng ở bước nào.
