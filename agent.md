# AI Coding Agent Rules — Projek GIO / YOLO26m

> Simpan file ini di root `Projek GIO/`. Aturan ini ditujukan untuk AI coding agent/Antigravity.
> Jangan memulai implementasi sebelum membaca dokumen proyek dan skill yang relevan.

## 1. Mandatory Reading Order

Sebelum membuat atau mengubah kode, baca berurutan:

1. `prd.md` — kebutuhan produk dan batasan scope.
2. `design.md` — desain dan perilaku UI.
3. `techstack.md` — arsitektur, model, API, testing, dan deployment.
4. `agent.md` — aturan eksekusi ini.
5. Instruksi skill relevan di `.agents/skills/`.
6. File dan konfigurasi proyek aktual yang terkait dengan task.

Dokumentasi diletakkan langsung di root `Projek GIO/`, berdampingan dengan `.agents/` dan artifact model.
Jangan menganggap contoh struktur pada dokumen sebagai izin untuk menimpa file yang sudah ada; inspect dulu.

## 2. Source of Truth and Scope Control

- `prd.md` menentukan **WHAT**.
- `design.md` menentukan aturan visual dan UX.
- `techstack.md` menentukan arsitektur dan technical contract.
- `agent.md` menentukan workflow agent.
- Paper, laporan, source code lama, dan metadata checkpoint menjadi sumber untuk detail penelitian/model.
- Instruksi eksplisit terbaru dari user dapat mengubah requirement. Perbarui dokumen terkait jika perubahan
  tersebut telah disetujui.

**Jangan improvisasi scope.** Jika fitur tidak ada di PRD, jangan menambahkannya karena dianggap kebiasaan umum.
Jangan membuat login, database, riwayat, penyimpanan permanen, video, webcam, atau fitur tambahan tanpa persetujuan.
Jika dua sumber bertentangan dan berdampak ke hasil penelitian, model, privasi, atau arsitektur, hentikan bagian
tersebut dan minta klarifikasi; jangan diam-diam memilih satu versi.

## 3. Known Project Structure

