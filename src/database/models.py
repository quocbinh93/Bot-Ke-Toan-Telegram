from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.sql import func
from datetime import datetime
from src.database import Base

class Invoice(Base):
    """Model lưu trữ thông tin hóa đơn"""
    __tablename__ = 'invoices'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Thông tin cơ bản
    invoice_number = Column(String(100), unique=True, nullable=False, index=True)
    invoice_date = Column(DateTime, nullable=False)
    supplier_name = Column(String(255), nullable=False)
    supplier_tax_code = Column(String(50))
    supplier_address = Column(Text)
    
    # Thông tin tài chính
    subtotal = Column(Float, default=0.0)  # Tiền trước thuế
    tax_rate = Column(Float, default=10.0)  # Thuế suất (%)
    tax_amount = Column(Float, default=0.0)  # Tiền thuế
    total_amount = Column(Float, nullable=False)  # Tổng tiền
    
    # Thông tin nội dung
    description = Column(Text)  # Mô tả hóa đơn
    items = Column(Text)  # JSON string của các items
    
    # Phân loại kế toán
    account_code = Column(String(20))  # Mã tài khoản kế toán (VD: 642)
    category = Column(String(100))  # Danh mục (VD: Chi phí văn phòng)
    
    # Trạng thái
    status = Column(String(50), default='pending', index=True)  # pending, approved, rejected
    approved_by = Column(String(100))
    approved_by_username = Column(String(100))  # Username người phê duyệt
    approved_at = Column(DateTime)
    rejection_reason = Column(Text)  # Lý do từ chối
    
    # File gốc
    file_path = Column(String(500))  # Đường dẫn file ảnh gốc
    raw_ocr_text = Column(Text)  # Text OCR gốc
    
    # Metadata
    created_by_user_id = Column(Integer, nullable=False)
    created_by_username = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Ghi chú
    notes = Column(Text)
    
    def __repr__(self):
        return f"<Invoice {self.invoice_number} - {self.supplier_name} - {self.total_amount}đ>"
    
    def to_dict(self):
        """Chuyển đổi object thành dictionary"""
        return {
            'id': self.id,
            'invoice_number': self.invoice_number,
            'invoice_date': self.invoice_date.isoformat() if self.invoice_date else None,
            'supplier_name': self.supplier_name,
            'supplier_tax_code': self.supplier_tax_code,
            'supplier_address': self.supplier_address,
            'subtotal': self.subtotal,
            'tax_rate': self.tax_rate,
            'tax_amount': self.tax_amount,
            'total_amount': self.total_amount,
            'description': self.description,
            'account_code': self.account_code,
            'category': self.category,
            'status': self.status,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'file_path': self.file_path,
            'created_by_username': self.created_by_username,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'notes': self.notes
        }

class User(Base):
    """Model lưu trữ thông tin user"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    telegram_user_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(100))
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(String(50), default='user', index=True)  # user, admin, accountant
    department = Column(String(100))  # Phòng ban
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    last_activity = Column(DateTime, default=func.now())
    total_invoices_submitted = Column(Integer, default=0)
    total_invoices_approved = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<User {self.username} ({self.role})>"
