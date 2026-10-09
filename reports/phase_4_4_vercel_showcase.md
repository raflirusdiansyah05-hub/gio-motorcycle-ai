# Laporan Hasil Phase 4.4 — GIO Vercel Showcase Portal

> **Dokumen**: `reports/phase_4_4_vercel_showcase.md`  
> **Tanggal**: 9 Oktober 2026  
> **Status**: **ARSIP HISTORIS / DIBATALKAN (Showcase Vercel Dibatalkan Sebelum Deployment; Arsitektur Final: Railway Only)**  
> **Target Arsitektur Final Proyek**: Single Public Entrypoint — Railway Streamlit Dashboard (`https://genuine-exploration-production-b1c3.up.railway.app`)

> [!IMPORTANT]
> **Adendum Keputusan Arsitektur Final (Phase 4.5 — Railway Only)**:  
> Menyusul keberhasilan verifikasi online penuh pada dashboard Streamlit Railway dan backend FastAPI YOLO26m, diputuskan bahwa portal showcase perantara Vercel **tidak lagi digunakan**. Pengguna langsung mengakses dashboard Streamlit Railway sebagai satu-satunya entrypoint publik. Berkas lokal `vercel-showcase/` telah dibersihkan pada Phase 4.5. Dokumen ini dipertahankan murni sebagai catatan teknis historis tanpa ada deployment Vercel yang dilakukan.

---

### 1. Ringkasan Pelaksanaan

Sesuai instruksi pada **Phase 4.4**, telah dibangun portal pameran statis mandiri di direktori `vercel-showcase/` untuk proyek **GIO Motorcycle AI**. Portal ini berfungsi sebagai pintu gerbang (*showcase / presentation landing gateway*) yang memperkenalkan latar belakang penelitian, metodologi computer vision YOLO26m, asosiasi spasial Intersection over Area (IoA), serta batasan akademis prototipe kepada pengunjung, dosen, dan penilai.

Seluruh tombol *Call-to-Action* (CTA) pada halaman showcase mengarahkan pengunjung secara langsung ke deployment produksi aktif Streamlit di Railway tanpa melalui perantara proxy atau serverless function.

---

### 2. Berkas yang Dibuat dan Diubah

| Berkas | Status | Deskripsi |
|---|---|---|
| `vercel-showcase/index.html` | **Baru** | Struktur HTML5 semantik: Header, Hero Section dengan mock preview card, 4 Kartu Fitur & Metodologi, Diagram Alur Pipeline 4 Tahap, Panel Batasan Riset, CTA Banner, dan Footer. Bebas ketergantungan JavaScript pihak ketiga. |
| `vercel-showcase/styles.css` | **Baru** | Lembar gaya CSS vanilla murni berpedoman pada `design.md` (tema gelap `#0B0D10`, aksen ungu `#7C5CFC`, font modern sans, komponen terstruktur, dan tata letak responsif dari 375px hingga 1366px+). |
| `vercel-showcase/assets/logo.svg` | **Baru** | Aset vektor logo badge `GIO` ungu beresolusi tajam dan ringan (< 400 bytes). |
| `TASKS.md` | **Diubah** | Pembaruan status Phase 4.3 dan Phase 4.4 menjadi selesai (`PASS`). |
| `reports/phase_4_4_vercel_showcase.md` | **Baru** | Laporan teknis resmi penyelesaian Phase 4.4. |

> **Catatan Integritas**: 
> - Berkas `poc/vercel-streamlit-proxy/` **dipertahankan utuh tanpa perubahan**.
> - Kode sumber backend (`inference/`) dan frontend (`dashboard/`) **tidak disentuh sama sekali**.
> - Tidak ada berkas biner model atau dependensi AI yang dipindahkan ke direktori showcase.

---

### 3. Konfirmasi Arsitektur: Halaman Statis vs Bukan Proxy

1. **Bukan Reverse Proxy / Rewrite**:
   Portal ini 100% merupakan situs web statis (*static HTML/CSS*). Tidak ada `vercel.json` dengan konfigurasi `rewrites` ke Streamlit, tidak ada edge middleware, dan tidak ada serverless function.
2. **Solusi Masalah WebSocket & Upload Buffer**:
   Dengan memisahkan domain landing Vercel dari aplikasi interaktif Streamlit, keterbatasan platform Vercel Serverless (seperti penutupan koneksi WebSocket setelah 30–60 detik dan batas buffer unggahan 4.5 MB) berhasil dihindari sepenuhnya.
3. **Penyaluran Beban Kerja**:
   - **Vercel**: Melayani aset statis `index.html`, `styles.css`, dan `logo.svg` dengan performa CDN global super cepat dan latensi minimal.
   - **Railway**: Menangani proses interaktif Streamlit (WebSocket, upload gambar hingga 10 MB, visualisasi anotasi) dan eksekusi model YOLO26m di backend.

---

### 4. Integrasi dengan Dashboard Railway

Semua CTA di halaman showcase terhubung langsung ke URL produksi Railway yang telah aktif:

```text
URL Target: https://genuine-exploration-production-b1c3.up.railway.app
```

