# PRD — YOLO26m Motorcycle Passenger Violation Detection

> Product Requirements Document. Simpan file ini di root `Projek GIO/`.
> Dokumen ini menjelaskan **apa** yang dibangun. `design.md` menjelaskan desain UI,
> `techstack.md` menjelaskan implementasi teknis, dan `agent.md` mengatur cara kerja AI coding agent.

## 1. Ringkasan Produk

### 1.1 Nama kerja

**YOLO26m Motorcycle Passenger Violation Detection Dashboard**

### 1.2 Tujuan

Membangun prototype dashboard untuk pameran/demo yang menerima satu foto sepeda motor,
menjalankan checkpoint YOLO26m milik proyek, mendeteksi objek yang dibutuhkan, menghubungkan
person dengan motorcycle menggunakan Intersection over Area (IoA), menghitung person pada
setiap motorcycle, lalu memberikan status **AMAN** atau **PELANGGARAN** untuk setiap motor.

Ini adalah prototype analisis citra berbantuan AI. Sistem bukan ETLE resmi dan bukan alat
penetapan atau penindakan hukum.

### 1.3 Konteks proyek dan aset yang tersedia

Struktur root proyek yang terlihat saat penyusunan dokumen:

```text
Projek GIO/
├── .agents/
│   └── skills/
│       ├── animate/
│       ├── antislop/
│       ├── antislop-layoutmobile/
│       ├── antislop-ui/
│       ├── api-and-interface-design/
│       ├── code-review-and-quality/
│       ├── debugging-and-error-recovery/   # nama lengkap perlu dicek jika tampilan terpotong
│       ├── design-taste-frontend/
│       ├── documentation-and-adrs/
│       ├── emil-design-eng/
│       ├── frontend-ui-engineering/
│       ├── hallmark/
│       ├── incremental-implementation/
│       ├── performance-optimization/
│       ├── review-animations/
│       ├── security-and-hardening/
│       └── shadcn/
├── yolo26m_best.pt                    # nama artifact yang terlihat; verifikasi di filesystem
├── prd.md
├── design.md
├── techstack.md
├── agent.md
└── TASKS.md                            # dibuat/diperbarui agent saat implementasi
```

Tampilan VS Code memperlihatkan `yolo26m_best.pt\best` dan entri seperti `data.pkl`, `byteorder`,
`version`, serta direktori/data internal. Tampilan itu bisa menunjukkan struktur internal arsip
checkpoint, bukan berarti path filesystem `yolo26m_best.pt/best` pasti dapat digunakan sebagai
path model. Agent wajib memeriksa jenis artifact yang sebenarnya sebelum menetapkan `MODEL_PATH`.
Jangan mengekstrak, mengubah, atau menyusun ulang artifact secara spekulatif.

Skill yang tersedia berada di `.agents/skills/`. Agent harus membaca instruksi skill yang relevan
sebelum melakukan task; nama folder saja tidak cukup untuk menyimpulkan seluruh instruksinya.

## 2. Masalah yang Diselesaikan

Model penelitian perlu disajikan sebagai aplikasi yang mudah dicoba pengunjung. Aplikasi perlu:

1. menerima foto secara sederhana;
2. menampilkan bounding box dan hasil deteksi;
3. mengasosiasikan person ke motorcycle dengan aturan yang konsisten;
4. menghitung person per motor dan menampilkan status tiap motor;
5. menjelaskan keterbatasan hasil tanpa melebih-lebihkan kemampuan model.

## 3. Sasaran dan Kriteria Keberhasilan

Pengunjung pameran, dosen, dan juri harus dapat membuka aplikasi tanpa akun, mengunggah satu
foto, menjalankan analisis, memahami hasil, melihat bukti visual, dan mengunduh annotated image.

Kriteria keberhasilan utama:

- aplikasi menerima satu gambar JPG/JPEG/PNG;
- service inference berhasil memuat artifact YOLO26m proyek yang terverifikasi;
- model mendeteksi kelas yang telah dikonfirmasi dari metadata checkpoint;
- logika association memakai IoA threshold `0.60`;
- status ditentukan **per motorcycle**: 0–2 person terkait = `AMAN`, 3 atau lebih = `PELANGGARAN`;
- hasil mencakup gambar anotasi, ringkasan jumlah objek, detail per motor, confidence, dan IoA bila tersedia;
- pengguna dapat mengunduh gambar anotasi;
- gambar unggahan tidak disimpan permanen;
- tidak ada login, database, Supabase, atau detection history.

## 4. Pengguna

### 4.1 Pengunjung pameran

Tidak harus memahami computer vision. Membutuhkan alur singkat, label status yang jelas, dan
penjelasan sederhana.

### 4.2 Reviewer teknis

Membutuhkan informasi model, confidence, IoA, hasil per objek, batasan sistem, dan penjelasan
pemisahan antara object detection, association, counting, dan decision rule.

## 5. Ruang Lingkup

### 5.1 Termasuk dalam MVP

