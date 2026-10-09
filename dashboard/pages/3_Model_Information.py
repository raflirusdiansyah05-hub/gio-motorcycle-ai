import streamlit as st
from dashboard.components.ui import (
    inject_custom_css,
    render_header,
    render_sidebar_brand,
    render_footer,
)

st.set_page_config(
    page_title="Informasi Model — GIO",
    page_icon="🛵",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_custom_css()

render_header(
    title="Spesifikasi & Informasi Model YOLO26m",
    subtitle="Fakta teknis terverifikasi mengenai bobot checkpoint, arsitektur inferensi, pemetaan kelas, dan metrik penelitian."
)

st.subheader("1. Karakteristik Checkpoint Model")

c1, c2 = st.columns(2)
with c1:
    with st.container(border=True):
        st.markdown("#### Metadata Checkpoint")
        st.markdown(
            """
            | Parameter | Nilai Terverifikasi |
            |---|---|
            | **Nama Model** | `YOLO26m` |
            | **Tugas Utama** | `detect` (Object Detection) |
            | **File Checkpoint** | `artifacts/yolo26m_candidate.pt` |
            | **Ukuran Berkas** | 41.96 MB (43.997.307 bytes) |
            | **Arsitektur Backbone** | DetectionModel (modul C3k2 & C2PSA) |
            | **Backend Runtime** | PyTorch 2.14+ CPU / Ultralytics 8.4+ |
            """
        )

with c2:
    with st.container(border=True):
        st.markdown("#### Pemetaan Kelas Aktual (Source of Truth)")
        st.caption("Berdasarkan metadata biner resmi checkpoint:")
        st.markdown(
            """
            | ID Kelas | Label Mentah | Deskripsi Semantik |
            |---|---|---|
            | **ID 0** | `motor` | Kendaraan roda dua / sepeda motor |
            | **ID 1** | `orang` | Manusia (pengendara, penumpang, pejalan kaki) |
            """
        )
        st.info("Mapping ID kelas diverifikasi langsung dari struktur metadata Ultralytics checkpoint.")

st.divider()

st.subheader("2. Pemisahan Modularitas Sistem")
st.caption("Sistem dirancang dengan pemisahan tanggung jawab yang ketat antarlapisan untuk stabilitas:")

col_mod1, col_mod2, col_mod3 = st.columns(3)
with col_mod1:
    with st.container(border=True):
        st.caption("LAPISAN DETEKTOR")
        st.markdown("#### Ultralytics YOLO26m")
        st.markdown(
            "Hanya bertanggung jawab mengekstrak bounding box koordinat dan skor confidence. Tidak mengetahui aturan lalu lintas atau kapasitas muatan."
        )

with col_mod2:
    with st.container(border=True):
        st.caption("LAPISAN SPASIAL")
        st.markdown("#### Kalkulasi IoA Geometri")
        st.markdown(
            "Fungsi independen murni berbasis koordinat Cartesian 2D. Mengasosiasikan orang ke motor ber-IoA tertinggi (≥ 0.60) dengan tie-breaking deterministik."
        )

with col_mod3:
    with st.container(border=True):
        st.caption("LAPISAN KEPUTUSAN")
        st.markdown("#### Aturan Kepatuhan")
        st.markdown(
            "Menerima hasil hitungan orang per motor. Menetapkan status **AMAN** (0–2 orang) atau **PELANGGARAN** (≥ 3 orang)."
        )

st.divider()

st.subheader("3. Metrik Penelitian & Evaluasi Model")
with st.container(border=True):
    st.markdown("#### mAP@50 yang Dilaporkan Penelitian: 89.59% (0.8959)")
    st.markdown(
        """
        **Catatan Integritas Data & Atribusi Penelitian:**
        Nilai mAP@50 di atas merupakan hasil pengujian pada dataset validasi penelitian yang dilaporkan oleh peneliti proyek.
        Metrik tersebut **bukan** merupakan jaminan akurasi per-citra tunggal pada setiap kondisi lingkungan di dunia nyata, dan tidak boleh ditafsirkan sebagai kepastian hukum mutlak.
        """
    )

render_footer()
