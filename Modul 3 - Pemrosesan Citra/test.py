"""
Test Script untuk Smart Document Scanner
Memastikan semua dependencies installed dan working
"""

import sys
import cv2
import numpy as np
from pathlib import Path


def test_imports():
    """Test semua required imports"""
    print("Testing imports...")
    try:
        import cv2
        print(f"✓ OpenCV {cv2.__version__}")
    except ImportError:
        print("✗ OpenCV not installed")
        return False
    
    try:
        import numpy
        print(f"✓ NumPy {numpy.__version__}")
    except ImportError:
        print("✗ NumPy not installed")
        return False
    
    try:
        from PIL import Image
        print(f"✓ Pillow installed")
    except ImportError:
        print("✗ Pillow not installed")
        return False
    
    try:
        import imutils
        print(f"✓ imutils installed")
    except ImportError:
        print("✗ imutils not installed")
        return False
    
    try:
        from document_scanner import DocumentScanner
        print(f"✓ DocumentScanner module OK")
    except ImportError as e:
        print(f"✗ DocumentScanner import failed: {e}")
        return False
    
    return True


def test_document_scanner():
    """Test DocumentScanner functionality"""
    print("\nTesting DocumentScanner...")
    
    try:
        from document_scanner import DocumentScanner
        
        # Create sample image
        print("Creating test image...")
        img = np.ones((600, 800, 3), dtype=np.uint8) * 200
        
        # Add text
        cv2.putText(img, "TEST DOCUMENT", (50, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
        cv2.rectangle(img, (30, 30), (770, 570), (0, 0, 0), 3)
        
        # Save
        cv2.imwrite("test_image.jpg", img)
        print("✓ Test image created: test_image.jpg")
        
        # Test scanner
        scanner = DocumentScanner()
        print("✓ DocumentScanner initialized")
        
        # Load image
        scanner.load_image("test_image.jpg")
        print("✓ Image loaded")
        
        # Detect
        preview, edges = scanner.detect_document()
        print("✓ Document detected")
        
        # Correct perspective
        corrected = scanner.perspective_correction()
        print("✓ Perspective corrected")
        
        # Enhance
        enhanced = scanner.enhance_document(corrected)
        print("✓ Image enhanced")
        
        # Export
        scanner.export_image("test_output.png", enhanced)
        print("✓ Image exported")
        
        # Cleanup
        Path("test_image.jpg").unlink()
        Path("test_output.png").unlink()
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gui_imports():
    """Test GUI imports"""
    print("\nTesting GUI imports...")
    
    try:
        import tkinter as tk
        print("✓ tkinter available")
    except ImportError:
        print("✗ tkinter not available")
        return False
    
    try:
        from PIL import ImageTk
        print("✓ PIL.ImageTk available")
    except ImportError:
        print("✗ PIL.ImageTk not available")
        return False
    
    return True


def create_sample_images():
    """Create sample images for testing"""
    print("\nCreating sample images...")
    
    # Create samples directory
    Path("sample_images").mkdir(exist_ok=True)
    
    # Sample 1: Text document simulation
    img1 = np.ones((800, 600, 3), dtype=np.uint8) * 255
    cv2.putText(img1, "CATATAN SEKOLAH", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 2)
    cv2.putText(img1, "Modul 03 - Image Processing", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1)
    cv2.putText(img1, "Edge Detection & Enhancement", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 1)
    cv2.rectangle(img1, (30, 30), (570, 770), (0, 0, 0), 2)
    cv2.imwrite("sample_images/sample_notes.jpg", img1)
    print("✓ Sample 1: sample_notes.jpg")
    
    # Sample 2: Rotated document (perspective)
    img2 = np.ones((500, 700, 3), dtype=np.uint8) * 240
    cv2.putText(img2, "DOKUMEN MIRING", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 0), 2)
    cv2.rectangle(img2, (25, 25), (675, 475), (0, 0, 0), 2)
    M = cv2.getRotationMatrix2D((350, 250), 20, 1)
    img2_rotated = cv2.warpAffine(img2, M, (700, 500))
    cv2.imwrite("sample_images/sample_rotated.jpg", img2_rotated)
    print("✓ Sample 2: sample_rotated.jpg")
    
    # Sample 3: Low contrast
    img3 = np.ones((600, 600, 3), dtype=np.uint8) * 150
    cv2.putText(img3, "LOW CONTRAST", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (120, 120, 120), 2)
    cv2.rectangle(img3, (30, 30), (570, 570), (140, 140, 140), 2)
    cv2.imwrite("sample_images/sample_lowcontrast.jpg", img3)
    print("✓ Sample 3: sample_lowcontrast.jpg")


def main():
    print("=" * 60)
    print("SMART DOCUMENT SCANNER - TEST SUITE")
    print("=" * 60)
    
    all_passed = True
    
    # Test 1: Imports
    if not test_imports():
        print("\n⚠️  Missing dependencies!")
        print("Run: pip install -r requirements.txt")
        all_passed = False
    
    # Test 2: GUI imports
    if not test_gui_imports():
        print("\n⚠️  GUI dependencies missing!")
        all_passed = False
    
    # Test 3: DocumentScanner
    if not test_document_scanner():
        all_passed = False
    
    # Test 4: Create samples
    try:
        create_sample_images()
    except Exception as e:
        print(f"✗ Failed to create samples: {e}")
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✓ ALL TESTS PASSED!")
        print("\nReady to use:")
        print("  Windows: double-click run.bat")
        print("  Linux/Mac: ./run.sh")
        return 0
    else:
        print("✗ SOME TESTS FAILED")
        print("\nFix errors and try again.")
        return 1
    
    print("=" * 60)


if __name__ == "__main__":
    sys.exit(main())
