# Discord Purchase Bot - Hướng dẫn triển khai

## 🚀 Deploy trên Railway (Khuyến nghị)

### Bước 1: Tạo Discord Bot
1. Truy cập [Discord Developer Portal](https://discord.com/developers/applications)
2. Tạo New Application
3. Vào tab "Bot" và tạo bot
4. Copy Bot Token (giữ bí mật!)
5. Bật các Privileged Gateway Intents:
   - Server Members Intent
   - Message Content Intent

### Bước 2: Deploy trên Railway
1. Truy cập [Railway](https://railway.app)
2. Đăng nhập và tạo project mới
3. Chọn "Deploy from GitHub repo"
4. Connect repository này
5. Vào Settings > Environment
6. Thêm environment variable:
   - Key: `DISCORD_BOT_TOKEN`
   - Value: Bot token từ bước 1
7. Railway sẽ tự động deploy

### Bước 3: Mời Bot vào Server
1. Vào tab "OAuth2" > "URL Generator" trong Discord Developer Portal
2. Chọn scopes: `bot` và `applications.commands`
3. Chọn permissions:
   - Send Messages
   - Use Slash Commands
   - Manage Roles
   - Read Message History
4. Copy URL và mời bot vào server

---

## 📱 Deploy trên Replit (Phương án thay thế)

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

### Railway Deploy Issues
- **Bot không khởi động:** Kiểm tra Environment Variables trong Railway Settings
- **Token error:** Đảm bảo `DISCORD_BOT_TOKEN` được set đúng
- **Build failed:** Kiểm tra logs trong Railway Dashboard
- **Memory issues:** Railway free tier có giới hạn RAM

### Discord Issues
- **Lệnh slash không hiện:** Đợi vài phút để Discord sync
- **Bot không gán role:** Kiểm tra bot có quyền Manage Roles và role bot cao hơn role cần gán
- **Permission denied:** Đảm bảo bot có đủ permissions trong server

### Data Persistence
- **Dữ liệu bị mất:** JSON files sẽ reset khi Railway restart
- **Giải pháp:** Cân nhắc upgrade lên Railway Pro hoặc sử dụng database

## 📞 Hỗ trợ
Nếu gặp vấn đề, hãy kiểm tra:
1. **Railway:** Logs trong Dashboard > Deployments
2. **Discord:** Bot permissions và token validity
3. **Environment:** Variables configuration trong Railway Settings

## 🔄 Files được tạo/sửa cho Railway:
- `Procfile` - Định nghĩa cách Railway chạy bot
- `railway.toml` - Cấu hình Railway deployment
- `pyproject.toml` - Loại bỏ dependencies không cần thiết
- `main.py` - Cải thiện error handling và logging