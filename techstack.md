# Technical Stack and Architecture — YOLO26m Motorcycle Violation Detection

> Simpan file ini di root `Projek GIO/`. Dokumen ini menjelaskan **bagaimana** sistem dibangun.
> Requirement produk berada di `prd.md`, aturan UI di `design.md`, dan aturan kerja agent di `agent.md`.

## 1. Architecture Overview

### 1.1 Target stack

- **Dashboard:** Streamlit.
- **API/inference service:** FastAPI + Python.
- **Model runtime:** runtime Ultralytics/PyTorch yang terbukti kompatibel dengan checkpoint proyek.
- **Model artifact:** `yolo26m_best.pt` (nama yang terlihat pada struktur proyek; verifikasi file sebenarnya sebelum dipakai).
- **Inference hosting:** Railway.
- **Deployment/access requirement:** Vercel; mekanisme integrasi dengan Streamlit harus diverifikasi, bukan diasumsikan.
- **Image handling:** Pillow dan/atau OpenCV bila dibutuhkan.
- **API client:** HTTP client Python yang sesuai dengan versi/dependency yang digunakan.
- **Testing:** pytest; lint/format dapat menggunakan Ruff/Black jika ditetapkan secara konsisten.
- **Packaging:** Docker untuk service inference jika diperlukan deployment yang repeatable.

Jangan menambahkan database, Supabase, Redis, queue, object storage, authentication, atau layanan lain
untuk kebutuhan yang tidak tercantum dalam PRD.

### 1.2 Data flow

```text
Browser
  ↓ membuka dashboard yang telah di-deploy
Vercel / mekanisme akses yang sudah diverifikasi
  ↓
Streamlit dashboard
  ↓ multipart image request
FastAPI inference service di Railway
  ↓
YOLO26m checkpoint terverifikasi
  ↓ person/motorcycle detections
IoA association (threshold 0.60)
  ↓
Counting person per motorcycle
  ↓
Rule status per motorcycle
  ↓
Annotation + structured result
  ↓ HTTP response
Streamlit menampilkan hasil + tombol download
```

### 1.3 Deployment caveat

Jangan mengasumsikan Vercel menjalankan proses Streamlit secara native. Sebelum deploy, periksa
mekanisme deployment yang aktual dan didukung. Railway tetap menjadi target untuk FastAPI/model.
Jika requirement Vercel dan Streamlit bertentangan pada implementasi yang tersedia, laporkan konflik,
berikan alternatif dengan perubahan minimum, dan minta persetujuan sebelum mengubah requirement.
Jangan memindahkan inference/model ke Vercel hanya demi membuat diagram tampak sederhana.

## 2. Model Artifact and Checkpoint Handling

### 2.1 Nama dan tampilan filesystem

Pada root proyek, artifact sumber ditemukan sebagai direktori `yolo26m_best.pt\best`, memuat file-file internal arsip PyTorch:
`.data`, `.format_version`, `.storage_alignment`, `byteorder`, `data.pkl`, `version`, dan folder `data/` (772 file tensor).
Ini merupakan direktori hasil ekstraksi arsip PyTorch.

**Status Verifikasi Model (Phase 0):**
1. Sumber asli `yolo26m_best.pt/best/` dipertahankan utuh dan tidak diubah.
2. Telah dibuat kandidat checkpoint: `artifacts/yolo26m_candidate.pt`.
3. Kandidat divalidasi identik byte-for-byte terhadap ke-778 file sumber (SHA256 matching).
4. Model sukses dimuat oleh runtime resmi `ultralytics.YOLO` dan `torch.load(..., weights_only=False)`.
5. Kelas terverifikasi: `{0: 'motor', 1: 'orang'}`.
6. Smoke test inferensi citra sintetis (640x640) berhasil dieksekusi (~360 ms CPU).

### 2.2 Path configuration

Gunakan konfigurasi yang eksplisit dan tidak bergantung pada current working directory.
Variabel resmi backend:

```dotenv
MODEL_PATH=./artifacts/yolo26m_candidate.pt
```

Nilai tersebut adalah default yang diusulkan, **bukan bukti bahwa path sudah valid**. Sesuaikan path
hanya setelah memeriksa filesystem aktual. Jangan hardcode path lokal mesin developer di source code.

### 2.3 Model integrity

- Gunakan checkpoint YOLO26m proyek; jangan menggantinya dengan model pretrained generik.
- Jangan retrain atau fine-tune tanpa instruksi eksplisit.
- Baca `model.names`/metadata dengan runtime yang kompatibel dan verifikasi kelas beserta ID.
- Jangan mengasumsikan `person` adalah class 0 atau `motorcycle` class 1.
- Gagal load model harus menghentikan inference secara eksplisit dan dilaporkan melalui health/error state.
- Model idealnya dimuat satu kali ketika service startup, bukan setiap request.
- Jangan menyalin weights ke bundle dashboard atau menjadikannya file publik yang dapat diunduh.

