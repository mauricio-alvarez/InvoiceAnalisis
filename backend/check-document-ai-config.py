#!/usr/bin/env python3
"""
Diagnostic script to check Document AI configuration
Run this to see what environment variables are being read
"""
import os
from app.core.config import get_settings

def check_config():
    print("=" * 60)
    print("Document AI Configuration Check")
    print("=" * 60)
    print()
    
    # Check environment variables directly
    print("Environment Variables (from os.environ):")
    print("-" * 60)
    env_vars = [
        'DOCUMENT_AI_PROJECT_ID',
        'DOCUMENT_AI_LOCATION',
        'DOCUMENT_AI_PROCESSOR_ID',
        'DOCUMENT_AI_ENABLED',
        'OCR_MODE',
        'GCP_PROJECT_ID'
    ]
    
    for var in env_vars:
        value = os.environ.get(var, '<NOT SET>')
        print(f"  {var}: {value}")
    
    print()
    print("=" * 60)
    print("Settings Object (from get_settings()):")
    print("-" * 60)
    
    try:
        settings = get_settings()
        print(f"  document_ai_project_id: {settings.document_ai_project_id}")
        print(f"  document_ai_location: {settings.document_ai_location}")
        print(f"  document_ai_processor_id: {settings.document_ai_processor_id}")
        print(f"  document_ai_enabled: {settings.document_ai_enabled}")
        print(f"  ocr_mode: {settings.ocr_mode}")
        print(f"  gcp_project_id: {settings.gcp_project_id}")
        
        print()
        print("=" * 60)
        print("Document AI Status:")
        print("-" * 60)
        
        if not settings.document_ai_enabled:
            print("  ❌ Document AI is DISABLED")
        elif not settings.document_ai_processor_id:
            print("  ❌ Document AI processor ID is NOT SET")
            print("     Document AI will not be used even if enabled=True")
        else:
            print("  ✅ Document AI is ENABLED")
            print(f"     Processor: projects/{settings.document_ai_project_id}/locations/{settings.document_ai_location}/processors/{settings.document_ai_processor_id}")
        
        print()
        print(f"  OCR Mode: {settings.ocr_mode}")
        if settings.ocr_mode == "auto":
            print("     Will try Document AI first, fallback to Tesseract")
        elif settings.ocr_mode == "document_ai":
            print("     Will use Document AI only")
        elif settings.ocr_mode == "tesseract":
            print("     Will use Tesseract only")
        
    except Exception as e:
        print(f"  ❌ Error loading settings: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 60)

if __name__ == "__main__":
    check_config()
