import json
import re
from datetime import datetime
from typing import Optional, Dict
from loguru import logger
import config

class DataProcessor:
    """Xử lý và cấu trúc hóa dữ liệu từ OCR text"""
    
    def __init__(self):
        """Khởi tạo processor với AI provider"""
        self.ai_provider = config.AI_PROVIDER
        
        if self.ai_provider == 'gemini':
            import google.generativeai as genai
            genai.configure(api_key=config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            logger.info("Initialized Gemini AI processor")
        elif self.ai_provider == 'openai':
            from openai import OpenAI
            self.client = OpenAI(api_key=config.OPENAI_API_KEY)
            logger.info("Initialized OpenAI processor")
    
    def extract_invoice_data(self, ocr_text: str) -> Optional[Dict]:
        """
        Trích xuất thông tin hóa đơn từ OCR text sử dụng AI
        
        Args:
            ocr_text: Text từ OCR
            
        Returns:
            Dictionary chứa thông tin hóa đơn hoặc None nếu có lỗi
        """
        try:
            prompt = self._create_extraction_prompt(ocr_text)
            
            if self.ai_provider == 'gemini':
                response = self.model.generate_content(prompt)
                result_text = response.text
            elif self.ai_provider == 'openai':
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Bạn là một chuyên gia kế toán, nhiệm vụ của bạn là trích xuất thông tin từ hóa đơn."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1
                )
                result_text = response.choices[0].message.content
            
            # Parse JSON từ response
            invoice_data = self._parse_ai_response(result_text)
            
            # Validate và làm sạch dữ liệu
            invoice_data = self._validate_and_clean(invoice_data)
            
            logger.info(f"Extracted invoice data: {invoice_data.get('invoice_number', 'N/A')}")
            return invoice_data
            
        except Exception as e:
            logger.error(f"Error extracting invoice data: {e}")
            return None
    
    def _create_extraction_prompt(self, ocr_text: str) -> str:
        """Tạo prompt cho AI"""
        return f"""
Hãy phân tích văn bản hóa đơn sau và trích xuất thông tin theo định dạng JSON.

Văn bản OCR:
{ocr_text}

Hãy trích xuất các thông tin sau (nếu không tìm thấy thì để null):
1. invoice_number: Số hóa đơn
2. invoice_date: Ngày hóa đơn (định dạng YYYY-MM-DD)
3. supplier_name: Tên nhà cung cấp/người bán
4. supplier_tax_code: Mã số thuế
5. supplier_address: Địa chỉ
6. subtotal: Tiền trước thuế (số)
7. tax_rate: Thuế suất % (số)
8. tax_amount: Tiền thuế (số)
9. total_amount: Tổng tiền (số)
10. description: Mô tả/nội dung hóa đơn
11. items: Danh sách sản phẩm/dịch vụ (nếu có)

Trả về CHÍNH XÁC theo định dạng JSON sau (không thêm text nào khác):
{{
    "invoice_number": "...",
    "invoice_date": "YYYY-MM-DD",
    "supplier_name": "...",
    "supplier_tax_code": "...",
    "supplier_address": "...",
    "subtotal": 0.0,
    "tax_rate": 10.0,
    "tax_amount": 0.0,
    "total_amount": 0.0,
    "description": "...",
    "items": "..."
}}
"""
    
    def _parse_ai_response(self, response_text: str) -> Dict:
        """Parse JSON từ AI response"""
        try:
            # Tìm JSON block trong response
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                json_str = json_match.group(0)
                return json.loads(json_str)
            else:
                logger.warning("No JSON found in AI response")
                return {}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            return {}
    
    def _validate_and_clean(self, data: Dict) -> Dict:
        """Validate và làm sạch dữ liệu"""
        cleaned = {}
        
        # Invoice number
        invoice_num = data.get('invoice_number')
        # Kiểm tra nếu là None, "None", null, hoặc chuỗi rỗng
        if not invoice_num or str(invoice_num).strip().lower() in ['none', 'null', '']:
            cleaned['invoice_number'] = self._generate_invoice_number()
        else:
            cleaned['invoice_number'] = str(invoice_num).strip()
        
        # Invoice date
        date_str = data.get('invoice_date')
        if date_str:
            try:
                cleaned['invoice_date'] = datetime.strptime(str(date_str), '%Y-%m-%d')
            except:
                cleaned['invoice_date'] = datetime.now()
        else:
            cleaned['invoice_date'] = datetime.now()
        
        # Supplier info
        cleaned['supplier_name'] = str(data.get('supplier_name', 'N/A')).strip()
        cleaned['supplier_tax_code'] = str(data.get('supplier_tax_code', '')).strip()
        cleaned['supplier_address'] = str(data.get('supplier_address', '')).strip()
        
        # Financial data
        cleaned['subtotal'] = self._parse_amount(data.get('subtotal', 0))
        cleaned['tax_rate'] = self._parse_amount(data.get('tax_rate', 10))
        cleaned['tax_amount'] = self._parse_amount(data.get('tax_amount', 0))
        cleaned['total_amount'] = self._parse_amount(data.get('total_amount', 0))
        
        # Calculate missing values
        if cleaned['total_amount'] > 0 and cleaned['subtotal'] == 0:
            cleaned['subtotal'] = cleaned['total_amount'] / (1 + cleaned['tax_rate'] / 100)
            cleaned['tax_amount'] = cleaned['total_amount'] - cleaned['subtotal']
        elif cleaned['subtotal'] > 0 and cleaned['total_amount'] == 0:
            cleaned['tax_amount'] = cleaned['subtotal'] * cleaned['tax_rate'] / 100
            cleaned['total_amount'] = cleaned['subtotal'] + cleaned['tax_amount']
        
        # Description and items
        cleaned['description'] = str(data.get('description', '')).strip()
        cleaned['items'] = str(data.get('items', '')).strip()
        
        # Auto-classify account
        cleaned['account_code'] = self._classify_account(cleaned['description'])
        cleaned['category'] = self._classify_category(cleaned['description'])
        
        return cleaned
    
    def _parse_amount(self, value) -> float:
        """Parse số tiền từ string hoặc number"""
        try:
            if isinstance(value, (int, float)):
                return float(value)
            
            # Remove common separators
            value_str = str(value).replace(',', '').replace('.', '').replace(' ', '')
            return float(value_str) if value_str else 0.0
        except:
            return 0.0
    
    def _generate_invoice_number(self) -> str:
        """Tạo số hóa đơn tự động"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"INV-{timestamp}"
    
    def _classify_account(self, description: str) -> str:
        """Phân loại tài khoản kế toán dựa trên mô tả"""
        desc_lower = description.lower()
        
        # Danh mục tài khoản kế toán phổ biến
        if any(word in desc_lower for word in ['điện', 'nước', 'internet', 'điện thoại', 'viễn thông']):
            return '642'  # Chi phí quản lý doanh nghiệp
        elif any(word in desc_lower for word in ['văn phòng phẩm', 'giấy', 'bút', 'mực in']):
            return '642'
        elif any(word in desc_lower for word in ['lương', 'thưởng', 'nhân viên']):
            return '334'  # Phải trả người lao động
        elif any(word in desc_lower for word in ['thuê', 'mặt bằng', 'văn phòng']):
            return '642'
        elif any(word in desc_lower for word in ['marketing', 'quảng cáo', 'pr']):
            return '641'  # Chi phí bán hàng
        else:
            return '642'  # Default
    
    def _classify_category(self, description: str) -> str:
        """Phân loại danh mục chi phí"""
        desc_lower = description.lower()
        
        # 1. Chi Phí Nhân Sự
        if any(word in desc_lower for word in ['lương', 'thưởng', 'nhân viên', 'nhân sự', 'tiền công', 'công lương']):
            return 'Chi Phí Nhân Sự'
        
        # 2. Chi Phí Tiện Ích
        elif any(word in desc_lower for word in ['điện', 'nước', 'điện nước']):
            return 'Chi Phí Tiện Ích - Điện Nước'
        
        # 3. Chi Phí Viễn Thông
        elif any(word in desc_lower for word in ['internet', 'điện thoại', 'viễn thông', 'di động', 'cước phí', 'wifi', 'mạng']):
            return 'Chi Phí Viễn Thông'
        
        # 4. Chi Phí Văn Phòng Phẩm
        elif any(word in desc_lower for word in ['văn phòng phẩm', 'giấy', 'bút', 'mực in', 'bìa', 'kẹp', 'ghim', 'bấm']):
            return 'Chi Phí Văn Phòng Phẩm'
        
        # 5. Chi Phí Thuê Mặt Bằng
        elif any(word in desc_lower for word in ['thuê', 'mặt bằng', 'văn phòng', 'nhà xưởng', 'kho', 'cho thuê']):
            return 'Chi Phí Thuê Mặt Bằng'
        
        # 6. Chi Phí Marketing & Quảng Cáo
        elif any(word in desc_lower for word in ['marketing', 'quảng cáo', 'pr', 'truyền thông', 'facebook ads', 'google ads', 'banner', 'poster']):
            return 'Chi Phí Marketing & Quảng Cáo'
        
        # 7. Chi Phí Đào Tạo
        elif any(word in desc_lower for word in ['đào tạo', 'khóa học', 'training', 'hội thảo', 'seminar', 'workshop']):
            return 'Chi Phí Đào Tạo'
        
        # 8. Chi Phí Vận Chuyển
        elif any(word in desc_lower for word in ['vận chuyển', 'giao hàng', 'ship', 'xe tải', 'chuyển hàng', 'logistics', 'cước phí vận chuyển']):
            return 'Chi Phí Vận Chuyển'
        
        # 9. Chi Phí Xăng Xe & Đi Lại
        elif any(word in desc_lower for word in ['xăng', 'dầu', 'nhiên liệu', 'bảo dưỡng xe', 'sửa xe', 'taxi', 'grab', 'đi lại', 'công tác phí']):
            return 'Chi Phí Xăng Xe & Đi Lại'
        
        # 10. Chi Phí Bảo Hiểm
        elif any(word in desc_lower for word in ['bảo hiểm', 'bhxh', 'bhyt', 'bhtn', 'insurance']):
            return 'Chi Phí Bảo Hiểm'
        
        # 11. Chi Phí Thuế & Phí
        elif any(word in desc_lower for word in ['thuế', 'phí', 'lệ phí', 'tax', 'môn bài']):
            return 'Chi Phí Thuế & Phí'
        
        # 12. Chi Phí Sửa Chữa & Bảo Trì
        elif any(word in desc_lower for word in ['sửa chữa', 'bảo trì', 'bảo dưỡng', 'maintenance', 'repair']):
            return 'Chi Phí Sửa Chữa & Bảo Trì'
        
        # 13. Chi Phí Khấu Hao
        elif any(word in desc_lower for word in ['khấu hao', 'depreciation', 'phân bổ']):
            return 'Chi Phí Khấu Hao'
        
        # 14. Chi Phí Nguyên Vật Liệu
        elif any(word in desc_lower for word in ['nguyên liệu', 'vật liệu', 'nguyên vật liệu', 'nvl', 'materials', 'raw material']):
            return 'Chi Phí Nguyên Vật Liệu'
        
        # 15. Chi Phí Ăn Uống & Tiếp Khách
        elif any(word in desc_lower for word in ['ăn uống', 'tiếp khách', 'cafe', 'cà phê', 'nhà hàng', 'buffet', 'tiệc', 'đãi']):
            return 'Chi Phí Ăn Uống & Tiếp Khách'
        
        # 16. Chi Phí In Ấn
        elif any(word in desc_lower for word in ['in ấn', 'photocopy', 'photo', 'scan', 'printing', 'catalogue', 'brochure', 'name card']):
            return 'Chi Phí In Ấn'
        
        # 17. Chi Phí Phần Mềm & Công Nghệ
        elif any(word in desc_lower for word in ['phần mềm', 'software', 'license', 'bản quyền', 'hosting', 'domain', 'cloud', 'saas']):
            return 'Chi Phí Phần Mềm & Công Nghệ'
        
        # 18. Chi Phí Tài Chính
        elif any(word in desc_lower for word in ['lãi vay', 'lãi suất', 'ngân hàng', 'chuyển khoản', 'phí bank', 'interest']):
            return 'Chi Phí Tài Chính'
        
        # 19. Chi Phí Đồ Dùng & Thiết Bị
        elif any(word in desc_lower for word in ['thiết bị', 'máy móc', 'dụng cụ', 'đồ dùng', 'equipment', 'tools']):
            return 'Chi Phí Đồ Dùng & Thiết Bị'
        
        # 20. Chi Phí Y Tế & An Toàn
        elif any(word in desc_lower for word in ['y tế', 'khám sức khỏe', 'thuốc', 'khẩu trang', 'bảo hộ lao động', 'atsk', 'an toàn']):
            return 'Chi Phí Y Tế & An Toàn'
        
        # 21. Chi Phí Quà Tặng & Phúc Lợi
        elif any(word in desc_lower for word in ['quà', 'tặng', 'phúc lợi', 'sinh nhật', 'lễ tết', 'kỷ niệm', 'welfare']):
            return 'Chi Phí Quà Tặng & Phúc Lợi'
        
        # 22. Chi Phí Dịch Vụ Chuyên Nghiệp
        elif any(word in desc_lower for word in ['tư vấn', 'luật sư', 'kế toán', 'kiểm toán', 'audit', 'consulting', 'dịch vụ']):
            return 'Chi Phí Dịch Vụ Chuyên Nghiệp'
        
        # Default
        else:
            return 'Chi Phí Khác'

# Global processor instance
data_processor = DataProcessor()
