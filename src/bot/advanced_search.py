"""Advanced search commands"""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger
from datetime import datetime, timedelta

from src.database.repository import InvoiceRepository

router = Router()
invoice_repo = InvoiceRepository()

@router.message(Command("search_date"))
async def cmd_search_date(message: Message):
    """
    Tìm kiếm theo khoảng thời gian
    Cú pháp: /search_date DD/MM/YYYY DD/MM/YYYY
    """
    try:
        parts = message.text.split()
        if len(parts) < 3:
            await message.answer(
                "📅 Cú pháp: /search_date DD/MM/YYYY DD/MM/YYYY\n"
                "Ví dụ: /search_date 01/12/2025 31/12/2025"
            )
            return
        
        start_date = datetime.strptime(parts[1], '%d/%m/%Y')
        end_date = datetime.strptime(parts[2], '%d/%m/%Y')
        
        invoices = invoice_repo.get_by_date_range(start_date, end_date)
        
        if not invoices:
            await message.answer(f"❌ Không tìm thấy hóa đơn từ {parts[1]} đến {parts[2]}")
            return
        
        total_amount = sum(inv.total_amount for inv in invoices)
        
        text = f"📅 <b>KẾT QUẢ TÌM KIẾM THEO NGÀY</b>\n\n"
        text += f"📆 Từ: {parts[1]}\n"
        text += f"📆 Đến: {parts[2]}\n"
        text += f"📊 Tìm thấy: {len(invoices)} hóa đơn\n"
        text += f"💰 Tổng tiền: <b>{total_amount:,.0f} VNĐ</b>\n\n"
        
        text += "<b>Chi tiết:</b>\n"
        for inv in invoices[:10]:  # Limit 10
            status_icon = {"pending": "⏳", "approved": "✅", "rejected": "❌"}.get(inv.status, "❓")
            text += f"\n{status_icon} #{inv.id} - {inv.invoice_date.strftime('%d/%m/%Y')}\n"
            text += f"   🏢 {inv.supplier_name}\n"
            text += f"   💰 {inv.total_amount:,.0f} VNĐ\n"
        
        if len(invoices) > 10:
            text += f"\n<i>... và {len(invoices) - 10} hóa đơn khác</i>"
        
        await message.answer(text, parse_mode="HTML")
        
    except ValueError:
        await message.answer("❌ Định dạng ngày không đúng! Dùng DD/MM/YYYY")
    except Exception as e:
        logger.error(f"Error in search_date: {e}")
        await message.answer(f"❌ Lỗi: {e}")

@router.message(Command("search_amount"))
async def cmd_search_amount(message: Message):
    """
    Tìm kiếm theo khoảng giá
    Cú pháp: /search_amount min max
    """
    try:
        parts = message.text.split()
        if len(parts) < 3:
            await message.answer(
                "💰 Cú pháp: /search_amount min max\n"
                "Ví dụ: /search_amount 1000000 5000000"
            )
            return
        
        min_amount = float(parts[1])
        max_amount = float(parts[2])
        
        invoices = invoice_repo.get_by_amount_range(min_amount, max_amount)
        
        if not invoices:
            await message.answer(
                f"❌ Không tìm thấy hóa đơn từ {min_amount:,.0f} đến {max_amount:,.0f} VNĐ"
            )
            return
        
        total_amount = sum(inv.total_amount for inv in invoices)
        
        text = f"💰 <b>KẾT QUẢ TÌM KIẾM THEO GIÁ TRỊ</b>\n\n"
        text += f"💵 Từ: {min_amount:,.0f} VNĐ\n"
        text += f"💵 Đến: {max_amount:,.0f} VNĐ\n"
        text += f"📊 Tìm thấy: {len(invoices)} hóa đơn\n"
        text += f"💰 Tổng: <b>{total_amount:,.0f} VNĐ</b>\n\n"
        
        text += "<b>Chi tiết:</b>\n"
        for inv in invoices[:10]:
            status_icon = {"pending": "⏳", "approved": "✅", "rejected": "❌"}.get(inv.status, "❓")
            text += f"\n{status_icon} #{inv.id} - {inv.invoice_number}\n"
            text += f"   🏢 {inv.supplier_name}\n"
            text += f"   💰 <b>{inv.total_amount:,.0f} VNĐ</b>\n"
        
        if len(invoices) > 10:
            text += f"\n<i>... và {len(invoices) - 10} hóa đơn khác</i>"
        
        await message.answer(text, parse_mode="HTML")
        
    except ValueError:
        await message.answer("❌ Giá trị không hợp lệ! Nhập số")
    except Exception as e:
        logger.error(f"Error in search_amount: {e}")
        await message.answer(f"❌ Lỗi: {e}")

