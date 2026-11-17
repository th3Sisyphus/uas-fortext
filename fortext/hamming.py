"""
BAGIAN 3 - JARAK HAMMING (langkah 12 s.d. 15)
"""


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
