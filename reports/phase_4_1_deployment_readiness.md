# Laporan Audit Kesiapan Deployment (Phase 4.1)
## GIO Motorcycle AI | Streamlit + FastAPI + YOLO26m | Railway + Vercel

> **Dokumen**: `reports/phase_4_1_deployment_readiness.md`  
> **Tanggal Evaluasi**: 9 Oktober 2026  
> **Target Lingkungan**: Backend (FastAPI + YOLO26m) di Railway, Frontend (Streamlit) di Railway/Streamlit Cloud, Domain Akses/Gateway di Vercel  
> **Status Audit**: **READY WITH BLOCKERS**

---

### A. Kesimpulan

**Status**: **`READY WITH BLOCKERS`**

**Alasan Berbasis Bukti Empiris**:
1. **Kesiapan Aplikasi & Model (READY)**:
   - Kode aplikasi backend (FastAPI) dan frontend (Streamlit) 100% stabil, lolos 57/57 pengujian otomatis (`pytest` 35 frontend, 22 backend).
   - Checkpoint model `artifacts/yolo26m_candidate.pt` (41.96 MB) tervalidasi utuh, memuat kelas riil `{0: 'motor', 1: 'orang'}`, dan waktu inferensi CPU cepat (~360–500 ms per citra).
   - Jejak memori terukur: ~313 MB saat model idle dan ~560 MB saat inferensi aktif (aman di bawah alokasi standar 1–2 GB RAM Railway).
   - Zero-persistence data terverifikasi (pemrosesan in-memory via `io.BytesIO`, tanpa penulisan citra ke disk atau database).
2. **Kendala Konfigurasi Deployment (BLOCKERS)**:
   - **Blocker 1 (Dockerfile Backend Hardcoded Port)**: `inference/Dockerfile` menggunakan `CMD ["uvicorn", "inference.app:app", "--host", "0.0.0.0", "--port", "8000"]`. Di Railway, port dinamis disuntikkan via variabel `$PORT`. Format exec array ini mengabaikan `$PORT` dan dapat menggagalkan healthcheck Railway.
   - **Blocker 2 (Inkompatibilitas Reverse Proxy Vercel ke Streamlit)**: Vercel Edge Rewrites tidak mendukung proxy WebSocket persisten (`/_stcore/stream`) ke origin eksternal, dan Vercel Serverless Function memiliki batas payload 4.5 MB (bertabrakan dengan requirement upload citra 10 MB). Direct reverse proxy Streamlit via Vercel terbukti berisiko memicu infinite reload loop.
   - **Blocker 3 (Keamanan Git & Ketiadaan `.gitignore`)**: Belum ada file `.gitignore` di root repositori. Repositori saat ini memuat `.venv/` (berukuran ~4.5 GB), artefak pengujian/screenshot sementara (~300 KB), dan file ekstraksi model `yolo26m_best.pt/` (~45 MB). Melakukan `git add .` tanpa `.gitignore` akan mengunggah gigabytes data biner ke Git.
   - **Blocker 4 (Ketiadaan Konfigurasi Deployment Dashboard)**: `dashboard/` belum memiliki `Dockerfile` mandiri atau konfigurasi buildpack Railway/Nixpacks khusus untuk production.

---

### B. Matriks Temuan Audit

