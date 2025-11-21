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

        submission_id = jotform_data.get('submission_id', 'unknown')

        for mapping in self.field_mapping.get('mappings', []):
            jotform_field = mapping['jotform_field']
            csd_field = mapping['csd_field']
            transform = mapping.get('transform')
            value_mapping = mapping.get('value_mapping', {})
            skip_if_empty = mapping.get('skip_if_empty', False)

            # Get value from JotForm data
            jotform_value = jotform_data.get(jotform_field)

            # Skip if no value
            if jotform_value is None:
                continue

            # Skip if empty and skip_if_empty is True
            if skip_if_empty and self._is_empty_value(jotform_value):
                continue

            # Handle different transformation types
            if transform == 'append_to_notes' or csd_field == 'COMPOSITE_NOTES':
                # Add to composite notes
                label = mapping['jotform_label']
                if isinstance(jotform_value, list):
                    value_str = ', '.join(str(v) for v in jotform_value if v)
                else:
                    value_str = str(jotform_value)

                if value_str.strip():  # Only add if not empty after conversion
                    composite_notes.append(f"{label}: {value_str}")

            elif transform == 'file_links_to_notes':
                # Handle file URLs - add links to composite notes
                file_links = self._extract_file_links(jotform_value)
                if file_links:
                    composite_notes.append(f"\n{mapping['jotform_label']}:")
                    for idx, link in enumerate(file_links, 1):
                        composite_notes.append(f"  File {idx}: {link}")

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
            csd_data['_composite_notes'] = template.format(
                notes_content=notes_content,
                submission_id=submission_id
            )

        return csd_data

    def _is_empty_value(self, value):
        """Check if a value is considered empty"""
        if value is None:
            return True
        if isinstance(value, str) and not value.strip():
            return True
        if isinstance(value, list) and len(value) == 0:
            return True
        return False

    def _extract_file_links(self, file_value):
        """Extract file URLs from JotForm file field"""
        if not file_value:
            return []

        file_links = []

        # JotForm can send file data in different formats
        if isinstance(file_value, str):
            # Single file URL
            if file_value.startswith('http'):
                file_links.append(file_value)
        elif isinstance(file_value, list):
            # Multiple files
            for item in file_value:
                if isinstance(item, str) and item.startswith('http'):
                    file_links.append(item)
                elif isinstance(item, dict) and 'url' in item:
                    file_links.append(item['url'])

        return file_links

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
        Submit data to CSD Portal using Selenium browser automation

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
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options
        from selenium.common.exceptions import TimeoutException, WebDriverException

        driver = None
        try:
            logger.info("Starting CSD Portal submission with Selenium")

            # Map JotForm fields to CSD fields
            csd_data = self._map_jotform_to_csd(jotform_data)

            # Calculate due date if enabled
            due_date_config = self.field_mapping.get('due_date_calculation', {})
            if due_date_config.get('enabled', False):
                from datetime import datetime, timedelta
                days_to_add = due_date_config.get('days_from_submission', 14)
                due_date = datetime.now() + timedelta(days=days_to_add)
                csd_data['ctl00_cphBody_txtDueDate'] = due_date.strftime('%m/%d/%Y')
                logger.info(f"Calculated due date: {csd_data['ctl00_cphBody_txtDueDate']}")

            # Configure Chrome for headless operation
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')

            logger.info("Launching headless Chrome browser")
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(30)

            # Open CSD Portal form
            logger.info(f"Opening CSD Portal: {self.csd_url}")
            driver.get(self.csd_url)

            # Wait for form to load
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.ID, "ctl00_cphBody_txtProjectName")))
            logger.info("Form loaded successfully")

            # Fill text fields
            logger.info("Filling form fields...")

            # Builder Name
            if 'ctl00_cphBody_txtBuilderName' in csd_data:
                elem = driver.find_element(By.ID, "ctl00_cphBody_txtBuilderName")
                elem.clear()
                elem.send_keys(csd_data['ctl00_cphBody_txtBuilderName'])
                logger.info(f"Filled Builder Name: {csd_data['ctl00_cphBody_txtBuilderName']}")

            # Project Name (required)
            if 'ctl00_cphBody_txtProjectName' in csd_data:
                elem = driver.find_element(By.ID, "ctl00_cphBody_txtProjectName")
                elem.clear()
                elem.send_keys(csd_data['ctl00_cphBody_txtProjectName'])
                logger.info(f"Filled Project Name: {csd_data['ctl00_cphBody_txtProjectName']}")

            # Plan Name
            if 'ctl00_cphBody_txtPlanName' in csd_data:
                elem = driver.find_element(By.ID, "ctl00_cphBody_txtPlanName")
                elem.clear()
                elem.send_keys(csd_data['ctl00_cphBody_txtPlanName'])
                logger.info(f"Filled Plan Name: {csd_data['ctl00_cphBody_txtPlanName']}")

            # Salesman/Contact Name (optional - may not exist on form)
            if 'ctl00_cphBody_txtName' in csd_data:
                try:
                    elem = driver.find_element(By.ID, "ctl00_cphBody_txtName")
                    elem.clear()
                    elem.send_keys(csd_data['ctl00_cphBody_txtName'])
                    logger.info(f"Filled Contact Name: {csd_data['ctl00_cphBody_txtName']}")
                except:
                    logger.warning("Contact Name field not found on form - skipping")

            # Due Date (optional)
            if 'ctl00_cphBody_txtDueDate' in csd_data:
                try:
                    elem = driver.find_element(By.ID, "ctl00_cphBody_txtDueDate")
                    elem.clear()
                    elem.send_keys(csd_data['ctl00_cphBody_txtDueDate'])
                    logger.info(f"Filled Due Date: {csd_data['ctl00_cphBody_txtDueDate']}")
                except:
                    logger.warning("Due Date field not found or not fillable - skipping")

            # Province/State (required)
            # Note: CSD Portal uses numeric IDs for states, not abbreviations
            # Georgia = 24, North Carolina = 38, etc.
            from selenium.webdriver.support.ui import Select
            elem = driver.find_element(By.ID, "ctl00_cphBody_ddlProvince")
            select = Select(elem)

            if 'ctl00_cphBody_ddlProvince' in csd_data:
                province_value = csd_data['ctl00_cphBody_ddlProvince']
                select.select_by_value(province_value)
                logger.info(f"Selected Province: {province_value}")
            else:
                # Default to Georgia (ID: 24) for Atlanta market
                select.select_by_value('24')
                logger.info("Selected Province: Georgia (24) - default")

            # Special Instructions / Composite Notes
            if '_composite_notes' in csd_data:
                notes_content = csd_data['_composite_notes']
                # Note: This textarea has shortened ID (not full ctl00_cphBody prefix)
                elem = driver.find_element(By.ID, "txtProjectComments")
                elem.clear()
                elem.send_keys(notes_content)
                logger.info(f"Filled Special Instructions ({len(notes_content)} chars)")

            # Take screenshot before submit (for debugging)
            try:
                Path('logs').mkdir(exist_ok=True)
                driver.save_screenshot('logs/csd_before_submit.png')
                logger.info("Saved screenshot before submit")
            except Exception as e:
                logger.warning(f"Could not save screenshot: {str(e)}")

            # Submit form
            logger.info("Clicking submit button...")
            submit_button = driver.find_element(By.ID, "btnSubmit")
            submit_button.click()

            # Wait for response (either success page or error)
            time.sleep(3)  # Give it time to process

            # Check current URL for success redirect
            current_url = driver.current_url
            logger.info(f"After submit, URL: {current_url}")

            # Take screenshot after submit
            try:
                driver.save_screenshot('logs/csd_after_submit.png')
                logger.info("Saved screenshot after submit")
            except Exception as e:
                logger.warning(f"Could not save screenshot: {str(e)}")

            # Check page content for success/error messages
            page_source = driver.page_source
            page_lower = page_source.lower()

            if 'thank you' in page_lower or 'success' in page_lower or 'submitted' in page_lower:
                logger.info("CSD Portal submission appears successful!")
                return {
                    'success': True,
                    'confirmation_number': self._extract_confirmation_number(page_source)
                }
            elif 'error' in page_lower or 'invalid' in page_lower or 'required' in page_lower:
                error_msg = self._extract_error_message(page_source)
                logger.error(f"CSD Portal returned error: {error_msg}")
                return {
                    'success': False,
                    'error': error_msg or 'Validation error - check screenshots'
                }
            else:
                logger.warning("CSD Portal response unclear - check screenshots")
                return {
                    'success': True,
                    'confirmation_number': 'VERIFY_MANUALLY - check screenshots'
                }

        except TimeoutException as e:
            logger.error(f"Timeout waiting for CSD Portal: {str(e)}")
            return {
                'success': False,
                'error': f"Timeout: {str(e)}"
            }
        except WebDriverException as e:
            logger.error(f"Browser error submitting to CSD Portal: {str(e)}")
            return {
                'success': False,
                'error': f"Browser error: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Unexpected error submitting to CSD Portal: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}"
            }
        finally:
            # Always close the browser
            if driver:
                try:
                    driver.quit()
                    logger.info("Browser closed")
                except Exception as e:
                    logger.warning(f"Error closing browser: {str(e)}")

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

            # Look for ASP.NET validation messages
            errors = []

            # Check for validation summary
            validation_summary = soup.find(class_='validation-summary-errors')
            if validation_summary:
                errors.append(validation_summary.get_text(strip=True))

            # Check for field-level validators
            validators = soup.find_all('span', {'style': lambda x: x and 'color:Red' in x})
            for validator in validators:
                text = validator.get_text(strip=True)
                if text:
                    errors.append(text)

            # Check for any elements with "required" text
            if not errors and 'required' in html.lower():
                # Try to find specific required field messages
                required_spans = soup.find_all('span', string=lambda x: x and 'required' in x.lower())
                for span in required_spans[:3]:  # Limit to first 3
                    errors.append(span.get_text(strip=True))

            if errors:
                return '; '.join(errors[:5])  # Return first 5 errors

            return None
        except Exception as e:
            logger.error(f"Error parsing validation errors: {str(e)}")
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
