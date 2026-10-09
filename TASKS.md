# TASKS.md — Rencana dan Pelacakan Pekerjaan Projek GIO

> Status terakhir diperbarui: Phase 0 (Sedang Berjalan)
> Dokumen acuan: `prd.md`, `design.md`, `techstack.md`, `agent.md`

---

## Ringkasan Keputusan Proyek yang Disetujui
1. **Model Resmi**: YOLO26m (bukan YOLO26n). Checkpoint sumber: `yolo26m_best.pt/best/`.
2. **Pemetaan Kelas Riil**: ID `0` = `motor`, ID `1` = `orang`. Semantik sistem: motorcycle dan person.
3. **Logika Asosiasi IoA**:
   - Threshold $\text{IoA} \ge 0.60$, di mana $\text{IoA}(P, M) = \frac{\text{Area}(P \cap M)}{\text{Area}(P)}$.
   - Jika 1 orang memenuhi threshold untuk $>1$ motor: diasosiasikan **hanya** ke motor dengan IoA tertinggi (*highest IoA*).
   - Satu orang tidak boleh dihitung pada lebih dari satu motor.
   - Tie-breaker: deterministik berdasarkan indeks deteksi motor terkecil.
4. **Logika Keputusan Status per Motor**:
   - $0\text{--}2$ orang terasosiasi = `AMAN`
   - $\ge 3$ orang terasosiasi = `PELANGGARAN`
5. **Requirement Akses Vercel**: Dashboard harus dapat diakses melalui domain Vercel. Pengujian kelayakan teknis proxy/routing Streamlit wajib dievaluasi melalui PoC sebelum implementasi final.

---

## Phase 0 — Environment Setup, Model Validation, dan Vercel Proxy PoC

- [x] **Task 0.1: Penyiapan Environment Python Terisolasi**
  - *Tujuan*: Membuat virtual environment `.venv` dengan Python 3.11.9 dan memasang dependensi minimal yang diperlukan.
  - *Status*: SELESAI
  - *Bukti Pengujian*: `.venv` aktif berbasis Python 3.11.9; paket terpasang via pip freeze: `torch==2.14.1+cpu`, `torchvision==0.29.1+cpu`, `ultralytics==8.4.174`, `fastapi==0.143.0`, `uvicorn==0.54.0`, `streamlit==1.65.0`, `pytest==9.1.1`.
- [x] **Task 0.2: Pembuatan Kandidat Checkpoint YOLO26m**
  - *Tujuan*: Mengemas ulang direktori ekstraksi `yolo26m_best.pt/best/` ke `artifacts/yolo26m_candidate.pt` tanpa mengubah file sumber atau bobot.
  - *Status*: SELESAI
  - *Bukti Pengujian*: File `artifacts/yolo26m_candidate.pt` (43.997.307 bytes / 41.96 MB) terbentuk; validasi SHA256 lulus byte-for-byte untuk seluruh 778 file anggota; sumber asli `yolo26m_best.pt/best/` tidak disentuh.
- [x] **Task 0.3: Validasi Model Checkpoint & Metadata**
  - *Tujuan*: Memuat kandidat via Ultralytics, memverifikasi arsitektur, ukuran, dan pemetaan kelas `0: motor` & `1: orang`.
  - *Status*: SELESAI
  - *Bukti Pengujian*: Pemuatan via `ultralytics.YOLO("artifacts/yolo26m_candidate.pt")` sukses; task = `detect`; kelas terverifikasi = `{0: 'motor', 1: 'orang'}`; arsitektur = `DetectionModel` (YOLO26m/v11 dengan modul `C3k2` & `C2PSA`).
- [x] **Task 0.4: Uji Inferensi Smoke Test**
  - *Tujuan*: Menjalankan inferensi pada citra uji aman untuk memvalidasi struktur output deteksi.
  - *Status*: SELESAI
  - *Bukti Pengujian*: Eksekusi `scripts/test_inference_smoke.py` pada citra sintetis RGB 640x640 selesai dalam 360 ms CPU; output boxes, tensor shape, dan metadata valid tanpa error unhandled exception.
- [x] **Task 0.5: Proof of Concept (PoC) Vercel-Streamlit Proxy**
  - *Tujuan*: Menguji kelayakan proxy/routing Streamlit melalui domain Vercel dengan aplikasi minimal terisolasi di `poc/vercel-streamlit-proxy/`.
  - *Status*: SELESAI (Pengujian Lokal Lolos; Analisis Keterbatasan Vercel Terdokumentasi)
  - *Bukti Pengujian*: Folder `poc/vercel-streamlit-proxy/` (`app.py`, `vercel.json`, `.streamlit/config.toml`, `README.md`) selesai; uji lokal via `streamlit.testing.v1.AppTest` lulus 100% (counter state & in-memory image); keterbatasan Vercel WebSocket rewrites didokumentasikan.
