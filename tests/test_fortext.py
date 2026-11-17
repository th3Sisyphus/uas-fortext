"""Tes inti SimHash. Jalankan: python -m unittest discover -s tests -v"""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from fortext import bandingkan, bandingkan_banyak  # noqa: E402
from fortext.fingerprint import fingerprint_kalimat  # noqa: E402
from fortext.hamming import geser_kanan, hamming  # noqa: E402
from fortext.preprocessing import segmentasi_kalimat, tokenisasi  # noqa: E402


def baca(n):
    return (ROOT / "contoh" / "contoh{}.txt".format(n)).read_text(encoding="utf-8")


class TesPraProses(unittest.TestCase):
    def test_segmentasi(self):
        k = segmentasi_kalimat("Satu. Dua!\nTiga?")
        self.assertEqual([x["teks"] for x in k], ["Satu.", "Dua!", "Tiga?"])
        self.assertEqual([x["id"] for x in k], [1, 2, 3])

    def test_tokenisasi(self):
        self.assertEqual(tokenisasi("halo, dunia 2"), ["halo", "dunia", "2"])


class TesHamming(unittest.TestCase):
    def test_hamming(self):
        self.assertEqual(hamming(0b1010, 0b0110), 2)

    def test_geser_rotasi(self):
        self.assertEqual(geser_kanan(0b0001, 1, 4), 0b1000)

    def test_fingerprint_stabil(self):
        self.assertEqual(fingerprint_kalimat("a b c", 64), fingerprint_kalimat("a b c", 64))
        self.assertIsNone(fingerprint_kalimat("!!!", 64))


class TesPerbandingan(unittest.TestCase):
    def test_identik_duplikat(self):
        self.assertEqual(bandingkan(baca(1), baca(1))["status"], "DUPLIKAT")

    def test_contoh1_contoh2_hampir_duplikat(self):
        self.assertEqual(bandingkan(baca(1), baca(2))["status"], "HAMPIR DUPLIKAT")

    def test_contoh1_contoh3_tidak_duplikat(self):
        self.assertEqual(bandingkan(baca(1), baca(3))["status"], "TIDAK DUPLIKAT")

    def test_banyak_dokumen_semua_pasangan(self):
        d = [{"nama": str(i), "teks": baca(i)} for i in (1, 2, 3)]
        self.assertEqual(len(bandingkan_banyak(d)["hasil"]), 3)

    def test_error(self):
        self.assertIn("error", bandingkan_banyak([{"nama": "x", "teks": "a."}]))
        d = [{"nama": "ok", "teks": baca(1)}, {"nama": "kosong", "teks": "  "}]
        self.assertIn("kosong", bandingkan_banyak(d)["error"])


if __name__ == "__main__":
    unittest.main()
