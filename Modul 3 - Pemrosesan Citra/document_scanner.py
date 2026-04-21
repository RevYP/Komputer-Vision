"""
Smart Document Scanner Module
Handles document detection, perspective correction, and enhancement
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional
import imutils


class DocumentScanner:
    """Deteksi dan enhancement dokumen dari foto"""
    
    def __init__(self):
        self.original_image = None
        self.processed_image = None
        self.document_contour = None
        
    def load_image(self, image_path: str) -> np.ndarray:
        """Load image dari file"""
        self.original_image = cv2.imread(image_path)
        if self.original_image is None:
            raise ValueError(f"Tidak bisa load image: {image_path}")
        return self.original_image
    
    def load_from_array(self, image_array: np.ndarray) -> np.ndarray:
        """Load image dari numpy array (dari kamera)"""
        self.original_image = image_array.copy()
        return self.original_image
    
    def detect_document(self, image: Optional[np.ndarray] = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Deteksi tepi dokumen menggunakan edge detection dan contour finding
        
        Args:
            image: Input image. Jika None, gunakan self.original_image
            
        Returns:
            Tuple dari (image_with_contour, document_outline)
        """
        if image is None:
            image = self.original_image
            
        if image is None:
            raise ValueError("Image tidak dimuat!")
        
        # Resize untuk processing yang lebih cepat
        ratio = image.shape[0] / 500.0
        orig = image.copy()
        image = imutils.resize(image, height=500)
        
        # Convert ke grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Blurring untuk mengurangi noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection dengan Canny
        edged = cv2.Canny(blurred, 75, 200)
        
        # Dilation & Erosion untuk memperbaiki edges
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        edged = cv2.dilate(edged, kernel, iterations=2)
        edged = cv2.erode(edged, kernel, iterations=1)
        
        # Cari contours
        cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)
        cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]
        
        screenCnt = None
        for c in cnts:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            
            # Cari contour dengan 4 sisi (dokumen)
            if len(approx) == 4:
                screenCnt = approx
                break
        
        if screenCnt is None:
            # Fallback: gunakan contour terbesar
            screenCnt = cnts[0]
        
        self.document_contour = screenCnt * ratio
        
        # Draw contour di original image
        image_copy = orig.copy()
        cv2.drawContours(image_copy, [self.document_contour.astype(int)], 0, (0, 255, 0), 2)
        
        return image_copy, edged
    
    def perspective_correction(self, image: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Lakukan perspective correction menggunakan document contour yang terdeteksi
        
        Args:
            image: Input image. Jika None, gunakan self.original_image
            
        Returns:
            Warped image setelah perspective correction
        """
        if image is None:
            image = self.original_image
            
        if image is None or self.document_contour is None:
            raise ValueError("Image atau document contour tidak tersedia!")
        
        pts = self.document_contour.reshape(4, 2)
        rect = self._order_points(pts)
        
        (tl, tr, br, bl) = rect
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))
        
        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))
        
        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]
        ], dtype="float32")
        
        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
        
        return warped
    
    def enhance_document(self, image: np.ndarray, 
                        brightness: float = 0, 
                        contrast: float = 1.0,
                        sharpness: float = 1.0) -> np.ndarray:
        """
        Enhance document untuk kualitas terbaik
        
        Args:
            image: Input image
            brightness: Brightness adjustment (-100 to 100)
            contrast: Contrast adjustment (0.5 to 3.0)
            sharpness: Sharpness adjustment (0.5 to 2.0)
            
        Returns:
            Enhanced image
        """
        # Brightness adjustment
        if brightness != 0:
            image = cv2.convertScaleAbs(image, alpha=1.0, beta=brightness)
        
        # Contrast adjustment
        image = cv2.convertScaleAbs(image, alpha=contrast, beta=0)
        
        # Convert ke grayscale untuk hasil yang lebih baik
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Adaptive thresholding untuk dokumen text yang jelas
        processed = cv2.adaptiveThreshold(gray, 255, 
                                         cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY, 11, 2)
        
        # Sharpness enhancement
        if sharpness > 1.0:
            kernel = np.array([[-1, -1, -1],
                              [-1,  9, -1],
                              [-1, -1, -1]]) / 9.0
            processed = cv2.filter2D(processed, -1, kernel)
        
        return processed
    
    def process_full_pipeline(self, image: Optional[np.ndarray] = None,
                             brightness: float = 0,
                             contrast: float = 1.0,
                             sharpness: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
        """
        Jalankan full pipeline: detect → perspective correction → enhance
        
        Returns:
            Tuple dari (processed_image, detection_preview)
        """
        # Detect document
        preview, _ = self.detect_document(image)
        
        # Perspective correction
        corrected = self.perspective_correction(image)
        
        # Enhancement
        enhanced = self.enhance_document(corrected, brightness, contrast, sharpness)
        
        self.processed_image = enhanced
        return enhanced, preview
    
    @staticmethod
    def _order_points(pts: np.ndarray) -> np.ndarray:
        """Urutkan 4 points ke format: TL, TR, BR, BL"""
        rect = np.zeros((4, 2), dtype="float32")
        
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        
        return rect
    
    def export_image(self, output_path: str, image: Optional[np.ndarray] = None) -> bool:
        """Export image ke file"""
        if image is None:
            image = self.processed_image
            
        if image is None:
            return False
        
        success = cv2.imwrite(output_path, image)
        return success
    
    def export_pdf(self, output_path: str, image: Optional[np.ndarray] = None) -> bool:
        """Export image to PDF"""
        try:
            from PIL import Image
            
            if image is None:
                image = self.processed_image
                
            if image is None:
                return False
            
            # Convert BGR to RGB
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            pil_image = Image.fromarray(image)
            pil_image.save(output_path, 'PDF')
            return True
        except:
            return False
