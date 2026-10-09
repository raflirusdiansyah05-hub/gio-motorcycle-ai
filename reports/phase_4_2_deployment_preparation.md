# Laporan Persiapan & Konfigurasi Deployment (Phase 4.2)
## GIO Motorcycle AI | Railway Backend + Railway Streamlit + Vercel Showcase Portal

> **Dokumen**: `reports/phase_4_2_deployment_preparation.md`  
> **Tanggal**: 9 Oktober 2026  
> **Status**: **PASS (Persiapan Konfigurasi Siap untuk Phase 4.3 Deployment)**  
> **Target Arsitektur**: Dual-Service Railway (FastAPI + Streamlit) & Vercel Showcase/Redirect Gateway

---

### 1. Ringkasan Perubahan

Pada Phase 4.2, seluruh blocker konfigurasi yang ditemukan pada audit Phase 4.1 telah diselesaikan secara menyeluruh tanpa mengubah logika aplikasi, model AI, aturan deteksi, atau antarmuka yang telah disetujui:

1. **Keamanan Repositori**: Dibuat file `.gitignore` komprehensif di root repositori untuk mencegah virtual environment (~4.5 GB), artefak dump pengujian, dan folder ekstraksi model cadangan terunggah ke Git, sambil tetap memastikan checkpoint resmi `artifacts/yolo26m_candidate.pt` aman terlindungi.
2. **Backend FastAPI Railway Readiness**: `inference/Dockerfile` diperbarui dengan pola shell execution `CMD ["sh", "-c", "exec uvicorn inference.app:app --host 0.0.0.0 --port ${PORT:-8000}"]` sehingga Uvicorn dapat mendengarkan port dinamis `$PORT` yang disuntikkan Railway sekaligus menangani sinyal terminasi kontainer secara graceful.
3. **Frontend Containerization**: Dibuat `dashboard/Dockerfile` mandiri berbasis `python:3.11-slim` yang dirancang khusus untuk Streamlit, menggunakan build context root monorepo, mendukung `$PORT` dinamis, dan terisolasi dari dependensi berat PyTorch/Ultralytics (menghasilkan image frontend ringan ~250–300 MB).
4. **Dokumentasi Lingkungan**: Dibuat file template `.env.example` terpusat yang mendokumentasikan setiap variabel lingkungan, pemilik service, sifat wajib/opsional, dan pemisahan nilai lokal vs produksi.
5. **Panduan Setup 2-Service Railway**: Disusun panduan konfigurasi step-by-step untuk deploy backend `gio-inference` dan frontend `gio-dashboard` dalam satu proyek Railway menggunakan private networking internal.

---

### 2. Berkas Baru dan Berkas yang Diubah

| Berkas | Status | Deskripsi Perubahan |
|---|---|---|
| `.gitignore` | **Baru** | Aturan pengabaian `.venv/`, cache Python, hasil uji dump, `.env`, dan direktori ekstraksi cadangan `yolo26m_best.pt/`. Mempertahankan `artifacts/yolo26m_candidate.pt`. |
| `inference/Dockerfile` | **Diubah** | Mengganti `CMD` statis dengan shell exec dinamis `${PORT:-8000}` untuk Railway. |
| `dashboard/Dockerfile` | **Diubah** | Kontainer mandiri Streamlit berbasis `python:3.11-slim`, `ENV PYTHONPATH=/app`, port dinamis `${PORT:-8501}`, headless mode, dan isolasi dari PyTorch. |
| `dashboard/__init__.py` | **Baru** | Deklarasi package resmi `dashboard` untuk Python package discovery di dalam kontainer. |
| `dashboard/app.py` | **Diubah** | Ditambahkan injeksi defensif `sys.path` untuk menjamin resolusi impor root package. |
| `.env.example` | **Baru** | Template dokumentasi variabel lingkungan untuk lokal, Railway internal private networking, dan publik. |
| `reports/phase_4_2_deployment_preparation.md` | **Baru/Diperbarui** | Laporan teknis lengkap persiapan deployment Phase 4.2 dan resolusi `ModuleNotFoundError`. |
| `TASKS.md` | **Diubah** | Pelacakan status penyelesaian Phase 4.2, hotfix `dashboard`, dan pembaruan roadmap Phase 4.3. |

