# Data Agent 0.4.2

Phiên làm việc sống sót qua việc tắt app hoặc khởi động lại máy, và khung trả lời nói được nó là gì.

## Nối tiếp phiên sau khi tắt app

Mở lại đúng thư mục đó, app hỏi có làm tiếp phiên dở dang không. Bấm đồng ý là Claude
giữ nguyên toàn bộ ngữ cảnh cũ — nó vẫn nhớ đã đọc gì và đã nói gì.

Điều app **không** làm, và nói thẳng ra trên màn hình: khôi phục lại đoạn hội thoại
hiển thị. Cái quay lại là trí nhớ của model, không phải nội dung bạn từng nhìn thấy.
Một khung log trống dưới dòng chữ "đã khôi phục phiên" là lời nói dối mà bạn chỉ phát
hiện khi hỏi một câu nó trả lời bằng ngữ cảnh bạn không thấy.

Phiên được ghi theo cặp thư mục + skill, ghi sau mỗi lượt kết thúc chứ không phải lúc
thoát — vì lần khởi động lại đáng cứu thường là lần không ai chọn.

## Khung trả lời

Trước đây bản ghi hội thoại phần lớn là JSON thô: sự kiện đếm token suy nghĩ rơi xuống
nhánh mặc định và được in nguyên dạng, mỗi nhịp một dòng. Giờ chúng gộp thành một dòng
đếm tự thay thế chính nó.

Khung nhập có tiêu đề, một câu nói rõ phiên vẫn giữ ngữ cảnh, ô nhập ba dòng với ví dụ
cụ thể, và dòng cảnh báo chế độ quyền của lượt kế tiếp.

## Sửa vặt

- Thanh tiêu đề không còn đẩy nút "Chạy trong app" xuống một dòng riêng.
- Khung log không còn để trống 340px dưới một câu trả lời ngắn.
- Nút "Dừng" không còn sáng sau khi nối lại phiên, khi chưa có gì đang chạy.

## Kiểm thử

114/114 test của app xanh, gồm 7 test mới cho phần phiên, mỗi test chạy trên một hồ sơ
dùng một lần nên không đụng tới cấu hình app thật của bạn. Bộ test chạy 137 giây, giảm
từ 599 giây, sau khi sửa một chỗ rò tiến trình trong harness.
