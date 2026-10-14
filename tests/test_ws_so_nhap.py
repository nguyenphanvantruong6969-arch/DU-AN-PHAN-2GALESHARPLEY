"""Sổ nhập CLB và trần nguyện vọng / thi theo cấu hình không gian làm việc."""

import base64
import json
import os
import re
import sqlite3
import subprocess
import sys

import pytest
from openpyxl import load_workbook

import cau_hinh_ws as cfgws
import so_nhap
from _dau_van_tay_so import bo_du_lieu, dau_van_tay, ghi_bo
from api import PipelineAPI

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLDEN = os.path.join(GOC, "tests", "du_lieu_ws")

NHAN_CONG_TY = {
    "person": {"vi": "Nhân viên", "en": "Employee"},
    "slot": {"vi": "Dự án", "en": "Project"},
    "session": {"vi": "Đợt", "en": "Round"},
    "group": {"vi": "Cấp bậc", "en": "Level"},
    "score": {"vi": "Điểm đánh giá", "en": "Rating"},
}


def cfg_cong_ty(**luat):
    r = {"max_choices": 3, "max_tests": None, "score_scope": "per_slot"}
    r.update(luat)
    return {"labels": NHAN_CONG_TY, "rules": r}


def _b64(duong):
    with open(duong, "rb") as f:
        return base64.b64encode(f.read()).decode()


def _clb(cid, ten, ct=10, buoi=""):
    return {"club_id": cid, "name": ten, "capacity": ct, "reserve_capacity": 0,
            "reserve_group": "", "buoi": buoi}


def _nv(cid, thi=False, diem=""):
    return {"club_id": cid, "thi": thi, "diem": diem}


def _hs(sid, nv, nhom=""):
    return {"student_id": sid, "name": "Tên " + sid, "reserve_group": nhom, "nv": nv}


@pytest.fixture
def goc(tmp_path):
    p = tmp_path / "goc"
    p.mkdir()
    return str(p)


@pytest.fixture
def api_ws(goc, tmp_path):
    x = tmp_path / "xuat"
    x.mkdir()
    return PipelineAPI(None, thu_muc_xuat=str(x), thu_muc_goc=goc)


def _mo(api, ten, cfg=None):
    slug = api.create_workspace(ten, cfg)["data"]["slug"]
    assert api.open_workspace(slug)["ok"]
    return slug


def _cfg_ws(luat=None, nhan=None, **khac):
    """Cấu hình đầy đủ để tạo workspace: nhãn công ty + luật cho trước."""
    cfg = {"name": "X", "industry": "company", "labels": nhan or NHAN_CONG_TY,
           "rules": {"max_choices": 3, "max_tests": None, "priority": "score",
                     "tier_mode": "reserve", "score_scope": "per_slot", "tiers": []}}
    cfg["rules"].update(luat or {})
    cfg.update(khac)
    return cfg


def _nap(api, duong):
    return api.import_so_nhap(_b64(duong))


def _luu(wb, duong):
    wb.save(duong)
    return str(duong)


# ------------------------------------------------------------------ #
# Trường học mặc định: y hệt trước đây
# ------------------------------------------------------------------ #

def test_ghi_cfg_none_khop_dau_van_tay_truoc_khi_co_cfg(tmp_path):
    """Sinh từ mã TRƯỚC khi có `cfg` (tests/du_lieu_ws/so_nhap_truoc.json)."""
    truoc = json.load(open(os.path.join(GOLDEN, "so_nhap_truoc.json"), encoding="utf-8"))
    nay = json.loads(json.dumps(ghi_bo(tmp_path), sort_keys=True))
    assert nay == truoc
    nay2 = json.loads(json.dumps(ghi_bo(tmp_path, cfg=None), sort_keys=True))
    assert nay2 == truoc