Dari struktur yang ditunjukkan user, tersedia:

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
│       ├── debugging-and-error-recovery/  # screenshot memotong akhir nama; verifikasi nama folder aktual
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
├── yolo26m_best.pt  # nama artifact dari tampilan; verifikasi bentuk/path filesystem
├── prd.md
├── design.md
├── techstack.md
├── agent.md
└── TASKS.md
```

Ini adalah pembacaan dari screenshot, bukan hasil inspeksi filesystem aktual. Pada tampilan VS Code, model
terlihat sebagai `yolo26m_best.pt\best` beserta entri internal seperti `data.pkl`, `byteorder`, dan `version`.
Jangan berasumsi bahwa `best` adalah subfolder filesystem yang dapat diberikan kepada runtime. Pastikan lokasi
file checkpoint yang sebenarnya sebelum menggunakannya.

## 4. Mandatory Skills in `.agents/skills/`

### 4.1 Cara membaca skill

Untuk task yang akan dikerjakan:

1. Buka direktori skill yang relevan di `.agents/skills/`.
2. Temukan dan baca file instruksi utama skill (misalnya `SKILL.md` atau file yang memang digunakan oleh skill itu).
3. Ikuti instruksi skill, termasuk dependency, workflow, batasan, dan kriteria verifikasi.
4. Jika skill tidak relevan atau tidak cocok dengan Streamlit/Python stack, jangan memaksakannya; jelaskan alasan
   singkat bila berpengaruh pada keputusan implementasi.
5. Jangan mengarang fungsi skill dari nama folder saja. Khusus `hallmark` dan skill yang namanya terpotong di UI,
   periksa isi dan nama aktual sebelum menyimpulkan tujuannya.

Tidak perlu membaca setiap skill untuk setiap perubahan kecil. Baca skill yang cocok dengan task yang sedang
berjalan dan skill review/security yang relevan terhadap dampak perubahan.

### 4.2 Skill yang tersedia dan pemakaian awal

| Skill folder | Gunakan ketika |
|---|---|
| `incremental-implementation` | Memecah kerja menjadi perubahan kecil dan teruji. |
| `api-and-interface-design` | Mendesain kontrak FastAPI dan komunikasi dashboard–API. |
| `code-review-and-quality` | Review kualitas, struktur, type hints, dan maintainability. |
| `debugging-and-error-recovery` | Melacak exception, kegagalan startup, API, atau deployment; verifikasi nama folder lengkap. |
| `documentation-and-adrs` | Memperbarui README, dokumentasi, keputusan arsitektur, dan alasan perubahan. |
| `performance-optimization` | Mengukur/memperbaiki waktu inference, konsumsi memori, dan request flow. |
| `security-and-hardening` | Upload file, validasi, CORS, secrets, dan deployment security. |
| `antislop` | Menilai solusi agar tidak generik/berlebihan dan tetap bernilai guna. |
| `antislop-ui` | Meninjau kualitas tampilan dan menghindari UI generik. |
| `antislop-layoutmobile` | Meninjau layout responsif/mobile. |
| `design-taste-frontend` | Menyempurnakan hierarchy, spacing, tipografi, dan visual polish. |
| `frontend-ui-engineering` | Pekerjaan UI; adaptasikan pada Streamlit dan jangan otomatis membawa stack web lain. |
| `emil-design-eng` | Baca instruksi skill lalu gunakan hanya pada pekerjaan yang relevan. |
| `animate` | Motion/interaksi bila benar-benar dibutuhkan dan dapat diimplementasikan di stack. |
| `review-animations` | Review motion/accessibility jika animasi digunakan. |
| `shadcn` | Hanya bila instruksi dan teknologi yang didukung benar-benar cocok; jangan menambah React/shadcn ke Streamlit tanpa persetujuan. |
| `hallmark` | Periksa instruksi di dalam folder sebelum menentukan kapan/pada apa skill digunakan. |

Daftar ini memetakan penggunaan awal dari nama folder yang terlihat. Isi file instruksi masing-masing skill tetap
menjadi otoritas; pemetaan ini tidak menggantikan pembacaan skill.

## 5. Required Workflow for Every Task

1. **Identify phase and task.** Nyatakan tujuan teknis yang ingin diselesaikan.
2. **Read context.** Baca bagian PRD/design/techstack dan skill yang relevan.
3. **Inspect before edit.** Periksa file, dependency, git diff/status bila tersedia, dan pola yang sudah dipakai.
4. **Plan briefly.** Sebutkan file yang akan dibuat/diubah, alasan, serta requirement yang dipenuhi.
5. **Implement incrementally.** Hindari rewrite besar yang tidak diperlukan.
6. **Test.** Jalankan test/check yang sesuai; jangan hanya mengandalkan keberhasilan membuat file.
7. **Review changes.** Periksa regressions, secrets, scope creep, dan konsistensi dokumentasi.
8. **Update `TASKS.md`.** Centang task hanya setelah implementasi dan validasi berhasil.
9. **Report honestly.** Laporkan apa yang diubah, test yang benar-benar dijalankan, yang belum diuji, dan blocker.

Jangan melanjutkan fase berikutnya jika ada test kritis gagal atau keputusan penting belum terverifikasi.

## 6. Model Integrity — Highest Priority

Nama artifact yang terlihat adalah `yolo26m_best.pt`. Sebelum coding inference:

1. Inspeksi filesystem dan tentukan apakah path itu file checkpoint yang nyata.
2. Verifikasi file dapat dibaca oleh runtime yang cocok.
3. Load checkpoint melalui cara yang didukung runtime model.
4. Periksa nama kelas dan class ID aktual dari metadata.
5. Jalankan inference smoke test pada gambar contoh yang sah.
6. Catat hasil dan konfigurasi runtime yang digunakan.

Jangan:

- mengganti checkpoint dengan pretrained model lain;
- mengganti nama/path berdasarkan tebakan;
- menganggap entry internal `best/` dalam tampilan arsip sebagai file model terpisah;
- mengubah class mapping agar kode berjalan tanpa konfirmasi;
- retrain/fine-tune tanpa instruksi eksplisit;
- mengklaim mAP@50 `0.8959` berasal dari file listing. Metrik tersebut harus dirujuk ke paper/laporan proyek.

Jika artifact tidak ada, rusak, ter- extract dengan cara yang tidak jelas, atau gagal dimuat, hentikan bagian inference dan
laporkan temuan. Jangan menyamarkan kegagalan model dengan model dummy/pretrained lain.

## 7. Fixed AI Pipeline

Pipeline target:

```text
Image upload
  → image validation/decoding
  → YOLO26m checkpoint
  → detections for verified classes
  → person–motorcycle IoA association
  → count person per motorcycle
  → status rule per motorcycle
  → annotation
  → structured FastAPI response
  → dashboard rendering/download
