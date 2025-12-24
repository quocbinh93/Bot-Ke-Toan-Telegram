from pathlib import Path
from typing import Optional
from loguru import logger
import config

# Try to import EasyOCR, fallback to simple OCR if not available
try:
    import easyocr
    from PIL import Image
    import numpy as np
    EASYOCR_AVAILABLE = True
    logger.info("EasyOCR is available")
except ImportError:
    EASYOCR_AVAILABLE = False
    logger.warning("EasyOCR not available, using fallback mode")
    from PIL import Image

class OCRProcessor:
    """Xử lý OCR cho hình ảnh - hỗ trợ EasyOCR hoặc fallback"""
    
    def __init__(self):
        """Khởi tạo OCR reader"""
        if EASYOCR_AVAILABLE:
            logger.info(f"Initializing EasyOCR with languages: {config.OCR_LANGUAGES}")
            self.reader = easyocr.Reader(config.OCR_LANGUAGES, gpu=False)
            logger.info("EasyOCR initialized successfully")
            self.mode = "easyocr"
        else:
            logger.warning("EasyOCR not available - using fallback mode")
            logger.info("Bot will work but OCR will be limited")
            logger.info("To enable OCR: Install Visual Studio Build Tools, then: pip install easyocr")
            self.reader = None
            self.mode = "fallback"
    
    def extract_text_from_image(self, image_path: str) -> Optional[str]:
        """
        Trích xuất text từ hình ảnh
        
        Args:
            image_path: Đường dẫn đến file ảnh
            
        Returns:
            Text được trích xuất hoặc None nếu có lỗi
        """
        try:
            logger.info(f"Processing image: {image_path}")
            
            if self.mode == "easyocr" and self.reader:
                # Đọc ảnh
                image = Image.open(image_path)
                
                # Chuyển đổi sang RGB nếu cần
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Chuyển đổi sang numpy array
                image_array = np.array(image)
                
                # Thực hiện OCR
                results = self.reader.readtext(image_array)
                
                # Kết hợp text từ tất cả các detections
                extracted_text = '\n'.join([text[1] for text in results])
                
                logger.info(f"Extracted {len(results)} text blocks")
                logger.debug(f"Extracted text preview: {extracted_text[:200]}")
                
                return extracted_text
            else:
                # Fallback mode - return instruction
                logger.warning("OCR not available - returning placeholder")
                return """
                [OCR KHÔNG KHẢ DỤNG]
                
                Ảnh đã được nhận nhưng không thể đọc tự động.
                Vui lòng nhập thông tin hóa đơn thủ công hoặc:
                
                1. Cài Visual Studio Build Tools
                2. Chạy: pip install easyocr
                3. Khởi động lại bot
                """
                
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return None
    
    def extract_text_from_pdf(self, pdf_path: str) -> Optional[str]:
        """
        Trích xuất text từ PDF
        
        Args:
            pdf_path: Đường dẫn đến file PDF
            
        Returns:
            Text được trích xuất hoặc None nếu có lỗi
        """
        try:
            from pdf2image import convert_from_path
            
            logger.info(f"Converting PDF to images: {pdf_path}")
            
            # Convert PDF sang images
            images = convert_from_path(pdf_path)
            
            all_text = []
            for i, image in enumerate(images):
                logger.info(f"Processing page {i + 1}/{len(images)}")
                
                # Convert PIL Image to numpy array
                image_array = np.array(image)
                
                # Thực hiện OCR
                results = self.reader.readtext(image_array)
                page_text = '\n'.join([text[1] for text in results])
                all_text.append(page_text)
            
            extracted_text = '\n\n--- PAGE BREAK ---\n\n'.join(all_text)
            logger.info(f"Extracted text from {len(images)} pages")
            
            return extracted_text
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return None
    
    def process_file(self, file_path: str) -> Optional[str]:
        """
        Xử lý file (tự động detect PDF hoặc image)
        
        Args:
            file_path: Đường dẫn đến file
            
        Returns:
            Text được trích xuất hoặc None nếu có lỗi
        """
        path = Path(file_path)
        
        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return None
        
        # Check file extension
        if path.suffix.lower() == '.pdf':
            return self.extract_text_from_pdf(file_path)
        elif path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']:
            return self.extract_text_from_image(file_path)
        else:
            logger.error(f"Unsupported file format: {path.suffix}")
            return None

# Global OCR instance
ocr_processor = OCRProcessor()