def test_doc_khop_ket_qua_truoc_khi_co_cfg(tmp_path):
    truoc = json.load(open(os.path.join(GOLDEN, "so_nhap_doc_truoc.json"), encoding="utf-8"))
    for ten, (clubs, hs) in bo_du_lieu().items():
        p = str(tmp_path / (ten + ".xlsx"))
        so_nhap.ghi_so_nhap(p, clubs, hs)
        for cfg in (None, {"labels": {k: {"vi": v} for k, v in so_nhap.NHAN_MAC_DINH.items()}}):
            kq = so_nhap.doc_so_nhap(load_workbook(p), cfg=cfg)
            assert json.loads(json.dumps(kq, sort_keys=True)) == truoc[ten], (ten, cfg)


def test_workspace_mac_dinh_ghi_dung_so_cu(api_ws, tmp_path):
    """Không gian làm việc chưa đổi gì: mẫu và sổ xuất giống từng ô sổ cũ."""
    _mo(api_ws, "Trường mặc định")
    clubs, hs = bo_du_lieu()["nhieu_buoi"]
    for c in clubs:
        assert api_ws.create_or_update_club(
            c["club_id"], c["name"], c["capacity"], c["reserve_capacity"],
            c["reserve_group"], c["buoi"])["ok"]
    mau = api_ws.tao_so_nhap_mau()["data"]["path"]
    cu = str(tmp_path / "cu.xlsx")
    with api_ws._ket_noi_doc() as cur:
        clubs_db, _, _, _ = api_ws._du_lieu_so_nhap(cur)
    so_nhap.ghi_so_nhap(cu, clubs_db, [])
    assert dau_van_tay(mau) == dau_van_tay(cu)
    xuat = api_ws.export_du_lieu_dau_vao()["data"]["path"]
    cu2 = str(tmp_path / "cu2.xlsx")
    with api_ws._ket_noi_doc() as cur:
        clubs_db, students_db, _, _ = api_ws._du_lieu_so_nhap(cur)
    so_nhap.ghi_so_nhap(cu2, clubs_db, students_db)
    assert dau_van_tay(xuat) == dau_van_tay(cu2)


def test_api_cau_hinh_so_nhap_la_none_khi_mac_dinh(api_ws):
    _mo(api_ws, "A")
    assert api_ws._cau_hinh_so_nhap() is None
    api_ws.update_workspace_config({"rules": {"max_choices": 4}})
    assert api_ws._cau_hinh_so_nhap()["rules"]["max_choices"] == 4
    api_ws.update_workspace_config({"rules": {"max_choices": 10}})
    assert api_ws._cau_hinh_so_nhap() is None


def test_nhan_mac_dinh_cua_so_nhap_khop_cau_hinh():
    """so_nhap.py không import được cau_hinh_ws nên chép nhãn; hai bên phải bằng nhau."""
    for k, cap in cfgws.MAC_DINH_TRUONG_HOC["labels"].items():
        assert so_nhap.NHAN_MAC_DINH[k] == cap["vi"], k
    assert so_nhap.TRAN_NV_MOI_BUOI == cfgws.MAC_DINH_TRUONG_HOC["rules"]["max_choices"]
    assert so_nhap.TRAN_THI_MOI_BUOI == cfgws.MAC_DINH_TRUONG_HOC["rules"]["max_tests"]


def test_so_nhap_chay_mot_minh_khong_keo_theo_cau_hinh_ws():
    ma = ("import sys, so_nhap; "
          "print('cau_hinh_ws' in sys.modules, 'workspace' in sys.modules)")
    r = subprocess.run([sys.executable, "-c", ma], cwd=GOC, capture_output=True,
                       text=True, check=True)
    assert r.stdout.split() == ["False", "False"]
    assert not re.search(r"^\s*(import|from)\s+cau_hinh_ws",
                         open(os.path.join(GOC, "so_nhap.py"), encoding="utf-8").read(), re.M)


# ------------------------------------------------------------------ #
# Ghi sổ theo nhãn
# ------------------------------------------------------------------ #

