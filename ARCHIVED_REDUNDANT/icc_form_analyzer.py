"""
ICC Form Analyzer
Analyzes the ICC form structure using requests and creates a manual mapping
"""
import requests
import json
from bs4 import BeautifulSoup

def analyze_icc_page():
    """Analyze the ICC page structure using requests"""
    url = "https://otplink.icc-cpi.int/"
    
    try:
        print("Fetching ICC website...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        print(f"Status Code: {response.status_code}")
        print(f"Content Length: {len(response.text)}")
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find forms
        forms = soup.find_all('form')
        print(f"Found {len(forms)} forms")
        
        # Find input fields
        inputs = soup.find_all('input')
        textareas = soup.find_all('textarea')
        selects = soup.find_all('select')
        
        print(f"Found {len(inputs)} input fields")
        print(f"Found {len(textareas)} textarea fields") 
        print(f"Found {len(selects)} select fields")
        
        # Create form structure
        form_structure = {
            'url': url,
            'forms_found': len(forms),
            'fields': []
        }
        
        # Process inputs
        for inp in inputs:
            field = {
                'type': 'input',
                'input_type': inp.get('type', 'text'),
                'name': inp.get('name'),
                'id': inp.get('id'),
                'placeholder': inp.get('placeholder'),
                'required': inp.get('required') is not None,
                'class': inp.get('class')
            }
            form_structure['fields'].append(field)
        
        # Process textareas
        for textarea in textareas:
            field = {
                'type': 'textarea',
                'name': textarea.get('name'),
                'id': textarea.get('id'),
                'placeholder': textarea.get('placeholder'),
                'required': textarea.get('required') is not None,
                'class': textarea.get('class')
            }
            form_structure['fields'].append(field)
        
        # Process selects
        for select in selects:
            options = select.find_all('option')
            field = {
                'type': 'select',
                'name': select.get('name'),
                'id': select.get('id'),
                'required': select.get('required') is not None,
                'class': select.get('class'),
                'options': [(opt.get('value'), opt.text.strip()) for opt in options]
            }
            form_structure['fields'].append(field)
        
        # Save to file
        with open('icc_form_structure.json', 'w', encoding='utf-8') as f:
            json.dump(form_structure, f, indent=2, ensure_ascii=False)
        
        print("Form structure saved to icc_form_structure.json")
        
        # Print summary
        print("\nForm Field Summary:")
        for i, field in enumerate(form_structure['fields'][:10]):
            print(f"{i+1}. {field['type']} - {field.get('name', 'No name')} - {field.get('placeholder', 'No placeholder')}")
        
        return form_structure
        
    except Exception as e:
        print(f"Error analyzing page: {str(e)}")
        return None

def create_manual_form_mapping():
    """Create a manual form mapping based on typical ICC forms"""
    manual_mapping = {
        'url': 'https://otplink.icc-cpi.int/',
        'description': 'Manual mapping of ICC form fields based on common patterns',
        'fields': [
            {
                'name': 'incident_date',
                'label': 'Date of Incident',
                'type': 'date',
                'required': True,
                'default_value': '2025-06-17'  # Today's date
            },
            {
                'name': 'incident_time',
                'label': 'Time of Incident',
                'type': 'time',
                'required': True,
                'default_value': '14:00'  # 2 PM
            },
            {
                'name': 'incident_location',
                'label': 'Location of Incident',
                'type': 'text',
                'required': True,
                'default_value': 'CBD, Nairobi, Kenya'
            },
            {
                'name': 'incident_description',
                'label': 'Description of Incident',
                'type': 'textarea',
                'required': True,
                'placeholder': 'Describe what happened...'
            },
            {
                'name': 'evidence_type',
                'label': 'Type of Evidence',
                'type': 'select',
                'required': True,
                'options': [
                    ('photo', 'Photograph'),
                    ('video', 'Video Recording'),
                    ('document', 'Document'),
                    ('audio', 'Audio Recording'),
                    ('witness_statement', 'Witness Statement')
                ]
            },
            {
                'name': 'evidence_files',
                'label': 'Evidence Files',
                'type': 'file',
                'required': True,
                'multiple': True
            },
            {
                'name': 'submitter_name',
                'label': 'Your Name (Optional)',
                'type': 'text',
                'required': False
            },
            {
                'name': 'submitter_email',
                'label': 'Your Email (Optional)',
                'type': 'email',
                'required': False
            },
            {
                'name': 'submitter_phone',
                'label': 'Your Phone (Optional)',
                'type': 'tel',
                'required': False
            },
            {
                'name': 'witness_name',
                'label': 'Witness Name (If any)',
                'type': 'text',
                'required': False
            },
            {
                'name': 'witness_contact',
                'label': 'Witness Contact',
                'type': 'text',
                'required': False
            },
            {
                'name': 'additional_info',
                'label': 'Additional Information',
                'type': 'textarea',
                'required': False,
                'placeholder': 'Any additional relevant information...'
            }
        ]
    }
    
    # Save manual mapping
    with open('icc_manual_form_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(manual_mapping, f, indent=2, ensure_ascii=False)
    
    print("Manual form mapping saved to icc_manual_form_mapping.json")
    return manual_mapping

if __name__ == "__main__":
    print("=== ICC Form Analysis ===")
    
    # Try to analyze the actual page
    form_data = analyze_icc_page()
    
    # Always create manual mapping as fallback
    print("\n=== Creating Manual Form Mapping ===")
    manual_data = create_manual_form_mapping()
    
    if form_data:
        print(f"\nAnalysis complete! Found {len(form_data['fields'])} fields on the actual page.")
    else:
        print("\nCouldn't analyze actual page, but manual mapping is ready.")
    
    print("You can now run the Streamlit app!")
