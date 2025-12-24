# 🚀 NEW FEATURES v2.0 - Approval Workflow & Advanced Search

## 📋 Overview

Version 2.0 của Bot Kế Toán Telegram bao gồm các tính năng mới:

1. **Approval Workflow** - Quy trình phê duyệt hóa đơn
2. **User Roles** - Phân quyền Admin/Accountant/User
3. **Advanced Search** - Tìm kiếm nâng cao theo nhiều tiêu chí
4. **Notification System** - Thông báo tự động cho admin và user

---

## 👥 User Roles

### 3 Loại Vai Trò:

#### 1. **User** (Người dùng thường)
- Gửi hóa đơn vào bot
- Xem hóa đơn của mình
- Nhận thông báo khi hóa đơn được duyệt/từ chối
- **Không thể**: Duyệt hóa đơn, quản lý users

#### 2. **Accountant** (Kế toán viên)
- Tất cả quyền của User
- Xem tất cả hóa đơn chờ duyệt
- Duyệt hoặc từ chối hóa đơn
- Xem thống kê admin
- **Không thể**: Phân quyền users

#### 3. **Admin** (Quản trị viên)
- Tất cả quyền của Accountant
- Quản lý danh sách users
- Phân quyền cho users
- Truy cập toàn bộ admin panel

---

## 🔄 Approval Workflow

### Quy Trình Phê Duyệt:

```
User gửi hóa đơn
      ↓
Bot OCR & trích xuất
      ↓
Status = "pending" (Chờ duyệt)
      ↓
Admin nhận notification
      ↓
Admin review và quyết định
      ↓
  ✅ Duyệt  hoặc  ❌ Từ chối
      ↓
User nhận thông báo
```

### Commands cho Approval:

#### `/admin` - Admin Panel
Hiển thị:
- Số hóa đơn chờ duyệt
- Tổng số users
- Các lệnh admin có sẵn

#### `/pending` - Xem Hóa Đơn Chờ Duyệt
- Hiển thị tối đa 10 hóa đơn pending
- Mỗi hóa đơn có inline keyboard:
  - ✅ **Duyệt** - Approve ngay lập tức
  - ❌ **Từ chối** - Nhập lý do từ chối
  - 👁️ **Xem ảnh** - Xem file hóa đơn gốc

### Trạng Thái Hóa Đơn:

- **pending** ⏳ - Chờ duyệt (mặc định)
- **approved** ✅ - Đã duyệt
- **rejected** ❌ - Đã từ chối

---

## 🔍 Advanced Search

### 6 Loại Tìm Kiếm Mới:

#### 1. `/search_date DD/MM/YYYY DD/MM/YYYY`
Tìm hóa đơn trong khoảng thời gian

**Ví dụ:**
```
/search_date 01/12/2025 31/12/2025
```

**Kết quả:**
- Danh sách hóa đơn từ 01/12 đến 31/12
- Tổng số hóa đơn và tổng tiền
- Hiển thị 10 hóa đơn đầu tiên

#### 2. `/search_amount min max`
Tìm hóa đơn theo khoảng giá

**Ví dụ:**
```
/search_amount 1000000 5000000
```
Tìm hóa đơn từ 1 triệu đến 5 triệu VNĐ

#### 3. `/search_supplier [tên nhà cung cấp]`
Tìm theo nhà cung cấp

**Ví dụ:**
```
/search_supplier CÔNG TY TNHH ABC
```

#### 4. `/search_category [danh mục]`
Tìm theo danh mục chi phí

**Ví dụ:**
```
/search_category Chi Phí Văn Phòng Phẩm
```

**Các danh mục có sẵn:**
- Chi Phí Nhân Sự
- Chi Phí Tiện Ích - Điện Nước
- Chi Phí Viễn Thông
- Chi Phí Văn Phòng Phẩm
- Chi Phí Thuê Mặt Bằng
- Chi Phí Marketing & Quảng Cáo
- ... (22 danh mục)

#### 5. `/search_status [pending|approved|rejected]`
Tìm theo trạng thái

**Ví dụ:**
```
/search_status approved
```

#### 6. `/search [từ khóa]`
Tìm kiếm cơ bản (đã có sẵn)

---

## 👥 User Management

### `/users` - Danh Sách Users

Hiển thị:
- Tất cả users trong hệ thống
- Role của từng user
- Số hóa đơn đã gửi và đã duyệt
- Trạng thái active/inactive

### `/set_role @username role`
Phân quyền cho user

**Cú pháp:**
```
/set_role @username [user|accountant|admin]
```

**Ví dụ:**
```
/set_role @john_doe accountant
```

**Lưu ý:**
- Chỉ Admin mới có quyền dùng lệnh này
- Username phải có @ ở đầu
- Role phải là: user, accountant, hoặc admin

---

## 📊 Admin Statistics

### `/stats_admin` - Thống Kê Chi Tiết

Hiển thị:
- Tổng số hóa đơn (tất cả trạng thái)
- Số hóa đơn chờ duyệt / đã duyệt / từ chối
- Tổng giá trị hóa đơn
- Tổng giá trị đã duyệt
- Tỷ lệ duyệt (%)

---

## 🔔 Notification System

### Thông Báo Tự Động:

#### 1. Khi User Gửi Hóa Đơn:
- User nhận: "✅ Hóa đơn đã được lưu, chờ phê duyệt"
- Admin/Accountant: Không nhận notification (xem qua /pending)

