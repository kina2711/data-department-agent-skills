# Phát hành

Ghi chú phát hành nằm trong thư mục này. Tag đã có trên `origin`; phần còn thiếu là bản
Release trên GitHub, và nó cần tài khoản của bạn.

## Vì sao chưa tạo sẵn được

Máy này không có `GITHUB_TOKEN`, không có credential helper, không có `~/.netrc`, và
`gh` chưa đăng nhập. `git push` chạy được vì dùng khóa SSH, nhưng tạo Release thì đi qua
GitHub API và cần token. Không có đường vòng nào hợp lệ ở đây, và cũng không nên có.

## Cần quyết trước khi phát hành

Kho này đang **public**, và ba nơi khai ba giấy phép khác nhau:

| Tệp | Đang ghi |
|---|---|
| `LICENSE` | "All rights reserved" |
| `.claude-plugin/plugin.json` | `"Proprietary"` |
| `.claude-plugin/marketplace.json` | `"Proprietary"` |
| `app/package.json` | `"MIT"` |

Gắn tệp cài đặt vào một bản Release công khai làm mâu thuẫn này thành chuyện thật, chứ
không còn là chi tiết nội bộ. Chọn một giấy phép và cho cả bốn nơi nói giống nhau trước
đã. Đây là quyết định của bạn, không phải của tôi.

## Các lệnh

```bash
gh auth login                      # một lần, chọn GitHub.com → SSH → trình duyệt

cd /home/kina2711/PROJECT/data-department-agent-skills

# Release cho hai tag đã đẩy từ trước
gh release create app-v0.4.0 --title "Data Agent 0.4.0" \
  --notes "Bản desktop đầu tiên: chọn skill, canvas workflow, chạy trong app."
gh release create app-v0.4.1 --title "Data Agent 0.4.1" \
  --notes "Nối tiếp hội thoại sau câu trả lời đầu tiên, và nói rõ lượt tới chạy ở chế độ quyền nào."

# Bản mới
git tag -a app-v0.4.2 -m "Data Agent 0.4.2"
git push origin app-v0.4.2
gh release create app-v0.4.2 --title "Data Agent 0.4.2" \
  --notes-file docs/releases/app-v0.4.2.md
```

## Kèm tệp cài đặt (tùy chọn, làm sau khi đã chốt giấy phép)

```bash
cd app && npm run dist            # sinh AppImage và .deb trong app/dist/
cd .. && gh release upload app-v0.4.2 app/dist/*.AppImage app/dist/*.deb
```

`npm run dist` chạy `electron-builder --linux AppImage deb`, nên nó chỉ sinh bản Linux.
Bản Windows và macOS cần chạy trên chính hệ đó hoặc qua CI.

## Cập nhật bản trên dock

Dock chạy `~/.local/opt/app-data-agent/app-data-agent`, không chạy AppImage. Thay bản
mới bằng cách chép đè thư mục đó; tệp `.desktop` và biểu tượng giữ nguyên nên ghim trên
dock không mất:

```bash
mv ~/.local/opt/app-data-agent ~/.local/opt/app-data-agent.bak-$(date +%F-%H%M%S)
cp -r app/dist/linux-unpacked ~/.local/opt/app-data-agent
```

> **Đừng chạy `npx asar extract-file` bên trong `app/`.** Nó ghi tệp giải nén ra thư mục
> hiện tại theo đúng tên trong archive, không ra stdout dù bạn truyền `/dev/stdout`. Chạy
> trong `app/` là nó đè `app/package.json` bằng bản rút gọn nằm trong asar — mất toàn bộ
> `scripts` và `build`, và triệu chứng đầu tiên là `npm test` báo *Missing script: "test"*.
> Muốn xem thì `cd` sang thư mục tạm trước.
