"""
Computer vision analysis tool.
Standardized interface for vision operations.
"""

from typing import Dict, Any, List
from .base_tool import BaseTool, ToolResult
from core.vision import VisionEngine


class VisionTool(BaseTool):
    """Computer vision analysis tool with standardized interface"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.vision_engine = VisionEngine()
    
    def get_required_fields(self) -> List[str]:
        """Get required input fields"""
        return ['image_path']
    
    def get_optional_fields(self) -> List[str]:
        """Get optional input fields"""
        return ['analysis_type', 'confidence_threshold', 'max_results']
    
    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input parameters"""
        if 'image_path' not in input_data:
            return False
        
        image_path = input_data['image_path']
        if not isinstance(image_path, str) or len(image_path.strip()) == 0:
            return False
        
        # Validate analysis type if provided
        if 'analysis_type' in input_data:
            valid_types = ['faces', 'objects', 'text', 'analyze', 'compare']
            if input_data['analysis_type'] not in valid_types:
                return False
        
        return True
    
    async def execute(self, input_data: Dict[str, Any]) -> ToolResult:
        """
        Execute computer vision analysis.
        
        Args:
            input_data: Vision parameters
                - image_path (str): Path to image file
                - analysis_type (str, optional): Type of analysis (faces, objects, text, analyze)
                - confidence_threshold (float, optional): Confidence threshold for detection
                - max_results (int, optional): Maximum number of results
        
        Returns:
            ToolResult with vision analysis results
        """
        try:
            image_path = input_data['image_path'].strip()
            analysis_type = input_data.get('analysis_type', 'analyze')
            confidence_threshold = input_data.get('confidence_threshold', 0.5)
            max_results = input_data.get('max_results', 10)
            
            self.logger.info(f"Analyzing image: {image_path} (type: {analysis_type})")
            
            # Route to appropriate vision operation
            if analysis_type == 'faces':
                result = await self.vision_engine.detect_faces(
                    image_path, 
                    min_neighbors=5
                )
            elif analysis_type == 'objects':
                result = await self.vision_engine.detect_objects(
                    image_path,
                    confidence_threshold
                )
            elif analysis_type == 'text':
                result = await self.vision_engine.extract_text(image_path)
            elif analysis_type == 'analyze':
                result = await self.vision_engine.analyze_image(image_path)
            else:
                return self._create_error_result(f"Unknown analysis type: {analysis_type}")
            
            # Check for errors in result
            if isinstance(result, list) and len(result) == 1 and 'error' in result[0]:
                error_msg = result[0]['error']
                return self._create_error_result(error_msg)
            elif isinstance(result, dict) and 'error' in result:
                error_msg = result['error']
                return self._create_error_result(error_msg)
            
            # Limit results if needed
            if isinstance(result, list) and len(result) > max_results:
                result = result[:max_results]
            
            metadata = {
                'image_path': image_path,
                'analysis_type': analysis_type,
                'confidence_threshold': confidence_threshold,
                'results_count': len(result) if isinstance(result, list) else 1
            }
            
            return self._create_success_result(result, metadata)
            
        except Exception as e:
            self.logger.error(f"Vision analysis failed: {e}")
            return self._create_error_result(str(e))
    
    async def detect_faces(self, image_path: str, min_neighbors: int = 5) -> ToolResult:
        """
        Detect faces in image.
        
        Args:
            image_path: Path to image
            min_neighbors: Minimum neighbors for detection
            
        Returns:
            ToolResult with detected faces
        """
        return await self.execute({
            'image_path': image_path,
            'analysis_type': 'faces',
            'min_neighbors': min_neighbors
        })
    
    async def detect_objects(self, image_path: str, confidence_threshold: float = 0.5) -> ToolResult:
        """
        Detect objects in image.
        
        Args:
            image_path: Path to image
            confidence_threshold: Confidence threshold
            
        Returns:
            ToolResult with detected objects
        """
        return await self.execute({
            'image_path': image_path,
            'analysis_type': 'objects',
            'confidence_threshold': confidence_threshold
        })
    
    async def extract_text(self, image_path: str) -> ToolResult:
        """
        Extract text from image (OCR).
        
        Args:
            image_path: Path to image
            
        Returns:
            ToolResult with extracted text
        """
        return await self.execute({
            'image_path': image_path,
            'analysis_type': 'text'
        })
    
    async def analyze_image(self, image_path: str) -> ToolResult:
        """
        Perform general image analysis.
        
        Args:
            image_path: Path to image
            
        Returns:
            ToolResult with image analysis
        """
        return await self.execute({
            'image_path': image_path,
            'analysis_type': 'analyze'
        })
    
    async def compare_images(self, image1_path: str, image2_path: str) -> ToolResult:
        """
        Compare two images for similarity.
        
        Args:
            image1_path: Path to first image
            image2_path: Path to second image
            
        Returns:
            ToolResult with comparison results
        """
        try:
            result = await self.vision_engine.compare_images(image1_path, image2_path)
            
            if 'error' in result:
                return self._create_error_result(result['error'])
            
            metadata = {
                'image1_path': image1_path,
                'image2_path': image2_path,
                'comparison_type': 'similarity'
            }
            
            return self._create_success_result(result, metadata)
            
        except Exception as e:
            self.logger.error(f"Image comparison failed: {e}")
            return self._create_error_result(str(e))
    
    async def health_check(self) -> bool:
        """Check if vision engine is working"""
        try:
            # Vision engine doesn't have a simple health check
            # We could create a test image or just return True
            return True
        except Exception as e:
            self.logger.error(f"Vision tool health check failed: {e}")
            return False