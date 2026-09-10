---
name: dd-capture
description: Take one link (or file) and run the whole capture-to-vault chain — capture the source, distil it into a Wiki note with facts, synthesis, inference and uncertainty kept apart, then write it into a local Obsidian vault as a single reversible operation.
argument-hint: "<url hoặc đường dẫn file> [--vault <đường dẫn vault>]"
disable-model-invocation: true
---

Ném một link vào đây và nhận về note đã tổng hợp, nằm sẵn trong vault: $ARGUMENTS

Bộ skill đã có đủ từng bước riêng lẻ cho việc này. Lệnh này chỉ nối chúng lại thành một
đường chạy, và thêm bước cuối cùng vốn còn thiếu: ghi vào vault.

1. Xác định vault. Nếu `--vault` không được truyền, đọc `second-brain-manifest.json` trong
   thư mục làm việc. **Không đoán một đường dẫn vault.** Không có vault thì dừng và hỏi —
   ghi note vào nhầm chỗ là thứ người dùng phải tự đi dọn.
2. `brain-capture-source-material` — lấy nội dung về, sinh stable ID, snapshot, checksum,
   origin và captured-at. Nếu không tải được nội dung, nói rõ là không tải được; đừng tổng
   hợp từ trí nhớ về một URL rồi trình bày như thể đã đọc.
3. `brain-normalize-source-metadata` — title, author, ngày, canonical URL, authority, sensitivity.
4. `brain-distill-source-to-wiki-note` — tách bốn phần: **nguồn nói gì**, **tổng hợp**,
   **suy luận chưa có trong nguồn**, **còn chưa chắc**. Gộp chúng lại là biến một phỏng đoán
   thành một câu trích dẫn.
5. `brain-build-atomic-knowledge-note` cho từng concept đứng riêng được, rồi
   `brain-link-knowledge-graph` để nối `[[wikilink]]` hai chiều.
6. Ghi vào vault bằng hai pha, không bao giờ một pha:

   ```bash
   # pha 1 — chỉ đọc, in ra đúng những file sẽ đổi và hash hiện tại của chúng
   python3 skills/personal-second-brain-and-knowledge-os/scripts/write_vault_bundle.py \
       --vault "$VAULT" --bundle bundle.json

   # pha 2 — ghi, và tự dừng nếu vault đã đổi kể từ pha 1
   python3 skills/personal-second-brain-and-knowledge-os/scripts/write_vault_bundle.py \
       --vault "$VAULT" --bundle bundle.json --apply --expect <expect từ pha 1>
   ```

   Đưa danh sách file sẽ bị ghi đè cho người dùng xem trước khi chạy `--apply`. Ghi đè một
   note họ đã sửa tay là mất công việc của họ, không phải là cập nhật.

Báo cáo: source ID, các note đã tạo, file nào ghi mới và file nào ghi đè, thư mục journal để
hoàn nguyên, và những gì còn chưa chắc trong note. Nếu chỉ chạy pha 1 thì nói thẳng là **chưa
ghi gì cả** — một plan không phải là một lần ghi.
