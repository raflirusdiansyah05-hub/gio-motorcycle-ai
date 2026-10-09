import textwrap
import streamlit as st
from typing import Any, Optional


def inject_custom_css():
    """
    Menyuntikkan CSS kustom dengan token desain resmi dari design.md:
    Dark theme, surface colors, subtle borders, crisp typography, responsive layout.
    """
    css = textwrap.dedent("""
    <style>
    :root {
        --gio-bg: #0B0D10;
        --gio-surface: #12161B;
        --gio-surface-2: #181D23;
        --gio-border: #272D35;
        --gio-text-primary: #F5F7FA;
        --gio-text-secondary: #9BA4B0;
        --gio-accent: #7C5CFC;
        --gio-accent-soft: #211C3D;
        --gio-success: #22C55E;
        --gio-success-soft: #102B1B;
        --gio-danger: #EF4444;
        --gio-danger-soft: #35171A;
        --gio-warning: #F59E0B;
        --gio-info: #38BDF8;
    }

    /* Main Content Spacing: Naikkan posisi konten utama dengan jarak aman di bawah toolbar */
    .main .block-container,
    [data-testid="stMainBlockContainer"],
    [data-testid="block-container"],
    .block-container {
        padding-top: 2.75rem !important;
        padding-bottom: 3.5rem !important;
        max-width: 1280px;
    }

    /* Pastikan heading utama tidak terpotong oleh toolbar dan memiliki line-height aman */
    .main h1:first-of-type,
    [data-testid="stMainBlockContainer"] h1:first-of-type,
    .block-container h1:first-of-type {
        margin-top: 0 !important;
        padding-top: 0.35rem !important;
        line-height: 1.25 !important;
    }

    /* Header Sidebar: Sejajarkan Branding [GIO] Motorcycle AI dengan tombol collapse [<<] dalam satu baris */
    [data-testid="stSidebarHeader"] {
        position: absolute !important;
        top: 0.6rem !important;
        right: 0.75rem !important;
        padding: 0 !important;
        margin: 0 !important;
        height: 2.25rem !important;
        min-height: 2.25rem !important;
        display: flex !important;
        align-items: center !important;
        justify-content: flex-end !important;
        z-index: 20 !important;
        background: transparent !important;
    }

    /* Tombol collapse << agar terpusat secara vertikal di sebelah kanan dan selalu terlihat */
    [data-testid="stSidebarCollapseButton"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 !important;
        padding: 0 !important;
        height: 2.25rem !important;
        width: 2.25rem !important;
    }

    [data-testid="stSidebarCollapseButton"] button {
        opacity: 1 !important;
        visibility: visible !important;
    }

    [data-testid="stLogoSpacer"] {
        display: none !important;
    }

    /* Container Sidebar Streamlit: Menggunakan ruang vertikal penuh viewport */
    section[data-testid="stSidebar"],
    [data-testid="stSidebar"] {
        height: 100vh !important;
        min-height: 100vh !important;
    }

    /* Mulai konten sidebar tepat di puncak dengan posisi relatif dan tinggi penuh viewport */
    [data-testid="stSidebarContent"] {
        display: flex !important;
        flex-direction: column !important;
        height: 100vh !important;
        min-height: 100vh !important;
        padding-top: 0.6rem !important;
        position: relative !important;
        overflow-y: auto !important;
        box-sizing: border-box !important;
    }

    /* Area 1 Branding: Sejajar satu baris di kiri dengan tombol collapse di kanan */
    .gio-sidebar-brand {
        display: flex !important;
        align-items: center !important;
        height: 2.25rem !important;
        min-height: 2.25rem !important;
        margin: 0 !important;
        padding: 0 2.5rem 0 0 !important; /* Ruang aman agar tidak bertabrakan dengan tombol << di kanan */
        box-sizing: border-box !important;
    }

    /* Sidebar User Content: Flex container yang mengisi sisa tinggi sidebar secara fleksibel */
    [data-testid="stSidebarUserContent"] {
        display: flex !important;
        flex-direction: column !important;
        flex: 1 1 auto !important;
        height: calc(100vh - 1.2rem) !important;
        min-height: calc(100vh - 1.2rem) !important;
        padding-top: 0 !important;
        padding-bottom: 0.75rem !important;
        box-sizing: border-box !important;
    }

    /* Seluruh wrapper perantara dan stVerticalBlock di dalam stSidebarUserContent mengisi tinggi penuh (flex: 1) */
    [data-testid="stSidebarUserContent"] > div,
    [data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"] {
        display: flex !important;
        flex-direction: column !important;
        flex: 1 1 auto !important;
        height: 100% !important;
        min-height: 100% !important;
    }

    /* PUSAT KOREKSI: Dorong wrapper elemen footer ke dasar paling bawah sidebar via margin-top: auto */
    [data-testid="stSidebarUserContent"] [data-testid="stElementContainer"]:has(.gio-sidebar-desc),
    [data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"]:last-child,
    [data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"] > div:last-child {
        margin-top: auto !important;
        width: 100% !important;
    }

    /* Judul Menu Navigasi statis dekat dengan branding tanpa panah dropdown */
    .gio-nav-title {
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        color: #9BA4B0 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        margin-top: 0.1rem !important;
        margin-bottom: 0.25rem !important;
        padding-left: 0.15rem !important;
        user-select: none !important;
    }

    /* Styling item navigasi page_link di dalam sidebar agar ringkas dan rapi */
    [data-testid="stSidebarUserContent"] a[data-testid="stPageLink-NavLink"] {
        border-radius: 6px !important;
        padding: 0.35rem 0.65rem !important;
        color: var(--gio-text-primary) !important;
        transition: background 0.15s ease !important;
    }

    [data-testid="stSidebarUserContent"] a[data-testid="stPageLink-NavLink"]:hover {
        background-color: var(--gio-surface-2) !important;
    }

    /* Area 3: Deskripsi produk di bagian paling bawah sidebar dengan garis pembatas */
    .gio-sidebar-desc {
        width: 100% !important;
        padding-top: 0.75rem !important;
        padding-bottom: 0.5rem !important;
        border-top: 1px solid #272D35 !important;
        font-size: 0.8rem !important;
        color: #9BA4B0 !important;
        line-height: 1.45 !important;
        letter-spacing: 0.01em !important;
        box-sizing: border-box !important;
    }

    /* Keselarasan status bar pada Dashboard */
    .stAlert {
        margin-bottom: 0 !important;
    }

    /* Subtitle text styling */
    .gio-subtitle {
        font-size: 1.05rem;
        color: var(--gio-text-secondary);
        margin-top: -0.5rem;
        margin-bottom: 1.5rem;
        line-height: 1.5;
    }

    /* Status Badges */
    .gio-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.25rem 0.65rem;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }
    .gio-badge-safe {
        background-color: var(--gio-success-soft);
        color: var(--gio-success);
        border: 1px solid #1A4D2E;
    }
    .gio-badge-violation {
        background-color: var(--gio-danger-soft);
        color: var(--gio-danger);
        border: 1px solid #5C2226;
    }
    .gio-badge-info {
        background-color: var(--gio-accent-soft);
        color: var(--gio-info);
        border: 1px solid #2D3A54;
    }
    .gio-badge-warning {
        background-color: #332614;
        color: var(--gio-warning);
        border: 1px solid #57411C;
    }

    /* Primary button enhancement */
    .stButton > button[kind="primary"] {
        background-color: var(--gio-accent);
        color: #FFFFFF;
        font-weight: 600;
        border-radius: 6px;
        padding: 0.55rem 1.5rem;
        border: none;
        transition: all 0.2s ease;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #6A4CE0;
        box-shadow: 0 4px 12px rgba(124, 92, 252, 0.25);
    }

    /* Download button */
    .stDownloadButton > button {
        background-color: var(--gio-surface-2);
        color: var(--gio-text-primary);
        border: 1px solid var(--gio-border);
        border-radius: 6px;
        font-weight: 500;
    }
    .stDownloadButton > button:hover {
        border-color: var(--gio-accent);
        color: #FFFFFF;
    }

    /* Mobile responsive adjustments */
    @media (max-width: 768px) {
        .main .block-container,
        [data-testid="stMainBlockContainer"],
        [data-testid="block-container"],
        .block-container {
            padding-top: 2rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        .gio-subtitle {
            font-size: 0.95rem;
        }
        [data-testid="stSidebarUserContent"] {
            min-height: auto !important;
        }
        .gio-sidebar-desc {
            margin-top: 2rem !important;
        }
    }
    </style>
    """).strip()
    st.markdown(css, unsafe_allow_html=True)