def test_ghi_theo_nhan_cong_ty_per_slot(tmp_path):
    p = str(tmp_path / "ct.xlsx")
    clubs = [_clb("d1", "Dự án A")]
    so_nhap.ghi_so_nhap(p, clubs, [], cfg=cfg_cong_ty(max_choices=4))
    wb = load_workbook(p)
    assert wb.sheetnames == ["1. Dự án", "2. Nhân viên", "Hướng dẫn"]
    assert [c.value for c in wb["1. Dự án"][1]] == [
        "Tên Dự án", "Đợt", "Chỉ tiêu", "Suất ưu tiên", "Cấp bậc", "Mã Dự án"]
    dau = [c.value for c in wb["2. Nhân viên"][1]]
    assert dau == ["Mã Nhân viên", "Họ tên", "Cấp bậc"] + [
        x for k in range(1, 5) for x in (f"NV{k}", f"Điểm đánh giá {k}")]
    assert wb["1. Dự án"]["A2"].value == "Dự án A"
    hd = "\n".join(str(r[0].value or "") for r in wb["Hướng dẫn"].iter_rows())
    assert "Dự án" in hd and "nhân viên" in hd and "CLB" not in hd
    # danh sách thả xuống NV trỏ đúng tên sheet mới
    dv = [d.formula1 for d in wb["2. Nhân viên"].data_validations.dataValidation
          if d.type == "list"]
    assert dv and dv[0].startswith("'1. Dự án'!")


def test_ghi_per_person_mot_cot_diem_sau_cot_nhom(tmp_path):
    p = str(tmp_path / "pp.xlsx")
    hs = [_hs("N1", [_nv("d1", True, "8,5"), _nv("d2", True, "8,5")], "Senior"),
          _hs("N2", [_nv("d1"), _nv("d2")]),
          _hs("N3", [_nv("d1", True, "")])]
    so_nhap.ghi_so_nhap(p, [_clb("d1", "Dự án A"), _clb("d2", "Dự án B")], hs,
                        cfg=cfg_cong_ty(score_scope="per_person", max_choices=3))
    ws = load_workbook(p)["2. Nhân viên"]
    assert [c.value for c in ws[1]] == [
        "Mã Nhân viên", "Họ tên", "Cấp bậc", "Điểm đánh giá", "NV1", "NV2", "NV3"]
    assert [c.value for c in ws[2]] == ["N1", "Tên N1", "Senior", 8.5, "Dự án A", "Dự án B", None]
    assert [c.value for c in ws[3]][3] is None                    # chưa thi
    assert ws["D4"].value == "thi"                                # thi chưa có điểm
    assert not any("Điểm đánh giá " in str(c.value) for c in ws[1])
    # kiểm điểm gắn đúng cột D, không phải cột NV
    dv = [(str(d.sqref), d.formula1) for d in ws.data_validations.dataValidation
          if d.type == "custom"]
    assert len(dv) == 1 and dv[0][0].startswith("D2:") and "D2" in dv[0][1]


def test_so_cot_nv_theo_max_choices_va_khong_bo_nv_nao(tmp_path):
    p = str(tmp_path / "n.xlsx")
    so_nhap.ghi_so_nhap(p, [_clb("d1", "A")], [], cfg=cfg_cong_ty(max_choices=2))
    dau = [c.value for c in load_workbook(p)["2. Nhân viên"][1]]
    assert dau.count("NV1") == 1 and "NV2" in dau and "NV3" not in dau
    # dữ liệu dài hơn trần (nhiều buổi): vẫn đủ cột, không rơi NV nào
    hs = [_hs("N1", [_nv(f"c{i}") for i in range(1, 6)])]
    so_nhap.ghi_so_nhap(p, [_clb(f"c{i}", f"C{i}") for i in range(1, 6)], hs,
                        cfg=cfg_cong_ty(max_choices=2))
    dau = [c.value for c in load_workbook(p)["2. Nhân viên"][1]]
    assert "NV5" in dau


