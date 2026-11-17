"""
BAGIAN 2 - PEMBENTUKAN FINGERPRINT SIMHASH (langkah 7 s.d. 11)
"""

import hashlib
from collections import Counter

from .preprocessing import normalisasi, segmentasi_kalimat, tokenisasi


def hash_token(token, b):
    """
    Langkah 7: ubah token menjadi bilangan desimal (hash) lalu
    potong menjadi b bit. Dipakai MD5 agar hasilnya selalu sama
    setiap program dijalankan (hash() bawaan Python berubah-ubah).
    """
    nilai = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
    return nilai % (2 ** b)


def fingerprint_kalimat(kalimat, b):
    """
    Langkah 8 s.d. 11: membuat fingerprint b bit untuk satu kalimat.
      - hitung tf tiap token (bobot)
      - vektor v (b komponen), awalnya 0 semua
      - bit hash = 1 -> v[i] += tf ; bit hash = 0 -> v[i] -= tf
      - fingerprint: v[i] > 0 jadi 1, selain itu (<= 0) jadi 0
    Mengembalikan (fingerprint dalam bentuk integer, None jika kalimat kosong).
    """
    token = tokenisasi(kalimat)
    if not token:
        return None

    tf = Counter(token)            # langkah 8: frekuensi term
    v = [0] * b                    # langkah 9: vektor berdimensi b

    for kata, bobot in tf.items():
        h = hash_token(kata, b)
        for i in range(b):
            bit = (h >> (b - 1 - i)) & 1   # bit ke-i dari kiri
            if bit == 1:
                v[i] += bobot              # langkah 10: tambah
            else:
                v[i] -= bobot              # langkah 10: kurang

    fp = 0
    for i in range(b):                     # langkah 11: vektor -> bit
        fp = (fp << 1) | (1 if v[i] > 0 else 0)
    return fp


def proses_dokumen(teks, b):
    """Jalankan normalisasi -> segmentasi -> fingerprint untuk satu dokumen."""
    teks = normalisasi(teks)
    hasil = []
    for k in segmentasi_kalimat(teks):
        fp = fingerprint_kalimat(k["teks"], b)
        if fp is not None:
            k["fp"] = fp
            hasil.append(k)
    return hasil
