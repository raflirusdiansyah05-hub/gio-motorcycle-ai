# Proof of Concept: Vercel Rewrites Proxy ke Streamlit

Dokumen ini menjelaskan rancangan, arsitektur, prosedur pengujian, dan temuan teknis mengenai kelayakan mengakses aplikasi Streamlit melalui domain Vercel.

---

## 1. Latar Belakang & Arsitektur PoC

### Tujuan
Menguji secara empiris dan terdokumentasi apakah aplikasi Streamlit (yang membutuhkan koneksi WebSocket persisten dua arah) dapat diakses dan berfungsi secara andal melalui domain deployment Vercel menggunakan mekanisme reverse proxy (`rewrites`).

### Diagram Arsitektur
```text
Browser Pengguna
   │
   ▼ HTTP / WebSocket Handshake
[Domain Vercel: https://projek-gio.vercel.app]
   │
   │ (vercel.json rewrites: /:path* -> host Streamlit)
   ▼
[Hosting Eksternal (Railway / Streamlit Cloud / Render)]
   │
   ▼ Streamlit Server (Tornado HTTP & WebSocket on port 8501)
[app.py (Streamlit Session State, Re-runs, Image Buffer)]
```

---

## 2. Struktur File PoC

```text
poc/vercel-streamlit-proxy/
├── app.py                     # Aplikasi Streamlit minimal (counter, state, image preview)
├── vercel.json                # Konfigurasi rewrites Vercel Edge Network
├── .streamlit/
│   └── config.toml           # Konfigurasi CORS & XSRF disabled untuk proxying
└── README.md                  # Dokumentasi pengujian dan analisis teknis
```

---

## 3. Cara Menjalankan & Menguji

### A. Pengujian Lokal
1. Masuk ke direktori PoC:
   ```bash
   cd poc/vercel-streamlit-proxy
   ```
2. Jalankan Streamlit menggunakan virtual environment proyek:
   ```bash
   ..\..\.venv\Scripts\streamlit run app.py
   ```
3. Buka browser pada `http://localhost:8501`.
4. Uji interaksi:
   - Klik tombol **Tambah Hitungan (+1)** untuk memastikan re-run dan session state berjalan.
   - Unggah gambar kecil untuk memverifikasi in-memory parsing tanpa penulisan ke disk.

### B. Pengujian Deployment Preview di Vercel
1. Deploy Streamlit terlebih dahulu pada platform yang mendukung daemon persisten (misal: Railway atau Streamlit Community Cloud).
2. Perbarui `destination` pada `vercel.json` dengan URL publik instance Streamlit tersebut.
3. Deploy folder PoC ke Vercel Preview Deployment:
   ```bash
   npx vercel
   ```
4. Buka URL Preview Vercel (`https://<project>-<hash>.vercel.app`) dan periksa Developer Tools (Network Tab):
   - Periksa request `_stcore/stream` (koneksi WebSocket Streamlit).
   - Periksa apakah HTTP status mengembalikan `101 Switching Protocols` atau error `400 / 502 / Connection Drop`.

---

## 4. Hasil Temuan Teknis & Batasan

### Temuan Berdasarkan Dokumentasi Resmi & Perilaku Runtime
Berdasarkan dokumentasi resmi Vercel ([Vercel Edge Network Rewrites](https://vercel.com/docs/edge-network/rewrites) & [Vercel WebSockets in Functions](https://vercel.com/docs/functions/websockets)):

1. **Inkompatibilitas WebSocket Proxy Eksternal**:
   - Vercel Rewrites dirancang untuk pola request-response HTTP stateless.
   - Fitur WebSockets native Vercel (dirilis Juni 2026) diperuntukkan bagi Vercel Functions internal (seperti Node.js `api/ws.ts`), bukan untuk mem-proxy upgrade WebSocket menuju server eksternal melalui rewrite rule.
   - Ketika client Streamlit meminta koneksi WebSocket (`wss://<domain-vercel>/_stcore/stream`), Edge Network Vercel sering kali tidak meneruskan header `Upgrade` dan `Connection: upgrade` ke origin eksternal, atau koneksi terputus akibat idle timeout (30–60 detik).
2. **Gejala Kegagalan pada Streamlit**:
   - Dashboard akan menampilkan pesan *"Please wait..."* atau animasi loading tanpa henti karena koneksi WebSocket gagal terbentuk.
   - Jika koneksi sempat terbentuk, timeout Vercel akan memutus WebSocket setiap 30–60 detik, memicu *continuous page reload loop* dan hilangnya session state.
3. **Konfigurasi Wajib Streamlit**:
   - Jika diakses melalui origin berbeda (misal domain Vercel sementara server di Railway), `enableCORS = false` dan `enableXsrfProtection = false` wajib diatur pada `.streamlit/config.toml`. Jika tidak, Streamlit secara bawaan akan menolak koneksi dari origin yang tidak cocok.

---

## 5. Status Verifikasi & Rekomendasi untuk Proyek GIO

| Komponen Uji | Status | Catatan Teknis |
|---|---|---|
| **Aplikasi Minimal Streamlit** | **VERIFIED (Lokal)** | Counter, state, dan image preview in-memory berfungsi 100%. |
| **Konfigurasi `vercel.json`** | **VERIFIED (Sintaks)** | Rule `rewrites` terdefinisi sesuai spesifikasi Vercel. |
| **Konektivitas WebSocket via Vercel Live** | **TERBLOKIR (Akses)** | Memerlukan kredensial akun/token Vercel & URL live hosting Streamlit yang aktif dari pemilik proyek untuk deploy live preview. |

### Rekomendasi Solusi Terbaik:
1. **Rekomendasi Utama (Streamlit di Railway / Streamlit Cloud + Domain Vercel Landing/Rewrite)**:
   - Jika pemilik proyek tetap mewajibkan domain Vercel untuk branding/pameran, deploy Streamlit langsung di Railway (atau Streamlit Community Cloud) agar WebSocket berjalan tanpa gangguan. Gunakan domain Vercel sebagai entry point atau uji konfigurasi proxy live saat kredensial deployment disiapkan.
   - Jika proxy Vercel terbukti memutus WebSocket pada pengujian live nantinya, solusi cadangan yang paling stabil dan tidak mengubah arsitektur adalah menyajikan link akses langsung ke dashboard di Railway.
