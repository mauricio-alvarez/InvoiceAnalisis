"""Invoice data models"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class LineItem(BaseModel):
    """Model for invoice line item"""
    description: str
    quantity: float = Field(..., gt=0)
    unit_price: float = Field(..., gt=0, alias="unitPrice")
    total_price: float = Field(..., ge=0, alias="totalPrice")
    
    class Config:
        populate_by_name = True
        by_alias = True


class InvoiceUpload(BaseModel):
    """Model for invoice upload metadata"""
    file_name: str = Field(alias="fileName")
    file_size: int = Field(alias="fileSize")
    content_type: str = Field(alias="contentType")
    
    class Config:
        populate_by_name = True
        by_alias = True


class InvoiceResponse(BaseModel):
    """Model for invoice response"""
    id: str
    user_id: str = Field(alias="userId")
    file_name: str = Field(alias="fileName")
    storage_url: str = Field(alias="storageUrl")
    status: str = Field(..., description="processing, processed, or failed")
    
    # Extracted data
    invoice_number: Optional[str] = Field(None, alias="invoiceNumber")
    invoice_date: Optional[str] = Field(None, alias="invoiceDate")
    vendor_name: Optional[str] = Field(None, alias="vendorName")
    total_amount: Optional[float] = Field(None, alias="totalAmount")
    currency: Optional[str] = None
    line_items: Optional[List[LineItem]] = Field(None, alias="lineItems")
    
    # Metadata
    uploaded_at: datetime = Field(alias="uploadedAt")
    processed_at: Optional[datetime] = Field(None, alias="processedAt")
    error_message: Optional[str] = Field(None, alias="errorMessage")
    
    class Config:
        from_attributes = True
        populate_by_name = True
        by_alias = True


class InvoiceListResponse(BaseModel):
    """Model for paginated invoice list response"""
    invoices: List[InvoiceResponse]
    total: int
    page: int = 1
    limit: int = 50


class InvoiceDetailResponse(InvoiceResponse):
    """Model for detailed invoice response with all fields"""
    pass


class InvoiceStatistics(BaseModel):
    """Model for invoice statistics"""
    total_invoices: int = Field(alias="totalInvoices")
    total_amount: float = Field(alias="totalAmount")
    success_rate: float = Field(alias="successRate")
    processing_count: int = Field(alias="processingCount")
    processed_count: int = Field(alias="processedCount")
    failed_count: int = Field(alias="failedCount")
    
    class Config:
        populate_by_name = True
        by_alias = True


class DownloadUrlResponse(BaseModel):
    """Model for signed download URL response"""
    download_url: str = Field(alias="downloadUrl")
    expires_at: datetime = Field(alias="expiresAt")
    
    class Config:
        populate_by_name = True
        by_alias = True