def test_ten_sheet_hop_le_voi_ky_tu_cam(tmp_path):
    p = str(tmp_path / "k.xlsx")
    nhan = dict(NHAN_CONG_TY, slot={"vi": "Lớp: A/B [mới] rất rất rất dài dòng"})
    so_nhap.ghi_so_nhap(p, [_clb("a", "A")], [],
                        cfg={"labels": nhan, "rules": {"max_choices": 3}})
    ten = load_workbook(p).sheetnames[0]
    assert len(ten) <= 31 and not re.search(r"[\[\]:*?/\\]", ten)
    assert so_nhap.doc_so_nhap(load_workbook(p),
                               cfg={"labels": nhan, "rules": {"max_choices": 3}})["loi"] == []


# ------------------------------------------------------------------ #
# Đọc sổ
# ------------------------------------------------------------------ #

def test_cong_ty_sinh_mau_roi_doc_lai_per_slot(api_ws, tmp_path):
    _mo(api_ws, "Công ty", _cfg_ws({"max_choices": 3}))
    assert api_ws.create_or_update_club("d1", "Dự án A", 2, 0, "")["ok"]
    assert api_ws.create_or_update_club("d2", "Dự án B", 2, 0, "")["ok"]
    mau = api_ws.tao_so_nhap_mau()["data"]["path"]
    wb = load_workbook(mau)
    assert wb.sheetnames[:2] == ["1. Dự án", "2. Nhân viên"]
    ws = wb["2. Nhân viên"]
    ws.append(["N1", "Lan", "Senior", "Dự án A", 9, "Dự án B"])
    ws.append(["N2", "Minh", "", "Dự án B", "thi"])
    kq = _nap(api_ws, _luu(wb, tmp_path / "dien.xlsx"))
    assert kq["ok"], kq
    with api_ws._ket_noi_doc() as cur:
        pref = cur.execute("SELECT student_id, club_id, rank FROM preferences "
                           "ORDER BY 1, 3").fetchall()
        diem = cur.execute("SELECT student_id, club_id, score FROM club_scores "
                           "ORDER BY 1, 2").fetchall()
        thi = cur.execute("SELECT student_id, club_id FROM club_test_selection "
                          "ORDER BY 1, 2").fetchall()
        nhom = cur.execute("SELECT student_id, reserve_group FROM students "
                           "ORDER BY 1").fetchall()
    assert [tuple(r) for r in pref] == [("N1", "d1", 1), ("N1", "d2", 2), ("N2", "d2", 1)]
    assert [tuple(r) for r in diem] == [("N1", "d1", 9.0)]
    assert [tuple(r) for r in thi] == [("N1", "d1"), ("N2", "d2")]
    assert dict(map(tuple, nhom))["N1"] == "senior"      # phần mềm chuẩn hoá nhóm về chữ thường


def test_cong_ty_sinh_mau_roi_doc_lai_per_person(api_ws, tmp_path):
    _mo(api_ws, "Công ty", _cfg_ws({"score_scope": "per_person", "max_choices": 3}))
    for cid, ten in (("d1", "Dự án A"), ("d2", "Dự án B"), ("d3", "Dự án C")):
        assert api_ws.create_or_update_club(cid, ten, 2, 0, "")["ok"]
    mau = api_ws.tao_so_nhap_mau()["data"]["path"]
    wb = load_workbook(mau)
    ws = wb["2. Nhân viên"]
    assert [c.value for c in ws[1]][:5] == [
        "Mã Nhân viên", "Họ tên", "Cấp bậc", "Điểm đánh giá", "NV1"]
    ws.append(["N1", "Lan", "", 8.5, "Dự án A", "Dự án B", "Dự án C"])
    ws.append(["N2", "Minh", "", None, "Dự án C"])
    kq = _nap(api_ws, _luu(wb, tmp_path / "dien.xlsx"))
    assert kq["ok"], kq
    with api_ws._ket_noi_doc() as cur:
        theo_nguoi = [tuple(r) for r in cur.execute(
            "SELECT student_id, diem_ca_nhan FROM students ORDER BY 1")]
        theo_cho = cur.execute("SELECT COUNT(*) FROM club_scores").fetchone()[0]
        thi = cur.execute("SELECT COUNT(*) FROM club_test_selection").fetchone()[0]
    # MỘT ô điểm cho mỗi người (không sao chép ra từng chỗ); N2 không điểm = NULL
    assert theo_nguoi == [("N1", 8.5), ("N2", None)]
    assert theo_cho == 0 and thi == 0


