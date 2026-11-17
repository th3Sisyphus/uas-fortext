# uas-fortext

Tugas Pemrograman Akhir **Forensic Text (IT9443) – Tugas A**: deteksi duplikat dan hampir duplikat antar dokumen teks menggunakan **SimHash** dan jarak Hamming. Antarmuka dibuat dengan **Streamlit**, dengan HTML dan CSS khusus untuk tabel dan lencana status.

## Fitur

- Unggah berkas `.txt` atau tempel teks langsung, dengan jumlah dokumen bebas (minimal 2).
- Semua dokumen dibandingkan berpasangan (A–B, A–C, B–C, dan seterusnya).
- Parameter dapat diubah: jumlah bit `b`, ambang jarak Hamming, dan ambang "sangat minimal".
- Hasil berupa ringkasan status (**DUPLIKAT**, **HAMPIR DUPLIKAT**, **TIDAK DUPLIKAT**) dan rincian tiap pasangan: kalimat mirip, kandidat setelah geser kanan dan pengurutan, serta fingerprint desimal dan biner tiap kalimat.
- Tombol **Muat contoh** mengisi dokumen dari folder `contoh/`.

## Struktur folder

```
uas-fortext/
├── app.py               # titik masuk Streamlit (susunan halaman)
├── requirements.txt     # dependensi (hanya streamlit)
├── fortext/             # logika SimHash, murni Python tanpa library luar
│   ├── preprocessing.py #   langkah 4-6: normalisasi, segmentasi kalimat, tokenisasi
│   ├── fingerprint.py   #   langkah 7-11: hash token, vektor berbobot, fingerprint
│   ├── hamming.py       #   langkah 12-15: jarak Hamming, geser kanan, kandidat urut
│   └── comparison.py    #   langkah 12, 16, 17: perbandingan dua atau banyak dokumen
├── ui/                  # lapisan antarmuka
│   ├── components.py    #   pembuat HTML tabel dan lencana
│   ├── state.py         #   pengelolaan daftar dokumen di session_state
│   └── styles.css       #   CSS khusus, mengikuti tema terang/gelap Streamlit
├── contoh/              # contoh1.txt, contoh2.txt, contoh3.txt
├── tests/               # tes logika inti dan tes UI
└── BACA.txt
```

Logika di `fortext/` tidak bergantung pada Streamlit, sehingga bisa diuji dan dipakai ulang secara terpisah.

## Cara menjalankan

Butuh Python 3.9 atau lebih baru.

```bash
pip install -r requirements.txt
streamlit run app.py
```

Browser akan terbuka di <http://localhost:8501>. Tutup program dengan `Ctrl+C`.

## Cara kerja singkat

1. Teks diubah menjadi huruf kecil, dipecah menjadi kalimat (pemisah `.`, `!`, `?` yang diikuti spasi, atau baris baru), lalu tiap kalimat dipecah menjadi kata (unigram).
2. Tiap kata di-hash dengan MD5 dan dipotong menjadi `b` bit. Memakai MD5 agar hasilnya sama setiap program dijalankan, karena `hash()` bawaan Python berubah-ubah.
3. Untuk tiap kalimat dibuat vektor `b` komponen: bit hash `1` menambah bobot (frekuensi kata), bit `0` mengurangi. Komponen bernilai positif menjadi bit `1`, selain itu `0`. Hasilnya adalah fingerprint kalimat.
4. Semua pasangan kalimat dari dua dokumen dibandingkan dengan jarak Hamming (XOR lalu hitung bit `1`). Pasangan dengan jarak di bawah ambang dianggap mirip.
5. Status ditentukan dari persentase kalimat yang mirip: **DUPLIKAT** jika minimal 80%, **HAMPIR DUPLIKAT** jika minimal 30%, selain itu **TIDAK DUPLIKAT**.
6. Sebagai pembanding, fingerprint digeser ke kanan 0, 2, dan 4 bit (dengan rotasi), diurutkan menurut nilai desimal, lalu kalimat yang bertetangga dihitung jarak Hamming-nya.

## Tes

```bash
python -m unittest discover -s tests -v
```

## Catatan

Lihat `BACA.txt`.
