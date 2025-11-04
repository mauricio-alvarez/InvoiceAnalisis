"""Tests for PDF processor service"""
import pytest
from app.services.pdf_processor import PDFProcessor


@pytest.fixture
def pdf_processor():
    """Create PDF processor instance"""
    return PDFProcessor()


def test_extract_invoice_number(pdf_processor):
    """Test invoice number extraction"""
    text = "Invoice #INV-12345\nDate: 2024-01-15"
    result = pdf_processor.extract_invoice_number(text)
    assert result == 'INV-12345'


def test_extract_invoice_number_alternative_format(pdf_processor):
    """Test invoice number extraction with alternative format"""
    text = "Invoice Number: 98765\nTotal: $100.00"
    result = pdf_processor.extract_invoice_number(text)
    assert result == '98765'


def test_extract_date(pdf_processor):
    """Test date extraction"""
    text = "Date: 15/01/2024\nInvoice: INV-123"
    result = pdf_processor.extract_date(text)
    assert result == '2024-01-15'


def test_extract_vendor(pdf_processor):
    """Test vendor name extraction"""
    text = "From: Acme Corporation\nInvoice: INV-123"
    result = pdf_processor.extract_vendor(text)
    assert 'Acme Corporation' in result


def test_extract_total_amount(pdf_processor):
    """Test total amount extraction"""
    text = "Total: $1,234.56\nThank you"
    result = pdf_processor.extract_total_amount(text)
    assert result == 1234.56


def test_extract_currency_usd(pdf_processor):
    """Test USD currency detection"""
    text = "Total: $100.00 USD"
    result = pdf_processor.extract_currency(text)
    assert result == 'USD'


def test_extract_currency_pen(pdf_processor):
    """Test PEN currency detection"""
    text = "Total: S/ 100.00 SOLES"
    result = pdf_processor.extract_currency(text)
    assert result == 'PEN'


def test_extract_invoice_number_not_found(pdf_processor):
    """Test invoice number extraction when not found"""
    text = "This is just some random text"
    result = pdf_processor.extract_invoice_number(text)
    assert result is None


def test_extract_date_not_found(pdf_processor):
    """Test date extraction when not found"""
    text = "This is just some random text"
    result = pdf_processor.extract_date(text)
    assert result is None
