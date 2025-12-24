# 🎉 TELEGRAM ACCOUNTING BOT - VERSION 2.0

## ✨ TÍNH NĂNG MỚI

### 1. 👥 **USER ROLES & PERMISSIONS**
- **3 vai trò**: User, Accountant, Admin
- Phân quyền chi tiết cho từng vai trò
- Admin panel để quản lý users
- Command `/set_role` để phân quyền

### 2. 🔄 **APPROVAL WORKFLOW**
- Hóa đơn tự động chuyển trạng thái "pending" khi upload
- Admin/Accountant duyệt qua inline keyboard
- Lý do từ chối được lưu vào database
- Notification tự động cho user khi được duyệt/từ chối

### 3. 🔍 **ADVANCED SEARCH (6 loại)**
- `/search_date` - Tìm theo khoảng thời gian
- `/search_amount` - Tìm theo khoảng giá
- `/search_supplier` - Tìm theo nhà cung cấp
- `/search_category` - Tìm theo 22 danh mục chi phí
- `/search_status` - Tìm theo trạng thái
- `/search` - Tìm kiếm cơ bản (đã có)

### 4. 🔔 **NOTIFICATION SYSTEM**
- Thông báo khi hóa đơn được duyệt
- Thông báo khi hóa đơn bị từ chối (kèm lý do)
- Hiển thị username người duyệt

### 5. 📊 **ENHANCED ADMIN FEATURES**
- `/admin` - Admin dashboard
- `/pending` - Xem hóa đơn chờ duyệt với inline buttons
- `/users` - Danh sách users và thống kê
- `/stats_admin` - Thống kê chi tiết cho admin

### 6. 📂 **22 DANH MỤC CHI PHÍ MỚI**
Phân loại tự động với Title Case:
- Chi Phí Nhân Sự
- Chi Phí Tiện Ích - Điện Nước
- Chi Phí Viễn Thông
- Chi Phí Văn Phòng Phẩm
- Chi Phí Thuê Mặt Bằng
- Chi Phí Marketing & Quảng Cáo
- Chi Phí Đào Tạo
- Chi Phí Vận Chuyển
- Chi Phí Xăng Xe & Đi Lại
- Chi Phí Bảo Hiểm
- Chi Phí Thuế & Phí
- Chi Phí Sửa Chữa & Bảo Trì
- Chi Phí Khấu Hao
- Chi Phí Nguyên Vật Liệu
- Chi Phí Ăn Uống & Tiếp Khách
- Chi Phí In Ấn
- Chi Phí Phần Mềm & Công Nghệ
- Chi Phí Tài Chính
- Chi Phí Đồ Dùng & Thiết Bị
- Chi Phí Y Tế & An Toàn
- Chi Phí Quà Tặng & Phúc Lợi
- Chi Phí Dịch Vụ Chuyên Nghiệp

---

## 📦 FILES MỚI

### 1. **src/bot/admin.py** (320 dòng)
Admin commands và approval workflow:
- `cmd_admin()` - Admin panel
- `cmd_pending()` - Xem pending invoices
- `callback_approve()` - Duyệt hóa đơn
- `callback_reject()` - Từ chối hóa đơn
- `cmd_users()` - Quản lý users
- `cmd_set_role()` - Phân quyền
- `cmd_stats_admin()` - Thống kê admin

### 2. **src/bot/advanced_search.py** (240 dòng)
6 commands tìm kiếm nâng cao:
- `cmd_search_date()`
- `cmd_search_amount()`
- `cmd_search_supplier()`
- `cmd_search_category()`
- `cmd_search_status()`

### 3. **FEATURES_V2.md** (400+ dòng)
Documentation đầy đủ cho version 2.0:
- User roles giải thích chi tiết
- Approval workflow diagram
- Advanced search examples
- Use cases
- Setup guide
- Testing guide

### 4. **migrate_database.py** (200 dòng)
Migration tool tự động:
- Thêm cột mới vào database
- Tạo indexes
- Verify migration
- Calculate statistics

### 5. **NEW_FEATURES_SUMMARY.md** (file này)
Tóm tắt các tính năng mới

---

## 🗄️ DATABASE CHANGES

### Invoices Table:
```sql
-- Cột mới
approved_by_username VARCHAR(100)  -- Username người duyệt
rejection_reason TEXT              -- Lý do từ chối

-- Index mới
CREATE INDEX idx_invoice_status ON invoices(status);
```

### Users Table:
```sql
-- Cột mới
department VARCHAR(100)                    -- Phòng ban
total_invoices_submitted INTEGER DEFAULT 0  -- Tổng HĐ đã gửi
total_invoices_approved INTEGER DEFAULT 0   -- Tổng HĐ đã duyệt

-- Index mới
CREATE INDEX idx_user_role ON users(role);
```

---

## 🚀 INSTALLATION & UPGRADE

### Bước 1: Backup Database
```bash
cp accounting.db accounting.db.backup
```

### Bước 2: Pull Code Mới
```bash
git pull origin main
```