- [x] **Task 0.6: Sinkronisasi Dokumentasi Proyek**
  - *Tujuan*: Memperbarui `prd.md`, `design.md`, `techstack.md`, `agent.md` dengan fakta terverifikasi dan keputusan terbaru.
  - *Status*: SELESAI
  - *Bukti Pengujian*: Keempat dokumen MD telah diselaraskan dengan path model kandidat, kelas riil `motor`/`orang`, aturan highest IoA, dan temuan Vercel PoC.

---

## Phase 1 — Backend Inference Service (FastAPI) [SELESAI]
- [x] **Task 1.1: Skema respons Pydantic dan kontrak API**
  - *Tujuan*: Membangun skema data terstruktur untuk health check, prediksi deteksi, motor, orang, ringkasan, dan error handling.
  - *Status*: SELESAI
  - *Bukti Pengujian*: Modul `inference/schemas/response.py` dan `schemas/__init__.py` teruji valid pada seluruh respons API; serialisasi Pydantic v2 kompatibel penuh.
- [x] **Task 1.2: Modul validasi file citra dan penanganan privasi**
  - *Tujuan*: Memvalidasi ekstensi (JPG/PNG), MIME type, batas ukuran $\le 10\text{ MB}$, validasi in-memory via Pillow `.verify()`, dan menjamin nol persistensi file ke disk.
  - *Status*: SELESAI
  - *Bukti Pengujian*: Pengujian streaming file size, ekstensi ilegal (`test.gif`), MIME ilegal, citra rusak (`CORRUPTED_IMAGE`), dan file kosong (`EMPTY_FILE`) lulus di `inference/tests/test_api.py`.
- [x] **Task 1.3: Wrapper detector YOLO26m**
  - *Tujuan*: Singleton wrapper Ultralytics YOLO26m dengan pemetaan eksplisit kelas `0: motor` dan `1: orang`, aman terhadap hasil deteksi kosong.
  - *Status*: SELESAI
  - *Bukti Pengujian*: Diuji di `test_predict_real_candidate_smoke` menggunakan checkpoint `artifacts/yolo26m_candidate.pt`; pemuatan satu kali saat startup, inferensi CPU berhasil dan bebas exception saat objek kosong.
- [x] **Task 1.4: Modul asosiasi IoA dengan aturan highest IoA & tie-breaking**
  - *Tujuan*: Menghitung $\text{IoA}(P, M) = \text{Area}(P \cap M) / \text{Area}(P)$ dengan ambang batas $0.60$, asosiasi eksklusif ke motor dengan IoA tertinggi, dan tie-breaker indeks motor terkecil.
  - *Status*: SELESAI
  - *Bukti Pengujian*: 8 unit test di `inference/tests/test_association.py` lulus 100% (kondisi overlap nol, IoA $<0.60$, IoA $=0.60$, IoA $>0.60$, highest IoA winner, tie-breaker deterministik, orang unassociated, nol motor).
- [x] **Task 1.5: Modul aturan keputusan per-motor (AMAN vs PELANGGARAN)**
  - *Tujuan*: Menentukan status setiap motor: 0–2 orang = AMAN, $\ge 3$ orang = PELANGGARAN; menghitung agregat ringkasan.
  - *Status*: SELESAI
  - *Bukti Pengujian*: 2 unit test suite di `inference/tests/test_rules.py` lulus untuk seluruh batas (0, 1, 2, 3, 4+ orang) serta multi-motorcycle.
- [x] **Task 1.6: Modul anotasi citra visual in-memory**
  - *Tujuan*: Menggambar bounding box motor (Hijau=AMAN, Merah=PELANGGARAN), orang, label status, dan mengembalikan Base64 JPEG Data URI tanpa menulis ke disk.
  - *Status*: SELESAI
  - *Bukti Pengujian*: Output data URI `data:image/jpeg;base64,...` diverifikasi valid pada `test_predict_success` dan `test_predict_real_candidate_smoke`.
- [x] **Task 1.7: Endpoint FastAPI (`GET /` dan `POST /predict`)**
  - *Tujuan*: Endpoint health/readiness check (200/503) dan endpoint inferensi multipart form dengan kode status 400, 413, 422, 500, 503.
  - *Status*: SELESAI
  - *Bukti Pengujian*: Seluruh skenario endpoint teruji via FastAPI TestClient di `test_api.py`.
- [x] **Task 1.8: Rangkaian pengujian otomatis backend**
  - *Tujuan*: Menjalankan unit test dan integration test menyeluruh di `.venv`.
  - *Status*: SELESAI
  - *Bukti Pengujian*: Pytest menjalankan 22 tes (`inference/tests/`) dan seluruhnya **PASSED (22 passed, 0 failed)** dalam 10.33 detik.

---

