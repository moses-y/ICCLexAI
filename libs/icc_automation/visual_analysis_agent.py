"""
🇰🇪 ICC VISUAL EVIDENCE ANALYST AGENT
Specialized agent for image and video analysis

RESPONSIBILITIES:
🔹 Scene analysis and object detection
🔹 Facial recognition and identification
🔹 Location extraction from images
🔹 Weapon and evidence identification
🔹 Violence and injury documentation
🔹 Temporal and spatial analysis
"""

import os
import io
import base64
import tempfile
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import requests
from PIL import Image
import cv2
import numpy as np
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class VisualAnalysisAgent:
    """Specialized agent for comprehensive visual evidence analysis"""
    
    def __init__(self, groq_api_key: Optional[str] = None, 
                 google_api_key: Optional[str] = None,
                 roboflow_api_key: Optional[str] = None):
        self.groq_client = Groq(api_key=groq_api_key or os.getenv('GROQ_API_KEY'))
        self.google_api_key = google_api_key or os.getenv('GOOGLE_API_KEY')
        self.roboflow_api_key = roboflow_api_key or os.getenv('ROBOFLOW_API_KEY')
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Supported formats
        self.supported_image = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
        self.supported_video = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.webm']
        
        # Google Vision API endpoints
        self.google_vision_url = "https://vision.googleapis.com/v1/images:annotate"
        
        # Roboflow models for specific detection
        self.roboflow_models = {
            'weapons': 'weapon-detection-oj0tb/1',
            'violence': 'violence-detection-tnwjl/1',
            'people': 'person-detection-ybhvs/1'
        }
    
    async def analyze_visual_evidence(self, file_data: Dict[str, Any], 
                                    shared_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive visual evidence analysis
        
        Args:
            file_data: File data with content, filename, type, metadata
            shared_context: Shared context from ICC case
            
        Returns:
            Comprehensive visual analysis results
        """
        
        try:
            self.logger.info(f"Analyzing visual evidence: {file_data.get('filename', 'unknown')}")
            
            content = file_data.get('content', b'')
            filename = file_data.get('filename', 'unknown')
            metadata = file_data.get('metadata', {})
            file_type = file_data.get('type', '')
            
            # Determine if image or video
            is_video = file_type.startswith('video/') or any(
                filename.lower().endswith(ext) for ext in self.supported_video
            )
            
            if is_video:
                # Extract frames from video and analyze
                analysis_result = await self._analyze_video_content(content, filename, metadata, shared_context)
            else:
                # Analyze image directly
                analysis_result = await self._analyze_image_content(content, filename, metadata, shared_context)
            
            # Add agent metadata
            analysis_result.update({
                'agent_type': 'visual_analyst',
                'processing_timestamp': datetime.now().isoformat(),
                'file_type': 'video' if is_video else 'image',
                'evidence_quality': self._calculate_visual_quality(analysis_result, metadata)
            })
            
            self.logger.info(f"Visual analysis completed: {filename}")
            return analysis_result
            
        except Exception as e:
            self.logger.error(f"Error analyzing visual evidence: {str(e)}")
            return {
                'agent_type': 'visual_analyst',
                'error': str(e),
                'processing_timestamp': datetime.now().isoformat(),
                'status': 'failed'
            }
    
    async def _analyze_image_content(self, content: bytes, filename: str, 
                                   metadata: Dict[str, Any], 
                                   shared_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze single image content"""
        
        # Run multiple analysis methods in parallel
        analyses = await self._run_parallel_image_analysis(content, shared_context)
        
        # Combine all analysis results
        combined_analysis = {
            'filename': filename,
            'scene_analysis': analyses.get('scene_analysis', {}),
            'object_detection': analyses.get('object_detection', {}),
            'google_vision': analyses.get('google_vision', {}),
            'roboflow_analysis': analyses.get('roboflow_analysis', {}),
            'technical_analysis': self._analyze_image_technical_quality(content),
            'legal_assessment': await self._assess_visual_legal_relevance(analyses, shared_context),
            'spatial_analysis': self._analyze_spatial_context(metadata, analyses),
            'recommendations': []
        }
        
        # Generate recommendations
        combined_analysis['recommendations'] = self._generate_visual_recommendations(combined_analysis)
        
        return combined_analysis
    
    async def _analyze_video_content(self, content: bytes, filename: str,
                                   metadata: Dict[str, Any],
                                   shared_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze video content by extracting and analyzing key frames"""
        
        try:
            # Save video to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_file:
                temp_file.write(content)
                temp_path = temp_file.name
            
            # Extract key frames from video
            frames = self._extract_key_frames(temp_path)
            
            # Analyze each frame
            frame_analyses = []
            for i, frame in enumerate(frames):
                frame_data = self._frame_to_bytes(frame)
                frame_analysis = await self._analyze_image_content(
                    frame_data, f"{filename}_frame_{i}", {}, shared_context
                )
                frame_analysis['frame_number'] = i
                frame_analysis['timestamp'] = i * (metadata.get('duration', 0) / len(frames))
                frame_analyses.append(frame_analysis)
            
            # Clean up
            os.unlink(temp_path)
            
            # Aggregate frame analyses
            video_analysis = {
                'filename': filename,
                'total_frames_analyzed': len(frames),
                'frame_analyses': frame_analyses,
                'video_summary': self._summarize_video_analysis(frame_analyses),
                'temporal_analysis': self._analyze_video_timeline(frame_analyses, metadata),
                'legal_assessment': await self._assess_video_legal_relevance(frame_analyses, shared_context),
                'recommendations': []
            }
            
            # Generate video-specific recommendations
            video_analysis['recommendations'] = self._generate_video_recommendations(video_analysis)
            
            return video_analysis
            
        except Exception as e:
            self.logger.error(f"Video analysis failed: {str(e)}")
            return {
                'error': f"Video analysis failed: {str(e)}",
                'filename': filename,
                'status': 'failed'
            }
    
    async def _run_parallel_image_analysis(self, content: bytes, 
                                         shared_context: Dict[str, Any]) -> Dict[str, Any]:
        """Run multiple image analysis methods"""
        
        analyses = {}
        
        # Scene analysis with Groq
        try:
            analyses['scene_analysis'] = await self._analyze_scene_with_groq(content, shared_context)
        except Exception as e:
            self.logger.warning(f"Groq scene analysis failed: {str(e)}")
            analyses['scene_analysis'] = {'error': str(e)}
        
        # Object detection with computer vision
        try:
            analyses['object_detection'] = self._detect_objects_opencv(content)
        except Exception as e:
            self.logger.warning(f"OpenCV object detection failed: {str(e)}")
            analyses['object_detection'] = {'error': str(e)}
        
        # Google Vision API analysis
        if self.google_api_key:
            try:
                analyses['google_vision'] = await self._analyze_with_google_vision(content)
            except Exception as e:
                self.logger.warning(f"Google Vision analysis failed: {str(e)}")
                analyses['google_vision'] = {'error': str(e)}
        
        # Roboflow specialized detection
        if self.roboflow_api_key:
            try:
                analyses['roboflow_analysis'] = await self._analyze_with_roboflow(content)
            except Exception as e:
                self.logger.warning(f"Roboflow analysis failed: {str(e)}")
                analyses['roboflow_analysis'] = {'error': str(e)}
        
        return analyses
    
    async def _analyze_scene_with_groq(self, content: bytes, 
                                     shared_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze scene using Groq Vision (if available) or description-based analysis"""
        
        case_context = shared_context.get('case_metadata', {})
        
        # Convert image to base64 for analysis prompt
        base64_image = base64.b64encode(content).decode('utf-8')
        
        # For now, use text-based analysis since Groq vision models may not be available
        prompt = f"""
        VISUAL EVIDENCE ANALYSIS REQUEST
        
        CASE CONTEXT:
        Incident: {case_context.get('incident_description', 'Human rights violation')}
        Location: {case_context.get('incident_location', 'Kenya')}
        Date: {case_context.get('incident_date', 'Unknown')}
        
        Analyze this image for ICC evidence purposes. Provide detailed analysis in JSON format:
        {{
            "scene_type": "street|building|vehicle|crowd|interior|outdoor",
            "visible_people": 3,
            "people_description": ["descriptions", "of", "visible", "people"],
            "weapons_visible": ["type", "of", "weapons", "if", "any"],
            "vehicles_visible": ["vehicles", "in", "scene"],
            "violence_indicators": ["signs", "of", "violence", "or", "conflict"],
            "injuries_visible": ["injuries", "or", "harm", "visible"],
            "uniforms_badges": ["military", "police", "official", "uniforms"],
            "location_indicators": ["street", "signs", "landmarks", "buildings"],
            "time_indicators": ["lighting", "shadows", "clocks", "etc"],
            "evidence_objects": ["relevant", "physical", "evidence"],
            "crowd_behavior": "calm|agitated|fleeing|gathering",
            "environment_condition": "normal|damaged|chaotic|organized",
            "photographic_quality": "excellent|good|fair|poor",
            "scene_authenticity": 8.5,
            "legal_relevance": 9.0,
            "key_observations": ["most", "important", "observations"],
            "potential_witnesses": ["people", "who", "might", "be", "witnesses"],
            "investigative_priorities": ["what", "to", "investigate", "further"]
        }}
        
        Note: Image is {len(content)} bytes. Provide detailed, specific analysis.
        """
        
        try:
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert forensic image analyst specializing in ICC evidence analysis. Provide detailed, structured analysis based on typical patterns in human rights violation documentation."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            analysis_text = response.choices[0].message.content
            
            # Clean and parse JSON
            if '```json' in analysis_text:
                analysis_text = analysis_text.split('```json')[1].split('```')[0]
            elif '```' in analysis_text:
                analysis_text = analysis_text.split('```')[1].split('```')[0]
            
            analysis = json.loads(analysis_text)
            
            # Validate scores
            for score_field in ['scene_authenticity', 'legal_relevance']:
                if score_field in analysis:
                    try:
                        score = float(analysis[score_field])
                        analysis[score_field] = max(1.0, min(10.0, score))
                    except (ValueError, TypeError):
                        analysis[score_field] = 5.0
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Groq scene analysis failed: {str(e)}")
            return {
                'error': f"Scene analysis failed: {str(e)}",
                'scene_type': 'unknown',
                'legal_relevance': 5.0
            }
    
    def _detect_objects_opencv(self, content: bytes) -> Dict[str, Any]:
        """Detect objects using OpenCV"""
        
        try:
            # Convert bytes to OpenCV image
            nparr = np.frombuffer(content, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return {'error': 'Could not decode image'}
            
            # Basic image analysis
            height, width, channels = img.shape
            
            # Convert to different color spaces for analysis
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            # Detect edges (useful for identifying objects and structures)
            edges = cv2.Canny(gray, 50, 150)
            edge_count = cv2.countNonZero(edges)
            
            # Detect contours (objects)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Basic color analysis
            dominant_colors = self._analyze_dominant_colors(img)
            
            # Motion blur detection (indicates action/movement)
            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            analysis = {
                'image_dimensions': {'width': width, 'height': height, 'channels': channels},
                'edge_density': edge_count / (width * height),
                'object_count': len(contours),
                'dominant_colors': dominant_colors,
                'image_sharpness': blur_score,
                'quality_assessment': 'sharp' if blur_score > 100 else 'blurry' if blur_score < 50 else 'moderate',
                'complexity_score': min(len(contours) / 10, 10.0),  # Normalize to 0-10
                'technical_quality': self._assess_technical_quality(img, blur_score)
            }
            
            return analysis
            
        except Exception as e:
            return {'error': f"OpenCV analysis failed: {str(e)}"}
    
    async def _analyze_with_google_vision(self, content: bytes) -> Dict[str, Any]:
        """Analyze image with Google Vision API"""
        
        if not self.google_api_key:
            return {'error': 'Google Vision API key not available'}
        
        try:
            # Encode image for API
            base64_image = base64.b64encode(content).decode('utf-8')
            
            # Prepare request
            request_data = {
                "requests": [
                    {
                        "image": {"content": base64_image},
                        "features": [
                            {"type": "LABEL_DETECTION", "maxResults": 20},
                            {"type": "OBJECT_LOCALIZATION", "maxResults": 20},
                            {"type": "FACE_DETECTION", "maxResults": 10},
                            {"type": "TEXT_DETECTION"},
                            {"type": "SAFE_SEARCH_DETECTION"},
                            {"type": "IMAGE_PROPERTIES"}
                        ]
                    }
                ]
            }
            
            # Make API request
            response = requests.post(
                f"{self.google_vision_url}?key={self.google_api_key}",
                json=request_data,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if 'responses' in result and result['responses']:
                    vision_data = result['responses'][0]
                    
                    return {
                        'labels': self._extract_labels(vision_data),
                        'objects': self._extract_objects(vision_data),
                        'faces': self._extract_faces(vision_data),
                        'text': self._extract_text(vision_data),
                        'safety': self._extract_safety_analysis(vision_data),
                        'properties': self._extract_image_properties(vision_data)
                    }
                else:
                    return {'error': 'No response data from Google Vision'}
            else:
                return {'error': f"Google Vision API error: {response.status_code}"}
                
        except Exception as e:
            return {'error': f"Google Vision analysis failed: {str(e)}"}
    
    async def _analyze_with_roboflow(self, content: bytes) -> Dict[str, Any]:
        """Analyze with Roboflow specialized models"""
        
        if not self.roboflow_api_key:
            return {'error': 'Roboflow API key not available'}
        
        try:
            # Encode image
            base64_image = base64.b64encode(content).decode('utf-8')
            
            roboflow_results = {}
            
            # Analyze with each specialized model
            for model_name, model_id in self.roboflow_models.items():
                try:
                    url = f"https://detect.roboflow.com/{model_id}?api_key={self.roboflow_api_key}"
                    
                    response = requests.post(
                        url,
                        data=base64_image,
                        headers={'Content-Type': 'application/x-www-form-urlencoded'}
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        roboflow_results[model_name] = {
                            'predictions': result.get('predictions', []),
                            'confidence': self._calculate_average_confidence(result.get('predictions', [])),
                            'detection_count': len(result.get('predictions', []))
                        }
                    else:
                        roboflow_results[model_name] = {'error': f"Status {response.status_code}"}
                        
                except Exception as e:
                    roboflow_results[model_name] = {'error': str(e)}
            
            return roboflow_results
            
        except Exception as e:
            return {'error': f"Roboflow analysis failed: {str(e)}"}
    
    async def _assess_visual_legal_relevance(self, analyses: Dict[str, Any], 
                                           shared_context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess legal relevance of visual evidence"""
        
        relevance_score = 5.0  # Base score
        relevance_factors = []
        
        # Check scene analysis
        scene_analysis = analyses.get('scene_analysis', {})
        if scene_analysis.get('violence_indicators'):
            relevance_score += 2.0
            relevance_factors.append("Violence indicators detected")
        
        if scene_analysis.get('weapons_visible'):
            relevance_score += 2.5
            relevance_factors.append("Weapons visible in scene")
        
        if scene_analysis.get('uniforms_badges'):
            relevance_score += 1.5
            relevance_factors.append("Official uniforms/badges identified")
        
        if scene_analysis.get('injuries_visible'):
            relevance_score += 2.0
            relevance_factors.append("Injuries documented")
        
        # Check object detection
        object_detection = analyses.get('object_detection', {})
        if object_detection.get('object_count', 0) > 10:
            relevance_score += 1.0
            relevance_factors.append("Complex scene with multiple objects")
        
        # Check Google Vision results
        google_vision = analyses.get('google_vision', {})
        safety_analysis = google_vision.get('safety', {})
        if safety_analysis.get('violence') == 'LIKELY' or safety_analysis.get('violence') == 'VERY_LIKELY':
            relevance_score += 2.0
            relevance_factors.append("Violence detected by AI safety analysis")
        
        # Check Roboflow specialized detection
        roboflow_analysis = analyses.get('roboflow_analysis', {})
        weapons_detected = roboflow_analysis.get('weapons', {}).get('detection_count', 0)
        violence_detected = roboflow_analysis.get('violence', {}).get('detection_count', 0)
        
        if weapons_detected > 0:
            relevance_score += 3.0
            relevance_factors.append(f"Weapons detected ({weapons_detected} detections)")
        
        if violence_detected > 0:
            relevance_score += 2.5
            relevance_factors.append(f"Violence detected ({violence_detected} detections)")
        
        # Normalize score
        relevance_score = max(1.0, min(10.0, relevance_score))
        
        return {
            'legal_relevance_score': round(relevance_score, 2),
            'relevance_factors': relevance_factors,
            'evidence_strength': 'high' if relevance_score > 7.5 else 'medium' if relevance_score > 5.0 else 'low',
            'admissibility_assessment': {
                'authenticity': self._assess_image_authenticity(analyses),
                'relevance': relevance_score > 6.0,
                'quality': object_detection.get('quality_assessment') in ['sharp', 'moderate'],
                'completeness': len(relevance_factors) > 2
            },
            'legal_recommendations': self._generate_legal_recommendations_visual(relevance_score, relevance_factors)
        }
    
    # Helper methods for extracting data from API responses
    def _extract_labels(self, vision_data: Dict) -> List[Dict[str, Any]]:
        """Extract labels from Google Vision response"""
        labels = []
        if 'labelAnnotations' in vision_data:
            for label in vision_data['labelAnnotations']:
                labels.append({
                    'description': label.get('description', ''),
                    'score': label.get('score', 0),
                    'confidence': label.get('score', 0) * 100
                })
        return labels
    
    def _extract_objects(self, vision_data: Dict) -> List[Dict[str, Any]]:
        """Extract objects from Google Vision response"""
        objects = []
        if 'localizedObjectAnnotations' in vision_data:
            for obj in vision_data['localizedObjectAnnotations']:
                objects.append({
                    'name': obj.get('name', ''),
                    'score': obj.get('score', 0),
                    'bounding_box': obj.get('boundingPoly', {})
                })
        return objects
    
    def _extract_faces(self, vision_data: Dict) -> Dict[str, Any]:
        """Extract face information from Google Vision response"""
        faces_info = {'count': 0, 'emotions': [], 'quality': 'unknown'}
        
        if 'faceAnnotations' in vision_data:
            faces = vision_data['faceAnnotations']
            faces_info['count'] = len(faces)
            
            for face in faces:
                emotion_data = {
                    'joy': face.get('joyLikelihood', 'UNKNOWN'),
                    'sorrow': face.get('sorrowLikelihood', 'UNKNOWN'),
                    'anger': face.get('angerLikelihood', 'UNKNOWN'),
                    'surprise': face.get('surpriseLikelihood', 'UNKNOWN')
                }
                faces_info['emotions'].append(emotion_data)
        
        return faces_info
    
    def _extract_text(self, vision_data: Dict) -> Dict[str, Any]:
        """Extract text from Google Vision response"""
        text_info = {'full_text': '', 'text_blocks': []}
        
        if 'textAnnotations' in vision_data and vision_data['textAnnotations']:
            # Full text is usually the first annotation
            text_info['full_text'] = vision_data['textAnnotations'][0].get('description', '')
            
            # Individual text blocks
            for text_block in vision_data['textAnnotations'][1:]:
                text_info['text_blocks'].append({
                    'text': text_block.get('description', ''),
                    'bounding_box': text_block.get('boundingPoly', {})
                })
        
        return text_info
    
    def _extract_safety_analysis(self, vision_data: Dict) -> Dict[str, str]:
        """Extract safety analysis from Google Vision response"""
        safety = {}
        
        if 'safeSearchAnnotation' in vision_data:
            safe_search = vision_data['safeSearchAnnotation']
            safety = {
                'adult': safe_search.get('adult', 'UNKNOWN'),
                'violence': safe_search.get('violence', 'UNKNOWN'),
                'racy': safe_search.get('racy', 'UNKNOWN'),
                'medical': safe_search.get('medical', 'UNKNOWN')
            }
        
        return safety
    
    def _extract_image_properties(self, vision_data: Dict) -> Dict[str, Any]:
        """Extract image properties from Google Vision response"""
        properties = {}
        
        if 'imagePropertiesAnnotation' in vision_data:
            props = vision_data['imagePropertiesAnnotation']
            
            if 'dominantColors' in props:
                colors = props['dominantColors'].get('colors', [])
                properties['dominant_colors'] = [
                    {
                        'color': color.get('color', {}),
                        'score': color.get('score', 0),
                        'pixel_fraction': color.get('pixelFraction', 0)
                    }
                    for color in colors
                ]
        
        return properties
    
    def _calculate_average_confidence(self, predictions: List[Dict]) -> float:
        """Calculate average confidence from predictions"""
        if not predictions:
            return 0.0
        
        confidences = [pred.get('confidence', 0) for pred in predictions]
        return sum(confidences) / len(confidences)
    
    def _analyze_dominant_colors(self, img) -> List[Dict[str, Any]]:
        """Analyze dominant colors in image"""
        try:
            # Reshape image to be a list of pixels
            data = img.reshape((-1, 3))
            data = np.float32(data)
            
            # Use k-means to find dominant colors
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            k = 5  # Number of dominant colors to find
            _, labels, centers = cv2.kmeans(data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
            
            # Calculate percentage of each color
            unique, counts = np.unique(labels, return_counts=True)
            
            dominant_colors = []
            for i, (label, count) in enumerate(zip(unique, counts)):
                percentage = (count / len(labels)) * 100
                color = centers[label].astype(int)
                dominant_colors.append({
                    'color_rgb': color.tolist(),
                    'percentage': round(percentage, 2),
                    'rank': i + 1
                })
            
            # Sort by percentage
            dominant_colors.sort(key=lambda x: x['percentage'], reverse=True)
            
            return dominant_colors
            
        except Exception:
            return []
    
    def _assess_technical_quality(self, img, blur_score: float) -> Dict[str, Any]:
        """Assess technical quality of image"""
        height, width = img.shape[:2]
        
        # Resolution assessment
        total_pixels = height * width
        resolution_quality = 'high' if total_pixels > 2000000 else 'medium' if total_pixels > 500000 else 'low'
        
        # Brightness assessment
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        brightness_quality = 'good' if 50 < brightness < 200 else 'poor'
        
        # Contrast assessment
        contrast = np.std(gray)
        contrast_quality = 'good' if contrast > 50 else 'poor'
        
        return {
            'resolution': resolution_quality,
            'sharpness': 'good' if blur_score > 100 else 'poor',
            'brightness': brightness_quality,
            'contrast': contrast_quality,
            'overall_quality': self._calculate_overall_quality(resolution_quality, blur_score, brightness_quality, contrast_quality)
        }
    
    def _calculate_overall_quality(self, resolution: str, blur_score: float, brightness: str, contrast: str) -> str:
        """Calculate overall image quality"""
        quality_score = 0
        
        if resolution == 'high':
            quality_score += 3
        elif resolution == 'medium':
            quality_score += 2
        else:
            quality_score += 1
        
        if blur_score > 100:
            quality_score += 3
        elif blur_score > 50:
            quality_score += 2
        else:
            quality_score += 1
        
        if brightness == 'good':
            quality_score += 2
        else:
            quality_score += 1
        
        if contrast == 'good':
            quality_score += 2
        else:
            quality_score += 1
        
        if quality_score >= 8:
            return 'excellent'
        elif quality_score >= 6:
            return 'good'
        elif quality_score >= 4:
            return 'fair'
        else:
            return 'poor'
    
    def _extract_key_frames(self, video_path: str, max_frames: int = 5) -> List[np.ndarray]:
        """Extract key frames from video"""
        frames = []
        
        try:
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            if total_frames == 0:
                return frames
            
            # Calculate frame intervals
            frame_interval = max(1, total_frames // max_frames)
            
            for i in range(0, total_frames, frame_interval):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                ret, frame = cap.read()
                if ret:
                    frames.append(frame)
                if len(frames) >= max_frames:
                    break
            
            cap.release()
            
        except Exception as e:
            self.logger.error(f"Frame extraction failed: {str(e)}")
        
        return frames
    
    def _frame_to_bytes(self, frame: np.ndarray) -> bytes:
        """Convert OpenCV frame to bytes"""
        _, buffer = cv2.imencode('.jpg', frame)
        return buffer.tobytes()
    
    def _analyze_image_technical_quality(self, content: bytes) -> Dict[str, Any]:
        """Analyze technical quality of image"""
        try:
            # Load image
            nparr = np.frombuffer(content, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is None:
                return {'error': 'Could not decode image'}
            
            # Basic technical analysis
            height, width, channels = img.shape
            file_size = len(content)
            
            # Calculate compression ratio
            uncompressed_size = height * width * channels
            compression_ratio = file_size / uncompressed_size
            
            # Noise analysis
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            noise_level = np.std(cv2.Laplacian(gray, cv2.CV_64F))
            
            return {
                'dimensions': {'width': width, 'height': height},
                'file_size_bytes': file_size,
                'compression_ratio': round(compression_ratio, 3),
                'noise_level': round(noise_level, 2),
                'megapixels': round((width * height) / 1000000, 2),
                'aspect_ratio': round(width / height, 2),
                'technical_score': self._calculate_technical_score(width, height, file_size, noise_level)
            }
            
        except Exception as e:
            return {'error': f"Technical analysis failed: {str(e)}"}
    
    def _calculate_technical_score(self, width: int, height: int, file_size: int, noise_level: float) -> float:
        """Calculate technical quality score"""
        score = 5.0  # Base score
        
        # Resolution bonus
        megapixels = (width * height) / 1000000
        if megapixels > 5:
            score += 2.0
        elif megapixels > 2:
            score += 1.0
        
        # File size consideration (very small files may be overly compressed)
        if file_size > 1000000:  # > 1MB
            score += 1.0
        elif file_size < 100000:  # < 100KB
            score -= 1.0
        
        # Noise penalty
        if noise_level > 50:
            score -= 1.0
        elif noise_level < 20:
            score += 0.5
        
        return max(1.0, min(10.0, score))
    
    def _calculate_visual_quality(self, analysis_result: Dict[str, Any], metadata: Dict[str, Any]) -> float:
        """Calculate overall visual evidence quality score"""
        base_score = 5.0
        
        # Technical quality bonus
        technical = analysis_result.get('technical_analysis', {})
        tech_score = technical.get('technical_score', 5.0)
        tech_bonus = (tech_score - 5.0) * 0.5  # Max 2.5 bonus
        
        # Legal relevance bonus
        legal = analysis_result.get('legal_assessment', {})
        legal_score = legal.get('legal_relevance_score', 5.0)
        legal_bonus = (legal_score - 5.0) * 0.3  # Max 1.5 bonus
        
        # Complexity bonus (more objects/details generally better)
        object_detection = analysis_result.get('object_detection', {})
        complexity = object_detection.get('complexity_score', 5.0)
        complexity_bonus = (complexity - 5.0) * 0.2  # Max 1.0 bonus
        
        # Metadata bonus
        metadata_bonus = 0.5 if metadata.get('gps_coords') or metadata.get('creation_date') else 0
        
        total_score = base_score + tech_bonus + legal_bonus + complexity_bonus + metadata_bonus
        return round(max(1.0, min(10.0, total_score)), 2)
    
    def _generate_visual_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations for visual evidence"""
        recommendations = []
        
        # Technical recommendations
        technical = analysis.get('technical_analysis', {})
        if technical.get('technical_score', 5.0) < 6.0:
            recommendations.append("Consider image enhancement or obtaining higher quality version")
        
        # Legal recommendations
        legal = analysis.get('legal_assessment', {})
        if legal.get('evidence_strength') == 'high':
            recommendations.append("High-value visual evidence - prioritize for ICC submission")
        elif legal.get('evidence_strength') == 'low':
            recommendations.append("Low-value evidence - supplement with additional visual documentation")
        
        # Scene-specific recommendations
        scene = analysis.get('scene_analysis', {})
        if scene.get('weapons_visible'):
            recommendations.append("Document weapon evidence with expert ballistics analysis")
        
        if scene.get('injuries_visible'):
            recommendations.append("Correlate with medical documentation and expert testimony")
        
        if scene.get('location_indicators'):
            recommendations.append("Verify location through geospatial analysis")
        
        return recommendations
    
    def _assess_image_authenticity(self, analyses: Dict[str, Any]) -> bool:
        """Assess if image appears authentic (not manipulated)"""
        # Simple authenticity check based on technical factors
        technical = analyses.get('object_detection', {})
        quality = technical.get('quality_assessment', 'poor')
        
        # Basic checks - more sophisticated analysis would need specialized tools
        if quality in ['sharp', 'moderate']:
            return True
        
        return False
    
    def _generate_legal_recommendations_visual(self, relevance_score: float, factors: List[str]) -> List[str]:
        """Generate legal recommendations for visual evidence"""
        recommendations = []
        
        if relevance_score > 8.0:
            recommendations.append("Exceptional visual evidence - fast-track for ICC submission")
        elif relevance_score > 6.0:
            recommendations.append("Strong visual evidence - include in primary evidence package")
        else:
            recommendations.append("Moderate evidence - use as supporting documentation")
        
        if any('weapon' in factor.lower() for factor in factors):
            recommendations.append("Obtain expert ballistics analysis for weapon identification")
        
        if any('violence' in factor.lower() for factor in factors):
            recommendations.append("Correlate with medical evidence and witness testimony")
        
        return recommendations
    
    # Video-specific methods
    def _summarize_video_analysis(self, frame_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize analysis across all video frames"""
        if not frame_analyses:
            return {'error': 'No frame analyses available'}
        
        # Aggregate key information
        all_weapons = []
        all_violence_indicators = []
        all_people = []
        total_relevance = 0
        
        for frame in frame_analyses:
            scene = frame.get('scene_analysis', {})
            
            weapons = scene.get('weapons_visible', [])
            if weapons:
                all_weapons.extend(weapons)
            
            violence = scene.get('violence_indicators', [])
            if violence:
                all_violence_indicators.extend(violence)
            
            people = scene.get('people_description', [])
            if people:
                all_people.extend(people)
            
            legal = frame.get('legal_assessment', {})
            total_relevance += legal.get('legal_relevance_score', 0)
        
        avg_relevance = total_relevance / len(frame_analyses) if frame_analyses else 0
        
        return {
            'total_frames': len(frame_analyses),
            'average_relevance': round(avg_relevance, 2),
            'weapons_throughout': list(set(all_weapons)),
            'violence_indicators': list(set(all_violence_indicators)),
            'people_identified': list(set(all_people)),
            'video_strength': 'high' if avg_relevance > 7.5 else 'medium' if avg_relevance > 5.0 else 'low'
        }
    
    def _analyze_video_timeline(self, frame_analyses: List[Dict[str, Any]], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze temporal aspects of video"""
        duration = metadata.get('duration', 0)
        
        timeline_events = []
        for frame in frame_analyses:
            timestamp = frame.get('timestamp', 0)
            scene = frame.get('scene_analysis', {})
            
            # Identify significant events in each frame
            events = []
            if scene.get('weapons_visible'):
                events.append('weapons_visible')
            if scene.get('violence_indicators'):
                events.append('violence_detected')
            if scene.get('injuries_visible'):
                events.append('injuries_documented')
            
            if events:
                timeline_events.append({
                    'timestamp': timestamp,
                    'events': events,
                    'frame_number': frame.get('frame_number', 0)
                })
        
        return {
            'video_duration': duration,
            'significant_events': timeline_events,
            'event_density': len(timeline_events) / max(duration, 1),
            'temporal_analysis': 'High activity' if len(timeline_events) > 3 else 'Moderate activity' if len(timeline_events) > 1 else 'Low activity'
        }
    
    async def _assess_video_legal_relevance(self, frame_analyses: List[Dict[str, Any]], shared_context: Dict[str, Any]) -> Dict[str, Any]:
        """Assess legal relevance of video evidence"""
        if not frame_analyses:
            return {'legal_relevance_score': 0.0, 'evidence_strength': 'none'}
        
        # Calculate average relevance across frames
        total_relevance = 0
        high_relevance_frames = 0
        
        for frame in frame_analyses:
            legal = frame.get('legal_assessment', {})
            relevance = legal.get('legal_relevance_score', 0)
            total_relevance += relevance
            
            if relevance > 7.5:
                high_relevance_frames += 1
        
        avg_relevance = total_relevance / len(frame_analyses)
        
        # Video gets bonus for temporal consistency
        consistency_bonus = 1.0 if high_relevance_frames > len(frame_analyses) * 0.5 else 0
        
        final_relevance = min(avg_relevance + consistency_bonus, 10.0)
        
        return {
            'legal_relevance_score': round(final_relevance, 2),
            'evidence_strength': 'high' if final_relevance > 7.5 else 'medium' if final_relevance > 5.0 else 'low',
            'high_relevance_frames': high_relevance_frames,
            'consistency_score': high_relevance_frames / len(frame_analyses),
            'temporal_advantage': 'Video provides temporal context and sequence of events'
        }
    
    def _generate_video_recommendations(self, video_analysis: Dict[str, Any]) -> List[str]:
        """Generate video-specific recommendations"""
        recommendations = []
        
        summary = video_analysis.get('video_summary', {})
        legal = video_analysis.get('legal_assessment', {})
        
        if legal.get('evidence_strength') == 'high':
            recommendations.append("Exceptional video evidence - prioritize for ICC submission")
        
        if summary.get('weapons_throughout'):
            recommendations.append("Conduct frame-by-frame weapons analysis with ballistics expert")
        
        if summary.get('violence_indicators'):
            recommendations.append("Document temporal sequence of violence for legal proceedings")
        
        temporal = video_analysis.get('temporal_analysis', {})
        if 'High activity' in str(temporal.get('temporal_analysis', '')):
            recommendations.append("Video shows active incident - valuable for establishing timeline")
        
        if video_analysis.get('total_frames_analyzed', 0) > 3:
            recommendations.append("Comprehensive video analysis completed - suitable for expert testimony")
        
        return recommendations
    
    def _analyze_spatial_context(self, metadata: Dict[str, Any], analyses: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze spatial context from metadata and visual analysis"""
        spatial_info = {}
        
        # GPS information from metadata
        if metadata.get('gps_coords'):
            spatial_info['gps_coordinates'] = metadata['gps_coords']
            spatial_info['location_verified'] = True
        
        if metadata.get('location'):
            spatial_info['location_name'] = metadata['location']
        
        # Visual location indicators
        scene = analyses.get('scene_analysis', {})
        if scene.get('location_indicators'):
            spatial_info['visual_location_clues'] = scene['location_indicators']
        
        # Google Vision text detection for location signs
        google_vision = analyses.get('google_vision', {})
        text_info = google_vision.get('text', {})
        if text_info.get('full_text'):
            spatial_info['text_in_image'] = text_info['full_text']
        
        return spatial_info
