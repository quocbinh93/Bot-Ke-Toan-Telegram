"""Script để xem dữ liệu trong database"""
import sqlite3
from datetime import datetime
from tabulate import tabulate

def view_all_invoices():
    """Hiển thị tất cả hóa đơn"""
    conn = sqlite3.connect('accounting.db')
    cursor = conn.cursor()
    
    # Lấy tất cả hóa đơn
    cursor.execute("""
        SELECT id, invoice_number, invoice_date, supplier_name, 
               total_amount, status, account_code, category
        FROM invoices
        ORDER BY created_at DESC
    """)
    
    rows = cursor.fetchall()
    
    if rows:
        headers = ['ID', 'Số HĐ', 'Ngày', 'Nhà cung cấp', 'Tổng tiền', 'Trạng thái', 'TK', 'Danh mục']
        print("\n" + "="*120)
        print("DANH SÁCH HÓA ĐƠN")
        print("="*120)
        print(tabulate(rows, headers=headers, tablefmt='grid'))
        print(f"\nTổng số: {len(rows)} hóa đơn")
    else:
        print("\n⚠️  Chưa có hóa đơn nào trong database")
    
    conn.close()

def view_invoice_detail(invoice_id):
    """Hiển thị chi tiết 1 hóa đơn"""
    conn = sqlite3.connect('accounting.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
    row = cursor.fetchone()
    
    if row:
        columns = [desc[0] for desc in cursor.description]
        print("\n" + "="*100)
        print(f"CHI TIẾT HÓA ĐƠN #{invoice_id}")
        print("="*100)
        
        for col, val in zip(columns, row):
            if col in ['raw_ocr_text'] and val and len(str(val)) > 200:
                print(f"{col:25s}: {str(val)[:200]}... (truncated)")
            else:
                print(f"{col:25s}: {val}")
    else:
        print(f"\n⚠️  Không tìm thấy hóa đơn #{invoice_id}")
    
    conn.close()

def view_statistics():
    """Hiển thị thống kê"""
    conn = sqlite3.connect('accounting.db')
    cursor = conn.cursor()
    
    # Tổng số hóa đơn
    cursor.execute("SELECT COUNT(*) FROM invoices")
    total = cursor.fetchone()[0]
    
    # Tổng tiền
    cursor.execute("SELECT SUM(total_amount) FROM invoices")
    total_amount = cursor.fetchone()[0] or 0
    
    # Theo trạng thái
    cursor.execute("""
        SELECT status, COUNT(*), SUM(total_amount)
        FROM invoices
        GROUP BY status
    """)
    status_stats = cursor.fetchall()
    
    # Theo tài khoản
    cursor.execute("""
        SELECT account_code, COUNT(*), SUM(total_amount)
        FROM invoices
        GROUP BY account_code
        ORDER BY COUNT(*) DESC
    """)
    account_stats = cursor.fetchall()
    
    print("\n" + "="*80)
    print("THỐNG KÊ TỔNG QUAN")
    print("="*80)
    print(f"Tổng số hóa đơn: {total}")
    print(f"Tổng tiền: {total_amount:,.0f} VNĐ")
    
    if status_stats:
        print("\n📊 Theo trạng thái:")
        print(tabulate(status_stats, headers=['Trạng thái', 'Số lượng', 'Tổng tiền'], tablefmt='grid'))
    
    if account_stats:
        print("\n📊 Theo tài khoản:")
        print(tabulate(account_stats, headers=['Mã TK', 'Số lượng', 'Tổng tiền'], tablefmt='grid'))
    
    conn.close()

def delete_invoice(invoice_id):
    """Xóa hóa đơn"""
    conn = sqlite3.connect('accounting.db')
    cursor = conn.cursor()
    
    # Kiểm tra tồn tại
    cursor.execute("SELECT invoice_number FROM invoices WHERE id = ?", (invoice_id,))
    row = cursor.fetchone()
    
    if row:
        confirm = input(f"\n⚠️  Bạn có chắc muốn xóa hóa đơn '{row[0]}'? (yes/no): ")
        if confirm.lower() == 'yes':
            cursor.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
            conn.commit()
            print(f"✅ Đã xóa hóa đơn #{invoice_id}")
        else:
            print("❌ Đã hủy")
    else:
        print(f"\n⚠️  Không tìm thấy hóa đơn #{invoice_id}")
    
    conn.close()

def clear_all_invoices():
    """Xóa tất cả hóa đơn"""
    confirm = input("\n⚠️⚠️⚠️  BẠN CÓ CHẮC MUỐN XÓA TẤT CẢ HÓA ĐƠN? (yes/no): ")
    if confirm.lower() == 'yes':
        conn = sqlite3.connect('accounting.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM invoices")
        conn.commit()
        count = cursor.rowcount
        conn.close()
        print(f"✅ Đã xóa {count} hóa đơn")
    else:
        print("❌ Đã hủy")

def main():
    """Menu chính"""
    while True:
        print("\n" + "="*80)
        print("🗂️  DATABASE VIEWER - Telegram Accounting Bot")
        print("="*80)
        print("1. Xem tất cả hóa đơn")
        print("2. Xem chi tiết hóa đơn")
        print("3. Xem thống kê")
        print("4. Xóa hóa đơn")
        print("5. Xóa tất cả hóa đơn")
        print("6. Thoát")
        print("="*80)
        
        choice = input("Chọn chức năng (1-6): ").strip()
        
        if choice == '1':
            view_all_invoices()
        elif choice == '2':
            invoice_id = input("Nhập ID hóa đơn: ").strip()
            if invoice_id.isdigit():
                view_invoice_detail(int(invoice_id))
            else:
                print("⚠️  ID không hợp lệ")
        elif choice == '3':
            view_statistics()
        elif choice == '4':
            invoice_id = input("Nhập ID hóa đơn cần xóa: ").strip()
            if invoice_id.isdigit():
                delete_invoice(int(invoice_id))
            else:
                print("⚠️  ID không hợp lệ")
        elif choice == '5':
            clear_all_invoices()
        elif choice == '6':
            print("\n👋 Tạm biệt!")
            break
        else:
            print("⚠️  Lựa chọn không hợp lệ")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Đã dừng!")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