### Bước 3: Chạy Migration
```bash
python migrate_database.py
```

### Bước 4: Restart Bot
```bash
# Stop bot hiện tại (Ctrl+C)
python main.py
```

### Bước 5: Set Admin Role
Trong bot, user đầu tiên cần được set làm admin:
```bash
# Gõ trong Telegram (nếu đã có admin):
/set_role @your_username admin

# Hoặc edit trực tiếp DB:
UPDATE users SET role = 'admin' WHERE telegram_user_id = YOUR_ID;
```

---

## 📋 COMMANDS CHI TIẾT

### Commands Cho Mọi User:
```
/start              - Bắt đầu
/help               - Hướng dẫn
/stats              - Thống kê cá nhân
/recent             - 10 HĐ gần nhất
/excel              - Xuất Excel
/word               - Xuất Word
/search [keyword]   - Tìm kiếm cơ bản

/search_date DD/MM/YYYY DD/MM/YYYY  - Tìm theo ngày
/search_amount min max              - Tìm theo giá
/search_supplier [name]             - Tìm theo NCC
/search_category [category]         - Tìm theo danh mục
/search_status [status]             - Tìm theo trạng thái
```

### Commands Cho Admin/Accountant:
```
/admin              - Admin panel
/pending            - HĐ chờ duyệt (có inline buttons)
/users              - Danh sách users
/stats_admin        - Thống kê chi tiết
```

### Commands Chỉ Admin:
```
/set_role @username role  - Phân quyền user
```

---

## 🎯 USE CASE EXAMPLES

### Example 1: Duyệt Hóa Đơn
```
User: [Gửi ảnh hóa đơn]
Bot: ✅ Đã lưu hóa đơn #INV-20251224120000, chờ phê duyệt

Admin: /pending
Bot: [Hiển thị hóa đơn với buttons ✅ Duyệt / ❌ Từ chối]

Admin: [Click ✅ Duyệt]
Bot → Admin: ✅ Đã duyệt hóa đơn!
Bot → User: ✅ Hóa đơn #INV-xxx đã được duyệt! 👤 @admin
```

### Example 2: Tìm Kiếm Theo Ngày
```
User: /search_date 01/12/2025 31/12/2025
Bot: 
📅 KẾT QUẢ TÌM KIẾM THEO NGÀY
📆 Từ: 01/12/2025
📆 Đến: 31/12/2025
📊 Tìm thấy: 15 hóa đơn
💰 Tổng tiền: 45,500,000 VNĐ

[Danh sách 10 hóa đơn đầu tiên...]
```

### Example 3: Phân Quyền User
```
Admin: /users
Bot: [Danh sách users]

Admin: /set_role @john_doe accountant
Bot: ✅ Đã cập nhật role cho @john_doe
     📊 Role mới: accountant
```

---

## 📊 REPOSITORY METHODS MỚI

### InvoiceRepository:
```python
get_by_status(status, limit)
count_by_status(status)
count_all()
get_total_amount()
get_total_amount_by_status(status)
get_by_amount_range(min, max)
get_by_category(category)
```

### UserRepository:
```python
get_by_username(username)
get_all()
count_all()
update_role(user_id, new_role)
increment_submitted_count(telegram_user_id)
increment_approved_count(telegram_user_id)
```

---

## 🧪 TESTING CHECKLIST

- [ ] Upload hóa đơn mới → check status = "pending"
- [ ] Admin `/pending` → thấy hóa đơn
- [ ] Click ✅ Duyệt → check status = "approved"
- [ ] User nhận notification
- [ ] Click ❌ Từ chối → nhập lý do
- [ ] Check rejection_reason trong DB
- [ ] `/search_date` với khoảng thời gian
- [ ] `/search_amount` với khoảng giá
- [ ] `/search_supplier` với tên NCC
- [ ] `/search_category` với danh mục
- [ ] `/search_status approved`
- [ ] `/set_role` để phân quyền
- [ ] `/users` xem danh sách
- [ ] `/stats_admin` xem thống kê

---

## 📈 PERFORMANCE NOTES

- Inline keyboards limit: 100 buttons/message
- `/pending` chỉ hiển thị 10 invoices mỗi lần
- Search commands limit: 10 kết quả đầu tiên
- Indexes được thêm cho `status` và `role` để tăng tốc queries

---

## 🔒 SECURITY

- Role checking dùng `telegram_user_id` (không đổi)
- Username chỉ dùng để hiển thị
- Admin commands có kiểm tra permission
- Callback queries verify user role trước khi execute

---

## 📞 SUPPORT & FEEDBACK

- Đọc docs: `FEATURES_V2.md`
- Report bugs: Create GitHub issue
- Feature requests: TODO.md
- Questions: GitHub Discussions

---

**Version**: 2.0.0  
**Release Date**: December 24, 2025  
**Backward Compatible**: ✅ Yes (với migration)  
**Breaking Changes**: ❌ None  

**Developed by**: Telegram Accounting Bot Team  
**License**: MIT
