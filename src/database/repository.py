from sqlalchemy.orm import Session
from src.database.models import Invoice, User
from datetime import datetime
from typing import List, Optional
from loguru import logger

class InvoiceRepository:
    """Repository để xử lý các thao tác với Invoice"""
    
    @staticmethod
    def create(session: Session, invoice_data: dict) -> Invoice:
        """Tạo mới một invoice"""
        invoice = Invoice(**invoice_data)
        session.add(invoice)
        session.commit()
        session.refresh(invoice)
        logger.info(f"Created invoice: {invoice.invoice_number}")
        return invoice
    
    @staticmethod
    def get_by_id(session: Session, invoice_id: int) -> Optional[Invoice]:
        """Lấy invoice theo ID"""
        return session.query(Invoice).filter(Invoice.id == invoice_id).first()
    
    @staticmethod
    def get_by_invoice_number(session: Session, invoice_number: str) -> Optional[Invoice]:
        """Lấy invoice theo số hóa đơn"""
        return session.query(Invoice).filter(Invoice.invoice_number == invoice_number).first()
    
    @staticmethod
    def search(session: Session, keyword: str) -> List[Invoice]:
        """Tìm kiếm invoice theo từ khóa"""
        return session.query(Invoice).filter(
            (Invoice.supplier_name.ilike(f'%{keyword}%')) |
            (Invoice.description.ilike(f'%{keyword}%')) |
            (Invoice.invoice_number.ilike(f'%{keyword}%'))
        ).all()
    
    @staticmethod
    def get_by_user(session: Session, user_id: int, limit: int = 50) -> List[Invoice]:
        """Lấy danh sách invoice của user"""
        return session.query(Invoice).filter(
            Invoice.created_by_user_id == user_id
        ).order_by(Invoice.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_by_date_range(session: Session, start_date: datetime, end_date: datetime) -> List[Invoice]:
        """Lấy danh sách invoice trong khoảng thời gian"""
        return session.query(Invoice).filter(
            Invoice.invoice_date >= start_date,
            Invoice.invoice_date <= end_date
        ).order_by(Invoice.invoice_date.desc()).all()
    
    @staticmethod
    def get_all(session: Session, limit: int = 100) -> List[Invoice]:
        """Lấy tất cả invoice"""
        return session.query(Invoice).order_by(Invoice.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_recent(session: Session, limit: int = 10) -> List[Invoice]:
        """Lấy danh sách invoice gần đây nhất"""
        return session.query(Invoice).order_by(Invoice.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def update(session: Session, invoice_id: int, update_data: dict) -> Optional[Invoice]:
        """Cập nhật invoice"""
        invoice = InvoiceRepository.get_by_id(session, invoice_id)
        if invoice:
            for key, value in update_data.items():
                if hasattr(invoice, key):
                    setattr(invoice, key, value)
            session.commit()
            session.refresh(invoice)
            logger.info(f"Updated invoice: {invoice.invoice_number}")
        return invoice
    
    @staticmethod
    def delete(session: Session, invoice_id: int) -> bool:
        """Xóa invoice"""
        invoice = InvoiceRepository.get_by_id(session, invoice_id)
        if invoice:
            session.delete(invoice)
            session.commit()
            logger.info(f"Deleted invoice: {invoice.invoice_number}")
            return True
        return False

class UserRepository:
    """Repository để xử lý các thao tác với User"""
    
    @staticmethod
    def create_or_update(session: Session, telegram_user_id: int, **kwargs) -> User:
        """Tạo mới hoặc cập nhật user"""
        user = session.query(User).filter(User.telegram_user_id == telegram_user_id).first()
        
        if user:
            # Update existing user
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            user.last_activity = datetime.now()
        else:
            # Create new user
            user = User(telegram_user_id=telegram_user_id, **kwargs)
            session.add(user)
        
        session.commit()
        session.refresh(user)
        return user
    
    @staticmethod
    def get_by_telegram_id(session: Session, telegram_user_id: int) -> Optional[User]:
        """Lấy user theo Telegram ID"""
        return session.query(User).filter(User.telegram_user_id == telegram_user_id).first()
    
    @staticmethod
    def get_by_username(session: Session, username: str) -> Optional[User]:
        """Lấy user theo username"""
        return session.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_all(session: Session) -> List[User]:
        """Lấy tất cả users"""
        return session.query(User).order_by(User.created_at.desc()).all()
    
    @staticmethod
    def count_all(session: Session) -> int:
        """Đếm tổng số users"""
        return session.query(User).count()
    
    @staticmethod
    def update_role(session: Session, user_id: int, new_role: str) -> Optional[User]:
        """Cập nhật role của user"""
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            user.role = new_role
            session.commit()
            session.refresh(user)
            logger.info(f"Updated role for user {user.username}: {new_role}")
        return user
    
    @staticmethod
    def increment_submitted_count(session: Session, telegram_user_id: int):
        """Tăng số lượng hóa đơn đã gửi"""
        user = UserRepository.get_by_telegram_id(session, telegram_user_id)
        if user:
            user.total_invoices_submitted = (user.total_invoices_submitted or 0) + 1
            session.commit()
    
    @staticmethod
    def increment_approved_count(session: Session, telegram_user_id: int):
        """Tăng số lượng hóa đơn đã duyệt"""
        user = UserRepository.get_by_telegram_id(session, telegram_user_id)
        if user:
            user.total_invoices_approved = (user.total_invoices_approved or 0) + 1
            session.commit()

class InvoiceRepositoryExtended:
    """Extended methods cho InvoiceRepository"""
    
    @staticmethod
    def get_by_status(session: Session, status: str, limit: int = 100) -> List[Invoice]:
        """Lấy hóa đơn theo trạng thái"""
        return session.query(Invoice).filter(
            Invoice.status == status
        ).order_by(Invoice.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def count_by_status(session: Session, status: str) -> int:
        """Đếm hóa đơn theo trạng thái"""
        return session.query(Invoice).filter(Invoice.status == status).count()
    
    @staticmethod
    def count_all(session: Session) -> int:
        """Đếm tổng số hóa đơn"""
        return session.query(Invoice).count()
    
    @staticmethod
    def get_total_amount(session: Session) -> float:
        """Tính tổng giá trị hóa đơn"""
        from sqlalchemy import func
        result = session.query(func.sum(Invoice.total_amount)).scalar()
        return result or 0.0
    
    @staticmethod
    def get_total_amount_by_status(session: Session, status: str) -> float:
        """Tính tổng giá trị theo trạng thái"""
        from sqlalchemy import func
        result = session.query(func.sum(Invoice.total_amount)).filter(
            Invoice.status == status
        ).scalar()
        return result or 0.0
    
    @staticmethod
    def get_by_amount_range(session: Session, min_amount: float, max_amount: float) -> List[Invoice]:
        """Lấy hóa đơn trong khoảng giá"""
        return session.query(Invoice).filter(
            Invoice.total_amount >= min_amount,
            Invoice.total_amount <= max_amount
        ).order_by(Invoice.total_amount.desc()).all()
    
    @staticmethod
    def get_by_category(session: Session, category: str) -> List[Invoice]:
        """Lấy hóa đơn theo danh mục"""
        return session.query(Invoice).filter(
            Invoice.category.ilike(f'%{category}%')
        ).order_by(Invoice.created_at.desc()).all()

# Merge extended methods vào InvoiceRepository
for attr_name in dir(InvoiceRepositoryExtended):
    if not attr_name.startswith('_'):
        setattr(InvoiceRepository, attr_name, getattr(InvoiceRepositoryExtended, attr_name))
