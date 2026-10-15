# -*- coding: utf-8 -*-
"""Bản .zip của hai skill phải chạy được một mình, ngoài kho mã, và ra đúng
như bản trong kho."""

import filecmp
import os
import subprocess
import sys
import zipfile

import pytest

pytest.importorskip("openpyxl")

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(GOC, "mau_forms_thi_clb"))

import dong_goi_skill  # noqa: E402


def test_zip_chay_ngoai_kho(tmp_path):
    zips = dong_goi_skill.dong_goi(str(tmp_path / "zip"))
    ngoai = tmp_path / "ngoai"
    for z in zips:
        with zipfile.ZipFile(z) as f:
            ten = os.path.basename(z)[:-4]
            assert all(n.startswith(ten + "/") for n in f.namelist())
            assert ten + "/SKILL.md" in f.namelist()
            f.extractall(str(ngoai))

    tf = str(ngoai / "tao-google-form-clb" / "scripts" / "tao_form.py")
    subprocess.run([sys.executable, tf, "mau", "--ra", str(ngoai / "m.xlsx")], check=True,
                   cwd=str(ngoai), capture_output=True)
    subprocess.run([sys.executable, tf, "tao", "--vao", str(ngoai / "m.xlsx"), "--ra", str(ngoai / "form")],
                   check=True, cwd=str(ngoai), capture_output=True)
    assert filecmp.cmp(str(ngoai / "form" / "TAO_GOOGLE_FORM.gs"),
                       os.path.join(GOC, "mau_forms_thi_clb", "TAO_GOOGLE_FORM.gs"), shallow=False)

    # Script trong .zip phải nạp các tệp đi kèm, không phải tệp trong kho.
    kiem = ("import runpy,sys; sys.argv=['x','--help']\n"
            "try: runpy.run_path(%r, run_name='x')\n"
            "except SystemExit: pass\n"
            "import sinh_du_lieu, tao_google_forms, so_nhap\n"
            "print(sinh_du_lieu.__file__); print(tao_google_forms.__file__); print(so_nhap.__file__)")
    out = subprocess.run([sys.executable, "-c", kiem % tf], check=True, cwd=str(ngoai),
                         capture_output=True, text=True, encoding="utf-8").stdout
    assert all(str(ngoai) in dong for dong in out.split())

    xr = str(ngoai / "xu-li-raw-forms" / "scripts" / "xu_li_raw.py")
    r = subprocess.run([sys.executable, xr, "--help"], cwd=str(ngoai), capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0 and "--raw" in r.stdout

    # Skill sinh dữ liệu (đi kèm trong .zip) phải GHI ĐƯỢC Sổ nhập CLB ở
    # ngoài kho — tức là so_nhap.py và i18n_errors.py đã được đóng gói theo.
    sdl = str(ngoai / "xu-li-raw-forms" / "scripts" / "sinh_du_lieu.py")
    r = subprocess.run([sys.executable, sdl, "ngau", "--ra", str(ngoai / "bo"), "--hoc-sinh", "15"],
                       cwd=str(ngoai), capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0, r.stderr
    assert os.path.isfile(str(ngoai / "bo" / "SO_NHAP_CLB.xlsx"))

    # …và ghi được sổ của WORKSPACE (nhãn, luật, điểm theo người) ngoài kho: --kich-ban cần
    # so_nhap.py, i18n_errors.py và nhan_ws.py đi kèm, và không được kéo cau_hinh_ws.py.
    assert not os.path.exists(str(ngoai / "xu-li-raw-forms" / "scripts" / "cau_hinh_ws.py"))
    for kich_ban, sheet in (("company", "2. Nhân viên"), ("event", "2. Khách tham dự")):
        ra = str(ngoai / ("bo_" + kich_ban))
        r = subprocess.run([sys.executable, sdl, "ngau", "--kich-ban", kich_ban, "--ra", ra,
                            "--hoc-sinh", "30", "--clb-moi-buoi", "4"],
                           cwd=str(ngoai), capture_output=True, text=True, encoding="utf-8")
        assert r.returncode == 0, r.stderr
        assert sorted(os.listdir(ra)) == ["SO_NHAP_CLB.xlsx", "config.json"]
        import openpyxl
        assert sheet in openpyxl.load_workbook(os.path.join(ra, "SO_NHAP_CLB.xlsx")).sheetnames
        r = subprocess.run([sys.executable, sdl, "soat", os.path.join(ra, "SO_NHAP_CLB.xlsx"),
                            "--cau-hinh", os.path.join(ra, "config.json")],
                           cwd=str(ngoai), capture_output=True, text=True, encoding="utf-8")
        assert r.returncode == 0, r.stderr