- Dashboard overview.
- Upload dan analisis **satu gambar per request**.
- Preview gambar asli dan annotated image.
- Ringkasan total motorcycle, total person terdeteksi, dan motorcycle berstatus pelanggaran.
- Daftar hasil per motorcycle, termasuk jumlah person, status, serta detail association bila tersedia.
- Confidence score untuk detections.
- IoA setiap pasangan person–motor yang relevan.
- Unduh annotated image.
- Halaman How It Works, Model Information, dan About.
- Pesan loading, empty state, dan error yang dapat dipahami.

### 5.2 Tidak termasuk

- Video, webcam, CCTV live/RTSP, frame extraction, atau tracking antar-frame.
- Login, registrasi, role/permission, atau profil pengguna.
- Database, Supabase, riwayat analisis, penyimpanan gambar permanen, atau storage bucket.
- Retraining/fine-tuning model.
- Penggantian checkpoint dengan model pretrained lain.
- Klaim sebagai sistem penindakan hukum resmi.

## 6. Alur Pengguna

```text
Buka aplikasi
  → Dashboard
  → Detection
  → Upload satu JPG/JPEG/PNG
  → Preview
  → Analyze
  → FastAPI inference service
  → YOLO26m detection
  → Person–motorcycle association (IoA)
  → Counting per motor
  → Status AMAN/PELANGGARAN
  → Annotated image + detail hasil
  → Tinjau atau unduh hasil
```

## 7. Functional Requirements

| ID | Requirement | Prioritas |
|---|---|---|
| FR-01 | Aplikasi dapat digunakan tanpa login. | MUST |
| FR-02 | Pengguna mengunggah tepat satu gambar per analisis. | MUST |
| FR-03 | Format yang diterima JPG, JPEG, dan PNG. | MUST |
| FR-04 | Sistem memvalidasi tipe dan ukuran file sebelum inference. | MUST |
| FR-05 | Dashboard mengirim gambar ke FastAPI inference service. | MUST |
| FR-06 | Service memuat checkpoint YOLO26m proyek yang telah diverifikasi. | MUST |
| FR-07 | Class ID dan nama kelas dikonfirmasi dari metadata model, bukan diasumsikan. | MUST |
| FR-08 | Person–motorcycle association menggunakan IoA threshold `0.60`. | MUST |
| FR-09 | Jumlah person dihitung secara terpisah untuk tiap motorcycle. | MUST |
| FR-10 | Setiap motorcycle diberi status berdasarkan rule 0–2 = AMAN dan ≥3 = PELANGGARAN. | MUST |
| FR-11 | Hasil visual menampilkan bounding box dan label yang konsisten. | MUST |
| FR-12 | Sistem menampilkan confidence detection. | MUST |
| FR-13 | Detail IoA/association ditampilkan jika data tersebut tersedia dari pipeline. | MUST |
| FR-14 | Dashboard menampilkan ringkasan jumlah motorcycle, person, dan motorcycle pelanggaran. | MUST |
| FR-15 | Pengguna dapat membaca hasil individual per motorcycle. | MUST |
| FR-16 | Pengguna dapat mengunduh annotated image. | MUST |
| FR-17 | Error ditampilkan menggunakan pesan yang ramah. | MUST |
| FR-18 | Tersedia halaman How It Works. | SHOULD |
| FR-19 | Tersedia halaman Model Information. | SHOULD |
| FR-20 | Tersedia halaman About/Project. | SHOULD |

## 8. Persyaratan Model dan Logika

### 8.1 Checkpoint

Nama artifact sumber yang ditemukan pada filesystem adalah folder `yolo26m_best.pt/best/` (berupa direktori hasil ekstraksi arsip PyTorch).
Untuk kebutuhan inferensi dan loading resmi Ultralytics, artifact sumber telah dikemas ulang secara non-destruktif ke:
`artifacts/yolo26m_candidate.pt` (telah divalidasi identik byte-for-byte terhadap 778 file sumber dan lolos uji loading Ultralytics).
Sumber asli `yolo26m_best.pt/best/` tetap dipertahankan utuh dan tidak diubah.

Catatan metrik penelitian: nilai mAP@50 `0.8959` tercantum pada spesifikasi proyek sebelumnya.
Nilai ini harus ditampilkan sebagai hasil evaluasi penelitian, bukan sebagai metrik yang otomatis
terbukti hanya dari nama atau isi file checkpoint. Pertahankan nilainya jika telah dikonfirmasi
pada paper/laporan yang menjadi sumber proyek.

### 8.2 Class names

Berdasarkan metadata checkpoint yang telah diverifikasi melalui dynamic loading dan disassembly metadata, nama kelas dan ID mentah model adalah:
- ID `0`: `motor`
- ID `1`: `orang`

Secara semantik untuk pipeline dan tampilan antarmuka, kelas `0` mewakili `motorcycle/motor` dan kelas `1` mewakili `person/orang`. Pipeline inferensi wajib memetakan ID `0` dan `1` tersebut, bukan mencari string bahasa Inggris default COCO (`person` dan `motorcycle`).

### 8.3 Association

Gunakan definisi:

`IoA(person, motorcycle) = area(person ∩ motorcycle) / area(person)`

