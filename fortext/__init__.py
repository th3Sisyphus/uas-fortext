"""Paket inti deteksi duplikat / hampir duplikat dengan SimHash (tanpa dependensi luar)."""

from .comparison import bandingkan, bandingkan_banyak

__all__ = ["bandingkan", "bandingkan_banyak"]