```

IoA definition:

`IoA(P, M) = Area(P ∩ M) / Area(P)`

Threshold: `IoA >= 0.60` qualifies as association.

Status rule:

- 0–2 associated persons per motorcycle → `AMAN`.
- 3 or more associated persons per motorcycle → `PELANGGARAN`.

Jangan menerapkan status berdasarkan total person dalam seluruh gambar. Untuk person yang overlap dengan beberapa
motor, periksa aturan sumber penelitian. Jika tidak ditemukan, minta persetujuan untuk aturan deterministik sebelum
menguncinya sebagai perilaku final.

## 8. Image-Only and Privacy Rules

**Image only.** Jangan mengimplementasikan MP4, video decoding, frame extraction, CCTV/RTSP, webcam, live stream,
tracking, atau temporal inference.

Jangan membuat login, registration, database, Supabase, user table, history, bucket, atau penyimpanan permanen.
Gambar harus diproses in-memory bila memungkinkan; annotated image dikembalikan kepada dashboard untuk ditampilkan
dan diunduh tanpa menyimpan image permanen.

## 9. Architecture Rules

- Streamlit bertanggung jawab atas UI, upload, render hasil, dan download.
- FastAPI bertanggung jawab atas validation, inference orchestration, association, rule, annotation, dan JSON response.
- Railway adalah target hosting service FastAPI/model.
- Vercel adalah requirement deployment/access yang harus diverifikasi secara aktual.
- Dashboard tidak boleh memuat weights atau menjalankan inference lokal.
- FastAPI tidak boleh bergantung pada kode UI Streamlit.
- API URL dan konfigurasi deployment harus memakai environment variables.
- Tidak ada platform/dependency baru tanpa alasan dan pemeriksaan skill terkait.

### Vercel/Streamlit conflict

Jika mekanisme deployment yang diminta tidak didukung, verifikasi dulu, lalu dokumentasikan konflik dan usulkan perubahan minimum.
Minta persetujuan sebelum mengganti platform atau mengubah arsitektur. Jangan melaporkan production-ready tanpa bukti.

## 10. API and Error Rules

Minimal endpoint:

- `GET /` untuk health/readiness;
- `POST /predict` untuk satu gambar.

API wajib memvalidasi format, ukuran, dan konten gambar; mengembalikan data terstruktur; menyertakan hasil per motorcycle,
detection detail yang diperlukan, processing time bila tersedia, dan annotated result; serta menangani error dengan status
HTTP yang sesuai.

Jangan membocorkan stack trace, secret, path internal, atau data pengguna melalui response publik. Error UI harus jelas dan
dapat ditindaklanjuti, bukan hanya `500 Internal Server Error`.

## 11. UI Rules

Ikuti `design.md` dan skill UI yang relevan. Wajib:

- dark-first, sidebar dan halaman yang konsisten;
- CTA utama mudah ditemukan;
- annotated image mendapat ruang memadai;
- ringkasan dan status per motorcycle mudah dibaca;
- confidence dan IoA tersedia tanpa membuat halaman terlalu padat;
- loading, empty, success, dan error states nyata;
- responsive behavior serta contrast/labels yang layak;
- setiap tombol memiliki aksi yang benar.

Dilarang: metrics palsu, fake historical chart, fake AI scan, fake progress percentage, tombol dekoratif yang tidak bekerja,
ornamen berlebihan, atau fitur di luar scope.

## 12. Code Quality and Resource Rules

- Gunakan fungsi kecil, single responsibility, dan type hints Python.
- Definisikan response schema dengan Pydantic bila cocok dengan implementasi.
- Isolasi detector, association, rule, annotation, API, dan dashboard client.
- Load model sekali saat startup bila praktis; jangan reload setiap request.
- Jangan menggunakan global mutable request state.
- Tangani exception secara eksplisit; jangan `except` lalu mengabaikannya.
- Hindari menyimpan bytes gambar secara permanen.
- Pin/record dependency penting setelah kompatibilitas checkpoint diuji.
- Ukur performance sebelum mengklaim optimisasi atau angka kinerja.

## 13. Minimum Test Requirements

### Checkpoint/model

- path/artifact terverifikasi;
- model dapat dimuat;
- classes/IDs tercatat;
- smoke inference selesai atau blocker dilaporkan.

### Logic/API

- valid JPG/JPEG/PNG;
- tipe/corrupt image ditolak;
- file terlalu besar ditolak;
- IoA di bawah `0.60` ditolak;
- IoA tepat `0.60` diterima;
- 2 associated persons → `AMAN`;
- 3 associated persons → `PELANGGARAN`;
- beberapa motorcycle dinilai independen;
- kasus association ambigu mengikuti aturan yang sudah disetujui;
- health, prediction schema, error handling, dan annotated result teruji.

### Dashboard/deployment

- upload, preview, analyze, loading, success, error, download;
- dashboard dapat menghubungi API deployment;
- health/predict di Railway dapat diverifikasi;
- mekanisme akses Vercel terdokumentasi dan dites atau status blocker/alternatif disetujui.

## 14. `TASKS.md` and Phases

Buat/perbarui `TASKS.md` langsung di root `Projek GIO/`. Checklist awal:

### Phase 0 — Environment Setup, Model Validation, dan Vercel Proxy PoC

- [x] Inspect root project and current git/status if available.
- [x] Read this four-doc set.
- [x] Read relevant `.agents/skills/` instructions.
- [x] Verify actual filesystem path and file type for `yolo26m_best.pt/best/`.
- [x] Create candidate `artifacts/yolo26m_candidate.pt`, verify load, class names/IDs (`0: motor`, `1: orang`).
- [x] Confirm approved research rule for ambiguous association (highest IoA + deterministic tie-break).
- [x] Build and test Vercel proxy PoC in `poc/vercel-streamlit-proxy/`.

### Phase 1 — Inference Service

- [ ] Implement FastAPI health/readiness endpoint.
- [ ] Implement image validation and size limit.
- [ ] Implement YOLO26m detector wrapper.
- [ ] Implement IoA association and per-motor decision logic.
- [ ] Implement annotated output and response schema.
- [ ] Add unit/API tests.

### Phase 2 — Streamlit Dashboard

- [ ] Create app shell/sidebar/pages consistent with `design.md`.
- [ ] Add one-image uploader, preview, and analyze CTA.
- [ ] Add API client using environment configuration.
- [ ] Add summary/per-motor result and annotated-image rendering.
- [ ] Add result download and UX states.

### Phase 3 — Integration and QA

- [ ] Test dashboard-to-API integration.
- [ ] Test errors/timeouts and retry behavior.
- [ ] Check no images persist after processing.
- [ ] Run visual/responsive QA using applicable skills.

### Phase 4 — Deployment

- [ ] Deploy FastAPI/model to Railway.
- [ ] Configure environment variables and CORS as appropriate.
- [ ] Verify real Vercel/Streamlit access mechanism; document blockers and obtain approval for any requirement change.
- [ ] Run production smoke tests.

A task may be marked `[x]` only after the required check passes. Do not mark a task complete merely because code was written.

## 15. Decision Framework and Definition of Done

When unsure:

1. read the relevant project doc;
2. inspect actual code, artifact, and skill instructions;
3. prefer the smallest change that meets the requirement;
4. test the change;
5. update `TASKS.md` and related documentation;
6. ask the user if the uncertainty affects model correctness, research validity, privacy, security, or architecture.

Definition of done:

- [ ] Project checkpoint `yolo26m_best.pt` is verified and used; no silent substitution.
- [ ] Classes come from verified metadata.
- [ ] IoA logic and per-motor decision rule pass tests.
- [ ] Streamlit UI and FastAPI API work together.
- [ ] Annotated image and key result details are shown and downloadable.
- [ ] No login/database/Supabase/history/permanent image storage.
- [ ] Railway deployment works.
- [ ] Vercel access requirement is verified or a user-approved alternative is documented.
- [ ] UI follows `design.md` and relevant skills were applied.
- [ ] Tests and final smoke test pass; untested items/blockers are clearly reported.
- [ ] `TASKS.md` and project documentation are current.
