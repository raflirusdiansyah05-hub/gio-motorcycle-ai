import time
import io
import streamlit as st
from PIL import Image

from dashboard.components.ui import (
    inject_custom_css,
    render_header,
    render_sidebar_brand,
    render_status_badge,
    render_footer,
)
from dashboard.services.inference_client import InferenceClient
from dashboard.utils.image_utils import validate_uploaded_file, decode_base64_data_uri

st.set_page_config(
    page_title="Deteksi Pelanggaran — GIO",
    page_icon="🛵",
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_custom_css()

render_header(
    title="Deteksi Pelanggaran Penumpang Sepeda Motor",
    subtitle="Unggah satu citra berformat JPG atau PNG untuk mendeteksi sepeda motor, penumpang, dan status kepatuhan muatan."
)

# Inisialisasi session state untuk manajemen hasil analisis
if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None
if "analyzed_file_name" not in st.session_state:
    st.session_state["analyzed_file_name"] = None
if "annotated_bytes" not in st.session_state:
    st.session_state["annotated_bytes"] = None
if "last_error" not in st.session_state:
    st.session_state["last_error"] = None

# Bagian 1: Uploader Citra
with st.container(border=True):
    st.markdown("##### Unggah Citra Uji")
    uploaded_file = st.file_uploader(
        "Pilih atau seret satu file citra (JPG, JPEG, PNG — Maks. 10 MB):",
        type=["jpg", "jpeg", "png"],
        help="Unggah satu citra yang memperlihatkan sepeda motor dan pengendara/penumpang."
    )

# Jika pengguna mengganti file atau mengosongkan, reset state hasil
if uploaded_file is None:
    st.session_state["analysis_result"] = None
    st.session_state["analyzed_file_name"] = None
    st.session_state["annotated_bytes"] = None
    st.session_state["last_error"] = None

col_upload_preview, col_action = st.columns([3, 2], vertical_alignment="top")

if uploaded_file is not None:
    # Validasi awal pada sisi frontend
    is_valid, validation_error = validate_uploaded_file(uploaded_file)

    if not is_valid:
        st.error(f"Validasi file gagal: {validation_error}")
    else:
        file_bytes = uploaded_file.getvalue()

        with col_upload_preview:
            with st.container(border=True):
                st.markdown("##### Pratinjau Citra Asli")
                try:
                    preview_img = Image.open(io.BytesIO(file_bytes))
                    st.image(
                        preview_img,
                        width="stretch",
                        caption=f"Berkas: {uploaded_file.name} ({len(file_bytes) / 1024:.1f} KB)"
                    )
                except Exception:
                    st.error("Gagal menampilkan pratinjau citra. Berkas mungkin rusak.")

        with col_action:
            with st.container(border=True):
                st.markdown("##### Panel Tindakan")
                st.caption(
                    "Klik tombol di bawah untuk mengirim citra ke backend FastAPI dan menjalankan inferensi YOLO26m serta kalkulasi asosiasi IoA."
                )

                # Tombol Analisis Utama (bersih tanpa emoji)
                if st.button("Analisis Pelanggaran", width="stretch", type="primary"):
                    client = InferenceClient()

                    # Tampilkan status proses yang jujur tanpa fake animations
                    with st.spinner("Menjalankan inferensi model YOLO26m pada backend..."):
                        mime_type = uploaded_file.type or "image/jpeg"
                        success, response_data = client.predict(
                            file_bytes=file_bytes,
                            filename=uploaded_file.name,
                            mime_type=mime_type
                        )

                    if success:
                        st.session_state["analysis_result"] = response_data
                        st.session_state["analyzed_file_name"] = uploaded_file.name
                        st.session_state["last_error"] = None

                        # Dekode Base64 data URI ke bytes biner untuk tombol unduh
                        data_uri = response_data.get("annotated_image", "")
                        try:
                            st.session_state["annotated_bytes"] = decode_base64_data_uri(data_uri)
                        except Exception:
                            st.session_state["annotated_bytes"] = None
                            st.warning("Citra anotasi diterima namun format Base64 gagal didekode untuk pengunduhan.")
                    else:
                        st.session_state["analysis_result"] = None
                        st.session_state["annotated_bytes"] = None
                        st.session_state["last_error"] = response_data

# Tampilkan pesan error jika ada (bersih tanpa emoji)
if st.session_state.get("last_error"):
    err = st.session_state["last_error"]
    err_code = err.get("code", "UNKNOWN_ERROR")
    err_msg = err.get("message", "Terjadi kesalahan saat memproses citra.")
    st.error(f"**Gagal Memproses [{err_code}]:** {err_msg}")

# Bagian 2: Tampilan Hasil Analisis
result = st.session_state.get("analysis_result")
if result:
    st.divider()
    st.subheader("Hasil Analisis Inferensi")

    summary = result.get("summary", {})
    motorcycles = result.get("motorcycles", [])
    unassociated = result.get("unassociated_persons", [])
    proc_time = result.get("processing_time_ms", 0.0)

    # Ringkasan Metrik menggunakan native st.metric
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric(label="Total Motor", value=summary.get("motorcycles", 0))
    with m2:
        st.metric(label="Total Orang", value=summary.get("persons", 0))
    with m3:
        st.metric(label="Motor Aman", value=summary.get("safe", 0))
    with m4:
        st.metric(label="Motor Pelanggaran", value=summary.get("violations", 0))
    with m5:
        st.metric(label="Waktu Inferensi", value=f"{proc_time:.0f} ms")

    st.markdown("<br/>", unsafe_allow_html=True)

    # Perbandingan Visual Side-by-Side (Fokus Utama)
    col_img_orig, col_img_annotated = st.columns(2)
    with col_img_orig:
        with st.container(border=True):
            st.markdown("##### 1. Citra Input Asli")
            if uploaded_file is not None:
                st.image(uploaded_file.getvalue(), width="stretch", caption="Citra Sebelum Analisis")

    with col_img_annotated:
        with st.container(border=True):
            st.markdown("##### 2. Citra Hasil Anotasi")
            annotated_data_uri = result.get("annotated_image")
            if annotated_data_uri:
                st.image(annotated_data_uri, width="stretch", caption="Bounding Box Motor, Penumpang & Status Kepatuhan")

            # Tombol Unduh Citra Anotasi (bersih tanpa emoji)
            if st.session_state.get("annotated_bytes"):
                timestamp = int(time.time())
                st.download_button(
                    label="Unduh Gambar Anotasi (JPEG)",
                    data=st.session_state["annotated_bytes"],
                    file_name=f"gio_annotated_{timestamp}.jpg",
                    mime="image/jpeg",
                    width="stretch"
                )

    st.divider()

    # Detail Per-Sepeda Motor
    st.subheader("Rincian Status per Sepeda Motor")
    if not motorcycles:
        st.info("Tidak ada sepeda motor yang terdeteksi pada citra ini.")
    else:
        for motor in motorcycles:
            m_id = motor.get("id", 0)
            status = motor.get("status", "AMAN")
            p_count = motor.get("person_count", 0)
            conf = motor.get("confidence", 0.0)
            bbox = motor.get("bbox", [])
            associated = motor.get("associated_persons", [])

            badge_html = render_status_badge(status)

            with st.container(border=True):
                c_header, c_badge = st.columns([4, 1], vertical_alignment="center")
                with c_header:
                    st.markdown(f"#### Sepeda Motor #{m_id} • {p_count} Orang")
                    st.caption(
                        f"Confidence: **{conf:.1%}** | Bounding Box: `[{bbox[0]:.1f}, {bbox[1]:.1f}, {bbox[2]:.1f}, {bbox[3]:.1f}]`"
                    )
                with c_badge:
                    st.markdown(badge_html, unsafe_allow_html=True)

                if associated:
                    with st.expander(f"Detail Penumpang Terasosiasi ({len(associated)} orang)"):
                        for p in associated:
                            p_id = p.get("person_id", p.get("id", 0))
                            p_conf = p.get("confidence", 0.0)
                            p_ioa = p.get("ioa", 0.0)
                            st.markdown(
                                f"- **Orang #{p_id}:** Confidence `{p_conf:.1%}` | Skor IoA ke Motor: `{p_ioa:.4f}` ({p_ioa:.1%})"
                            )

    # Orang yang Tidak Terasosiasi (jika ada)
    if unassociated:
        st.divider()
        st.subheader("Orang di Luar Kendaraan (Unassociated)")
        st.caption(
            f"Terdapat {len(unassociated)} orang terdeteksi yang memiliki IoA < 0.60 terhadap seluruh sepeda motor (pejalan kaki/di luar kendaraan)."
        )
        with st.expander(f"Lihat Detail {len(unassociated)} Orang Tidak Terasosiasi"):
            for u in unassociated:
                u_id = u.get("person_id", u.get("id", 0))
                u_conf = u.get("confidence", 0.0)
                u_bbox = u.get("bbox", [])
                st.markdown(
                    f"- **Orang #{u_id}:** Confidence `{u_conf:.1%}` | BBox: `[{u_bbox[0]:.1f}, {u_bbox[1]:.1f}, {u_bbox[2]:.1f}, {u_bbox[3]:.1f}]`"
                )

render_footer()