#### 2. Khi Admin Duyệt:
- User nhận:
  ```
  ✅ Hóa đơn #INV-xxx của bạn đã được duyệt!
  👤 Người duyệt: @admin_username
  ```

#### 3. Khi Admin Từ Chối:
- User nhận:
  ```
  ❌ Hóa đơn #INV-xxx đã bị từ chối
  
  📝 Lý do: [lý do từ admin]
  👤 Người từ chối: @admin_username
  ```

---

## 🗄️ Database Changes

### Bảng `invoices`:
**Cột mới:**
- `status` (VARCHAR) - pending/approved/rejected (có index)
- `approved_by_username` (VARCHAR) - Username người duyệt
- `rejection_reason` (TEXT) - Lý do từ chối

### Bảng `users`:
**Cột mới:**
- `role` (VARCHAR) - user/accountant/admin (có index)
- `department` (VARCHAR) - Phòng ban
- `total_invoices_submitted` (INT) - Tổng số HĐ đã gửi
- `total_invoices_approved` (INT) - Tổng số HĐ đã duyệt (cho admin)

---

## 📖 Use Cases

### Use Case 1: Nhân viên gửi hóa đơn

1. Nhân viên (User) chụp ảnh hóa đơn và gửi vào bot
2. Bot OCR và trích xuất thông tin
3. Hóa đơn được lưu với status = "pending"
4. Nhân viên nhận thông báo: "Đã lưu, chờ duyệt"

### Use Case 2: Kế toán viên duyệt hóa đơn

1. Kế toán viên gõ `/pending`
2. Bot hiển thị 10 hóa đơn chờ duyệt
3. Kế toán viên nhấn "✅ Duyệt" hoặc "❌ Từ chối"
4. Nếu từ chối → nhập lý do
5. Nhân viên nhận thông báo kết quả

### Use Case 3: Admin phân quyền

1. Admin gõ `/users` để xem danh sách
2. Muốn thăng John Doe lên Accountant
3. Gõ: `/set_role @john_doe accountant`
4. John Doe giờ có quyền duyệt hóa đơn

### Use Case 4: Tìm kiếm nâng cao

1. Giám đốc muốn xem chi phí tháng 12
2. Gõ: `/search_date 01/12/2025 31/12/2025`
3. Bot hiển thị tất cả HĐ trong tháng
4. Muốn lọc thêm theo danh mục
5. Gõ: `/search_category Chi Phí Marketing`

---

## ⚙️ Setup & Configuration

### 1. Tạo Admin User Đầu Tiên

Sau khi chạy bot lần đầu, cần set role cho admin:

```python
# Chạy trong Python shell hoặc tạo script
from src.database import db_manager
from src.database.repository import UserRepository

with db_manager.session_scope() as session:
    user_repo = UserRepository()
    # Thay YOUR_TELEGRAM_ID bằng ID Telegram của bạn
    user = user_repo.get_by_telegram_id(session, YOUR_TELEGRAM_ID)
    if user:
        user_repo.update_role(session, user.id, 'admin')
        print("✅ Admin role set!")
```

Hoặc edit trực tiếp database:
```sql
UPDATE users SET role = 'admin' WHERE telegram_user_id = YOUR_TELEGRAM_ID;
```

### 2. Migration Database

Nếu nâng cấp từ v1.0:

```sql
-- Thêm cột mới vào invoices
ALTER TABLE invoices ADD COLUMN approved_by_username VARCHAR(100);
ALTER TABLE invoices ADD COLUMN rejection_reason TEXT;
CREATE INDEX idx_invoice_status ON invoices(status);

-- Thêm cột mới vào users
ALTER TABLE users ADD COLUMN department VARCHAR(100);
ALTER TABLE users ADD COLUMN total_invoices_submitted INTEGER DEFAULT 0;
ALTER TABLE users ADD COLUMN total_invoices_approved INTEGER DEFAULT 0;
CREATE INDEX idx_user_role ON users(role);
```

---

## 🧪 Testing

### Test Approval Workflow:

1. Gửi hóa đơn test với user thường
2. Kiểm tra status = "pending"
3. Login bằng admin account
4. Gõ `/pending` → thấy hóa đơn vừa gửi
5. Nhấn ✅ Duyệt
6. Kiểm tra user nhận notification
7. Verify status = "approved" trong DB

### Test Search:

```bash
# Test search by date
/search_date 01/01/2025 31/12/2025

# Test search by amount
/search_amount 100000 1000000

# Test search by supplier
/search_supplier CÔNG TY

# Test search by category
/search_category Chi Phí Nhân Sự

# Test search by status
/search_status approved
```

---

## 📝 Notes

- **Performance**: Inline keyboards có thể bị limit nếu có quá nhiều pending invoices (> 50)
- **Security**: Username trong Telegram có thể thay đổi, nên dùng telegram_user_id để check quyền
- **Backup**: Nên backup database trước khi migration

---

## 🔜 Future Enhancements

- [ ] Bulk approve/reject
- [ ] Export filtered results to Excel
- [ ] Email notifications (kèm Telegram)
- [ ] Scheduled reports
- [ ] Mobile app integration

---

**Version**: 2.0.0
**Release Date**: December 24, 2025
**Author**: Accounting Bot Team
