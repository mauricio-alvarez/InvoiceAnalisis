"""PDF text extraction using pdfminer.six"""
import logging
from io import StringIO, BytesIO
from typing import Dict, Optional

from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter

logger = logging.getLogger(__name__)


class PDFMinerExtractor:
    """Service for extracting text from PDF using pdfminer.six"""
    
    def __init__(self):
        """Initialize PDFMiner extractor"""
        self.laparams = LAParams()
        logger.info("PDFMiner extractor initialized")
    
    def extract_text_by_page(self, pdf_content: bytes) -> Dict[str, str]:
        """
        Extract text from PDF, page by page
        
        Args:
            pdf_content: PDF file content as bytes
            
        Returns:
            Dictionary with page numbers as keys and extracted text as values
            
        Raises:
            Exception: If extraction fails
        """
        output = {}
        
        try:
            pdf_file = BytesIO(pdf_content)
            resource_manager = PDFResourceManager()
            
            for page_number, page in enumerate(PDFPage.get_pages(pdf_file), start=1):
                output_string = StringIO()
                device = TextConverter(
                    resource_manager, 
                    output_string, 
                    laparams=self.laparams
                )
                interpreter = PDFPageInterpreter(resource_manager, device)
                
                try:
                    interpreter.process_page(page)
                    raw_text = output_string.getvalue()
                    
                    # Clean the text
                    cleaned_text = raw_text.replace('\n', ' ').replace('\r', '').strip()
                    cleaned_text = ' '.join(cleaned_text.split())  # Remove extra whitespace
                    
                    output[f"Page {page_number}"] = cleaned_text
                    
                    logger.debug(f"Extracted {len(cleaned_text)} characters from page {page_number}")
                    
                except Exception as e:
                    logger.warning(f"Failed to process page {page_number}: {e}")
                    output[f"Page {page_number}"] = ""
                
                finally:
                    device.close()
                    output_string.close()
            
            total_chars = sum(len(text) for text in output.values())
            logger.info(f"Extracted text from {len(output)} pages, total {total_chars} characters")
            
            return output
            
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            raise
    
    def extract_text_combined(self, pdf_content: bytes) -> str:
        """
        Extract all text from PDF as a single string
        
        Args:
            pdf_content: PDF file content as bytes
            
        Returns:
            Combined text from all pages
            
        Raises:
            Exception: If extraction fails
        """
        try:
            pages = self.extract_text_by_page(pdf_content)
            
            # Combine all pages with page separators
            combined_text = "\n\n".join([
                f"--- {page_key} ---\n{text}"
                for page_key, text in pages.items()
                if text.strip()
            ])
            
            logger.info(f"Combined text: {len(combined_text)} characters")
            
            return combined_text
            
        except Exception as e:
            logger.error(f"Failed to extract combined text: {e}")
            raise
    
    def extract_text_simple(self, pdf_content: bytes) -> str:
        """
        Extract text using pdfminer's high-level API (simpler, faster)
        
        Args:
            pdf_content: PDF file content as bytes
            
        Returns:
            Extracted text
            
        Raises:
            Exception: If extraction fails
        """
        try:
            pdf_file = BytesIO(pdf_content)
            output_string = StringIO()
            
            extract_text_to_fp(
                pdf_file, 
                output_string, 
                laparams=self.laparams
            )
            
            text = output_string.getvalue()
            output_string.close()
            
            # Clean the text
            cleaned_text = ' '.join(text.split())
            
            logger.info(f"Extracted {len(cleaned_text)} characters using simple method")
            
            return cleaned_text
            
        except Exception as e:
            logger.error(f"Failed to extract text with simple method: {e}")
            raise
