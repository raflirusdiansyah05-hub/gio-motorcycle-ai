# Design Specification — YOLO26m Motorcycle Violation Detection

> Simpan file ini di root `Projek GIO/`. Dokumen ini menetapkan aturan visual dan pengalaman
> pengguna. Implementasi harus mengikuti `prd.md` dan stack pada `techstack.md`.

## 1. Design Direction

Buat dashboard AI/computer-vision yang terasa modern, rapi, premium, teknis tetapi mudah dipahami,
dan layak ditampilkan pada pameran. Gunakan **dark-first UI** dengan kontras yang baik. Fokus utama
adalah bukti visual dan hasil per motorcycle, bukan ornamen.

Urutan perhatian pengguna:

1. Status utama dan ringkasan hasil.
2. Annotated image sebagai bukti visual.
3. Hasil tiap motorcycle.
4. Detail confidence/IoA.
5. Navigasi dan informasi sekunder.

## 2. Prinsip Desain

- **Clarity first:** instruksi dan CTA utama jelas.
- **Evidence first:** ruang cukup untuk gambar hasil agar bounding box mudah dilihat.
- **Status plus text:** warna status selalu ditemani label teks.
- **Technical detail on demand:** tampilkan ringkasan dengan jelas; detail IoA dapat berada di expander.
- **Consistent hierarchy:** gunakan ukuran/ketebalan teks dan jarak secara konsisten.
- **Responsive:** desktop menjadi prioritas demo, namun tampilan sempit tetap usable.
- **Honest interface:** jangan menampilkan angka demo sebagai hasil live, fake chart, fake history,
  fake AI scan, progress palsu, atau metrik yang tidak bersumber.
- **Minimal decoration:** hindari glassmorphism berlebihan, gradient berlebihan, partikel, dan efek yang
  mengalihkan perhatian dari hasil.

## 3. Design Tokens

Gunakan token secara konsisten; jangan memilih warna baru per komponen tanpa kebutuhan aksesibilitas.

| Token | Nilai | Pemakaian |
|---|---|---|
| `--bg` | `#0B0D10` | Latar aplikasi |
| `--surface` | `#12161B` | Panel/kartu utama |
| `--surface-2` | `#181D23` | Panel bertingkat |
| `--border` | `#272D35` | Garis pemisah/border |
| `--text-primary` | `#F5F7FA` | Teks utama |
| `--text-secondary` | `#9BA4B0` | Teks pendamping |
| `--accent` | `#7C5CFC` | CTA/fokus utama |
| `--accent-soft` | `#211C3D` | Latar aksen |
| `--success` | `#22C55E` | Status AMAN |
| `--success-soft` | `#102B1B` | Latar AMAN |
| `--danger` | `#EF4444` | Status PELANGGARAN/error |
| `--danger-soft` | `#35171A` | Latar pelanggaran |
| `--warning` | `#F59E0B` | Ketidakpastian/perhatian |
| `--info` | `#38BDF8` | Informasi/proses |

### 3.1 Label status

| Keadaan | Label | Tampilan |
|---|---|---|
| Hasil 0–2 person terasosiasi | `AMAN` | Hijau + teks |
| Hasil ≥3 person terasosiasi | `PELANGGARAN` | Merah + teks |
| Inference berlangsung | `MEMPROSES` | Aksen/info + teks |
| Hasil/association perlu ditinjau | `PERLU PERHATIAN` | Kuning + teks, hanya jika benar-benar diperlukan |
| Kegagalan | `GAGAL` | Merah + penjelasan |

Jangan gunakan `PERLU PERHATIAN` untuk menyamarkan error atau hasil yang belum tersedia.

## 4. Typography and Spacing

Gunakan sans-serif yang mudah dibaca; jika font eksternal tidak tersedia, gunakan fallback sistem.

| Elemen | Ukuran referensi |
|---|---:|
| Judul halaman | 28–32 px |
| Judul section | 20–24 px |
| Judul kartu | 16–18 px |
| Body | 14–16 px |
| Caption | 12–13 px |
| Metrik utama | 28–40 px |

Gunakan spacing yang konsisten dan whitespace yang cukup. Jangan membuat setiap informasi menjadi
kartu terpisah jika sebenarnya dapat dikelompokkan secara sederhana.

## 5. Global Layout

### 5.1 Sidebar

Sidebar kiri memuat nama/logo proyek dan navigasi:

- Dashboard
- Detection
- How It Works
- Model Information
- About

Item aktif harus mudah dibedakan. Gunakan ikon hanya jika ikon tersedia dan maknanya jelas; jangan
menggunakan emoji sebagai pengganti ikon fungsional. Di mobile, gunakan perilaku sidebar native
Streamlit bila paling stabil.

### 5.2 Main content

- Lebar konten desktop sekitar 1.200–1.280 px jika didukung layout.
- Jaga ruang gambar agar bounding box tidak terlalu kecil.
- Gunakan panel/kartu untuk pengelompokan yang bermakna saja.
- Jangan menyisipkan visual stok atau ilustrasi yang tidak membantu alur.

## 6. Page Specifications

### 6.1 Dashboard

Tujuan: pengunjung paham produk dalam beberapa detik.

Urutan konten yang disarankan:

1. Hero dengan nama proyek dan deskripsi satu kalimat.
2. CTA utama **Analyze an Image** menuju halaman Detection.
3. Ringkasan cara kerja singkat: Upload → Detect → Associate → Count → Decide.
4. Fakta model yang sudah terverifikasi, seperti YOLO26m, kelas aktual, dan IoA threshold 0.60.
5. Catatan singkat bahwa sistem merupakan prototype analisis citra.

