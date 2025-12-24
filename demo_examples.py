"""
Demo script - Kiểm tra từng component riêng lẻ
Chạy script này để test các tính năng mà không cần bot Telegram
"""

import sys
from datetime import datetime
from pathlib import Path

def demo_database():
    """Demo database operations"""
    print("\n" + "="*60)
    print("📊 DEMO: Database Operations")
    print("="*60)
    
    from src.database import db_manager
    from src.database.models import Invoice, User
    from src.database.repository import InvoiceRepository, UserRepository
    
    # Create tables
    db_manager.create_tables()
    print("✓ Database tables created")
    
    # Get session
    session = db_manager.get_session()
    
    try:
        # Create a user
        user = UserRepository.create_or_update(
            session,
            telegram_user_id=123456789,
            username="demo_user",
            first_name="Demo",
            last_name="User"
        )
        print(f"✓ Created user: {user.username}")
        
        # Create an invoice
        invoice_data = {
            'invoice_number': 'DEMO-001',
            'invoice_date': datetime.now(),
            'supplier_name': 'Công ty Demo ABC',
            'supplier_tax_code': '0123456789',
            'supplier_address': '123 Demo Street',
            'subtotal': 1000000,
            'tax_rate': 10,
            'tax_amount': 100000,
            'total_amount': 1100000,
            'description': 'Hóa đơn demo',
            'account_code': '642',
            'category': 'Chi phí văn phòng',
            'created_by_user_id': user.telegram_user_id,
            'created_by_username': user.username,
            'file_path': '/demo/path/invoice.jpg',
            'raw_ocr_text': 'Demo OCR text'
        }
        
        invoice = InvoiceRepository.create(session, invoice_data)
        print(f"✓ Created invoice: {invoice.invoice_number}")
        print(f"  → Supplier: {invoice.supplier_name}")
        print(f"  → Amount: {invoice.total_amount:,.0f} VNĐ")
        
        # Search invoice
        results = InvoiceRepository.search(session, 'Demo')
        print(f"✓ Search found {len(results)} invoices")
        
        # Get by user
        user_invoices = InvoiceRepository.get_by_user(session, user.telegram_user_id)
        print(f"✓ User has {len(user_invoices)} invoices")
        
        print("\n✅ Database demo completed successfully!")
        
    finally:
        session.close()

def demo_ocr():
    """Demo OCR processing"""
    print("\n" + "="*60)
    print("📸 DEMO: OCR Processing")
    print("="*60)
    
    print("\n⚠️  OCR Demo requires an actual image file")
    print("To test OCR:")
    print("1. Place an invoice image in 'data/test_invoice.jpg'")
    print("2. Uncomment the code below in demo_examples.py")
    print("\nExample code:")
    print("""
    from src.ocr import ocr_processor
    
    image_path = 'data/test_invoice.jpg'
    text = ocr_processor.extract_text_from_image(image_path)
    print(f"Extracted text: {text[:200]}...")
    """)

def demo_processor():
    """Demo data processor"""
    print("\n" + "="*60)
    print("🤖 DEMO: AI Data Processor")
    print("="*60)
    
    from src.processor import data_processor
    
    # Sample OCR text (Vietnamese invoice)
    sample_text = """
    HÓA ĐƠN GIÁ TRỊ GIA TĂNG
    
    Công ty TNHH ABC Corporation
    Mã số thuế: 0123456789
    Địa chỉ: 123 Nguyễn Văn Linh, Quận 7, TP.HCM
    
    Số hóa đơn: 0001234567
    Ngày 15 tháng 12 năm 2025
    
    Nội dung: Mua văn phòng phẩm
    
    Tiền trước thuế: 1,000,000 VNĐ
    Thuế GTGT (10%): 100,000 VNĐ
    Tổng cộng: 1,100,000 VNĐ
    """
    
    print("Sample OCR text:")
    print(sample_text)
    print("\n⚠️  Note: This requires valid Gemini/OpenAI API key")
    print("Uncomment code below to test with real API:")
    print("""
    invoice_data = data_processor.extract_invoice_data(sample_text)
    print(f"\\nExtracted data:")
    print(f"  Invoice number: {invoice_data.get('invoice_number')}")
    print(f"  Supplier: {invoice_data.get('supplier_name')}")
    print(f"  Total: {invoice_data.get('total_amount'):,.0f} VNĐ")
    """)

