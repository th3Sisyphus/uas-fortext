"""
Tugas Pemrograman Akhir Forensic Text (IT9443) - Tugas A
Deteksi Duplikat / Hampir Duplikat dengan SimHash

NIM  : ........ (isi)
Nama : ........ (isi)

Cara menjalankan:
    python app.py
Browser akan terbuka otomatis di http://localhost:8000
(Jika tidak terbuka, buka alamat itu secara manual. Tutup program dengan Ctrl+C.)

Hanya memakai library bawaan Python (tanpa pip install).
"""

import hashlib
import json
import os
import re
import webbrowser
from collections import Counter
from http.server import BaseHTTPRequestHandler, HTTPServer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PORT = 8000


# =====================================================================
# BAGIAN 1 - PRA-PEMROSESAN TEKS (langkah 4 s.d. 6 di panduan)
# =====================================================================

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


# =====================================================================
# BAGIAN 2 - PEMBENTUKAN FINGERPRINT SIMHASH (langkah 7 s.d. 11)
# =====================================================================

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


# =====================================================================
# BAGIAN 3 - JARAK HAMMING (langkah 12 s.d. 15)
# =====================================================================

def hamming(x, y):
    """Langkah 12-13: XOR lalu hitung jumlah bit 1."""
    return bin(x ^ y).count("1")


def geser_kanan(x, n, b):
    """
    Langkah 14: geser bit ke kanan sebanyak n posisi.
    Bit yang keluar di kanan dimasukkan lagi di kiri (rotasi),
    supaya tidak ada bit yang hilang.
    """
    mask = (1 << b) - 1
    return ((x >> n) | (x << (b - n))) & mask


def bin_str(x, b):
    return format(x, "0{}b".format(b))


def cari_kandidat_urut(dok_a, dok_b, b, ambang, daftar_geser):
    """
    Langkah 14-15: untuk tiap nilai geseran,
      1) geser semua fingerprint (dokumen A dan B),
      2) urutkan dari nilai desimal kecil ke besar,
      3) hitung Hamming antara kalimat yang bertetangga
         (tetangga yang berasal dari dokumen berbeda).
    Fingerprint yang mirip akan berdekatan setelah diurutkan,
    jadi pasangan mirip bisa ditemukan tanpa membandingkan semua pasangan.
    """
    hasil = []
    for n in daftar_geser:
        item = [(geser_kanan(k["fp"], n, b), "A", k["id"]) for k in dok_a]
        item += [(geser_kanan(k["fp"], n, b), "B", k["id"]) for k in dok_b]
        item.sort(key=lambda t: t[0])            # urut berdasarkan desimal

        for i in range(len(item) - 1):
            x, y = item[i], item[i + 1]
            if x[1] != y[1]:                     # harus beda dokumen
                jarak = hamming(x[0], y[0])
                if jarak <= ambang:
                    a, bb = (x, y) if x[1] == "A" else (y, x)
                    hasil.append({"geser": n, "id_a": a[2], "id_b": bb[2],
                                  "jarak": jarak})
    return hasil


# =====================================================================
# BAGIAN 4 - PERBANDINGAN DOKUMEN (langkah 12, 16, 17)
# =====================================================================