Metrik paper mAP@50 `0.8959` hanya merupakan klaim evaluasi penelitian yang perlu dirujuk ke paper/laporan,
bukan sesuatu yang bisa disimpulkan dari internal file listing.

## 3. Repository Layout

File dokumentasi ini akan berada langsung di **root `Projek GIO/`**, berdampingan dengan `.agents/`
dan artifact model.

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
│       ├── debugging-and-error-recovery/
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
├── yolo26m_best.pt                  # pastikan file/path nyata; bukan asumsi dari tampilan archive
├── dashboard/
│   ├── app.py
│   ├── pages/
│   │   ├── 1_Detection.py
│   │   ├── 2_How_It_Works.py
│   │   ├── 3_Model_Information.py
│   │   └── 4_About.py
│   ├── components/
│   ├── services/
│   │   └── inference_client.py
│   ├── utils/
│   ├── assets/
│   └── requirements.txt
├── inference/
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── services/
│   │   ├── detector.py
│   │   ├── association.py
│   │   └── annotation.py
│   ├── schemas/
│   │   └── response.py
│   └── tests/
│       ├── test_model_loading.py
│       ├── test_association.py
│       ├── test_rules.py
│       └── test_api.py
├── .env.example
├── README.md
├── prd.md
├── design.md
├── techstack.md
├── agent.md
└── TASKS.md
```

This is the **target layout**, not a direction to overwrite existing project files blindly. The agent must inspect
what is present and make incremental changes; adapt file names only when justified by the actual repository.
Do not move the model artifact unless needed and approved.

## 4. Environment Variables

Recommended variables:

```dotenv
MODEL_PATH=./yolo26m_best.pt
INFERENCE_API_URL=https://<railway-service>/predict
INFERENCE_HEALTH_URL=https://<railway-service>/
MAX_UPLOAD_MB=10
```

- `MODEL_PATH` is used by the inference service and must point to the verified artifact.
- `INFERENCE_API_URL` and `INFERENCE_HEALTH_URL` are used by the dashboard; do not hardcode a production URL.
- `MAX_UPLOAD_MB` is an initial suggestion, not a platform guarantee. Keep dashboard and API validation consistent.
- Use the hosting provider’s environment configuration for production values.
- `.env.example` contains placeholders only; do not commit secrets.

## 5. Inference Pipeline

Required logical stages:

1. Decode and validate image.
2. Run YOLO26m inference.
3. Separate detections by verified class names/IDs.
4. Compute person-to-motorcycle IoA association.
5. Count associated persons per motorcycle.
6. Apply status rule per motorcycle.
7. Draw annotations.
8. Return a structured result and annotated image.

### 5.1 IoA definition

`IoA(P, M) = Area(P ∩ M) / Area(P)`

where `P` is the person bounding box and `M` is the motorcycle bounding box. A pair qualifies when
`IoA >= 0.60`. Confirm box coordinate conventions and clipping behavior in implementation and tests.

### 5.2 Ambiguous association

Sebuah person dapat secara geometris bertumpukan dengan lebih dari satu motorcycle dengan nilai IoA >= 0.60.
**Aturan Resmi Proyek (Disetujui)**:
1. Jika seorang person memenuhi threshold IoA terhadap lebih dari satu motorcycle, asosiasikan orang tersebut **hanya** ke motorcycle dengan IoA tertinggi (*highest IoA*).
2. Satu person tidak boleh dihitung pada lebih dari satu motorcycle.
3. Jika terdapat nilai IoA yang sama persis (*tie*), gunakan aturan tie-break deterministik: asosiasikan ke motorcycle dengan indeks deteksi terkecil (indeks pertama pada daftar deteksi).

### 5.3 Status rule

```python
status = "PELANGGARAN" if person_count >= 3 else "AMAN"
```

Apply per motorcycle. People not associated to a motorcycle are not included in that motorcycle's count.

## 6. FastAPI Contract

### 6.1 Health endpoint

`GET /`

Minimal response concept:

```json
{
  "status": "ok",
  "model": "YOLO26m",
  "model_loaded": true
}
```

Health should not claim the model is loaded if startup loading failed. Consider a readiness response or
appropriate non-200 response for unavailable model state.

### 6.2 Prediction endpoint

`POST /predict` with `multipart/form-data` field `file` containing exactly one image.

Response concept (fields may vary, semantics must remain stable):

```json
{
  "success": true,
  "model": {
    "name": "YOLO26m",
    "checkpoint": "yolo26m_best.pt"
  },
  "image": {
    "width": 1920,
    "height": 1080
  },
  "summary": {
    "motorcycles": 3,
    "persons": 7,
    "violations": 1
  },
  "motorcycles": [
    {
      "id": 1,
      "person_count": 2,
      "status": "AMAN",
      "associated_persons": [
        {
          "person_id": 1,
          "confidence": 0.93,
          "ioa": 0.72
        }
      ]
    }
  ],
  "detections": [],
  "processing_time_ms": 420
}
```

Example numbers are illustrative schema examples only; they must not be presented as live performance/results.
Dashboard needs enough structured data to render all required summaries and per-motor details.

### 6.3 Annotated image transport

Choose one implementation after considering payload size and hosting limits:

- a binary/image response endpoint, or
- an encoded payload for small enough results.

Avoid unnecessarily large JSON payloads. No permanent storage is required: annotated output can remain in
request memory and be sent directly to the dashboard. If a separate endpoint is used, do not use a permanent
filesystem/object-storage URL unless requirements change.

### 6.4 Error format

Use a stable structured error shape, for example:

```json
{
  "success": false,
  "error": {
    "code": "INVALID_IMAGE",
    "message": "The uploaded file is not a supported JPG or PNG image."
  }
}
```

Recommended statuses:

- `400` — invalid request;
- `413` — upload too large;
- `422` — unsupported/corrupt image;
- `500` — inference failure;
- `503` — service/model unavailable.

Do not return stack traces, secrets, or internal paths to public users.

## 7. Dashboard ↔ API Contract

Dashboard responsibilities:

1. validate extension/type/size client-side for UX;
2. send multipart request to FastAPI;
3. apply request timeout and handle non-success responses;
4. render success/error states;
5. offer download of annotated image.

The API must independently validate inputs; frontend validation alone is insufficient. Dashboard must not
load the model weights or duplicate inference logic.

## 8. Performance and Resource Limits

- Initial maximum upload: 10 MB, adjustable only with a documented reason and synchronized validation.
- Target end-to-end response: 5–10 seconds ideal; 10–20 seconds acceptable for exhibition prototype.
- Model benchmark FPS from research must not be described as end-to-end request latency.
- Load model once on service startup when practical.
- Avoid writing source images or annotated images to permanent local storage.
- Use explicit request timeout and provide meaningful failure/retry guidance.
- Measure actual performance on deployment; do not invent the numbers.

## 9. Security and Privacy

- Never commit API secrets or production credentials.
- Validate both claimed file type and decoded image where practical.
- Enforce upload size at both dashboard and API.
- Do not log raw image contents.
- Do not persist user images or results.
- Restrict production CORS to actual allowed origin(s) if applicable.
- Do not publicly serve model weights.
- Follow the `security-and-hardening` skill when touching uploads, API boundaries, deployment config,
  headers, CORS, or secrets.

## 10. Testing

Minimum test coverage:

### Model and startup

- verified checkpoint path exists;
- checkpoint loads under pinned/known dependencies;
- model metadata/classes are inspected;
- service readiness reflects model load status.

### Image/API

- valid JPG/JPEG accepted;
- valid PNG accepted;
- corrupt or unsupported image rejected;
- oversized image rejected;
- health endpoint reflects service state;
- prediction schema and annotated image response work;
- model unavailable and timeout errors render helpfully.

### Logic

- IoA below `0.60` does not qualify;
- IoA exactly `0.60` qualifies;
- 2 associated persons → `AMAN`;
- 3 associated persons → `PELANGGARAN`;
- multiple motorcycles are assessed independently;
- ambiguous assignment follows the approved rule;
- unassociated people are not counted toward a motorcycle.

### UI/integration

- upload/preview/analyze;
- loading and disabled-submit behavior;
- success summary and per-motor details;
- annotated image download;
- API error and unavailable service states;
- deployed dashboard can call the Railway endpoint.

## 11. Deployment Responsibilities

### Railway

Host the FastAPI inference service, verified model artifact, and inference dependencies. Confirm `GET /`
and `POST /predict` against the deployed service. Set environment variables without exposing them in source.

### Vercel

Requirement akses proyek menetapkan akses dashboard melalui domain Vercel.
**Status Evaluasi Teknis PoC (`poc/vercel-streamlit-proxy/`)**:
- Aplikasi minimal Streamlit terbukti berjalan lokal dengan in-memory processing dan session state yang stabil.
- Analisis resmi arsitektur Vercel: Vercel Serverless / Rewrites tidak mendukung koneksi WebSocket persisten secara stabil untuk backend eksternal (idle timeout dan keterbatasan HTTP rewrite proxy).
- Rekomendasi arsitektur: Streamlit di-host pada platform persistent container (Railway / Streamlit Community Cloud), dan domain Vercel dikonfigurasikan sebagai landing page gateway / URL rewrite publik.

### Streamlit

Owns UI only, not model inference or weights. The actual hosting mechanism and its relationship to Vercel
must be documented once verified.

## 12. Technical Non-Goals

Unless the user explicitly changes the PRD, do not add:

- Supabase or another database;
- login/authentication/account management;
- analysis history;
- permanent image/object storage;
- video or live-camera processing;
- background job queues or extra infrastructure;
- training or fine-tuning pipeline.

## 13. Deployment Smoke Test

Before declaring deployment complete, verify:

- checkpoint is present at configured path and loads;
- Railway health endpoint is reachable;
- prediction endpoint returns expected fields and annotation;
- production dashboard can reach the API;
- size validation and CORS are appropriate;
- no uploaded image persists after request processing;
- Vercel requirement has a verified implementation or documented blocker and user-approved alternative;
- final URL is tested from a browser outside the developer environment.