---

### 3. Isi dan Cakupan `.gitignore`

Aturan `.gitignore` dirancang mengikuti prinsip *least privilege* dan proteksi aset biner:

- **Virtual Environment**: `.venv/`, `venv/`, `env/`, `ENV/` (mencegah commit ribuan paket lokal berukuran ~4.5 GB).
- **Python Cache**: `__pycache__/`, `*.py[cod]`, `*$py.class`, `.Python`.
- **Testing Cache**: `.pytest_cache/`, `.coverage`, `htmlcov/`.
- **Secret & Lingkungan Lokal**: `.env`, `.env.local`, `.env.*.local`, dengan pengecualian eksplisit template: `!.env.example`.
- **Artefak Uji Sementara**: `real_browser_screenshot.png`, `screenshot_*.png`, `test_*.png`, `sidebar_dump.html`, `*.log`.
- **Folder Ekstraksi Cadangan**: `yolo26m_best.pt/` (direktori lokal awal berisi 778 file tensor PyTorch yang tidak dibutuhkan container build).
- **Perlindungan Checkpoint Model Resmi**:
  ```gitignore
  !artifacts/
  !artifacts/yolo26m_candidate.pt
  ```
  *Kebijakan*: Checkpoint `yolo26m_candidate.pt` (41.96 MB) dipastikan **tetap terdaftar** agar build container backend di Railway dapat menyalin file bobot model secara otomatis.

---

### 4. Keputusan Build Context dan Dockerfile Path

Kedua service Railway dikonfigurasi menggunakan **satu repositori (Monorepo)** dengan build context di **root repositori (`.`)**:

```text
Projek GIO/ (Root Build Context: .)
├── artifacts/
│   └── yolo26m_candidate.pt      <── Dibutuhkan backend saat build
├── inference/
│   ├── Dockerfile                 <── Service 1 Dockerfile
│   ├── app.py
│   └── requirements.txt
├── dashboard/
│   ├── Dockerfile                 <── Service 2 Dockerfile
│   ├── app.py
│   └── requirements.txt
└── .streamlit/
    └── config.toml                <── Dibutuhkan frontend saat build
```

| Service | Dockerfile Path | Build Context | Alasan Teknis |
|---|---|---|---|
| **`gio-inference`** | `inference/Dockerfile` | `.` (Root) | Container backend perlu menyalin `artifacts/yolo26m_candidate.pt` dan package `inference/`. Menggunakan subdirektori sebagai context akan menggagalkan akses ke folder `artifacts/`. |
| **`gio-dashboard`** | `dashboard/Dockerfile` | `.` (Root) | Container frontend perlu menyalin `.streamlit/config.toml` (konfigurasi tema dan upload 10 MB) serta package `dashboard/`. |

---

### 5. Strategi Penggunaan Variabel `PORT`

Railway mengalokasikan port secara dinamis pada setiap deployment kontainer melalui variabel lingkungan `$PORT`.

- **Pola Command Shell Exec**:
  - Backend: `CMD ["sh", "-c", "exec uvicorn inference.app:app --host 0.0.0.0 --port ${PORT:-8000}"]`
  - Frontend: `CMD ["sh", "-c", "exec streamlit run dashboard/app.py --server.address 0.0.0.0 --server.port ${PORT:-8501} --server.headless true"]`
- **Keunggulan Pola `sh -c "exec ..."`**:
  1. *Variabel Expansion*: Sintaks `${PORT:-8000}` memastikan jika Railway menyuntikkan `PORT=5678`, server langsung mengikat port tersebut. Jika dijalankan lokal tanpa `$PORT`, otomatis fallback ke default `8000` atau `8501`.
  2. *Process Replacement (`exec`)*: Perintah `exec` menggantikan proses shell (`sh`) dengan proses utama (`uvicorn`/`streamlit`) sebagai PID 1 di dalam kontainer, menjamin penanganan sinyal `SIGTERM`/`SIGINT` untuk *graceful shutdown* saat rolling update di Railway.

---

### 6. Manifest Dependency Masing-Masing Service

