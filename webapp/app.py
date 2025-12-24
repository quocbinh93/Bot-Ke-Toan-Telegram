"""
Web Admin Panel for Telegram Accounting Bot
Quản lý users, roles, và invoices qua giao diện web
"""

from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database import init_db, UserRepository, InvoiceRepository, db_manager
from src.database.models import User, Invoice

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'  # Change this!

# Initialize database
init_db()

# Simple authentication - Admin password
ADMIN_PASSWORD = "admin123"  # Change this in production!


def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Vui lòng đăng nhập trước', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['logged_in'] = True
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Mật khẩu không đúng!', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    """Logout"""
    session.pop('logged_in', None)
    flash('Đã đăng xuất', 'info')
    return redirect(url_for('login'))


@app.route('/')
@login_required
def dashboard():
    """Dashboard with statistics"""
    session = db_manager.get_session()
    try:
        # Get statistics
        total_users = UserRepository.count_all(session)
        total_invoices = InvoiceRepository.count_all(session)
        pending_count = InvoiceRepository.count_by_status(session, 'pending')
        approved_count = InvoiceRepository.count_by_status(session, 'approved')
        rejected_count = InvoiceRepository.count_by_status(session, 'rejected')
        
        # Get total amounts
        total_amount = InvoiceRepository.get_total_amount(session) or 0
        approved_amount = InvoiceRepository.get_total_amount_by_status(session, 'approved') or 0
        pending_amount = InvoiceRepository.get_total_amount_by_status(session, 'pending') or 0
        
        # Get recent invoices
        recent_invoices = InvoiceRepository.get_recent(session, 10)
        
        # Get user role statistics
        users = UserRepository.get_all(session)
        role_stats = {
            'admin': sum(1 for u in users if u.role == 'admin'),
            'accountant': sum(1 for u in users if u.role == 'accountant'),
            'user': sum(1 for u in users if u.role == 'user')
        }
        
        return render_template('dashboard.html',
                             total_users=total_users,
                             total_invoices=total_invoices,
                             pending_count=pending_count,
                             approved_count=approved_count,
                             rejected_count=rejected_count,
                             total_amount=total_amount,
                             approved_amount=approved_amount,
                             pending_amount=pending_amount,
                             recent_invoices=recent_invoices,
                             role_stats=role_stats)
    finally:
        session.close()


@app.route('/users')
@login_required
def users():
    """User management page"""
    session = db_manager.get_session()
    try:
        all_users = UserRepository.get_all(session)
        return render_template('users.html', users=all_users)
    finally:
        session.close()


@app.route('/users/add', methods=['POST'])
@login_required
def add_user():
    """Add new user manually"""
    session = db_manager.get_session()
    try:
        telegram_user_id = int(request.form.get('telegram_user_id'))
        username = request.form.get('username', '').strip()
        full_name = request.form.get('full_name', '').strip()
        role = request.form.get('role', 'user')
        
        # Validate
        if not telegram_user_id:
            return jsonify({'success': False, 'message': 'Telegram ID là bắt buộc'}), 400
        
        # Check if user already exists
        existing = session.query(User).filter(
            User.telegram_user_id == telegram_user_id
        ).first()
        
        if existing:
            return jsonify({'success': False, 'message': f'User {telegram_user_id} đã tồn tại!'}), 400
        
        # Create new user
        new_user = User(
            telegram_user_id=telegram_user_id,
            username=username if username else f'user_{telegram_user_id}',
            first_name=full_name.split()[0] if full_name else 'New',
            last_name=' '.join(full_name.split()[1:]) if full_name and len(full_name.split()) > 1 else 'User',
            role=role,
            department=None,
            is_active=True,
            created_at=datetime.now(),
            last_activity=datetime.now(),
            total_invoices_submitted=0,
            total_invoices_approved=0
        )
        
        session.add(new_user)
        session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Đã tạo user thành công!',
            'user': {
                'telegram_user_id': new_user.telegram_user_id,
                'username': new_user.username,
                'full_name': f'{new_user.first_name} {new_user.last_name or ""}',
                'role': new_user.role
            }
        })
    except ValueError:
        return jsonify({'success': False, 'message': 'Telegram ID phải là số'}), 400
    except Exception as e:
        session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        session.close()


