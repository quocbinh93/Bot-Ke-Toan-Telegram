from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
from aiogram.enums import ParseMode
from datetime import datetime, timedelta
from loguru import logger

from src.database import db_manager
from src.database.repository import InvoiceRepository
from src.exporter import ExcelExporter, WordExporter, StatisticsExporter

router = Router()

@router.message(Command("search"))
async def cmd_search(message: Message):
    """Tìm kiếm hóa đơn"""
    try:
        # Get search keyword
        command_args = message.text.split(maxsplit=1)
        if len(command_args) < 2:
            await message.answer("❌ Vui lòng nhập từ khóa tìm kiếm.\nVí dụ: /search Công ty ABC")
            return
        
        keyword = command_args[1]
        await message.answer(f"🔍 Đang tìm kiếm: {keyword}...")
        
        session = db_manager.get_session()
        try:
            invoices = InvoiceRepository.search(session, keyword)
            
            if not invoices:
                await message.answer("❌ Không tìm thấy hóa đơn nào.")
                return
            
            # Send results
            result_text = f"<b>Tìm thấy {len(invoices)} hóa đơn:</b>\n\n"
            
            for inv in invoices[:10]:  # Limit to 10 results
                result_text += f"""
📄 <b>{inv.invoice_number}</b>
📅 Ngày: {inv.invoice_date.strftime('%d/%m/%Y')}
🏢 NCC: {inv.supplier_name}
💰 Tổng: {inv.total_amount:,.0f} VNĐ
{'—' * 25}
"""
            
            if len(invoices) > 10:
                result_text += f"\n<i>... và {len(invoices) - 10} hóa đơn khác</i>"
            
            await message.answer(result_text, parse_mode=ParseMode.HTML)
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error in search command: {e}")
        await message.answer("❌ Có lỗi xảy ra khi tìm kiếm.")

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    """Hiển thị thống kê"""
    try:
        await message.answer("📊 Đang tính toán thống kê...")
        
        session = db_manager.get_session()
        try:
            # Get invoices from current month
            now = datetime.now()
            first_day = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            invoices = InvoiceRepository.get_by_date_range(session, first_day, now)
            
            if not invoices:
                await message.answer("❌ Chưa có dữ liệu trong tháng này.")
                return
            
            # Generate statistics
            summary = StatisticsExporter.generate_monthly_summary(invoices)
            
            stats_text = f"""
📊 <b>THỐNG KÊ THÁNG {now.month}/{now.year}</b>

📈 <b>Tổng quan:</b>
• Số lượng HĐ: {summary['total_invoices']}
• Tổng giá trị: {summary['total_amount']:,.0f} VNĐ
• Trung bình: {summary['average_amount']:,.0f} VNĐ/HĐ

💼 <b>Theo danh mục:</b>
"""
            
            for category, amount in list(summary['by_category'].items())[:5]:
                stats_text += f"• {category}: {amount:,.0f} VNĐ\n"
            
            stats_text += f"\n📂 <b>Theo tài khoản:</b>\n"
            for account, amount in list(summary['by_account'].items())[:5]:
                stats_text += f"• TK {account}: {amount:,.0f} VNĐ\n"
            
            await message.answer(stats_text, parse_mode=ParseMode.HTML)
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error in stats command: {e}")
        await message.answer("❌ Có lỗi xảy ra khi tính thống kê.")

@router.message(Command("excel"))
async def cmd_excel(message: Message):
    """Xuất dữ liệu ra Excel"""
    try:
        await message.answer("📊 Đang tạo file Excel...")
        
        session = db_manager.get_session()
        try:
            invoices = InvoiceRepository.get_by_user(session, message.from_user.id, limit=1000)
            
            if not invoices:
                await message.answer("❌ Chưa có dữ liệu để xuất.")
                return
            
            # Export to Excel
            excel_path = ExcelExporter.export_invoices(invoices)
            
            # Send file
            file = FSInputFile(excel_path)
            await message.answer_document(
                document=file,
                caption=f"✅ Đã xuất {len(invoices)} hóa đơn ra Excel!"
            )
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error in excel command: {e}")
        await message.answer("❌ Có lỗi xảy ra khi xuất Excel.")

@router.message(Command("word"))
async def cmd_word(message: Message):
    """Xuất báo cáo Word"""
    try:
        await message.answer("📝 Đang tạo file Word...")
        
        session = db_manager.get_session()
        try:
            invoices = InvoiceRepository.get_by_user(session, message.from_user.id, limit=1000)
            
            if not invoices:
                await message.answer("❌ Chưa có dữ liệu để xuất.")
                return
            
            # Export to Word
            word_path = WordExporter.export_invoice_report(invoices)
            
            # Send file
            file = FSInputFile(word_path)
            await message.answer_document(
                document=file,
                caption=f"✅ Đã tạo báo cáo Word với {len(invoices)} hóa đơn!"
            )
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error in word command: {e}")
        await message.answer("❌ Có lỗi xảy ra khi xuất Word.")

@router.message(Command("recent"))
async def cmd_recent(message: Message):
    """Hiển thị hóa đơn gần đây"""
    try:
        session = db_manager.get_session()
        try:
            invoices = InvoiceRepository.get_by_user(session, message.from_user.id, limit=10)
            
            if not invoices:
                await message.answer("❌ Chưa có hóa đơn nào.")
                return
            
            result_text = "<b>🕐 10 hóa đơn gần nhất:</b>\n\n"
            
            for inv in invoices:
                result_text += f"""
📄 <b>{inv.invoice_number}</b>
📅 {inv.invoice_date.strftime('%d/%m/%Y')}
🏢 {inv.supplier_name}
💰 {inv.total_amount:,.0f} VNĐ
{'—' * 25}
"""
            
            await message.answer(result_text, parse_mode=ParseMode.HTML)
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error in recent command: {e}")
        await message.answer("❌ Có lỗi xảy ra.")
