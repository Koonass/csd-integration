"""
CSD Portal form submitter - handles automated submission to CSD Portal
"""
import json
import logging
import requests
from typing import Dict, Any, Optional
from pathlib import Path
import time

import config


logger = logging.getLogger(__name__)


class CSDSubmitter:
    """Handle submission to CSD Portal"""

    def __init__(self):
        self.csd_url = config.CSD_PORTAL_URL
        self.timeout = config.CSD_SUBMISSION_TIMEOUT
        self.session = requests.Session()
        self.field_mapping = self._load_field_mapping()

    def _load_field_mapping(self) -> Dict[str, Any]:
        """Load field mapping configuration"""
        try:
            with open(config.FIELD_MAPPING_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading field mapping: {str(e)}")
            return {'mappings': []}

    def reload_mapping(self):
        """Reload field mapping from file (useful after updates)"""
        self.field_mapping = self._load_field_mapping()

    def _map_jotform_to_csd(self, jotform_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map JotForm field data to CSD Portal field names

        Args:
            jotform_data: Raw JotForm submission data

        Returns:
            Dictionary with CSD Portal field names and values
        """
        csd_data = {}
        composite_notes = []

        for mapping in self.field_mapping.get('mappings', []):
            jotform_field = mapping['jotform_field']
            csd_field = mapping['csd_field']
            transform = mapping.get('transform')
            value_mapping = mapping.get('value_mapping', {})

            # Get value from JotForm data
            jotform_value = jotform_data.get(jotform_field)

            if jotform_value is None:
                continue

            # Handle different transformation types
            if transform == 'append_to_notes' or csd_field == 'COMPOSITE_NOTES':
                # Add to composite notes
                label = mapping['jotform_label']
                if isinstance(jotform_value, list):
                    value_str = ', '.join(jotform_value)
                else:
                    value_str = str(jotform_value)
                composite_notes.append(f"{label}: {value_str}")

            elif transform == 'map_roof_type' and value_mapping:
                # Transform value using mapping
                mapped_value = value_mapping.get(jotform_value, jotform_value)
                csd_data[csd_field] = mapped_value

            elif transform == 'map_manufacturer' and value_mapping:
                # Manufacturer goes to notes if not Simpson/USP
                if value_mapping.get(jotform_value) == 'NOTES':
                    composite_notes.append(f"Preferred Manufacturer: {jotform_value}")

            elif transform == 'map_to_joist_fields':
                # Store for later dynamic field handling
                csd_data['_joist_depth_preference'] = jotform_value

            elif transform == 'upload_file':
                # Store file URL for later processing
                csd_data['_file_attachments'] = jotform_value

            else:
                # Direct mapping
                csd_data[csd_field] = jotform_value

        # Combine composite notes
        if composite_notes:
            template = self.field_mapping.get(
                'composite_notes_template',
                '=== SUBMISSION DETAILS ===\n{notes_content}'
            )
            notes_content = '\n'.join(composite_notes)
            csd_data['_composite_notes'] = template.format(notes_content=notes_content)

        return csd_data

    def _get_aspnet_form_state(self) -> Dict[str, str]:
        """
        Get ASP.NET form state fields (__VIEWSTATE, __EVENTVALIDATION, etc.)
        These are required for ASP.NET forms to work properly

        Returns:
            Dictionary with ASP.NET state fields
        """
        try:
            response = self.session.get(self.csd_url, timeout=self.timeout)
            response.raise_for_status()

            # Parse HTML to extract form state
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')

            state_fields = {}

            # Get common ASP.NET form fields
            for field_name in ['__VIEWSTATE', '__VIEWSTATEGENERATOR', '__EVENTVALIDATION', '__EVENTTARGET', '__EVENTARGUMENT']:
                field = soup.find('input', {'name': field_name})
                if field:
                    state_fields[field_name] = field.get('value', '')

            return state_fields

        except Exception as e:
            logger.error(f"Error getting ASP.NET form state: {str(e)}")
            return {}

    def submit_to_csd(self, jotform_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit data to CSD Portal

        Args:
            jotform_data: Raw JotForm submission data

        Returns:
            Dictionary with success status and details:
            {
                'success': bool,
                'confirmation_number': str (if successful),
                'error': str (if failed)
            }
        """
        try:
            logger.info("Starting CSD Portal submission")

            # Map JotForm fields to CSD fields
            csd_data = self._map_jotform_to_csd(jotform_data)

            # Get ASP.NET form state
            aspnet_state = self._get_aspnet_form_state()

            # Build form data
            form_data = {**aspnet_state}

            # Add mapped data
            for field, value in csd_data.items():
                if not field.startswith('_'):  # Skip internal fields
                    form_data[field] = value

            # Add composite notes to appropriate field
            # TODO: Determine which field on CSD form is for special instructions
            if '_composite_notes' in csd_data:
                # This needs to be mapped to the correct notes field in CSD Portal
                # For now, we'll log it
                logger.info(f"Composite notes: {csd_data['_composite_notes']}")

            # Handle required CSD fields
            # Project Name is required by CSD
            if 'ctl00_cphBody_txtProjectName' not in form_data:
                # Try to construct from available data
                builder = form_data.get('ctl00_cphBody_txtBuilderName', 'Unknown')
                plan = form_data.get('ctl00_cphBody_txtPlanName', 'Project')
                form_data['ctl00_cphBody_txtProjectName'] = f"{builder} - {plan}"

            # Province is required
            if 'ctl00_cphBody_ddlProvince' not in form_data:
                # Default to GA (Georgia) for Atlanta market
                form_data['ctl00_cphBody_ddlProvince'] = 'GA'

            logger.debug(f"Form data prepared: {len(form_data)} fields")

            # Submit form
            response = self.session.post(
                self.csd_url,
                data=form_data,
                timeout=self.timeout,
                allow_redirects=True
            )

            response.raise_for_status()

            # Check for success indicators in response
            # This will depend on how CSD Portal indicates success
            if 'thank you' in response.text.lower() or 'success' in response.text.lower():
                logger.info("CSD Portal submission successful")
                return {
                    'success': True,
                    'confirmation_number': self._extract_confirmation_number(response.text)
                }
            else:
                # Check for error messages
                error_msg = self._extract_error_message(response.text)
                if error_msg:
                    logger.error(f"CSD Portal returned error: {error_msg}")
                    return {
                        'success': False,
                        'error': error_msg
                    }
                else:
                    logger.warning("CSD Portal response unclear - may need manual verification")
                    return {
                        'success': True,
                        'confirmation_number': 'VERIFY_MANUALLY'
                    }

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error submitting to CSD Portal: {str(e)}")
            return {
                'success': False,
                'error': f"Network error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error submitting to CSD Portal: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            }

    def _extract_confirmation_number(self, html: str) -> Optional[str]:
        """
        Extract confirmation number from CSD Portal response

        Args:
            html: Response HTML from CSD Portal

        Returns:
            Confirmation number if found, None otherwise
        """
        # TODO: Implement based on actual CSD Portal response
        # This will depend on how CSD Portal provides confirmation
        return None

    def _extract_error_message(self, html: str) -> Optional[str]:
        """
        Extract error message from CSD Portal response

        Args:
            html: Response HTML from CSD Portal

        Returns:
            Error message if found, None otherwise
        """
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')

            # Look for common error indicators
            error_elements = soup.find_all(class_=['error', 'alert', 'validation-summary'])
            if error_elements:
                return error_elements[0].get_text(strip=True)

            return None
        except Exception:
            return None

    def test_connection(self) -> bool:
        """
        Test connection to CSD Portal

        Returns:
            True if connection successful, False otherwise
        """
        try:
            response = self.session.get(self.csd_url, timeout=self.timeout)
            response.raise_for_status()
            logger.info("CSD Portal connection test successful")
            return True
        except Exception as e:
            logger.error(f"CSD Portal connection test failed: {str(e)}")
            return False
