import os
from app.logging.logger import app_logger

class OCRService:
    def __init__(self):
        # In a real enterprise app, we'd initialize PaddleOCR here.
        # It's a heavy library, so we load it only when needed or use an API.
        self.ocr = None

    def initialize(self):
        try:
            from paddleocr import PaddleOCR
            self.ocr = PaddleOCR(use_angle_cls=True, lang='ar')
            app_logger.info("PaddleOCR initialized successfully.")
        except ImportError:
            app_logger.error("PaddleOCR not installed. OCR features will be disabled.")
        except Exception as e:
            app_logger.error(f"OCR Initialization error: {e}")

    def extract_text_from_pdf(self, pdf_path: str) -> list:
        if not self.ocr:
            self.initialize()

        if not self.ocr:
            return []

        try:
            # Simplified workflow for Enterprise ERP
            result = self.ocr.ocr(pdf_path, cls=True)
            extracted_items = []
            for line in result:
                for word_info in line:
                    # In a real ERP, we'd use regex/LLM to parse the data into structured items
                    extracted_items.append(word_info[1][0])
            return extracted_items
        except Exception as e:
            app_logger.error(f"OCR Extraction error: {e}")
            return []