| Area | Status | Bukti Temuan | Risiko | Rekomendasi Mitigasi |
|---|---|---|---|---|
| **Repository** | `WARNING` | Repositori belum diinisialisasi Git, belum ada file `.gitignore` di root. Terdapat folder `.venv` (~4.5 GB), model ekstraksi `yolo26m_best.pt/` (~45 MB), serta file screenshot hasil testing di root. | File virtual environment raksasa dan file dump sementara tidak sengaja ter-commit ke remote repo. | Buat `.gitignore` komprehensif mengabaikan `.venv/`, `*.png`, `*.html`, `__pycache__/`, dan cache sebelum `git init`. |
| **Dependency** | `WARNING` | `inference/requirements.txt` mencantumkan `torch==2.14.1+cpu` dan dependency testing (`pytest`, `httpx`). Dockerfile memasang torch CPU via `--index-url https://download.pytorch.org/whl/cpu`. `dashboard/requirements.txt` minimal dan bersih (4 paket). | Build gagal jika buildpack standar mencoba mengunduh wheel `+cpu` dari indeks PyPI standar, atau build mengunduh wheel GPU/CUDA (>2.5 GB). | Pertahankan Dockerfile multi-stage dengan CPU index URL eksplisit untuk backend; pisahkan dev/test dependencies. |
| **Backend Railway** | `BLOCKED` | `inference/Dockerfile` mengeksekusi `CMD ["uvicorn", "...", "--port", "8000"]`. Build context mengasumsikan root repositori (`COPY artifacts/...`). Tidak ada `railway.json`. | Railway menyuntikkan `$PORT` dinamis. Eksekusi exec array tidak membaca `$PORT`, menyebabkan healthcheck Railway gagal / timeout saat deploy. | Ubah CMD menjadi shell format: `CMD sh -c "uvicorn inference.app:app --host 0.0.0.0 --port ${PORT:-8000}"` dan tentukan root build context `.`. |
| **Dashboard Streamlit** | `WARNING` | `dashboard/services/inference_client.py` membaca `os.getenv("INFERENCE_API_URL", "http://127.0.0.1:8000")`. Belum ada `Dockerfile` untuk dashboard. Port Streamlit default 8501. | Di Railway, Streamlit harus mendengar pada `$PORT` dinamis dan diarahkan ke URL publik/internal FastAPI. | Buat Dockerfile ringan untuk Streamlit dengan `--server.port $PORT --server.address 0.0.0.0` dan pasang env `INFERENCE_API_URL`. |
| **Integrasi Vercel** | `BLOCKED` | `poc/vercel-streamlit-proxy/vercel.json` menggunakan rewrite `/:path*` -> origin luar. Vercel Edge Network memutus koneksi WebSocket (`101 Switching Protocols`) setelah 30–60 detik dan memiliki request body limit 4.5 MB. | Dashboard Streamlit macet pada pesan "Connecting..." / terus-menerus reload, dan gagal mengunggah citra di atas 4.5 MB. | **Gunakan Vercel sebagai Showcase Portal / Landing Gateway** dengan tombol link/redirect langsung ke instance Streamlit di Railway, atau HTTP 307/308 redirect. |
| **Model & Resource** | `PASS` | Pengukuran empiris via `psutil`: idle model = 313 MB RAM, peak inference (1280x720) = 560 MB RAM. CPU inference time: 360–500 ms. Ukuran file kandidat = 41.96 MB. | Memori melonjak jika beberapa request inferensi berjalan paralel pada kontainer dengan batas memori < 512 MB. | Tetapkan batas resource kontainer Railway minimal **1 GB RAM** (disarankan 2 GB RAM) dan 1 vCPU. |
| **Environment & Secret** | `PASS` | Grep audit membuktikan **nol credential / secret hardcoded** di seluruh codebase. Variabel yang dibutuhkan: `INFERENCE_API_URL`, `PORT`, `MODEL_PATH`, `MAX_UPLOAD_MB`, `ALLOWED_ORIGINS`. | Kesalahan konfigurasi URL backend publik membuat dashboard menampilkan error `CONNECTION_FAILED`. | Siapkan dokumen `.env.example` terpusat dan pastikan variabel disuntikkan melalui Railway Dashboard. |
| **Tes Regresi** | `PASS` | Rangkaian tes lokal berjalan sempurna: `dashboard/tests`: 35/35 PASSED, `inference/tests`: 22/22 PASSED (Total: 57/57 PASSED, 100%). Endpoint lokal aktif merespons 200 OK. | Tidak ada regresi fungsional atau logika deteksi. | Jalankan smoke test otomatis pasca deployment menggunakan script pengujian live yang sudah tersedia. |

---

### C. Analisis & Rekomendasi Arsitektur Deployment (Railway + Vercel)

#### 1. Masalah Fundamental Vercel vs Streamlit
- **Protokol Komunikasi Streamlit**: Streamlit membutuhkan koneksi **WebSocket dua arah persisten** (`/_stcore/stream`) untuk sinkronisasi `SessionState`, delta widgets, dan eksekusi skrip Python.
- **Karakteristik Vercel**:
  - Vercel dioptimalkan untuk arsitektur *Serverless Jamstack / Edge functions* yang bersifat stateless (request-response singkat).
  - Vercel Rewrites (`vercel.json`) tidak mem-proxy upgrade WebSocket menuju server eksternal secara stabil.
  - Vercel Serverless memiliki batas ukuran payload request **4.5 MB**, yang melanggar spesifikasi sistem GIO (upload citra hingga **10 MB**).
  - Upaya memaksakan reverse proxy Streamlit melalui Vercel menghasilkan gejala umum: aplikasi mengalami *looping reconnect* atau session terputus saat pengunjung sedang melakukan analisis.

