"""
BAGIAN 4 - PERBANDINGAN DOKUMEN (langkah 12, 16, 17)
"""

from .fingerprint import proses_dokumen
from .hamming import bin_str, cari_kandidat_urut, hamming


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
    # Pastikan tiap dokumen punya isi; sebutkan nama dokumen yang kosong
    kosong = [d["nama"] for d in dokumen if not proses_dokumen(d["teks"], b)]
    if kosong:
        return {"error": "Dokumen kosong: " + ", ".join(kosong) +
                ". Isi teksnya atau hapus dokumen tersebut."}
    hasil = []
    for i in range(len(dokumen)):
        for j in range(i + 1, len(dokumen)):
            r = bandingkan(dokumen[i]["teks"], dokumen[j]["teks"],
                           b, ambang, ambang_min)
            r["nama_a"] = dokumen[i]["nama"]
            r["nama_b"] = dokumen[j]["nama"]
            hasil.append(r)
    return {"hasil": hasil}
