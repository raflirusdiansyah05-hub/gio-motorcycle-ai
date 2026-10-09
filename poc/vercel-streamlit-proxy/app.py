import streamlit as st
from PIL import Image
import io

st.set_page_config(
    page_title="PoC Vercel-Streamlit Proxy",
    page_icon="⚡",
    layout="centered"
)

st.title("⚡ PoC Vercel-Streamlit Proxy Test")
st.caption("Aplikasi uji minimal untuk memvalidasi WebSocket, Session State, dan Upload Citra melalui Proxy/Rewrites.")

st.markdown("---")

# Test 1: Session State & Counter
st.subheader("1. Test Session State & Re-run")
if "counter" not in st.session_state:
    st.session_state.counter = 0

col1, col2 = st.columns([1, 3])
with col1:
    if st.button("Tambah Hitungan (+1)", key="btn_inc"):
        st.session_state.counter += 1
with col2:
    st.metric(label="Nilai Counter", value=st.session_state.counter)

# Test 2: In-Memory Image Upload & Preview
st.subheader("2. Test In-Memory Image Upload & Preview")
uploaded_file = st.file_uploader(
    "Unggah citra uji (JPG/PNG, in-memory, tidak disimpan ke disk):",
    type=["jpg", "jpeg", "png"],
    key="uploader"
)

if uploaded_file is not None:
    try:
        image_bytes = uploaded_file.read()
        image = Image.open(io.BytesIO(image_bytes))
        st.success(f"Citra berhasil dibaca di memori! Ukuran: {image.width}x{image.height} px, Format: {image.format}")
        st.image(image, caption="Preview Citra In-Memory", use_container_width=True)
    except Exception as e:
        st.error(f"Gagal memproses citra: {e}")
else:
    st.info("Silakan unggah citra kecil untuk menguji transfer data multipart melalui proxy.")

st.markdown("---")

# Test 3: Environment & Header Diagnosis
st.subheader("3. Informasi Host & Runtime")
st.json({
    "session_state_keys": list(st.session_state.keys()),
    "counter_value": st.session_state.counter,
    "has_uploaded_file": uploaded_file is not None
})