## Phase 2 — Frontend Dashboard (Streamlit) [SELESAI]
- [x] **Task 2.1: App shell, tema Dark UI, navigasi sidebar 5 halaman**
  - *Tujuan*: Mengonfigurasi tema gelap resmi (`#0B0D10`, `#12161B`, `#7C5CFC`), CSS token, struktur multipage 5 halaman, dan sidebar branding.
  - *Status*: SELESAI
  - *Bukti Pengujian*: File `.streamlit/config.toml`, `dashboard/components/ui.py`, dan `dashboard/app.py` terverifikasi; seluruh 5 halaman (`app.py`, `1_Detection.py`, `2_How_It_Works.py`, `3_Model_Information.py`, `4_About.py`) lulus dieksekusi via `streamlit.testing.v1.AppTest` di `dashboard/tests/test_pages.py`.
- [x] **Task 2.2: Halaman Deteksi (upload, preview, analisis, visualisasi side-by-side, unduh)**
  - *Tujuan*: Menerima 1 file citra ($\le 10$ MB), pratinjau aspek rasio asli, tombol analisis tanpa pengiriman berulang, visualisasi hasil per-motor & IoA, serta tombol unduh citra biner JPEG tanpa persistensi disk.
  - *Status*: SELESAI
  - *Bukti Pengujian*: Halaman `dashboard/pages/1_Detection.py` teruji; fungsi `validate_uploaded_file` dan `decode_base64_data_uri` lulus 8 unit test di `dashboard/tests/test_utils.py`.
- [x] **Task 2.3: Client API FastAPI dengan variabel lingkungan dan timeout handler**
  - *Tujuan*: Client HTTP terpusat `InferenceClient` membaca `INFERENCE_API_URL` (default `http://127.0.0.1:8000`), menangani timeout (5s health, 45s predict), memetakan status error (400, 413, 422, 500, 503), dan bebas log biner citra.
  - *Status*: SELESAI
  - *Bukti Pengujian*: 9 unit test di `dashboard/tests/test_inference_client.py` lulus 100% (kondisi respons 200, 422, 503, invalid JSON, timeout, connection error, empty bytes).
- [x] **Task 2.4: Halaman informasi (How It Works, Model Information, About)**
  - *Tujuan*: Halaman edukasi transparan menjelaskan 6 tahapan pipeline, rumus IoA $\ge 0.60$, spesifikasi arsitektur YOLO26m, metadata kelas riil (`0: motor`, `1: orang`), batasan prototipe, atribusi paper mAP@50 89.59%, dan penafian (bukan ETLE resmi).
  - *Status*: SELESAI
  - *Bukti Pengujian*: Halaman `2_How_It_Works.py`, `3_Model_Information.py`, dan `4_About.py` lulus uji render Streamlit AppTest tanpa unhandled exception.

---

## Phase 3 — Integrasi End-to-End & Security QA [SELESAI]
- [x] **Task 3.1: Integrasi frontend-backend lokal dan verifikasi error states**
  - *Tujuan*: Menjalankan FastAPI dan Streamlit sebagai proses independen terpisah, menguji HTTP nyata (`GET /` dan `POST /predict`), validasi inferensi model aktual, serta verifikasi error states (400, 413, 422, 503).
  - *Status*: SELESAI
  - *Bukti Pengujian*: Pengujian live `scripts/test_live_integration.py` dan suite `dashboard/tests/test_e2e_integration.py` lulus 100% pada port 8000 dan 8501; inferensi model riil mengembalikan data terstruktur dan citra anotasi Base64.
- [x] **Task 3.2: Audit privasi dan penanganan file (Zero-Persistence Verification)**
  - *Tujuan*: Memverifikasi alur upload dan pengolahan citra bebas dari penulisan disk permanen, database, atau logging biner mentah; memastikan spool buffer dibersihkan via `await file.close()`.
  - *Status*: SELESAI
  - *Bukti Pengujian*: Audit kode pada `inference/app.py` mengonfirmasi penggunaan `io.BytesIO`, pembacaan streaming chunk, `await file.close()` dalam blok `finally`, dan dekode Base64 murni di RAM tanpa penulisan filesystem.
- [x] **Task 3.3: Uji responsivitas mobile dan aksesibilitas keyboard (WCAG AA)**
  - *Tujuan*: Memverifikasi layout responsif (desktop vs mobile viewport 375px), rasio kontras teks (WCAG AA), dan keterbacaan status badge tanpa mengandalkan warna semata.
  - *Status*: SELESAI
  - *Bukti Pengujian*: Audit CSS dan token di `dashboard/components/ui.py` mengonfirmasi kontras teks $\ge 7:1$ (melebihi standar WCAG AA 4.5:1), media queries breakpoint 768px, layout stack otomatis Streamlit, dan status selalu dilengkapi teks eksplisit (`✓ AMAN` dan `⚠ PELANGGARAN`).

