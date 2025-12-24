"""
Script test để kiểm tra cấu hình và các module
"""

import sys
from pathlib import Path

def test_config():
    """Test file cấu hình"""
    print("✓ Testing configuration...")
    try:
        import config
        print(f"  ✓ Config loaded")
        print(f"  ✓ Database: {config.DATABASE_URL}")
        print(f"  ✓ OCR Type: {config.OCR_TYPE}")
        print(f"  ✓ AI Provider: {config.AI_PROVIDER}")
        return True
    except Exception as e:
        print(f"  ✗ Config error: {e}")
        return False

def test_database():
    """Test database connection"""
    print("\n✓ Testing database...")
    try:
        from src.database import db_manager
        db_manager.create_tables()
        print("  ✓ Database initialized")
        
        session = db_manager.get_session()
        session.close()
        print("  ✓ Database connection OK")
        return True
    except Exception as e:
        print(f"  ✗ Database error: {e}")
        return False

def test_ocr():
    """Test OCR module"""
    print("\n✓ Testing OCR module...")
    try:
        from src.ocr import ocr_processor
        print("  ✓ OCR processor initialized")
        print("  ⚠ Note: First run will download OCR models (~1-2GB)")
        return True
    except Exception as e:
        print(f"  ✗ OCR error: {e}")
        return False

def test_processor():
    """Test data processor"""
    print("\n✓ Testing data processor...")
    try:
        from src.processor import data_processor
        print("  ✓ Data processor initialized")
        return True
    except Exception as e:
        print(f"  ✗ Processor error: {e}")
        return False

def test_exporter():
    """Test exporter module"""
    print("\n✓ Testing exporter...")
    try:
        from src.exporter import ExcelExporter, WordExporter
        print("  ✓ Excel exporter OK")
        print("  ✓ Word exporter OK")
        return True
    except Exception as e:
        print(f"  ✗ Exporter error: {e}")
        return False

def test_bot_modules():
    """Test bot modules"""
    print("\n✓ Testing bot modules...")
    try:
        from src.bot import commands, handlers, queries
        print("  ✓ Commands module OK")
        print("  ✓ Handlers module OK")
        print("  ✓ Queries module OK")
        return True
    except Exception as e:
        print(f"  ✗ Bot modules error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("  Testing Telegram Accounting Bot Configuration")
    print("=" * 50)
    
    # Check .env file
    env_file = Path('.env')
    if not env_file.exists():
        print("\n✗ ERROR: .env file not found!")
        print("  Please copy .env.example to .env and configure it")
        sys.exit(1)
    
    print("\n✓ .env file found")
    
    results = []
    results.append(("Configuration", test_config()))
    results.append(("Database", test_database()))
    results.append(("OCR Module", test_ocr()))
    results.append(("Data Processor", test_processor()))
    results.append(("Exporter", test_exporter()))
    results.append(("Bot Modules", test_bot_modules()))
    
    # Summary
    print("\n" + "=" * 50)
    print("  Test Summary")
    print("=" * 50)
    
    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8} | {name}")
        if not result:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("\n✅ All tests passed! Bot is ready to run.")
        print("\n📝 Next steps:")
        print("  1. Run: python main.py")
        print("  2. Open Telegram and message your bot")
        print("  3. Send /start command")
    else:
        print("\n⚠️  Some tests failed. Please fix the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
