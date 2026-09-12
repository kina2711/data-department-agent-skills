---
name: dd-pipeline
description: Run the whole chain from a folder of source material to a published content series — books, slides and lecture video become a systematic note corpus and a curriculum, land in an Obsidian vault, and come back out as posts for Facebook, LinkedIn and Threads. Use when the request spans learning material and publishing rather than one of them.
argument-hint: "<chủ đề> [--ref <thư mục>] [--vault <đường dẫn>] [--dung-o <mốc>]"
disable-model-invocation: true
---

Chạy cả dây chuyền cho: $ARGUMENTS

Workflow `workflows/data-trainer.workflow.json` — 50 task, 31 đợt, 3 cổng duyệt.
Nó chạm bốn skill, nên **điều phối qua `data-department-orchestrator`**; đừng để một skill ôm
phần nó không rành.

| Skill | Sở hữu |
|---|---|
| `book-to-knowledge-and-action` | Trích xuất từ nguồn, và cổng bản quyền |
| `data-academy-and-curriculum` | Roadmap, track, kế hoạch corpus, note, giáo trình |
| `personal-second-brain-and-knowledge-os` | Bốn lớp vault, provenance, wikilink |
| `data-technical-content-and-social` | Canonical article và ba biến thể kênh |

## Trước khi chạy

1. Xác định thư mục nguồn (`--ref`, mặc định `./ref`) và **vault** (`--vault`, hoặc đọc
   `second-brain-manifest.json`). Không đoán đường dẫn vault.
2. Gán owner cho các task trong workflow. Validator từ chối chạy khi còn task chưa có owner —
   một task không ai chịu trách nhiệm thì không ai duyệt được nó.
3. Hỏi người dùng dừng ở mốc nào: sau kế hoạch corpus, sau khi vào vault, sau khi soạn xong
   content, hay chạy hết qua từng cổng.

## Bốn chặng

**Nguồn.** `book-assess-source-rights` chạy trước tiên và chốt ngưỡng trích dẫn *trước khi* đọc
sâu. Sau đó theo loại nguồn: PDF và sách qua `book-extract-source-text`; video bài giảng qua
`brain-transcribe-audio-video-source` có timestamp và ghi rõ chỗ nghe không rõ; slide và ảnh qua
`brain-process-image-and-diagram-source`. Nội dung không đọc được thì **nói là không đọc được**,
đừng suy từ tên tệp.

**Corpus.** Roadmap có dẫn nguồn, track có exit criterion, rồi `academy-elicit-prior-knowledge`
**hỏi người học đã biết gì**, rồi `core-define-success-contract` biến câu trả lời thành tiêu chuẩn
nghiệm thu. `academy-plan-note-corpus` là cổng: mọi note có ID, module và prerequisite trước khi
viết note đầu tiên.

**Vault.** Note viết vào `./notes` của project, **không ghi thẳng vào vault**. Xuất bản bằng hai
pha của `write_vault_bundle.py`: pha plan cho người dùng xem sẽ tạo và ghi đè tệp nào, họ duyệt
rồi mới `--apply --expect`. Ánh xạ lớp: nguồn → `1_Nguon`; note → `2_Wiki`; kiến thức sẵn có và
quy ước cá nhân → `3_Toi`; giáo trình và bài đăng → `4_Ket-Qua`.

**Content.** Một canonical article rồi mới ra ba biến thể — Facebook tiếng Việt, LinkedIn tiếng
Anh, Threads tiếng Việt. Giới hạn ký tự là ràng buộc câu chữ, **không phải cớ để bỏ mệnh đề làm
cho claim đúng**.

Ảnh là ảnh thật, không phải bản mô tả ảnh. `content-render-post-images` chạy
`scripts/render_content_images.js` dưới Electron của app và xuất PNG cho ba loại: code có tô màu
cú pháp, cheatsheet dạng bảng, và diagram từ SVG. **Ảnh màn hình thật thì script không dựng** —
một ảnh màn hình là bằng chứng có thứ gì đó đã chạy, và dựng ra nó là chế tạo bằng chứng đó.
Người dùng tự chụp và đưa vào thư mục ảnh.

## Dây chuyền dừng ở gói bàn giao, không đăng

`content-package-technical-series-repository` là bước cuối trước handoff: bài đã soạn, ảnh đã
dựng, mọi audit đã qua, đóng thành một gói để **người dùng tự đăng**.

Đăng không nằm trong workflow này. Tài khoản là của họ, và một workflow liệt kê việc đăng sẽ mời
gọi một tuyên bố mà không ai có bằng chứng. Không bao giờ nói đã đăng.

Hai cổng còn lại: bản quyền, và quyền riêng tư của vault.

Báo cáo: nguồn nào đọc được và nguồn nào không, số note viết ra, tệp nào vào vault, bài nào soạn
xong ở kênh nào, ảnh nào đã dựng, cổng nào đã qua và cổng nào đang chờ người duyệt.