#### 2. Rekomendasi Arsitektur Terbaik (Dual Railway Service + Vercel Portal/Gateway)

```text
Pengunjung Pameran / Pengguna
       │
       ├───► [Akses Domain Utama Vercel: https://gio-motorcycle.vercel.app]
       │        │
       │        ▼ (Landing Page Showcase, Info Riset, & Gateway CTA)
       │     "Buka Live Demo Deteksi" ───┐
       │                                 │
       ▼                                 ▼
[Browser Client] ◄───────────────────────┘
       │
       │ (Koneksi Langsung HTTP + WebSocket Persisten)
       ▼
┌────────────────────────────────────────────────────────────────────────┐
│ RAILWAY PROJECT: gio-motorcycle-ai                                     │
│                                                                        │
│  [Service 1: Frontend Streamlit Dashboard]                             │
│   - URL Publik: https://gio-dashboard-production.up.railway.app        │
│   - Runtime: Python 3.11 Container (Port $PORT dinamis)               │
│   - Mengelola UI, Upload Citra, Visualisasi Bounding Box, Unduh JPEG   │
│   - Env: INFERENCE_API_URL=http://gio-inference.railway.internal:8000 │
│          (atau URL publik Service 2)                                   │
│        │                                                               │
│        │ (Multipart Form Request HTTP: POST /predict)                  │
│        ▼                                                               │
│  [Service 2: Backend FastAPI Inference Service]                       │
│   - URL Internal / Publik: https://gio-api-production.up.railway.app   │
│   - Runtime: Dockerfile (Python 3.11-slim + PyTorch CPU + OpenCV)      │
│   - Checkpoint: /app/artifacts/yolo26m_candidate.pt                    │
│   - Memori: 1 GB RAM (Idle ~313 MB, Active ~560 MB)                    │
│   - Zero-Persistence (In-Memory Processing)                            │
└────────────────────────────────────────────────────────────────────────┘
```

**Peran Masing-Masing Platform**:
1. **Railway**:
   - Menjalankan **FastAPI Inference Service** (Service 2) menggunakan Dockerfile yang telah divalidasi.
   - Menjalankan **Streamlit Dashboard** (Service 1) sebagai persistent container yang mendukung WebSocket tanpa batas idle timeout.
   - Menyediakan jaringan privat antar-layanan (*Railway Private Networking*), sehingga transfer citra dari Streamlit ke FastAPI berlangsung sangat cepat di jaringan internal tanpa latensi publik.
2. **Vercel**:
   - Berfungsi sebagai **Akses & Domain Resmi Proyek** (`https://gio-motorcycle.vercel.app`).
   - Menyajikan *Showcase Portal / Presentation Gateway* yang menjelaskan latar belakang riset, arsitektur YOLO26m, atribusi mAP@50 89.59%, dan tombol langsung ke Live Dashboard di Railway.
   - Alternatif: Dapat dikonfigurasikan dengan HTTP 307 / 308 redirect (`vercel.json`) dari `https://gio.vercel.app` langsung ke `https://gio-dashboard-production.up.railway.app` jika pengguna menginginkan URL Vercel langsung membuka Streamlit.

---

### D. Audit Spesifikasi Lingkungan & Dependensi

#### 1. Versi Runtime Python & Paket Utama
- **Python**: `3.11.9` (Tervalidasi di `.venv` lokal; kompatibel dengan `python:3.11-slim` di Docker).
- **FastAPI**: `0.143.0` (Asynchronous HTTP framework).
- **Uvicorn**: `0.54.0` (ASGI server).
- **PyTorch**: `2.14.1+cpu` (Wheel CPU-only, ukuran ~170 MB vs GPU wheel ~2.5 GB).
- **Ultralytics**: `8.4.174` (YOLO26m architecture runner).
- **Streamlit**: `1.65.0` (Frontend interactive dashboard).
- **Pillow**: `12.3.0` (In-memory image validation and JPEG encoding).
- **OpenCV (`opencv-python`)**: `5.0.0.93` (Image annotation rendering).

