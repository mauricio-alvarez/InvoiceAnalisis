"""Document AI processor service for advanced invoice OCR"""
import logging
import re
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

from google.cloud import documentai_v1 as documentai
from google.api_core.exceptions import GoogleAPIError

from app.core.config import get_settings

logger = logging.getLogger(__name__)

# Spanish month names mapping
SPANISH_MONTHS = {
    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
    'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
    'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
}


class DocumentAIProcessor:
    """Service for processing invoices using Google Document AI"""
    
    def __init__(self, project_id: Optional[str] = None, 
                 location: Optional[str] = None, 
                 processor_id: Optional[str] = None):
        """
        Initialize Document AI client
        
        Args:
            project_id: GCP project ID (defaults to settings)
            location: Document AI location (defaults to settings)
            processor_id: Document AI processor ID (defaults to settings)
        """
        settings = get_settings()
        
        self.project_id = project_id or settings.document_ai_project_id
        self.location = location or settings.document_ai_location
        self.processor_id = processor_id or settings.document_ai_processor_id
        
        if not all([self.project_id, self.location, self.processor_id]):
            raise ValueError(
                "Document AI configuration incomplete. "
                "Ensure project_id, location, and processor_id are set."
            )
        
        # Initialize Document AI client
        self.client = documentai.DocumentProcessorServiceClient()
        
        # Build processor name
        self.processor_name = self.client.processor_path(
            self.project_id, self.location, self.processor_id
        )
        
        logger.info(
            f"Initialized Document AI processor: {self.processor_name}"
        )
    
    async def process_document(self, pdf_content: bytes, 
                              mime_type: str = "application/pdf") -> Dict[str, Any]:
        """
        Process document using Document AI
        
        Args:
            pdf_content: PDF file content as bytes
            mime_type: MIME type of the document
            
        Returns:
            Dictionary with extracted invoice data
            
        Raises:
            GoogleAPIError: If Document AI API call fails
            Exception: For other processing errors
        """
        try:
            logger.info(f"Processing document with Document AI (size: {len(pdf_content)} bytes)")
            
            # Create the document request
            raw_document = documentai.RawDocument(
                content=pdf_content,
                mime_type=mime_type
            )
            
            # Configure the process request
            request = documentai.ProcessRequest(
                name=self.processor_name,
                raw_document=raw_document
            )
            
            # Process the document
            result = self.client.process_document(request=request)
            document = result.document
            
            logger.info(f"Document AI processing complete. Confidence: {document.confidence:.2%}")
            
            # Extract entities from the document
            invoice_data = self._extract_entities(document)
            
            # Add confidence score
            invoice_data['ocrConfidence'] = document.confidence
            
            return invoice_data
            
        except GoogleAPIError as e:
            logger.error(f"Document AI API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in Document AI processing: {e}")
            raise

    def _extract_entities(self, document: documentai.Document) -> Dict[str, Any]:
        """
        Extract structured entities from Document AI response
        
        Args:
            document: Document AI document object
            
        Returns:
            Dictionary with extracted invoice fields
        """
        invoice_data = {
            'invoiceNumber': None,
            'invoiceDate': None,
            'dueDate': None,
            'vendorName': None,
            'supplierRuc': None,
            'totalAmount': None,
            'taxAmount': None,
            'subtotal': None,
            'currency': None,
        }
        
        # Extract entities from Document AI
        for entity in document.entities:
            entity_type = entity.type_
            entity_text = entity.mention_text.strip() if entity.mention_text else None
            
            if not entity_text:
                continue
            
            logger.debug(f"Processing entity: {entity_type} = {entity_text}")
            
            # Map Document AI entity types to our invoice fields
            if entity_type in ['invoice_id', 'invoice_number']:
                invoice_data['invoiceNumber'] = entity_text
                
            elif entity_type in ['invoice_date', 'issue_date']:
                parsed_date = self._parse_spanish_date(entity_text)
                if parsed_date:
                    invoice_data['invoiceDate'] = parsed_date
                    
            elif entity_type in ['due_date', 'payment_due_date']:
                parsed_date = self._parse_spanish_date(entity_text)
                if parsed_date:
                    invoice_data['dueDate'] = parsed_date
                    
            elif entity_type in ['supplier_name', 'vendor_name', 'receiver_name']:
                invoice_data['vendorName'] = entity_text
                
            elif entity_type in ['supplier_tax_id', 'vat_number', 'tax_id']:
                # RUC is the Peruvian tax ID
                invoice_data['supplierRuc'] = entity_text
                
            elif entity_type in ['total_amount', 'net_amount']:
                amount, currency = self._parse_currency(entity_text)
                if amount is not None:
                    invoice_data['totalAmount'] = amount
                if currency:
                    invoice_data['currency'] = currency
                    
            elif entity_type in ['total_tax_amount', 'vat_amount']:
                amount, currency = self._parse_currency(entity_text)
                if amount is not None:
                    invoice_data['taxAmount'] = amount
                if currency and not invoice_data['currency']:
                    invoice_data['currency'] = currency
                    
            elif entity_type in ['subtotal', 'subtotal_amount']:
                amount, currency = self._parse_currency(entity_text)
                if amount is not None:
                    invoice_data['subtotal'] = amount
                if currency and not invoice_data['currency']:
                    invoice_data['currency'] = currency
        
        # Fallback: extract from document text if entities not found
        if not invoice_data['currency']:
            invoice_data['currency'] = self._detect_currency_from_text(document.text)
        
        # Log extracted data
        extracted_fields = [k for k, v in invoice_data.items() if v is not None]
        logger.info(f"Extracted fields: {', '.join(extracted_fields)}")
        
        return invoice_data
    
    def _parse_spanish_date(self, date_str: str) -> Optional[str]:
        """
        Parse Spanish date formats to ISO format (YYYY-MM-DD)
        
        Supports formats:
        - DD/MM/YYYY
        - DD-MM-YYYY
        - DD de mes de YYYY (e.g., "15 de enero de 2024")
        
        Args:
            date_str: Date string in Spanish format
            
        Returns:
            Date in ISO format (YYYY-MM-DD) or None if parsing fails
        """
        if not date_str:
            return None
        
        date_str = date_str.strip()
        
        # Pattern 1: DD/MM/YYYY or DD-MM-YYYY
        numeric_pattern = r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})'
        match = re.search(numeric_pattern, date_str)
        if match:
            day, month, year = match.groups()
            try:
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
        
        # Pattern 3: Try standard ISO format YYYY-MM-DD
        iso_pattern = r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})'
        match = re.search(iso_pattern, date_str)
        if match:
            year, month, day = match.groups()
            try:
                date_obj = datetime(int(year), int(month), int(day))
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                logger.warning(f"Invalid date values: {year}/{month}/{day}")
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def _parse_currency(self, amount_str: str) -> Tuple[Optional[float], Optional[str]]:
        """
        Parse currency amounts with Spanish formats
        
        Supports:
        - S/. 1,234.56 (Peruvian Sol)
        - $ 1,234.56 (USD)
        - 1,234.56 (no symbol)
        
        Args:
            amount_str: Amount string with or without currency symbol
            
        Returns:
            Tuple of (amount as float, currency code) or (None, None)
        """
        if not amount_str:
            return None, None
        
        amount_str = amount_str.strip()
        currency = None
        
        # Detect currency symbol
        if 'S/' in amount_str or 'S/.' in amount_str:
            currency = 'PEN'
            amount_str = re.sub(r'S/\.?', '', amount_str)
        elif '$' in amount_str:
            currency = 'USD'
            amount_str = amount_str.replace('$', '')
        elif '€' in amount_str:
            currency = 'EUR'
            amount_str = amount_str.replace('€', '')
        
        # Check for currency keywords
        if 'soles' in amount_str.lower() or 'pen' in amount_str.lower():
            currency = 'PEN'
            amount_str = re.sub(r'(soles|pen)', '', amount_str, flags=re.IGNORECASE)
        elif 'usd' in amount_str.lower():
            currency = 'USD'
            amount_str = re.sub(r'usd', '', amount_str, flags=re.IGNORECASE)
        
        # Clean up the amount string
        # Remove spaces and common separators
        amount_str = amount_str.strip()
        
        # Handle different number formats
        # Spanish format: 1.234,56 (dot for thousands, comma for decimal)
        # English format: 1,234.56 (comma for thousands, dot for decimal)
        
        # Try to detect format by looking at the last separator
        if ',' in amount_str and '.' in amount_str:
            # Both separators present
            last_comma = amount_str.rfind(',')
            last_dot = amount_str.rfind('.')
            
            if last_comma > last_dot:
                # Spanish format: 1.234,56
                amount_str = amount_str.replace('.', '').replace(',', '.')
            else:
                # English format: 1,234.56
                amount_str = amount_str.replace(',', '')
        elif ',' in amount_str:
            # Only comma - could be thousands or decimal
            # If there are 2 digits after comma, it's likely decimal
            parts = amount_str.split(',')
            if len(parts) == 2 and len(parts[1]) == 2:
                # Likely decimal: 1234,56
                amount_str = amount_str.replace(',', '.')
            else:
                # Likely thousands: 1,234
                amount_str = amount_str.replace(',', '')
        # If only dot, assume it's already in correct format
        
        # Extract numeric value
        try:
            amount = float(amount_str)
            return amount, currency
        except ValueError:
            logger.warning(f"Could not parse amount: {amount_str}")
            return None, None
    
    def _detect_currency_from_text(self, text: str) -> Optional[str]:
        """
        Detect currency from document text
        
        Args:
            text: Full document text
            
        Returns:
            Currency code or None
        """
        if not text:
            return None
        
        # Check for currency symbols and keywords
        if 'S/' in text or 'soles' in text.lower() or 'PEN' in text:
            return 'PEN'
        elif '$' in text or 'USD' in text:
            return 'USD'
        elif '€' in text or 'EUR' in text:
            return 'EUR'
        
        # Default to PEN for Spanish invoices
        return 'PEN'
