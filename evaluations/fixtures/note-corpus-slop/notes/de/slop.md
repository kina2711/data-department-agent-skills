---
id: de.x.slop
ai_summary: "Idempotency cho phép chạy lại pipeline mà không sinh bản ghi trùng."
relationships:
  builds_on: [de.x.other]
version_sensitive: false
---
# Idempotency

**Tóm tắt bản chất:** Trong thế giới dữ liệu ngày nay, idempotency là một khái niệm vô cùng quan trọng, mạnh mẽ và linh hoạt.

## Nỗi Đau & Động Lực
Bài viết này sẽ trình bày về idempotency. Điều quan trọng cần lưu ý là pipeline có thể đôi khi thường bị chạy lại.
Không chỉ gây trùng dữ liệu mà còn làm sai báo cáo — và điều đó — như ta thấy — rất tệ — thật sự tệ.

## Cơ Chế Tác Động
Dùng khoá tự nhiên và MERGE.

## Bản Đồ Quyết Định
| Tình huống | Chọn gì | Vì sao |
|---|---|---|
| Chạy lại toàn phần | MERGE theo khoá | Không sinh bản ghi trùng |

## Case Study Thực Chiến: Retry sau khi job đêm chết giữa chừng
Job nạp đơn hàng chết lúc 2h sáng sau khi ghi được 40% số dòng. Chạy lại từ đầu bằng INSERT sẽ nhân đôi 40% đó.

## Góc Khuất & Ngộ Nhận
- **Hiểu lầm:** MERGE luôn idempotent → **Thực tế:** không, nếu khoá không duy nhất.
- **Hiểu lầm:** Retry là đủ → **Thực tế:** retry không có khoá vẫn nhân bản.

## Tự Kiểm Tra Nhanh
1. Vì sao INSERT không idempotent?
   <details><summary>Đáp án</summary>Vì mỗi lần chạy sinh dòng mới.</details>
2. Khi nào MERGE hỏng?
   <details><summary>Đáp án</summary>Khi khoá không duy nhất.</details>
