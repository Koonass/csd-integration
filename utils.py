"""
Utility functions for the CSD Portal integration
"""
import logging
import json
import hashlib
import hmac
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

import config


def setup_logging() -> logging.Logger:
    """
    Setup logging configuration

    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    config.LOG_DIR.mkdir(exist_ok=True)

    # Create logger
    logger = logging.getLogger('csd_integration')
    logger.setLevel(getattr(logging, config.LOG_LEVEL))

    # Create file handler
    file_handler = logging.FileHandler(config.LOG_FILE)
    file_handler.setLevel(logging.DEBUG)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def parse_jotform_webhook(webhook_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Parse JotForm webhook data into standardized format

    Args:
        webhook_data: Raw webhook data from JotForm

    Returns:
        Parsed submission data or None if parsing failed
    """
    try:
        # JotForm sends data in different formats depending on settings
        # Try to extract submission data

        submission_id = webhook_data.get('submissionID')
        if not submission_id:
            # Try alternative field names
            submission_id = webhook_data.get('submission_id')

        if not submission_id:
            logging.error("No submission ID found in webhook data")
            return None

        # Extract raw request data
        raw_request = webhook_data.get('rawRequest', {})
        if isinstance(raw_request, str):
            try:
                raw_request = json.loads(raw_request)
            except json.JSONDecodeError:
                raw_request = {}

        # Parse individual fields
        # JotForm webhook data structure varies, so we handle multiple formats

        # Try to get field data
        fields = {}

        # Method 1: Direct field access from webhook_data
        for key, value in webhook_data.items():
            if key.startswith('q') and '_' in key:
                # JotForm question format (q3_builderName, q5_planName, etc.)
                # Strip the qXX_ prefix to get the field name
                field_name = key.split('_', 1)[1] if '_' in key else key
                fields[field_name] = value
                # Also keep the original key with prefix
                fields[key] = value

        # Method 2: From rawRequest
        if raw_request:
            for key, value in raw_request.items():
                if key.startswith('q') and '_' in key:
                    field_name = key.split('_', 1)[1] if '_' in key else key
                    fields[field_name] = value
                    fields[key] = value

        # Create standardized parsed data
        parsed_data = {
            'jotform_id': submission_id,
            'submitter_name': fields.get('salesman', ''),
            'submitter_email': '',
            'builder_name': fields.get('builderName', ''),
            'plan_name': fields.get('planName', ''),
            'raw_data': {
                **fields,
                'submission_id': submission_id,
                'form_id': webhook_data.get('formID', ''),
                'submission_date': webhook_data.get('created_at', datetime.now().isoformat())
            },
            'retry_count': 0
        }

        return parsed_data

    except Exception as e:
        logging.error(f"Error parsing JotForm webhook: {str(e)}", exc_info=True)
        return None


def validate_webhook(request, secret: str) -> bool:
    """
    Validate JotForm webhook signature

    Args:
        request: Flask request object
        secret: JotForm webhook secret

    Returns:
        True if signature is valid, False otherwise
    """
    try:
        # JotForm webhook signature validation
        # The exact implementation depends on JotForm's signature method

        signature = request.headers.get('X-JotForm-Signature')
        if not signature:
            return True  # If no signature required, allow through

        # Compute expected signature
        body = request.get_data()
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(signature, expected_signature)

    except Exception as e:
        logging.error(f"Error validating webhook signature: {str(e)}")
        return False


def format_phone_number(phone: str) -> str:
    """
    Format phone number to (XXX)-XXX-XXXX format for CSD Portal

    Args:
        phone: Raw phone number string

    Returns:
        Formatted phone number
    """
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, phone))

    if len(digits) == 10:
        return f"({digits[:3]})-{digits[3:6]}-{digits[6:]}"
    elif len(digits) == 11 and digits[0] == '1':
        # Remove leading 1
        return f"({digits[1:4]})-{digits[4:7]}-{digits[7:]}"
    else:
        return phone  # Return as-is if can't format


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file operations

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    import re
    # Remove any characters that aren't alphanumeric, dash, underscore, or period
    sanitized = re.sub(r'[^\w\s\-\.]', '', filename)
    # Replace spaces with underscores
    sanitized = sanitized.replace(' ', '_')
    return sanitized


def download_jotform_file(file_url: str, save_path: Path) -> bool:
    """
    Download file from JotForm

    Args:
        file_url: URL to the file on JotForm
        save_path: Path where to save the file

    Returns:
        True if successful, False otherwise
    """
    import requests

    try:
        response = requests.get(file_url, timeout=30)
        response.raise_for_status()

        save_path.parent.mkdir(parents=True, exist_ok=True)

        with open(save_path, 'wb') as f:
            f.write(response.content)

        logging.info(f"Downloaded file from JotForm: {save_path}")
        return True

    except Exception as e:
        logging.error(f"Error downloading file from JotForm: {str(e)}")
        return False


def get_field_mapping_summary() -> Dict[str, Any]:
    """
    Get summary of field mapping configuration

    Returns:
        Dictionary with mapping summary
    """
    try:
        with open(config.FIELD_MAPPING_FILE, 'r') as f:
            mapping_data = json.load(f)

        mappings = mapping_data.get('mappings', [])

        summary = {
            'total_fields': len(mappings),
            'mapped_fields': sum(1 for m in mappings if not m['csd_field'].startswith('PLACEHOLDER')),
            'unmapped_fields': sum(1 for m in mappings if m['csd_field'].startswith('PLACEHOLDER')),
            'required_fields': sum(1 for m in mappings if m.get('required', False)),
            'file_upload_fields': len(mapping_data.get('file_upload_fields', [])),
            'version': mapping_data.get('version', 'unknown'),
            'last_updated': mapping_data.get('last_updated', 'unknown')
        }

        return summary

    except Exception as e:
        logging.error(f"Error getting field mapping summary: {str(e)}")
        return {}


def generate_test_jotform_data() -> Dict[str, Any]:
    """
    Generate test JotForm data for testing

    Returns:
        Dictionary with test submission data
    """
    return {
        'submissionID': 'TEST_' + datetime.now().strftime('%Y%m%d_%H%M%S'),
        'formID': '240734091032042',
        'builderName': 'Test Builder Inc',
        'lotAnd': 'Lot 123, Test Subdivision',
        'planName': 'Test Plan A',
        'foundationType': 'Slab',
        'roofType': 'Trussed by CBC',
        'jobNotes': 'This is a test submission - DO NOT PROCESS',
        'isThis': 'NO',
        'salesman': 'test@example.com',
        'typeA': 'Atlanta Market',
        'joistDepth': 'Per Designer',
        'chooseAny': ['Sealed Engineered Layout', 'Permit Drawing'],
        'preferredManufacturer': 'Boise',
        'fireplaceConstruction': 'Per Plan'
    }