## Phase 3.5 — Frontend Redesign & Visual Quality [SELESAI]
- [x] **Task 3.5.1: Audit visual dan identifikasi akar masalah rendering**
  - *Tujuan*: Mengidentifikasi penyebab HTML literal tampil sebagai blok kode pada kelima halaman.
  - *Status*: SELESAI
  - *Bukti Pengujian*: Ditemukan bahwa multi-line string yang diindentasi 4+ spasi di dalam blok `with` atau fungsi diperlakukan oleh parser CommonMark sebagai indented code block (`<pre><code>`).
- [x] **Task 3.5.2: Perbaikan HTML literal**
  - *Tujuan*: Menghilangkan kebocoran tag markup HTML mentah dari kelima halaman.
  - *Status*: SELESAI
  - *Bukti Pengujian*: Seluruh helper dan halaman direfaktor menggunakan elemen native Streamlit dan `textwrap.dedent()`; diverifikasi lulus 5/5 pengujian pada `dashboard/tests/test_visual_rendering.py`.
- [x] **Task 3.5.3: Perbaikan navigasi dan komponen bersama**
  - *Tujuan*: Mengganti label navigasi `app` menjadi `Dashboard` di sidebar dan memperbarui `ui.py`.
  - *Status*: SELESAI
  - *Bukti Pengujian*: `st.navigation` diimplementasikan di `dashboard/app.py` dengan label eksplisit `Dashboard`, `Detection`, `How It Works`, `Model Information`, `About`.
- [x] **Task 3.5.4: Redesign Dashboard**
  - *Tujuan*: Meningkatkan hierarki visual landing page, status koneksi live, kartu alur kerja, dan parameter teknis.
  - *Status*: SELESAI
  - *Bukti Pengujian*: Halaman `dashboard/app.py` menggunakan `st.container(border=True)` dan tombol CTA `st.switch_page`; lulus pengujian `test_pages.py`.
- [x] **Task 3.5.5: Redesign Detection**
  - *Tujuan*: Menjadikan area canvas deteksi sebagai hero visual utama, side-by-side comparison, tombol download jelas, dan kartu motor rapi.
  - *Status*: SELESAI
  - *Bukti Pengujian*: Halaman `dashboard/pages/1_Detection.py` teruji dengan download JPEG valid dan expander IoA; lulus tes live E2E.
- [x] **Task 3.5.6: Redesign How It Works, Model Information, dan About**
  - *Tujuan*: Memperbaiki 3 halaman informasi dengan layout native container, tabel markdown bersih, atribusi paper mAP@50 89.59%, dan disclaimer legal.
  - *Status*: SELESAI
  - *Bukti Pengujian*: Ketiga halaman direfaktor dan diverifikasi bebas error serta bebas HTML literal code block.
- [x] **Task 3.5.7: Visual review desktop dan mobile**
  - *Tujuan*: Memeriksa alignment, kontras rasio (WCAG AA), dan layout responsif pada desktop dan layar sempit.
  - *Status*: SELESAI (AppTest & Programmatic Simulation Lolos; Browser Driver Headless Terkendala Eksternal)
  - *Bukti Pengujian*: CSS media queries 768px terpasang, kontras teks $\ge 7:1$, layout stack otomatis Streamlit berfungsi, dan ketiadaan horizontal overflow terverifikasi.
- [x] **Task 3.5.8: Regression testing frontend dan backend**
  - *Tujuan*: Memastikan seluruh pengujian backend dan frontend tetap lulus tanpa regresi fungsional.
  - *Status*: SELESAI
  - *Bukti Pengujian*: Backend (`inference/tests`): 22/22 PASSED; Frontend (`dashboard/tests`): 32/32 PASSED; Total 54/54 PASSED (100%).
- [x] **Task 3.5.9: Sinkronisasi dokumentasi dan laporan**
  - *Tujuan*: Mencatat seluruh perbaikan teknis dan temuan visual pada `TASKS.md` dan laporan penutupan.
  - *Status*: SELESAI
  - *Bukti Pengujian*: `TASKS.md` dan laporan Phase 3.5 disinkronkan.

---

## Final UI Refinement — Sidebar, Responsive Spacing, dan Penghapusan Data Teknis Lapangan [SELESAI]
- [x] **Tugas A: Penghapusan Data Teknis Lapangan (Raw JSON) pada Halaman Detection**
  - *Tujuan*: Menghapus panel expander raw JSON pada `dashboard/pages/1_Detection.py` tanpa mengubah backend FastAPI atau merusak ringkasan, gambar, tombol download, dan per-motorcycle breakdown.
  - *Status*: SELESAI
  - *Bukti Pengujian*: Blok expander `🛠 Data Teknis Lengkap Respons API (Raw JSON)` dan `st.json` dihapus total; seluruh metrik, gambar input/anotasi, tombol unduh JPEG, dan perincian motor tetap utuh; diverifikasi lulus di `test_detection_page_no_raw_json_or_technical_expander` (`test_ui_refinement.py`).
