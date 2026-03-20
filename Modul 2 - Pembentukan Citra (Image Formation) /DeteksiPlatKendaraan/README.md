# Prototype Parkir Mal - Deteksi Plat dari CCTV (Simulasi Gambar)

Dokumentasi ini fokus pada aplikasi GUI berbasis gambar di file `deteksiPlatKendaraanGambarGUI.py`.
Program ini adalah prototype sistem parkir untuk simulasi pembacaan plat kendaraan dari frame CCTV dengan berbagai sudut kamera.

## Tujuan Program

1. Membaca frame CCTV simulasi dari file gambar.
2. Mendeteksi kandidat area plat.
3. Melakukan koreksi perspektif agar plat lebih tegak.
4. Meningkatkan kualitas crop plat menggunakan gamma correction.
5. Membaca teks plat dengan OCR.
6. Menyimpan hasil crop plat otomatis dengan timestamp.
7. Menampilkan log status kendaraan masuk, parkir, dan keluar.

## Struktur Folder dan Fungsi File

- `deteksiPlatKendaraanGambarGUI.py`
	- File aplikasi utama.
	- Berisi GUI (Tkinter), pipeline deteksi, OCR, logging, dan estimasi waktu parkir.

- `output_crop_plat/`
	- Folder output hasil crop plat.
	- Nama file otomatis berbentuk `plate_<PLAT>_<TIMESTAMP>.jpg`.

- `README.md`
	- Penjelasan setup, arsitektur, alur program, dan fitur aplikasi.

## Teknologi yang Dipakai

- Python
	- Bahasa utama aplikasi.

- Tkinter
	- Membangun GUI desktop (tombol, panel preview, tabel log).

- OpenCV (`cv2`)
	- Baca gambar, preprocessing, deteksi kontur, transformasi perspektif, anotasi, dan simpan output.

- EasyOCR
	- Membaca teks plat dari hasil crop/warped plate.

- NumPy
	- Operasi numerik untuk manipulasi titik dan proses image transform.

- Pillow (`PIL`)
	- Konversi frame OpenCV ke format preview GUI (`ImageTk`).

## Garis Besar Alur Program

1. User memilih gambar CCTV melalui tombol **Load Frame CCTV**.
2. Program menjalankan deteksi kandidat plat melalui tiga jalur:
	 - Kontur geometri.
	 - OCR candidate dari full frame (multiscale).
	 - OCR fallback ROI area bawah kendaraan.
3. Tiap kandidat diperspektifkan (warp) agar tegak.
4. Hasil warp ditingkatkan dengan gamma correction dan variasi preprocessing lain.
5. OCR dijalankan pada beberapa varian untuk memilih hasil teks terbaik.
6. Kandidat terbaik dianotasi pada frame asli.
7. Crop plat disimpan ke `output_crop_plat/` dengan timestamp.
8. Log parkir diperbarui pada tabel (masuk/parkir/keluar + durasi).

## Fitur Aplikasi

- **Load Frame CCTV**
	- Memuat gambar simulasi CCTV dari file.

- **Proses Deteksi**
	- Mendeteksi area plat dan membaca teksnya.
	- Menampilkan hasil anotasi dan crop plat terkoreksi.

- **Proses Kendaraan Keluar**
	- Menutup sesi parkir kendaraan aktif.
	- Mengisi waktu keluar dan durasi akhir.

- **Simpan Frame Hasil**
	- Menyimpan frame anotasi ke file yang dipilih user.

- **Reset**
	- Menghapus tampilan sementara dan mengembalikan state GUI.

## Format Log Kendaraan

Kolom log yang ditampilkan:

1. No
2. Waktu Masuk
3. Waktu Keluar
4. Nomor Plat
5. Durasi Parkir
6. Status (`MASUK`, `PARKIR`, `KELUAR`)
7. Sumber Frame
8. File Crop

## Instalasi Dependensi

```bash
pip install opencv-python easyocr pillow numpy
```

## Menjalankan Program

```bash
python deteksiPlatKendaraanGambarGUI.py
```

## Catatan Penggunaan

- Program ini adalah prototype berbasis gambar (bukan stream video real-time).
- Akurasi OCR dipengaruhi resolusi gambar, sudut kamera, dan pencahayaan.
- Untuk hasil lebih baik, gunakan frame yang tajam dan area plat tidak blur.