def bandingkan(teks_a, teks_b, b=64, ambang=10, ambang_min=3,
               batas_duplikat=80, batas_hampir=30):
    dok_a = proses_dokumen(teks_a, b)
    dok_b = proses_dokumen(teks_b, b)
    if not dok_a or not dok_b:
        return {"error": "Salah satu dokumen kosong / tidak punya kalimat."}

    # Langkah 12: Hamming semua pasangan kalimat A x B
    pasangan = []
    terbaik_a = {}   # id kalimat A -> jarak terkecil ke kalimat B mana pun
    terbaik_b = {}
    for ka in dok_a:
        for kb in dok_b:
            j = hamming(ka["fp"], kb["fp"])
            pasangan.append({"id_a": ka["id"], "id_b": kb["id"], "jarak": j})
            terbaik_a[ka["id"]] = min(terbaik_a.get(ka["id"], b), j)
            terbaik_b[kb["id"]] = min(terbaik_b.get(kb["id"], b), j)

    # Langkah 16: pasangan dengan jarak < ambang dianggap mirip
    mirip = sorted([p for p in pasangan if p["jarak"] < ambang],
                   key=lambda p: p["jarak"])
    sama_a = sum(1 for j in terbaik_a.values() if j < ambang)
    sama_b = sum(1 for j in terbaik_b.values() if j < ambang)
    persen_mirip = 100.0 * (sama_a + sama_b) / (len(dok_a) + len(dok_b))

    if persen_mirip >= batas_duplikat:
        status = "DUPLIKAT"
    elif persen_mirip >= batas_hampir:
        status = "HAMPIR DUPLIKAT"
    else:
        status = "TIDAK DUPLIKAT"

    # Langkah 17: persentase kalimat dengan jarak Hamming sangat minimal
    min_a = sum(1 for j in terbaik_a.values() if j <= ambang_min)
    min_b = sum(1 for j in terbaik_b.values() if j <= ambang_min)
    persen_min = 100.0 * (min_a + min_b) / (len(dok_a) + len(dok_b))

    # Langkah 14-15: geser kanan 2 bit, urutkan, hitung ulang Hamming
    kandidat = cari_kandidat_urut(dok_a, dok_b, b, ambang, [0, 2, 4])

    def tampil(dok):
        return [{"id": k["id"], "teks": k["teks"], "desimal": str(k["fp"]),
                 "biner": bin_str(k["fp"], b)} for k in dok]

    return {
        "status": status,
        "persen_mirip": round(persen_mirip, 2),
        "persen_minimal": round(persen_min, 2),
        "jumlah_kalimat_a": len(dok_a),
        "jumlah_kalimat_b": len(dok_b),
        "pasangan_mirip": mirip,
        "kandidat_urut": kandidat,
        "kalimat_a": tampil(dok_a),
        "kalimat_b": tampil(dok_b),
        "parameter": {"b": b, "ambang": ambang, "ambang_min": ambang_min},
    }


def bandingkan_banyak(dokumen, b=64, ambang=10, ambang_min=3):
    """
    Membandingkan sejumlah dokumen (minimal 2).
    Setiap pasangan dokumen (1-2, 1-3, 2-3, dst.) dibandingkan
    dengan fungsi bandingkan() di atas.
    dokumen: list berisi {"nama": ..., "teks": ...}
    """
    if len(dokumen) < 2:
        return {"error": "Minimal harus ada 2 dokumen."}
    hasil = []
    for i in range(len(dokumen)):
        for j in range(i + 1, len(dokumen)):
            r = bandingkan(dokumen[i]["teks"], dokumen[j]["teks"],
                           b, ambang, ambang_min)
            r["nama_a"] = dokumen[i]["nama"]
            r["nama_b"] = dokumen[j]["nama"]
            hasil.append(r)
    return {"hasil": hasil}


# =====================================================================
# BAGIAN 5 - SERVER WEB SEDERHANA (penghubung Python <-> index.html)
# =====================================================================

class Handler(BaseHTTPRequestHandler):

    def _kirim(self, kode, isi, tipe="application/json; charset=utf-8"):
        data = isi if isinstance(isi, bytes) else isi.encode("utf-8")
        self.send_response(kode)
        self.send_header("Content-Type", tipe)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        # Halaman utama
        if self.path in ("/", "/index.html"):
            with open(os.path.join(BASE_DIR, "index.html"), "rb") as f:
                self._kirim(200, f.read(), "text/html; charset=utf-8")

        else:
            self._kirim(404, json.dumps({"error": "Tidak ditemukan"}))

    def do_POST(self):
        if self.path != "/bandingkan":
            self._kirim(404, json.dumps({"error": "Tidak ditemukan"}))
            return
        try:
            panjang = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(panjang).decode("utf-8"))
            hasil = bandingkan_banyak(
                data.get("dokumen", []),
                b=int(data.get("b", 64)),
                ambang=int(data.get("ambang", 10)),
                ambang_min=int(data.get("ambang_min", 3)),
            )
            self._kirim(200, json.dumps(hasil))
        except Exception as e:
            self._kirim(400, json.dumps({"error": str(e)}))


if __name__ == "__main__":
    server = HTTPServer(("localhost", PORT), Handler)
    alamat = "http://localhost:{}".format(PORT)
    print("Program berjalan di", alamat, "(tekan Ctrl+C untuk berhenti)")
    webbrowser.open(alamat)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nProgram dihentikan.")
