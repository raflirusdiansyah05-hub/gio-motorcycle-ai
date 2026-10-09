import streamlit as st
from dashboard.components.ui import (
    inject_custom_css,
    render_header,
    render_sidebar_brand,
    render_footer,
)

st.set_page_config(
    page_title="Tentang Proyek — GIO",
    page_icon="🛵",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_custom_css()

render_header(
    title="Tentang Proyek GIO",
    subtitle="Latar belakang, arsitektur teknis, jaminan privasi, dan batasan operasional prototipe."
)

st.subheader("Latar Belakang & Tujuan")
with st.container(border=True):
    st.markdown(
        """
        Proyek **GIO** dikembangkan untuk mengeksplorasi pemanfaatan model deep learning object detection modern (**YOLO26m**) yang dikombinasikan dengan heuristik komputasi spasial **Intersection over Area (IoA)** guna mendeteksi potensi pelanggaran kelebihan kapasitas penumpang pada sepeda motor roda dua.

        Sistem ini berfungsi sebagai media demonstrasi teknis dan sarana evaluasi prototipe pameran akademik untuk menguji keandalan asosiasi visual antara kendaraan dan penumpang dalam format citra diam (*still image*).
        """
    )

st.divider()

st.subheader("Arsitektur Teknologi Terintegrasi")
col_tech1, col_tech2 = st.columns(2)

with col_tech1:
    with st.container(border=True):
        st.markdown("#### Frontend Application")
        st.markdown(
            """
            - **Framework:** Streamlit (Python)
            - **Desain:** Dark-first UI (Design Tokens `#0B0D10`, `#12161B`, `#7C5CFC`)
            - **Komunikasi API:** HTTP client tersinkronisasi via variabel `INFERENCE_API_URL`
            - **Validasi Input:** Batas unggah 10 MB, format JPG/PNG, rendering Base64
            """
        )

with col_tech2:
    with st.container(border=True):
        st.markdown("#### Backend Inference Engine")
        st.markdown(
            """
            - **Framework:** FastAPI & Uvicorn (REST API)
            - **Model Checkpoint:** `artifacts/yolo26m_candidate.pt` (Ultralytics PyTorch)
            - **Asosiasi Spasial:** Modul IoA independen (Ambang batas 0.60, Highest IoA)
            - **Anotasi Visual:** Pillow in-memory rendering & Base64 Data URI
            """
        )

st.divider()

st.subheader("Kebijakan Privasi & Nol Penyimpanan (Zero-Persistence)")
with st.container(border=True):
    st.markdown(
        """
        **Komitmen Perlindungan Privasi Data:**
        1. **Pemrosesan Murni In-Memory:** Seluruh citra yang diunggah diproses secara langsung di dalam memori akses acak (RAM).
        2. **Nol Penyimpanan Disk:** Tidak ada berkas citra asli maupun citra beranotasi yang disimpan secara permanen pada disk server atau basis data eksternal.
        3. **Nol Logging Konten:** Server tidak mencatat (*log*) isi biner citra mentah atau informasi identifikasi personal (PII).
        4. **Pembersihan Resource:** Setelah sesi request dan visualisasi selesai, buffer memori upload segera dilepaskan dan file stream ditutup (`await file.close()`).
        """
    )

st.divider()

st.subheader("Batasan Hukum & Status Prototipe")
with st.container(border=True):
    st.markdown(
        """
        **Pernyataan Penyangkalan (Disclaimer):**
        Sistem GIO adalah alat bantu analisis berbasis kecerdasan buatan eksperimental. Sistem ini **BUKAN** merupakan bagian dari Electronic Traffic Law Enforcement (ETLE) resmi milik kepolisian atau otoritas perhubungan mana pun. Hasil status AMAN atau PELANGGARAN merupakan hasil komputasi model dan tidak dapat digunakan sebagai alat bukti hukum, penegakan sanksi, atau penetapan tilang di jalan raya.
        """
    )

render_footer()
