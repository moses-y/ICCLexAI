"""
🇰🇪 ICC EVIDENCE ANALYSIS SYSTEM TEST SUITE
Comprehensive testing for ALL ICC file types and validation workflow

TESTS:
🔹 File type validation for all ICC-supported formats
🔹 API endpoint functionality
🔹 Human-in-the-loop validation workflow
🔹 Case summary generation and editing
🔹 Final ICC submission process
"""

import requests
import json
import io
from datetime import datetime
from pathlib import Path
import tempfile
import os

class ICCSystemTester:
    """Comprehensive tester for ICC evidence analysis system"""
    
    def __init__(self, api_base_url="http://localhost:8001"):
        self.api_base_url = api_base_url
        self.test_files = {}
        self.session_id = None
        
    def create_test_files(self):
        """Create mock test files for all ICC-supported formats"""
        test_data = {
            # Document Evidence
            'witness_statement.pdf': b'%PDF-1.4\nMock PDF witness statement content...',
            'police_report.docx': b'PK\x03\x04Mock DOCX police report content...',
            'testimony.txt': b'Mock text testimony content describing incident...',
            
            # Image Evidence
            'incident_photo.jpg': b'\xff\xd8\xff\xe0Mock JPEG image data...',
            'scene_photo.png': b'\x89PNG\r\n\x1a\nMock PNG image data...',
            'evidence_photo.gif': b'GIF89aMock GIF image data...',
            
            # Video Evidence
            'incident_video.mp4': b'\x00\x00\x00\x18ftypMock MP4 video data...',
            'witness_video.avi': b'RIFF    AVI Mock AVI video data...',
            'phone_video.mov': b'\x00\x00\x00\x14ftypqtMock QuickTime data...',
            
            # Audio Evidence
            'witness_audio.mp3': b'ID3\x03\x00Mock MP3 audio data...',
            'incident_audio.wav': b'RIFF    WAVEfmt Mock WAV audio data...',
            'phone_call.m4a': b'\x00\x00\x00\x18ftypM4A Mock M4A audio data...',
            
            # Digital Evidence
            'metadata.json': b'{"timestamp": "2025-06-17T14:23:15", "location": "Nairobi"}',
            'communications.xml': b'<?xml version="1.0"?><messages>Mock XML data</messages>',
            'data_export.csv': b'timestamp,event,location\n2025-06-17,incident,nairobi',
            
            # Archive Evidence
            'evidence_bundle.zip': b'PK\x03\x04Mock ZIP archive content...',
            'backup_files.rar': b'Rar!\x1a\x07\x00Mock RAR archive content...',
            
            # Forensic Evidence (mock)
            'disk_image.dd': b'Mock disk image content for forensic analysis...',
            'evidence_dump.e01': b'Mock EnCase evidence file content...'
        }
        
        # Create temporary files
        for filename, content in test_data.items():
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=f'_{filename}')
            temp_file.write(content)
            temp_file.close()
            self.test_files[filename] = temp_file.name
        
        print(f"✅ Created {len(self.test_files)} test files")
    
    def test_api_health(self):
        """Test API health and basic functionality"""
        print("\n🔍 Testing API Health...")
        
        try:
            response = requests.get(f"{self.api_base_url}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ API Health: {health_data['status']}")
                print(f"   AI Services: {health_data['ai_services']}")
                return True
            else:
                print(f"❌ API Health Check Failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ API Connection Error: {e}")
            return False
    
    def test_supported_file_types(self):
        """Test supported file types endpoint"""
        print("\n📁 Testing Supported File Types...")
        
        try:
            response = requests.get(f"{self.api_base_url}/supported-file-types")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Total Supported Formats: {data['total_formats']}")
                
                for category, formats in data['supported_formats'].items():
                    print(f"   📂 {category.title()}: {len(formats)} formats")
                    print(f"      Max Size: {data['max_sizes_mb'][category]:.0f}MB")
                
                return True
            else:
                print(f"❌ File Types Test Failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ File Types Error: {e}")
            return False
    
    def test_file_validation(self):
        """Test file validation for all types"""
        print("\n✅ Testing File Validation...")
        
        validation_results = {}
        
        for filename, filepath in self.test_files.items():
            try:
                with open(filepath, 'rb') as f:
                    files = {'file': (filename, f, 'application/octet-stream')}
                    response = requests.post(f"{self.api_base_url}/validate-file", files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    validation_results[filename] = result
                    status = "✅" if result['is_valid'] else "❌"
                    print(f"   {status} {filename}: {result['message']}")
                else:
                    print(f"   ❌ {filename}: HTTP {response.status_code}")
            
            except Exception as e:
                print(f"   ❌ {filename}: {e}")
        
        valid_count = sum(1 for r in validation_results.values() if r['is_valid'])
        print(f"\n📊 Validation Summary: {valid_count}/{len(self.test_files)} files valid")
        
        return validation_results
    
    def test_single_file_analysis(self):
        """Test single file analysis"""
        print("\n🔍 Testing Single File Analysis...")
        
        # Test with a document file
        test_file = 'witness_statement.pdf'
        if test_file in self.test_files:
            try:
                with open(self.test_files[test_file], 'rb') as f:
                    files = {'file': (test_file, f, 'application/pdf')}
                    response = requests.post(f"{self.api_base_url}/analyze-evidence", files=files)
                
                if response.status_code == 200:
                    result = response.json()
                    if result['success']:
                        analysis = result['analysis']
                        print(f"✅ Analysis successful for {test_file}")
                        print(f"   Category: {analysis['category']}")
                        print(f"   Confidence: {analysis['confidence']:.1%}")
                        print(f"   AI Analysis Types: {analysis.get('ai_analysis_types', [])}")
                        return True
                    else:
                        print(f"❌ Analysis failed: {result['error']}")
                        return False
                else:
                    print(f"❌ Analysis request failed: {response.status_code}")
                    return False
            
            except Exception as e:
                print(f"❌ Single file analysis error: {e}")
                return False
        else:
            print(f"❌ Test file {test_file} not found")
            return False
    
    def test_batch_analysis(self):
        """Test batch analysis with multiple files"""
        print("\n📦 Testing Batch Analysis...")
        
        # Select a subset of files for batch testing
        batch_files = [
            'witness_statement.pdf',
            'incident_photo.jpg', 
            'incident_video.mp4',
            'witness_audio.mp3',
            'metadata.json'
        ]
        
        try:
            files = []
            for filename in batch_files:
                if filename in self.test_files:
                    f = open(self.test_files[filename], 'rb')
                    files.append(('files', (filename, f, 'application/octet-stream')))
            
            response = requests.post(f"{self.api_base_url}/analyze-batch", files=files)
            
            # Close file handles
            for _, file_tuple in files:
                file_tuple[1].close()
            
            if response.status_code == 200:
                result = response.json()
                self.session_id = result['session_id']
                
                print(f"✅ Batch analysis completed!")
                print(f"   Session ID: {self.session_id}")
                print(f"   Total Files: {result['total_files']}")
                print(f"   Successful: {result['successful_analyses']}")
                print(f"   Failed: {result['failed_analyses']}")
                
                # Display case summary
                if 'case_summary' in result:
                    summary = result['case_summary']
                    print(f"   Case ID: {summary['case_id']}")
                    print(f"   Overall Confidence: {summary['overall_confidence']:.1%}")
                
                return True
            else:
                print(f"❌ Batch analysis failed: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"❌ Batch analysis error: {e}")
            return False
    
    def test_case_summary_retrieval(self):
        """Test case summary retrieval"""
        print("\n📋 Testing Case Summary Retrieval...")
        
        if not self.session_id:
            print("❌ No session ID available")
            return False
        
        try:
            response = requests.get(f"{self.api_base_url}/case-summary/{self.session_id}")
            
            if response.status_code == 200:
                summary = response.json()
                print(f"✅ Case summary retrieved successfully")
                print(f"   Case ID: {summary['case_id']}")
                print(f"   Evidence Count: {summary['evidence_count']}")
                print(f"   Evidence Categories: {summary['evidence_categories']}")
                return True
            else:
                print(f"❌ Case summary retrieval failed: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"❌ Case summary error: {e}")
            return False
    
    def test_human_validation_workflow(self):
        """Test human-in-the-loop validation workflow"""
        print("\n👤 Testing Human Validation Workflow...")
        
        if not self.session_id:
            print("❌ No session ID available")
            return False
        
        try:
            # Test case summary update
            update_data = {
                'incident_summary': 'Updated incident summary with human input',
                'legal_significance': 'Enhanced legal analysis after human review',
                'additional_notes': 'Human validator notes and corrections'
            }
            
            response = requests.post(
                f"{self.api_base_url}/update-case-summary/{self.session_id}",
                data=update_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Case summary updated successfully")
                print(f"   Human Validated: {result['updated_summary'].get('human_validated')}")
                return True
            else:
                print(f"❌ Case summary update failed: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"❌ Human validation error: {e}")
            return False
    
    def test_icc_document_generation(self):
        """Test ICC document generation"""
        print("\n📄 Testing ICC Document Generation...")
        
        if not self.session_id:
            print("❌ No session ID available")
            return False
        
        try:
            response = requests.post(f"{self.api_base_url}/generate-icc-document/{self.session_id}")
            
            if response.status_code == 200:
                result = response.json()
                document = result['document']
                
                print(f"✅ ICC document generated successfully")
                print(f"   Case ID: {result['case_id']}")
                print(f"   Document Length: {len(document)} characters")
                print(f"   Contains Required Sections: {'INCIDENT SUMMARY' in document and 'EVIDENCE ANALYSIS' in document}")
                
                # Save document for review
                doc_filename = f"ICC_Document_{self.session_id}.txt"
                with open(doc_filename, 'w') as f:
                    f.write(document)
                print(f"   📁 Document saved as: {doc_filename}")
                
                return True
            else:
                print(f"❌ ICC document generation failed: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"❌ ICC document generation error: {e}")
            return False
    
    def test_final_submission(self):
        """Test final ICC submission"""
        print("\n🚀 Testing Final ICC Submission...")
        
        if not self.session_id:
            print("❌ No session ID available")
            return False
        
        try:
            submission_data = {
                'submission_method': 'API Submission',
                'witness_protection': True,
                'additional_notes': 'Test submission - witness protection requested'
            }
            
            response = requests.post(
                f"{self.api_base_url}/submit-to-icc/{self.session_id}",
                data=submission_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ ICC submission completed successfully")
                print(f"   Submission ID: {result['submission_id']}")
                print(f"   Status: {result['submission_record']['status']}")
                print(f"   Witness Protection: {result['submission_record']['witness_protection']}")
                return True
            else:
                print(f"❌ ICC submission failed: {response.status_code}")
                return False
        
        except Exception as e:
            print(f"❌ ICC submission error: {e}")
            return False
    
    def cleanup_test_files(self):
        """Clean up temporary test files"""
        print("\n🧹 Cleaning up test files...")
        
        for filename, filepath in self.test_files.items():
            try:
                os.unlink(filepath)
            except Exception as e:
                print(f"⚠️ Could not delete {filename}: {e}")
        
        print(f"✅ Cleanup completed")
    
    def run_comprehensive_test(self):
        """Run complete test suite"""
        print("🇰🇪 ICC EVIDENCE ANALYSIS SYSTEM - COMPREHENSIVE TEST SUITE")
        print("=" * 70)
        
        # Create test files
        self.create_test_files()
        
        # Test sequence
        tests = [
            ("API Health Check", self.test_api_health),
            ("Supported File Types", self.test_supported_file_types),
            ("File Validation", self.test_file_validation),
            ("Single File Analysis", self.test_single_file_analysis),
            ("Batch Analysis", self.test_batch_analysis),
            ("Case Summary Retrieval", self.test_case_summary_retrieval),
            ("Human Validation Workflow", self.test_human_validation_workflow),
            ("ICC Document Generation", self.test_icc_document_generation),
            ("Final ICC Submission", self.test_final_submission)
        ]
        
        results = {}
        
        for test_name, test_function in tests:
            try:
                results[test_name] = test_function()
            except Exception as e:
                print(f"❌ {test_name} failed with exception: {e}")
                results[test_name] = False
        
        # Test summary
        print("\n" + "=" * 70)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 70)
        
        passed = sum(1 for result in results.values() if result)
        total = len(results)
        
        for test_name, result in results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} {test_name}")
        
        print(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total:.0%})")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED! ICC system is fully functional.")
        else:
            print("⚠️ Some tests failed. Please review the output above.")
        
        # Cleanup
        self.cleanup_test_files()
        
        return passed == total

if __name__ == "__main__":
    # Run tests
    tester = ICCSystemTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print("\n🚀 ICC Evidence Analysis System is ready for deployment!")
    else:
        print("\n🔧 Please fix the issues before deployment.")