def test_per_person_diem_sai_va_diem_thi(tmp_path):
    cfg = cfg_cong_ty(score_scope="per_person")
    p = str(tmp_path / "s.xlsx")
    so_nhap.ghi_so_nhap(p, [_clb("d1", "Dự án A")], [], cfg=cfg)
    wb = load_workbook(p)
    ws = wb["2. Nhân viên"]
    ws.append(["N1", "A", "", "abc", "Dự án A"])
    ws.append(["N2", "B", "", -3, "Dự án A"])
    ws.append(["N3", "C", "", "thi", "Dự án A"])
    ws.append(["N4", "D", "", "7,5", "Dự án A"])
    kq = so_nhap.doc_so_nhap(wb, cfg=cfg)
    ma = [(e["code"], e["params"]["student_id"]) for e in kq["loi"]]
    assert ma == [("so_nhap_diem_ca_nhan_sai", "N1"), ("so_nhap_diem_ca_nhan_sai", "N2")]
    hs = {s["student_id"]: s for s in kq["students"]}
    # điểm theo người giữ nguyên MỘT ô; nguyện vọng không mang điểm riêng
    assert hs["N3"]["nv"] == [{"club_id": "d1", "thi": False, "diem": ""}]
    assert hs["N3"]["diem_ca_nhan"] == ""             # chữ `thi` = chưa có điểm
    assert hs["N4"]["nv"] == [{"club_id": "d1", "thi": False, "diem": ""}]
    assert hs["N4"]["diem_ca_nhan"] == "7,5"


def test_kieu_diem_khac_kieu_workspace_bi_bao_thay_vi_bo_diem(tmp_path):
    p = str(tmp_path / "t.xlsx")
    clubs, hs = bo_du_lieu()["mot_buoi"]
    so_nhap.ghi_so_nhap(p, clubs, hs)                      # sổ cũ: Điểm 1, Điểm 2…
    kq = so_nhap.doc_so_nhap(load_workbook(p), cfg=cfg_cong_ty(score_scope="per_person"))
    assert [e["code"] for e in kq["loi"]] == ["so_nhap_diem_kieu_theo_cho"]
    # và ngược lại: sổ một-cột-điểm nạp vào workspace chấm theo từng nguyện vọng
    q = str(tmp_path / "u.xlsx")
    nhan_truong = {k: {"vi": v} for k, v in so_nhap.NHAN_MAC_DINH.items()}
    pp = {"labels": nhan_truong, "rules": {"score_scope": "per_person", "max_choices": 10}}
    so_nhap.ghi_so_nhap(q, clubs, hs, cfg=pp)
    assert load_workbook(q).sheetnames[:2] == ["1. CLB", "2. Học sinh"]
    kq = so_nhap.doc_so_nhap(load_workbook(q), cfg=dict(
        pp, rules={"score_scope": "per_slot", "max_choices": 10}))
    assert [e["code"] for e in kq["loi"]] == ["so_nhap_diem_kieu_theo_nguoi"]
    # không cfg: giữ đúng hành vi cũ (cột lạ bị bỏ qua, không báo lỗi mới)
    assert so_nhap.doc_so_nhap(load_workbook(q))["loi"] == []


