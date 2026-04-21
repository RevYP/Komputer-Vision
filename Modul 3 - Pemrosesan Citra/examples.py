"""
Quick Start & Example Usage
Smart Document Scanner
"""

from document_scanner import DocumentScanner
import cv2
import numpy as np


def example_1_basic_usage():
    """
    Contoh 1: Basic usage - Load image, detect, dan process
    """
    print("=== Example 1: Basic Usage ===")
    
    # Buat scanner instance
    scanner = DocumentScanner()
    
    # Load image
    try:
        scanner.load_image("sample_image.jpg")
        print("✓ Image loaded")
    except:
        print("✗ Image tidak ditemukan. Gunakan image Anda sendiri!")
        return
    
    # Detect document edges
    preview, edges = scanner.detect_document()
    print("✓ Document detected")
    
    # Perspective correction
    corrected = scanner.perspective_correction()
    print("✓ Perspective corrected")
    
    # Enhancement
    enhanced = scanner.enhance_document(corrected, brightness=20, contrast=1.5, sharpness=1.5)
    print("✓ Image enhanced")
    
    # Export
    scanner.export_image("output_example1.png", enhanced)
    print("✓ Saved: output_example1.png")


def example_2_custom_adjustments():
    """
    Contoh 2: Custom adjustments dengan berbagai parameter
    """
    print("\n=== Example 2: Custom Adjustments ===")
    
    scanner = DocumentScanner()
    
    try:
        scanner.load_image("sample_image.jpg")
    except:
        print("✗ Image tidak ditemukan!")
        return
    
    # Process dengan berbagai setting
    parameters = [
        {"brightness": 0, "contrast": 1.0, "sharpness": 1.0, "name": "normal"},
        {"brightness": 20, "contrast": 1.5, "sharpness": 1.5, "name": "bright_high_contrast"},
        {"brightness": -20, "contrast": 1.2, "sharpness": 1.2, "name": "dark_soft"},
    ]
    
    for param in parameters:
        name = param.pop("name")
        processed, _ = scanner.process_full_pipeline(brightness=param["brightness"], 
                                                     contrast=param["contrast"],
                                                     sharpness=param["sharpness"])
        scanner.export_image(f"output_{name}.png", processed)
        print(f"✓ Saved: output_{name}.png")


def example_3_batch_processing():
    """
    Contoh 3: Batch processing multiple images
    """
    print("\n=== Example 3: Batch Processing ===")
    
    import os
    import glob
    
    # Cari semua jpg files
    image_files = glob.glob("*.jpg") + glob.glob("*.png")
    
    if not image_files:
        print("✗ Tidak ada image files ditemukan!")
        return
    
    scanner = DocumentScanner()
    
    for idx, image_file in enumerate(image_files[:3], 1):  # Process 3 images
        try:
            print(f"\nProcessing {idx}: {image_file}")
            scanner.load_image(image_file)
            processed, _ = scanner.process_full_pipeline(brightness=10, contrast=1.3)
            
            output_name = f"batch_{idx}_{os.path.splitext(image_file)[0]}.png"
            scanner.export_image(output_name, processed)
            print(f"✓ Saved: {output_name}")
        except Exception as e:
            print(f"✗ Error: {e}")


def example_4_export_to_pdf():
    """
    Contoh 4: Export hasil ke PDF
    """
    print("\n=== Example 4: Export to PDF ===")
    
    scanner = DocumentScanner()
    
    try:
        scanner.load_image("sample_image.jpg")
    except:
        print("✗ Image tidak ditemukan!")
        return
    
    # Process
    processed, _ = scanner.process_full_pipeline(brightness=15, contrast=1.4)
    
    # Export ke PDF
    success = scanner.export_pdf("output_document.pdf", processed)
    if success:
        print("✓ PDF saved: output_document.pdf")
    else:
        print("✗ Gagal membuat PDF")


def example_5_create_sample_image():
    """
    Contoh 5: Buat sample image untuk testing
    """
    print("\n=== Example 5: Create Sample Image ===")
    
    # Buat image dengan teks simulasi papan tulis
    img = np.ones((600, 800, 3), dtype=np.uint8) * 255  # White background
    
    # Add text seperti papan tulis
    cv2.putText(img, "PAPAN TULIS SIMULASI", (50, 100), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 0), 3)
    cv2.putText(img, "Computer Vision - Modul 03", (50, 150),
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(img, "Edge Detection & Image Enhancement", (50, 200),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    
    cv2.rectangle(img, (30, 30), (770, 570), (0, 0, 0), 3)
    
    # Rotate sedikit untuk simulasi sudut pandang
    M = cv2.getRotationMatrix2D((400, 300), 15, 1)
    img_rotated = cv2.warpAffine(img, M, (800, 600))
    
    cv2.imwrite("sample_board.jpg", img_rotated)
    print("✓ Sample image created: sample_board.jpg")
    
    # Process langsung
    scanner = DocumentScanner()
    scanner.load_from_array(img_rotated)
    processed, _ = scanner.process_full_pipeline(brightness=10, contrast=1.5)
    scanner.export_image("sample_board_processed.png", processed)
    print("✓ Processed: sample_board_processed.png")


if __name__ == "__main__":
    print("\n" + "="*50)
    print("Smart Document Scanner - Usage Examples")
    print("="*50)
    
    # Uncomment contoh yang ingin dijalankan:
    
    # example_1_basic_usage()
    # example_2_custom_adjustments()
    # example_3_batch_processing()
    # example_4_export_to_pdf()
    example_5_create_sample_image()
    
    print("\n" + "="*50)
    print("Examples completed!")
    print("="*50 + "\n")
