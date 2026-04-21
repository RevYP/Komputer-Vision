"""
Smart Document Scanner GUI
Aplikasi praktis untuk scanning papan tulis/catatan sekolah
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
import os
from datetime import datetime
from document_scanner import DocumentScanner
import threading


class DocumentScannerGUI:
    """GUI untuk Smart Document Scanner"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("📸 Smart Document Scanner - Praktis untuk Sekolah!")
        self.root.geometry("1200x700")
        self.root.resizable(False, False)
        
        # Scanner instance
        self.scanner = DocumentScanner()
        self.current_image = None
        self.processed_image = None
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        """Setup interface"""
        # Header
        header = tk.Frame(self.root, bg="#2c3e50", height=50)
        header.pack(fill=tk.X)
        
        title_label = tk.Label(header, text="📸 Smart Document Scanner", 
                              font=("Arial", 16, "bold"), 
                              bg="#2c3e50", fg="white")
        title_label.pack(pady=10)
        
        # Main container
        main_container = tk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Controls
        left_panel = tk.Frame(main_container, width=250, bg="white")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=5)
        left_panel.pack_propagate(False)
        
        self.setup_control_panel(left_panel)
        
        # Right panel - Preview & Results
        right_panel = tk.Frame(main_container)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        self.setup_preview_panel(right_panel)
        
    def setup_control_panel(self, parent):
        """Setup control panel"""
        # Title
        title = tk.Label(parent, text="KONTROL", font=("Arial", 12, "bold"), bg="white")
        title.pack(pady=10)
        
        # Load buttons
        btn_load = tk.Button(parent, text="📁 Load Image", 
                            command=self.load_image,
                            bg="#3498db", fg="white", 
                            font=("Arial", 10), width=20)
        btn_load.pack(pady=5)
        
        btn_camera = tk.Button(parent, text="📷 Buka Kamera", 
                              command=self.open_camera,
                              bg="#9b59b6", fg="white",
                              font=("Arial", 10), width=20)
        btn_camera.pack(pady=5)
        
        # Separator
        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Enhancement controls
        controls_label = tk.Label(parent, text="PENYESUAIAN", font=("Arial", 11, "bold"), bg="white")
        controls_label.pack(pady=10)
        
        # Brightness
        tk.Label(parent, text="Kecerahan:", font=("Arial", 9), bg="white").pack(anchor=tk.W, padx=10)
        self.brightness_slider = tk.Scale(parent, from_=-100, to=100, orient=tk.HORIZONTAL,
                                         bg="white", length=200)
        self.brightness_slider.set(0)
        self.brightness_slider.pack(padx=10, pady=5)
        
        # Contrast
        tk.Label(parent, text="Kontras:", font=("Arial", 9), bg="white").pack(anchor=tk.W, padx=10)
        self.contrast_slider = tk.Scale(parent, from_=0.5, to=3.0, orient=tk.HORIZONTAL,
                                       bg="white", length=200, resolution=0.1)
        self.contrast_slider.set(1.0)
        self.contrast_slider.pack(padx=10, pady=5)
        
        # Sharpness
        tk.Label(parent, text="Ketajaman:", font=("Arial", 9), bg="white").pack(anchor=tk.W, padx=10)
        self.sharpness_slider = tk.Scale(parent, from_=0.5, to=2.0, orient=tk.HORIZONTAL,
                                        bg="white", length=200, resolution=0.1)
        self.sharpness_slider.set(1.0)
        self.sharpness_slider.pack(padx=10, pady=5)
        
        # Separator
        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Process button
        btn_process = tk.Button(parent, text="⚙️ PROSES", 
                               command=self.process_image,
                               bg="#e74c3c", fg="white",
                               font=("Arial", 11, "bold"), width=20)
        btn_process.pack(pady=10)
        
        # Separator
        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # Export section
        export_label = tk.Label(parent, text="SIMPAN HASIL", font=("Arial", 11, "bold"), bg="white")
        export_label.pack(pady=10)
        
        btn_export_png = tk.Button(parent, text="💾 PNG", 
                                  command=lambda: self.export_image("PNG"),
                                  bg="#27ae60", fg="white",
                                  font=("Arial", 9), width=20)
        btn_export_png.pack(pady=3)
        
        btn_export_jpg = tk.Button(parent, text="💾 JPG", 
                                  command=lambda: self.export_image("JPG"),
                                  bg="#27ae60", fg="white",
                                  font=("Arial", 9), width=20)
        btn_export_jpg.pack(pady=3)
        
        btn_export_pdf = tk.Button(parent, text="📄 PDF", 
                                  command=lambda: self.export_image("PDF"),
                                  bg="#2980b9", fg="white",
                                  font=("Arial", 9), width=20)
        btn_export_pdf.pack(pady=3)
        
        # Status
        ttk.Separator(parent, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        tk.Label(parent, text="STATUS", font=("Arial", 10, "bold"), bg="white").pack(pady=5)
        self.status_label = tk.Label(parent, text="Siap", font=("Arial", 9), 
                                    bg="#f0f0f0", fg="#2c3e50", width=25)
        self.status_label.pack(pady=5, padx=5)
        
    def setup_preview_panel(self, parent):
        """Setup preview dan hasil"""
        # Tab untuk original vs processed
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1 - Original dengan detection
        tab1 = tk.Frame(notebook)
        notebook.add(tab1, text="📸 Original + Detection")
        
        self.preview_canvas = tk.Canvas(tab1, bg="black")
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Tab 2 - Hasil Processing
        tab2 = tk.Frame(notebook)
        notebook.add(tab2, text="✨ Hasil Scanning")
        
        self.result_canvas = tk.Canvas(tab2, bg="black")
        self.result_canvas.pack(fill=tk.BOTH, expand=True)
        
    def load_image(self):
        """Load image dari file"""
        file_path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp"),
                      ("Semua files", "*.*")]
        )
        
        if file_path:
            self.scanner.load_image(file_path)
            self.current_image = self.scanner.original_image.copy()
            self.update_status("Image dimuat!")
            self.display_preview()
            
    def open_camera(self):
        """Buka kamera untuk capture"""
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "Kamera tidak tersedia!")
            return
        
        # Create window untuk capture
        window_name = "Tekan SPACE untuk capture, ESC untuk batal"
        captured = False
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            frame = imutils.resize(frame, width=800)
            cv2.imshow(window_name, frame)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 32:  # SPACE
                self.scanner.load_from_array(frame)
                self.current_image = frame.copy()
                captured = True
                self.update_status("Foto diambil!")
                break
            elif key == 27:  # ESC
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        if captured:
            self.display_preview()
    
    def display_preview(self):
        """Tampilkan preview dengan detection"""
        if self.current_image is None:
            return
        
        try:
            # Detect document
            preview, _ = self.scanner.detect_document(self.current_image)
            
            # Resize untuk display
            preview = imutils.resize(preview, width=500)
            
            # Convert BGR to RGB untuk tkinter
            preview_rgb = cv2.cvtColor(preview, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(preview_rgb)
            photo = ImageTk.PhotoImage(pil_image)
            
            # Display di canvas
            self.preview_canvas.create_image(0, 0, image=photo, anchor=tk.NW)
            self.preview_canvas.image = photo
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saat display: {str(e)}")
    
    def process_image(self):
        """Process image"""
        if self.current_image is None:
            messagebox.showwarning("Warning", "Load image terlebih dahulu!")
            return
        
        try:
            self.update_status("Sedang memproses...")
            self.root.update()
            
            # Get slider values
            brightness = self.brightness_slider.get()
            contrast = float(self.contrast_slider.get())
            sharpness = float(self.sharpness_slider.get())
            
            # Process full pipeline
            processed, preview = self.scanner.process_full_pipeline(
                self.current_image, brightness, contrast, sharpness
            )
            
            self.processed_image = processed
            
            # Display hasil
            self.display_result(processed)
            self.update_status("Selesai! Siap untuk simpan.")
            
        except Exception as e:
            self.update_status("Error!")
            messagebox.showerror("Error", f"Error saat processing: {str(e)}")
    
    def display_result(self, image):
        """Tampilkan hasil processing"""
        try:
            result = imutils.resize(image, width=500)
            
            # Convert ke RGB jika perlu
            if len(result.shape) == 2:
                result_rgb = cv2.cvtColor(result, cv2.COLOR_GRAY2RGB)
            else:
                result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
            
            pil_image = Image.fromarray(result_rgb)
            photo = ImageTk.PhotoImage(pil_image)
            
            self.result_canvas.create_image(0, 0, image=photo, anchor=tk.NW)
            self.result_canvas.image = photo
            
        except Exception as e:
            messagebox.showerror("Error", f"Error saat display result: {str(e)}")
    
    def export_image(self, format_type):
        """Export image"""
        if self.processed_image is None:
            messagebox.showwarning("Warning", "Proses image terlebih dahulu!")
            return
        
        # Create output directory
        output_dir = "hasil_scan"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            if format_type == "PNG":
                filename = f"{output_dir}/scan_{timestamp}.png"
                success = self.scanner.export_image(filename)
            elif format_type == "JPG":
                filename = f"{output_dir}/scan_{timestamp}.jpg"
                success = self.scanner.export_image(filename)
            elif format_type == "PDF":
                filename = f"{output_dir}/scan_{timestamp}.pdf"
                success = self.scanner.export_pdf(filename)
            
            if success:
                messagebox.showinfo("Sukses", f"File disimpan:\n{filename}")
                self.update_status(f"Disimpan: {filename}")
            else:
                messagebox.showerror("Error", "Gagal menyimpan file!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error saat export: {str(e)}")
    
    def update_status(self, text):
        """Update status label"""
        self.status_label.config(text=text[:23])


def main():
    root = tk.Tk()
    app = DocumentScannerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    # Import untuk kamera
    try:
        import imutils
    except ImportError:
        print("Menginstall imutils...")
        import subprocess
        subprocess.check_call(["pip", "install", "imutils"])
        import imutils
    
    main()
