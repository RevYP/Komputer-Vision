# 🚀 Quick Start Tutorial
## Smart Document Scanner dalam 5 Menit

### Langkah 1: Setup (2 menit)

#### Windows:
1. Buka folder ini di File Explorer
2. Double-click `run.bat`
3. Tunggu sampai aplikasi terbuka (download dependencies first time)

#### Linux/Mac:
1. Buka terminal di folder ini
2. `chmod +x run.sh` (beri permission)
3. `./run.sh`

### Langkah 2: Jalankan Aplikasi (30 detik)

Saat aplikasi terbuka, Anda akan melihat GUI dengan:
- **KONTROL** panel (kiri) - tombol & pengaturan
- **Preview panel** (kanan) - tampilan hasil

### Langkah 3: Load/Capture Image (1 menit)

Pilih salah satu:

**Opsi A - Load dari File:**
```
1. Klik "📁 Load Image"
2. Pilih foto papan tulis/catatan Anda
3. Preview akan muncul dengan garis hijau mendeteksi tepi dokumen
```

**Opsi B - Capture dari Kamera:**
```
1. Klik "📷 Buka Kamera"
2. Tekan SPACE untuk capture
3. Tekan ESC untuk batal
```

### Langkah 4: Adjustment & Processing (1 menit)

```
1. Drag slider untuk menyesuaikan:
   - Kecerahan: untuk image gelap/terang
   - Kontras: untuk membuat lebih jelas
   - Ketajaman: untuk teks lebih tajam

2. Klik "⚙️ PROSES" untuk memproses

3. Lihat hasil di tab "✨ Hasil Scanning"
```

### Langkah 5: Save Hasil (30 detik)

```
1. Pilih format:
   - 💾 PNG (resolution tinggi, ukuran besar)
   - 💾 JPG (balance, ukuran sedang)
   - 📄 PDF (untuk print)

2. File otomatis tersimpan di folder "hasil_scan/"

3. Selesai! Hasil siap digunakan/dibagikan
```

---

## 💡 Pro Tips

### Untuk Hasil Terbaik:

1. **Pencahayaan** 
   - Gunakan di ruangan terang atau pakai lampu
   - Hindari bayangan atau glare

2. **Positioning**
   - Tahan kamera tegak lurus (90°) dengan dokumen
   - Jangan miring/oblique

3. **Fokus**
   - Pastikan foto fokus sebelum capture
   - Teks harus terlihat jelas

### Troubleshooting

| Problem | Solusi |
|---------|--------|
| Garis deteksi tidak ada | ↑ Brightness, ↑ Contrast |
| Hasil terlalu terang | ↓ Brightness |
| Hasil terlalu gelap | ↑ Brightness |
| Teks masih buram | ↑ Sharpness |
| Kamera error | Tutup app lain yang pakai kamera |

---

## 🎯 Use Cases

### Scenario 1: Scan Papan Tulis
```
1. Load → foto papan tulis yang guru tulis
2. Adjust → increase contrast & sharpness
3. Process → correction & enhancement otomatis
4. Export → PNG untuk dibagikan ke grup
```

### Scenario 2: Scan Catatan Tangan
```
1. Capture → ambil foto catatan di buku/kertas
2. Adjust → brightness untuk hasil lebih jelas
3. Process → hasil akan straight & terang
4. Export → JPG untuk upload ke Google Drive
```

### Scenario 3: Scan Dokumen Sekolah
```
1. Load → lembar soal/sertifikat/kartu ID
2. Adjust → normal atau sesuai kebutuhan
3. Process → automatic perspective fix & enhancement
4. Export → PDF untuk print atau arsip digital
```

---

## ⚙️ Algoritma di Balik Layar

Saat Anda klik "⚙️ PROSES", aplikasi melakukan:

```
1. Edge Detection (Canny)
   → Deteksi semua tepi di gambar
   
2. Contour Finding
   → Cari bentuk 4 sisi (dokumen)
   
3. Perspective Correction (Warp)
   → Ubah sudut pandang → jadi straight
   
4. Enhancement
   → Adaptive Thresholding → teks lebih jelas
   → Sharpening kernel → tambah ketajaman
```

---

## 📚 Konsep Computer Vision

Aplikasi ini menggunakan:
- **Edge Detection** - Menemukan batas objek
- **Image Warping** - Transform geometry image
- **Adaptive Thresholding** - Konversi ke binary dengan threshold lokal
- **Morphological Ops** - Dilation & erosion
- **Histogram Processing** - Adjustment brightness/contrast

---

## 🆘 Butuh Bantuan?

### Error: "Kamera tidak tersedia"
```
→ Periksa kamera terhubung
→ Close aplikasi lain yang pakai kamera
→ Restart aplikasi
```

### Error: "Image load failed"
```
→ Pastikan format: JPG, PNG, BMP
→ File tidak corrupt
→ Coba ulang dengan file lain
```

### Aplikasi lambat?
```
→ Normal untuk first time (install dependencies)
→ Processing besar untuk large images
→ Resize image kalau terlalu besar (3000x4000+)
```

---

## 🎓 Untuk Pembelajaran

Lihat file-file ini untuk belajar:
- `document_scanner.py` - Core algoritma (~ 250 lines)
- `scanner_gui.py` - GUI implementation (~ 300 lines)
- `examples.py` - Contoh penggunaan

---

**Selamat! Siap mulai scanning? 📸 Let's go!**
