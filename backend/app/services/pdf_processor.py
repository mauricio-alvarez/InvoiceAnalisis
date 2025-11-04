"""PDF processing service for invoice data extraction"""
import logging
import re
from typing import Optional, List, Dict, Any
from datetime import datetime
import io

import pdfplumber

from app.models.invoice import LineItem

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Service for extracting invoice data from PDF files"""
    
    def __init__(self):
        pass
    
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
        Extract invoice number from text using regex patterns
        
        Args:
            text: Extracted PDF text
            
        Returns:
            Invoice number or None if not found
        """
        patterns = [
            r'Invoice\s*#?\s*:?\s*([A-Z0-9-]+)',
            r'Invoice\s*Number\s*:?\s*([A-Z0-9-]+)',
            r'INV-?([0-9]+)',
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
        Extract invoice date from text
        
        Args:
            text: Extracted PDF text
            
        Returns:
            Invoice date in ISO format or None if not found
        """
        # Date patterns (various formats)
        patterns = [
            # DD/MM/YYYY or DD-MM-YYYY
            r'(?:Date|Fecha|Date of Invoice)\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
            # YYYY-MM-DD
            r'(?:Date|Fecha|Date of Invoice)\s*:?\s*(\d{4}[/-]\d{1,2}[/-]\d{1,2})',
            # Month DD, YYYY
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
        Parse date string to ISO format
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Date in ISO format (YYYY-MM-DD) or None
        """
        date_formats = [
            '%d/%m/%Y',
            '%d-%m-%Y',
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
    
    def extract_total_amount(self, text: str) -> Optional[float]:
        """
        Extract total amount from text with currency detection
        
        Args:
            text: Extracted PDF text
            
        Returns:
            Total amount as float or None if not found
        """
        patterns = [
            r'(?:Total|Amount Due|Balance Due|Grand Total)\s*:?\s*\$?\s*([\d,]+\.?\d*)',
            r'(?:Total|Monto Total|Importe Total)\s*:?\s*S/\.?\s*([\d,]+\.?\d*)',
            r'(?:Total|Monto Total)\s*:?\s*€?\s*([\d,]+\.?\d*)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    amount = float(amount_str)
                    logger.info(f"Extracted total amount: {amount}")
                    return amount
                except ValueError:
                    continue
        
        logger.warning("Total amount not found")
        return None
    
    def extract_currency(self, text: str) -> Optional[str]:
        """
        Extract currency from text
        
        Args:
            text: Extracted PDF text
            
        Returns:
            Currency code or None if not found
        """
        # Look for currency symbols and codes
        if '$' in text or 'USD' in text.upper():
            return 'USD'
        elif 'S/' in text or 'PEN' in text.upper() or 'SOLES' in text.upper():
            return 'PEN'
        elif '€' in text or 'EUR' in text.upper():
            return 'EUR'
        elif '£' in text or 'GBP' in text.upper():
            return 'GBP'
        
        # Default to USD if not found
        return 'USD'
    
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
    
    def process_invoice(self, pdf_content: bytes) -> Dict[str, Any]:
        """
        Process PDF invoice and extract all data
        
        Args:
            pdf_content: PDF file content as bytes
            
        Returns:
            Dictionary with extracted invoice data
        """
        try:
            # Extract text
            text = self.extract_text(pdf_content)
            
            # Extract all fields
            invoice_data = {
                'invoiceNumber': self.extract_invoice_number(text),
                'invoiceDate': self.extract_date(text),
                'vendorName': self.extract_vendor(text),
                'totalAmount': self.extract_total_amount(text),
                'currency': self.extract_currency(text),
                'lineItems': [item.model_dump() for item in self.extract_line_items(text)],
            }
            
            logger.info("Successfully processed invoice")
            return invoice_data
            
        except Exception as e:
            logger.error(f"Failed to process invoice: {e}")
            raise
