---
id: data-analyst._schema
title: Lược đồ ví dụ chạy xuyên suốt
domain: data-analyst
type: pattern
tags: [schema, canonical]
status: stable
ai_summary: Canonical schema of the running example used across the data-analyst corpus; five tables of a subscription commerce business with the key cardinalities stated.
relationships:
  builds_on: []
  prerequisite_of: [data-analyst.sql.grain]
  commonly_confused_with: []
created: 2026-09-01
updated: 2026-09-01
version_sensitive: false
---

# Lược đồ ví dụ chạy xuyên suốt

**Tóm tắt bản chất:** Toàn bộ corpus Data Analyst dùng chung một doanh nghiệp giả định — bán hàng có đăng ký định kỳ — với năm bảng cố định. Mọi ghi chú trích lại 3–6 cột nó thực sự dùng, không bảng nào được thêm cột mới.

Lý do có file này: một đoạn ghi chú bị cắt rời khỏi ngữ cảnh vẫn phải đọc hiểu được. Nếu mỗi ghi chú tự bịa một lược đồ riêng, người đọc phải học lại bảng biểu ở từng ghi chú, và hai ghi chú nói về cùng một lỗi sẽ trông như nói về hai hệ thống khác nhau.

## Năm bảng

| Bảng | Khóa chính | Một dòng là gì | Quan hệ |
|---|---|---|---|
| `customers` | `customer_id` | một khách hàng đã đăng ký tài khoản | — |
| `orders` | `order_id` | một đơn hàng đã đặt | `customer_id` → `customers`, N:1 |
| `order_items` | `order_item_id` | một dòng hàng trong đơn | `order_id` → `orders`, N:1 |
| `payments` | `payment_id` | một lần thu tiền cho đơn | `order_id` → `orders`, **N:1** |
| `refunds` | `refund_id` | một lần hoàn tiền cho đơn | `order_id` → `orders`, **N:1** |

Hai quan hệ in đậm là nguồn gốc của phần lớn lỗi trong corpus này. Một đơn hàng có thể được thu tiền nhiều lần — trả góp, thu bổ sung sau khi đổi hàng, thu lại sau khi thẻ bị từ chối — và có thể được hoàn nhiều lần. Cả hai đều không phải quan hệ 1:1, dù trực giác kinh doanh hay mặc định là vậy.

## Cột của từng bảng

```sql
customers   (customer_id, signed_up_at, country, segment)
orders      (order_id, customer_id, ordered_at, status, gross_amount)
order_items (order_item_id, order_id, sku, quantity, unit_price, discount_amount)
payments    (payment_id, order_id, paid_at, amount, method)
refunds     (refund_id, order_id, refunded_at, amount, reason)
```

Ba cột cho phép `NULL` và được dùng làm ví dụ trong ghi chú về null: `discount_amount` khi dòng hàng không giảm giá, `refunded_at` khi bản ghi hoàn tiền đã tạo nhưng chưa xử lý xong, và `segment` khi khách hàng chưa được phân nhóm.

`orders.gross_amount` là tổng tiền hàng do hệ thống đặt hàng ghi lại tại thời điểm đặt. Nó **không** bắt buộc bằng tổng `order_items`, và chênh lệch giữa hai con số là một tình huống có thật chứ không phải lỗi dữ liệu — phí vận chuyển và làm tròn thuế nằm ở đơn, không nằm ở dòng hàng.

Ghi chú tiếp theo trong lộ trình là [Grain](sql-foundation/sql.grain.md): trước khi tính bất cứ thứ gì trên lược đồ này, phải nói được một dòng của bảng đang tính là gì.
