"""Admin commands cho Telegram Bot"""
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger
from datetime import datetime

from src.database import db_manager
from src.database.repository import InvoiceRepository, UserRepository

router = Router()
invoice_repo = InvoiceRepository()
user_repo = UserRepository()

class AdminStates(StatesGroup):
    """States cho admin workflow"""
    waiting_for_rejection_reason = State()
    waiting_for_user_role = State()

def is_admin(user_id: int) -> bool:
    """Kiểm tra user có phải admin không"""
    user = user_repo.get_by_telegram_id(user_id)
    return user and user.role in ['admin', 'accountant']

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Admin panel"""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Bạn không có quyền truy cập chức năng này!")
        return
    
    user = user_repo.get_by_telegram_id(message.from_user.id)
    
    # Thống kê
    pending_count = invoice_repo.count_by_status('pending')
    total_users = user_repo.count_all()
    
    text = f"""
🔐 <b>ADMIN PANEL</b>

👤 Xin chào {user.first_name or user.username}!
📊 Vai trò: <b>{user.role.upper()}</b>

📈 <b>Thống kê:</b>
• Hóa đơn chờ duyệt: {pending_count}
• Tổng số users: {total_users}

<b>Các lệnh có sẵn:</b>
/pending - Xem hóa đơn chờ duyệt
/users - Quản lý users
/stats_admin - Thống kê chi tiết
/set_role - Phân quyền user
"""
    await message.answer(text, parse_mode="HTML")

@router.message(Command("pending"))
async def cmd_pending(message: Message):
    """Xem hóa đơn chờ duyệt"""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Bạn không có quyền truy cập!")
        return
    
    pending_invoices = invoice_repo.get_by_status('pending', limit=10)
    
    if not pending_invoices:
        await message.answer("✅ Không có hóa đơn nào chờ duyệt!")
        return
    
    for invoice in pending_invoices:
        text = f"""
📄 <b>Hóa đơn #{invoice.id}</b>

🔢 Số HĐ: {invoice.invoice_number}
📅 Ngày: {invoice.invoice_date.strftime('%d/%m/%Y')}
🏢 Nhà CC: {invoice.supplier_name}
💰 Tổng tiền: <b>{invoice.total_amount:,.0f} VNĐ</b>
📝 Mô tả: {invoice.description[:100]}...
👤 Người tạo: @{invoice.created_by_username or 'N/A'}

📂 Danh mục: {invoice.category}
🏷️ Mã TK: {invoice.account_code}
"""
        # Inline keyboard cho approve/reject
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Duyệt", callback_data=f"approve_{invoice.id}"),
                InlineKeyboardButton(text="❌ Từ chối", callback_data=f"reject_{invoice.id}")
            ],
            [InlineKeyboardButton(text="👁️ Xem ảnh", callback_data=f"view_{invoice.id}")]
        ])
        
        await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

@router.callback_query(F.data.startswith("approve_"))
async def callback_approve(callback: CallbackQuery):
    """Duyệt hóa đơn"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Bạn không có quyền!", show_alert=True)
        return
    
    invoice_id = int(callback.data.split("_")[1])
    user = user_repo.get_by_telegram_id(callback.from_user.id)
    
    # Cập nhật status
    invoice = invoice_repo.get_by_id(invoice_id)
    if invoice:
        invoice_repo.update(invoice_id, {
            'status': 'approved',
            'approved_by': str(callback.from_user.id),
            'approved_by_username': callback.from_user.username,
            'approved_at': datetime.now()
        })
        
        # Update user stats
        user_repo.increment_approved_count(callback.from_user.id)
        
        await callback.message.edit_text(
            f"✅ <b>ĐÃ DUYỆT</b>\n\n{callback.message.text}\n\n"
            f"👤 Người duyệt: @{callback.from_user.username}\n"
            f"⏰ Thời gian: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            parse_mode="HTML"
        )
        
        # Gửi notification cho user tạo hóa đơn
        try:
            await callback.bot.send_message(
                invoice.created_by_user_id,
                f"✅ Hóa đơn #{invoice.invoice_number} của bạn đã được duyệt!\n"
                f"👤 Người duyệt: @{callback.from_user.username}"
            )
        except:
            pass
    
    await callback.answer("✅ Đã duyệt hóa đơn!")

@router.callback_query(F.data.startswith("reject_"))
async def callback_reject(callback: CallbackQuery, state: FSMContext):
    """Từ chối hóa đơn"""
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Bạn không có quyền!", show_alert=True)
        return
    
    invoice_id = int(callback.data.split("_")[1])
    
    await state.update_data(invoice_id=invoice_id)
    await state.set_state(AdminStates.waiting_for_rejection_reason)
    
    await callback.message.answer(
        "📝 Vui lòng nhập lý do từ chối hóa đơn này:",
        parse_mode="HTML"
    )
    await callback.answer()