Metrik penelitian seperti mAP@50 89.59% hanya boleh tampil sebagai hasil paper/laporan yang telah
dikonfirmasi. Jangan mempresentasikannya sebagai akurasi per gambar atau jaminan performa deployment.

### 6.2 Detection — halaman utama

**Sebelum analisis:**

- Judul dan instruksi upload satu gambar.
- Uploader drag-and-drop yang jelas.
- Daftar format JPG/JPEG/PNG dan limit ukuran dari konfigurasi aktual.
- Preview gambar asli.
- Tombol utama **Analyze Image**.

**Saat proses:**

- Tampilkan `MEMPROSES` dan status teks yang jujur.
- Jangan membuat persentase progress palsu.
- Cegah klik berulang yang mengirim request duplikat jika request sedang berjalan.

**Sesudah berhasil:**

- Layout dua kolom pada desktop: annotated image sebagai visual utama dan ringkasan hasil di sisi lain.
- Ringkasan: total motorcycle, total person terdeteksi, total motorcycle pelanggaran.
- Daftar hasil per motorcycle dengan jumlah person dan status.
- Detail association, confidence, dan IoA melalui detail/expander yang tidak memadati tampilan awal.
- Tombol **Download Annotated Image**.
- Jika praktis, tampilkan original dan result side-by-side; jangan mengecilkan gambar hasil secara berlebihan.

**Sesudah gagal:**

- Pesan jelas, misalnya file tidak didukung, file terlalu besar, service tidak tersedia, atau analisis gagal.
- Pertahankan halaman dalam keadaan dapat dipulihkan dan memungkinkan pengguna mencoba kembali.
- Jangan menampilkan stack trace, path server, atau secret di UI.

### 6.3 How It Works

Tampilkan proses dalam 5–6 langkah yang responsif:

`Upload → YOLO26m → Person/Motorcycle Detections → IoA Association → Counting → Decision`

Setiap langkah berisi judul singkat dan penjelasan satu kalimat. Diagram bukan dekorasi: setiap langkah
harus merefleksikan pipeline yang benar-benar diimplementasikan.

### 6.4 Model Information

Tampilkan hanya informasi yang terverifikasi:

- Nama model yang digunakan: YOLO26m.
- Nama artifact: `yolo26m_best.pt`, setelah keberadaan dan formatnya dikonfirmasi.
- Nama class dan ID aktual berdasarkan metadata checkpoint.
- IoA threshold `0.60`.
- Rule status per motorcycle.
- Metrik paper, termasuk mAP@50 89.59%, hanya jika dikonfirmasi dari sumber penelitian.
- Batasan prototype dan perbedaan antara object detection dengan association/decision logic.

Jangan menunjukkan detail internal arsip checkpoint seperti `data.pkl` sebagai metrik atau kemampuan model.

### 6.5 About

Muat judul, konteks proyek, dan informasi tim/organisasi yang memang diberikan untuk dipublikasikan.
Jangan menambahkan nama, logo, afiliasi, atau klaim yang tidak disetujui/dikonfirmasi.

## 7. Component Inventory

| Komponen konseptual | Tanggung jawab |
|---|---|
| `SidebarNav` | Navigasi konsisten |
| `ImageUploader` | Upload satu JPG/JPEG/PNG |
| `ImagePreview` | Menampilkan gambar asli dengan aspect ratio tepat |
| `DetectionSummary` | Ringkasan hasil |
| `AnnotatedImage` | Menampilkan hasil deteksi |
| `StatusBadge` | Status dengan teks dan warna |
| `MotorcycleResult` | Hitungan/status setiap motorcycle |
| `AssociationDetails` | Confidence dan IoA bila tersedia |
| `PipelineStep` | Penjelasan pipeline |
| `ErrorNotice` | Error/actionable message |
| `DownloadResult` | Download annotated image |

Implementasikan sebagai komponen/fungsi yang cocok dengan Streamlit; nama di tabel bersifat konseptual,
bukan kewajiban memakai framework frontend tambahan.

## 8. Interaction and Motion

Animasi sangat terbatas dan hanya bila mendukung feedback: hover tombol, expand/collapse detail,
atau loading indicator native. Skill `animate` dan `review-animations` hanya dipakai jika interaksi
nyata memang membutuhkan motion dan instruksinya kompatibel dengan Streamlit.

Dilarang:

- fake radar/scan yang seolah-olah model sedang melakukan sesuatu yang tidak terjadi;
- persentase proses rekaan;
- auto-playing carousel;
- efek partikel/parallax berlebihan;
- animasi yang menghambat aksesibilitas atau membuat halaman lambat.

## 9. Responsive and Accessibility

- Pada layar sempit, susun gambar dan hasil secara vertikal.
- Pertahankan aspect ratio gambar; jangan stretch.
- Gunakan label tekstual, contrast yang cukup, focus state yang dapat dikenali, serta tombol dengan
  label yang bermakna.
- Jangan bergantung pada warna saja untuk menyampaikan status.
- Area interaktif harus cukup besar dan tidak saling bertumpuk.
- Pastikan empty/loading/error/success states dapat dibedakan.

## 10. Visual QA Checklist

- [ ] Satu CTA utama yang jelas pada Dashboard dan Detection.
- [ ] Sidebar konsisten untuk seluruh halaman.
- [ ] Hasil anotasi menjadi fokus utama setelah inference.
- [ ] Status selalu berisi teks, bukan warna saja.
- [ ] Image aspect ratio terjaga dan bounding box dapat dibaca.
- [ ] Detail teknis tersedia tanpa membuat tampilan awal padat.
- [ ] Tidak ada data palsu, fake history, atau fake progress.
- [ ] Mobile layout tetap dapat digunakan.
- [ ] Semua tombol dan ikon melakukan aksi nyata.
- [ ] Loading, error, empty, dan success states telah diperiksa.