#### 2. Kebutuhan Sumber Daya (Resource Footprint)
- **Ukuran Checkpoint**: 43.997.307 bytes (~41.96 MB).
- **RAM Idle**: ~313 MB (FastAPI + YOLO26m loaded).
- **RAM Peak Inference**: ~560 MB (saat decoding & inference citra 1280x720).
- **CPU Time**: ~360–500 ms per frame pada CPU modern.
- **Rekomendasi Railway Plan**: Container RAM minimal **1 GB** (disarankan **2 GB** untuk mengantisipasi concurrent users saat pameran).

---

### E. Daftar Variabel Lingkungan (Environment Variables)

| Nama Variabel | Service Pemilik | Tipe / Default | Status | Deskripsi & Fungsi |
|---|---|---|---|---|
| `PORT` | FastAPI & Streamlit | Integer (`8000` / `8501`) | **Wajib (Runtime)** | Port HTTP dinamis yang disuntikkan platform Railway saat kontainer dijalankan. |
| `INFERENCE_API_URL` | Streamlit Dashboard | URL (`http://127.0.0.1:8000`) | **Wajib (Production)** | URL dasar endpoint FastAPI (contoh: `https://gio-api-production.up.railway.app` atau `http://gio-api.railway.internal:8000`). |
| `MODEL_PATH` | FastAPI Inference | Path (`/app/artifacts/yolo26m_candidate.pt`) | Opsional | Lokasi absolut/relatif file checkpoint YOLO26m di dalam container backend. |
| `MAX_UPLOAD_MB` | FastAPI Inference | Integer (`10`) | Opsional | Batas maksimum ukuran file citra yang diizinkan (default 10 MB). |
| `ALLOWED_ORIGINS` | FastAPI Inference | String (`*`) | Opsional | Daftar domain asal yang diizinkan untuk CORS (pisahkan dengan koma di production). |
| `YOLO_AUTOINSTALL` | FastAPI Inference | String (`0`) | Bawaan Kode | Mencegah Ultralytics mengunduh library tambahan saat runtime. |

*Catatan Keamanan: Tidak ada API key, token rahasia, atau kredensial database yang diperlukan.*

---

### F. Rencana Aksi Sebelum Deployment (Next Steps)

Untuk melangkah ke **Phase 4.2 (Deployment Implementation)**, berikut urutan langkah kerja teknis yang direkomendasikan:

1. **Langkah 1: Penyiapan Keamanan Repositori & Git**
   - Buat berkas `.gitignore` komprehensif (abaikan `.venv/`, `__pycache__/`, file dump screenshot `*.png`, file HTML dump, `.pytest_cache/`).
   - Evaluasi penyimpanan `artifacts/yolo26m_candidate.pt` (41.96 MB aman di Git standar karena < 50 MB, tetapi pastikan `yolo26m_best.pt/` diabaikan untuk menghindari duplikasi).
2. **Langkah 2: Penyesuaian Dockerfile Backend untuk Railway**
   - Perbarui baris `CMD` pada `inference/Dockerfile` agar membaca `$PORT` dinamis:
     `CMD sh -c "uvicorn inference.app:app --host 0.0.0.0 --port ${PORT:-8000}"`
   - Siapkan `railway.json` dengan konfigurasi root context.
3. **Langkah 3: Pembuatan Konfigurasi Deployment Dashboard**
   - Buat Dockerfile mandiri untuk `dashboard/` yang menjalankan Streamlit dengan `--server.port $PORT --server.address 0.0.0.0`.
4. **Langkah 4: Deployment Backend di Railway & Validasi Live**
   - Deploy backend FastAPI ke Railway, periksa status startup log dan readiness endpoint `GET /` (harus `200 OK`).
5. **Langkah 5: Deployment Dashboard di Railway & Integrasi URL**
   - Deploy dashboard ke Railway, suntikkan `INFERENCE_API_URL` mengarah ke Railway backend.
6. **Langkah 6: Konfigurasi Akses Domain Vercel**
   - Siapkan proyek Vercel dengan gateway portal / HTTP redirect ke instance Railway Streamlit.
7. **Langkah 7: End-to-End Production Smoke Test**
   - Uji alur upload citra nyata hingga download JPEG pada domain publik di luar jaringan lokal.

---
*Laporan audit selesai disusun. Menunggu persetujuan pengguna sebelum melakukan tindakan deployment.*
