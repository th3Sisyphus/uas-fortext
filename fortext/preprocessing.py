"""
BAGIAN 1 - PRA-PEMROSESAN TEKS (langkah 4 s.d. 6 di panduan)
"""

import re


def normalisasi(teks):
    """Langkah 4: ubah semua huruf menjadi huruf kecil."""
    return teks.lower()


def segmentasi_kalimat(teks):
    """
    Langkah 5: pecah teks menjadi kalimat dan beri id tiap kalimat.
    Pemisah kalimat: tanda . ! ? yang diikuti spasi, atau baris baru.
    """
    potongan = re.split(r"(?<=[.!?])\s+|\n+", teks)
    potongan = [p.strip() for p in potongan if p.strip()]
    return [{"id": i + 1, "teks": p} for i, p in enumerate(potongan)]


def tokenisasi(kalimat):
    """Langkah 6: shingle berukuran unigram = satu kata (token)."""
    return re.findall(r"\w+", kalimat)
