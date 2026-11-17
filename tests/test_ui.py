"""Tes UI Streamlit (AppTest). Jalankan: python -m unittest discover -s tests -v"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from streamlit.testing.v1 import AppTest  # noqa: E402


def app():
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30)
    at.run()
    return at


def tombol(at, label):
    return next(b for b in at.button if b.label == label)


class TesUI(unittest.TestCase):
    def test_render_awal_dua_dokumen(self):
        at = app()
        self.assertFalse(at.exception)
        self.assertEqual(len(at.text_area), 2)

    def test_tambah_dan_hapus(self):
        at = app()
        tombol(at, "Tambah dokumen").click().run()
        self.assertEqual(len(at.text_area), 3)
        tombol(at, "Hapus").click().run()
        self.assertEqual(len(at.text_area), 2)
        tombol(at, "Hapus").click().run()          # tidak boleh di bawah 2
        self.assertEqual(len(at.text_area), 2)
        self.assertTrue(any("Minimal harus ada 2 dokumen." in m.value for m in at.markdown))

    def test_dokumen_kosong_error(self):
        at = app()
        tombol(at, "Bandingkan dokumen").click().run()
        self.assertEqual(len(at.error), 1)
        self.assertIn("Dokumen kosong", at.error[0].value)

    def test_muat_contoh_lalu_bandingkan(self):
        at = app()
        tombol(at, "Muat contoh").click().run()
        self.assertEqual(len(at.text_area), 3)
        tombol(at, "Bandingkan dokumen").click().run()
        self.assertFalse(at.exception)
        self.assertEqual(len(at.expander), 3)
        isi = " ".join(m.value for m in at.markdown)
        self.assertIn("HAMPIR DUPLIKAT", isi)
        self.assertIn("TIDAK DUPLIKAT", isi)


if __name__ == "__main__":
    unittest.main()