def demo_exporter():
    """Demo Excel/Word export"""
    print("\n" + "="*60)
    print("📄 DEMO: Excel & Word Export")
    print("="*60)
    
    from src.database import db_manager
    from src.database.repository import InvoiceRepository
    from src.exporter import ExcelExporter, WordExporter
    
    session = db_manager.get_session()
    
    try:
        # Get invoices
        invoices = InvoiceRepository.get_all(session, limit=10)
        
        if not invoices:
            print("⚠️  No invoices in database. Run demo_database() first!")
            return
        
        print(f"Found {len(invoices)} invoices")
        
        # Export to Excel
        print("\n📊 Exporting to Excel...")
        excel_path = ExcelExporter.export_invoices(invoices)
        print(f"✓ Excel file created: {excel_path}")
        
        # Export to Word
        print("\n📝 Exporting to Word...")
        word_path = WordExporter.export_invoice_report(invoices)
        print(f"✓ Word file created: {word_path}")
        
        print("\n✅ Export demo completed!")
        print(f"\nCheck these files:")
        print(f"  - {excel_path}")
        print(f"  - {word_path}")
        
    finally:
        session.close()

def demo_statistics():
    """Demo statistics"""
    print("\n" + "="*60)
    print("📈 DEMO: Statistics & Analytics")
    print("="*60)
    
    from src.database import db_manager
    from src.database.repository import InvoiceRepository
    from src.exporter import StatisticsExporter
    from datetime import datetime, timedelta
    
    session = db_manager.get_session()
    
    try:
        # Get this month's invoices
        now = datetime.now()
        first_day = now.replace(day=1, hour=0, minute=0, second=0)
        invoices = InvoiceRepository.get_by_date_range(session, first_day, now)
        
        if not invoices:
            print("⚠️  No invoices in database. Run demo_database() first!")
            return
        
        # Generate statistics
        summary = StatisticsExporter.generate_monthly_summary(invoices)
        
        print(f"\n📊 Statistics for {now.month}/{now.year}:")
        print(f"  Total invoices: {summary['total_invoices']}")
        print(f"  Total amount: {summary['total_amount']:,.0f} VNĐ")
        print(f"  Average amount: {summary['average_amount']:,.0f} VNĐ")
        
        print("\n💼 By category:")
        for category, amount in summary['by_category'].items():
            print(f"  • {category}: {amount:,.0f} VNĐ")
        
        print("\n📂 By account:")
        for account, amount in summary['by_account'].items():
            print(f"  • TK {account}: {amount:,.0f} VNĐ")
        
        print("\n✅ Statistics demo completed!")
        
    finally:
        session.close()

def main():
    """Run all demos"""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "TELEGRAM BOT DEMO" + " "*26 + "║")
    print("╚" + "="*58 + "╝")
    
    print("\nSelect demo to run:")
    print("  1. Database Operations")
    print("  2. OCR Processing (requires image)")
    print("  3. AI Data Processor (requires API key)")
    print("  4. Excel/Word Export")
    print("  5. Statistics & Analytics")
    print("  6. Run All (1, 4, 5)")
    print("  0. Exit")
    
    choice = input("\nEnter your choice (0-6): ").strip()
    
    if choice == '1':
        demo_database()
    elif choice == '2':
        demo_ocr()
    elif choice == '3':
        demo_processor()
    elif choice == '4':
        demo_exporter()
    elif choice == '5':
        demo_statistics()
    elif choice == '6':
        demo_database()
        demo_exporter()
        demo_statistics()
    elif choice == '0':
        print("\nBye! 👋")
        return
    else:
        print("\n❌ Invalid choice!")
        return
    
    print("\n" + "="*60)
    print("Demo completed! Press Enter to exit...")
    input()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