def render_sidebar_top_brand():
    """Merender identitas dan logo pada bagian paling atas sidebar (Area 1) sejajar dengan tombol collapse."""
    brand_html = textwrap.dedent("""
    <div class="gio-sidebar-brand">
        <div style="font-size: 1.15rem; font-weight: 700; color: #F5F7FA; display: flex; align-items: center; gap: 0.55rem; letter-spacing: -0.01em;">
            <span style="background: #7C5CFC; color: #FFF; padding: 2px 7px; border-radius: 5px; font-size: 0.85rem; font-weight: 700; letter-spacing: 0.04em;">GIO</span>
            <span>Motorcycle AI</span>
        </div>
    </div>
    """).strip()
    st.sidebar.markdown(brand_html, unsafe_allow_html=True)


def render_sidebar_bottom_desc():
    """Merender deskripsi produk di bagian paling bawah sidebar (Area 3)."""
    desc_html = textwrap.dedent("""
    <div class="gio-sidebar-desc">
        YOLO26m Passenger Violation Detector
    </div>
    """).strip()
    st.sidebar.markdown(desc_html, unsafe_allow_html=True)


def render_app_sidebar(pages_spec: list):
    """
    Merender sidebar terpadu 3 area secara murni di dalam st.sidebar:
    1. Kontrol collapse bawaan Streamlit [<<] tetap di posisi atas bawaan
    2. Area 1: Branding [GIO] Motorcycle AI di bagian paling atas
    3. Divider tipis
    4. Header statis 'Menu Navigasi' (tanpa panah dropdown)
    5. Area 2: Daftar navigasi st.page_link (Dashboard, Detection, How It Works, Model Info, About)
    6. Ruang fleksibel vertikal (margin-top: auto)
    7. Divider tipis & Area 3: Deskripsi produk di bagian paling bawah
    """
    with st.sidebar:
        # Area 1: Branding di atas
        render_sidebar_top_brand()

        # Divider tipis setelah branding
        st.markdown(
            '<hr style="border: none; border-top: 1px solid #272D35; margin: 0.45rem 0 0.45rem 0;" />',
            unsafe_allow_html=True,
        )

        # Area 2: Judul Menu Navigasi tanpa panah dropdown
        st.markdown(
            '<div class="gio-nav-title">Menu Navigasi</div>',
            unsafe_allow_html=True,
        )

        # Daftar navigasi page_link
        for item in pages_spec:
            st.page_link(item["page"], label=item["label"], icon=item["icon"], width="stretch")

        # Area 3: Deskripsi produk di bagian paling bawah sidebar
        render_sidebar_bottom_desc()