- [x] **Tugas B: Restrukturisasi 3 Area Sidebar**
  - *Tujuan*: Menata ulang sidebar menjadi 3 area teratur: Area 1 (Branding GIO Motorcycle AI di paling atas), Area 2 (Menu Navigasi di bawah branding), Area 3 (Deskripsi `YOLO26m Passenger Violation Detector` di paling bawah).
  - *Status*: SELESAI
  - *Bukti Pengujian*: Komponen `render_sidebar_top_brand()` dan `render_sidebar_bottom_desc()` dibuat di `dashboard/components/ui.py`; flex ordering CSS (`order: 1` untuk brand, `order: 2` untuk nav, `order: 10` dengan `margin-top: auto` untuk deskripsi) diverifikasi di `test_sidebar_structure_tokens`.
- [x] **Tugas C: Penghapusan Panah Dropdown Menu Navigasi & Preservasi Kontrol Sidebar**
  - *Tujuan*: Menghilangkan panah dropdown collapse pada header "Menu Navigasi", mencegah menu tertutup tidak sengaja, sambil mempertahankan tombol penutup/pembuka seluruh sidebar.
  - *Status*: SELESAI
  - *Bukti Pengujian*: Target CSS `[data-testid="stNavSectionHeader"] svg { display: none !important; }` dan `pointer-events: none !important` menyembunyikan ikon chevron dan mematikan klik collapse menu; tombol collapse sidebar utama `[data-testid="stSidebarCollapseButton"]` di `[data-testid="stSidebarHeader"]` tetap aktif tanpa terpengaruh.
- [x] **Tugas D: Pengurangan Jarak Vertikal Atas Konten Utama pada Semua Halaman**
  - *Tujuan*: Mengurangi ruang kosong berlebih di atas konten utama secara konsisten pada kelima halaman (Dashboard, Detection, How It Works, Model Information, About).
  - *Status*: SELESAI
  - *Bukti Pengujian*: Aturan `.main .block-container { padding-top: 1.75rem !important; }` dan `h1:first-of-type { margin-top: 0 !important; }` diinjeksi via `inject_custom_css()` dan aktif di entrypoint `app.py` serta seluruh halaman; breakpoint mobile 768px (`padding-top: 1.25rem !important`) terpasang.
- [x] **Pengujian Regresi Menyeluruh (Regression Testing)**
  - *Tujuan*: Memastikan tidak ada regresi fungsional di backend maupun frontend.
  - *Status*: SELESAI
  - *Bukti Pengujian*: Frontend (`dashboard/tests`): 35/35 PASSED (100%); Backend (`inference/tests`): 22/22 PASSED (100%); Total 57/57 tests lulus.

## Final UI Correction — Sidebar, Content Spacing, Penghapusan Emoji, dan Konsistensi Tampilan [SELESAI]
- [x] **Tugas A: Pembenahan Struktur Sidebar Terpadu (Akar Masalah DOM)**
  - *Tujuan*: Mengatasi akar masalah DOM yang menyebabkan branding hilang/berada di bawah dengan memigrasikan `st.navigation` ke `position="hidden"` dan merender seluruh elemen sidebar secara murni di dalam `st.sidebar` menggunakan `render_app_sidebar()`.
  - *Status*: SELESAI
  - *Bukti Pengujian*: Urutan elemen diuji secara deterministik di `dashboard/tests/test_ui_refinement.py` (`test_dashboard_emojis_and_sidebar_order`). Urutan: Branding [GIO] Motorcycle AI di posisi 1 -> Divider -> Header statis 'Menu Navigasi' (tanpa panah) -> 5 link navigasi `st.page_link` -> Divider -> Deskripsi `YOLO26m Passenger Violation Detector` di dasar sidebar via `margin-top: auto`.
- [x] **Tugas B: Penghapusan Emoji pada 4 Elemen UI Kunci**
  - *Tujuan*: Membersihkan emoji pada status backend, tombol buka deteksi, tombol analisis, dan tombol unduh sesuai instruksi.
  - *Status*: SELESAI
  - *Bukti Pengujian*: Keempat label dibersihkan dari emoji:
    1. Status backend: `Backend Siap: Service FastAPI aktif dan model YOLO26m termuat dalam memori.` (tanpa centang hijau).
    2. Tombol pembuka deteksi: `Buka Halaman Deteksi` (tanpa emoji roket).
    3. Tombol analisis pelanggaran: `Analisis Pelanggaran` (tanpa emoji kaca pembesar).
    4. Tombol unduh anotasi: `Unduh Gambar Anotasi (JPEG)` (tanpa emoji unduh).
    Diverifikasi lulus 100% pada `test_detection_page_no_raw_json_and_clean_buttons` dan `test_dashboard_emojis_and_sidebar_order`.
