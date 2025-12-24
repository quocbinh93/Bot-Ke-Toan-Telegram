"""
Database Migration Script - v1.0 to v2.0
Thêm các cột mới cho tính năng Approval Workflow và User Roles
"""
import sqlite3
from pathlib import Path
from loguru import logger

def migrate_database(db_path='accounting.db'):
    """Migrate database từ v1.0 sang v2.0"""
    
    if not Path(db_path).exists():
        logger.error(f"Database không tồn tại: {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        logger.info("Starting database migration v1.0 → v2.0...")
        
        # 1. Backup database
        logger.info("Creating backup...")
        cursor.execute("VACUUM")
        
        # 2. Thêm cột mới vào invoices
        logger.info("Migrating invoices table...")
        
        migrations_invoices = [
            ("approved_by_username", "ALTER TABLE invoices ADD COLUMN approved_by_username VARCHAR(100)"),
            ("rejection_reason", "ALTER TABLE invoices ADD COLUMN rejection_reason TEXT"),
        ]
        
        for col_name, sql in migrations_invoices:
            try:
                cursor.execute(sql)
                logger.info(f"✓ Added column: {col_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column" in str(e).lower():
                    logger.warning(f"  Column {col_name} already exists, skipping")
                else:
                    raise
        
        # 3. Tạo index cho status (nếu chưa có)
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoice_status ON invoices(status)")
            logger.info("✓ Created index: idx_invoice_status")
        except Exception as e:
            logger.warning(f"  Index creation failed: {e}")
        
        # 4. Thêm cột mới vào users
        logger.info("Migrating users table...")
        
        migrations_users = [
            ("department", "ALTER TABLE users ADD COLUMN department VARCHAR(100)"),
            ("total_invoices_submitted", "ALTER TABLE users ADD COLUMN total_invoices_submitted INTEGER DEFAULT 0"),
            ("total_invoices_approved", "ALTER TABLE users ADD COLUMN total_invoices_approved INTEGER DEFAULT 0"),
        ]
        
        for col_name, sql in migrations_users:
            try:
                cursor.execute(sql)
                logger.info(f"✓ Added column: {col_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column" in str(e).lower():
                    logger.warning(f"  Column {col_name} already exists, skipping")
                else:
                    raise
        
        # 5. Tạo index cho role
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_role ON users(role)")
            logger.info("✓ Created index: idx_user_role")
        except Exception as e:
            logger.warning(f"  Index creation failed: {e}")
        
        # 6. Update default values cho user counters
        cursor.execute("""
            UPDATE users 
            SET total_invoices_submitted = 0,
                total_invoices_approved = 0
            WHERE total_invoices_submitted IS NULL 
               OR total_invoices_approved IS NULL
        """)
        logger.info("✓ Updated default values for user stats")
        
        # 7. Update invoice counts từ dữ liệu hiện có
        logger.info("Calculating invoice statistics...")
        
        # Count submitted invoices per user
        cursor.execute("""
            UPDATE users
            SET total_invoices_submitted = (
                SELECT COUNT(*) 
                FROM invoices 
                WHERE invoices.created_by_user_id = users.telegram_user_id
            )
        """)
        
        # Count approved invoices (for admins/accountants who approved)
        cursor.execute("""
            UPDATE users
            SET total_invoices_approved = (
                SELECT COUNT(*) 
                FROM invoices 
                WHERE invoices.approved_by = CAST(users.telegram_user_id AS TEXT)
                  AND invoices.status = 'approved'
            )
        """)
        
        logger.info("✓ Calculated invoice statistics")
        
        # Commit changes
        conn.commit()
        
        logger.info("=" * 60)
        logger.info("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)
        
        # Show summary
        cursor.execute("SELECT COUNT(*) FROM invoices")
        total_invoices = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM invoices WHERE status = 'pending'")
        pending = cursor.fetchone()[0]
        
        logger.info(f"Database stats:")
        logger.info(f"  - Total invoices: {total_invoices}")
        logger.info(f"  - Total users: {total_users}")
        logger.info(f"  - Pending invoices: {pending}")
        
        return True
        
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Migration failed: {e}")
        logger.error("Database rolled back to previous state")
        return False
    
    finally:
        conn.close()

def verify_migration(db_path='accounting.db'):
    """Verify migration thành công"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    logger.info("\nVerifying migration...")
    
    # Check invoices columns
    cursor.execute("PRAGMA table_info(invoices)")
    invoice_cols = [col[1] for col in cursor.fetchall()]
    
    required_invoice_cols = ['approved_by_username', 'rejection_reason']
    for col in required_invoice_cols:
        if col in invoice_cols:
            logger.info(f"  ✓ invoices.{col} exists")
        else:
            logger.error(f"  ✗ invoices.{col} missing!")
    
    # Check users columns
    cursor.execute("PRAGMA table_info(users)")
    user_cols = [col[1] for col in cursor.fetchall()]
    
    required_user_cols = ['department', 'total_invoices_submitted', 'total_invoices_approved']
    for col in required_user_cols:
        if col in user_cols:
            logger.info(f"  ✓ users.{col} exists")
        else:
            logger.error(f"  ✗ users.{col} missing!")
    
    # Check indexes
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
    indexes = [idx[0] for idx in cursor.fetchall()]
    
    if 'idx_invoice_status' in indexes:
        logger.info("  ✓ idx_invoice_status exists")
    else:
        logger.warning("  ⚠ idx_invoice_status missing")
    
    if 'idx_user_role' in indexes:
        logger.info("  ✓ idx_user_role exists")
    else:
        logger.warning("  ⚠ idx_user_role missing")
    
    conn.close()
    logger.info("\n✅ Verification complete!")

if __name__ == '__main__':
    import sys
    
    # Configure logging
    logger.add(
        sys.stdout,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level="INFO"
    )
    
    print("=" * 60)
    print("DATABASE MIGRATION TOOL - v1.0 to v2.0")
    print("=" * 60)
    print()
    
    db_path = 'accounting.db'
    
    # Run migration
    success = migrate_database(db_path)
    
    if success:
        # Verify
        verify_migration(db_path)
        
        print()
        print("=" * 60)
        print("🎉 Migration hoàn tất!")
        print("=" * 60)
        print()
        print("Bước tiếp theo:")
        print("1. Restart bot: python main.py")
        print("2. Set admin role cho user đầu tiên:")
        print("   /set_role @your_username admin")
        print("3. Test approval workflow với /pending")
        print()
    else:
        print()
        print("=" * 60)
        print("❌ Migration thất bại!")
        print("=" * 60)
        print("Vui lòng kiểm tra logs và thử lại")