def render_sidebar_brand():
    """Fallback kompatibilitas: memanggil branding atas dan deskripsi bawah jika dipanggil langsung."""
    render_sidebar_top_brand()
    render_sidebar_bottom_desc()


def render_header(title: str, subtitle: Optional[str] = None):
    """
    Merender judul dan subjudul halaman menggunakan elemen native Streamlit
    untuk menjamin 100% bebas dari bug indented code block pada Markdown.
    """
    st.title(title)
    if subtitle:
        st.markdown(f"<p class='gio-subtitle'>{subtitle}</p>", unsafe_allow_html=True)


def render_status_badge(status: str) -> str:
    """Mengembalikan tag HTML untuk status badge dengan teks eksplisit dan warna kontras."""
    status_upper = status.upper().strip()
    if status_upper == "AMAN":
        return '<span class="gio-badge gio-badge-safe">✓ AMAN</span>'
    elif status_upper == "PELANGGARAN":
        return '<span class="gio-badge gio-badge-violation">⚠ PELANGGARAN</span>'
    elif status_upper in ("MEMPROSES", "PROSES"):
        return '<span class="gio-badge gio-badge-info">● MEMPROSES</span>'
    else:
        return f'<span class="gio-badge gio-badge-warning">{status_upper}</span>'


def render_metric_card(label: str, value: Any, color_hint: Optional[str] = None):
    """Merender metrik menggunakan komponen native st.metric yang bersih dan responsif."""
    st.metric(label=label, value=value)


def render_footer():
    """Merender footer informasi privasi dan status prototipe tanpa leading indentation."""
    footer_html = textwrap.dedent("""
    <hr style="border-top: 1px solid #272D35; margin: 2rem 0 1rem 0;"/>
    <div style="font-size: 0.8rem; color: #9BA4B0; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem; padding-bottom: 1rem;">
        <div>
            <strong>GIO Prototype</strong> — Deteksi Berbantuan AI YOLO26m &amp; Aturan IoA (Bukan Instrumen ETLE Resmi)
        </div>
        <div>
            Privasi Terjamin: Pemrosesan In-Memory, Citra Tidak Disimpan Permanen
        </div>
    </div>
    """).strip()
    st.markdown(footer_html, unsafe_allow_html=True)