def test_so_cu_cua_truong_hoc_nap_duoc_vao_workspace_doi_nhan(api_ws, tmp_path):
    """Sổ ghi bằng tiêu đề cũ (1. CLB, Mã HS, Điểm 1…) vào workspace công ty."""
    _mo(api_ws, "Công ty", _cfg_ws({"max_choices": 3}))
    clubs, hs = bo_du_lieu()["mot_buoi"]
    p = str(tmp_path / "cu.xlsx")
    so_nhap.ghi_so_nhap(p, clubs, hs)
    wb = load_workbook(p)
    assert wb.sheetnames[:2] == ["1. CLB", "2. Học sinh"]
    kq = _nap(api_ws, p)
    assert kq["ok"], kq
    with api_ws._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM clubs").fetchone()[0] == 2
        assert cur.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 2
        assert cur.execute("SELECT score FROM club_scores WHERE student_id='HS01'"
                           ).fetchone()[0] == 9.5


def test_sheet_ten_cu_va_ten_moi_deu_nhan(tmp_path):
    cfg = cfg_cong_ty()
    p = str(tmp_path / "a.xlsx")
    so_nhap.ghi_so_nhap(p, [_clb("d1", "Dự án A")], [], cfg=cfg)
    wb = load_workbook(p)
    assert so_nhap.la_so_nhap(wb.sheetnames, cfg)
    assert not so_nhap.la_so_nhap(wb.sheetnames)       # không cfg: chỉ tên cũ
    wb["1. Dự án"].title = "1 du an"                    # gõ lại không dấu
    assert so_nhap.la_so_nhap(wb.sheetnames, cfg)


def test_tieu_de_theo_nhan_nhan_khong_dau_va_hoa_thuong(tmp_path):
    cfg = cfg_cong_ty()
    p = str(tmp_path / "b.xlsx")
    so_nhap.ghi_so_nhap(p, [_clb("d1", "Dự án A")], [_hs("N1", [_nv("d1", True, "8")])],
                        cfg=cfg)
    wb = load_workbook(p)
    for c in wb["2. Nhân viên"][1]:
        if c.value:
            c.value = so_nhap.bo_dau(c.value).upper()    # "MA NHAN VIEN", "DIEM DANH GIA 1"
    for c in wb["1. Dự án"][1]:
        if c.value:
            c.value = so_nhap.bo_dau(c.value).upper()
    kq = so_nhap.doc_so_nhap(wb, cfg=cfg)
    assert kq["loi"] == [] and kq["students"][0]["nv"][0]["diem"] == "8"


# ------------------------------------------------------------------ #
# Trần nguyện vọng / thi theo luật
# ------------------------------------------------------------------ #

def _them_clb(api, n, buoi=""):
    for i in range(1, n + 1):
        assert api.create_or_update_club("c%02d" % i, "CLB %d" % i, 5, 0, "", buoi)["ok"]


def test_max_choices_3_tu_choi_nguyen_vong_thu_tu(api_ws):
    _mo(api_ws, "A", _cfg_ws({"max_choices": 3}))
    _them_clb(api_ws, 5)
    assert api_ws.create_student_if_missing("S1", "An")["ok"]
    assert api_ws.submit_preferences("S1", ["c01", "c02", "c03"])["ok"]
    res = api_ws.submit_preferences("S1", ["c01", "c02", "c03", "c04"])
    assert res["ok"] is False
    err = res["errors"][0]
    assert err["code"] == "pref_too_many" and err["params"]["tran"] == 3
    # và mặc định trường học vẫn là 10
    _mo(api_ws, "B")
    _them_clb(api_ws, 11)
    api_ws.create_student_if_missing("S1", "An")
    assert api_ws.submit_preferences("S1", ["c%02d" % i for i in range(1, 11)])["ok"]
    res = api_ws.submit_preferences("S1", ["c%02d" % i for i in range(1, 12)])
    assert res["errors"][0]["params"]["tran"] == 10


