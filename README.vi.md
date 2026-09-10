# Thư viện Lark tiếng Việt

Trang mục lục một trang cho tài liệu Lark dành cho partner triển khai và khách hàng tại Việt Nam.
Mỗi thẻ trỏ tới tài liệu gốc trên Lark. Bản thân trang chỉ là mục lục.

Link: https://nixthinh-bit.github.io/lark-vn-library/

English: [README.md](README.md)

## Cập nhật

Nội dung nằm ở `content.json`, không nằm trong HTML. Để thêm hoặc sửa một tài liệu:

1. Sửa `content.json`: mỗi tài liệu có tên, mô tả, đối tượng, mức độ, ngôn ngữ, thời gian đọc
   và cờ `shared`. Có thể thêm tài liệu mới hoặc cả một nhóm mới.
2. Chạy lại build:

   ```
   python3 build.py
   ```

   Lệnh này đọc `content.json` và ghi đè `index.html`. Số liệu ở đầu trang tự tính lại.

Chỉ cần sửa `build.py` khi muốn đổi màu hoặc thêm một layout section mới.

## Các file

| File | Vai trò |
|---|---|
| `index.html` | Trang kết quả. GitHub Pages phục vụ file này. |
| `content.json` | Toàn bộ nội dung: nhóm, tài liệu, metadata. |
| `build.py` | Trình sinh trang. `python3 build.py` dựng lại `index.html`. |

## Layout

Bảy nhóm, mỗi nhóm một layout riêng để trang không đọc thành một lưới lặp lại:
thẻ nổi bật chia đôi, bước đánh số, danh sách dòng, xếp chồng dọc, lưới có tab,
panel hai cột, và một dải hỗ trợ nền tối.

Một file tự chứa. Không CDN, không font ngoài, không gọi mạng, nên hiển thị giống nhau
khi xem trong Lark preview.