- [x] **Tugas C: Perapian Alignment Layout Dashboard dan Detection**
  - *Tujuan*: Menyelaraskan status bar backend dan tombol CTA pada Dashboard secara vertikal, serta merapikan kolom aksi dan pratinjau Detection. Mengeliminasi deprecation warning Streamlit dengan mengganti `use_container_width=True` ke `width="stretch"`.
  - *Status*: SELESAI
  - *Bukti Pengujian*: Ditambahkan CSS `.stAlert { margin-bottom: 0 !important; }`, `vertical_alignment="center"` pada kolom CTA, serta parameter `width="stretch"` terpasang di seluruh tombol dan citra.
- [x] **Tugas D: Spacing Vertikal Konten Utama Lima Halaman**
  - *Tujuan*: Mempertahankan padding atas konten utama sebesar `1.75rem` (desktop) dan `1.25rem` (mobile) tanpa margin negatif atau positioning absolut.
  - *Status*: SELESAI
  - *Bukti Pengujian*: CSS diinjeksi via `inject_custom_css()` dan aktif di entrypoint `app.py` serta seluruh halaman; diverifikasi di `test_custom_css_rules`.
- [x] **Tugas E: Verifikasi Eliminasi Total Data Teknis Lapangan (Raw JSON)**
  - *Tujuan*: Memastikan respons mentah backend/expander raw JSON tetap tidak muncul di halaman Detection.
  - *Status*: SELESAI
  - *Bukti Pengujian*: `at.json` berjumlah 0 dan tidak ada expander data teknis diuji di `test_detection_page_no_raw_json_and_clean_buttons`.
- [x] **Pengujian Regresi Menyeluruh (Full Regression)**
  - *Tujuan*: Memastikan stabilitas penuh backend dan frontend.
  - *Status*: SELESAI
  - *Bukti Pengujian*: Frontend (`dashboard/tests`): 35/35 PASSED (100%); Backend (`inference/tests`): 22/22 PASSED (100%); Total 57/57 tests lulus.

## Final Layout Fix — Sidebar Header Sejajar Tombol Collapse, Navigation, Footer, dan Dashboard Heading [SELESAI]
- [x] **Tugas A: Header Branding Sejajar Horizontal dengan Tombol Collapse Sidebar**
  - *Tujuan*: Memposisikan branding `[GIO] Motorcycle AI` (badge ungu di kiri) dan tombol collapse `[<<]` (di kanan) dalam satu baris horizontal paling atas dengan vertical center yang selaras, ruang aman anti-tabrakan, dan eliminasi dead space atas.
  - *Status*: SELESAI
  - *Bukti Pengujian*:
    - Analisis DOM Streamlit membuktikan `[data-testid="stSidebarContent"]` menaungi `[data-testid="stSidebarHeader"]` dan `[data-testid="stSidebarUserContent"]`.
    - Diterapkan CSS: `[data-testid="stSidebarHeader"] { position: absolute !important; top: 0.6rem !important; right: 0.75rem !important; height: 2.25rem !important; z-index: 20 !important; }`.
    - `.gio-sidebar-brand { display: flex !important; align-items: center !important; height: 2.25rem !important; padding: 0 2.5rem 0 0 !important; margin: 0 !important; }`.
    - Branding dan tombol `<<` berada pada ketinggian identik (`top: 0.6rem`, tinggi `2.25rem`), vertical alignment tepat di tengah, dan padding kanan `2.5rem` menjamin nol tumpang tindih. Tombol collapse tetap berfungsi penuh dan dapat diklik.
- [x] **Tugas B: Penaikan Menu Navigasi agar Dekat dengan Branding**
  - *Tujuan*: Menaikkan judul "Menu Navigasi" dan 5 item menu mendekati branding tanpa spacer tetap yang kaku, tanpa panah dropdown, dan mempertahankan visual active link.
  - *Status*: SELESAI
  - *Bukti Pengujian*: Divider antar-elemen dirapatkan (`margin: 0.45rem 0;`), margin `.gio-nav-title` diperpendek (`margin-top: 0.1rem; margin-bottom: 0.25rem;`), dan padding link navigasi dioptimalkan (`0.35rem 0.65rem;`). Menu tersusun rapat di bawah branding dengan keterbacaan yang tetap prima.