def test_max_choices_tinh_theo_tung_buoi(api_ws):
    _mo(api_ws, "A", _cfg_ws({"max_choices": 2}))
    for i, b in enumerate(("thu_2", "thu_2", "thu_2", "thu_3", "thu_3")):
        api_ws.create_or_update_club("c%d" % i, "C%d" % i, 5, 0, "", b)
    api_ws.create_student_if_missing("S1", "An")
    assert api_ws.submit_preferences("S1", ["c0", "c1", "c3", "c4"])["ok"]   # 2 + 2
    res = api_ws.submit_preferences("S1", ["c0", "c1", "c2"])
    assert res["errors"][0]["code"] == "max_pref_moi_buoi"
    assert res["errors"][0]["params"]["tran"] == 2


def test_so_nhap_co_4_nguyen_vong_bi_tu_choi_khi_max_choices_3(api_ws, tmp_path):
    _mo(api_ws, "A", _cfg_ws({"max_choices": 3}))
    clubs = [_clb("c%d" % i, "Dự án %d" % i) for i in range(1, 5)]
    hs = [_hs("S1", [_nv("c%d" % i) for i in range(1, 5)])]
    p = str(tmp_path / "bon.xlsx")
    so_nhap.ghi_so_nhap(p, clubs, hs, so_nv=4)
    kq = _nap(api_ws, p)
    assert kq["ok"] is False
    e = kq["errors"][0]
    assert e["code"] == "so_nhap_qua_tran_nv" and e["params"]["tran"] == 3
    with api_ws._ket_noi_doc() as cur:       # không nạp gì cả
        assert cur.execute("SELECT COUNT(*) FROM clubs").fetchone()[0] == 0


def test_nap_csv_nguyen_vong_cat_theo_max_choices(api_ws):
    _mo(api_ws, "A", _cfg_ws({"max_choices": 3}))
    _them_clb(api_ws, 4)
    csv = "student_id,name,pref_1,pref_2,pref_3,pref_4\nS1,An,c01,c02,c03,c04\n"
    res = api_ws.import_preferences_csv(csv)
    assert res["ok"]
    dem = [w_ for w_ in res["data"]["warnings"] if w_["code"] == "csv_pref_too_many_skipped"]
    assert dem and dem[0]["params"]["tran"] == 3


def test_max_tests_none_nhan_12_cho_thi(api_ws):
    _mo(api_ws, "A", _cfg_ws({"max_tests": None, "max_choices": 20}))
    _them_clb(api_ws, 12)
    api_ws.create_student_if_missing("S1", "An")
    ids = ["c%02d" % i for i in range(1, 13)]
    assert api_ws.submit_test_selection("S1", ids)["ok"]
    with api_ws._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM club_test_selection").fetchone()[0] == 12
    # cảnh báo "thi quá trần" của bảng sức khoẻ cũng tắt theo
    ma = [c["code"] for c in api_ws.get_data_health_report()["data"]["warnings"]]
    assert "health_thi_qua_tran" not in ma
    # mặc định trường học (5) thì từ chối
    _mo(api_ws, "B")
    _them_clb(api_ws, 12)
    api_ws.create_student_if_missing("S1", "An")
    res = api_ws.submit_test_selection("S1", ids)
    assert res["ok"] is False and res["errors"][0]["params"]["tran"] == 5
    assert api_ws.submit_test_selection("S1", ids[:5])["ok"]


def test_max_tests_so_nhap_12_o_diem_nap_duoc_khi_khong_gioi_han(api_ws, tmp_path):
    clubs = [_clb("c%02d" % i, "Dự án %d" % i) for i in range(1, 13)]
    hs = [_hs("S1", [_nv("c%02d" % i, True, str(i)) for i in range(1, 13)])]
    p = str(tmp_path / "m.xlsx")
    so_nhap.ghi_so_nhap(p, clubs, hs, so_nv=12)
    # trường học (5): từ chối
    _mo(api_ws, "Mặc định")
    kq = _nap(api_ws, p)
    assert kq["ok"] is False
    assert "so_nhap_qua_tran_thi" in {e["code"] for e in kq["errors"]}
    # max_tests None, max_choices 12: nạp được cả 12 chỗ thi
    _mo(api_ws, "Thoáng", _cfg_ws({"max_tests": None, "max_choices": 12}))
    kq = _nap(api_ws, p)
    assert kq["ok"], kq
    with api_ws._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM club_test_selection").fetchone()[0] == 12
        assert cur.execute("SELECT COUNT(*) FROM club_scores").fetchone()[0] == 12


