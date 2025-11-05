"""PDF processing service for invoice data extraction"""
import logging
from typing import Dict, Any

from app.services.document_ai_processor import DocumentAIProcessor
from app.services.pdfminer_extractor import PDFMinerExtractor
from app.services.llm_extractor import LLMExtractor
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Service for extracting invoice data from PDF files using modern AI methods"""
    
    def __init__(self, ocr_mode: str = None):
        """
        Initialize PDF processor with OCR mode
        
        Args:
            ocr_mode: OCR engine mode - "document_ai", "llm", or "auto"
                     If None, uses value from settings
        """
        settings = get_settings()
        self.ocr_mode = ocr_mode or settings.ocr_mode
        
        # Initialize PDFMiner extractor (always available for LLM mode)
        self.pdfminer = PDFMinerExtractor()
        logger.info("PDFMiner extractor initialized")
        
        # Initialize LLM extractor if enabled
        self.llm_extractor = None
        if settings.llm_extraction_enabled and settings.openai_api_key:
            try:
                self.llm_extractor = LLMExtractor()
                logger.info("LLM extractor initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM extractor: {e}")
        
        # Initialize Document AI processor if needed
        self.document_ai = None
        if self.ocr_mode in ["document_ai", "auto"]:
            try:
                if settings.document_ai_enabled and settings.document_ai_processor_id:
                    self.document_ai = DocumentAIProcessor()
                    logger.info(f"Document AI processor initialized for mode: {self.ocr_mode}")
                else:
                    logger.warning("Document AI not configured")
                    if self.ocr_mode == "document_ai":
                        # If Document AI is explicitly requested but not available, fail
                        raise Exception("Document AI requested but not configured")
            except Exception as e:
                logger.error(f"Failed to initialize Document AI: {e}")
                if self.ocr_mode == "document_ai":
                    raise
        
        # Validate configuration
        if self.ocr_mode == "llm" and not self.llm_extractor:
            raise Exception("LLM mode requested but LLM extractor not available")
        
        if self.ocr_mode == "auto" and not self.llm_extractor and not self.document_ai:
            raise Exception("Auto mode requires either LLM or Document AI to be configured")
        
        logger.info(f"PDFProcessor initialized with OCR mode: {self.ocr_mode}")
    
    async def _process_with_document_ai(self, pdf_content: bytes) -> Dict[str, Any]:
        """
        Process invoice using Document AI
        
        Args:
            pdf_content: PDF file content as bytes
            
        Returns:
            Dictionary with extracted invoice data
        """
        logger.info("Processing invoice with Document AI")
        
        if not self.document_ai:
            raise Exception("Document AI processor not initialized")
        
        # Process with Document AI
        result = await self.document_ai.process_invoice(pdf_content)
        
        # Extract invoice data from Document AI response
        invoice_data = {
            'invoiceNumber': result.get('invoice_number'),
            'invoiceDate': result.get('invoice_date'),
            'dueDate': result.get('due_date'),
            'supplierName': result.get('supplier_name'),
            'supplierRuc': result.get('supplier_ruc'),
            'vendorName': result.get('supplier_name'),  # Same as supplier
            'subtotal': result.get('subtotal'),
            'taxAmount': result.get('tax_amount'),
            'totalAmount': result.get('total_amount'),
            'currency': result.get('currency'),
            'lineItems': result.get('line_items', []),
            'ocrEngine': 'document_ai',
            'ocrConfidence': result.get('confidence', 0.9)
        }
        
        logger.info(f"Document AI extraction complete: {invoice_data.get('invoiceNumber')}")
        return invoice_data
    
    def _process_with_llm(self, pdf_content: bytes) -> Dict[str, Any]:
        """
        Process invoice using LLM (OpenAI) with PDFMiner text extraction
        
        Args:
            pdf_content: PDF file content as bytes
            
        Returns:
            Dictionary with extracted invoice data
        """
        logger.info("Processing invoice with LLM (OpenAI + PDFMiner)")
        
        if not self.llm_extractor:
            raise Exception("LLM extractor not initialized")
        
        # Extract text using PDFMiner (more robust than pdfplumber)
        text = self.pdfminer.extract_text_combined(pdf_content)
        
        if not text or len(text.strip()) < 50:
            raise Exception("Insufficient text extracted from PDF")
        
        logger.info(f"Extracted {len(text)} characters from PDF")
        
        # Use LLM to extract structured data
        invoice_data = self.llm_extractor.extract_invoice_data(text)
        
        # Add OCR engine metadata
        invoice_data['ocrEngine'] = 'llm'
        invoice_data['ocrConfidence'] = 0.95  # LLM typically has high confidence
        
        logger.info(f"LLM extraction complete: {invoice_data.get('invoiceNumber')}")
        
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
            if self.ocr_mode == "llm":
                # Use LLM only
                invoice_data = self._process_with_llm(pdf_content)
                ocr_engine_used = "llm"
                logger.info("Invoice processed successfully with LLM")
                
            elif self.ocr_mode == "document_ai":
                # Use Document AI only
                invoice_data = await self._process_with_document_ai(pdf_content)
                ocr_engine_used = "document_ai"
                logger.info("Invoice processed successfully with Document AI")
                
            else:  # auto mode
                # Try LLM first (if available), then Document AI
                try:
                    if self.llm_extractor:
                        invoice_data = self._process_with_llm(pdf_content)
                        ocr_engine_used = "llm"
                        logger.info("Invoice processed successfully with LLM (auto mode)")
                    elif self.document_ai:
                        invoice_data = await self._process_with_document_ai(pdf_content)
                        ocr_engine_used = "document_ai"
                        logger.info("Invoice processed successfully with Document AI (auto mode)")
                    else:
                        raise Exception("No extraction methods available")
                        
                except Exception as e:
                    logger.error(f"All extraction methods failed in auto mode: {e}")
                    raise Exception(f"Failed to process invoice: {str(e)}")
            
            # Ensure OCR engine is set
            if invoice_data and 'ocrEngine' not in invoice_data:
                invoice_data['ocrEngine'] = ocr_engine_used
            
            logger.info(f"Successfully processed invoice using {ocr_engine_used}")
            return invoice_data
            
        except Exception as e:
            logger.error(f"Failed to process invoice: {e}")
            raise
