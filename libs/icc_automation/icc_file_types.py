"""
ICC File Type Support Matrix
Comprehensive support for ALL file types accepted by the International Criminal Court
"""

import os
from typing import Dict, List, Tuple
import mimetypes
from enum import Enum

class ICCEvidenceCategory(Enum):
    """ICC Evidence Categories as per ICC submission guidelines"""
    DOCUMENTARY = "documentary"
    VISUAL = "visual"
    AUDIO = "audio"
    MULTIMEDIA = "multimedia"
    DIGITAL = "digital"
    FORENSIC = "forensic"

class ICCFileTypeRegistry:
    """
    Complete registry of ICC-accepted file formats
    Based on ICC Registry procedures and technical requirements
    """
    
    # Primary Evidence File Types (ICC-accepted)
    ICC_SUPPORTED_FORMATS = {
        # Document Evidence
        'documents': {
            '.pdf': {'category': ICCEvidenceCategory.DOCUMENTARY, 'max_size_mb': 25, 'ai_analysis': ['text_extraction', 'entity_recognition', 'legal_analysis']},
            '.doc': {'category': ICCEvidenceCategory.DOCUMENTARY, 'max_size_mb': 25, 'ai_analysis': ['text_extraction', 'entity_recognition', 'legal_analysis']},
            '.docx': {'category': ICCEvidenceCategory.DOCUMENTARY, 'max_size_mb': 25, 'ai_analysis': ['text_extraction', 'entity_recognition', 'legal_analysis']},
            '.txt': {'category': ICCEvidenceCategory.DOCUMENTARY, 'max_size_mb': 10, 'ai_analysis': ['text_extraction', 'entity_recognition', 'legal_analysis']},
            '.rtf': {'category': ICCEvidenceCategory.DOCUMENTARY, 'max_size_mb': 10, 'ai_analysis': ['text_extraction', 'entity_recognition', 'legal_analysis']},
            '.odt': {'category': ICCEvidenceCategory.DOCUMENTARY, 'max_size_mb': 25, 'ai_analysis': ['text_extraction', 'entity_recognition', 'legal_analysis']},
        },
        
        # Image Evidence
        'images': {
            '.jpg': {'category': ICCEvidenceCategory.VISUAL, 'max_size_mb': 50, 'ai_analysis': ['exif_extraction', 'scene_analysis', 'object_detection', 'face_recognition', 'forensic_analysis']},
            '.jpeg': {'category': ICCEvidenceCategory.VISUAL, 'max_size_mb': 50, 'ai_analysis': ['exif_extraction', 'scene_analysis', 'object_detection', 'face_recognition', 'forensic_analysis']},
            '.png': {'category': ICCEvidenceCategory.VISUAL, 'max_size_mb': 50, 'ai_analysis': ['exif_extraction', 'scene_analysis', 'object_detection', 'face_recognition', 'forensic_analysis']},
            '.gif': {'category': ICCEvidenceCategory.VISUAL, 'max_size_mb': 25, 'ai_analysis': ['scene_analysis', 'object_detection', 'timeline_analysis']},
            '.bmp': {'category': ICCEvidenceCategory.VISUAL, 'max_size_mb': 100, 'ai_analysis': ['exif_extraction', 'scene_analysis', 'object_detection', 'forensic_analysis']},
            '.tiff': {'category': ICCEvidenceCategory.VISUAL, 'max_size_mb': 100, 'ai_analysis': ['exif_extraction', 'scene_analysis', 'object_detection', 'forensic_analysis']},
            '.tif': {'category': ICCEvidenceCategory.VISUAL, 'max_size_mb': 100, 'ai_analysis': ['exif_extraction', 'scene_analysis', 'object_detection', 'forensic_analysis']},
            '.webp': {'category': ICCEvidenceCategory.VISUAL, 'max_size_mb': 25, 'ai_analysis': ['scene_analysis', 'object_detection']},
            '.heic': {'category': ICCEvidenceCategory.VISUAL, 'max_size_mb': 50, 'ai_analysis': ['exif_extraction', 'scene_analysis', 'object_detection', 'forensic_analysis']},
            '.raw': {'category': ICCEvidenceCategory.FORENSIC, 'max_size_mb': 200, 'ai_analysis': ['exif_extraction', 'forensic_analysis', 'metadata_analysis']},
        },
        
        # Video Evidence
        'videos': {
            '.mp4': {'category': ICCEvidenceCategory.MULTIMEDIA, 'max_size_mb': 500, 'ai_analysis': ['video_analysis', 'audio_transcription', 'scene_detection', 'face_recognition', 'timeline_analysis']},
            '.avi': {'category': ICCEvidenceCategory.MULTIMEDIA, 'max_size_mb': 500, 'ai_analysis': ['video_analysis', 'audio_transcription', 'scene_detection', 'face_recognition', 'timeline_analysis']},
            '.mov': {'category': ICCEvidenceCategory.MULTIMEDIA, 'max_size_mb': 500, 'ai_analysis': ['video_analysis', 'audio_transcription', 'scene_detection', 'face_recognition', 'timeline_analysis']},
            '.mkv': {'category': ICCEvidenceCategory.MULTIMEDIA, 'max_size_mb': 500, 'ai_analysis': ['video_analysis', 'audio_transcription', 'scene_detection', 'timeline_analysis']},
            '.wmv': {'category': ICCEvidenceCategory.MULTIMEDIA, 'max_size_mb': 500, 'ai_analysis': ['video_analysis', 'audio_transcription', 'scene_detection', 'timeline_analysis']},
            '.flv': {'category': ICCEvidenceCategory.MULTIMEDIA, 'max_size_mb': 500, 'ai_analysis': ['video_analysis', 'audio_transcription', 'scene_detection']},
            '.webm': {'category': ICCEvidenceCategory.MULTIMEDIA, 'max_size_mb': 500, 'ai_analysis': ['video_analysis', 'audio_transcription', 'scene_detection']},
            '.m4v': {'category': ICCEvidenceCategory.MULTIMEDIA, 'max_size_mb': 500, 'ai_analysis': ['video_analysis', 'audio_transcription', 'scene_detection', 'timeline_analysis']},
            '.3gp': {'category': ICCEvidenceCategory.MULTIMEDIA, 'max_size_mb': 100, 'ai_analysis': ['video_analysis', 'audio_transcription', 'mobile_metadata']},
        },
        
        # Audio Evidence
        'audio': {
            '.mp3': {'category': ICCEvidenceCategory.AUDIO, 'max_size_mb': 100, 'ai_analysis': ['audio_transcription', 'speaker_identification', 'emotion_analysis', 'background_analysis']},
            '.wav': {'category': ICCEvidenceCategory.AUDIO, 'max_size_mb': 200, 'ai_analysis': ['audio_transcription', 'speaker_identification', 'emotion_analysis', 'forensic_audio_analysis']},
            '.m4a': {'category': ICCEvidenceCategory.AUDIO, 'max_size_mb': 100, 'ai_analysis': ['audio_transcription', 'speaker_identification', 'emotion_analysis', 'background_analysis']},
            '.flac': {'category': ICCEvidenceCategory.AUDIO, 'max_size_mb': 200, 'ai_analysis': ['audio_transcription', 'speaker_identification', 'emotion_analysis', 'forensic_audio_analysis']},
            '.ogg': {'category': ICCEvidenceCategory.AUDIO, 'max_size_mb': 100, 'ai_analysis': ['audio_transcription', 'speaker_identification', 'emotion_analysis']},
            '.aac': {'category': ICCEvidenceCategory.AUDIO, 'max_size_mb': 100, 'ai_analysis': ['audio_transcription', 'speaker_identification', 'emotion_analysis']},
            '.wma': {'category': ICCEvidenceCategory.AUDIO, 'max_size_mb': 100, 'ai_analysis': ['audio_transcription', 'speaker_identification', 'emotion_analysis']},
            '.amr': {'category': ICCEvidenceCategory.AUDIO, 'max_size_mb': 50, 'ai_analysis': ['audio_transcription', 'mobile_audio_analysis']},
        },
        
        # Digital Evidence & Forensic Files
        'digital': {
            '.xml': {'category': ICCEvidenceCategory.DIGITAL, 'max_size_mb': 25, 'ai_analysis': ['data_extraction', 'metadata_analysis', 'structure_analysis']},
            '.json': {'category': ICCEvidenceCategory.DIGITAL, 'max_size_mb': 25, 'ai_analysis': ['data_extraction', 'metadata_analysis', 'api_analysis']},
            '.csv': {'category': ICCEvidenceCategory.DIGITAL, 'max_size_mb': 50, 'ai_analysis': ['data_extraction', 'pattern_analysis', 'statistical_analysis']},
            '.xlsx': {'category': ICCEvidenceCategory.DIGITAL, 'max_size_mb': 50, 'ai_analysis': ['data_extraction', 'pattern_analysis', 'financial_analysis']},
            '.xls': {'category': ICCEvidenceCategory.DIGITAL, 'max_size_mb': 50, 'ai_analysis': ['data_extraction', 'pattern_analysis', 'financial_analysis']},
            '.html': {'category': ICCEvidenceCategory.DIGITAL, 'max_size_mb': 25, 'ai_analysis': ['content_extraction', 'web_analysis', 'metadata_analysis']},
            '.mhtml': {'category': ICCEvidenceCategory.DIGITAL, 'max_size_mb': 50, 'ai_analysis': ['content_extraction', 'web_analysis', 'archive_analysis']},
        },
        
        # Archive & Compressed Evidence
        'archives': {
            '.zip': {'category': ICCEvidenceCategory.DIGITAL, 'max_size_mb': 1000, 'ai_analysis': ['archive_analysis', 'bulk_processing', 'metadata_extraction']},
            '.rar': {'category': ICCEvidenceCategory.DIGITAL, 'max_size_mb': 1000, 'ai_analysis': ['archive_analysis', 'bulk_processing', 'metadata_extraction']},
            '.7z': {'category': ICCEvidenceCategory.DIGITAL, 'max_size_mb': 1000, 'ai_analysis': ['archive_analysis', 'bulk_processing', 'metadata_extraction']},
            '.tar': {'category': ICCEvidenceCategory.DIGITAL, 'max_size_mb': 1000, 'ai_analysis': ['archive_analysis', 'bulk_processing', 'metadata_extraction']},
            '.gz': {'category': ICCEvidenceCategory.DIGITAL, 'max_size_mb': 1000, 'ai_analysis': ['archive_analysis', 'bulk_processing', 'metadata_extraction']},
        },
        
        # Specialized Forensic Evidence
        'forensic': {
            '.dd': {'category': ICCEvidenceCategory.FORENSIC, 'max_size_mb': 5000, 'ai_analysis': ['disk_image_analysis', 'forensic_analysis', 'deleted_file_recovery']},
            '.e01': {'category': ICCEvidenceCategory.FORENSIC, 'max_size_mb': 5000, 'ai_analysis': ['encase_analysis', 'forensic_analysis', 'chain_of_custody']},
            '.aff': {'category': ICCEvidenceCategory.FORENSIC, 'max_size_mb': 5000, 'ai_analysis': ['advanced_forensic_format', 'forensic_analysis']},
            '.vmdk': {'category': ICCEvidenceCategory.FORENSIC, 'max_size_mb': 2000, 'ai_analysis': ['virtual_machine_analysis', 'digital_forensics']},
        }
    }
    
    @classmethod
    def get_all_supported_extensions(cls) -> List[str]:
        """Get all supported file extensions"""
        extensions = []
        for category in cls.ICC_SUPPORTED_FORMATS.values():
            extensions.extend(category.keys())
        return sorted(extensions)
    
    @classmethod
    def get_file_category(cls, filename: str) -> str:
        """Determine the category of a file based on its extension"""
        ext = os.path.splitext(filename.lower())[1]
        
        for category_name, formats in cls.ICC_SUPPORTED_FORMATS.items():
            if ext in formats:
                return category_name
        
        return 'unknown'
    
    @classmethod
    def get_file_info(cls, filename: str) -> Dict:
        """Get detailed information about a file's ICC compatibility"""
        ext = os.path.splitext(filename.lower())[1]
        
        for category_name, formats in cls.ICC_SUPPORTED_FORMATS.items():
            if ext in formats:
                return {
                    'extension': ext,
                    'category': category_name,
                    'icc_category': formats[ext]['category'].value,
                    'max_size_mb': formats[ext]['max_size_mb'],
                    'ai_analysis_types': formats[ext]['ai_analysis'],
                    'supported': True
                }
        
        return {
            'extension': ext,
            'category': 'unknown',
            'icc_category': 'unsupported',
            'max_size_mb': 0,
            'ai_analysis_types': [],
            'supported': False
        }
    
    @classmethod
    def validate_file_for_icc(cls, filename: str, file_size_bytes: int) -> Tuple[bool, str]:
        """Validate if a file meets ICC submission requirements"""
        file_info = cls.get_file_info(filename)
        
        if not file_info['supported']:
            return False, f"File type {file_info['extension']} is not supported by ICC"
        
        max_size_bytes = file_info['max_size_mb'] * 1024 * 1024
        if file_size_bytes > max_size_bytes:
            return False, f"File size ({file_size_bytes/1024/1024:.1f}MB) exceeds ICC limit ({file_info['max_size_mb']}MB)"
        
        return True, "File meets ICC submission requirements"
    
    @classmethod
    def get_recommended_ai_analysis(cls, filename: str) -> List[str]:
        """Get recommended AI analysis types for a file"""
        file_info = cls.get_file_info(filename)
        return file_info.get('ai_analysis_types', [])

# File type validation utilities
def is_icc_supported(filename: str) -> bool:
    """Quick check if file type is supported by ICC"""
    return ICCFileTypeRegistry.get_file_info(filename)['supported']

def get_mime_type(filename: str) -> str:
    """Get MIME type for a file"""
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

# ICC Evidence Classification
ICC_EVIDENCE_TYPES = {
    'witness_statement': ['documents', 'audio', 'video'],
    'physical_evidence': ['images', 'videos', 'forensic'],
    'documentary_evidence': ['documents', 'digital', 'archives'],
    'digital_evidence': ['digital', 'forensic', 'archives'],
    'expert_report': ['documents', 'digital'],
    'victim_impact': ['documents', 'audio', 'video', 'images']
}
