"""Pembuat HTML untuk tabel dan lencana hasil perbandingan."""

import html
from pathlib import Path

import streamlit as st

CSS_PATH = Path(__file__).with_name("styles.css")

KELAS_STATUS = {
    "DUPLIKAT": "ft-duplikat",
    "HAMPIR DUPLIKAT": "ft-hampir",
    "TIDAK DUPLIKAT": "ft-tidak",
}
IKON_STATUS = {"DUPLIKAT": "🔴", "HAMPIR DUPLIKAT": "🟠", "TIDAK DUPLIKAT": "🟢"}


def muat_css():
    """Sisipkan styles.css ke halaman."""
    css = CSS_PATH.read_text(encoding="utf-8")
    st.markdown("<style>" + css + "</style>", unsafe_allow_html=True)


def esc(s):
    return html.escape(str(s))


def lencana(status):
    return '<span class="ft-badge {}">{}</span>'.format(KELAS_STATUS[status], esc(status))


def tabel(kepala, baris):
    """Tabel HTML. Sel sudah harus berupa HTML aman (gunakan esc() untuk teks)."""
    if not baris:
        return '<p class="ft-note">Tidak ada data.</p>'
    th = "".join("<th>{}</th>".format(k) for k in kepala)
    tr = "".join("<tr>" + "".join("<td>{}</td>".format(c) for c in r) + "</tr>"
                 for r in baris)
    return ('<div class="ft-scroll"><table class="ft-tabel"><tr>' + th + "</tr>"
            + tr + "</table></div>")


def _potong_lingkaran(cx, cy, r, tebal, mulai, porsi):
    """Satu irisan donat sebagai elemen <path> SVG.

    mulai/porsi dalam satuan 1/1 penuh (0..1), mulai dari jam 12 dan searah jarum.
    """
    if porsi <= 0:
        return ""
    akhir = mulai + porsi
    if porsi >= 0.9999:  # lingkaran penuh: busur tidak boleh berimpit
        akhir = 0.9999
    besar = 1 if porsi > 0.5 else 0

    def titik(u):
        import math
        sudut = (u - 0.25) * 2 * math.pi
        return (cx + r * math.cos(sudut), cy + r * math.sin(sudut))

    luar_mulai = titik(mulai)
    luar_akhir = titik(akhir)
    dalam_akhir = titik(akhir)
    d = ("M {:.2f} {:.2f} A {:.2f} {:.2f} 0 {} 1 {:.2f} {:.2f} L {:.2f} {:.2f} "
         "A {:.2f} {:.2f} 0 {} 0 {:.2f} {:.2f} Z").format(
        luar_mulai[0], luar_mulai[1], r, r, besar, luar_akhir[0], luar_akhir[1],
        dalam_akhir[0], dalam_akhir[1], r - tebal, r - tebal, besar,
        luar_mulai[0], luar_mulai[1])
    return '<path d="{}"></path>'.format(d)


def diagram_lingkaran(hasil):
    """Diagram lingkaran (donat) komposisi status pasangan dokumen."""
    hitung = {"DUPLIKAT": 0, "HAMPIR DUPLIKAT": 0, "TIDAK DUPLIKAT": 0}
    total = 0
    for r in hasil:
        if "error" in r:
            continue
        hitung[r["status"]] = hitung.get(r["status"], 0) + 1
        total += 1
    if not total:
        return ""

    urutan = ["DUPLIKAT", "HAMPIR DUPLIKAT", "TIDAK DUPLIKAT"]
    warna = {"DUPLIKAT": "var(--ft-bad)", "HAMPIR DUPLIKAT": "var(--ft-warn)",
             "TIDAK DUPLIKAT": "var(--ft-ok)"}

    segmen = {s: hitung[s] for s in urutan if hitung[s]}
    if len(segmen) == 1:
        status_tunggal = next(iter(segmen))
        isi = ('<circle cx="90" cy="90" r="70" fill="none" stroke="{}" '
               'stroke-width="34"></circle>').format(warna[status_tunggal])
    else:
        irisan = []
        mulai = 0.0
        for s in urutan:
            if not hitung[s]:
                continue
            porsi = hitung[s] / float(total)
            potong = _potong_lingkaran(90, 90, 70, 34, mulai, porsi)
            if potong:
                irisan.append(potong.replace(">", ' style="fill:{}">'.format(warna[s]), 1))
            mulai += porsi
        isi = "".join(irisan)

    legenda = "".join(
        '<li><span class="ft-kotak" style="background:{}"></span>'
        "<span class=\"ft-legenda-teks\">{}</span>"
        '<span class="ft-legenda-angka">{} ({}%)</span></li>'.format(
            warna[s], esc(s), hitung[s], round(100.0 * hitung[s] / total, 1))
        for s in urutan)

    return (
        '<div class="ft-diagram">'
        '<svg viewBox="0 0 180 180" role="img" '
        'aria-label="Komposisi status {} pasangan dokumen">{}'
        '<text class="ft-diagram-angka" x="90" y="86">{}</text>'
        '<text class="ft-diagram-label" x="90" y="104">pasangan</text>'
        "</svg>"
        '<ul class="ft-legenda">{}</ul>'
        "</div>".format(total, isi, total, legenda)
    )


def tabel_ringkasan(hasil):
    baris = []
    for r in hasil:
        pasangan = esc(r["nama_a"]) + " – " + esc(r["nama_b"])
        if "error" in r:
            baris.append([pasangan, '<span class="ft-err">{}</span>'.format(esc(r["error"])),
                          "-", "-"])
        else:
            baris.append([pasangan, lencana(r["status"]),
                          "{}%".format(r["persen_mirip"]),
                          "{}%".format(r["persen_minimal"])])
    return tabel(["Pasangan dokumen", "Status",
                  "Kalimat mirip (jarak &lt; ambang)", "Kemiripan sangat minimal"], baris)


def _kalimat(teks_per_id, id_):
    return "#{} {}".format(id_, esc(teks_per_id[id_]))


def rincian_pasangan(r):
    """Kembalikan tiga potongan HTML: pasangan mirip, kandidat urut, fingerprint."""
    t_a = {k["id"]: k["teks"] for k in r["kalimat_a"]}
    t_b = {k["id"]: k["teks"] for k in r["kalimat_b"]}

    mirip = tabel(
        ["Jarak", "Kalimat A", "Kalimat B"],
        [[p["jarak"], _kalimat(t_a, p["id_a"]), _kalimat(t_b, p["id_b"])]
         for p in r["pasangan_mirip"]])

    kandidat = tabel(
        ["Geser", "Jarak", "Kalimat A", "Kalimat B"],
        [[p["geser"], p["jarak"], _kalimat(t_a, p["id_a"]), _kalimat(t_b, p["id_b"])]
         for p in r["kandidat_urut"]])

    fp = []
    for kode, daftar in (("A", r["kalimat_a"]), ("B", r["kalimat_b"])):
        for k in daftar:
            fp.append([kode, k["id"], esc(k["teks"]), k["desimal"],
                       '<span class="ft-mono">{}</span>'.format(k["biner"])])
    fingerprint = tabel(["Dok", "ID", "Kalimat", "Desimal", "Biner"], fp)
    return mirip, kandidat, fingerprint