@router.message(AdminStates.waiting_for_rejection_reason)
async def process_rejection(message: Message, state: FSMContext):
    """Xử lý lý do từ chối"""
    data = await state.get_data()
    invoice_id = data.get('invoice_id')
    reason = message.text
    
    invoice = invoice_repo.get_by_id(invoice_id)
    if invoice:
        invoice_repo.update(invoice_id, {
            'status': 'rejected',
            'approved_by': str(message.from_user.id),
            'approved_by_username': message.from_user.username,
            'approved_at': datetime.now(),
            'rejection_reason': reason
        })
        
        await message.answer(
            f"❌ Đã từ chối hóa đơn #{invoice.invoice_number}\n"
            f"📝 Lý do: {reason}",
            parse_mode="HTML"
        )
        
        # Notify user
        try:
            await message.bot.send_message(
                invoice.created_by_user_id,
                f"❌ Hóa đơn #{invoice.invoice_number} đã bị từ chối\n\n"
                f"📝 Lý do: {reason}\n"
                f"👤 Người từ chối: @{message.from_user.username}"
            )
        except:
            pass
    
    await state.clear()

@router.callback_query(F.data.startswith("view_"))
async def callback_view_image(callback: CallbackQuery):
    """Xem ảnh hóa đơn"""
    invoice_id = int(callback.data.split("_")[1])
    invoice = invoice_repo.get_by_id(invoice_id)
    
    if invoice and invoice.file_path:
        try:
            from aiogram.types import FSInputFile
            photo = FSInputFile(invoice.file_path)
            await callback.message.answer_photo(
                photo,
                caption=f"📄 Hóa đơn #{invoice.invoice_number}"
            )
        except Exception as e:
            await callback.answer(f"❌ Không thể tải ảnh: {e}", show_alert=True)
    else:
        await callback.answer("❌ Không tìm thấy file ảnh!", show_alert=True)

@router.message(Command("users"))
async def cmd_users(message: Message):
    """Danh sách users"""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Bạn không có quyền!")
        return
    
    users = user_repo.get_all()
    
    text = "<b>👥 DANH SÁCH USERS</b>\n\n"
    for user in users[:20]:  # Limit 20
        status = "✅" if user.is_active else "❌"
        role_icon = {"admin": "👑", "accountant": "📊", "user": "👤"}.get(user.role, "👤")
        text += f"{status} {role_icon} @{user.username or 'N/A'} - {user.role}\n"
        text += f"   📈 Đã gửi: {user.total_invoices_submitted} | Đã duyệt: {user.total_invoices_approved}\n\n"
    
    text += f"\n<i>Tổng: {len(users)} users</i>"
    await message.answer(text, parse_mode="HTML")

@router.message(Command("set_role"))
async def cmd_set_role(message: Message, state: FSMContext):
    """Phân quyền user"""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Bạn không có quyền!")
        return
    
    # Parse command: /set_role @username role
    parts = message.text.split()
    if len(parts) < 3:
        await message.answer(
            "📝 Cú pháp: /set_role @username role\n"
            "Roles: user, accountant, admin"
        )
        return
    
    username = parts[1].replace("@", "")
    new_role = parts[2].lower()
    
    if new_role not in ['user', 'accountant', 'admin']:
        await message.answer("❌ Role không hợp lệ! (user/accountant/admin)")
        return
    
    # Find user
    user = user_repo.get_by_username(username)
    if not user:
        await message.answer(f"❌ Không tìm thấy user @{username}")
        return
    
    # Update role
    user_repo.update_role(user.id, new_role)
    
    await message.answer(
        f"✅ Đã cập nhật role cho @{username}:\n"
        f"📊 Role mới: <b>{new_role}</b>",
        parse_mode="HTML"
    )

@router.message(Command("stats_admin"))
async def cmd_stats_admin(message: Message):
    """Thống kê chi tiết cho admin"""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Bạn không có quyền!")
        return
    
    # Lấy thống kê
    total_invoices = invoice_repo.count_all()
    pending = invoice_repo.count_by_status('pending')
    approved = invoice_repo.count_by_status('approved')
    rejected = invoice_repo.count_by_status('rejected')
    
    total_amount = invoice_repo.get_total_amount()
    approved_amount = invoice_repo.get_total_amount_by_status('approved')
    
    text = f"""
📊 <b>THỐNG KÊ TỔNG QUAN</b>

📄 <b>Hóa đơn:</b>
• Tổng số: {total_invoices}
• Chờ duyệt: {pending}
• Đã duyệt: {approved}
• Từ chối: {rejected}

💰 <b>Tài chính:</b>
• Tổng giá trị: {total_amount:,.0f} VNĐ
• Đã duyệt: {approved_amount:,.0f} VNĐ
• Chờ duyệt: {(total_amount - approved_amount):,.0f} VNĐ

📈 <b>Tỷ lệ duyệt:</b> {(approved/total_invoices*100 if total_invoices > 0 else 0):.1f}%
"""
    
    await message.answer(text, parse_mode="HTML")
