# Discord Purchase Bot - Hướng dẫn triển khai trên Replit

## 📋 Mô tả
Bot Discord quản lý thông tin mua hàng và phân quyền role tự động dựa trên tổng số tiền đã chi tiêu.

## 🚀 Cách triển khai trên Replit

### Bước 1: Tạo Discord Bot
1. Truy cập [Discord Developer Portal](https://discord.com/developers/applications)
2. Tạo New Application
3. Vào tab "Bot" và tạo bot
4. Copy Bot Token (giữ bí mật!)
5. Bật các Privileged Gateway Intents:
   - Server Members Intent
   - Message Content Intent

### Bước 2: Mời Bot vào Server
1. Vào tab "OAuth2" > "URL Generator"
2. Chọn scopes: `bot` và `applications.commands`
3. Chọn permissions:
   - Send Messages
   - Use Slash Commands
   - Manage Roles
   - Read Message History
4. Copy URL và mời bot vào server

### Bước 3: Triển khai trên Replit
1. Tạo Repl mới trên [Replit](https://replit.com)
2. Chọn "Import from GitHub" hoặc upload các file:
   - `main.py`
   - `requirements.txt`
   - `.replit`
   - `purchases.json`
   - `roles.json`

3. **Cấu hình Environment Variables:**
   - Vào tab "Secrets" (🔒)
   - Thêm secret mới:
     - Key: `DISCORD_BOT_TOKEN`
     - Value: Bot token từ bước 1

4. Nhấn "Run" để khởi động bot

### Bước 4: Kiểm tra Bot hoạt động
- Bot sẽ hiển thị "🤖 Bot [tên bot] đã sẵn sàng!" khi khởi động thành công
- Thử lệnh `/list` trong Discord để kiểm tra

## 📝 Các lệnh có sẵn

### Lệnh Admin (cần quyền Administrator)
- `/luu` - Lưu thông tin mua hàng
- `/setup_role` - Thiết lập role theo ngưỡng tiền

### Lệnh User
- `/list` - Xem thông tin mua hàng cá nhân
- `/rank` - Xem top 20 khách hàng

## 🔧 Cấu trúc File

- `main.py` - File chính chạy bot
- `requirements.txt` - Dependencies
- `.replit` - Cấu hình Replit
- `purchases.json` - Dữ liệu mua hàng
- `roles.json` - Cấu hình role và ngưỡng

## ⚠️ Lưu ý quan trọng

1. **Bảo mật Token:** Không bao giờ chia sẻ bot token
2. **Backup dữ liệu:** Định kỳ backup file JSON
3. **Quyền Bot:** Đảm bảo bot có quyền manage roles
4. **Replit Always On:** Cân nhắc upgrade để bot chạy 24/7

## 🐛 Troubleshooting

### Bot không khởi động
- Kiểm tra token trong Secrets
- Xem console log để biết lỗi cụ thể

### Lệnh slash không hiện
- Đợi vài phút để Discord sync
- Kick và invite lại bot

### Bot không gán role
- Kiểm tra bot có quyền Manage Roles
- Đảm bảo role bot cao hơn role cần gán

## 📞 Hỗ trợ
Nếu gặp vấn đề, hãy kiểm tra:
1. Console log trong Replit
2. Bot permissions trong Discord
3. Token configuration trong Secrets