- [x] **Tugas C: Perbaikan Akar Masalah Footer Menempel di Bagian Bawah**
  - *Tujuan*: Mengatasi akar masalah footer `YOLO26m Passenger Violation Detector` yang sebelumnya mengambang di bawah menu About dengan ruang kosong besar di bawahnya, dan memastikannya menempel di dasar sidebar menggunakan rantai flexbox terpadu.
  - *Status*: SELESAI
  - *Akar Masalah yang Ditemukan*:
    1. Inspeksi DOM riil via CDP membuktikan Streamlit menyematkan inline style `height: auto` pada `section[data-testid="stSidebar"]`, sehingga kontainer turunan hanya memiliki tinggi setinggi kontennya (~428px) alih-alih 100vh.
    2. Kontainer antara `stSidebarUserContent > div` dan `stVerticalBlock` (`km`) memiliki default `height: auto` dan tidak meregang (`flex: 1`).
    3. Blok teks `.gio-sidebar-desc` tidak langsung menjadi anak dari flex container, melainkan dibungkus di dalam `[data-testid="stElementContainer"]`. Akibatnya, `margin-top: auto` pada teks footer tidak berefek karena elemen pembungkusnya tetap berada tepat di bawah menu About.
  - *Solusi Implementasi*:
    1. Memaksa `section[data-testid="stSidebar"]` dan `[data-testid="stSidebarContent"]` memiliki `height: 100vh !important; min-height: 100vh !important; display: flex !important; flex-direction: column !important;`.
    2. Memberikan `[data-testid="stSidebarUserContent"]` `height: calc(100vh - 1.2rem) !important; min-height: calc(100vh - 1.2rem) !important; flex: 1 1 auto !important;`.
    3. Memberikan `[data-testid="stSidebarUserContent"] > div` dan `[data-testid="stVerticalBlock"]` `display: flex !important; flex-direction: column !important; flex: 1 1 auto !important; height: 100% !important;`.
    4. Menargetkan pembungkus footer: `[data-testid="stSidebarUserContent"] [data-testid="stElementContainer"]:has(.gio-sidebar-desc)`, `[data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:last-child`, dan `[data-testid="stVerticalBlock"] > div:last-child` dengan `margin-top: auto !important; width: 100% !important;`.
    5. Menghidupkan visibilitas permanen tombol collapse `[data-testid="stSidebarCollapseButton"]` dengan `visibility: visible !important; opacity: 1 !important;` agar selalu terlihat berdampingan dengan header branding.
  - *Bukti Pengujian & Validasi Browser*:
    - Pemeriksaan CDP mengonfirmasi dasar footer (`descBottom`) berada di Y: 620px (dasar viewport), bukan 370px seperti sebelumnya.
    - Tangkapan layar browser Chrome riil (resolusi desktop 1366 × 768 px) pada `real_browser_screenshot.png` (91.713 bytes) membuktikan:
      - Header branding dan tombol `<<` sejajar sempurna di baris paling atas.
      - Menu navigasi berada tepat di bawah header.
      - Ruang fleksibel di tengah terbuka bersih.
      - Footer garis horizontal dan teks `YOLO26m Passenger Violation Detector` menempel di dasar paling bawah sidebar.
      - Bebas dari ruang kosong raksasa di bawah footer.
- [x] **Tugas D: Penyesuaian Spacing Judul Dashboard agar Bebas Terpotong Toolbar**
  - *Tujuan*: Mengidentifikasi akar masalah pemotongan bagian atas judul "Sistem Deteksi Pelanggaran Penumpang Sepeda Motor" dan menyesuaikan spacing agar judul tampil utuh tanpa terpotong toolbar Streamlit.
  - *Status*: SELESAI
  - *Bukti Pengujian*: Ditemukan bahwa toolbar bawaan Streamlit memiliki tinggi ~46px (~2.875rem) dengan posisi sticky. Dengan padding konten sebelumnya `1.75rem` (28px), bagian atas huruf terpotong ~18px. Diperbaiki dengan menetapkan `.block-container { padding-top: 2.75rem !important; }` dan `h1:first-of-type { padding-top: 0.35rem !important; line-height: 1.25 !important; }`. Judul kini tampil 100% utuh dengan jarak aman di bawah toolbar.
- [x] **Tugas E: Preservasi Seluruh Perbaikan Sebelumnya & Keutuhan Sistem**
  - *Tujuan*: Mempertahankan eliminasi total panel raw JSON "Data Teknis Lapangan", 4 label tombol/status tanpa emoji, model YOLO26m, aturan IoA $\ge 0.60$, aturan keputusan AMAN (0-2) / PELANGGARAN ($\ge 3$), dan kontrak API FastAPI.
  - *Status*: SELESAI
  - *Bukti Pengujian*: Seluruh pengujian regresi lulus 100%; tidak ada perubahan pada algoritma inferensi, bobot model, atau struktur respons FastAPI.
- [x] **Tugas F & G: Responsivitas & Pengujian Regresi Lengkap**
  - *Tujuan*: Memastikan tampilan proporsional pada desktop (1366x768), tablet (768-1024), dan mobile (375-430) serta memvalidasi seluruh test suite.
  - *Status*: SELESAI
  - *Bukti Pengujian*:
    - Frontend (`dashboard/tests`): 35/35 PASSED (100%).
    - Backend (`inference/tests`): 22/22 PASSED (100%).
    - Total: 57/57 PASSED.

---