@router.message(Command("search_supplier"))
async def cmd_search_supplier(message: Message):
    """
    Tìm kiếm theo nhà cung cấp
    Cú pháp: /search_supplier tên nhà cung cấp
    """
    try:
        # Lấy tên nhà cung cấp (sau command)
        supplier_name = message.text.replace("/search_supplier", "").strip()
        
        if not supplier_name:
            await message.answer(
                "🏢 Cú pháp: /search_supplier tên nhà cung cấp\n"
                "Ví dụ: /search_supplier CÔNG TY TNHH ABC"
            )
            return
        
        invoices = invoice_repo.search(supplier_name)
        
        # Filter by supplier_name specifically
        invoices = [inv for inv in invoices if supplier_name.lower() in inv.supplier_name.lower()]
        
        if not invoices:
            await message.answer(f"❌ Không tìm thấy hóa đơn của '{supplier_name}'")
            return
        
        total_amount = sum(inv.total_amount for inv in invoices)
        
        text = f"🏢 <b>KẾT QUẢ TÌM KIẾM NHÀ CUNG CẤP</b>\n\n"
        text += f"🔍 Từ khóa: {supplier_name}\n"
        text += f"📊 Tìm thấy: {len(invoices)} hóa đơn\n"
        text += f"💰 Tổng: <b>{total_amount:,.0f} VNĐ</b>\n\n"
        
        text += "<b>Chi tiết:</b>\n"
        for inv in invoices[:10]:
            status_icon = {"pending": "⏳", "approved": "✅", "rejected": "❌"}.get(inv.status, "❓")
            text += f"\n{status_icon} #{inv.id} - {inv.invoice_date.strftime('%d/%m/%Y')}\n"
            text += f"   🏢 {inv.supplier_name}\n"
            text += f"   💰 {inv.total_amount:,.0f} VNĐ\n"
            text += f"   📝 {inv.description[:50]}...\n"
        
        if len(invoices) > 10:
            text += f"\n<i>... và {len(invoices) - 10} hóa đơn khác</i>"
        
        await message.answer(text, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error in search_supplier: {e}")
        await message.answer(f"❌ Lỗi: {e}")

@router.message(Command("search_category"))
async def cmd_search_category(message: Message):
    """
    Tìm kiếm theo danh mục
    Cú pháp: /search_category tên danh mục
    """
    try:
        category = message.text.replace("/search_category", "").strip()
        
        if not category:
            await message.answer(
                "📂 Cú pháp: /search_category tên danh mục\n"
                "Ví dụ: /search_category Chi Phí Văn Phòng Phẩm"
            )
            return
        
        invoices = invoice_repo.get_by_category(category)
        
        if not invoices:
            await message.answer(f"❌ Không tìm thấy hóa đơn danh mục '{category}'")
            return
        
        total_amount = sum(inv.total_amount for inv in invoices)
        
        text = f"📂 <b>KẾT QUẢ TÌM KIẾM THEO DANH MỤC</b>\n\n"
        text += f"🏷️ Danh mục: {category}\n"
        text += f"📊 Tìm thấy: {len(invoices)} hóa đơn\n"
        text += f"💰 Tổng: <b>{total_amount:,.0f} VNĐ</b>\n\n"
        
        text += "<b>Chi tiết:</b>\n"
        for inv in invoices[:10]:
            status_icon = {"pending": "⏳", "approved": "✅", "rejected": "❌"}.get(inv.status, "❓")
            text += f"\n{status_icon} #{inv.id} - {inv.invoice_date.strftime('%d/%m/%Y')}\n"
            text += f"   🏢 {inv.supplier_name}\n"
            text += f"   💰 {inv.total_amount:,.0f} VNĐ\n"
        
        if len(invoices) > 10:
            text += f"\n<i>... và {len(invoices) - 10} hóa đơn khác</i>"
        
        await message.answer(text, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error in search_category: {e}")
        await message.answer(f"❌ Lỗi: {e}")

@router.message(Command("search_status"))
async def cmd_search_status(message: Message):
    """
    Tìm kiếm theo trạng thái
    Cú pháp: /search_status pending|approved|rejected
    """
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer(
                "📊 Cú pháp: /search_status [pending|approved|rejected]\n"
                "Ví dụ: /search_status approved"
            )
            return
        
        status = parts[1].lower()
        if status not in ['pending', 'approved', 'rejected']:
            await message.answer("❌ Trạng thái không hợp lệ! (pending/approved/rejected)")
            return
        
        invoices = invoice_repo.get_by_status(status)
        
        if not invoices:
            await message.answer(f"❌ Không tìm thấy hóa đơn trạng thái '{status}'")
            return
        
        total_amount = sum(inv.total_amount for inv in invoices)
        status_names = {
            'pending': '⏳ Chờ duyệt',
            'approved': '✅ Đã duyệt',
            'rejected': '❌ Từ chối'
        }
        
        text = f"📊 <b>HÓA ĐƠN {status_names[status].upper()}</b>\n\n"
        text += f"📊 Tìm thấy: {len(invoices)} hóa đơn\n"
        text += f"💰 Tổng: <b>{total_amount:,.0f} VNĐ</b>\n\n"
        
        text += "<b>Chi tiết:</b>\n"
        for inv in invoices[:10]:
            text += f"\n#{inv.id} - {inv.invoice_date.strftime('%d/%m/%Y')}\n"
            text += f"   🏢 {inv.supplier_name}\n"
            text += f"   💰 {inv.total_amount:,.0f} VNĐ\n"
            if status == 'rejected' and inv.rejection_reason:
                text += f"   📝 Lý do: {inv.rejection_reason[:50]}...\n"
        
        if len(invoices) > 10:
            text += f"\n<i>... và {len(invoices) - 10} hóa đơn khác</i>"
        
        await message.answer(text, parse_mode="HTML")
        
    except Exception as e:
        logger.error(f"Error in search_status: {e}")
        await message.answer(f"❌ Lỗi: {e}")
