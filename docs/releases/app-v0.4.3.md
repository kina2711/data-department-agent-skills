# Data Agent 0.4.3

Chạy hai skill cùng lúc, mà không đánh mất người chịu trách nhiệm.

## Ghép hai skill

Trong màn hình một skill, chọn **+ Ghép skill thứ hai**. Thanh ghép hiện ra nói rõ cái nào
là **CHÍNH** và cái nào là **PHỤ**.

Đây không phải chuyện thẩm mỹ. Kỷ luật của cả bộ skill là *một deliverable có đúng một người
chịu trách nhiệm*. Nếu prompt chỉ nói "dùng cả hai skill" thì kết quả là hai agent, mỗi bên
đều tưởng bên kia đã lo cái gate. Nên prompt sinh ra nêu thẳng: skill chính giữ deliverable,
gate và approval; skill phụ chỉ đóng góp phần chuyên môn của nó và giao lại có nhãn.

Và một câu nữa, để cái ghép tự tháo khi nó sai: *nếu hóa ra việc này thuộc hẳn về một trong
hai, nói ra và làm theo một skill thay vì chia đôi trách nhiệm.*

## Cảnh báo khi ghép qua ranh giới đã chốt

Bộ skill có 28 cặp "dễ nhầm", mỗi cặp là một ranh giới đã được quyết bằng test: việc thuộc
về skill nào, và không thuộc về skill nào. Ghép đúng một trong 28 cặp đó, thanh ghép chuyển
màu hổ phách và nói rằng ở đây thường chỉ một skill sở hữu việc.

Vẫn ghép được — cảnh báo, không chặn. Nhưng cảnh báo chỉ hiện ở đúng những cặp có ranh giới,
vì cảnh báo mọi lúc thì chẳng ai đọc nữa.

Cặp nào có bàn giao khai báo sẵn giữa hai skill thì được nói ra là hợp lệ.

## Chi tiết

- Skill đang mở luôn là skill chính; không ghép được với chính nó
- Cái ghép **không đi theo** khi bạn mở skill khác
- Ghép chồng lên công việc dựng sẵn chứ không thay thế nó
- Dữ liệu cặp đọc từ `docs/skill-pairs.json` trong suite, sinh cùng lúc với chỉ mục định tuyến

123/123 test app xanh, gồm 9 test mới cho phần ghép.
