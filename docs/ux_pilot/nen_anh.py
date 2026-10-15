# -*- coding: utf-8 -*-
"""Nén ảnh chụp của vòng thử người dùng mới trước khi đưa vào kho: PNG đầy màu -> PNG bảng 128 màu
(ảnh giao diện chỉ có vài chục màu, nhỏ đi khoảng ba lần mà chữ vẫn đọc được).

    python docs/ux_pilot/nen_anh.py <thư mục chứa nhan_su/ và su_kien/> <thư mục đích>

Chép luôn các tệp .txt (chữ nhìn thấy trên từng màn) và ghi_chu_may.json cạnh ảnh.
"""
import glob
import os
import shutil
import sys

from PIL import Image


def nen(nguon, dich):
    for nguoi in ("nhan_su", "su_kien"):
        os.makedirs(os.path.join(dich, nguoi), exist_ok=True)
        for t in sorted(glob.glob(os.path.join(nguon, nguoi, "*"))):
            ra = os.path.join(dich, nguoi, os.path.basename(t))
            if t.endswith(".png"):
                Image.open(t).convert("RGB").quantize(
                    colors=128, method=Image.MEDIANCUT, dither=Image.NONE).save(ra, optimize=True)
            else:
                shutil.copy(t, ra)


if __name__ == "__main__":
    nen(sys.argv[1], sys.argv[2])