def test_max_tests_3_tu_choi_6_va_per_person_khong_soat_tran_thi(api_ws, tmp_path):
    _mo(api_ws, "A", _cfg_ws({"max_tests": 3, "max_choices": 8}))
    _them_clb(api_ws, 4)
    api_ws.create_student_if_missing("S1", "An")
    res = api_ws.submit_test_selection("S1", ["c01", "c02", "c03", "c04"])
    assert res["ok"] is False and res["errors"][0]["params"]["tran"] == 3
    # điểm theo người: mọi nguyện vọng đều được chấm, trần thi không áp dụng
    _mo(api_ws, "B", _cfg_ws({"max_tests": 3, "max_choices": 8,
                              "score_scope": "per_person"}))
    clubs = [_clb("c%d" % i, "Dự án %d" % i) for i in range(1, 7)]
    hs = [_hs("S1", [_nv("c%d" % i, True, "7") for i in range(1, 7)])]
    p = str(tmp_path / "pp.xlsx")
    so_nhap.ghi_so_nhap(p, clubs, hs, cfg=cfg_cong_ty(
        score_scope="per_person", max_choices=8, max_tests=3))
    kq = _nap(api_ws, p)
    assert kq["ok"], kq


def test_kiem_tra_du_lieu_dung_tran_cua_workspace(api_ws):
    _mo(api_ws, "A", _cfg_ws({"max_choices": 3}))
    _them_clb(api_ws, 4)
    api_ws.create_student_if_missing("S1", "An")
    with sqlite3.connect(api_ws.db_path) as c:       # lách cửa nhập: ghi thẳng 4 NV
        for r, cid in enumerate(["c01", "c02", "c03", "c04"], start=1):
            c.execute("INSERT INTO preferences (student_id, club_id, rank) VALUES (?,?,?)",
                      ("S1", cid, r))
    res = api_ws.check_data_integrity()
    assert res["ok"] is False and res["errors"][0]["code"] == "pref_too_many"
    api_ws.update_workspace_config({"rules": {"max_choices": 4}})
    assert api_ws.check_data_integrity()["ok"] is True


def test_validate_data_integrity_tham_so_mac_dinh_la_hang_so():
    from rbda_priority_pipeline import (TRAN_NGUYEN_VONG_MOI_BUOI,
                                        validate_data_integrity)
    clubs = {"c%d" % i: {"capacity": 5, "reserve_capacity": 0} for i in range(12)}
    prefs = {"S": list(clubs)[:11]}
    sv = {"S": {}}
    assert TRAN_NGUYEN_VONG_MOI_BUOI == 10
    assert [e["code"] for e in validate_data_integrity(sv, clubs, prefs, {})] == [
        "pref_too_many"]
    assert validate_data_integrity(sv, clubs, prefs, {}, 11) == []
    assert validate_data_integrity(sv, clubs, {"S": ["c0"] * 1}, {}, 1) == []


def test_chay_thuat_toan_voi_workspace_mac_dinh_khong_doi(api_ws):
    """Đổi chỗ đọc trần không được làm lệch kết quả của trường học mặc định."""
    _mo(api_ws, "A")
    _them_clb(api_ws, 3)
    for i in range(1, 7):
        sid = "S%d" % i
        api_ws.create_student_if_missing(sid, "HS " + sid)
        assert api_ws.submit_preferences(sid, ["c01", "c02", "c03"])["ok"]
    res = api_ws.run_pipeline(42)
    assert res["ok"], res
