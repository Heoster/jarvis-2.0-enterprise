"""Computer vision capabilities using OpenCV."""

import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import asyncio
from pathlib import Path

from core.logger import get_logger

logger = get_logger(__name__)


class VisionEngine:
    """Computer vision engine using OpenCV."""
    
    def __init__(self):
        """Initialize vision engine."""
        self.face_cascade = None
        self.eye_cascade = None
        self._load_cascades()
        
        logger.info("Vision engine initialized")
    
    def _load_cascades(self):
        """Load Haar cascade classifiers."""
        try:
            # Load pre-trained cascades
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            self.eye_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_eye.xml'
            )
            logger.info("Cascade classifiers loaded")
        except Exception as e:
            logger.error(f"Failed to load cascades: {e}")
    
    async def detect_faces(
        self,
        image_path: str,
        scale_factor: float = 1.1,
        min_neighbors: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Detect faces in an image.
        
        Args:
            image_path: Path to image file
            scale_factor: Scale factor for detection
            min_neighbors: Minimum neighbors for detection
            
        Returns:
            List of detected faces with coordinates
        """
        return await asyncio.to_thread(
            self._detect_faces_sync,
            image_path,
            scale_factor,
            min_neighbors
        )
    
    def _detect_faces_sync(
        self,
        image_path: str,
        scale_factor: float,
        min_neighbors: int
    ) -> List[Dict[str, Any]]:
        """Synchronous face detection."""
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return [{"error": "Failed to load image"}]
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=scale_factor,
                minNeighbors=min_neighbors
            )
            
            results = []
            for (x, y, w, h) in faces:
                results.append({
                    "x": int(x),
                    "y": int(y),
                    "width": int(w),
                    "height": int(h),
                    "confidence": 1.0  # Haar cascades don't provide confidence
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            return [{"error": str(e)}]
    
    async def detect_objects(
        self,
        image_path: str,
        confidence_threshold: float = 0.5
    ) -> List[Dict[str, Any]]:
        """
        Detect objects in an image using basic methods.
        
        Args:
            image_path: Path to image file
            confidence_threshold: Confidence threshold
            
        Returns:
            List of detected objects
        """
        return await asyncio.to_thread(
            self._detect_objects_sync,
            image_path,
            confidence_threshold
        )
    
    def _detect_objects_sync(
        self,
        image_path: str,
        confidence_threshold: float
    ) -> List[Dict[str, Any]]:
        """Synchronous object detection."""
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return [{"error": "Failed to load image"}]
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Detect edges
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(
                edges,
                cv2.RETR_EXTERNAL,
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            results = []
            for i, contour in enumerate(contours[:10]):  # Limit to top 10
                x, y, w, h = cv2.boundingRect(contour)
                area = cv2.contourArea(contour)
                
                if area > 1000:  # Filter small objects
                    results.append({
                        "id": i,
                        "x": int(x),
                        "y": int(y),
                        "width": int(w),
                        "height": int(h),
                        "area": int(area),
                        "type": "object"
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Object detection failed: {e}")
            return [{"error": str(e)}]
    
    async def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze image properties.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Image analysis results
        """
        return await asyncio.to_thread(self._analyze_image_sync, image_path)
    
    def _analyze_image_sync(self, image_path: str) -> Dict[str, Any]:
        """Synchronous image analysis."""
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return {"error": "Failed to load image"}
            
            # Get image properties
            height, width, channels = img.shape
            
            # Calculate color statistics
            mean_color = cv2.mean(img)[:3]
            
            # Detect dominant colors
            pixels = img.reshape(-1, 3)
            pixels = np.float32(pixels)
            
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
            k = 5
            _, labels, centers = cv2.kmeans(
                pixels,
                k,
                None,
                criteria,
                10,
                cv2.KMEANS_RANDOM_CENTERS
            )
            
            dominant_colors = centers.astype(int).tolist()
            
            # Calculate brightness
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            
            return {
                "width": width,
                "height": height,
                "channels": channels,
                "mean_color": {
                    "b": int(mean_color[0]),
                    "g": int(mean_color[1]),
                    "r": int(mean_color[2])
                },
                "dominant_colors": dominant_colors,
                "brightness": float(brightness),
                "aspect_ratio": float(width / height)
            }
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return {"error": str(e)}
    
    async def extract_text(self, image_path: str) -> Dict[str, Any]:
        """
        Extract text from image (OCR).
        Note: Requires pytesseract for full functionality.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted text
        """
        try:
            import pytesseract
            
            return await asyncio.to_thread(
                self._extract_text_sync,
                image_path,
                pytesseract
            )
            
        except ImportError:
            return {
                "error": "OCR not available",
                "message": "Install pytesseract for text extraction"
            }
    
    def _extract_text_sync(self, image_path: str, pytesseract) -> Dict[str, Any]:
        """Synchronous text extraction."""
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return {"error": "Failed to load image"}
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Extract text
            text = pytesseract.image_to_string(thresh)
            
            return {
                "text": text.strip(),
                "length": len(text.strip())
            }
            
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            return {"error": str(e)}
    
    async def compare_images(
        self,
        image1_path: str,
        image2_path: str
    ) -> Dict[str, Any]:
        """
        Compare two images for similarity.
        
        Args:
            image1_path: Path to first image
            image2_path: Path to second image
            
        Returns:
            Similarity metrics
        """
        return await asyncio.to_thread(
            self._compare_images_sync,
            image1_path,
            image2_path
        )
    
    def _compare_images_sync(
        self,
        image1_path: str,
        image2_path: str
    ) -> Dict[str, Any]:
        """Synchronous image comparison."""
        try:
            # Read images
            img1 = cv2.imread(image1_path)
            img2 = cv2.imread(image2_path)
            
            if img1 is None or img2 is None:
                return {"error": "Failed to load one or both images"}
            
            # Resize to same dimensions
            height = min(img1.shape[0], img2.shape[0])
            width = min(img1.shape[1], img2.shape[1])
            
            img1_resized = cv2.resize(img1, (width, height))
            img2_resized = cv2.resize(img2, (width, height))
            
            # Calculate structural similarity
            gray1 = cv2.cvtColor(img1_resized, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(img2_resized, cv2.COLOR_BGR2GRAY)
            
            # Calculate mean squared error
            mse = np.mean((gray1 - gray2) ** 2)
            
            # Calculate histogram similarity
            hist1 = cv2.calcHist([img1_resized], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            hist2 = cv2.calcHist([img2_resized], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            
            hist1 = cv2.normalize(hist1, hist1).flatten()
            hist2 = cv2.normalize(hist2, hist2).flatten()
            
            correlation = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
            
            return {
                "mse": float(mse),
                "histogram_correlation": float(correlation),
                "similarity_score": float(1 / (1 + mse)) * correlation
            }
            
        except Exception as e:
            logger.error(f"Image comparison failed: {e}")
            return {"error": str(e)}
