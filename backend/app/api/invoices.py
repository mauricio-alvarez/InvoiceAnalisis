"""Invoice API endpoints"""
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query

from app.core.security import (
    AuthenticatedUser,
    require_profile_completed
)
from app.models.invoice import (
    InvoiceResponse,
    InvoiceListResponse,
    InvoiceDetailResponse,
    DownloadUrlResponse
)
from app.services.storage_service import StorageService
from app.services.firestore_service import FirestoreService
from app.services.pdf_processor import PDFProcessor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/invoices", tags=["Invoices"])


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_invoice(
    file: UploadFile = File(...),
    current_user: AuthenticatedUser = Depends(require_profile_completed)
) -> dict:
    """
    Upload a PDF invoice
    
    Uploads a PDF invoice file to Cloud Storage and triggers processing.
    Requires email verification and completed business profile.
    
    Args:
        file: PDF file to upload (max 10MB)
        current_user: Authenticated user with verified email and completed profile
        
    Returns:
        Dictionary with invoice ID, filename, and status
        
    Raises:
        400: Invalid file type or size
        403: Email not verified or profile not completed
        401: Invalid or expired token
        500: Upload failed
    """
    try:
        storage_service = StorageService()
        firestore_service = FirestoreService()
        pdf_processor = PDFProcessor()
        
        # Upload file to Cloud Storage
        storage_url, blob_name = await storage_service.upload_pdf(
            file,
            current_user.uid
        )
        
        # Create invoice document in Firestore
        invoice_data = {
            'userId': current_user.uid,
            'fileName': file.filename,
            'storageUrl': storage_url,
            'status': 'processing',
            'uploadedAt': datetime.utcnow(),
        }
        
        invoice_id = await firestore_service.create_invoice(invoice_data)
        
        # Process PDF in background (simplified - in production use Cloud Tasks)
        try:
            # Download file content
            file_content = storage_service.download_file(blob_name)
            
            # Extract invoice data
            extracted_data = pdf_processor.process_invoice(file_content)
            
            # Update invoice with extracted data
            update_data = {
                'status': 'processed',
                'processedAt': datetime.utcnow(),
                **extracted_data
            }
            
            await firestore_service.update_invoice(invoice_id, update_data)
            
            logger.info(f"Successfully processed invoice: {invoice_id}")
            
        except Exception as e:
            logger.error(f"Failed to process invoice {invoice_id}: {e}")
            # Update status to failed
            await firestore_service.update_invoice(invoice_id, {
                'status': 'failed',
                'errorMessage': str(e),
                'processedAt': datetime.utcnow()
            })
        
        return {
            'invoiceId': invoice_id,
            'fileName': file.filename,
            'status': 'processing',
            'message': 'Invoice uploaded successfully and is being processed'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload invoice: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload invoice"
        )


@router.get("", response_model=InvoiceListResponse)
async def get_invoices(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("uploadedAt", description="Field to sort by"),
    order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    current_user: AuthenticatedUser = Depends(require_profile_completed)
) -> InvoiceListResponse:
    """
    Get user's invoices
    
    Retrieves a paginated list of invoices uploaded by the current user.
    
    Args:
        page: Page number (default: 1)
        limit: Items per page (default: 50, max: 100)
        sort_by: Field to sort by (default: uploadedAt)
        order: Sort order - asc or desc (default: desc)
        current_user: Authenticated user with verified email and completed profile
        
    Returns:
        InvoiceListResponse with paginated invoices
        
    Raises:
        401: Invalid or expired token
        403: Email not verified or profile not completed
        500: Failed to retrieve invoices
    """
    firestore_service = FirestoreService()
    return await firestore_service.get_user_invoices(
        user_id=current_user.uid,
        page=page,
        limit=limit,
        sort_by=sort_by,
        order=order
    )


@router.get("/{invoice_id}", response_model=InvoiceDetailResponse)
async def get_invoice_detail(
    invoice_id: str,
    current_user: AuthenticatedUser = Depends(require_profile_completed)
) -> InvoiceDetailResponse:
    """
    Get invoice details
    
    Retrieves detailed information for a specific invoice.
    Users can only access their own invoices.
    
    Args:
        invoice_id: Invoice document ID
        current_user: Authenticated user with verified email and completed profile
        
    Returns:
        InvoiceDetailResponse with complete invoice data
        
    Raises:
        401: Invalid or expired token
        403: Access denied (not owner) or profile not completed
        404: Invoice not found
        500: Failed to retrieve invoice
    """
    firestore_service = FirestoreService()
    
    # Get invoice
    invoice_data = await firestore_service.get_invoice(invoice_id)
    
    if not invoice_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    # Check ownership
    if invoice_data.get('userId') != current_user.uid:
        logger.warning(
            f"User {current_user.uid} attempted to access invoice {invoice_id} "
            f"owned by {invoice_data.get('userId')}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Convert to response model
    if 'uploadedAt' in invoice_data:
        invoice_data['uploaded_at'] = invoice_data.pop('uploadedAt')
    if 'processedAt' in invoice_data:
        invoice_data['processed_at'] = invoice_data.pop('processedAt')
    
    response_data = {
        'id': invoice_data.get('id'),
        'user_id': invoice_data.get('userId'),
        'file_name': invoice_data.get('fileName'),
        'storage_url': invoice_data.get('storageUrl'),
        'status': invoice_data.get('status'),
        'invoice_number': invoice_data.get('invoiceNumber'),
        'invoice_date': invoice_data.get('invoiceDate'),
        'vendor_name': invoice_data.get('vendorName'),
        'total_amount': invoice_data.get('totalAmount'),
        'currency': invoice_data.get('currency'),
        'line_items': invoice_data.get('lineItems'),
        'uploaded_at': invoice_data.get('uploaded_at'),
        'processed_at': invoice_data.get('processed_at'),
        'error_message': invoice_data.get('errorMessage'),
    }
    
    return InvoiceDetailResponse(**response_data)


@router.get("/{invoice_id}/download", response_model=DownloadUrlResponse)
async def get_download_url(
    invoice_id: str,
    current_user: AuthenticatedUser = Depends(require_profile_completed)
) -> DownloadUrlResponse:
    """
    Get signed download URL for invoice PDF
    
    Generates a temporary signed URL for downloading the original PDF file.
    URL expires after 1 hour.
    
    Args:
        invoice_id: Invoice document ID
        current_user: Authenticated user with verified email and completed profile
        
    Returns:
        DownloadUrlResponse with signed URL and expiration time
        
    Raises:
        401: Invalid or expired token
        403: Access denied (not owner) or profile not completed
        404: Invoice or file not found
        500: Failed to generate download URL
    """
    firestore_service = FirestoreService()
    storage_service = StorageService()
    
    # Get invoice
    invoice_data = await firestore_service.get_invoice(invoice_id)
    
    if not invoice_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    # Check ownership
    if invoice_data.get('userId') != current_user.uid:
        logger.warning(
            f"User {current_user.uid} attempted to download invoice {invoice_id} "
            f"owned by {invoice_data.get('userId')}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Get storage URL and extract blob name
    storage_url = invoice_data.get('storageUrl')
    if not storage_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    blob_name = storage_service.get_blob_name_from_url(storage_url)
    
    # Generate signed URL
    signed_url, expires_at = storage_service.generate_signed_url(blob_name)
    
    return DownloadUrlResponse(
        download_url=signed_url,
        expires_at=expires_at
    )
