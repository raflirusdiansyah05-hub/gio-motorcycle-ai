import sys
from pathlib import Path

# Pastikan root aplikasi (/app di kontainer atau root repositori lokal) tersedia di sys.path
_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

import streamlit as st
from dashboard.components.ui import (
    inject_custom_css,
    render_header,
    render_app_sidebar,
    render_footer,
)
from dashboard.services.inference_client import InferenceClient

st.set_page_config(
    page_title="GIO — Motorcycle Violation Detection",
    page_icon="🛵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Injeksi CSS global sejak entrypoint app.py untuk layout sidebar, footer di dasar, dan spacing
inject_custom_css()


def show_dashboard():
    """Halaman utama Dashboard (Landing Overview)."""
    render_header(
        title="Sistem Deteksi Pelanggaran Penumpang Sepeda Motor",
        subtitle="Prototipe analisis citra berbasis computer vision YOLO26m dan asosiasi spasial Intersection over Area (IoA)."
    )

    # Periksa status aktual backend inference service
    client = InferenceClient()
    is_ready, health_info = client.check_health()

    # Indikator Konektivitas Backend Real & CTA (bersih tanpa emoji)
    col_status, col_btn = st.columns([3, 1], vertical_alignment="center")
    with col_status:
        if is_ready:
            model_name = health_info.get("model", "YOLO26m")
            st.success(
                f"**Backend Siap:** Service FastAPI aktif dan model **{model_name}** termuat dalam memori."
            )
        else:
            err_msg = health_info.get("error", {}).get("message", "Service backend tidak dapat dihubungi.")
            st.error(
                f"**Backend Tidak Siap:** {err_msg} (Jalankan service di port 8000)."
            )

    with col_btn:
        if st.button("Buka Halaman Deteksi", width="stretch", type="primary"):
            st.switch_page(page_detect)

    st.divider()

    # Seksi 1: Alur Kerja Analisis
    st.subheader("Alur Analisis Sistem")
    st.caption("Rangkaian pemrosesan komputer visi dan logika keputusan geometris:")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        with st.container(border=True):
            st.markdown("##### 1. Deteksi Objek")
            st.markdown(
                "Model **YOLO26m** mendeteksi bounding box sepeda motor (ID: 0) dan orang (ID: 1) secara simultan."
            )
    with c2:
        with st.container(border=True):
            st.markdown("##### 2. Asosiasi Spasial")
            st.markdown(
                "Dihitung rasio **IoA &ge; 0.60** untuk menghubungkan setiap orang ke motor dengan overlap tertinggi (*highest IoA*)."
            )
    with c3:
        with st.container(border=True):
            st.markdown("##### 3. Penghitungan")
            st.markdown(
                "Setiap sepeda motor dihitung penumpangnya secara independen tanpa risiko *double-counting*."
            )
    with c4:
        with st.container(border=True):
            st.markdown("##### 4. Keputusan Status")
            st.markdown(
                "Status **AMAN** untuk 0–2 orang; status **PELANGGARAN** untuk 3 orang atau lebih pada satu motor."
            )

    st.divider()

    # Seksi 2: Parameter Teknis Terverifikasi
    st.subheader("Parameter Sistem Terverifikasi")

    p1, p2, p3 = st.columns(3)
    with p1:
        with st.container(border=True):
            st.caption("ARSITEKTUR MODEL")
            st.markdown("### YOLO26m")
            st.markdown(
                "Backbone Ultralytics dengan modul C3k2 & C2PSA. Checkpoint: `artifacts/yolo26m_candidate.pt` (41.96 MB)."
            )
    with p2:
        with st.container(border=True):
            st.caption("AMBANG BATAS ASOSIASI")
            st.markdown("### IoA &ge; 0.60")
            st.markdown(
                "Rumus: $\\text{Area}(P \\cap M) / \\text{Area}(P)$. Seleksi eksklusif motor overlap terbesar dengan tie-break deterministik."
            )
    with p3:
        with st.container(border=True):
            st.caption("BATAS KEPATUHAN KAPASITAS")
            st.markdown("### 0–2 AMAN • &ge;3 PELANGGARAN")
            st.markdown(
                "Berdasarkan regulasi kapasitas muatan standar kendaraan roda dua jalan raya."
            )

    st.divider()

    # Catatan Prototipe dan Batasan
    with st.container(border=True):
        st.markdown(
            """
            **Pemberitahuan Karakteristik Prototipe:**
            Aplikasi ini merupakan prototipe demonstrasi teknis untuk pameran akademik/penelitian. Sistem ini menggunakan inferensi computer vision dan aturan heuristik spasial. Sistem ini bukan sistem penegakan hukum resmi (bukan ETLE) dan tidak digunakan untuk penindakan tilang hukum. Seluruh pemrosesan foto dilakukan secara *in-memory* tanpa menyimpan berkas ke media penyimpanan permanen.
            """
        )

    render_footer()


# Definisi seluruh halaman aplikasi untuk router dan navigasi sidebar
page_dash = st.Page(show_dashboard, title="Dashboard", icon=":material/dashboard:", default=True)
page_detect = st.Page("pages/1_Detection.py", title="Detection", icon=":material/videocam:")
page_how = st.Page("pages/2_How_It_Works.py", title="How It Works", icon=":material/help:")
page_model = st.Page("pages/3_Model_Information.py", title="Model Information", icon=":material/psychology:")
page_about = st.Page("pages/4_About.py", title="About", icon=":material/info:")

nav_pages = [
    {"page": page_dash, "label": "Dashboard", "icon": ":material/dashboard:"},
    {"page": page_detect, "label": "Detection", "icon": ":material/videocam:"},
    {"page": page_how, "label": "How It Works", "icon": ":material/help:"},
    {"page": page_model, "label": "Model Information", "icon": ":material/psychology:"},
    {"page": page_about, "label": "About", "icon": ":material/info:"},
]

# Multipage Navigation dengan position="hidden" agar tidak merender stSidebarNav bawaan yang collapsible
pg = st.navigation([p["page"] for p in nav_pages], position="hidden")

# Render Sidebar 3 area terstruktur secara murni di dalam st.sidebar
render_app_sidebar(nav_pages)

pg.run()
