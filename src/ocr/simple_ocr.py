"""
Simple OCR fallback khi không dùng EasyOCR
Sử dụng Tesseract hoặc API online
"""

from PIL import Image
from pathlib import Path
from typing import Optional
from loguru import logger

class SimpleOCRProcessor:
    """OCR processor đơn giản không cần EasyOCR"""
    
    def __init__(self):
        logger.warning("Using SimpleOCR fallback - OCR functionality limited")
        logger.info("For better OCR, install: pip install easyocr (requires Visual Studio Build Tools)")
    
    def extract_text_from_image(self, image_path: str) -> Optional[str]:
        """
        Placeholder - trả về hướng dẫn thay vì OCR thực
        
        Trong production, bạn có thể:
        1. Dùng Tesseract OCR
        2. Dùng API online (Google Vision, Azure OCR)
        3. Manual input từ user
        """
        logger.warning(f"OCR not available for: {image_path}")
        
        # Return placeholder text
        return """
        [OCR NOT AVAILABLE]
        
        Để sử dụng OCR tự động, cần:
        1. Cài Visual Studio Build Tools
        2. Chạy: pip install easyocr
        
        Hoặc bạn có thể:
        - Nhập thông tin thủ công
        - Dùng Google Vision API
        - Dùng Tesseract OCR
        """
    
    def extract_text_from_pdf(self, pdf_path: str) -> Optional[str]:
        """PDF processing placeholder"""
        logger.warning(f"PDF OCR not available for: {pdf_path}")
        return "[OCR NOT AVAILABLE - See extract_text_from_image]"
    
    def process_file(self, file_path: str) -> Optional[str]:
        """Process file placeholder"""
        path = Path(file_path)
        
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return None
        
        if path.suffix.lower() == '.pdf':
            return self.extract_text_from_pdf(file_path)
        else:
            return self.extract_text_from_image(file_path)

# Global instance
simple_ocr_processor = SimpleOCRProcessor()