Dependency dipisahkan secara tegas untuk efisiensi ukuran image dan keamanan runtime:

#### A. Backend (`inference/requirements.txt`)
- `torch==2.14.1+cpu` & `torchvision==0.29.1+cpu` (dipasang dari indeks resmi wheel CPU: `https://download.pytorch.org/whl/cpu` untuk menghemat ~2.3 GB memori disk dibandingkan CUDA).
- `ultralytics==8.4.174` (arsitektur YOLO26m).
- `fastapi==0.143.0` & `uvicorn==0.54.0` (ASGI server).
- `python-multipart==0.0.32` (multipart form parser untuk upload citra).
- `pydantic==2.14.0` (validasi skema respons API).
- `pillow==12.3.0` (verifikasi citra in-memory).
- `opencv-python==5.0.0.93` (rendering anotasi bounding box).

#### B. Frontend (`dashboard/requirements.txt`)
- `streamlit>=1.35.0` (interactive UI).
- `requests>=2.31.0` (HTTP client komunikasi ke FastAPI).
- `pillow>=10.0.0` (decode dan manipulasi citra in-memory).
- *Bebas dari*: PyTorch, Torchvision, Ultralytics, dan OpenCV (tidak ada beban AI/tensor di frontend).

---

### 7. Dokumentasi Environment Variables (`.env.example`)

| Variabel | Service | Status | Default Lokal | Nilai Produksi Railway | Fungsi |
|---|---|---|---|---|---|
| `PORT` | Kedua service | Otomatis | `8000` / `8501` | *Disuntikkan Railway* | Port listener HTTP kontainer. |
| `INFERENCE_API_URL` | Streamlit | **Wajib** | `http://127.0.0.1:8000` | `http://${{gio-inference.RAILWAY_PRIVATE_DOMAIN}}:${{gio-inference.PORT}}` | Endpoint FastAPI yang dipanggil dashboard. |
| `MODEL_PATH` | FastAPI | Opsional | `./artifacts/yolo26m_candidate.pt` | `/app/artifacts/yolo26m_candidate.pt` | Lokasi checkpoint model di dalam container backend. |
| `MAX_UPLOAD_MB` | FastAPI | Opsional | `10` | `10` | Batas maksimum upload citra (MB). |
| `ALLOWED_ORIGINS` | FastAPI | Opsional | `*` | Domain Streamlit & Vercel | Whitelist CORS origin. |

---

### 8. Panduan Setup Dua Service Railway (Monorepo)

Berikut panduan konfigurasi pada dashboard Railway (tanpa deploy manual saat ini):

#### Service 1: `gio-inference` (Backend)
1. Buat Proyek baru di Railway: `New Project` -> `Deploy from GitHub repo`.
2. Pilih repository: `Projek GIO`.
3. Buka tab **Settings**:
   - **Service Name**: `gio-inference`.
   - **Root Directory**: `.` (Root repository).
   - **Builder**: `Dockerfile`.
   - **Dockerfile Path**: `inference/Dockerfile`.
   - **Healthcheck Path**: `/`.
   - **Healthcheck Timeout**: `300` detik (memberi waktu pemuatan model saat startup pertama).
4. Buka tab **Variables**:
   - `MODEL_PATH`: `/app/artifacts/yolo26m_candidate.pt`
   - `MAX_UPLOAD_MB`: `10`
5. Buka tab **Settings** -> **Networking**:
   - Aktifkan **Private Networking** (Railway otomatis menyediakan domain privat `*.railway.internal`).
   - (Opsional) Klik **Generate Domain** jika ingin menguji endpoint via publik: `https://gio-inference-production.up.railway.app`.

#### Service 2: `gio-dashboard` (Frontend)
1. Pada proyek Railway yang sama, klik **New Service** -> **GitHub Repo** (pilih repo yang sama).
2. Buka tab **Settings**:
   - **Service Name**: `gio-dashboard`.
   - **Root Directory**: `.` (Root repository).
   - **Builder**: `Dockerfile`.
   - **Dockerfile Path**: `dashboard/Dockerfile`.
   - **Healthcheck Path**: `/_stcore/health`.
   - **Healthcheck Timeout**: `120` detik.