@app.route('/users/set_role/<int:telegram_user_id>', methods=['POST'])
@login_required
def set_role(telegram_user_id):
    """Set user role via AJAX"""
    new_role = request.form.get('role')
    if new_role not in ['user', 'accountant', 'admin']:
        return jsonify({'success': False, 'message': 'Role không hợp lệ'}), 400
    
    session = db_manager.get_session()
    try:
        UserRepository.update_role(session, telegram_user_id, new_role)
        return jsonify({'success': True, 'message': f'Đã cập nhật role thành {new_role}'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        session.close()


@app.route('/invoices')
@app.route('/invoices/<status>')
@login_required
def invoices(status=None):
    """Invoice management page"""
    session = db_manager.get_session()
    try:
        if status:
            invoice_list = InvoiceRepository.get_by_status(session, status)
            page_title = f"Hóa đơn {status}"
        else:
            invoice_list = InvoiceRepository.get_all(session)
            page_title = "Tất cả hóa đơn"
        
        return render_template('invoices.html', 
                             invoices=invoice_list,
                             page_title=page_title,
                             current_status=status)
    finally:
        session.close()


@app.route('/invoices/approve/<int:invoice_id>', methods=['POST'])
@login_required
def approve_invoice(invoice_id):
    """Approve invoice"""
    session = db_manager.get_session()
    try:
        invoice = InvoiceRepository.get_by_id(session, invoice_id)
        if not invoice:
            return jsonify({'success': False, 'message': 'Không tìm thấy hóa đơn'}), 404
        
        invoice.status = 'approved'
        invoice.approved_by_username = 'web_admin'
        invoice.updated_at = datetime.now()
        session.commit()
        
        # Increment approved count for user
        UserRepository.increment_approved_count(session, invoice.telegram_user_id)
        
        return jsonify({'success': True, 'message': 'Đã duyệt hóa đơn'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        session.close()


@app.route('/invoices/reject/<int:invoice_id>', methods=['POST'])
@login_required
def reject_invoice(invoice_id):
    """Reject invoice"""
    session = db_manager.get_session()
    try:
        reason = request.form.get('reason', 'Không có lý do')
        invoice = InvoiceRepository.get_by_id(session, invoice_id)
        if not invoice:
            return jsonify({'success': False, 'message': 'Không tìm thấy hóa đơn'}), 404
        
        invoice.status = 'rejected'
        invoice.rejection_reason = reason
        invoice.updated_at = datetime.now()
        session.commit()
        
        return jsonify({'success': True, 'message': 'Đã từ chối hóa đơn'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        session.close()


@app.route('/invoices/view/<int:invoice_id>')
@login_required
def view_invoice(invoice_id):
    """View invoice details"""
    session = db_manager.get_session()
    try:
        invoice = InvoiceRepository.get_by_id(session, invoice_id)
        if not invoice:
            flash('Không tìm thấy hóa đơn', 'danger')
            return redirect(url_for('invoices'))
        
        return render_template('invoice_detail.html', invoice=invoice)
    finally:
        session.close()


@app.route('/api/stats')
@login_required
def api_stats():
    """API endpoint for statistics - for charts"""
    session = db_manager.get_session()
    try:
        # Get invoices by date (last 7 days)
        today = datetime.now()
        daily_stats = []
        
        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            
            # Count invoices for this date
            invoices_on_date = [inv for inv in InvoiceRepository.get_all(session) 
                               if inv.created_at.strftime('%Y-%m-%d') == date_str]
            
            daily_stats.append({
                'date': date.strftime('%d/%m'),
                'count': len(invoices_on_date),
                'amount': sum(inv.total_amount or 0 for inv in invoices_on_date)
            })
        
        return jsonify(daily_stats)
    finally:
        session.close()


# Template filters
@app.template_filter('currency')
def currency_filter(value):
    """Format currency"""
    if value is None:
        return '0 ₫'
    return f"{value:,.0f} ₫".replace(',', '.')


@app.template_filter('datetime')
def datetime_filter(value):
    """Format datetime"""
    if value is None:
        return ''
    return value.strftime('%d/%m/%Y %H:%M')


@app.template_filter('date')
def date_filter(value):
    """Format date"""
    if value is None:
        return ''
    return value.strftime('%d/%m/%Y')


if __name__ == '__main__':
    print("=" * 50)
    print("🌐 WEB ADMIN PANEL")
    print("=" * 50)
    print(f"📍 URL: http://localhost:5000")
    print(f"🔑 Password: {ADMIN_PASSWORD}")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
