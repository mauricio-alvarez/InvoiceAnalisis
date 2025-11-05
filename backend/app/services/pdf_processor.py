"""PDF processing service for invoice data extraction"""
import logging
import re
from typing import Optional, List, Dict, Any
from datetime import datetime
import io

import pdfplumber

from app.models.invoice import LineItem
from app.services.document_ai_processor import DocumentAIProcessor
from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Spanish month names mapping
SPANISH_MONTHS = {
    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
    'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
    'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
}


class PDFProcessor:
    """Service for extracting invoice data from PDF files"""
    
    def __init__(self, ocr_mode: Optional[str] = None):
        """
        Initialize PDF processor with OCR mode
        
        Args:
            ocr_mode: OCR engine mode - "document_ai", "tesseract", or "auto"
                     If None, uses value from settings
        """
        settings = get_settings()
        self.ocr_mode = ocr_mode or settings.ocr_mode
        
        # Initialize Document AI processor if needed
        self.document_ai = None
        if self.ocr_mode in ["document_ai", "auto"]:
            try:
                if settings.document_ai_enabled and settings.document_ai_processor_id:
                    self.document_ai = DocumentAIProcessor()
                    logger.info(f"Document AI processor initialized for mode: {self.ocr_mode}")
                else:
                    logger.warning("Document AI not configured, will use tesseract only")
                    if self.ocr_mode == "document_ai":
                        self.ocr_mode = "tesseract"
            except Exception as e:
                logger.warning(f"Failed to initialize Document AI: {e}. Will use tesseract.")
                if self.ocr_mode == "document_ai":
                    self.ocr_mode = "tesseract"
        
        logger.info(f"PDFProcessor initialized with OCR mode: {self.ocr_mode}")
    
    def extract_text(self, pdf_content: bytes) -> str:
        """
        Extract text from PDF file
        
        Args:
            pdf_content: PDF file content as bytes
            
        Returns:
            Extracted text
            
        Raises:
            Exception: If extraction fails
        """
        try:
            text = ""
            with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            
            logger.info(f"Extracted {len(text)} characters from PDF")
            return text
            
        except Exception as e:
            logger.error(f"Failed to extract text from PDF: {e}")
            raise
    
    def extract_invoice_number(self, text: str) -> Optional[str]:
        """
        Extract invoice number from text using regex patterns (Spanish optimized)
        
        Args:
            text: Extracted PDF text
            
        Returns:
            Invoice number or None if not found
        """
        patterns = [
            # Spanish patterns
            r'(?:Factura|Comprobante)\s*(?:N[°º]|Nro\.?|Número)\s*:?\s*([A-Z0-9-]+)',
            r'(?:Número de Factura)\s*:?\s*([A-Z0-9-]+)',
            r'N[°º]\s*(?:de\s*)?(?:Factura|Comprobante)\s*:?\s*([A-Z0-9-]+)',
            # English patterns
            r'Invoice\s*#?\s*:?\s*([A-Z0-9-]+)',
            r'Invoice\s*Number\s*:?\s*([A-Z0-9-]+)',
            r'INV-?([0-9]+)',
            # Generic patterns
            r'Factura\s*#?\s*:?\s*([A-Z0-9-]+)',
            r'N[°º]\s*([A-Z0-9-]+)',
            r'No\.\s*([A-Z0-9-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                invoice_number = match.group(1).strip()
                logger.info(f"Extracted invoice number: {invoice_number}")
                return invoice_number
        
        logger.warning("Invoice number not found")
        return None
    
    def extract_date(self, text: str) -> Optional[str]:
        """
        Extract invoice date from text (Spanish optimized)
        
        Args:
            text: Extracted PDF text
            
        Returns:
            Invoice date in ISO format or None if not found
        """
        # Date patterns (Spanish and English formats)
        patterns = [
            # Spanish patterns
            r'(?:Fecha de Emisión|Fecha de Factura|Fecha)\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
            r'(?:Fecha de Emisión|Fecha de Factura|Fecha)\s*:?\s*(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})',
            # English patterns
            r'(?:Date|Date of Invoice|Issue Date)\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
            r'(?:Date|Date of Invoice)\s*:?\s*(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
            r'(?:Date|Fecha)\s*:?\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                date_str = match.group(1).strip()
                
                # Try to parse the date
                parsed_date = self._parse_date(date_str)
                if parsed_date:
                    logger.info(f"Extracted invoice date: {parsed_date}")
                    return parsed_date
        
        logger.warning("Invoice date not found")
        return None
    
    def _parse_date(self, date_str: str) -> Optional[str]:
        """
        Parse date string to ISO format (Spanish optimized)
        
        Supports:
        - DD/MM/YYYY or DD-MM-YYYY
        - DD de mes de YYYY (Spanish format)
        - Standard formats
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Date in ISO format (YYYY-MM-DD) or None
        """
        if not date_str:
            return None
        
        date_str = date_str.strip()
        
        # Pattern 1: DD/MM/YYYY or DD-MM-YYYY (Spanish format)
        numeric_pattern = r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})'
        match = re.search(numeric_pattern, date_str)
        if match:
            day, month, year = match.groups()
            try:
                # Assume DD/MM/YYYY for Spanish invoices
                date_obj = datetime(int(year), int(month), int(day))
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                logger.warning(f"Invalid date values: {day}/{month}/{year}")
        
        # Pattern 2: DD de mes de YYYY (Spanish format)
        spanish_pattern = r'(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})'
        match = re.search(spanish_pattern, date_str, re.IGNORECASE)
        if match:
            day, month_name, year = match.groups()
            month_name = month_name.lower()
            
            if month_name in SPANISH_MONTHS:
                month = SPANISH_MONTHS[month_name]
                try:
                    date_obj = datetime(int(year), month, int(day))
                    return date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    logger.warning(f"Invalid date values: {day}/{month}/{year}")
        
        # Pattern 3: Try standard formats
        date_formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%m/%d/%Y',
            '%B %d, %Y',
            '%b %d, %Y',
            '%d %B %Y',
            '%d %b %Y',
        ]
        
        for fmt in date_formats:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def extract_vendor(self, text: str) -> Optional[str]:
        """
        Extract vendor name from text
        
        Args:
            text: Extracted PDF text
            
        Returns:
            Vendor name or None if not found
        """
        patterns = [
            r'(?:From|Vendor|Supplier|Company)\s*:?\s*([A-Za-z0-9\s&.,]+)',
            r'(?:De|Proveedor|Empresa)\s*:?\s*([A-Za-z0-9\s&.,]+)',
            r'(?:Razón Social)\s*:?\s*([A-Za-z0-9\s&.,]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                vendor = match.group(1).strip()
                # Clean up - take only first line
                vendor = vendor.split('\n')[0].strip()
                if len(vendor) > 3:  # Minimum length check
                    logger.info(f"Extracted vendor: {vendor}")
                    return vendor
        
        # Fallback: try to get first line that looks like a company name
        lines = text.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            # Look for lines with company indicators
            if any(indicator in line.upper() for indicator in ['INC', 'LLC', 'LTD', 'CORP', 'S.A.', 'S.R.L.']):
                logger.info(f"Extracted vendor (fallback): {line}")
                return line
        
        logger.warning("Vendor name not found")
        return None
    
    def extract_ruc(self, text: str) -> Optional[str]:
        """
        Extract RUC (Peruvian tax ID) from text
        
        Args:
            text: Extracted PDF text
            
        Returns:
            RUC number or None if not found
        """
        patterns = [
            r'RUC\s*:?\s*(\d{11})',
            r'R\.U\.C\.\s*:?\s*(\d{11})',
            r'Tax\s*ID\s*:?\s*(\d{11})',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                ruc = match.group(1).strip()
                logger.info(f"Extracted RUC: {ruc}")
                return ruc
        
        logger.warning("RUC not found")
        return None
    
    def extract_tax_amount(self, text: str) -> Optional[float]:
        """
        Extract tax amount (IGV) from text with Spanish patterns
        
        Args:
            text: Extracted PDF text
            
        Returns:
            Tax amount as float or None if not found
        """
        patterns = [
            # Spanish patterns (IGV is Peruvian VAT)
            r'(?:IGV|Impuesto)\s*(?:\(18%\))?\s*:?\s*S/\.?\s*([\d,]+\.?\d*)',
            r'(?:IGV|IVA)\s*(?:\(18%\))?\s*:?\s*([\d,]+\.?\d*)',
            # English patterns
            r'(?:Tax|VAT)\s*(?:\(18%\))?\s*:?\s*\$?\s*([\d,]+\.?\d*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1)
                amount_str = self._normalize_amount(amount_str)
                try:
                    amount = float(amount_str)
                    logger.info(f"Extracted tax amount: {amount}")
                    return amount
                except ValueError:
                    continue
        
        logger.warning("Tax amount not found")
        return None
    
    def extract_subtotal(self, text: str) -> Optional[float]:
        """
        Extract subtotal amount from text with Spanish patterns
        
        Args:
            text: Extracted PDF text
            
        Returns:
            Subtotal amount as float or None if not found
        """
        patterns = [
            # Spanish patterns
            r'(?:Subtotal|Sub Total|Base Imponible)\s*:?\s*S/\.?\s*([\d,]+\.?\d*)',
            r'(?:Subtotal|Sub Total|Base Imponible)\s*:?\s*([\d,]+\.?\d*)',
            # English patterns
            r'(?:Subtotal|Sub-total|Sub Total)\s*:?\s*\$?\s*([\d,]+\.?\d*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1)
                amount_str = self._normalize_amount(amount_str)
                try:
                    amount = float(amount_str)
                    logger.info(f"Extracted subtotal: {amount}")
                    return amount
                except ValueError:
                    continue
        
        logger.warning("Subtotal not found")
        return None
    
    def extract_total_amount(self, text: str) -> Optional[float]:
        """
        Extract total amount from text with Spanish currency detection
        
        Args:
            text: Extracted PDF text
            
        Returns:
            Total amount as float or None if not found
        """
        patterns = [
            # Spanish patterns with PEN currency (S/.)
            r'(?:Total|Importe Total|Monto Total)\s*:?\s*S/\.?\s*([\d,]+\.?\d*)',
            r'(?:Total a Pagar|Total Neto)\s*:?\s*S/\.?\s*([\d,]+\.?\d*)',
            # Spanish patterns with generic currency
            r'(?:Total|Importe Total|Monto Total)\s*:?\s*([\d,]+\.?\d*)\s*(?:soles|PEN)?',
            # English patterns
            r'(?:Total|Amount Due|Balance Due|Grand Total)\s*:?\s*\$?\s*([\d,]+\.?\d*)',
            r'(?:Total|Amount Due)\s*:?\s*€?\s*([\d,]+\.?\d*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1)
                # Handle Spanish number format (1.234,56)
                amount_str = self._normalize_amount(amount_str)
                try:
                    amount = float(amount_str)
                    logger.info(f"Extracted total amount: {amount}")
                    return amount
                except ValueError:
                    continue
        
        logger.warning("Total amount not found")
        return None
    
    def _normalize_amount(self, amount_str: str) -> str:
        """
        Normalize amount string to standard format
        
        Handles both Spanish (1.234,56) and English (1,234.56) formats
        
        Args:
            amount_str: Amount string with separators
            
        Returns:
            Normalized amount string
        """
        if not amount_str:
            return "0"
        
        amount_str = amount_str.strip()
        
        # If both comma and dot present, determine format
        if ',' in amount_str and '.' in amount_str:
            last_comma = amount_str.rfind(',')
            last_dot = amount_str.rfind('.')
            
            if last_comma > last_dot:
                # Spanish format: 1.234,56
                amount_str = amount_str.replace('.', '').replace(',', '.')
            else:
                # English format: 1,234.56
                amount_str = amount_str.replace(',', '')
        elif ',' in amount_str:
            # Only comma - check if it's decimal or thousands
            parts = amount_str.split(',')
            if len(parts) == 2 and len(parts[1]) == 2:
                # Likely decimal: 1234,56
                amount_str = amount_str.replace(',', '.')
            else:
                # Likely thousands: 1,234
                amount_str = amount_str.replace(',', '')
        
        return amount_str
    
    def extract_currency(self, text: str) -> Optional[str]:
        """
        Extract currency from text with Spanish currency support
        
        Args:
            text: Extracted PDF text
            
        Returns:
            Currency code or None if not found
        """
        # Look for currency symbols and codes (prioritize Spanish currencies)
        # Check for Peruvian Sol first (most common in Spanish invoices)
        if 'S/' in text or 'S/.' in text or 'PEN' in text.upper() or 'SOLES' in text.upper():
            return 'PEN'
        elif '$' in text or 'USD' in text.upper():
            return 'USD'
        elif '€' in text or 'EUR' in text.upper():
            return 'EUR'
        elif '£' in text or 'GBP' in text.upper():
            return 'GBP'
        
        # Default to PEN for Spanish invoices
        return 'PEN'
    
    def extract_line_items(self, text: str) -> List[LineItem]:
        """
        Extract line items from invoice
        
        Args:
            text: Extracted PDF text
            
        Returns:
            List of LineItem objects
        """
        line_items = []
        
        try:
            # Look for table-like structures
            # This is a simplified implementation
            # In production, you might use more sophisticated table extraction
            
            lines = text.split('\n')
            
            # Look for lines that match item pattern: description, quantity, price
            item_pattern = r'(.+?)\s+(\d+)\s+\$?([\d,]+\.?\d*)\s+\$?([\d,]+\.?\d*)'
            
            for line in lines:
                match = re.search(item_pattern, line)
                if match:
                    try:
                        description = match.group(1).strip()
                        quantity = float(match.group(2))
                        unit_price = float(match.group(3).replace(',', ''))
                        total_price = float(match.group(4).replace(',', ''))
                        
                        # Validate that total = quantity * unit_price (with tolerance)
                        expected_total = quantity * unit_price
                        if abs(expected_total - total_price) < 0.01:
                            line_items.append(LineItem(
                                description=description,
                                quantity=quantity,
                                unit_price=unit_price,
                                total_price=total_price
                            ))
                    except (ValueError, IndexError):
                        continue
            
            logger.info(f"Extracted {len(line_items)} line items")
            
        except Exception as e:
            logger.warning(f"Failed to extract line items: {e}")
        
        return line_items
    
    async def _process_with_document_ai(self, pdf_content: bytes) -> Dict[str, Any]:
        """
        Process invoice using Document AI
        
        Args:
            pdf_content: PDF file content as bytes
            
        Returns:
            Dictionary with extracted invoice data
            
        Raises:
            Exception: If Document AI processing fails
        """
        if not self.document_ai:
            raise Exception("Document AI processor not initialized")
        
        logger.info("Processing invoice with Document AI")
        invoice_data = await self.document_ai.process_document(pdf_content)
        
        # Add OCR engine metadata
        invoice_data['ocrEngine'] = 'document_ai'
        
        return invoice_data
    
    def _process_with_tesseract(self, pdf_content: bytes) -> Dict[str, Any]:
        """
        Process invoice using Tesseract OCR with Spanish language support
        
        Args:
            pdf_content: PDF file content as bytes
            
        Returns:
            Dictionary with extracted invoice data
        """
        logger.info("Processing invoice with Tesseract (Spanish language)")
        
        # Extract text using pdfplumber
        text = self.extract_text(pdf_content)
        
        # Extract all fields using regex patterns
        invoice_data = {
            'invoiceNumber': self.extract_invoice_number(text),
            'invoiceDate': self.extract_date(text),
            'vendorName': self.extract_vendor(text),
            'supplierRuc': self.extract_ruc(text),
            'totalAmount': self.extract_total_amount(text),
            'taxAmount': self.extract_tax_amount(text),
            'subtotal': self.extract_subtotal(text),
            'currency': self.extract_currency(text),
            'lineItems': [item.model_dump() for item in self.extract_line_items(text)],
            'ocrEngine': 'tesseract',
        }
        
        return invoice_data
    
    async def process_invoice(self, pdf_content: bytes) -> Dict[str, Any]:
        """
        Process PDF invoice and extract all data with automatic OCR engine selection
        
        Args:
            pdf_content: PDF file content as bytes
            
        Returns:
            Dictionary with extracted invoice data including OCR engine metadata
        """
        ocr_engine_used = None
        invoice_data = None
        
        try:
            if self.ocr_mode == "document_ai":
                # Use Document AI only
                invoice_data = await self._process_with_document_ai(pdf_content)
                ocr_engine_used = "document_ai"
                logger.info("Invoice processed successfully with Document AI")
                
            elif self.ocr_mode == "tesseract":
                # Use Tesseract only
                invoice_data = self._process_with_tesseract(pdf_content)
                ocr_engine_used = "tesseract"
                logger.info("Invoice processed successfully with Tesseract")
                
            else:  # auto mode
                # Try Document AI first, fall back to Tesseract
                try:
                    if self.document_ai:
                        invoice_data = await self._process_with_document_ai(pdf_content)
                        ocr_engine_used = "document_ai"
                        logger.info("Invoice processed successfully with Document AI (auto mode)")
                    else:
                        raise Exception("Document AI not available")
                        
                except Exception as e:
                    logger.warning(f"Document AI failed in auto mode, falling back to Tesseract: {e}")
                    invoice_data = self._process_with_tesseract(pdf_content)
                    ocr_engine_used = "tesseract"
                    logger.info("Invoice processed successfully with Tesseract (fallback)")
            
            # Ensure OCR engine is set
            if invoice_data and 'ocrEngine' not in invoice_data:
                invoice_data['ocrEngine'] = ocr_engine_used
            
            logger.info(f"Successfully processed invoice using {ocr_engine_used}")
            return invoice_data
            
        except Exception as e:
            logger.error(f"Failed to process invoice: {e}")
            raise
