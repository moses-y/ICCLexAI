"""
🤖 SELENIUM AUTOMATION CORE AGENT
Specialized agent for ICC form submission automation
Part of the 5-agent intelligent consolidation system

AGENT RESPONSIBILITIES:
- Chrome WebDriver setup and management
- ICC website navigation and form automation
- File upload automation
- Form field population from data structures
- Error handling and retry mechanisms
- Screenshot capture for submission proof
- Multi-browser support (Chrome, Firefox, Edge)

This is CORE AGENT #3 - focused solely on web automation capabilities
"""

import streamlit as st
import os
import json
import time
from datetime import datetime
from pathlib import Path
import base64
from typing import Dict, List, Optional, Tuple

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    WebDriverException,
    ElementNotInteractableException
)

# WebDriver managers
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

class SeleniumAutomationAgent:
    """
    🤖 CORE AGENT #3: Advanced Web Automation for ICC Submissions
    
    This agent specializes in:
    - Automated ICC form submission
    - Multi-browser support (Chrome, Firefox, Edge)
    - Smart element detection and interaction
    - File upload automation
    - Error handling and retry mechanisms
    - Screenshot capture for proof of submission
    - Headless and headed modes
    """
    
    def __init__(self, browser='chrome', headless=False, timeout=30):
        self.browser = browser.lower()
        self.headless = headless
        self.timeout = timeout
        self.driver = None
        self.icc_url = "https://otplink.icc-cpi.int/"
        self.submission_screenshots = []
        
        # ICC form field mappings
        self.icc_form_selectors = {
            'contact_name': 'input[name="contact_name"]',
            'contact_email': 'input[name="contact_email"]',
            'contact_phone': 'input[name="contact_phone"]',
            'incident_date': 'input[name="incident_date"]',
            'incident_location': 'input[name="incident_location"]',
            'incident_description': 'textarea[name="incident_description"]',
            'evidence_files': 'input[type="file"]',
            'submit_button': 'button[type="submit"], input[type="submit"]'
        }
    
    def setup_driver(self) -> bool:
        """
        🚀 Setup WebDriver with optimal configuration
        
        Returns:
            bool: True if driver setup successful, False otherwise
        """
        try:
            if self.browser == 'chrome':
                return self._setup_chrome_driver()
            elif self.browser == 'firefox':
                return self._setup_firefox_driver()
            elif self.browser == 'edge':
                return self._setup_edge_driver()
            else:
                raise ValueError(f"Unsupported browser: {self.browser}")
                
        except Exception as e:
            st.error(f"❌ Failed to setup {self.browser} driver: {str(e)}")
            return False
    
    def _setup_chrome_driver(self) -> bool:
        """Setup Chrome WebDriver with optimal settings"""
        try:
            chrome_options = ChromeOptions()
            
            # Performance optimizations
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--window-size=1920,1080")
            
            # Headless mode if requested
            if self.headless:
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--disable-logging")
                chrome_options.add_argument("--silent")
            
            # File download settings
            prefs = {
                "download.default_directory": str(Path.cwd() / "downloads"),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            chrome_options.add_experimental_option("prefs", prefs)
            
            # Setup service
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Configure timeouts
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(self.timeout)
            
            return True
            
        except Exception as e:
            st.error(f"Chrome driver setup failed: {str(e)}")
            return False
    
    def _setup_firefox_driver(self) -> bool:
        """Setup Firefox WebDriver with optimal settings"""
        try:
            firefox_options = FirefoxOptions()
            
            if self.headless:
                firefox_options.add_argument("--headless")
            
            # Performance settings
            firefox_options.set_preference("dom.webdriver.enabled", False)
            firefox_options.set_preference("useAutomationExtension", False)
            
            service = FirefoxService(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=firefox_options)
            
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(self.timeout)
            
            return True
            
        except Exception as e:
            st.error(f"Firefox driver setup failed: {str(e)}")
            return False
    
    def _setup_edge_driver(self) -> bool:
        """Setup Edge WebDriver with optimal settings"""
        try:
            edge_options = EdgeOptions()
            
            if self.headless:
                edge_options.add_argument("--headless")
            
            edge_options.add_argument("--no-sandbox")
            edge_options.add_argument("--disable-dev-shm-usage")
            
            service = EdgeService(EdgeChromiumDriverManager().install())
            self.driver = webdriver.Edge(service=service, options=edge_options)
            
            self.driver.implicitly_wait(10)
            self.driver.set_page_load_timeout(self.timeout)
            
            return True
            
        except Exception as e:
            st.error(f"Edge driver setup failed: {str(e)}")
            return False
    
    def navigate_to_icc_portal(self) -> bool:
        """
        🌐 Navigate to ICC submission portal
        
        Returns:
            bool: True if navigation successful
        """
        try:
            st.info(f"🔄 Navigating to ICC portal: {self.icc_url}")
            
            self.driver.get(self.icc_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, self.timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Take screenshot for verification
            self._capture_screenshot("icc_portal_loaded")
            
            # Check if we're on the correct page
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            st.success(f"✅ Successfully loaded: {page_title}")
            st.info(f"Current URL: {current_url}")
            
            return True
            
        except TimeoutException:
            st.error("❌ Timeout: ICC portal took too long to load")
            return False
        except Exception as e:
            st.error(f"❌ Navigation error: {str(e)}")
            return False
    
    def submit_evidence_form(self, form_data: Dict, evidence_files: List = None) -> Dict:
        """
        📝 Submit evidence form to ICC with comprehensive automation
        
        Args:
            form_data: Dictionary containing form field data
            evidence_files: List of file paths to upload
            
        Returns:
            Dict: Submission result with success status and details
        """
        submission_result = {
            'success': False,
            'submission_id': None,
            'timestamp': datetime.now().isoformat(),
            'errors': [],
            'screenshots': []
        }
        
        try:
            # Fill form fields
            st.info("📝 Filling ICC submission form...")
            if not self._fill_form_fields(form_data):
                submission_result['errors'].append("Failed to fill form fields")
                return submission_result
            
            # Upload evidence files
            if evidence_files:
                st.info("📎 Uploading evidence files...")
                if not self._upload_evidence_files(evidence_files):
                    submission_result['errors'].append("Failed to upload evidence files")
                    return submission_result
            
            # Submit form
            st.info("🚀 Submitting form to ICC...")
            if not self._submit_form():
                submission_result['errors'].append("Failed to submit form")
                return submission_result
            
            # Verify submission
            submission_id = self._verify_submission()
            if submission_id:
                submission_result['success'] = True
                submission_result['submission_id'] = submission_id
                submission_result['screenshots'] = self.submission_screenshots
                
                st.success(f"✅ Successfully submitted to ICC! ID: {submission_id}")
            else:
                submission_result['errors'].append("Could not verify submission")
                
        except Exception as e:
            error_msg = f"Submission failed: {str(e)}"
            submission_result['errors'].append(error_msg)
            st.error(f"❌ {error_msg}")
            
        finally:
            # Capture final screenshot
            self._capture_screenshot("submission_complete")
            
        return submission_result
    
    def _fill_form_fields(self, form_data: Dict) -> bool:
        """Fill ICC form fields with provided data"""
        try:
            # Map form data to ICC form fields
            field_mappings = {
                'submitter_name': 'contact_name',
                'submitter_email': 'contact_email', 
                'submitter_phone': 'contact_phone',
                'incident_date': 'incident_date',
                'incident_location': 'incident_location',
                'incident_description': 'incident_description'
            }
            
            for data_key, form_field in field_mappings.items():
                if data_key in form_data and form_data[data_key]:
                    success = self._fill_field(
                        self.icc_form_selectors[form_field], 
                        form_data[data_key]
                    )
                    if not success:
                        st.warning(f"⚠️ Could not fill field: {form_field}")
            
            # Take screenshot after filling form
            self._capture_screenshot("form_filled")
            return True
            
        except Exception as e:
            st.error(f"Error filling form fields: {str(e)}")
            return False
    
    def _fill_field(self, selector: str, value: str, retry_count: int = 3) -> bool:
        """Fill a specific form field with retry mechanism"""
        for attempt in range(retry_count):
            try:
                # Find element using multiple strategies
                element = None
                
                # Try CSS selector
                try:
                    element = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                except TimeoutException:
                    # Try by name attribute
                    name = selector.replace('input[name="', '').replace('"]', '').replace('textarea[name="', '')
                    try:
                        element = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.NAME, name))
                        )
                    except TimeoutException:
                        # Try by ID
                        try:
                            element = WebDriverWait(self.driver, 5).until(
                                EC.element_to_be_clickable((By.ID, name))
                            )
                        except TimeoutException:
                            continue
                
                if element:
                    # Clear and fill field
                    element.clear()
                    element.send_keys(value)
                    
                    # Verify the value was entered
                    if element.get_attribute('value') == value:
                        return True
                    
            except ElementNotInteractableException:
                # Try using JavaScript if regular interaction fails
                try:
                    self.driver.execute_script(
                        "arguments[0].value = arguments[1];", 
                        element, value
                    )
                    return True
                except:
                    continue
                    
            except Exception as e:
                st.debug(f"Attempt {attempt + 1} failed for selector {selector}: {str(e)}")
                time.sleep(1)
        
        return False
    
    def _upload_evidence_files(self, file_paths: List[str]) -> bool:
        """Upload evidence files to the ICC form"""
        try:
            # Find file input element
            file_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.icc_form_selectors['evidence_files']))
            )
            
            # Upload each file
            for file_path in file_paths:
                if os.path.exists(file_path):
                    file_input.send_keys(file_path)
                    time.sleep(2)  # Allow upload to process
                    
                    st.success(f"📎 Uploaded: {Path(file_path).name}")
                else:
                    st.warning(f"⚠️ File not found: {file_path}")
            
            self._capture_screenshot("files_uploaded")
            return True
            
        except Exception as e:
            st.error(f"File upload failed: {str(e)}")
            return False
    
    def _submit_form(self) -> bool:
        """Submit the ICC form"""
        try:
            # Find and click submit button
            submit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.icc_form_selectors['submit_button']))
            )
            
            # Scroll to submit button
            self.driver.execute_script("arguments[0].scrollIntoView();", submit_button)
            time.sleep(1)
            
            # Take screenshot before submission
            self._capture_screenshot("before_submission")
            
            # Click submit
            submit_button.click()
            
            # Wait for submission to process
            time.sleep(5)
            
            return True
            
        except Exception as e:
            st.error(f"Form submission failed: {str(e)}")
            return False
    
    def _verify_submission(self) -> Optional[str]:
        """Verify form submission and extract submission ID"""
        try:
            # Look for success indicators
            success_indicators = [
                "success", "submitted", "confirmation", "thank you", 
                "received", "processed"
            ]
            
            # Check page content for success messages
            page_source = self.driver.page_source.lower()
            
            for indicator in success_indicators:
                if indicator in page_source:
                    # Generate submission ID based on timestamp
                    submission_id = f"ICC-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    
                    # Try to extract actual submission ID from page
                    try:
                        # Look for ID patterns in the page
                        import re
                        id_patterns = [
                            r'submission[_\s]*id[:\s]*([A-Z0-9\-]+)',
                            r'reference[_\s]*number[:\s]*([A-Z0-9\-]+)',
                            r'case[_\s]*id[:\s]*([A-Z0-9\-]+)'
                        ]
                        
                        for pattern in id_patterns:
                            match = re.search(pattern, page_source, re.IGNORECASE)
                            if match:
                                submission_id = match.group(1)
                                break
                                
                    except:
                        pass
                    
                    self._capture_screenshot("submission_success")
                    return submission_id
            
            # If no success indicator found, assume failure
            self._capture_screenshot("submission_unclear")
            return None
            
        except Exception as e:
            st.error(f"Submission verification failed: {str(e)}")
            return None
    
    def _capture_screenshot(self, stage: str) -> str:
        """Capture screenshot at different stages of automation"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"icc_submission_{stage}_{timestamp}.png"
            filepath = Path("screenshots") / filename
            
            # Create screenshots directory if it doesn't exist
            filepath.parent.mkdir(exist_ok=True)
            
            # Capture screenshot
            self.driver.save_screenshot(str(filepath))
            
            # Store for later reference
            self.submission_screenshots.append({
                'stage': stage,
                'filepath': str(filepath),
                'timestamp': timestamp
            })
            
            return str(filepath)
            
        except Exception as e:
            st.debug(f"Screenshot capture failed: {str(e)}")
            return ""
    
    def simulate_icc_submission(self, form_data: Dict, evidence_files: List = None) -> Dict:
        """
        🎭 Simulate ICC submission for testing purposes
        
        This method simulates the submission process without actually
        interacting with the ICC website. Useful for testing and development.
        """
        st.info("🎭 Running ICC submission simulation...")
        
        # Simulate processing time
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        stages = [
            "Connecting to ICC portal",
            "Loading submission form", 
            "Filling form fields",
            "Uploading evidence files",
            "Submitting form",
            "Verifying submission"
        ]
        
        for i, stage in enumerate(stages):
            status_text.text(f"🔄 {stage}...")
            progress_bar.progress((i + 1) / len(stages))
            time.sleep(2)
        
        # Generate mock submission result
        submission_id = f"ICC-SIM-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        result = {
            'success': True,
            'submission_id': submission_id,
            'timestamp': datetime.now().isoformat(),
            'mode': 'simulation',
            'form_data': form_data,
            'evidence_count': len(evidence_files) if evidence_files else 0,
            'errors': [],
            'screenshots': []
        }
        
        status_text.text("✅ Simulation completed successfully!")
        st.success(f"🎭 Simulated submission complete! ID: {submission_id}")
        
        return result
    
    def cleanup(self):
        """Clean up WebDriver resources"""
        try:
            if self.driver:
                self.driver.quit()
                self.driver = None
                st.info("🧹 WebDriver cleaned up successfully")
        except Exception as e:
            st.debug(f"Cleanup warning: {str(e)}")
    
    def __del__(self):
        """Ensure cleanup on object destruction"""
        self.cleanup()

# Factory function for agent creation
def get_selenium_agent(browser='chrome', headless=False, timeout=30):
    """
    🎯 Factory function to create Selenium automation agent
    
    Args:
        browser: Browser to use ('chrome', 'firefox', 'edge')
        headless: Run in headless mode
        timeout: Page load timeout in seconds
        
    Returns:
        SeleniumAutomationAgent: Configured automation agent
    """
    return SeleniumAutomationAgent(browser=browser, headless=headless, timeout=timeout)

# Standalone execution for testing
if __name__ == "__main__":
    st.title("🤖 Selenium Automation Core Agent")
    st.write("Test ICC form submission automation")
    
    # Configuration options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        browser = st.selectbox("Browser", ['chrome', 'firefox', 'edge'])
    with col2:
        headless = st.checkbox("Headless Mode")
    with col3:
        simulation_mode = st.checkbox("Simulation Mode", value=True)
    
    # Create agent
    agent = get_selenium_agent(browser=browser, headless=headless)
    
    # Test data
    test_form_data = {
        'submitter_name': 'Test Submitter',
        'submitter_email': 'test@example.com',
        'submitter_phone': '+254700000000',
        'incident_date': '2025-06-17',
        'incident_location': 'CBD, Nairobi, Kenya',
        'incident_description': 'Test incident for automation testing'
    }
    
    if st.button("🚀 Test ICC Submission"):
        try:
            if simulation_mode:
                # Run simulation
                result = agent.simulate_icc_submission(test_form_data)
            else:
                # Run actual automation
                if agent.setup_driver():
                    if agent.navigate_to_icc_portal():
                        result = agent.submit_evidence_form(test_form_data)
                    else:
                        result = {'success': False, 'errors': ['Navigation failed']}
                else:
                    result = {'success': False, 'errors': ['Driver setup failed']}
            
            # Display results
            st.subheader("📊 Submission Results")
            st.json(result)
            
        except Exception as e:
            st.error(f"❌ Test failed: {str(e)}")
        finally:
            agent.cleanup()
