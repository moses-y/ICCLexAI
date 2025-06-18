"""
🔍 METADATA EXTRACTION CORE AGENT
Specialized agent for comprehensive file metadata extraction
Part of the 5-agent intelligent consolidation system

AGENT RESPONSIBILITIES:
- GPS coordinate extraction from EXIF data
- Timestamp and creation date analysis  
- Document metadata parsing (PDF, Word, etc.)
- Audio/video technical metadata
- Camera and device information extraction
- Geolocation services integration

This is CORE AGENT #2 - focused solely on metadata extraction capabilities
"""

import streamlit as st
import os
import io
import json
import tempfile
from datetime import datetime
from pathlib import Path
import exifread
from geopy.geocoders import Nominatim
from mutagen import File as MutagenFile
import fitz  # PyMuPDF
from docx import Document
import cv2
import numpy as np

class MetadataExtractionAgent:
    """
    🔍 CORE AGENT #2: Advanced Metadata Extraction
    
    This agent specializes in extracting comprehensive metadata from evidence files:
    - Image EXIF data (GPS, timestamps, camera info)
    - Video metadata (duration, resolution, codecs)
    - Audio metadata (duration, bitrate, creation dates)
    - Document metadata (author, creation/modification dates)
    - PDF metadata (title, subject, creator info)
    - Geolocation conversion from GPS coordinates
    """
    
    def __init__(self):
        self.supported_image_types = ['jpg', 'jpeg', 'png', 'tiff', 'bmp', 'gif']
        self.supported_video_types = ['mp4', 'avi', 'mov', 'mkv', 'wmv', 'flv']
        self.supported_audio_types = ['mp3', 'wav', 'ogg', 'aac', 'm4a', 'flac']
        self.supported_document_types = ['pdf', 'docx', 'doc', 'txt']
        
    def extract_comprehensive_metadata(self, uploaded_file):
        """
        🎯 MAIN METHOD: Extract all available metadata from any file type
        
        Returns comprehensive metadata dictionary with:
        - Basic file info (name, size, type)
        - Technical metadata (resolution, duration, etc.)
        - Location data (GPS coordinates, address)
        - Timestamps (creation, modification dates)
        - Device/software information
        """
        try:
            # Initialize base metadata structure
            metadata = {
                'basic_info': {
                    'filename': uploaded_file.name,
                    'size_bytes': uploaded_file.size,
                    'size_mb': round(uploaded_file.size / (1024 * 1024), 2),
                    'file_type': uploaded_file.type,
                    'file_extension': Path(uploaded_file.name).suffix.lower()
                },
                'technical_metadata': {},
                'location_data': {
                    'gps_coordinates': None,
                    'location_address': None,
                    'extraction_method': None
                },
                'timestamps': {
                    'creation_date': None,
                    'modification_date': None,
                    'exif_datetime': None
                },
                'device_info': {
                    'camera_make': None,
                    'camera_model': None,
                    'software': None,
                    'lens_info': None
                },
                'extraction_status': {
                    'success': True,
                    'errors': [],
                    'warnings': []
                }
            }
            
            # Read file content once
            file_content = uploaded_file.read()
            uploaded_file.seek(0)  # Reset file pointer for other uses
            
            # Route to appropriate extraction method based on file type
            file_ext = metadata['basic_info']['file_extension']
            
            if any(ext in file_ext for ext in self.supported_image_types):
                image_metadata = self._extract_image_metadata(file_content)
                metadata['technical_metadata'].update(image_metadata.get('technical', {}))
                metadata['location_data'].update(image_metadata.get('location', {}))
                metadata['timestamps'].update(image_metadata.get('timestamps', {}))
                metadata['device_info'].update(image_metadata.get('device', {}))
                
            elif any(ext in file_ext for ext in self.supported_video_types):
                video_metadata = self._extract_video_metadata(file_content)
                metadata['technical_metadata'].update(video_metadata.get('technical', {}))
                metadata['timestamps'].update(video_metadata.get('timestamps', {}))
                
            elif any(ext in file_ext for ext in self.supported_audio_types):
                audio_metadata = self._extract_audio_metadata(file_content)
                metadata['technical_metadata'].update(audio_metadata.get('technical', {}))
                metadata['timestamps'].update(audio_metadata.get('timestamps', {}))
                
            elif file_ext == '.pdf':
                pdf_metadata = self._extract_pdf_metadata(file_content)
                metadata['technical_metadata'].update(pdf_metadata.get('technical', {}))
                metadata['timestamps'].update(pdf_metadata.get('timestamps', {}))
                metadata['device_info'].update(pdf_metadata.get('device', {}))
                
            elif any(ext in file_ext for ext in ['.docx', '.doc']):
                doc_metadata = self._extract_document_metadata(file_content)
                metadata['technical_metadata'].update(doc_metadata.get('technical', {}))
                metadata['timestamps'].update(doc_metadata.get('timestamps', {}))
                metadata['device_info'].update(doc_metadata.get('device', {}))
            
            # Convert GPS coordinates to human-readable address
            if metadata['location_data']['gps_coordinates']:
                address = self._get_address_from_coordinates(
                    metadata['location_data']['gps_coordinates']
                )
                if address:
                    metadata['location_data']['location_address'] = address
                    metadata['location_data']['extraction_method'] = 'GPS_to_Address'
            
            return metadata
            
        except Exception as e:
            return {
                'basic_info': {
                    'filename': uploaded_file.name,
                    'size_bytes': uploaded_file.size,
                    'file_type': uploaded_file.type
                },
                'extraction_status': {
                    'success': False,
                    'errors': [f"Metadata extraction failed: {str(e)}"]
                }
            }
    
    def _extract_image_metadata(self, file_content):
        """🖼️ Extract comprehensive EXIF data from image files"""
        metadata = {
            'technical': {},
            'location': {},
            'timestamps': {},
            'device': {}
        }
        
        try:
            # Process EXIF data
            tags = exifread.process_file(io.BytesIO(file_content), details=True)
            
            # Extract GPS coordinates
            if 'GPS GPSLatitude' in tags and 'GPS GPSLongitude' in tags:
                lat = self._convert_gps_to_decimal(
                    tags['GPS GPSLatitude'], 
                    tags.get('GPS GPSLatitudeRef', 'N')
                )
                lon = self._convert_gps_to_decimal(
                    tags['GPS GPSLongitude'], 
                    tags.get('GPS GPSLongitudeRef', 'E')
                )
                
                if lat is not None and lon is not None:
                    metadata['location']['gps_coordinates'] = (lat, lon)
                    metadata['location']['gps_latitude'] = lat
                    metadata['location']['gps_longitude'] = lon
            
            # Extract timestamps
            datetime_fields = [
                'EXIF DateTimeOriginal',
                'EXIF DateTime', 
                'Image DateTime',
                'GPS GPSDate'
            ]
            
            for field in datetime_fields:
                if field in tags:
                    try:
                        datetime_str = str(tags[field])
                        if ':' in datetime_str:
                            parsed_date = datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
                            metadata['timestamps']['exif_datetime'] = parsed_date.isoformat()
                            break
                    except ValueError:
                        continue
            
            # Extract camera/device information
            device_fields = {
                'Image Make': 'camera_make',
                'Image Model': 'camera_model', 
                'Image Software': 'software',
                'EXIF LensModel': 'lens_model',
                'EXIF LensMake': 'lens_make'
            }
            
            for exif_field, metadata_key in device_fields.items():
                if exif_field in tags:
                    metadata['device'][metadata_key] = str(tags[exif_field])
            
            # Extract technical image data
            technical_fields = {
                'EXIF ExifImageWidth': 'width',
                'EXIF ExifImageLength': 'height',
                'EXIF Orientation': 'orientation',
                'EXIF Flash': 'flash_info',
                'EXIF FocalLength': 'focal_length',
                'EXIF ISO': 'iso_speed'
            }
            
            for exif_field, metadata_key in technical_fields.items():
                if exif_field in tags:
                    metadata['technical'][metadata_key] = str(tags[exif_field])
                    
        except Exception as e:
            st.debug(f"Error extracting image metadata: {e}")
            
        return metadata
    
    def _extract_video_metadata(self, file_content):
        """🎬 Extract metadata from video files using OpenCV"""
        metadata = {
            'technical': {},
            'timestamps': {}
        }
        
        try:
            # Save to temporary file for OpenCV processing
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                temp_file.write(file_content)
                temp_path = temp_file.name
            
            # Extract video properties
            cap = cv2.VideoCapture(temp_path)
            
            if cap.isOpened():
                # Technical properties
                metadata['technical']['fps'] = cap.get(cv2.CAP_PROP_FPS)
                metadata['technical']['frame_count'] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                metadata['technical']['width'] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                metadata['technical']['height'] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                
                # Calculate duration
                fps = metadata['technical']['fps']
                frame_count = metadata['technical']['frame_count']
                if fps > 0:
                    duration_seconds = frame_count / fps
                    metadata['technical']['duration_seconds'] = round(duration_seconds, 2)
                    metadata['technical']['duration_formatted'] = self._format_duration(duration_seconds)
                
                cap.release()
            
            # Try to get file creation date
            import os
            file_stat = os.stat(temp_path)
            metadata['timestamps']['file_creation'] = datetime.fromtimestamp(file_stat.st_ctime).isoformat()
            metadata['timestamps']['file_modification'] = datetime.fromtimestamp(file_stat.st_mtime).isoformat()
            
            # Clean up temporary file
            os.unlink(temp_path)
            
        except Exception as e:
            st.debug(f"Error extracting video metadata: {e}")
            
        return metadata
    
    def _extract_audio_metadata(self, file_content):
        """🎵 Extract metadata from audio files using mutagen"""
        metadata = {
            'technical': {},
            'timestamps': {}
        }
        
        try:
            # Save to temporary file for mutagen processing
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file_content)
                temp_path = temp_file.name
            
            # Extract audio properties
            audio_file = MutagenFile(temp_path)
            
            if audio_file and hasattr(audio_file, 'info'):
                # Technical properties
                if hasattr(audio_file.info, 'length'):
                    duration = audio_file.info.length
                    metadata['technical']['duration_seconds'] = round(duration, 2)
                    metadata['technical']['duration_formatted'] = self._format_duration(duration)
                
                if hasattr(audio_file.info, 'bitrate'):
                    metadata['technical']['bitrate'] = audio_file.info.bitrate
                
                if hasattr(audio_file.info, 'channels'):
                    metadata['technical']['channels'] = audio_file.info.channels
                
                # Extract tags if available
                if hasattr(audio_file, 'tags') and audio_file.tags:
                    for key, value in audio_file.tags.items():
                        if 'date' in key.lower() or 'year' in key.lower():
                            date_value = value[0] if isinstance(value, list) else value
                            metadata['timestamps']['tag_date'] = str(date_value)
                            break
            
            # Clean up temporary file
            os.unlink(temp_path)
            
        except Exception as e:
            st.debug(f"Error extracting audio metadata: {e}")
            
        return metadata
    
    def _extract_pdf_metadata(self, file_content):
        """📄 Extract metadata from PDF documents"""
        metadata = {
            'technical': {},
            'timestamps': {},
            'device': {}
        }
        
        try:
            # Open PDF document
            pdf_doc = fitz.open(stream=file_content, filetype="pdf")
            
            # Basic document info
            metadata['technical']['page_count'] = pdf_doc.page_count
            
            # Extract document metadata
            doc_metadata = pdf_doc.metadata
            
            if doc_metadata:
                # Document properties
                metadata['device']['title'] = doc_metadata.get('title', '')
                metadata['device']['author'] = doc_metadata.get('author', '')
                metadata['device']['subject'] = doc_metadata.get('subject', '')
                metadata['device']['creator'] = doc_metadata.get('creator', '')
                metadata['device']['producer'] = doc_metadata.get('producer', '')
                
                # Parse timestamps
                creation_date = doc_metadata.get('creationDate', '')
                mod_date = doc_metadata.get('modDate', '')
                
                if creation_date:
                    parsed_date = self._parse_pdf_date(creation_date)
                    if parsed_date:
                        metadata['timestamps']['creation_date'] = parsed_date
                
                if mod_date:
                    parsed_date = self._parse_pdf_date(mod_date)
                    if parsed_date:
                        metadata['timestamps']['modification_date'] = parsed_date
            
            pdf_doc.close()
            
        except Exception as e:
            st.debug(f"Error extracting PDF metadata: {e}")
            
        return metadata
    
    def _extract_document_metadata(self, file_content):
        """📝 Extract metadata from Word documents"""
        metadata = {
            'technical': {},
            'timestamps': {},
            'device': {}
        }
        
        try:
            # Save to temporary file for python-docx processing
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file:
                temp_file.write(file_content)
                temp_path = temp_file.name
            
            # Load document
            doc = Document(temp_path)
            
            # Extract core properties
            core_props = doc.core_properties
            
            # Document properties
            metadata['device']['title'] = core_props.title or ''
            metadata['device']['author'] = core_props.author or ''
            metadata['device']['subject'] = core_props.subject or ''
            metadata['device']['keywords'] = core_props.keywords or ''
            metadata['device']['comments'] = core_props.comments or ''
            
            # Technical properties
            metadata['technical']['paragraph_count'] = len(doc.paragraphs)
            metadata['technical']['section_count'] = len(doc.sections)
            
            # Timestamps
            if core_props.created:
                metadata['timestamps']['creation_date'] = core_props.created.isoformat()
            if core_props.modified:
                metadata['timestamps']['modification_date'] = core_props.modified.isoformat()
            if core_props.last_printed:
                metadata['timestamps']['last_printed'] = core_props.last_printed.isoformat()
            
            # Clean up temporary file
            os.unlink(temp_path)
            
        except Exception as e:
            st.debug(f"Error extracting document metadata: {e}")
            
        return metadata
    
    def _convert_gps_to_decimal(self, gps_coord, ref):
        """🌍 Convert GPS coordinates from EXIF format to decimal degrees"""
        try:
            if hasattr(gps_coord, 'values'):
                # Handle exifread format
                degrees = float(gps_coord.values[0].num) / float(gps_coord.values[0].den)
                minutes = float(gps_coord.values[1].num) / float(gps_coord.values[1].den)
                seconds = float(gps_coord.values[2].num) / float(gps_coord.values[2].den)
            else:
                # Handle other formats
                degrees, minutes, seconds = gps_coord[:3]
            
            decimal_degrees = degrees + (minutes / 60.0) + (seconds / 3600.0)
            
            # Apply hemisphere reference
            if hasattr(ref, 'values'):
                ref_str = str(ref.values[0])
            else:
                ref_str = str(ref)
                
            if ref_str in ['S', 'W']:
                decimal_degrees = -decimal_degrees
                
            return decimal_degrees
            
        except Exception as e:
            st.debug(f"Error converting GPS coordinates: {e}")
            return None
    
    def _get_address_from_coordinates(self, coords):
        """🗺️ Convert GPS coordinates to human-readable address"""
        try:
            geolocator = Nominatim(user_agent="icc_metadata_agent")
            lat, lon = coords
            location = geolocator.reverse(f"{lat}, {lon}", timeout=10)
            
            if location:
                return location.address
            else:
                return None
                
        except Exception as e:
            st.debug(f"Error getting address from coordinates: {e}")
            return None
    
    def _parse_pdf_date(self, pdf_date_str):
        """📅 Parse PDF date format to ISO format"""
        try:
            # PDF dates are often in format: D:YYYYMMDDHHmmSSOHH'mm'
            if pdf_date_str.startswith('D:'):
                date_part = pdf_date_str[2:16]  # YYYYMMDDHHmmSS
                parsed_date = datetime.strptime(date_part, '%Y%m%d%H%M%S')
                return parsed_date.isoformat()
            else:
                # Try standard datetime parsing
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%m/%d/%Y']:
                    try:
                        parsed_date = datetime.strptime(pdf_date_str, fmt)
                        return parsed_date.isoformat()
                    except ValueError:
                        continue
            return None
        except Exception:
            return None
    
    def _format_duration(self, seconds):
        """⏱️ Format duration seconds to human-readable format"""
        try:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            
            if hours > 0:
                return f"{hours:02d}:{minutes:02d}:{secs:02d}"
            else:
                return f"{minutes:02d}:{secs:02d}"
        except:
            return "Unknown"
    
    def display_metadata_summary(self, metadata):
        """📊 Display comprehensive metadata in Streamlit UI"""
        st.subheader("🔍 Metadata Extraction Results")
        
        # Basic file information
        with st.expander("📁 Basic File Information", expanded=True):
            basic = metadata.get('basic_info', {})
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Filename:** {basic.get('filename', 'Unknown')}")
                st.write(f"**File Type:** {basic.get('file_type', 'Unknown')}")
                st.write(f"**Size:** {basic.get('size_mb', 0)} MB")
            
            with col2:
                st.write(f"**Extension:** {basic.get('file_extension', 'Unknown')}")
                extraction_status = metadata.get('extraction_status', {})
                if extraction_status.get('success', False):
                    st.success("✅ Metadata extraction successful")
                else:
                    st.error("❌ Metadata extraction failed")
        
        # Location data
        location_data = metadata.get('location_data', {})
        if location_data.get('gps_coordinates'):
            with st.expander("🌍 Location Information"):
                coords = location_data['gps_coordinates']
                st.write(f"**GPS Coordinates:** {coords[0]:.6f}, {coords[1]:.6f}")
                
                if location_data.get('location_address'):
                    st.write(f"**Address:** {location_data['location_address']}")
                
                # Show map if coordinates available
                st.map([{"lat": coords[0], "lon": coords[1]}])
        
        # Technical metadata
        technical = metadata.get('technical_metadata', {})
        if technical:
            with st.expander("⚙️ Technical Information"):
                for key, value in technical.items():
                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")
        
        # Device information
        device_info = metadata.get('device_info', {})
        if any(device_info.values()):
            with st.expander("📱 Device Information"):
                for key, value in device_info.items():
                    if value:
                        st.write(f"**{key.replace('_', ' ').title()}:** {value}")
        
        # Timestamps
        timestamps = metadata.get('timestamps', {})
        if any(timestamps.values()):
            with st.expander("⏰ Timestamp Information"):
                for key, value in timestamps.items():
                    if value:
                        st.write(f"**{key.replace('_', ' ').title()}:** {value}")

# Export the agent for use by other components
def get_metadata_agent():
    """🎯 Factory function to get metadata extraction agent instance"""
    return MetadataExtractionAgent()

# Standalone execution for testing
if __name__ == "__main__":
    st.title("🔍 Metadata Extraction Core Agent")
    st.write("Upload a file to test comprehensive metadata extraction")
    
    agent = MetadataExtractionAgent()
    
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=['jpg', 'jpeg', 'png', 'mp4', 'avi', 'mp3', 'wav', 'pdf', 'docx']
    )
    
    if uploaded_file:
        with st.spinner("🔍 Extracting metadata..."):
            metadata = agent.extract_comprehensive_metadata(uploaded_file)
            agent.display_metadata_summary(metadata)
            
            # Show raw metadata in expander
            with st.expander("🗂️ Raw Metadata JSON"):
                st.json(metadata)