3. Buka tab **Variables**:
   - Tambahkan variabel koneksi internal Railway:
     ```text
     INFERENCE_API_URL=http://${{gio-inference.RAILWAY_PRIVATE_DOMAIN}}:${{gio-inference.PORT}}
     ```
4. Buka tab **Settings** -> **Networking**:
   - Klik **Generate Domain** untuk mendapatkan URL publik dashboard (misal: `https://gio-dashboard-production.up.railway.app`).

---

### 9. Rencana Konfigurasi Vercel (Phase 4.4)

- **Status Saat Ini**: Berkas `poc/vercel-streamlit-proxy/vercel.json` **dipertahankan utuh dan tidak diubah** pada fase ini.
- **Rencana Implementasi Phase 4.4**:
  1. Domain resmi Vercel (`https://gio-motorcycle.vercel.app`) akan difungsikan sebagai **Showcase / Landing Gateway**.
  2. Halaman Vercel menyajikan rangkuman riset, arsitektur YOLO26m, dan tombol CTA utama: `"Buka Live Demo Deteksi"` yang mengarahkan pengunjung ke domain Railway Streamlit.
  3. Dengan memisahkan domain landing Vercel dari koneksi WebSocket aplikasi, Streamlit terbebas dari kendala *idle timeout 30–60 detik* dan batas upload *4.5 MB* milik Vercel Serverless.

---

### 10. Hasil Pengujian Regresi & Validasi Docker

#### A. Rangkaian Tes Otomatis (Pytest)
- **Frontend Test Suite** (`dashboard/tests`):
  - Perintah: `.\.venv\Scripts\python.exe -m pytest dashboard/tests -v`
  - Hasil: **35 PASSED (100%)**, 0 failed dalam 2.72 detik.
- **Backend Test Suite** (`inference/tests`):
  - Perintah: `.\.venv\Scripts\python.exe -m pytest inference/tests -v`
  - Hasil: **22 PASSED (100%)**, 0 failed dalam 3.47 detik.
- **Total Uji Otomatis**: **57 / 57 PASSED (100%)**.

#### B. Validasi Docker Lokal
- **Status**: `NOT VERIFIED (Lokal)`
- **Alasan**: Docker CLI / Docker Desktop tidak terpasang pada lingkungan Windows lokal developer (`The term 'docker' is not recognized`).
- **Verifikasi Statis Dockerfile**:
  - `inference/Dockerfile`: Sintaks multi-stage valid, dependensi sistem `libgl1` dan `libglib2.0-0` terpasang, perintah `pip install` menggunakan CPU index wheel, dan CMD shell exec tervalidasi.
  - `dashboard/Dockerfile`: Sintaks valid, utilitas `curl` terpasang untuk healthcheck, dependensi terisolasi, dan CMD shell exec tervalidasi.

---

### 11. Kesimpulan Kesiapan untuk Phase 4.3

| Komponen | Status | Catatan |
|---|---|---|
| Repositori & `.gitignore` | `PASS` | Folder `.venv` dan file dump pengujian terlindungi; model kandidat dipertahankan. |
| Backend Dockerfile | `PASS` | Mendukung port dinamis `$PORT`, build context root, dan healthcheck `/`. |
| Frontend Dockerfile | `PASS` | Kontainer Streamlit mandiri terisolasi, `ENV PYTHONPATH=/app`, `dashboard/__init__.py`, mendukung `$PORT` dan `INFERENCE_API_URL`. |
| Dokumentasi Environment | `PASS` | `.env.example` terdokumentasi lengkap dan bebas dari secret. |
| Panduan Setup Railway | `PASS` | Alur monorepo 2-service dan private networking terdokumentasi. |
| Pengujian Unit/Regresi | `PASS` | 57/57 tests lulus tanpa regresi. |
| Docker Build Lokal | `NOT VERIFIED` | Tidak tersedia daemon Docker lokal; validasi sintaks tuntas. |

Seluruh kebutuhan persiapan konfigurasi Phase 4.2 telah rampung. Repositori siap melanjutkan ke tahap deployment backend pada Phase 4.3 setelah disetujui.
