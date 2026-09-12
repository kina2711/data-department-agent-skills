# Sách → note corpus → giáo trình → vault

Một workflow chạy được cho việc lặp lại: có một kệ sách, muốn ra bộ note đầy đủ có hệ
thống cho đúng một đối tượng, rồi đưa vào vault Obsidian.

`workflows/book-to-curriculum-to-vault.workflow.json` — 29 task, 19 đợt, 2 cổng duyệt.

## Vì sao ba skill chứ không một

| Skill | Sở hữu |
|---|---|
| `book-to-knowledge-and-action` | Sách thành tri thức có cấu trúc, và cổng bản quyền |
| `data-academy-and-curriculum` | Roadmap, track, kế hoạch corpus, viết note, giáo trình |
| `personal-second-brain-and-knowledge-os` | Bốn lớp vault, provenance, wikilink |

Ba vai thì đi qua `data-department-orchestrator`. Để một skill ôm cả ba là cách nhanh
nhất để không ai chịu trách nhiệm cho phần mình không rành.

## Bốn giai đoạn

**Giai đoạn 0 — được phép làm gì với sách này.** `book-assess-source-rights` chạy
trước tiên và chốt ngưỡng trích dẫn *trước khi* đọc sâu. Sau đó source manifest với
checksum, rồi `brain-capture-source-material` đưa vào `1_Nguon`.

**Giai đoạn 1 — dạy gì, và làm sao biết là đạt.** Roadmap có dẫn nguồn, track có exit
criterion, rồi `academy-elicit-prior-knowledge` **hỏi người học đã biết gì**, rồi
`core-define-success-contract` chốt tiêu chuẩn nghiệm thu. Kết thúc bằng
`academy-plan-note-corpus`.

Đây là cổng thật sự của cả workflow. Note viết ra khi chưa có ID trong kế hoạch sẽ
mang prerequisite trỏ vào hư không, và đi sâu vài module rồi thì sửa đồ thị rất đắt.

**Giai đoạn 2 — từng module một.** `academy-plan-corpus-milestone` cắt một lát của kế
hoạch, năm task trích xuất chạy song song, `academy-build-note-module` viết, rồi
`core-verify-deliverable` đối chiếu với success contract ở giai đoạn 1. Lặp lại lát này
cho từng module.

**Giai đoạn 3 và 4 — corpus như một tổng thể, rồi xuất bản.** Audit trùng lặp và link
chết, index, wikilink hai chiều, map of content, giáo trình vào `4_Ket-Qua`, và hai
audit R3 chặn trước khi công bố: bản quyền và quyền riêng tư.

## Viết ở project, xuất bản sang vault

Note viết vào `./notes` của project, **không ghi thẳng vào vault**. Ghi thẳng là bỏ qua
cơ chế hai pha của `write_vault_bundle.py` — thứ đảm bảo không có gì đè lên note bạn đã
sửa tay trong Obsidian mà không cho bạn xem trước.

```
project/notes/  →  plan (chỉ đọc, in ra sẽ đổi gì)  →  bạn duyệt  →  --apply --expect
```

Ánh xạ lớp: sách → `1_Nguon`; note corpus → `2_Wiki`; kiến thức sẵn có và quy ước của
bạn → `3_Toi`; giáo trình → `4_Ket-Qua`.

## Chạy thế nào

**Trong app:** tab Workflow → chọn `book-to-curriculum-to-vault` → **Chạy thử khô** để
xem 19 đợt và 2 cổng → gán owner → Validate → chạy.

Hoặc tab Skills → *Book to Knowledge and Action* → công việc **"Sách → note corpus →
giáo trình → vault"** → điền form (thư mục sách, đối tượng, vault, phương ngữ SQL, bạn
đã biết gì) → Chạy trong app.

**Terminal:** mở thư mục project rồi mô tả việc; hoặc gọi thẳng
`/dd-orchestrate` và trỏ vào workflow này.

## Hai chỗ nó sẽ dừng lại hỏi

Đó là thiết kế, không phải agent lười.

Sau `academy-elicit-prior-knowledge` nó hỏi bạn đã biết gì. Corpus sinh ra mà không hỏi
sẽ dạy bạn thứ bạn đã biết, và cái giá rơi vào bạn: đọc những module lẽ ra bỏ qua được,
rồi mất tin vào phần còn lại.

Trước mỗi lần ghi vào vault nó cho bạn xem danh sách tệp sẽ tạo và ghi đè. Note bạn đã
sửa tay thì nó dừng hẳn và hỏi.

## Owner phải điền trước khi chạy

Mọi workflow trong `workflows/` để owner trống, và đó là quy ước có kiểm tra tự động:
một workflow phát hành kèm sẵn tên người sẽ giao việc cho người không có mặt khi người
khác dùng nó.

Nên bước đầu tiên khi mở nó ra là gán owner. Trong app: chọn node, điền ô owner ở
inspector. `validate_workflow.py` sẽ từ chối chạy chừng nào còn task chưa có owner —
đó là cổng, không phải phiền hà: một task không có ai chịu trách nhiệm thì không ai
duyệt được nó.
