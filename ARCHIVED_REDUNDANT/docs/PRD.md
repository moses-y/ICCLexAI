# Product Requirements Document (PRD)
## ICC Evidence Submission Automation Tool

### Executive Summary
An emergency-response web application that enables citizens to submit evidence to the International Criminal Court (ICC) regarding incidents in Nairobi CBD. The application automates the evidence submission process to reduce barriers and ensure critical evidence is properly documented and submitted.

### Project Overview
**Problem**: Manual ICC evidence submission is complex and time-consuming, potentially preventing critical evidence from reaching the proper authorities during urgent situations.

**Solution**: A streamlit-based web application with automated form filling capabilities that streamlines the evidence submission process to the ICC portal.

### Core Features

#### 1. Evidence Upload Interface
- **Drag & Drop File Upload**: Intuitive file dropping area
- **Multi-source Upload**: Support for local files, Google Drive, OneDrive
- **File Format Support**: Documents, images, videos, audio files
- **File Validation**: Ensure appropriate file types and sizes

#### 2. Automated Form Processing
- **Selenium Integration**: Automated navigation and form filling on ICC portal
- **Field Mapping**: Intelligent mapping of user data to ICC form fields
- **Error Handling**: Robust error detection and retry mechanisms
- **Progress Tracking**: Real-time submission status updates

#### 3. User Interface
- **Kenyan Flag Theme**: Colors inspired by Kenyan flag (black, red, green, white)
- **Simple Design**: Clean, accessible interface for emergency use
- **Mobile Responsive**: Works on various device sizes
- **Clear Instructions**: Step-by-step guidance for users

#### 4. Data Collection
- **Incident Details**: Date, time, location (defaulted to CBD Nairobi, 2 PM today)
- **Evidence Description**: Automated categorization and description
- **Contact Information**: Optional submitter details
- **Witness Information**: Optional witness contact details

### Technical Requirements

#### Technology Stack
- **Frontend**: Streamlit
- **Automation**: Selenium WebDriver
- **File Handling**: Python file I/O libraries
- **Cloud Integration**: Google Drive API, OneDrive API
- **Backend**: Python

#### Security & Privacy
- **Data Encryption**: Secure file transmission
- **No Local Storage**: Files processed and transmitted immediately
- **Anonymous Option**: Allow anonymous submissions
- **Secure Connections**: HTTPS only

### Success Metrics
- **Submission Success Rate**: >95% successful ICC submissions
- **Processing Time**: <5 minutes from upload to submission
- **User Experience**: Intuitive interface requiring minimal technical knowledge
- **Accessibility**: Works on mobile and desktop devices

### Timeline
**Phase 1 (Immediate)**: Core upload and automation functionality
**Phase 2**: Cloud integration and enhanced UI
**Phase 3**: Mobile optimization and advanced features

### Risk Mitigation
- **ICC Portal Changes**: Regular testing and update mechanisms
- **Network Issues**: Retry logic and offline capability
- **File Corruption**: Validation and backup processes
- **Legal Compliance**: Ensure all submissions meet ICC requirements

---
*This PRD addresses the urgent need for streamlined ICC evidence submission following incidents in Nairobi CBD.*