Sebuah person memenuhi threshold untuk sebuah motorcycle jika `IoA >= 0.60`.
Unassociated persons tidak ditambahkan ke hitungan penumpang motorcycle mana pun.

**Aturan multi-motor yang telah disetujui pemilik proyek**:
- Jika seorang person memenuhi threshold `IoA >= 0.60` untuk lebih dari satu motorcycle, orang tersebut **diasosiasikan hanya ke motorcycle dengan nilai IoA tertinggi** (*highest IoA*).
- Satu person tidak boleh dihitung pada lebih dari satu motorcycle.
- Jika terdapat nilai IoA yang sama persis, gunakan tie-breaker deterministik berdasarkan indeks deteksi motorcycle terkecil (indeks pertama).

### 8.4 Rule status

```python
if associated_person_count >= 3:
    status = "PELANGGARAN"
else:
    status = "AMAN"
```

Rule berlaku pada setiap motorcycle secara independen, bukan hanya berdasarkan total person dalam
foto. Status adalah output rule prototype, bukan keputusan hukum.

## 9. Output Minimum

- Preview gambar asli.
- Annotated image dengan bounding box/label.
- Total motorcycle terdeteksi.
- Total person terdeteksi.
- Total motorcycle berstatus `PELANGGARAN`.
- Untuk tiap motorcycle: ID tampilan, person count, status, dan association detail yang tersedia.
- Confidence untuk detection.
- IoA untuk pasangan yang dievaluasi, jika tersedia.
- Waktu pemrosesan bila dapat diukur.
- Tombol unduh annotated image.

## 10. Halaman Aplikasi

1. **Dashboard** — pengenalan singkat, CTA ke Detection, ringkasan cara kerja, dan batasan prototype.
2. **Detection** — upload, preview, analisis, annotated image, summary, hasil per motor, dan unduh.
3. **How It Works** — pipeline detection → association → counting → decision.
4. **Model Information** — jenis model, provenance checkpoint, kelas terverifikasi, IoA threshold,
   metrik paper yang sudah dikonfirmasi, dan keterbatasan.
5. **About** — konteks proyek/tim yang memang disetujui untuk ditampilkan ke publik.

## 11. Non-Functional Requirements

- **Usability:** alur inti mudah dipahami oleh pengunjung non-teknis.
- **Performance:** target awal 5–10 detik per gambar; 10–20 detik masih dapat diterima untuk prototype
  pameran. Angka tersebut adalah target aplikasi, bukan jaminan.
- **Reliability:** kegagalan file, model, API, atau jaringan mempunyai penanganan yang eksplisit.
- **Privacy:** tidak ada penyimpanan permanen gambar unggahan atau logging isi gambar.
- **Maintainability:** pemisahan dashboard, API, inferensi, association logic, dan annotation.
- **Responsive UI:** paling baik pada desktop pameran, tetap dapat digunakan pada viewport kecil.
- **Honesty:** jangan menampilkan angka, progres, status, atau data riwayat palsu.

## 12. Deployment Requirements

Target stack proyek:

- Streamlit untuk dashboard.
- FastAPI untuk API/inference service.
- Railway untuk menjalankan service model.
- Vercel sebagai requirement deployment/access proyek.

Mekanisme menjalankan/mengakses Streamlit melalui Vercel telah dievaluasi melalui PoC pada `poc/vercel-streamlit-proxy/`.
Temuan teknis menunjukkan bahwa Vercel Rewrites/Serverless tidak mendukung koneksi WebSocket persisten secara stabil untuk server eksternal Streamlit. Solusi yang direkomendasikan adalah menjalankan frontend Streamlit pada platform berbasis persistent container (seperti Railway atau Streamlit Community Cloud) dan mengarahkan domain Vercel ke instance tersebut, atau menyajikan landing gateway.

## 13. Acceptance Checklist

- [x] Artifact sumber `yolo26m_best.pt/best/` dikemas ulang ke `artifacts/yolo26m_candidate.pt` dan sukses dimuat oleh Ultralytics.
- [x] Class names/IDs diverifikasi dari model (`0: motor`, `1: orang`).
- [ ] Endpoint health dan prediction berfungsi.
- [ ] JPG/JPEG dan PNG valid diterima; tipe/ukuran invalid ditolak.
- [ ] Threshold IoA tepat di `0.60` diuji.
- [ ] 2 person terkait menghasilkan `AMAN`; 3 person terkait menghasilkan `PELANGGARAN`.
- [ ] Beberapa motorcycle diproses secara independen.
- [ ] Annotated image dan detail hasil tampil.
- [ ] Annotated image dapat diunduh.
- [ ] Error, loading, dan empty states berfungsi.
- [ ] Tidak ada login, Supabase, database, history, atau penyimpanan gambar permanen.
- [ ] Dashboard Streamlit berhasil berkomunikasi dengan FastAPI di Railway.
- [x] Requirement Vercel telah dianalisis melalui PoC dan status/solusinya didokumentasikan di `poc/vercel-streamlit-proxy/`.
- [x] Dokumen dan `TASKS.md` berada di root `Projek GIO/`.
