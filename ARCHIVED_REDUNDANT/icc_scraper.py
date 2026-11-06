"""
ICC Website Scraper
Scrapes the ICC evidence submission form to understand field requirements
"""
import requests
from bs4 import BeautifulSoup
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class ICCFormScraper:
    def __init__(self):
        self.url = "https://otplink.icc-cpi.int/"
        self.form_fields = {}
        
    def setup_driver(self):
        """Setup Chrome WebDriver with options (works with Brave browser too)"""
        chrome_options = Options()
        # Don't use headless for initial testing so we can see what's happening
        # chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        
        # Try to find Brave browser first, then fall back to Chrome
        brave_paths = [
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
            os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe")
        ]
        
        brave_path = None
        for path in brave_paths:
            if os.path.exists(path):
                brave_path = path
                break
        
        if brave_path:
            chrome_options.binary_location = brave_path
            print(f"Using Brave browser at: {brave_path}")
        else:
            print("Brave browser not found, using default Chrome")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        return driver
        
    def scrape_form_structure(self):
        """Scrape the ICC form to understand its structure"""
        driver = self.setup_driver()
        
        try:
            print("Loading ICC website...")
            driver.get(self.url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Wait a bit more for dynamic content
            time.sleep(3)
            
            # Find all form elements
            forms = driver.find_elements(By.TAG_NAME, "form")
            print(f"Found {len(forms)} forms on the page")
            
            # Look for input fields, textareas, selects
            inputs = driver.find_elements(By.TAG_NAME, "input")
            textareas = driver.find_elements(By.TAG_NAME, "textarea")
            selects = driver.find_elements(By.TAG_NAME, "select")
            buttons = driver.find_elements(By.TAG_NAME, "button")
            
            print(f"Found {len(inputs)} input fields")
            print(f"Found {len(textareas)} textarea fields")
            print(f"Found {len(selects)} select fields")
            print(f"Found {len(buttons)} buttons")
            
            # Extract field information
            fields = []
            
            for input_elem in inputs:
                field_info = {
                    'type': 'input',
                    'input_type': input_elem.get_attribute('type'),
                    'name': input_elem.get_attribute('name'),
                    'id': input_elem.get_attribute('id'),
                    'placeholder': input_elem.get_attribute('placeholder'),
                    'required': input_elem.get_attribute('required'),
                    'class': input_elem.get_attribute('class')
                }
                fields.append(field_info)
                
            for textarea in textareas:
                field_info = {
                    'type': 'textarea',
                    'name': textarea.get_attribute('name'),
                    'id': textarea.get_attribute('id'),
                    'placeholder': textarea.get_attribute('placeholder'),
                    'required': textarea.get_attribute('required'),
                    'class': textarea.get_attribute('class')
                }
                fields.append(field_info)
                
            for select in selects:
                options = select.find_elements(By.TAG_NAME, "option")
                option_values = [opt.get_attribute('value') for opt in options]
                option_texts = [opt.text for opt in options]
                
                field_info = {
                    'type': 'select',
                    'name': select.get_attribute('name'),
                    'id': select.get_attribute('id'),
                    'required': select.get_attribute('required'),
                    'class': select.get_attribute('class'),
                    'options': list(zip(option_values, option_texts))                }
                fields.append(field_info)
            
            # Save the form structure
            self.form_fields = {
                'url': self.url,
                'fields': fields,
                'total_inputs': len(inputs),
                'total_textareas': len(textareas),
                'total_selects': len(selects),
                'buttons': [btn.get_attribute('type') for btn in buttons]
            }
            
            return self.form_fields
            
        except Exception as e:
            print(f"Error scraping form: {str(e)}")
            return None
            
        finally:
            driver.quit()
    
    def save_form_structure(self, filename="icc_form_structure.json"):
        """Save the scraped form structure to a JSON file"""
        if self.form_fields:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.form_fields, f, indent=2, ensure_ascii=False)
            print(f"Form structure saved to {filename}")
        else:
            print("No form structure to save")

if __name__ == "__main__":
    scraper = ICCFormScraper()
    form_data = scraper.scrape_form_structure()
    
    if form_data:
        scraper.save_form_structure()
        print("\\nForm Analysis Complete!")
        print(f"Total fields found: {len(form_data['fields'])}")
        
        # Print field summary
        for i, field in enumerate(form_data['fields'][:10]):  # Show first 10 fields
            print(f"{i+1}. {field['type']} - {field.get('name', 'No name')} - {field.get('placeholder', 'No placeholder')}")
    else:
        print("Failed to scrape form structure")
