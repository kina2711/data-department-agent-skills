# Data Agent 0.5.0

Canvas workflow di chuyển và phóng to được, và hai thao tác sửa vốn âm thầm giờ phải hỏi trước.

## Pan và zoom

Cuộn chuột để phóng, kéo nền để di chuyển, hoặc dùng nút `−` `+` `Về gốc` với số phần trăm
bên cạnh.

Cuộn phóng **về phía con trỏ**, không phải về tâm khung. Phóng về tâm là bản dễ viết và sai:
thứ bạn đang xem nằm dưới con trỏ, phóng về tâm đẩy nó ra khỏi màn hình, nên mỗi lần phóng
lại tốn một lần kéo để bù.

Toàn bộ chạy trên `viewBox` của SVG chứ không phải CSS transform — vừa hợp CSP của trang
(cấm inline style), vừa giữ đúng vùng bấm. Transform trên khung bọc sẽ dời hình mà để nguyên
chỗ bấm.

Có chặn biên: kéo bao xa thì đồ thị vẫn còn dính màn hình. Mở workflow khác thì view về gốc,
chứ không mở ra ở góc của một đồ thị không còn tồn tại.

## Sửa workflow có kiểm soát

Hai thao tác trước đây **âm thầm đổi ý nghĩa của thứ khác**:

**Xoá node cắt tiền đề của node khác.** Node biến mất và ba task khác lặng lẽ mất một điều
kiện tiên quyết — đó là thay đổi với những task kia, không phải với task bị xoá. Giờ nút đổi
thành *"Xoá thật? Bấm lại"* và nói rõ task nào sẽ mất tiền đề. Nếu trạng thái đang là
`implemented`, `approved` hay `released`, nó nói thêm rằng đây là xoá một bản ghi đã có bằng
chứng.

**Tick phụ thuộc tạo được vòng lặp.** Vòng lặp thì không có phân tầng — canvas không vẽ nổi,
planner không xếp thứ tự nổi — mà trước đây chỉ lộ lúc validate, tức là sau khi thao tác gây
ra nó đã trôi khỏi tầm mắt. Giờ ô tick bật lại ngay và nói lý do.

Cả hai vẫn **cho phép** thao tác. Khác biệt là bạn được biết trước.

Phép kiểm vòng lặp dùng lại `WfGraph.layer()` — chính hàm mà việc vẽ đã phụ thuộc vào, thay
vì viết một bộ dò vòng lặp thứ hai có thể lệch với bộ thứ nhất.

## Kiểm thử

135/135 test app, gồm 8 test pan/zoom và 4 test cổng chặn khi sửa.
