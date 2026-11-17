"""
Tugas Pemrograman Akhir Forensic Text (IT9443) - Tugas A
Deteksi Duplikat / Hampir Duplikat dengan SimHash

NIM  : ........ (isi)
Nama : ........ (isi)

Cara menjalankan:
    pip install -r requirements.txt
    streamlit run app.py
Browser akan terbuka otomatis di http://localhost:8501
"""

import streamlit as st

from fortext import bandingkan_banyak
from ui import state
from ui.components import (IKON_STATUS, diagram_lingkaran, esc, muat_css,
                           rincian_pasangan, tabel_ringkasan)

st.set_page_config(page_title="Deteksi Duplikat dengan SimHash", page_icon="🔎",
                   layout="wide")
muat_css()
state.init()

st.markdown(
    '<div class="ft-judul">Deteksi Duplikat dan Hampir Duplikat</div>'
    '<p class="ft-sub">Bandingkan dokumen dengan SimHash. Unggah berkas .txt, '
    "atau tempel teks langsung.</p>",
    unsafe_allow_html=True,
)

# ---------- Kartu dokumen ----------
docs = st.session_state.docs
for baris in range(0, len(docs), 2):
    kolom = st.columns(2)
    for kol, d in zip(kolom, docs[baris:baris + 2]):
        with kol, st.container(border=True):
            kepala, tombol = st.columns([4, 1])
            kepala.subheader(d["nama"])
            tombol.button("Hapus", key="hapus_{}".format(d["id"]),
                          on_click=state.hapus, args=(d["id"],),
                          use_container_width=True)
            st.file_uploader("Unggah " + d["nama"], type=["txt"],
                             key="berkas_{}".format(d["id"]),
                             on_change=state.muat_berkas, args=(d["id"],),
                             label_visibility="collapsed")
            st.text_area("Teks " + d["nama"], key="teks_{}".format(d["id"]),
                         height=170, label_visibility="collapsed")

with st.container(border=True):
    kiri, kanan = st.columns([1, 1])
    kiri.button("Tambah dokumen", on_click=state.tambah)
    kanan.button("Muat contoh", on_click=state.muat_contoh,
                 help="Ganti semua dokumen dengan berkas di folder contoh/")
    st.markdown('<p class="ft-note">Semua dokumen dibandingkan berpasangan '
                "(A–B, A–C, B–C, dan seterusnya).</p>", unsafe_allow_html=True)

# ---------- Parameter ----------
with st.container(border=True):
    c1, c2, c3, c4 = st.columns([1, 1, 1, 1], vertical_alignment="bottom")
    b = c1.number_input("Jumlah bit (b)", 8, 128, 64)
    ambang = c2.number_input("Ambang jarak Hamming", 1, 64, 10)
    ambang_min = c3.number_input('Ambang "sangat minimal"', 0, 64, 3)
    jalankan = c4.button("Bandingkan dokumen", type="primary",
                         use_container_width=True)
    if st.session_state.get("pesan"):
        st.markdown('<p class="ft-err">{}</p>'.format(esc(st.session_state.pesan)),
                    unsafe_allow_html=True)

if jalankan:
    st.session_state.pesan = ""
    dokumen = [{"nama": d["nama"], "teks": st.session_state["teks_{}".format(d["id"])]}
               for d in st.session_state.docs]
    st.session_state.hasil = bandingkan_banyak(dokumen, int(b), int(ambang),
                                               int(ambang_min))

# ---------- Hasil ----------
hasil = st.session_state.get("hasil")
if hasil:
    if "error" in hasil:
        st.error(hasil["error"])
    else:
        with st.container(border=True):
            st.subheader("Ringkasan perbandingan")
            st.markdown(diagram_lingkaran(hasil["hasil"]), unsafe_allow_html=True)
            st.markdown(tabel_ringkasan(hasil["hasil"]), unsafe_allow_html=True)

        st.subheader("Rincian tiap pasangan")
        for r in hasil["hasil"]:
            if "error" in r:
                continue
            judul = "{} {} – {} ({})".format(IKON_STATUS[r["status"]], r["nama_a"],
                                            r["nama_b"], r["status"])
            with st.expander(judul):
                mirip, kandidat, fingerprint = rincian_pasangan(r)
                st.markdown('<div class="ft-h3">Pasangan kalimat mirip (A = {}, B = {})'
                            "</div>".format(esc(r["nama_a"]), esc(r["nama_b"])) + mirip,
                            unsafe_allow_html=True)
                st.markdown('<div class="ft-h3">Kandidat setelah geser kanan dan '
                            "pengurutan</div>"
                            '<p class="ft-note">Fingerprint digeser ke kanan 0, 2, dan 4 '
                            "bit, diurutkan menurut nilai desimal, lalu kalimat yang "
                            "bertetangga dihitung jarak Hamming-nya.</p>" + kandidat,
                            unsafe_allow_html=True)
                st.markdown('<div class="ft-h3">Fingerprint tiap kalimat</div>'
                            + fingerprint, unsafe_allow_html=True)
