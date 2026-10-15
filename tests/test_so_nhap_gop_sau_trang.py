# -*- coding: utf-8 -*-
"""Sổ nhập gộp sáu trang (cách chamTheoCLB ghi nay) phải nạp được vào phần mềm thật.

chamTheoCLB ghi MỘT tệp SO_NHAP_CLB.xlsx gồm sáu trang, đúng thứ tự:
1. CLB, 2. Học sinh, Bảng điểm, Cảnh báo, Raw, Đáp án.
Phần mềm chỉ được đọc hai trang đầu theo tên; bốn trang còn lại phải bị bỏ qua
mà không gây cảnh báo. Bài kiểm này nạp đúng tệp như vậy với 500 học sinh.
"""

import base64
import importlib.util
import os
import sys
import time

import pytest

openpyxl = pytest.importorskip("openpyxl")

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(GOC, ".claude", "skills", "xu-li-raw-forms", "scripts", "xu_li_raw.py")
sys.path.insert(0, GOC)
sys.path.insert(0, os.path.join(GOC, "mau_forms_thi_clb"))

from api import PipelineAPI  # noqa: E402
from test_skill_xu_li_raw import Raw, ghi_dap_an  # noqa: E402


@pytest.fixture(scope="module")
def xr():
    spec = importlib.util.spec_from_file_location("xu_li_raw", SCRIPT)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@pytest.fixture(scope="module")
def de():
    import tao_google_forms as tg
    return tg.du_lieu_gs()


def _ghi_clb_suc_chua_lon(de, duong, suc_chua):
    """Danh sách CLB với chỉ tiêu đủ lớn để 500 học sinh không bị báo quá tải."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["club_id", "name", "capacity", "reserve_capacity", "reserve_group", "buoi"])
    for d in de:
        for c in d["clubs"]:
            ws.append([c["id"], c["name"], suc_chua, 0, "", d["ma"]])
    wb.save(duong)


def _dung_500_hoc_sinh(xr, de, thu):
    """Raw Forms giả cho 500 học sinh, mỗi em chọn vài CLB và làm bài."""
    r = Raw(xr, de)
    T2 = [c["id"] for c in de[0]["clubs"]]
    T4 = [c["id"] for c in de[2]["clubs"]]
    for i in range(500):
        # Mỗi em tick đúng CLB mình làm bài, và làm được 1 hoặc 2 câu (không có điểm 0 giả).
        a = T2[i % len(T2)]
        buoi = {"thu_2": {"hang": [a], "tick": [a], "lam": {a: 1 + i % 2}}}
        if i % 2 == 0:
            b = T4[i % len(T4)]
            khac = [c for c in T4 if c != b]
            buoi["thu_4"] = {"hang": [b] + khac[: 2 + i % 3], "tick": [b], "lam": {b: 1 + i % 2}}
        r.phieu("HS%04d" % (i + 1), "Học sinh mẫu %d" % (i + 1), buoi,
                email="hs%d@truong.vn" % (i + 1))
    r.ghi(str(thu / "RAW_PHIEU.xlsx"))
    ghi_dap_an(de, str(thu / "DAP_AN.xlsx"))
    _ghi_clb_suc_chua_lon(de, str(thu / "01.xlsx"), 200)


def _ghep_sau_trang(thu, sheet_so_nhap):
    """Ghép đúng bố cục chamTheoCLB: 1. CLB, 2. Học sinh, Bảng điểm, Cảnh báo, Raw, Đáp án."""
    gop = openpyxl.Workbook()
    gop.remove(gop.active)
    nguon = openpyxl.load_workbook(sheet_so_nhap)
    for ten in ("1. CLB", "2. Học sinh"):
        ws = gop.create_sheet(ten)
        for dong in nguon[ten].iter_rows(values_only=True):
            ws.append(list(dong))
    bang = gop.create_sheet("Bảng điểm")
    bang.append(["Mã HS", "Họ tên"])
    for dong in nguon["2. Học sinh"].iter_rows(min_row=2, max_col=2, values_only=True):
        bang.append(list(dong))
    canh = gop.create_sheet("Cảnh báo")
    canh.append(["Phiếu", "Mã HS", "Nội dung"])
    canh.append(["", "", "Không có cảnh báo nào."])
    for ten, duong in (("Raw", thu / "RAW_PHIEU.xlsx"), ("Đáp án", thu / "DAP_AN.xlsx")):
        ws = gop.create_sheet(ten)
        for dong in openpyxl.load_workbook(str(duong)).active.iter_rows(values_only=True):
            ws.append(list(dong))
    duong = thu / "GOP_SO_NHAP_CLB.xlsx"
    gop.save(str(duong))
    return duong


@pytest.fixture(scope="module")
def gop(tmp_path_factory, xr, de):
    thu = tmp_path_factory.mktemp("gop500")
    _dung_500_hoc_sinh(xr, de, thu)
    ra = thu / "ra"
    assert xr.main(["--raw", str(thu / "RAW_PHIEU.xlsx"), "--dap-an", str(thu / "DAP_AN.xlsx"),
                    "--clb", str(thu / "01.xlsx"), "--ra", str(ra)]) == 0
    duong = _ghep_sau_trang(thu, str(ra / "SO_NHAP_CLB.xlsx"))
    return thu, duong


def test_so_nhap_sau_trang_nap_sach_500_hoc_sinh(gop):
    thu, duong = gop
    with open(str(duong), "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    api = PipelineAPI(str(thu / "app.db"), thu_muc_xuat=str(thu))

    xem = api.xem_truoc_so_nhap(b64)
    assert xem["ok"], xem
    assert xem["data"]["n_hoc_sinh"] == 500, xem["data"]

    t0 = time.time()
    kq = api.import_so_nhap(b64)
    giay = time.time() - t0
    assert kq["ok"] and not (kq["data"].get("warnings") or []), kq
    # Quy mô 500 em, tệp đầy đủ sáu trang: nạp phải xong trong vài chục giây.
    assert giay < 120, "nạp mất %.1f giây" % giay

    canh_bao = [w for w in api.get_data_health_report()["data"]["warnings"]
                if w["code"] != "health_oversubscribed_buoi"]
    assert canh_bao == [], canh_bao
    assert api.run_pipeline(seed=42)["ok"]


def test_ghi_de_chinh_tep_dau_vao_bi_chan(gop, xr):
    """Chạy lại với --ra là thư mục chứa tệp gộp: phải dừng, không ghi đè."""
    thu, duong = gop
    ra = thu / "chan"
    ra.mkdir()
    cung_ten = ra / "SO_NHAP_CLB.xlsx"
    cung_ten.write_bytes(duong.read_bytes())
    truoc = cung_ten.read_bytes()
    code = xr.main(["--raw", str(cung_ten), "--ra", str(ra)])
    assert code == 1
    assert cung_ten.read_bytes() == truoc
    assert sorted(os.listdir(str(ra))) == ["SO_NHAP_CLB.xlsx"]
