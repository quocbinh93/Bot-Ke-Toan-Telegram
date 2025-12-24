from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from loguru import logger

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handler cho lệnh /start"""
    welcome_text = """
🤖 <b>Chào mừng đến với Bot Kế Toán Telegram!</b>

Bot này giúp bạn tự động xử lý và quản lý hóa đơn, chứng từ kế toán.

<b>📋 Các lệnh có sẵn:</b>

/start - Hiển thị hướng dẫn này
/help - Trợ giúp chi tiết
/stats - Xem thống kê tổng hợp
/excel - Xuất dữ liệu ra Excel
/word - Xuất báo cáo Word
/search [từ khóa] - Tìm kiếm hóa đơn
/recent - Xem 10 hóa đơn gần nhất

<b>📸 Cách sử dụng:</b>

1️⃣ Gửi ảnh hoặc file PDF chứng từ vào đây
2️⃣ Bot sẽ tự động đọc và trích xuất thông tin
3️⃣ Dữ liệu được lưu vào cơ sở dữ liệu
4️⃣ Bạn có thể tra cứu và xuất báo cáo bất cứ lúc nào

<i>Hãy thử gửi một ảnh hóa đơn để bắt đầu!</i> ✨
"""
    await message.answer(welcome_text, parse_mode=ParseMode.HTML)
    logger.info(f"User {message.from_user.id} started the bot")

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handler cho lệnh /help"""
    help_text = """
<b>📖 HƯỚNG DẪN SỬ DỤNG BOT</b>

<b>📋 LỆNH CƠ BẢN:</b>
/start - Hiển thị hướng dẫn
/help - Trợ giúp chi tiết
/stats - Thống kê tổng hợp
/recent - 10 hóa đơn mới nhất

<b>🔍 TÌM KIẾM NÂNG CAO:</b>
/search [từ khóa] - Tìm theo tên/số HĐ
/search_date DD/MM/YYYY DD/MM/YYYY - Theo ngày
/search_amount min max - Theo giá trị
/search_supplier [tên] - Theo nhà cung cấp
/search_category [danh mục] - Theo danh mục
/search_status [pending/approved/rejected] - Theo trạng thái

<b>📊 XUẤT FILE:</b>
/excel - Xuất Excel
/word - Xuất báo cáo Word

<b>🔐 ADMIN (Chỉ Admin/Accountant):</b>
/admin - Admin panel
/pending - Xem hóa đơn chờ duyệt
/users - Quản lý users
/set_role @username role - Phân quyền
/stats_admin - Thống kê chi tiết

<b>💡 CÁCH SỬ DỤNG:</b>
1️⃣ Gửi ảnh/PDF hóa đơn
2️⃣ Bot tự động OCR và trích xuất
3️⃣ Hóa đơn chờ admin duyệt
4️⃣ Tra cứu và xuất báo cáo

<b>⚠️ LƯU Ý:</b>
• Ảnh rõ ràng, không bị mờ
• Hỗ trợ tiếng Việt + Anh
• File tối đa: 20MB
"""
    await message.answer(help_text, parse_mode=ParseMode.HTML)
