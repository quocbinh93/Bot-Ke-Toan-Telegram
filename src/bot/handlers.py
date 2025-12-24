import os
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from aiogram.enums import ParseMode
from pathlib import Path
from datetime import datetime, timedelta
from loguru import logger
import config

from src.ocr import ocr_processor
from src.processor import data_processor
from src.database import db_manager
from src.database.models import Invoice, User
from src.database.repository import InvoiceRepository, UserRepository
from src.exporter import ExcelExporter, WordExporter, StatisticsExporter

router = Router()

@router.message(F.photo)
async def handle_photo(message: Message):
    """Xử lý ảnh được gửi đến bot"""
    try:
        await message.answer("📸 Đang xử lý ảnh của bạn, vui lòng đợi...")
        
        # Get the largest photo
        photo = message.photo[-1]
        
        # Check file size
        file_size_mb = photo.file_size / (1024 * 1024)
        if file_size_mb > config.MAX_FILE_SIZE_MB:
            await message.answer(f"❌ File quá lớn! Kích thước tối đa: {config.MAX_FILE_SIZE_MB}MB")
            return
        
        # Download photo
        file = await message.bot.get_file(photo.file_id)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = config.DATA_DIR / f'invoice_{message.from_user.id}_{timestamp}.jpg'
        
        await message.bot.download_file(file.file_path, file_path)
        logger.info(f"Downloaded photo to {file_path}")
        
        # Process with OCR
        await message.answer("🔍 Đang đọc văn bản từ ảnh...")
        ocr_text = ocr_processor.process_file(str(file_path))
        
        if not ocr_text:
            await message.answer("❌ Không thể đọc được văn bản từ ảnh. Vui lòng thử lại với ảnh rõ hơn.")
            return
        
        # Extract structured data
        await message.answer("🤖 Đang phân tích thông tin hóa đơn...")
        invoice_data = data_processor.extract_invoice_data(ocr_text)
        
        if not invoice_data:
            await message.answer("❌ Không thể trích xuất thông tin hóa đơn. Vui lòng kiểm tra lại ảnh.")
            return
        
        # Save to database
        session = db_manager.get_session()
        try:
            # Create or update user
            user = UserRepository.create_or_update(
                session,
                telegram_user_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name
            )
            
            # Add invoice data
            invoice_data['created_by_user_id'] = message.from_user.id
            invoice_data['created_by_username'] = message.from_user.username
            invoice_data['file_path'] = str(file_path)
            invoice_data['raw_ocr_text'] = ocr_text
            
            invoice = InvoiceRepository.create(session, invoice_data)
            
            # Send confirmation
            result_text = f"""
✅ <b>Đã lưu hóa đơn thành công!</b>

<b>Thông tin:</b>
📄 Số HĐ: {invoice.invoice_number}
📅 Ngày: {invoice.invoice_date.strftime('%d/%m/%Y')}
🏢 NCC: {invoice.supplier_name}
💰 Tổng tiền: {invoice.total_amount:,.0f} VNĐ

📊 Tài khoản: {invoice.account_code}
📂 Danh mục: {invoice.category}

<i>Sử dụng /search {invoice.invoice_number} để xem chi tiết</i>
"""
            await message.answer(result_text, parse_mode=ParseMode.HTML)
            
        except Exception as e:
            logger.error(f"Error saving invoice: {e}")
            await message.answer("❌ Lỗi khi lưu dữ liệu. Vui lòng thử lại.")
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error handling photo: {e}")
        await message.answer("❌ Có lỗi xảy ra khi xử lý ảnh. Vui lòng thử lại.")

@router.message(F.document)
async def handle_document(message: Message):
    """Xử lý file document (PDF)"""
    try:
        document = message.document
        
        # Check if PDF
        if not document.file_name.lower().endswith('.pdf'):
            await message.answer("❌ Chỉ hỗ trợ file PDF. Vui lòng gửi file đúng định dạng.")
            return
        
        await message.answer("📄 Đang xử lý file PDF của bạn...")
        
        # Check file size
        file_size_mb = document.file_size / (1024 * 1024)
        if file_size_mb > config.MAX_FILE_SIZE_MB:
            await message.answer(f"❌ File quá lớn! Kích thước tối đa: {config.MAX_FILE_SIZE_MB}MB")
            return
        
        # Download PDF
        file = await message.bot.get_file(document.file_id)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = config.DATA_DIR / f'invoice_{message.from_user.id}_{timestamp}.pdf'
        
        await message.bot.download_file(file.file_path, file_path)
        logger.info(f"Downloaded PDF to {file_path}")
        
        # Process similar to photo
        await message.answer("🔍 Đang đọc văn bản từ PDF...")
        ocr_text = ocr_processor.process_file(str(file_path))
        
        if not ocr_text:
            await message.answer("❌ Không thể đọc được văn bản từ PDF.")
            return
        
        await message.answer("🤖 Đang phân tích thông tin hóa đơn...")
        invoice_data = data_processor.extract_invoice_data(ocr_text)
        
        if not invoice_data:
            await message.answer("❌ Không thể trích xuất thông tin hóa đơn.")
            return
        
        # Save to database (similar to photo handler)
        session = db_manager.get_session()
        try:
            user = UserRepository.create_or_update(
                session,
                telegram_user_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name
            )
            
            invoice_data['created_by_user_id'] = message.from_user.id
            invoice_data['created_by_username'] = message.from_user.username
            invoice_data['file_path'] = str(file_path)
            invoice_data['raw_ocr_text'] = ocr_text
            
            invoice = InvoiceRepository.create(session, invoice_data)
            
            result_text = f"""
✅ <b>Đã lưu hóa đơn từ PDF thành công!</b>

<b>Thông tin:</b>
📄 Số HĐ: {invoice.invoice_number}
📅 Ngày: {invoice.invoice_date.strftime('%d/%m/%Y')}
🏢 NCC: {invoice.supplier_name}
💰 Tổng tiền: {invoice.total_amount:,.0f} VNĐ
"""
            await message.answer(result_text, parse_mode=ParseMode.HTML)
            
        finally:
            session.close()
            
    except Exception as e:
        logger.error(f"Error handling document: {e}")
        await message.answer("❌ Có lỗi xảy ra khi xử lý file PDF.")
