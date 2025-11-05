"""LLM-based invoice data extraction service using OpenAI"""
import logging
import json
from typing import Dict, Any, Optional
from openai import OpenAI

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class LLMExtractor:
    """Service for extracting invoice data using LLM"""
    
    def __init__(self):
        """Initialize OpenAI client"""
        settings = get_settings()
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        logger.info(f"LLM Extractor initialized with model: {self.model}")
    
    def extract_invoice_data(self, text: str) -> Dict[str, Any]:
        """
        Extract invoice data from text using LLM
        
        Args:
            text: Extracted text from PDF (all pages combined)
            
        Returns:
            Dictionary with extracted invoice data
            
        Raises:
            Exception: If extraction fails
        """
        try:
            logger.info(f"Extracting invoice data from {len(text)} characters of text")
            
            # Create the prompt
            prompt = self._create_extraction_prompt(text)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert invoice data extraction assistant. Extract structured data from invoice text and return it as valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,  # Low temperature for consistent extraction
                response_format={"type": "json_object"}  # Ensure JSON response
            )
            
            # Parse the response
            result_text = response.choices[0].message.content
            invoice_data = json.loads(result_text)
            
            logger.info(f"Successfully extracted invoice data: {list(invoice_data.keys())}")
            
            # Validate and normalize the data
            normalized_data = self._normalize_invoice_data(invoice_data)
            
            return normalized_data
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            logger.error(f"Response text: {result_text}")
            raise Exception("LLM returned invalid JSON")
        except Exception as e:
            logger.error(f"Failed to extract invoice data with LLM: {e}")
            raise
    
    def _create_extraction_prompt(self, text: str) -> str:
        """
        Create the extraction prompt for the LLM
        
        Args:
            text: Invoice text
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Extract the following information from this invoice text and return it as a JSON object.

**Invoice Text:**
{text}

**Required JSON Format:**
{{
  "invoiceNumber": "string or null",
  "invoiceDate": "YYYY-MM-DD or null",
  "dueDate": "YYYY-MM-DD or null",
  "supplierName": "string or null",
  "supplierRuc": "string or null (Peruvian tax ID)",
  "vendorName": "string or null (same as supplierName if not found separately)",
  "subtotal": number or null,
  "taxAmount": number or null (IGV in Peru, typically 18%)",
  "totalAmount": number or null,
  "currency": "string or null (e.g., PEN, USD, S/.)",
  "lineItems": [
    {{
      "description": "string",
      "quantity": number,
      "unitPrice": number,
      "totalPrice": number
    }}
  ] or []
}}

**Extraction Guidelines:**
1. **Invoice Number**: Look for "Factura", "Comprobante", "Invoice", "N°", "Nro", "Número"
2. **Dates**: Convert Spanish dates to YYYY-MM-DD format (e.g., "15 de marzo de 2024" → "2024-03-15")
3. **RUC**: Peruvian tax ID, typically 11 digits
4. **Supplier/Vendor**: Company name issuing the invoice
5. **Amounts**: Extract numeric values only (remove currency symbols)
6. **Currency**: Identify currency (S/. = PEN, $ = USD, etc.)
7. **Line Items**: Extract product/service descriptions with quantities and prices
8. **Tax (IGV)**: In Peru, typically 18% of subtotal
9. If a field cannot be found, set it to null
10. Ensure all numeric fields are numbers, not strings
11. Return ONLY valid JSON, no additional text

**Spanish Field Names to Look For:**
- Razón Social → supplierName
- RUC → supplierRuc
- Fecha de Emisión → invoiceDate
- Fecha de Vencimiento → dueDate
- Número de Factura → invoiceNumber
- Subtotal → subtotal
- IGV → taxAmount
- Total → totalAmount

Extract the data now:"""
        
        return prompt
    
    def _normalize_invoice_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize and validate extracted invoice data
        
        Args:
            data: Raw extracted data from LLM
            
        Returns:
            Normalized invoice data
        """
        normalized = {
            'invoiceNumber': data.get('invoiceNumber'),
            'invoiceDate': data.get('invoiceDate'),
            'dueDate': data.get('dueDate'),
            'supplierName': data.get('supplierName') or data.get('vendorName'),
            'supplierRuc': data.get('supplierRuc'),
            'vendorName': data.get('vendorName') or data.get('supplierName'),
            'subtotal': self._to_float(data.get('subtotal')),
            'taxAmount': self._to_float(data.get('taxAmount')),
            'totalAmount': self._to_float(data.get('totalAmount')),
            'currency': self._normalize_currency(data.get('currency')),
            'lineItems': data.get('lineItems', [])
        }
        
        # Validate line items
        if normalized['lineItems']:
            normalized['lineItems'] = [
                {
                    'description': item.get('description', ''),
                    'quantity': self._to_float(item.get('quantity', 0)),
                    'unitPrice': self._to_float(item.get('unitPrice', 0)),
                    'totalPrice': self._to_float(item.get('totalPrice', 0))
                }
                for item in normalized['lineItems']
                if isinstance(item, dict)
            ]
        
        logger.info(f"Normalized invoice data: invoiceNumber={normalized.get('invoiceNumber')}, total={normalized.get('totalAmount')}")
        
        return normalized
    
    def _to_float(self, value: Any) -> Optional[float]:
        """Convert value to float, return None if not possible"""
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _normalize_currency(self, currency: Optional[str]) -> Optional[str]:
        """Normalize currency code"""
        if not currency:
            return None
        
        currency = str(currency).upper().strip()
        
        # Map common variations
        currency_map = {
            'S/.': 'PEN',
            'S/': 'PEN',
            'SOLES': 'PEN',
            'SOL': 'PEN',
            '$': 'USD',
            'DOLARES': 'USD',
            'DÓLARES': 'USD'
        }
        
        return currency_map.get(currency, currency)
