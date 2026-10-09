import streamlit as st
from dashboard.components.ui import (
    inject_custom_css,
    render_header,
    render_sidebar_brand,
    render_footer,
)

st.set_page_config(
    page_title="Cara Kerja — GIO",
    page_icon="🛵",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_custom_css()

render_header(
    title="Cara Kerja Sistem Analisis GIO",
    subtitle="Penjelasan komprehensif alur kerja dari input citra hingga penentuan status kepatuhan kapasitas muatan."
)

st.subheader("Pipeline Inferensi & Asosiasi Spasial")
st.caption(
    "Sistem bekerja melalui 6 tahapan pemrosesan berurutan yang memisahkan tanggung jawab deteksi objek visual, kalkulasi geometri spasial, dan logika keputusan bisnis:"
)

steps = [
    {
        "num": "1",
        "title": "Input & Validasi Citra",
        "desc": "Satu berkas citra (JPG atau PNG, maksimal 10 MB) diterima dan divalidasi keutuhan datanya secara in-memory melalui Pillow tanpa pernah ditulis ke media penyimpanan disk permanen."
    },
    {
        "num": "2",
        "title": "Deteksi Objek YOLO26m",
        "desc": "Model deep learning YOLO26m (kandidat `artifacts/yolo26m_candidate.pt`) mengekstrak bounding box koordinat dan skor confidence untuk dua kelas terverifikasi: `motor` (ID: 0) dan `orang` (ID: 1)."
    },
    {
        "num": "3",
        "title": "Kalkulasi Intersection over Area (IoA)",
        "desc": "Untuk setiap kotak orang (P) dan kotak motor (M), dihitung rasio luas irisan terhadap total luas orang menggunakan rumus matematis:\n\n"
                "$$\\text{IoA}(P, M) = \\frac{\\text{Area}(P \\cap M)}{\\text{Area}(P)}$$\n\n"
                "Rasio ini mengukur proporsi tubuh orang yang berada di dalam area sepeda motor."
    },
    {
        "num": "4",
        "title": "Ambang Batas & Aturan Highest IoA",
        "desc": "Kandidat asosiasi disaring dengan ambang batas resmi **IoA ≥ 0.60**. Jika satu orang memenuhi ambang batas terhadap lebih dari satu sepeda motor, sistem memilih motor dengan **skor IoA tertinggi**. Jika nilai IoA sama persis, diterapkan tie-breaker deterministik berdasarkan indeks deteksi motor terkecil. **Satu orang dijamin tidak pernah dihitung lebih dari satu kali.**"
    },
    {
        "num": "5",
        "title": "Penghitungan Penumpang per Motor",
        "desc": "Jumlah orang yang terasosiasi diakumulasikan secara independen untuk masing-masing sepeda motor. Orang yang tidak memenuhi ambang batas IoA terhadap motor mana pun (< 0.60) dikategorikan sebagai pejalan kaki/di luar kendaraan."
    },
    {
        "num": "6",
        "title": "Penentuan Status Kepatuhan",
        "desc": "Status kepatuhan dievaluasi per unit motor berdasarkan aturan baku:\n\n"
                "- **0, 1, atau 2 Orang:** Status **AMAN** (motor kosong, pengendara tunggal, atau berboncengan dua wajar).\n"
                "- **3 Orang atau Lebih:** Status **PELANGGARAN** (melebihi kapasitas muatan aman)."
    }
]

for step in steps:
    with st.container(border=True):
        st.markdown(f"#### Tahap {step['num']} — {step['title']}")
        st.markdown(step["desc"])

st.divider()

# Batasan Teknis & Asumsi
st.subheader("Batasan Teknis & Karakteristik Geometri 2D")
with st.container(border=True):
    st.markdown(
        """
        - **Proyeksi Kamera 2D:** Intersection over Area (IoA) merupakan pendekatan berbasis geometri kotak pembatas (bounding box) pada proyeksi citra 2 dimensi. Metode ini tidak memiliki sensor kedalaman 3D (seperti LiDAR atau depth camera).
        - **Oklusi dan Sudut Pandang (Perspective):** Pada sudut kamera yang sangat datar (*eye-level*) dengan kepadatan lalu lintas tinggi, pejalan kaki yang berdiri di depan motor dapat memiliki tumpang-tindih visual yang menyerupai penumpang.
        - **Sifat Prototipe:** Hasil analisis merupakan estimasi otomatis berbantuan kecerdasan buatan untuk tujuan demonstrasi, bukan hasil sertifikasi alat ukur hukum. Sistem tidak mendukung video streaming, CCTV live feed, atau pelacakan antar-frame (object tracking).
        """
    )

render_footer()