## Phase 4 — Deployment & Aksesibilitas Publik

- [x] **Phase 4.1: Deployment Readiness Audit (Railway + Vercel + YOLO26m)**
  - *Tujuan*: Mengaudit kesiapan deployment, dependencies, konfigurasi Dockerfile, kompatibilitas runtime Vercel vs Streamlit, resource footprint, keamanan Git, dan menyusun laporan audit formal.
  - *Status*: SELESAI (Status: `READY WITH BLOCKERS`)
  - *Lokasi Laporan*: `reports/phase_4_1_deployment_readiness.md`
  - *Ringkasan Bukti*:
    - Tes lokal: 57/57 tests PASSED (35 frontend, 22 backend).
    - Resource empiris: RAM idle model ~313 MB, peak inference ~560 MB (alokasi kontainer Railway minimal 1 GB RAM).
    - 4 Blocker Utama: Dockerfile CMD hardcoded port 8000, batasan Vercel WebSocket & payload 4.5 MB, ketiadaan `.gitignore` di root, serta ketiadaan Dockerfile frontend.
    - Rekomendasi Arsitektur: Dual-service Railway (FastAPI + Streamlit) dengan Vercel sebagai Showcase Portal / Landing Gateway ber-URL publik.
- [x] **Phase 4.2: Deployment Preparation & Configuration (Railway + Streamlit + Vercel Portal)**
  - *Tujuan*: Mengatasi seluruh blocker Phase 4.1: membuat `.gitignore` komprehensif, mengonfigurasi port dinamis `$PORT` pada `inference/Dockerfile`, membuat `dashboard/Dockerfile` mandiri, menyusun `.env.example`, panduan konfigurasi dual-service Railway monorepo, serta regresi test suite.
  - *Status*: SELESAI (Status: `PASS`)
  - *Lokasi Laporan*: `reports/phase_4_2_deployment_preparation.md`
  - *Ringkasan Bukti*:
    - `.gitignore` dibuat: Melindungi virtual environment (~4.5 GB), cache, file dump sementara, dan backup extraction `yolo26m_best.pt/`, dengan preservasi ketat terhadap `artifacts/yolo26m_candidate.pt`.
    - `inference/Dockerfile` diperbarui: Shell exec pattern `CMD ["sh", "-c", "exec uvicorn inference.app:app --host 0.0.0.0 --port ${PORT:-8000}"]` untuk ekspansi port dinamis Railway dan graceful shutdown handling.
    - `dashboard/Dockerfile` dibuat: Image mandiri berbasis `python:3.11-slim` tanpa dependensi PyTorch/Ultralytics, port dinamis `${PORT:-8501}`, binding `0.0.0.0`, headless.
    - `.env.example` dibuat: Dokumentasi variabel `PORT`, `INFERENCE_API_URL`, `MODEL_PATH`, `MAX_UPLOAD_MB`, `ALLOWED_ORIGINS` untuk lokal dan private networking Railway.
    - Panduan konfigurasi Railway dual-service (monorepo root context) dan rencana Showcase Portal Vercel didokumentasikan.
    - Pengujian otomatis: 57/57 PASSED (35 frontend, 22 backend). Docker CLI lokal: `NOT VERIFIED (Lokal)`.
  - *Production Hotfix (ModuleNotFoundError: No module named 'dashboard')*:
    - *Akar Masalah*: Streamlit menempatkan direktori script (`/app/dashboard`) di `sys.path[0]`, bukan root `/app`. Tanpa `ENV PYTHONPATH=/app` dan berkas `dashboard/__init__.py`, import `from dashboard.components.ui` dkk gagal ditemukan oleh Python interpreter di dalam kontainer Railway.
    - *Perbaikan*:
      1. Menambahkan `PYTHONPATH=/app` pada instruksi `ENV` di `dashboard/Dockerfile`.
      2. Membuat berkas `dashboard/__init__.py` untuk mendeklarasikan package formal.
      3. Menambahkan injeksi defensif `sys.path` berbasis path absolut repo di bagian paling atas `dashboard/app.py`.
    - *Hasil Uji*: 57/57 PASSED (35 frontend, 22 backend).
- [ ] **Phase 4.3: Deployment Implementation (Railway Backend & Frontend)**
  - Deployment service backend FastAPI (`gio-inference`) ke Railway dan verifikasi health check `/`.
  - Deployment service frontend Streamlit (`gio-dashboard`) ke Railway dan penyambungan `INFERENCE_API_URL` melalui private networking.
  - Pengujian koneksi antarlayanan dan live inference di Railway.
- [ ] **Phase 4.4: Vercel Showcase Portal & End-to-End Production Verification**
  - Konfigurasi Vercel sebagai showcase portal / presentation gateway dengan tautan langsung ke dashboard Railway.
  - Validasi end-to-end responsivitas, alur upload 10 MB, WebSocket, dan performa produksi publik.

