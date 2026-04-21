# 📸 Smart Document Scanner
## Aplikasi Praktis Scanning Papan Tulis & Catatan untuk Sekolah

**Gunakan aplikasi ini untuk:**
- ✅ Scan papan tulis/catatan tangan → hasil jelas & lurus otomatis
- ✅ Scan dokumen, lembar soal, sertifikat
- ✅ Enhancement otomatis (kecerahan, kontras, ketajaman)
- ✅ Simpan hasil sebagai PNG, JPG, atau PDF
- ✅ Cocok untuk tugas sekolah, presensi, arsip dokumen

---

## 🚀 Instalasi Cepat

### 1. Setup di Terminal
```bash
# Buka terminal di folder ini
cd SmartDocumentScanner

# (Opsional) Buat virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Jalankan Aplikasi
```bash
python scanner_gui.py
```

---

## 📖 Cara Penggunaan

### Opsi 1: Load Image dari File
1. Klik tombol **"📁 Load Image"**
2. Pilih foto papan tulis/catatan (JPG, PNG, BMP)
3. Preview akan menampilkan deteksi tepi dokumen (garis hijau)

### Opsi 2: Capture dari Kamera
1. Klik tombol **"📷 Buka Kamera"**
2. Tekan **SPACE** untuk capture
3. Tekan **ESC** untuk batal

### Pengaturan & Processing
1. **Kecerahan** - Slider untuk menambah/mengurangi kecerahan (-100 hingga +100)
2. **Kontras** - Slider untuk meningkatkan kontras (0.5 hingga 3.0)
3. **Ketajaman** - Slider untuk meningkatkan ketajaman teks (0.5 hingga 2.0)
4. Klik **"⚙️ PROSES"** untuk memproses dengan setting terpilih

### Lihat Hasil
- Tab **"📸 Original + Detection"** - Menampilkan image original dengan deteksi tepi
- Tab **"✨ Hasil Scanning"** - Menampilkan hasil akhir setelah enhancement

### Simpan Hasil
- Klik **"💾 PNG"** - Simpan sebagai PNG (resolusi tinggi)
- Klik **"💾 JPG"** - Simpan sebagai JPG (ukuran lebih kecil)
- Klik **"📄 PDF"** - Simpan sebagai PDF (untuk print)

Hasil tersimpan di folder `hasil_scan/`

---

## 🔧 Fitur Teknis

### Core Processing Pipeline
1. **Edge Detection** - Deteksi tepi dokumen menggunakan Canny Edge Detection
2. **Contour Finding** - Cari bentuk 4 sisi (dokumen persegi)
3. **Perspective Correction** - Ubah sudut pandang dokumen menjadi lurus (Warp Perspective)
4. **Enhancement** - Adaptive Thresholding untuk hasil teks yang jelas
5. **Sharpness** - Convolution kernel untuk meningkatkan ketajaman

### Algoritma Utama

#### 1. Document Detection
```python
# Edge detection
edged = cv2.Canny(blurred, 75, 200)

# Dilation & Erosion untuk memperbaiki tepi
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
edged = cv2.dilate(edged, kernel, iterations=2)

# Cari contour terbesar dengan 4 sisi
cnts = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
```

#### 2. Perspective Correction
```python
# Hitung width & height yang benar
# Lakukan warp perspective untuk straighten dokumen
M = cv2.getPerspectiveTransform(rect, dst)
warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
```

#### 3. Enhancement
```python
# Adaptive Thresholding untuk teks yang lebih jelas
processed = cv2.adaptiveThreshold(gray, 255, 
                                 cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 11, 2)
```

---

## 📋 Use Cases Praktis

### 1. Scanning Papan Tulis
- Foto papan tulis yang ditulis guru
- App otomatis straighten & enhance
- Hasil bisa dibagikan ke teman atau disimpan

### 2. Scan Catatan Tangan
- Foto catatan di kertas/buku
- Enhancement membuat teks lebih jelas & gelap
- Simpan sebagai PDF untuk print atau arsip

### 3. Scan Dokumen Sekolah
- Lembar soal, sertifikat, kartu identitas
- Hasil terurus & terang
- Ideal untuk submit ke guru atau penyimpanan digital

### 4. Absensi Manual
- Foto lembar absensi
- Enhancement membuat mudah dibaca
- Arsip digital permanent

---

## 💡 Tips Penggunaan

### Hasil Terbaik:
1. **Pencahayaan** - Gunakan di tempat yang terang atau pakai lampu
2. **Posisi Kamera** - Tegak lurus dengan dokumen (tidak miring)
3. **Fokus** - Pastikan gambar fokus sebelum capture
4. **Kontras** - Papan tulis atau catatan yang kontras akan hasilnya lebih baik

### Troubleshooting:
- **Garis deteksi tidak ketemu?** → Coba atur brightness/contrast slider
- **Hasil masih buram?** → Tingkatkan sharpness slider
- **Hasil terlalu terang/gelap?** → Adjust kecerahan slider
- **Kamera tidak terdeteksi?** → Pastikan kamera terhubung dan aplikasi lain tidak pakai kamera

---

## 📚 Learning Path

Aplikasi ini menggunakan konsep Computer Vision dari Modul 03:

1. **Edge Detection** → Canny Edge Detection
2. **Contour Analysis** → Finding contours & filtering
3. **Image Transformation** → Perspective Warp
4. **Image Enhancement** → Brightness, Contrast, Thresholding
5. **Morphological Operations** → Dilation & Erosion

---

## 🎯 Next Steps

Untuk mengembangkan lebih lanjut:
- ✏️ Tambah OCR (extract teks dari gambar)
- 📊 Tambah batch processing (scan banyak halaman)
- 🎨 Tambah filter warna-warni
- ☁️ Integration dengan cloud storage
- 📱 Port ke aplikasi mobile

---

## 📝 License & Credits

Dibuat untuk keperluan pembelajaran Computer Vision Modul 03.

---

**Selamat menggunakan! Semoga bermanfaat untuk sekolah lu! 📚✨**
