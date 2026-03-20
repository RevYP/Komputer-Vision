import os
import re
from datetime import datetime

import cv2
import easyocr
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from PIL import Image, ImageTk


class ParkingCCTVPrototypeApp:
    def __init__(self, root):
        # Inisialisasi state utama aplikasi GUI.
        self.root = root
        self.root.title("Prototype Parkir Mal - Deteksi Plat dari CCTV (Simulasi Gambar)")
        self.root.geometry("1400x860")

        self.reader = None
        self.current_file_path = ""
        self.original_image = None
        self.annotated_image = None
        self.corrected_plate_image = None

        self.original_preview = None
        self.annotated_preview = None
        self.corrected_preview = None

        self.output_dir = os.path.join(os.path.dirname(__file__), "output_crop_plat")
        os.makedirs(self.output_dir, exist_ok=True)

        # entry_times menyimpan waktu masuk awal per plat.
        # active_sessions menyimpan row log aktif agar bisa di-update saat kendaraan keluar.
        self.entry_times = {}
        self.active_sessions = {}
        self.log_no = 0
        self.current_detected_plate = ""

        self._build_ui()

    def _build_ui(self):
        # Bagian kontrol utama aplikasi.
        top_frame = tk.Frame(self.root, padx=12, pady=10)
        top_frame.pack(fill="x")

        tk.Button(top_frame, text="Load Frame CCTV", command=self.load_image, width=16).pack(side="left", padx=4)
        tk.Button(top_frame, text="Proses Deteksi", command=self.detect_plate, width=16).pack(side="left", padx=4)
        tk.Button(top_frame, text="Proses Kendaraan Keluar", command=self.process_vehicle_exit, width=20).pack(side="left", padx=4)
        tk.Button(top_frame, text="Simpan Frame Hasil", command=self.save_annotated, width=16).pack(side="left", padx=4)
        tk.Button(top_frame, text="Reset", command=self.reset_view, width=10).pack(side="left", padx=4)

        self.status_var = tk.StringVar(value="Silakan load gambar CCTV simulasi.")
        tk.Label(top_frame, textvariable=self.status_var, anchor="w").pack(side="left", padx=12)

        center_frame = tk.Frame(self.root, padx=12, pady=8)
        center_frame.pack(fill="both", expand=True)

        # Tiga panel visual: frame asli, frame anotasi, dan crop plat hasil koreksi.
        left_panel = tk.LabelFrame(center_frame, text="Frame CCTV Asli", padx=8, pady=8)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 6))

        middle_panel = tk.LabelFrame(center_frame, text="Deteksi Area Plat", padx=8, pady=8)
        middle_panel.pack(side="left", fill="both", expand=True, padx=6)

        right_panel = tk.LabelFrame(center_frame, text="Plat Terkoreksi + Gamma", padx=8, pady=8)
        right_panel.pack(side="left", fill="both", expand=True, padx=(6, 0))

        self.original_label = tk.Label(left_panel, bg="#1c1f22")
        self.original_label.pack(fill="both", expand=True)

        self.annotated_label = tk.Label(middle_panel, bg="#1c1f22")
        self.annotated_label.pack(fill="both", expand=True)

        self.corrected_label = tk.Label(right_panel, bg="#1c1f22")
        self.corrected_label.pack(fill="both", expand=True)

        info_frame = tk.Frame(self.root, padx=12, pady=8)
        info_frame.pack(fill="x")

        self.plate_var = tk.StringVar(value="-")
        self.saved_crop_var = tk.StringVar(value="-")
        self.park_time_var = tk.StringVar(value="-")

        tk.Label(info_frame, text="Plat terdeteksi:", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(info_frame, textvariable=self.plate_var, fg="#0b6b3a", font=("Consolas", 12, "bold")).grid(
            row=0, column=1, sticky="w", padx=8
        )

        tk.Label(info_frame, text="File crop tersimpan:", font=("Segoe UI", 10, "bold")).grid(row=1, column=0, sticky="w")
        tk.Label(info_frame, textvariable=self.saved_crop_var, font=("Consolas", 10)).grid(row=1, column=1, sticky="w", padx=8)

        tk.Label(info_frame, text="Estimasi waktu parkir:", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w")
        tk.Label(info_frame, textvariable=self.park_time_var, font=("Consolas", 10, "bold"), fg="#1e4f91").grid(
            row=2, column=1, sticky="w", padx=8
        )

        log_frame = tk.LabelFrame(self.root, text="Log Kendaraan Masuk (Simulasi)", padx=8, pady=8)
        log_frame.pack(fill="both", expand=False, padx=12, pady=(0, 12))

        columns = ("no", "waktu_masuk", "waktu_keluar", "plat", "durasi", "status", "sumber", "crop_file")
        self.log_tree = ttk.Treeview(log_frame, columns=columns, show="headings", height=9)
        self.log_tree.heading("no", text="No")
        self.log_tree.heading("waktu_masuk", text="Waktu Masuk")
        self.log_tree.heading("waktu_keluar", text="Waktu Keluar")
        self.log_tree.heading("plat", text="Nomor Plat")
        self.log_tree.heading("durasi", text="Durasi Parkir")
        self.log_tree.heading("status", text="Status")
        self.log_tree.heading("sumber", text="Sumber Frame")
        self.log_tree.heading("crop_file", text="File Crop")

        self.log_tree.column("no", width=48, anchor="center")
        self.log_tree.column("waktu_masuk", width=155, anchor="center")
        self.log_tree.column("waktu_keluar", width=155, anchor="center")
        self.log_tree.column("plat", width=160, anchor="center")
        self.log_tree.column("durasi", width=120, anchor="center")
        self.log_tree.column("status", width=90, anchor="center")
        self.log_tree.column("sumber", width=240, anchor="w")
        self.log_tree.column("crop_file", width=250, anchor="w")
        self.log_tree.pack(fill="x")

    def _ensure_reader(self):
        # EasyOCR di-load sekali agar proses berikutnya lebih cepat.
        if self.reader is None:
            self.status_var.set("Memuat model OCR... tunggu sebentar.")
            self.root.update_idletasks()
            self.reader = easyocr.Reader(["en"], gpu=False)

    def _to_preview(self, bgr_img, max_size=(430, 360)):
        rgb_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(rgb_img)
        pil_img.thumbnail(max_size, Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(pil_img)

    def _render_images(self):
        if self.original_image is not None:
            self.original_preview = self._to_preview(self.original_image)
            self.original_label.configure(image=self.original_preview)

        if self.annotated_image is not None:
            self.annotated_preview = self._to_preview(self.annotated_image)
            self.annotated_label.configure(image=self.annotated_preview)

        if self.corrected_plate_image is not None:
            self.corrected_preview = self._to_preview(self.corrected_plate_image, max_size=(430, 220))
            self.corrected_label.configure(image=self.corrected_preview)

    def _order_points(self, pts):
        # Urutkan titik menjadi: kiri-atas, kanan-atas, kanan-bawah, kiri-bawah.
        rect = np.zeros((4, 2), dtype="float32")
        sums = pts.sum(axis=1)
        diffs = np.diff(pts, axis=1)
        rect[0] = pts[np.argmin(sums)]
        rect[2] = pts[np.argmax(sums)]
        rect[1] = pts[np.argmin(diffs)]
        rect[3] = pts[np.argmax(diffs)]
        return rect

    def _warp_plate(self, image, quad_points):
        # Perspektif transform agar area plat miring menjadi tampak frontal.
        rect = self._order_points(quad_points)
        (tl, tr, br, bl) = rect

        width_a = np.linalg.norm(br - bl)
        width_b = np.linalg.norm(tr - tl)
        max_width = int(max(width_a, width_b))

        height_a = np.linalg.norm(tr - br)
        height_b = np.linalg.norm(tl - bl)
        max_height = int(max(height_a, height_b))

        max_width = max(max_width, 64)
        max_height = max(max_height, 24)

        destination = np.array(
            [[0, 0], [max_width - 1, 0], [max_width - 1, max_height - 1], [0, max_height - 1]],
            dtype="float32",
        )

        matrix = cv2.getPerspectiveTransform(rect, destination)
        warped = cv2.warpPerspective(image, matrix, (max_width, max_height))
        return warped

    def _apply_gamma_correction(self, image, gamma=1.6):
        # Gamma correction untuk membantu visibilitas karakter di plat gelap.
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        return cv2.LUT(image, table)

    def _clean_plate_text(self, text):
        text = text.upper()
        cleaned = re.sub(r"[^A-Z0-9]", "", text)
        return cleaned

    def _is_plate_like(self, text):
        # Validasi sederhana: teks harus campuran huruf dan angka.
        if len(text) < 4 or len(text) > 10:
            return False
        has_alpha = any(ch.isalpha() for ch in text)
        has_digit = any(ch.isdigit() for ch in text)
        return has_alpha and has_digit

    def _estimate_parking_duration(self, plate_text):
        now = datetime.now()
        if plate_text not in self.entry_times:
            self.entry_times[plate_text] = now
            return "00:00:00", now

        delta = now - self.entry_times[plate_text]
        total_seconds = int(delta.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}", self.entry_times[plate_text]

    def _format_duration(self, start_time, end_time):
        delta = end_time - start_time
        total_seconds = int(delta.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def load_image(self):
        # Simulasi input CCTV dari file gambar lokal.
        file_path = filedialog.askopenfilename(
            title="Pilih frame CCTV (simulasi)",
            filetypes=[
                ("Image Files", "*.jpg *.jpeg *.png *.bmp *.webp"),
                ("All Files", "*.*"),
            ],
        )
        if not file_path:
            return

        image = cv2.imread(file_path)
        if image is None:
            messagebox.showerror("Error", "Gagal membaca gambar CCTV simulasi.")
            return

        self.current_file_path = file_path
        self.original_image = image
        self.annotated_image = image.copy()
        self.corrected_plate_image = None

        self.plate_var.set("-")
        self.saved_crop_var.set("-")
        self.park_time_var.set("-")
        self.current_detected_plate = ""
        self.status_var.set("Frame CCTV dimuat. Klik 'Proses Deteksi'.")
        self._render_images()

    def _detect_plate_candidate(self, image):
        # Jalur kandidat 1: deteksi berbasis kontur geometri 4 titik.
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blur, 80, 200)

        contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:120]

        candidates = []
        for contour in contours:
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

            if len(approx) != 4:
                continue

            x, y, w, h = cv2.boundingRect(approx)
            if h == 0:
                continue

            aspect_ratio = w / float(h)
            area = cv2.contourArea(approx)
            if 1.8 <= aspect_ratio <= 6.5 and 1200 <= area <= 100000:
                candidates.append((approx.reshape(4, 2), (x, y, w, h)))

        return candidates

    def _detect_text_candidates_from_frame(self, image):
        # Jalur kandidat 2: OCR langsung dari seluruh frame (multiscale).
        frame_h, frame_w = image.shape[:2]
        frame_results = self._readtext_multiscale(image, scales=[1.0, 1.4, 1.8, 2.2])
        candidates = []

        for item in frame_results:
            raw_text = item[1]
            conf = float(item[2])
            cleaned = self._clean_plate_text(raw_text)
            if not self._is_plate_like(cleaned):
                continue

            quad = np.array(item[0], dtype="float32")
            x, y, w, h = cv2.boundingRect(quad.astype(np.int32))
            if h <= 0:
                continue

            aspect_ratio = w / float(h)
            area = w * h
            if aspect_ratio < 1.5 or aspect_ratio > 8.0:
                continue
            if area < 800 or area > 150000:
                continue

            # Lokasi plat kendaraan umumnya berada di bagian bawah frame CCTV.
            y_center_norm = (y + h / 2.0) / frame_h
            location_bonus = 0.2 if y_center_norm > 0.40 else 0.0

            candidates.append(
                {
                    "quad": quad,
                    "bbox": (x, y, w, h),
                    "seed_text": cleaned,
                    "seed_conf": conf + location_bonus,
                }
            )

        return candidates

    def _readtext_multiscale(self, image, scales):
        # OCR pada beberapa skala untuk menangkap teks kecil dari sudut sulit.
        all_results = []
        for scale in scales:
            if scale == 1.0:
                scaled = image
            else:
                scaled = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

            results = self.reader.readtext(
                scaled,
                allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                paragraph=False,
            )
            if not results:
                continue

            for item in results:
                quad = np.array(item[0], dtype="float32")
                if scale != 1.0:
                    quad = quad / scale
                all_results.append((quad.tolist(), item[1], item[2]))

        return all_results

    def _remove_black_borders(self, image):
        # Hapus padding hitam agar area kendaraan menjadi lebih dominan.
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, 16, 255, cv2.THRESH_BINARY)
        points = cv2.findNonZero(mask)

        if points is None:
            return image, 0, 0

        x, y, w, h = cv2.boundingRect(points)
        area_ratio = (w * h) / float(image.shape[0] * image.shape[1])
        if area_ratio < 0.30:
            return image, 0, 0

        cropped = image[y : y + h, x : x + w]
        return cropped, x, y

    def _detect_roi_fallback_candidates(self, image):
        # Jalur kandidat 3: fokus ROI area bawah kendaraan sebagai fallback.
        h, w = image.shape[:2]
        y1 = int(h * 0.45)
        y2 = int(h * 0.92)
        x1 = int(w * 0.08)
        x2 = int(w * 0.92)

        roi = image[y1:y2, x1:x2]
        if roi.size == 0:
            return []

        roi_results = self._readtext_multiscale(roi, scales=[1.4, 1.8, 2.4, 3.0])
        candidates = []
        for item in roi_results:
            quad_roi = np.array(item[0], dtype="float32")
            text = self._clean_plate_text(item[1])
            conf = float(item[2])
            if not self._is_plate_like(text):
                continue

            quad = quad_roi.copy()
            quad[:, 0] += x1
            quad[:, 1] += y1

            bx, by, bw, bh = cv2.boundingRect(quad.astype(np.int32))
            if bw * bh < 700:
                continue

            candidates.append(
                {
                    "quad": quad,
                    "bbox": (bx, by, bw, bh),
                    "seed_text": text,
                    "seed_conf": conf + 0.25,
                }
            )

        return candidates

    def _build_plate_variants(self, plate_img):
        # Bangun beberapa versi crop plat untuk meningkatkan robust OCR.
        variants = [plate_img]

        gamma_img = self._apply_gamma_correction(plate_img, gamma=1.6)
        variants.append(gamma_img)

        gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
        eq = cv2.equalizeHist(gray)
        variants.append(cv2.cvtColor(eq, cv2.COLOR_GRAY2BGR))

        blur = cv2.GaussianBlur(eq, (3, 3), 0)
        _, th = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        variants.append(cv2.cvtColor(th, cv2.COLOR_GRAY2BGR))

        return variants

    def _merge_ocr_tokens(self, ocr_results):
        # Gabungkan token OCR sebaris agar format seperti "B" + "1963SSJ" jadi utuh.
        tokens = []
        for item in ocr_results:
            raw_text = item[1]
            cleaned = self._clean_plate_text(raw_text)
            if not cleaned:
                continue

            quad = np.array(item[0], dtype="float32")
            x, y, w, h = cv2.boundingRect(quad.astype(np.int32))
            conf = float(item[2])
            tokens.append({"text": cleaned, "x": x, "y": y, "w": w, "h": h, "conf": conf})

        if not tokens:
            return []

        tokens.sort(key=lambda t: t["y"])
        lines = []
        for token in tokens:
            placed = False
            for line in lines:
                if abs(token["y"] - line["y_mean"]) <= max(14, int(0.6 * max(token["h"], line["h_mean"]))):
                    line["items"].append(token)
                    line["y_vals"].append(token["y"])
                    line["h_vals"].append(token["h"])
                    line["y_mean"] = sum(line["y_vals"]) / len(line["y_vals"])
                    line["h_mean"] = sum(line["h_vals"]) / len(line["h_vals"])
                    placed = True
                    break
            if not placed:
                lines.append(
                    {
                        "items": [token],
                        "y_vals": [token["y"]],
                        "h_vals": [token["h"]],
                        "y_mean": token["y"],
                        "h_mean": token["h"],
                    }
                )

        merged = []
        for line in lines:
            sorted_items = sorted(line["items"], key=lambda t: t["x"])
            joined = "".join([t["text"] for t in sorted_items])
            avg_conf = sum(t["conf"] for t in sorted_items) / len(sorted_items)
            merged.append((joined, avg_conf))

        return merged

    def _run_ocr(self, plate_img):
        # Pilih hasil OCR terbaik dari beberapa varian preprocessing.
        if plate_img is None or plate_img.size == 0:
            return "", 0.0

        best_text = ""
        best_conf = 0.0
        variants = self._build_plate_variants(plate_img)

        for variant in variants:
            ocr_results = self.reader.readtext(
                variant,
                allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
                paragraph=False,
            )
            if not ocr_results:
                continue

            merged_candidates = self._merge_ocr_tokens(ocr_results)
            for merged_text, merged_conf in merged_candidates:
                if not self._is_plate_like(merged_text):
                    continue

                score = merged_conf + min(len(merged_text), 10) * 0.03
                if score > best_conf:
                    best_conf = score
                    best_text = merged_text

        if not best_text:
            return "", 0.0

        return best_text, best_conf

    def detect_plate(self):
        if self.original_image is None:
            messagebox.showwarning("Peringatan", "Load frame CCTV dulu sebelum proses deteksi.")
            return

        # Pipeline utama: kandidat -> warp -> OCR -> scoring -> pilih terbaik.
        self._ensure_reader()
        frame_raw = self.original_image.copy()
        frame, offset_x, offset_y = self._remove_black_borders(frame_raw)
        annotated = frame.copy()
        contour_candidates = self._detect_plate_candidate(frame)
        ocr_candidates = self._detect_text_candidates_from_frame(frame)
        roi_candidates = self._detect_roi_fallback_candidates(frame)

        candidates = []
        for quad_points, bbox in contour_candidates:
            candidates.append({"quad": quad_points.astype("float32"), "bbox": bbox, "seed_text": "", "seed_conf": 0.0})
        for candidate in ocr_candidates:
            candidates.append(candidate)
        for candidate in roi_candidates:
            candidates.append(candidate)

        best = None
        for candidate in candidates:
            quad_points = candidate["quad"]
            x, y, w, h = candidate["bbox"]

            warped = self._warp_plate(frame, quad_points)
            corrected = self._apply_gamma_correction(warped, gamma=1.6)
            text, conf = self._run_ocr(corrected)

            if not text and candidate["seed_text"]:
                text = candidate["seed_text"]
                conf = candidate["seed_conf"]

            if not text:
                continue

            score = conf + min(len(text), 12) * 0.05 + candidate["seed_conf"] * 0.3
            if best is None or score > best["score"]:
                best = {
                    "quad": quad_points,
                    "bbox": (x, y, w, h),
                    "plate": corrected,
                    "text": text,
                    "score": score,
                }

        if best is None:
            self.annotated_image = annotated
            self.corrected_plate_image = None
            self.plate_var.set("Tidak terbaca")
            self.saved_crop_var.set("-")
            self.park_time_var.set("-")
            self.status_var.set("Plat belum terdeteksi. Coba frame lain atau kualitas lebih jelas.")
            self._render_images()
            return

        # Kembalikan koordinat kandidat dari frame ter-crop ke frame asli.
        quad = best["quad"].astype(int)
        x, y, w, h = best["bbox"]
        plate_text = best["text"]
        corrected_plate = best["plate"]

        quad[:, 0] += offset_x
        quad[:, 1] += offset_y
        x += offset_x
        y += offset_y

        annotated = frame_raw.copy()

        cv2.polylines(annotated, [quad], True, (0, 255, 0), 2)
        cv2.rectangle(annotated, (x, y), (x + w, y + h), (20, 220, 20), 2)

        label = f"{plate_text}"
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0]
        label_top = max(0, y - label_size[1] - 10)
        label_bottom = max(0, y - 2)
        cv2.rectangle(annotated, (x, label_top), (x + label_size[0] + 8, label_bottom), (20, 220, 20), -1)
        cv2.putText(
            annotated,
            label,
            (x + 4, label_bottom - 4),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        timestamp = datetime.now()
        ts_for_name = timestamp.strftime("%Y%m%d_%H%M%S")
        safe_plate = re.sub(r"[^A-Z0-9]", "", plate_text) or "UNKNOWN"
        crop_name = f"plate_{safe_plate}_{ts_for_name}.jpg"
        crop_path = os.path.join(self.output_dir, crop_name)
        cv2.imwrite(crop_path, corrected_plate)

        # Update log kendaraan: MASUK (baru) atau PARKIR (sesi aktif).
        durasi, waktu_masuk = self._estimate_parking_duration(plate_text)
        source_name = os.path.basename(self.current_file_path)

        if plate_text not in self.active_sessions:
            self.log_no += 1
            row_id = self.log_tree.insert(
                "",
                "end",
                values=(
                    self.log_no,
                    waktu_masuk.strftime("%Y-%m-%d %H:%M:%S"),
                    "-",
                    plate_text,
                    durasi,
                    "MASUK",
                    source_name,
                    crop_name,
                ),
            )
            self.active_sessions[plate_text] = {
                "row_id": row_id,
                "entry_time": waktu_masuk,
            }
        else:
            session = self.active_sessions[plate_text]
            row_id = session["row_id"]
            self.log_tree.item(
                row_id,
                values=(
                    self.log_tree.item(row_id, "values")[0],
                    session["entry_time"].strftime("%Y-%m-%d %H:%M:%S"),
                    "-",
                    plate_text,
                    durasi,
                    "PARKIR",
                    source_name,
                    crop_name,
                ),
            )

        self.annotated_image = annotated
        self.corrected_plate_image = corrected_plate
        self.current_detected_plate = plate_text

        self.plate_var.set(plate_text)
        self.saved_crop_var.set(crop_name)
        self.park_time_var.set(durasi)
        self.status_var.set("Deteksi selesai: plat ter-crop, perspektif terkoreksi, gamma correction diterapkan.")
        self._render_images()

    def process_vehicle_exit(self):
        # Menutup sesi parkir aktif untuk plat terakhir yang terdeteksi.
        plate_text = self.current_detected_plate.strip()
        if not plate_text:
            messagebox.showwarning("Peringatan", "Deteksi plat dulu sebelum proses kendaraan keluar.")
            return

        if plate_text not in self.active_sessions:
            messagebox.showwarning("Peringatan", "Plat ini tidak ditemukan pada sesi parkir aktif.")
            return

        now = datetime.now()
        session = self.active_sessions.pop(plate_text)
        row_id = session["row_id"]
        entry_time = session["entry_time"]
        durasi_final = self._format_duration(entry_time, now)

        old_values = self.log_tree.item(row_id, "values")
        self.log_tree.item(
            row_id,
            values=(
                old_values[0],
                old_values[1],
                now.strftime("%Y-%m-%d %H:%M:%S"),
                plate_text,
                durasi_final,
                "KELUAR",
                old_values[6],
                old_values[7],
            ),
        )

        if plate_text in self.entry_times:
            del self.entry_times[plate_text]

        self.park_time_var.set(durasi_final)
        self.status_var.set(f"Kendaraan {plate_text} keluar. Total parkir: {durasi_final}")

    def save_annotated(self):
        # Simpan frame hasil anotasi ke lokasi yang dipilih user.
        if self.annotated_image is None:
            messagebox.showwarning("Peringatan", "Belum ada frame hasil deteksi yang bisa disimpan.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Simpan frame hasil deteksi",
            defaultextension=".jpg",
            filetypes=[("JPG", "*.jpg"), ("PNG", "*.png"), ("BMP", "*.bmp")],
        )
        if not file_path:
            return

        saved = cv2.imwrite(file_path, self.annotated_image)
        if saved:
            self.status_var.set(f"Frame hasil tersimpan: {file_path}")
        else:
            messagebox.showerror("Error", "Gagal menyimpan frame hasil.")

    def reset_view(self):
        # Reset tampilan tanpa menghapus histori log pada tabel.
        self.current_file_path = ""
        self.original_image = None
        self.annotated_image = None
        self.corrected_plate_image = None

        self.original_preview = None
        self.annotated_preview = None
        self.corrected_preview = None

        self.original_label.configure(image="")
        self.annotated_label.configure(image="")
        self.corrected_label.configure(image="")

        self.plate_var.set("-")
        self.saved_crop_var.set("-")
        self.park_time_var.set("-")
        self.current_detected_plate = ""
        self.status_var.set("Reset selesai. Silakan load frame CCTV simulasi baru.")


if __name__ == "__main__":
    root = tk.Tk()
    app = ParkingCCTVPrototypeApp(root)
    root.mainloop()
