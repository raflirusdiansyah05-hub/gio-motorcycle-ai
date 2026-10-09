import os
import unittest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DASHBOARD_DIR = os.path.abspath(os.path.join(CURRENT_DIR, ".."))


class TestUIRefinement(unittest.TestCase):
    """
    Pengujian otomatis untuk verifikasi Tugas Refinement UI:
    - Tugas A: Struktur sidebar 3 area (Branding atas, Navigasi tengah, Deskripsi bawah)
    - Tugas B: Pembersihan emoji pada 4 elemen UI kunci
    - Tugas C: Layout Dashboard & Detection bebas error dan proporsional
    - Tugas D: Spacing vertikal atas konten utama (1.75rem desktop, 1.25rem mobile)
    - Tugas E: Penghapusan total panel Data Teknis Lapangan (Raw JSON)
    """

    @patch("dashboard.services.inference_client.InferenceClient.predict")
    def test_detection_page_no_raw_json_and_clean_buttons(self, mock_predict):
        """Tugas A & E: Pastikan tidak ada komponen st.json/expander data teknis, dan tombol bebas emoji."""
        import io
        from PIL import Image

        # Simulasikan hasil analisis pada backend
        dummy_result = {
            "success": True,
            "processing_time_ms": 42.5,
            "summary": {
                "motorcycles": 2,
                "persons": 3,
                "safe": 1,
                "violations": 1,
            },
            "motorcycles": [
                {
                    "id": 1,
                    "confidence": 0.92,
                    "bbox": [10.0, 20.0, 100.0, 150.0],
                    "person_count": 1,
                    "status": "AMAN",
                    "associated_persons": [
                        {"person_id": 1, "confidence": 0.88, "ioa": 0.75}
                    ]
                },
                {
                    "id": 2,
                    "confidence": 0.85,
                    "bbox": [150.0, 30.0, 260.0, 180.0],
                    "person_count": 2,
                    "status": "PELANGGARAN",
                    "associated_persons": [
                        {"person_id": 2, "confidence": 0.81, "ioa": 0.68},
                        {"person_id": 3, "confidence": 0.79, "ioa": 0.65}
                    ]
                }
            ],
            "unassociated_persons": [],
            "annotated_image": "data:image/jpeg;base64,/9j/4AAQSkZJRg=="
        }

        mock_predict.return_value = (True, dummy_result)

        path = os.path.join(DASHBOARD_DIR, "pages", "1_Detection.py")
        at = AppTest.from_file(path)
        at.run(timeout=10)

        # Upload citra dummy valid
        img = Image.new("RGB", (64, 64), color=(50, 50, 50))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        at.file_uploader[0].upload("test.jpg", buf.getvalue(), "image/jpeg")
        at.run(timeout=10)

        # Verifikasi tombol analisis: "Analisis Pelanggaran" tanpa emoji kaca pembesar
        btn_labels = [b.label for b in at.button]
        self.assertIn("Analisis Pelanggaran", btn_labels)
        self.assertNotIn("🔍 Analisis Pelanggaran", btn_labels)

        # Jalankan aksi klik tombol analisis
        at.button[0].click()
        at.run(timeout=10)

        self.assertFalse(at.exception, f"Detection page raised exception: {at.exception}")

        # 1. Pastikan TIDAK ADA st.json di seluruh halaman (Tugas E)
        self.assertEqual(len(at.json), 0, "st.json harus 0 (Data Teknis Lapangan dihapus total)")

        # 2. Pastikan tidak ada expander berlabel 'Data Teknis' atau 'Raw JSON'
        for exp in at.expander:
            self.assertNotIn("Data Teknis", exp.label)
            self.assertNotIn("Raw JSON", exp.label)

        # 3. Pastikan metrik ringkasan tetap ada dan lengkap
        metric_labels = [m.label for m in at.metric]
        self.assertIn("Total Motor", metric_labels)
        self.assertIn("Total Orang", metric_labels)
        self.assertIn("Motor Aman", metric_labels)
        self.assertIn("Motor Pelanggaran", metric_labels)
        self.assertIn("Waktu Inferensi", metric_labels)

        # 4. Pastikan tombol unduh bebas emoji: "Unduh Gambar Anotasi (JPEG)"
        download_labels = [btn.label for btn in at.download_button]
        self.assertIn("Unduh Gambar Anotasi (JPEG)", download_labels)
        self.assertNotIn("📥 Unduh Gambar Anotasi (JPEG)", download_labels)

        # 5. Pastikan detail status sepeda motor tetap dirender
        markdown_texts = " ".join([m.value for m in at.markdown])
        self.assertIn("Sepeda Motor #1", markdown_texts)
        self.assertIn("Sepeda Motor #2", markdown_texts)

    @patch("dashboard.services.inference_client.InferenceClient.check_health")
    def test_dashboard_emojis_and_sidebar_order(self, mock_health):
        """Tugas A & B: Verifikasi pembersihan emoji pada Dashboard & urutan elemen sidebar."""
        mock_health.return_value = (True, {"status": "ok", "model": "YOLO26m", "model_loaded": True})

        path = os.path.join(DASHBOARD_DIR, "app.py")
        at = AppTest.from_file(path)
        at.run(timeout=10)
        self.assertFalse(at.exception, f"App raised exception: {at.exception}")

        # 1. Verifikasi teks status backend bebas emoji centang
        success_texts = [s.value for s in at.success]
        self.assertTrue(len(success_texts) > 0)
        self.assertIn("Backend Siap:", success_texts[0])
        self.assertNotIn("✅", success_texts[0])

        # 2. Verifikasi tombol CTA pembuka deteksi bebas emoji roket
        button_labels = [b.label for b in at.button]
        self.assertIn("Buka Halaman Deteksi", button_labels)
        self.assertNotIn("🚀 Buka Halaman Deteksi", button_labels)

        # 3. Verifikasi struktur sidebar: Urutan elemen di st.sidebar
        sidebar_items = [getattr(e, "value", getattr(e, "label", "")) for e in at.sidebar]
        sidebar_text = " ".join(sidebar_items)

        # Pastikan branding ada
        self.assertIn("gio-sidebar-brand", sidebar_text)
        self.assertIn("Motorcycle AI", sidebar_text)

        # Pastikan title navigasi tanpa panah ada
        self.assertIn("Menu Navigasi", sidebar_text)

        # Pastikan deskripsi ada di bagian bawah
        self.assertIn("gio-sidebar-desc", sidebar_text)
        self.assertIn("YOLO26m Passenger Violation Detector", sidebar_text)

        # Verifikasi urutan indeks: Brand muncul SEBELUM Navigasi, dan Navigasi SEBELUM Deskripsi
        idx_brand = sidebar_text.find("gio-sidebar-brand")
        idx_nav = sidebar_text.find("Menu Navigasi")
        idx_desc = sidebar_text.find("gio-sidebar-desc")

        self.assertGreater(idx_brand, -1)
        self.assertGreater(idx_nav, -1)
        self.assertGreater(idx_desc, -1)
        self.assertLess(idx_brand, idx_nav, "Branding harus muncul sebelum Menu Navigasi")
        self.assertLess(idx_nav, idx_desc, "Menu Navigasi harus muncul sebelum Deskripsi produk")

    def test_custom_css_rules(self):
        """Tugas D: Verifikasi aturan CSS untuk spacing konten dan struktur sidebar flexbox."""
        from dashboard.components.ui import inject_custom_css
        import inspect

        src = inspect.getsource(inject_custom_css)

        # Verifikasi pengurangan padding-top konten utama (Tugas D - judul aman tanpa terpotong)
        self.assertIn("padding-top: 2.75rem !important;", src)
        self.assertIn(".block-container", src)

        # Verifikasi flexbox pada stSidebarUserContent
        self.assertIn("stSidebarUserContent", src)
        self.assertIn("flex-direction: column !important;", src)

        # Verifikasi deskripsi produk di dasar sidebar via margin-top: auto
        self.assertIn("gio-sidebar-desc", src)
        self.assertIn("margin-top: auto !important;", src)

        # Verifikasi penataan header branding sejajar dengan tombol collapse
        self.assertIn('data-testid="stSidebarHeader"', src)
        self.assertIn("position: absolute !important;", src)
        self.assertIn(".gio-sidebar-brand", src)
        self.assertIn("padding: 0 2.5rem 0 0 !important;", src)


if __name__ == "__main__":
    unittest.main()