Atribut tautan yang diterapkan:
- `target="_blank"`: Membuka dashboard Streamlit pada tab peramban baru sehingga halaman showcase tetap terbuka.
- `rel="noopener noreferrer"`: Mencegah celah keamanan *reverse tabnabbing* dan isolasi *window opener context*.

Daftar penempatan CTA:
1. **Header**: Tombol `"Buka Live Demo"` di navigasi kanan atas.
2. **Hero Section**: Tombol utama `"Buka Live Demo"` dengan ikon panah.
3. **CTA Banner**: Tombol utama `"Buka Live Demo"` di akhir halaman.
4. **Footer**: Tautan navigasi `"Dashboard Streamlit di Railway ↗"`.

---

### 5. Hasil Validasi Lokal dan Pemeriksaan Responsivitas

Pengujian statis dan visual dilakukan secara lokal menggunakan server HTTP internal dan peramban Google Chrome headless:

#### A. Verifikasi Status Aset HTTP
```text
GET /                 -> HTTP 200 (20,407 bytes)
GET /styles.css       -> HTTP 200 (17,588 bytes)
GET /assets/logo.svg  -> HTTP 200 (372 bytes)
```
Semua aset termuat tanpa 404, tanpa peringatan konsol, dan tanpa broken link.

#### B. Pengujian Dimensi Viewport & Horizontal Overflow
Pemeriksaan dilakukan dengan mengukur metrik `scrollWidth` terhadap `clientWidth` di seluruh breakpoint penting:

| Resolusi | Target Perangkat | `clientWidth` | `scrollWidth` | Status Overflow |
|---|---|---|---|---|
| **1366 x 768** | Desktop Monitor | 1333 px | 1333 px | **`hasOverflow = false` (PASS)** |
| **1024 x 768** | Desktop / Tablet Landscape | 991 px | 991 px | **`hasOverflow = false` (PASS)** |
| **768 x 1024** | Tablet Portrait (iPad) | 735 px | 735 px | **`hasOverflow = false` (PASS)** |
| **480 x 800** | Phablet / Mobile Lebar | 489 px | 489 px | **`hasOverflow = false` (PASS)** |
| **375 x 812** | Mobile Standar (iPhone SE/13) | 375 px | 375 px | **`hasOverflow = false` (PASS)** |

#### C. Bukti Visual Tangkapan Layar (Screenshots)
Tangkapan layar telah disimpan di direktori artefak untuk peninjauan visual:
- Desktop (1366 px): `showcase_desktop_1366.png`
- Tablet (768 px): `showcase_tablet_768.png`
- Mobile (375 px): `showcase_mobile_375.png`

---

### 6. Panduan Pengaturan Vercel (Manual Deployment Guide)

Ketika pengguna menghubungkan repositori `raflirusdiansyah05-hub/gio-motorcycle-ai` ke akun Vercel, lakukan konfigurasi berikut pada dashboard Vercel:

1. Buka dashboard Vercel -> Klik **Add New...** -> **Project**.
2. Pilih repositori GitHub: `raflirusdiansyah05-hub/gio-motorcycle-ai`.
3. Pada bagian **Project Configuration**:
   - **Project Name**: `gio-motorcycle-ai` (atau sesuai preferensi).
   - **Framework Preset**: Pilih **`Other`**.
   - **Root Directory**: Klik *Edit*, pilih folder **`vercel-showcase`**.
4. Pada bagian **Build and Output Settings**:
   - **Build Command**: *Kosongkan / Nonaktifkan* (karena merupakan situs HTML statis tanpa bundler).
   - **Output Directory**: *Kosongkan* (default `./`).
5. Pada bagian **Environment Variables**:
   - *Tidak memerlukan variabel lingkungan apa pun*.
6. Klik **Deploy**.
7. Dalam beberapa detik, situs web showcase akan aktif pada domain Vercel (misal: `https://gio-motorcycle-ai.vercel.app`).

---

### 7. Kendala yang Tersisa

- **Nihil**: Tidak ada kendala teknis atau blocker yang tersisa.
- Halaman statis telah memenuhi seluruh kriteria aksesibilitas, tema warna, hirarki konten, dan integrasi tautan langsung ke Railway.

---

### 8. Kesimpulan & Catatan Penutup (Phase 4.5 Update)

- Pekerjaan implementasi teknis halaman statis pada Phase 4.4 telah terselesaikan dan terverifikasi secara lokal.
- Namun, berdasarkan evaluasi kepraktisan alur pengguna pada Phase 4.5, **implementasi showcase Vercel dibatalkan sebelum proses deployment**. Pengguna langsung diarahkan ke satu-satunya domain publik aktif: `https://genuine-exploration-production-b1c3.up.railway.app`.
- Direktori `vercel-showcase/` telah dihapus secara bersih dari repositori pada Phase 4.5.
- Tidak ada deployment ke Vercel yang dilakukan, dan repositori kini beroperasi penuh dengan arsitektur **Railway Only**. Dokumen ini dipertahankan sebagai arsip historis perancangan.
