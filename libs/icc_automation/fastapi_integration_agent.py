"""
⚡ FASTAPI INTEGRATION CORE AGENT
Specialized agent for backend API communication and fast analysis
Part of the 5-agent intelligent consolidation system

AGENT RESPONSIBILITIES:
- FastAPI backend health monitoring
- High-speed evidence analysis via API endpoints
- Request/response optimization and caching
- Real-time progress tracking and monitoring
- Data visualization and analytics
- Error handling and fallback mechanisms
- Performance metrics and benchmarking

This is CORE AGENT #4 - focused solely on backend integration capabilities
"""

import streamlit as st
import requests
import json
import time
import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import hashlib

class FastAPIIntegrationAgent:
    """
    ⚡ CORE AGENT #4: Advanced FastAPI Backend Integration
    
    This agent specializes in:
    - High-performance API communication
    - Intelligent caching and optimization
    - Real-time progress monitoring
    - Analytics and data visualization
    - Health monitoring and diagnostics
    - Async operations for speed
    - Comprehensive error handling
    """
    
    def __init__(self, base_url: str = "http://localhost:8001", timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.performance_metrics = []
        
        # API endpoint mapping
        self.endpoints = {
            'health': '/health',
            'analyze_evidence': '/analyze-evidence/',
            'analyze_batch': '/analyze-batch/',
            'get_analysis': '/analysis/{analysis_id}',
            'models': '/models',
            'capabilities': '/capabilities',
            'metrics': '/metrics'
        }
        
        # Initialize session state for caching
        if 'api_cache' not in st.session_state:
            st.session_state.api_cache = {}
        if 'performance_data' not in st.session_state:
            st.session_state.performance_data = []
    
    def check_backend_health(self) -> Tuple[bool, Dict]:
        """
        🏥 Comprehensive backend health check
        
        Returns:
            Tuple[bool, Dict]: (is_healthy, health_data)
        """
        try:
            start_time = time.time()
            
            response = self.session.get(
                f"{self.base_url}{self.endpoints['health']}", 
                timeout=5
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                health_data = response.json()
                health_data['response_time'] = response_time
                health_data['timestamp'] = datetime.now().isoformat()
                
                # Store performance metric
                self._record_performance('health_check', response_time, True)
                
                return True, health_data
            else:
                return False, {
                    'error': f"Health check failed with status {response.status_code}",
                    'response_time': response_time
                }
                
        except requests.exceptions.ConnectionError:
            return False, {'error': 'Backend not reachable - connection refused'}
        except requests.exceptions.Timeout:
            return False, {'error': 'Backend health check timed out'}
        except Exception as e:
            return False, {'error': f"Health check failed: {str(e)}"}
    
    def get_backend_capabilities(self) -> Optional[Dict]:
        """
        🛠️ Get backend AI model capabilities and features
        
        Returns:
            Dict: Backend capabilities or None if failed
        """
        try:
            response = self.session.get(
                f"{self.base_url}{self.endpoints['capabilities']}", 
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                capabilities = response.json()
                
                # Cache capabilities
                st.session_state.api_cache['capabilities'] = {
                    'data': capabilities,
                    'timestamp': datetime.now().isoformat()
                }
                
                return capabilities
            else:
                st.error(f"Failed to get capabilities: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"Error getting backend capabilities: {str(e)}")
            return None
    
    def analyze_evidence_fast(self, uploaded_file, show_progress: bool = True) -> Tuple[Optional[Dict], bool]:
        """
        🚀 Lightning-fast evidence analysis with caching
        
        Args:
            uploaded_file: Streamlit uploaded file object
            show_progress: Whether to show progress indicators
            
        Returns:
            Tuple[Optional[Dict], bool]: (analysis_result, from_cache)
        """
        try:
            # Generate file hash for caching
            file_content = uploaded_file.getvalue()
            file_hash = hashlib.md5(file_content).hexdigest()
            
            # Check cache first
            cache_key = f"analysis_{file_hash}"
            if cache_key in st.session_state.api_cache:
                cached_data = st.session_state.api_cache[cache_key]
                if show_progress:
                    st.success("⚡ Retrieved from cache (instant)")
                return cached_data['result'], True
            
            # Prepare file for API
            files = {
                "file": (uploaded_file.name, file_content, uploaded_file.type)
            }
            
            # Show progress if requested
            progress_container = None
            if show_progress:
                progress_container = st.container()
                with progress_container:
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                status_text.text("🚀 Uploading to AI analysis engine...")
                progress_bar.progress(25)
            
            # Send to FastAPI backend
            start_time = time.time()
            
            response = self.session.post(
                f"{self.base_url}{self.endpoints['analyze_evidence']}", 
                files=files, 
                timeout=self.timeout
            )
            
            analysis_time = time.time() - start_time
            
            if show_progress:
                progress_bar.progress(75)
                status_text.text("🤖 AI models processing evidence...")
            
            if response.status_code == 200:
                result = response.json()
                result['analysis_time'] = analysis_time
                result['file_hash'] = file_hash
                
                # Cache result
                st.session_state.api_cache[cache_key] = {
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                }
                
                # Record performance
                self._record_performance('analyze_evidence', analysis_time, True)
                
                if show_progress:
                    progress_bar.progress(100)
                    status_text.text(f"✅ Analysis complete in {analysis_time:.2f}s")
                    time.sleep(1)
                    if progress_container:
                        progress_container.empty()
                
                return result, False
                
            else:
                error_msg = f"Analysis failed: HTTP {response.status_code}"
                if show_progress:
                    st.error(error_msg)
                
                self._record_performance('analyze_evidence', analysis_time, False)
                return None, False
                
        except requests.exceptions.Timeout:
            error_msg = "⏰ Analysis timeout - file too large or server overloaded"
            if show_progress:
                st.error(error_msg)
            self._record_performance('analyze_evidence', self.timeout, False)
            return None, False
            
        except requests.exceptions.ConnectionError:
            error_msg = "🔌 Backend connection failed - is the API server running?"
            if show_progress:
                st.error(error_msg)
            return None, False
            
        except Exception as e:
            error_msg = f"❌ Analysis error: {str(e)}"
            if show_progress:
                st.error(error_msg)
            return None, False
    
    async def analyze_batch_async(self, files: List, batch_size: int = 5) -> List[Dict]:
        """
        📦 Async batch analysis for multiple files
        
        Args:
            files: List of uploaded file objects
            batch_size: Number of files to process concurrently
            
        Returns:
            List[Dict]: Analysis results for all files
        """
        results = []
        
        # Process files in batches
        for i in range(0, len(files), batch_size):
            batch = files[i:i + batch_size]
            
            # Create async tasks for batch
            async with aiohttp.ClientSession() as session:
                tasks = []
                for file in batch:
                    task = self._analyze_file_async(session, file)
                    tasks.append(task)
                
                # Execute batch
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        results.append({
                            'filename': batch[j].name,
                            'error': str(result),
                            'success': False
                        })
                    else:
                        results.append(result)
        
        return results
    
    async def _analyze_file_async(self, session: aiohttp.ClientSession, file) -> Dict:
        """Async file analysis helper"""
        try:
            file_content = file.getvalue()
            
            data = aiohttp.FormData()
            data.add_field('file', file_content, filename=file.name, content_type=file.type)
            
            async with session.post(
                f"{self.base_url}{self.endpoints['analyze_evidence']}", 
                data=data,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                
                if response.status == 200:
                    result = await response.json()
                    result['filename'] = file.name
                    result['success'] = True
                    return result
                else:
                    return {
                        'filename': file.name,
                        'error': f"HTTP {response.status}",
                        'success': False
                    }
                    
        except Exception as e:
            return {
                'filename': file.name,
                'error': str(e),
                'success': False
            }
    
    def get_analysis_by_id(self, analysis_id: str) -> Optional[Dict]:
        """
        🔍 Retrieve analysis results by ID
        
        Args:
            analysis_id: Unique analysis identifier
            
        Returns:
            Dict: Analysis result or None if not found
        """
        try:
            endpoint = self.endpoints['get_analysis'].format(analysis_id=analysis_id)
            response = self.session.get(f"{self.base_url}{endpoint}", timeout=self.timeout)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                st.error(f"Analysis {analysis_id} not found")
                return None
            else:
                st.error(f"Failed to retrieve analysis: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"Error retrieving analysis: {str(e)}")
            return None
    
    def get_performance_metrics(self) -> Dict:
        """
        📊 Get backend performance metrics
        
        Returns:
            Dict: Performance metrics and statistics
        """
        try:
            response = self.session.get(
                f"{self.base_url}{self.endpoints['metrics']}", 
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                # Return local metrics if backend metrics unavailable
                return self._calculate_local_metrics()
                
        except Exception as e:
            st.debug(f"Could not get backend metrics: {str(e)}")
            return self._calculate_local_metrics()
    
    def _calculate_local_metrics(self) -> Dict:
        """Calculate performance metrics from local data"""
        if not st.session_state.performance_data:
            return {'message': 'No performance data available'}
        
        df = pd.DataFrame(st.session_state.performance_data)
        
        metrics = {
            'total_requests': len(df),
            'successful_requests': len(df[df['success'] == True]),
            'failed_requests': len(df[df['success'] == False]),
            'success_rate': len(df[df['success'] == True]) / len(df) * 100,
            'average_response_time': df['response_time'].mean(),
            'min_response_time': df['response_time'].min(),
            'max_response_time': df['response_time'].max(),
            'operations': df.groupby('operation').size().to_dict()
        }
        
        return metrics
    
    def _record_performance(self, operation: str, response_time: float, success: bool):
        """Record performance metric"""
        metric = {
            'operation': operation,
            'response_time': response_time,
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        
        st.session_state.performance_data.append(metric)
        
        # Keep only last 1000 metrics to prevent memory issues
        if len(st.session_state.performance_data) > 1000:
            st.session_state.performance_data = st.session_state.performance_data[-1000:]
    
    def display_backend_status(self):
        """
        📊 Display comprehensive backend status dashboard
        """
        st.subheader("⚡ FastAPI Backend Status")
        
        # Health check
        healthy, health_data = self.check_backend_health()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if healthy:
                st.success("✅ Backend Online")
                if 'response_time' in health_data:
                    st.metric("Response Time", f"{health_data['response_time']:.3f}s")
            else:
                st.error("❌ Backend Offline")
                st.error(health_data.get('error', 'Unknown error'))
        
        with col2:
            if healthy and 'version' in health_data:
                st.info(f"🔧 Version: {health_data.get('version', 'Unknown')}")
            if 'models_loaded' in health_data:
                st.metric("Models Loaded", health_data['models_loaded'])
        
        with col3:
            cache_size = len(st.session_state.api_cache)
            st.metric("Cache Entries", cache_size)
            
            performance_count = len(st.session_state.performance_data)
            st.metric("Recorded Operations", performance_count)
        
        # Performance metrics
        if st.session_state.performance_data:
            with st.expander("📈 Performance Analytics"):
                metrics = self._calculate_local_metrics()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Success Rate", f"{metrics['success_rate']:.1f}%")
                    st.metric("Avg Response Time", f"{metrics['average_response_time']:.3f}s")
                
                with col2:
                    st.metric("Total Requests", metrics['total_requests'])
                    st.metric("Failed Requests", metrics['failed_requests'])
                
                # Performance chart
                if len(st.session_state.performance_data) > 1:
                    df = pd.DataFrame(st.session_state.performance_data)
                    
                    fig = px.line(
                        df, 
                        x='timestamp', 
                        y='response_time',
                        color='operation',
                        title="Response Time Over Time"
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # Cache management
        with st.expander("💾 Cache Management"):
            if st.session_state.api_cache:
                cache_df = pd.DataFrame([
                    {
                        'key': key,
                        'timestamp': data.get('timestamp', 'Unknown'),
                        'type': type(data.get('result', {})).__name__
                    }
                    for key, data in st.session_state.api_cache.items()
                ])
                st.dataframe(cache_df)
                
                if st.button("🗑️ Clear Cache"):
                    st.session_state.api_cache.clear()
                    st.success("Cache cleared successfully!")
                    st.experimental_rerun()
            else:
                st.info("No cached data available")
    
    def display_analysis_results(self, results: Dict, show_raw: bool = False):
        """
        📊 Display analysis results with visualizations
        
        Args:
            results: Analysis results dictionary
            show_raw: Whether to show raw JSON data
        """
        if not results:
            st.error("No analysis results to display")
            return
        
        # Performance metrics
        if 'analysis_time' in results:
            st.success(f"⚡ Analysis completed in {results['analysis_time']:.2f} seconds")
        
        # Main results
        if 'evidence_type' in results:
            st.write(f"**Evidence Type:** {results['evidence_type']}")
        
        if 'confidence_score' in results:
            st.progress(results['confidence_score'] / 100)
            st.write(f"**Confidence:** {results['confidence_score']}%")
        
        # Visualizations
        if 'categories' in results and isinstance(results['categories'], dict):
            # Category confidence chart
            categories = results['categories']
            fig = px.bar(
                x=list(categories.keys()),
                y=list(categories.values()),
                title="Category Confidence Scores"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed analysis
        if 'analysis' in results:
            with st.expander("📋 Detailed Analysis"):
                st.write(results['analysis'])
        
        # Raw data
        if show_raw:
            with st.expander("🗂️ Raw Analysis Data"):
                st.json(results)
    
    def cleanup_cache(self, max_age_hours: int = 24):
        """
        🧹 Clean up old cache entries
        
        Args:
            max_age_hours: Maximum age of cache entries in hours
        """
        current_time = datetime.now()
        cleaned_count = 0
        
        keys_to_remove = []
        
        for key, data in st.session_state.api_cache.items():
            if 'timestamp' in data:
                try:
                    cache_time = datetime.fromisoformat(data['timestamp'])
                    age_hours = (current_time - cache_time).total_seconds() / 3600
                    
                    if age_hours > max_age_hours:
                        keys_to_remove.append(key)
                        cleaned_count += 1
                except:
                    # Remove invalid timestamp entries
                    keys_to_remove.append(key)
                    cleaned_count += 1
        
        for key in keys_to_remove:
            del st.session_state.api_cache[key]
        
        if cleaned_count > 0:
            st.info(f"🧹 Cleaned {cleaned_count} old cache entries")

# Factory function for agent creation
def get_fastapi_agent(base_url: str = "http://localhost:8001", timeout: int = 30):
    """
    🎯 Factory function to create FastAPI integration agent
    
    Args:
        base_url: Base URL of the FastAPI backend
        timeout: Request timeout in seconds
        
    Returns:
        FastAPIIntegrationAgent: Configured integration agent
    """
    return FastAPIIntegrationAgent(base_url=base_url, timeout=timeout)

# Standalone execution for testing
if __name__ == "__main__":
    st.title("⚡ FastAPI Integration Core Agent")
    st.write("Test backend integration and analysis capabilities")
    
    # Configuration
    col1, col2 = st.columns(2)
    
    with col1:
        api_url = st.text_input("API Base URL", value="http://localhost:8001")
    with col2:
        timeout = st.number_input("Timeout (seconds)", value=30, min_value=5, max_value=120)
    
    # Create agent
    agent = get_fastapi_agent(base_url=api_url, timeout=timeout)
    
    # Display status dashboard
    agent.display_backend_status()
    
    # File analysis test
    st.subheader("🧪 Test Evidence Analysis")
    
    uploaded_file = st.file_uploader(
        "Upload test file",
        type=['jpg', 'jpeg', 'png', 'mp4', 'avi', 'mp3', 'wav', 'pdf', 'docx']
    )
    
    if uploaded_file:
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Analyze with Backend"):
                result, from_cache = agent.analyze_evidence_fast(uploaded_file)
                
                if result:
                    cache_indicator = " (from cache)" if from_cache else ""
                    st.success(f"✅ Analysis completed{cache_indicator}")
                    agent.display_analysis_results(result, show_raw=True)
                else:
                    st.error("❌ Analysis failed")
        
        with col2:
            if st.button("📊 Get Backend Capabilities"):
                capabilities = agent.get_backend_capabilities()
                
                if capabilities:
                    st.json(capabilities)
                else:
                    st.error("❌ Could not retrieve capabilities")
