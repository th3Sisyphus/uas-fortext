"""Pengelolaan daftar dokumen di st.session_state."""

from pathlib import Path

import streamlit as st

DIR_CONTOH = Path(__file__).resolve().parent.parent / "contoh"


def init():
    if "docs" not in st.session_state:
        st.session_state.docs = []     # [{"id": int, "nama": str}]
        st.session_state.next_id = 1
        tambah()
        tambah()


def tambah(nama=None, teks=""):
    i = st.session_state.next_id
    st.session_state.next_id += 1
    st.session_state.docs.append({"id": i, "nama": nama or "Dokumen {}".format(i)})
    st.session_state["teks_{}".format(i)] = teks


def hapus(doc_id):
    if len(st.session_state.docs) <= 2:
        st.session_state.pesan = "Minimal harus ada 2 dokumen."
        return
    st.session_state.pesan = ""
    st.session_state.docs = [d for d in st.session_state.docs if d["id"] != doc_id]
    st.session_state.pop("teks_{}".format(doc_id), None)
    st.session_state.pop("berkas_{}".format(doc_id), None)


def muat_berkas(doc_id):
    """Callback file_uploader: isi textarea dengan isi berkas, nama dokumen = nama berkas."""
    f = st.session_state.get("berkas_{}".format(doc_id))
    if f is None:
        return
    st.session_state["teks_{}".format(doc_id)] = f.getvalue().decode("utf-8", errors="replace")
    for d in st.session_state.docs:
        if d["id"] == doc_id:
            d["nama"] = f.name


def muat_contoh():
    """Ganti semua dokumen dengan berkas di folder contoh/."""
    for d in st.session_state.docs:
        st.session_state.pop("teks_{}".format(d["id"]), None)
        st.session_state.pop("berkas_{}".format(d["id"]), None)
    st.session_state.docs = []
    for p in sorted(DIR_CONTOH.glob("*.txt")):
        tambah(p.name, p.read_text(encoding="utf-8"))
    st.session_state.pesan = ""
    st.session_state.pop("hasil", None)
