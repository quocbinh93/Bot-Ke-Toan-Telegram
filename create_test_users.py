"""
Script để tạo user test cho Web Admin Panel
"""
import sys
from src.database import init_db, db_manager
from src.database.models import User
from datetime import datetime

def create_test_user(telegram_user_id: int, username: str, full_name: str, role: str = 'user'):
    """Tạo test user"""
    init_db()
    session = db_manager.get_session()
    
    try:
        # Check if user exists
        existing_user = session.query(User).filter(
            User.telegram_user_id == telegram_user_id
        ).first()
        
        if existing_user:
            print(f"❌ User {telegram_user_id} already exists!")
            return
        
        # Create new user
        user = User(
            telegram_user_id=telegram_user_id,
            username=username,
            first_name=full_name.split()[0] if full_name else username,
            last_name=' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else None,
            role=role,
            department=None,
            is_active=True,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            total_invoices_submitted=0,
            total_invoices_approved=0
        )
        
        session.add(user)
        session.commit()
        
        print(f"✅ Created user: {full_name} (@{username}) with role: {role}")
        print(f"   Telegram ID: {telegram_user_id}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == '__main__':
    print("=" * 50)
    print("CREATE TEST USERS FOR WEB ADMIN PANEL")
    print("=" * 50)
    print()
    
    # Create admin user
    create_test_user(
        telegram_user_id=123456789,
        username='admin',
        full_name='Admin User',
        role='admin'
    )
    
    # Create accountant
    create_test_user(
        telegram_user_id=987654321,
        username='accountant',
        full_name='Kế Toán Trưởng',
        role='accountant'
    )
    
    # Create regular users
    create_test_user(
        telegram_user_id=111222333,
        username='user1',
        full_name='Nguyễn Văn A',
        role='user'
    )
    
    create_test_user(
        telegram_user_id=444555666,
        username='user2',
        full_name='Trần Thị B',
        role='user'
    )
    
    print()
    print("=" * 50)
    print("✅ DONE! Now refresh your web admin panel.")
    print("=" * 50)
