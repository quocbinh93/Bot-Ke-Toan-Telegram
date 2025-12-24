# 🌐 Web Admin Panel - Hướng Dẫn Sử Dụng

## 📖 Giới Thiệu

Web Admin Panel là giao diện web quản lý Telegram Accounting Bot, giúp admin dễ dàng:
- ✅ Quản lý users và phân quyền (set role)
- ✅ Duyệt/Từ chối hóa đơn
- ✅ Xem thống kê tổng quan
- ✅ Quản lý tất cả invoices

## 🚀 Cài Đặt

### 1. Cài đặt dependencies
```bash
pip install -r requirements-web.txt
```

Hoặc cài thủ công:
```bash
pip install Flask Flask-Session
```

### 2. Chạy web server

**Windows:**
```bash
run_web.bat
```

**Linux/Mac:**
```bash
python webapp/app.py
```

### 3. Truy cập

Mở trình duyệt và vào:
```
http://localhost:5000
```

**Mật khẩu mặc định:** `admin123`

⚠️ **QUAN TRỌNG:** Đổi mật khẩu trong file `webapp/app.py` (dòng 21):
```python
ADMIN_PASSWORD = "your-strong-password-here"
```

## 📊 Tính Năng

### 1. Dashboard
- 📈 Thống kê tổng quan:
  - Tổng số users (phân chia theo role)
  - Tổng số invoices và tổng tiền
  - Số lượng pending/approved/rejected
- 📋 10 invoices mới nhất

### 2. User Management (`/users`)

**Chức năng:**
- Xem danh sách tất cả users
- Thông tin: Telegram ID, Username, Full Name, Role, Department
- Thống kê: Số invoices submitted/approved
- **Set Role:** Thay đổi role của user (User/Accountant/Admin)

**Cách set role:**
1. Click nút "Set Role" bên cạnh user
2. Chọn role mới từ dropdown menu
3. Confirm thay đổi
4. Badge role tự động cập nhật

**Role Colors:**
- 🔴 Admin - Red badge
- 🟡 Accountant - Yellow badge  
- 🔵 User - Blue badge

### 3. Invoice Management (`/invoices`)

**Filter invoices:**
- All - Tất cả hóa đơn
- Pending - Chờ duyệt
- Approved - Đã duyệt
- Rejected - Đã từ chối

**Actions cho Pending invoices:**
- ✅ **Approve:** Click nút xanh để duyệt
- ❌ **Reject:** Click nút đỏ để từ chối (nhập lý do)

**Thông tin hiển thị:**
- Invoice Number, Date, Supplier
- Tax Code, Category
- Total Amount
- Status, User submitted

## 🎨 Giao Diện

### Navigation Bar
```
Admin Panel | Dashboard | Users | Invoices ▼ | Logout
```

### Statistics Cards
```
┌─────────────┬─────────────┬──────────┬──────────┬──────────┐
│ Total Users │Total Invoice│ Pending  │ Approved │ Rejected │
│     15      │     248     │    12    │   230    │    6     │
└─────────────┴─────────────┴──────────┴──────────┴──────────┘
```

### User Table
```
Telegram ID | Username  | Name | Role       | Actions
───────────────────────────────────────────────────────
123456789   | @john     | John | [User]     | [Set Role ▼]
987654321   | @admin    | Jane | [Admin]    | [Set Role ▼]
```

## 🔐 Bảo Mật

### 1. Đổi Password
File: `webapp/app.py`
```python
ADMIN_PASSWORD = "admin123"  # ← Đổi thành mật khẩu mạnh
```

### 2. Secret Key
File: `webapp/app.py`
```python
app.secret_key = 'your-secret-key-change-this-in-production'
```

Tạo secret key ngẫu nhiên:
```python
import secrets
print(secrets.token_hex(32))
```

### 3. Production Deployment

**Không dùng Flask development server cho production!**

Dùng production WSGI server như Gunicorn:

```bash
# Cài đặt
pip install gunicorn

# Chạy
gunicorn -w 4 -b 0.0.0.0:5000 webapp.app:app
```

**Hoặc dùng Waitress (Windows):**
```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 webapp.app:app
```

## 📱 Responsive Design

Web panel tương thích với:
- 💻 Desktop
- 📱 Tablet  
- 📱 Mobile

Bootstrap 5 responsive layout tự động điều chỉnh.

## 🛠️ Troubleshooting

### Lỗi: "Template not found"
```bash
# Kiểm tra cấu trúc thư mục
webapp/
  ├── app.py
  ├── templates/
  │   ├── base.html
  │   ├── login.html
  │   ├── dashboard.html
  │   ├── users.html
  │   └── invoices.html
  └── static/
      └── style.css
```

### Lỗi: "Database not found"
```bash
# Chạy bot trước để tạo database
python main.py

# Hoặc chạy migration
python migrate_database.py
```

### Lỗi: "Port 5000 already in use"
```python
# Đổi port trong webapp/app.py (dòng cuối)
app.run(debug=True, host='0.0.0.0', port=8080)  # ← Đổi port
```

## 🔄 Workflow

### Duyệt hóa đơn qua web:

1. User gửi invoice qua Telegram bot
2. Admin login vào web panel
3. Vào **Invoices** → **Pending**
4. Click ✅ để approve hoặc ❌ để reject
5. Nếu reject: nhập lý do
6. User nhận notification trên Telegram

### Set role cho user mới:

1. User sử dụng bot lần đầu (tự động tạo account với role=user)
2. Admin login web panel
3. Vào **Users**
4. Tìm user mới
5. Click **Set Role** → chọn Accountant hoặc Admin
6. Confirm → Role được cập nhật ngay lập tức

## 📊 API Endpoints

Web panel cũng cung cấp JSON API:

```bash
GET  /api/stats              # Thống kê 7 ngày
POST /users/set_role/<id>    # Set role
POST /invoices/approve/<id>  # Approve invoice
POST /invoices/reject/<id>   # Reject invoice
```

## 🎯 Best Practices

1. **Luôn đổi mật khẩu mặc định**
2. **Sử dụng HTTPS trong production**
3. **Đặt secret key phức tạp và bảo mật**
4. **Backup database thường xuyên**
5. **Giới hạn access bằng firewall/VPN**
6. **Sử dụng production WSGI server**
7. **Enable logging để audit actions**

## 🚀 Deployment Options

### Option 1: Local Network
```bash
# Chạy trên local network
python webapp/app.py
# Access: http://YOUR_LOCAL_IP:5000
```

### Option 2: Ngrok (Temporary Public URL)
```bash
# Install ngrok
# Run web
python webapp/app.py

# In another terminal
ngrok http 5000
# Access: https://xxxx.ngrok.io
```

### Option 3: Cloud (Heroku, Railway, Render)
- Push code to Git repository
- Deploy as Flask app
- Set environment variables
- Use PostgreSQL instead of SQLite

## 📞 Support

Nếu gặp vấn đề:
1. Kiểm tra file log
2. Đảm bảo database đã được migrate
3. Verify dependencies đã được cài đủ
4. Check port không bị conflict

## 🎉 Features Summary

✅ Dashboard với realtime statistics  
✅ User management với role-based access  
✅ Invoice approval workflow  
✅ AJAX updates (no page reload)  
✅ Responsive design (mobile-friendly)  
✅ Toast notifications  
✅ Bootstrap 5 UI  
✅ Secure authentication  
✅ Simple and intuitive  

---

**Developed for Telegram Accounting Bot**  
**Version 2.0 - Web Admin Panel**  
**© 2025**
