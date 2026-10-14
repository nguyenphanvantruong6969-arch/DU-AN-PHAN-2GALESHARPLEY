"""Kiểm toán đầu-cuối nhiều workspace (TASK 7): các lỗi ở CHỖ NỐI giữa các task, và đợt rà an ninh.

Mỗi phần bắt một lỗi tìm thấy khi đọc diff từ 0e4d774 và chạy thử ba workspace:

  A. Tên nhóm trong luật (`tiers`) phải khớp nhóm đã nạp từ Sổ nhập ("Quản lý" <-> "quan_ly").
  B. Một workspace hỏng giữa các workspace lành: bảng chọn báo hỏng, mở thì nói rõ, khôi phục được
     TỪ BẢNG CHỌN (màn phục hồi chỉ hiện khi KHÔNG workspace nào mở được).
  C. Cấu hình độc hại trong `workspace_settings` (lồng sâu, chuỗi khổng lồ, kiểu sai) rơi về mặc định.
  D. Nhập zip: tên thiết bị / dấu hai chấm của Windows, quá nhiều mục, dữ liệu nén hỏng, app.db hỏng.
  E. Slug: tên thiết bị Windows không dùng làm slug; thư mục lạ không có slug hợp lệ không hiện trong danh sách.
  F. Máy chủ dự phòng không phục vụ tệp trong workspaces/ và gọi được MỌI phương thức workspace.
  G. Gói PyInstaller: mọi module Python main.py kéo theo, và mọi hàm backend giao diện gọi.
  H. Chạy với đường dẫn CSDL trong argv: y như trước khi có workspace.
  I. Tệp sinh ra (sao lưu, match_results.csv, bản xuất lùi) nằm trong thư mục workspace ĐANG MỞ.
"""

import ast
import base64
import hashlib
import json
import os
import re
import sqlite3
import sys
import urllib.error
import urllib.request
import zipfile

import pytest

import browser_host
import cau_hinh_ws as ch
import rbda_priority_pipeline as rp
import workspace as ws
from api import PipelineAPI
from api_workspace import WorkspaceMixin

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BAK = ".bak-20260101_000000_000000"


@pytest.fixture
def goc(tmp_path):
    g = tmp_path / "goc"
    g.mkdir()
    return str(g)


@pytest.fixture
def api(goc, tmp_path):
    slug = ws.tao(goc, "Trường học", None)
    xuat = tmp_path / "xuat"
    xuat.mkdir()
    return PipelineAPI(ws.duong_dan_db(goc, slug), thu_muc_xuat=str(xuat), thu_muc_goc_ws=goc)


def _dat_cau_hinh_tho(db, gia_tri):
    conn = sqlite3.connect(db)
    try:
        conn.execute("INSERT OR REPLACE INTO workspace_settings (key, value) VALUES ('config', ?)",
                     (gia_tri,))
        conn.commit()
    finally:
        conn.close()


def _bam(duong):
    with open(duong, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


# ===========================================================================
# A. Tên nhóm trong luật khớp nhóm đã nạp từ Sổ nhập
# ===========================================================================

@pytest.mark.parametrize("nhom", ["quan_ly", "Quản lý", "QUAN LY", "quan-ly", "quan  ly", " quan_ly_ "])
def test_ten_nhom_khop_dang_da_chuan_hoa_cua_so_nhap(nhom):
    """Sổ nhập, CSV và màn quản lý đều ghi nhóm thành `quan_ly` (`chuan_hoa_nhom_du_tru`).
    Luật ghi "Quản lý": phải ra CÙNG một nhóm, không thì mọi người rơi xuống "không nhóm"."""
    hang = rp.xay_tier_rank({"a": {"reserve_group": nhom}}, ["Quản lý", "Chuyên viên"])
    assert hang == {"a": 0}


def test_dau_cau_van_phan_biet_nhom_that_su_khac_nhau():
    # "Khối 1 2" khác "Khối 12" (đã có test cũ); dấu gạch dưới/gạch nối chỉ là khoảng trắng.
    hang = rp.xay_tier_rank({"a": {"reserve_group": "khoi_1_2"}, "b": {"reserve_group": "khoi_12"}},
                            ["Khối 12"])
    assert hang == {"b": 0}


def test_ten_nhom_toan_ky_hieu_khong_khop_nguoi_khong_nhom():
    hang = rp.xay_tier_rank({"a": {"reserve_group": "___"}, "b": {"reserve_group": "!!!"}}, ["???"])
    assert hang == {}


def test_luat_tu_choi_hai_ten_nhom_cung_mot_nhom():
    """Cặp "Quản lý" / "quan_ly" là MỘT nhóm với thuật toán; cho qua thì hạng thứ hai bị nuốt im lặng."""
    with pytest.raises(ValueError, match="trùng"):
        ch.chuan_hoa({"rules": {"tiers": ["Quản lý", "quan_ly"]}})
    with pytest.raises(ValueError, match="trùng"):
        ch.chuan_hoa({"rules": {"tiers": ["A+", "A-"]}})
    ch.chuan_hoa({"rules": {"tiers": ["Quản lý", "Chuyên viên"]}})        # khác nhau thì được


def test_so_nhap_roi_chay_xep_nhom_cung_dung_het_nguoi(goc, tmp_path):
    """Từ Sổ nhập đến lần chạy: không ai bị rơi khỏi `tier_rank`, cảnh báo sức khoẻ im."""
    from test_ws_e2e import CONG_TY, _dien_so_cong_ty
    import random

    slug = ws.tao(goc, "Cty", CONG_TY)
    api = PipelineAPI(ws.duong_dan_db(goc, slug), thu_muc_xuat=str(tmp_path), thu_muc_goc_ws=goc)
    assert api.import_so_nhap(_dien_so_cong_ty(api, random.Random(3)))["ok"]
    luat = api._luat_nghiem()
    (hs, *_), _ = rp.load_from_sqlite_kem_dau_van_tay(api.db_path, luat)
    assert len(rp.tham_so_luat(luat, hs)["tier_rank"]) == len(hs) == 24
    ma = [w["params"] for w in api.get_data_health_report()["data"]["warnings"]
          if w["code"] == "health_tier_missing"]
    assert ma == []


# ===========================================================================
# B. Một workspace hỏng giữa các workspace lành
# ===========================================================================

def _lam_hong(db):
    with open(db, "wb") as f:
        f.write(b"khong phai sqlite " * 300)


def _hai_workspace_mot_hong(goc, tmp_path, co_sao_luu=True):
    """('lanh', 'hong'): 'hong' có một câu lạc bộ `c1`, bản sao lưu lành (nếu cần), rồi bị phá."""
    lanh = ws.tao(goc, "Lành", None)
    hong = ws.tao(goc, "Hỏng", None)
    db = ws.duong_dan_db(goc, hong)
    a = PipelineAPI(db, thu_muc_xuat=str(tmp_path), thu_muc_goc_ws=goc)
    assert a.create_or_update_club("c1", "Cờ vua", 5, 0, "")["ok"]
    if co_sao_luu:
        ws._chep_db(db, db + BAK)
    _lam_hong(db)
    return lanh, hong


def _mo(goc, tmp_path, slug):
    return PipelineAPI(ws.duong_dan_db(goc, slug), thu_muc_xuat=str(tmp_path), thu_muc_goc_ws=goc)


def test_bang_chon_bao_workspace_hong_va_so_ban_sao_luu(goc, tmp_path):
    lanh, hong = _hai_workspace_mot_hong(goc, tmp_path)
    api = _mo(goc, tmp_path, lanh)
    ds = {w["slug"]: w for w in api.list_workspaces()["data"]["workspaces"]}
    assert ds[lanh]["hong"] is False and ds[hong]["hong"] is True
    assert ds[hong]["n_sao_luu"] == 1 and ds[lanh]["n_sao_luu"] == 0
    assert ds[lanh]["dang_mo"] is True            # workspace đang mở KHÔNG bị kiểm lại


def test_kiem_hong_khong_nham_tep_dang_bi_khoa_hay_khong_co_hay_trong(goc, tmp_path):
    """Chỉ tệp HỎNG THẬT mới bị gắn nhãn: đang có tiến trình khác ghi (khoá), tệp rỗng 0 byte
    (SQLite coi là CSDL mới) hay tệp không còn đều không phải "hỏng"."""
    slug = ws.tao(goc, "Khoá", None)
    db = ws.duong_dan_db(goc, slug)
    assert ws.kiem_hong(db) is False
    giu = sqlite3.connect(db, timeout=0.1, isolation_level=None)
    try:
        giu.execute("BEGIN EXCLUSIVE")                     # như một lần chạy xếp đang ghi
        assert ws.kiem_hong(db) is False
    finally:
        giu.close()
    rong = tmp_path / "rong.db"
    rong.write_bytes(b"")
    assert ws.kiem_hong(str(rong)) is False
    assert ws.kiem_hong(str(tmp_path / "khong-co.db")) is False
    _lam_hong(db)
    assert ws.kiem_hong(db) is True


def test_mo_workspace_hong_noi_ro_thay_vi_loi_sqlite(goc, tmp_path):
    lanh, hong = _hai_workspace_mot_hong(goc, tmp_path)
    api = _mo(goc, tmp_path, lanh)
    r = api.open_workspace(hong)
    assert not r["ok"] and r["errors"][0]["code"] == "ws_hong"
    assert api.db_path == ws.duong_dan_db(goc, lanh)      # vẫn ở workspace lành
    from i18n_errors import MESSAGES
    assert MESSAGES["ws_hong"]["vi"] and MESSAGES["ws_hong"]["en"]


def test_doc_cau_hinh_workspace_hong_hoac_cau_hinh_hong_khong_tra_mac_dinh_gia(goc, tmp_path):
    lanh, hong = _hai_workspace_mot_hong(goc, tmp_path)
    api = _mo(goc, tmp_path, lanh)
    kq = api.get_workspace_config(hong)
    assert not kq["ok"] and kq["errors"][0]["code"] == "ws_hong"
    cau_hinh_xau = ws.tao(goc, "Cấu hình xấu", None)
    _dat_cau_hinh_tho(ws.duong_dan_db(goc, cau_hinh_xau), "{khong phai json")
    kq = api.get_workspace_config(cau_hinh_xau)
    assert not kq["ok"] and kq["errors"][0]["code"] == "ws_cau_hinh_hong"
    # …còn workspace lành vẫn đọc bình thường
    assert api.get_workspace_config(lanh)["ok"]


def test_khoi_phuc_workspace_hong_tu_bang_chon_chi_dong_dung_cai_do(goc, tmp_path):
    lanh, hong = _hai_workspace_mot_hong(goc, tmp_path)
    api = _mo(goc, tmp_path, lanh)
    db_lanh = ws.duong_dan_db(goc, lanh)
    bam_lanh = _bam(db_lanh)

    r = api.recover_workspace(hong)
    assert r["ok"], r["errors"]
    assert r["data"]["restored_from"].startswith("app.db.bak-")

    assert _bam(db_lanh) == bam_lanh                       # workspace lành không bị đụng
    assert api.db_path == db_lanh                          # và vẫn là cái đang mở
    ds = {w["slug"]: w for w in api.list_workspaces()["data"]["workspaces"]}
    assert ds[hong]["hong"] is False
    assert api.open_workspace(hong)["ok"]
    assert [c["club_id"] for c in api.list_clubs_admin()["data"]] == ["c1"]
    # tệp hỏng được dời đi chứ không xoá
    thu_muc = os.path.dirname(ws.duong_dan_db(goc, hong))
    assert [t for t in os.listdir(thu_muc) if ".corrupt-" in t]


def test_khoi_phuc_khong_co_ban_sao_luu_va_bat_dau_moi(goc, tmp_path):
    lanh, hong = _hai_workspace_mot_hong(goc, tmp_path, co_sao_luu=False)
    api = _mo(goc, tmp_path, lanh)
    r = api.recover_workspace(hong)
    assert not r["ok"] and r["errors"][0]["code"] == "recovery_no_backups"
    r = api.recover_workspace(hong, "bat_dau_moi")
    assert r["ok"], r["errors"]
    assert api.open_workspace(hong)["ok"]
    assert api.list_clubs_admin()["data"] == []
    assert not api.recover_workspace(hong, "xoa_sach")["ok"]        # cách lạ bị từ chối


def test_khoi_phuc_workspace_lanh_bi_tu_choi(goc, tmp_path):
    lanh, _ = _hai_workspace_mot_hong(goc, tmp_path)
    api = _mo(goc, tmp_path, lanh)
    before = _bam(ws.duong_dan_db(goc, lanh))
    r = api.recover_workspace(lanh)
    assert not r["ok"] and r["errors"][0]["code"] == "recovery_db_is_healthy"
    assert _bam(ws.duong_dan_db(goc, lanh)) == before
    assert api.recover_workspace("../etc")["errors"][0]["code"] == "ws_khong_co"


def test_khoi_dong_khi_nhieu_workspace_hong_roi_cuu_lan_luot(goc, tmp_path, monkeypatch):
    """Hai workspace hỏng: màn phục hồi hiện cho CÁI MỚI NHẤT và chỉ cứu cái đó; lần khởi động sau
    vào được giao diện chính, bảng chọn vẫn liệt kê cả hai và đánh dấu cái còn hỏng để cứu tiếp."""
    import main
    a = ws.tao(goc, "Một", None)
    b = ws.tao(goc, "Hai", None)
    db_a, db_b = ws.duong_dan_db(goc, a), ws.duong_dan_db(goc, b)
    for ten, db in (("ca", db_a), ("cb", db_b)):
        PipelineAPI(db, thu_muc_xuat=str(tmp_path), thu_muc_goc_ws=goc).create_or_update_club(
            ten, ten, 3, 0, "")
        ws._chep_db(db, db + BAK)
        _lam_hong(db)
    os.utime(db_b, (1_700_000_000, 1_700_000_000))            # B cũ hơn A
    bam_b = _bam(db_b)

    monkeypatch.setattr(main, "BASE_DIR", goc)
    monkeypatch.setattr(sys, "argv", ["main.py"])
    mo = []
    monkeypatch.setattr(main, "_show_ui", lambda title, page, js_api, *x, **k: mo.append((page, js_api)))

    main.main()
    (trang, phuc_hoi), = mo
    assert trang == "recovery.html" and phuc_hoi.db_path == db_a       # đúng tệp hỏng, mới nhất
    assert phuc_hoi.restore_from_backup()["ok"]
    assert _bam(db_b) == bam_b                                          # cái kia không bị đụng

    mo.clear()
    main.main()
    (trang, api), = mo
    assert trang == "index.html" and api.db_path == db_a
    ds = {w["slug"]: w for w in api.list_workspaces()["data"]["workspaces"]}
    assert sorted(ds) == sorted([a, b])
    assert ds[a]["hong"] is False and ds[b]["hong"] is True and ds[b]["n_sao_luu"] == 1
    assert api.recover_workspace(b)["ok"]
    assert [w["hong"] for w in api.list_workspaces()["data"]["workspaces"]] == [False, False]
    assert api.open_workspace(b)["ok"]
    assert [c["club_id"] for c in api.list_clubs_admin()["data"]] == ["cb"]


def test_xoa_workspace_hong_van_duoc_va_danh_sach_con_lai_lanh(goc, tmp_path):
    lanh, hong = _hai_workspace_mot_hong(goc, tmp_path)
    api = _mo(goc, tmp_path, lanh)
    assert api.delete_workspace(hong, "XOA")["ok"]
    assert [w["slug"] for w in api.list_workspaces()["data"]["workspaces"]] == [lanh]


def test_giao_dien_co_nut_khoi_phuc_cho_workspace_hong():
    nguon = open(os.path.join(GOC, "js", "075_workspace.js"), encoding="utf-8").read()
    assert "recover_workspace" in nguon and 'hanhDong("khoi_phuc"' in nguon and "ws_badge_hong" in nguon
    i18n = open(os.path.join(GOC, "i18n.js"), encoding="utf-8").read()
    for khoa in ("ws_btn_khoi_phuc", "ws_badge_hong", "ws_da_khoi_phuc"):
        assert len(re.findall(r'\b%s:' % khoa, i18n)) == 2, khoa          # đúng một lần ở vi và en


# ===========================================================================
# C. Cấu hình độc hại trong workspace_settings
# ===========================================================================

def _mac_dinh():
    return ch.doc_cau_hinh(os.path.join(os.sep, "khong", "co", "tep.db"))


@pytest.mark.parametrize("nguy_hiem", [
    "[" * 200000 + "]" * 200000,                                             # lồng sâu: RecursionError
    '{"labels":' * 20000 + "1" + "}" * 20000,
    json.dumps({"name": "x" * 5_000_000}),                                   # chuỗi khổng lồ
    json.dumps({"labels": {"slot": {"vi": "y" * 3_000_000}}}),
    json.dumps({"rules": {"tier_mode": "strict", "tiers": ["t%d" % i for i in range(50_000)]}}),
    json.dumps({"rules": {"tier_mode": "strict", "tiers": ["z" * 100_000]}}),
    json.dumps({"rules": {"max_choices": "10"}}),                              # kiểu sai
    json.dumps({"labels": {"slot": ["vi", "en"]}}),
    json.dumps({"labels": [1, 2, 3]}),
    json.dumps({"rules": {"tiers": "khong phai danh sach"}}),
    json.dumps({"name": 12345}),
    json.dumps({"name": ["a"]}),
    '{"rules": {"max_choices": NaN}}',
    '{"rules": {"max_choices": Infinity}}',
    "[]", '"x"', "null", "5", "",
    b"\xff\xfe\x00bad utf8",
])
def test_cau_hinh_doc_hai_roi_ve_mac_dinh_va_khong_nem(goc, nguy_hiem):
    slug = ws.tao(goc, "Thử", None)
    db = ws.duong_dan_db(goc, slug)
    _dat_cau_hinh_tho(db, nguy_hiem)
    kq = ch.doc_cau_hinh(db)                      # không ném
    mac_dinh = _mac_dinh()
    mac_dinh["name"] = kq["name"]
    assert kq == mac_dinh == ch.doc_cau_hinh(db)  # = mặc định trường học
    # …và mọi nơi liệt kê/mở workspace cũng sống
    assert [w["slug"] for w in ws.danh_sach(goc)] == [slug]
    with pytest.raises((ValueError, sqlite3.Error, RecursionError)):
        ch.doc_cau_hinh(db, nghiem=True)          # chế độ nghiêm vẫn báo, không đoán


def test_ghi_cau_hinh_tu_choi_chuoi_va_danh_sach_qua_dai():
    mau = {"name": "ok"}
    for xau in (
        {"name": "x" * (ch.TRAN_TEN + 1)},
        {"labels": {"slot": {"vi": "y" * (ch.TRAN_NHAN + 1), "en": "a"}}},
        {"labels": {"slot": {"vi": "a", "en": "y" * (ch.TRAN_NHAN + 1)}}},
        {"rules": {"tiers": ["t%d" % i for i in range(ch.TRAN_SO_NHOM + 1)]}},
        {"rules": {"tiers": ["z" * (ch.TRAN_NHAN + 1)]}},
        {"name": "ok\x00"},
        {"labels": {"slot": {"vi": "a\x00b", "en": "a"}}},
    ):
        with pytest.raises(ValueError):
            ch.chuan_hoa({**mau, **xau})
    gioi_han = {"name": "x" * ch.TRAN_TEN,
                "labels": {"slot": {"vi": "y" * ch.TRAN_NHAN, "en": "z" * ch.TRAN_NHAN}},
                "rules": {"tiers": ["t%d" % i for i in range(ch.TRAN_SO_NHOM)]}}
    assert ch.chuan_hoa(gioi_han)["name"] == "x" * ch.TRAN_TEN


def test_api_tao_va_doi_ten_tu_choi_ten_khong_hop_le(api):
    kq = api.create_workspace("x" * 5000, None)
    assert not kq["ok"] and kq["errors"][0]["code"] == "ws_du_lieu_sai"
    for cfg in ([1, 2], "abc", 5):
        kq = api.create_workspace("Cfg la", cfg)
        assert not kq["ok"] and kq["errors"][0]["code"] == "ws_du_lieu_sai", cfg
    slug = api.get_workspace_state()["data"]["slug"]
    assert not api.rename_workspace(slug, "y" * 5000)["ok"]
    assert not api.rename_workspace(slug, 123)["ok"]
    assert [w["slug"] for w in ws.danh_sach(api._goc_ws)] == [slug]    # không workspace rác


def test_khoi_dong_song_khi_mot_workspace_co_cau_hinh_long_sau(goc, monkeypatch):
    import main
    monkeypatch.setattr(main, "BASE_DIR", goc)
    monkeypatch.setattr(sys, "argv", ["main.py"])
    a = ws.tao(goc, "A", None)
    ws.tao(goc, "B", None)
    _dat_cau_hinh_tho(ws.duong_dan_db(goc, a), "[" * 200000 + "]" * 200000)
    db, goc_ws, da_chon = main.khoi_dong_workspace()
    assert goc_ws == goc and da_chon is False and os.path.exists(db)


# ===========================================================================
# D. Nhập zip
# ===========================================================================

def _db_bytes(tmp_path, ten="mau.db"):
    p = str(tmp_path / ten)
    rp.init_db(p)
    with open(p, "rb") as f:
        return f.read()


def _zip(duong, muc):
    with zipfile.ZipFile(duong, "w", zipfile.ZIP_DEFLATED) as z:
        for ten, nd in muc:
            z.writestr(ten, nd)
    return str(duong)


def _thu_muc_con(goc):
    g = os.path.join(goc, "workspaces")
    return sorted(os.listdir(g)) if os.path.isdir(g) else []


@pytest.mark.parametrize("ten", [
    "CON", "con.txt", "NUL", "nul.log", "a/AUX", "a/aux.csv", "PRN.x", "COM1", "com9.txt",
    "LPT1", "lpt9.db", "CONIN$", "CONOUT$",                     # tên thiết bị
    "app.db:evil", "ghi-chu.txt:Zone.Identifier", "a/b:c",     # luồng dữ liệu phụ NTFS
    "tep.", "thu muc /x.txt", "x/y ", "bad<name>.txt", 'q"q.txt', "p|q.txt", "w?.txt", "s*.txt",
    "x\x01y.txt",
])
def test_nhap_zip_tu_choi_ten_khong_an_toan_tren_windows(goc, tmp_path, ten):
    z = _zip(tmp_path / "x.zip", [("app.db", _db_bytes(tmp_path)), (ten, b"x")])
    with pytest.raises(ValueError, match="không an toàn"):
        ws.nhap_zip(goc, z)
    assert _thu_muc_con(goc) == []                  # không workspace dở, không thư mục tạm


def test_nhap_zip_ten_hop_le_giong_ten_thiet_bi_van_duoc(goc, tmp_path):
    """"console.txt", "concat.csv", "auxiliary/x" chỉ BẮT ĐẦU bằng tên thiết bị: vẫn hợp lệ."""
    z = _zip(tmp_path / "x.zip", [("app.db", _db_bytes(tmp_path)), ("console.txt", b"a"),
                                   ("concat.csv", b"b"), ("auxiliary/x.txt", b"c")])
    slug = ws.nhap_zip(goc, z)
    assert sorted(os.listdir(os.path.join(goc, "workspaces", slug))) == [
        "app.db", "auxiliary", "concat.csv", "console.txt"]


def test_nhap_zip_tu_choi_qua_nhieu_muc(goc, tmp_path, monkeypatch):
    monkeypatch.setattr(ws, "TRAN_SO_MUC_ZIP", 5)
    z = _zip(tmp_path / "x.zip", [("app.db", _db_bytes(tmp_path))] + [("f%d.txt" % i, b"x") for i in range(10)])
    with pytest.raises(ValueError, match="quá nhiều"):
        ws.nhap_zip(goc, z)
    assert _thu_muc_con(goc) == []


def test_nhap_zip_tu_choi_duong_dan_qua_sau_hoac_qua_dai(goc, tmp_path):
    for ten in ("/".join(["d"] * 40) + "/x.txt", "d/" + "x" * 300 + ".txt"):
        z = _zip(tmp_path / "x.zip", [("app.db", _db_bytes(tmp_path)), (ten, b"x")])
        with pytest.raises(ValueError, match="quá dài|quá sâu"):
            ws.nhap_zip(goc, z)
    assert _thu_muc_con(goc) == []


def test_nhap_zip_du_lieu_nen_hong_la_loi_ro_rang_khong_phai_bad_zip(goc, tmp_path):
    p = str(tmp_path / "x.zip")
    with zipfile.ZipFile(p, "w", zipfile.ZIP_STORED) as z:
        z.writestr("app.db", _db_bytes(tmp_path))
        z.writestr("ghi-chu.txt", b"noi dung that cua ghi chu " * 10)
    du = bytearray(open(p, "rb").read())
    i = du.find(b"noi dung that cua ghi chu")
    du[i + 3] ^= 0xFF                                  # hỏng một byte dữ liệu -> sai CRC
    open(p, "wb").write(bytes(du))
    with pytest.raises(ValueError, match="hỏng"):
        ws.nhap_zip(goc, p)
    assert _thu_muc_con(goc) == []


def test_nhap_zip_app_db_sqlite_nhung_hong_trang(goc, tmp_path):
    du = bytearray(_db_bytes(tmp_path))
    for i in range(4096, len(du)):
        du[i] = 0xAB                                   # giữ nguyên tiêu đề, phá mọi trang sau đó
    z = _zip(tmp_path / "x.zip", [("app.db", bytes(du))])
    with pytest.raises(ValueError, match="app.db"):
        ws.nhap_zip(goc, z)
    assert _thu_muc_con(goc) == []


def test_api_nhap_zip_khong_dung_ten_tep_nguoi_dung_lam_ten_tep_tam(api, goc, tmp_path, monkeypatch):
    thay = []
    goc_ham = ws.nhap_zip

    def nghe(root, zip_path, ten_mac_dinh=None):
        thay.append((os.path.basename(zip_path), ten_mac_dinh))
        return goc_ham(root, zip_path, ten_mac_dinh)

    monkeypatch.setattr(ws, "nhap_zip", nghe)
    z = _zip(tmp_path / "x.zip", [("app.db", _db_bytes(tmp_path))])
    b64 = base64.b64encode(open(z, "rb").read()).decode()
    for ten in ("NUL", "CON.zip", 'a:b*c?.zip', "../../x.zip", "C:\\Users\\x\\ngày 1.zip", ""):
        r = api.import_workspace(b64, ten)
        assert r["ok"], (ten, r["errors"])
    assert {t for t, _ in thay} == {"nhap.zip"}
    assert [m for _, m in thay] == ["NUL", "CON", "a:b*c?", "x", "ngày 1", "workspace"]
    # tên dự phòng cũng phải qua kiểm cấu hình: không workspace nào mang tên toàn ký hiệu cấm
    assert all(w["name"] for w in api.list_workspaces()["data"]["workspaces"])


def test_api_nhap_zip_tu_choi_tai_len_qua_lon(api, monkeypatch):
    monkeypatch.setattr(ws, "TRAN_GIAI_NEN_BYTE", 1000)
    r = api.import_workspace(base64.b64encode(b"x" * 5000).decode(), "x.zip")
    assert not r["ok"] and r["errors"][0]["code"] == "ws_du_lieu_sai"
    assert _thu_muc_con(api._goc_ws) == ["truong-hoc"]


# ===========================================================================
# E. Slug
# ===========================================================================

@pytest.mark.parametrize("slug", ["con", "nul", "aux", "prn", "com1", "com9", "lpt1", "lpt9"])
def test_slug_ten_thiet_bi_windows_khong_dung_duoc(goc, slug):
    with pytest.raises(ValueError):
        ws.duong_dan_db(goc, slug)
    try:
        os.makedirs(os.path.join(goc, "workspaces", slug), exist_ok=True)
    except OSError:
        return          # Windows không cho tạo thư mục tên thiết bị: càng chứng tỏ slug đó vô dụng
    assert ws.danh_sach(goc) == []


@pytest.mark.parametrize("slug", ["../x", "a/b", "a\\b", "..", ".", "", " ", "A", "a b", "a--b",
                                   "-a", "a-", "_trash", "trash\x00", "a.b", "a" * 61 + "-"])
def test_slug_xau_van_bi_tu_choi_o_moi_ham_api(api, slug):
    for r in (api.open_workspace(slug), api.rename_workspace(slug, "x"),
              api.duplicate_workspace(slug, "x"), api.export_workspace(slug),
              api.save_as_template(slug, "x"), api.recover_workspace(slug),
              api.delete_workspace(slug, "XOA")):
        assert not r["ok"] and r["errors"][0]["code"] in ("ws_khong_co", "ws_du_lieu_sai"), (slug, r)
    assert api.get_workspace_config(slug)["ok"] is False or slug.strip() == ""


def test_danh_sach_bo_thu_muc_khong_co_slug_hop_le(goc):
    ws.tao(goc, "Thật", None)
    la = os.path.join(goc, "workspaces", "Thư mục Chép Tay")
    os.makedirs(la)
    rp.init_db(os.path.join(la, "app.db"))
    assert [w["slug"] for w in ws.danh_sach(goc)] == ["that"]


# ===========================================================================
# F. Máy chủ dự phòng (browser_host)
# ===========================================================================

def _lay(base, duong):
    req = urllib.request.Request(base + duong)
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""


def test_may_chu_du_phong_khong_phuc_vu_tep_trong_workspaces(tmp_path):
    goc = tmp_path / "goc"
    (goc / "workspaces" / "x").mkdir(parents=True)
    (goc / "templates").mkdir()
    (goc / "index.html").write_text("<html><head></head><body>ok</body></html>", encoding="utf-8")
    (goc / "logo.svg").write_text("<svg/>", encoding="utf-8")
    for duong in ("workspaces/x/doc-hai.svg", "workspaces/x/doc-hai.js", "workspaces/x/doc-hai.html",
                  "templates/doc-hai.js"):
        (goc / duong).write_text("alert(1)", encoding="utf-8")
    api = PipelineAPI(str(tmp_path / "app.db"))
    url = browser_host.serve(api, str(goc), "index.html", open_browser=False)
    base = url.split("/index.html")[0]
    assert _lay(base, "/logo.svg")[0] == 200                      # đối chứng: tệp giao diện vẫn phục vụ
    for duong in ("/workspaces/x/doc-hai.svg", "/workspaces/x/doc-hai.js",
                  "/workspaces/x/doc-hai.html", "/templates/doc-hai.js", "/Workspaces/x/doc-hai.js",
                  "/workspaces%2Fx/doc-hai.js", "/./workspaces/x/doc-hai.js"):
        assert _lay(base, duong)[0] == 404, duong


def test_may_chu_du_phong_goi_duoc_moi_phuong_thuc_workspace(goc, tmp_path):
    slug = ws.tao(goc, "Thử", None)
    api = PipelineAPI(ws.duong_dan_db(goc, slug), thu_muc_xuat=str(tmp_path), thu_muc_goc_ws=goc)
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    base, token = url.split("/index.html?t=")

    def goi(ten, *args):
        req = urllib.request.Request(
            "%s/__api__/%s" % (base, ten), data=json.dumps({"args": list(args)}).encode(),
            headers={"Content-Type": "application/json", "X-Kiosk-Token": token}, method="POST")
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())

    cong_khai = sorted(n for n in dir(WorkspaceMixin)
                       if not n.startswith("_") and callable(getattr(WorkspaceMixin, n)))
    assert {"get_workspace_state", "list_workspaces", "list_templates", "open_workspace",
            "create_workspace", "rename_workspace", "duplicate_workspace", "delete_workspace",
            "save_as_template", "export_workspace", "import_workspace", "get_workspace_config",
            "update_workspace_config", "dat_tieu_de_cua_so", "recover_workspace"} <= set(cong_khai)
    for ten in cong_khai:
        status, kq = goi(ten)                    # thiếu đối số -> lỗi có cấu trúc, KHÔNG phải 404
        assert status == 200 and "ok" in kq or "errors" in kq, ten
    assert goi("get_workspace_state")[1]["data"]["slug"] == slug
    ds = goi("list_workspaces")[1]["data"]["workspaces"]
    assert [w["slug"] for w in ds] == [slug]
    ra = goi("create_workspace", "Công ty", {"industry": "company"})[1]
    assert ra["ok"], ra
    assert goi("open_workspace", ra["data"]["slug"])[1]["ok"]
    assert goi("get_workspace_state")[1]["data"]["config"]["industry"] == "company"
    assert api.db_path == ws.duong_dan_db(goc, ra["data"]["slug"])


# ===========================================================================
# G. Gói PyInstaller
# ===========================================================================

def _module_goc():
    return {f[:-3] for f in os.listdir(GOC) if f.endswith(".py")}


def _ma_nguon(ten):
    with open(os.path.join(GOC, ten + ".py"), encoding="utf-8") as f:
        return ast.parse(f.read())


def _bao_dong_tu_main():
    """Module Python ở thư mục gốc mà PyInstaller tìm thấy được khi phân tích tĩnh từ main.py
    (mọi câu `import`, ở bất kỳ phạm vi nào) và các lời nhập động còn sót."""
    co = _module_goc()
    thay, cho, dong = set(), ["main"], []
    while cho:
        m = cho.pop()
        if m in thay:
            continue
        thay.add(m)
        for n in ast.walk(_ma_nguon(m)):
            ten = []
            if isinstance(n, ast.Import):
                ten = [a.name.split(".")[0] for a in n.names]
            elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
                ten = [n.module.split(".")[0]]
            elif isinstance(n, ast.Call):
                f = n.func
                if getattr(f, "attr", getattr(f, "id", "")) in ("import_module", "__import__"):
                    dong.append((m, n.lineno))
            cho += [x for x in ten if x in co]
    return thay, dong


# Công cụ chạy tay của nhà phát triển, không thuộc phần mềm chạy.
CONG_CU_RIENG = {"tao_bao_cao_docx", "tao_i18n_js", "tao_logo"}


def test_moi_module_python_cua_phan_mem_deu_den_duoc_tu_main():
    thay, dong = _bao_dong_tu_main()
    assert dong == [], "nhập động không thấy được khi đóng gói: %s" % dong
    # Các module mới của tính năng workspace phải nằm trong bản đóng gói…
    assert {"workspace", "cau_hinh_ws", "nhan_ws", "api_workspace", "so_nhap", "so_excel",
            "browser_host", "recovery", "i18n_errors"} <= thay
    # …và không có module ở gốc bị bỏ quên (không ai kéo vào mà cũng không phải công cụ riêng).
    lac = _module_goc() - thay - CONG_CU_RIENG
    assert lac == set(), "module không được gói (không nhập từ main.py): %s" % sorted(lac)


def test_kiosk_spec_khong_loai_module_nao_cua_phan_mem():
    spec = open(os.path.join(GOC, "kiosk.spec"), encoding="utf-8").read()
    thay, _ = _bao_dong_tu_main()
    ds = re.search(r"excludes\s*=\s*\[([^\]]*)\]", spec).group(1)
    loai = set(re.findall(r'"([^"]+)"', ds))
    assert not (loai & thay), loai & thay
    # Phân tích bắt đầu từ main.py: nếu đổi điểm vào thì danh sách trên phải xét lại.
    assert re.search(r'Analysis\(\s*\["main.py"\]', spec)


def test_tep_js_khop_danh_sach_index_html_va_goi_nguyen_thu_muc():
    """`js/*.js` = `js/_danh_sach.txt` = các thẻ <script> của index.html (cùng thứ tự). Workflow
    build soát SHA256 MỌI tệp trong js/ nên tệp mồ côi (có mà không ai nạp) cũng đỏ build; còn
    kiosk.spec gói cả thư mục js/ một lần nên tệp mới không cần khai riêng."""
    tren_dia = sorted(t[:-3] for t in os.listdir(os.path.join(GOC, "js")) if t.endswith(".js"))
    with open(os.path.join(GOC, "js", "_danh_sach.txt"), encoding="utf-8") as f:
        danh_sach = [d.strip() for d in f if d.strip()]
    with open(os.path.join(GOC, "index.html"), encoding="utf-8") as f:
        the_script = re.findall(r'<script src="js/([^"]+)\.js"></script>', f.read())
    assert sorted(danh_sach) == tren_dia
    assert the_script == danh_sach
    assert "075_workspace" in danh_sach
    spec = open(os.path.join(GOC, "kiosk.spec"), encoding="utf-8").read()
    assert re.search(r'\("js",\s*"js"\)', spec)


def test_moi_ham_backend_ma_giao_dien_goi_deu_ton_tai():
    """Giao diện gọi `callApi("ten")` / `pywebview.api.ten`: tên gõ sai thì chỉ lộ ra khi bấm nút."""
    ten = set()
    for t in sorted(os.listdir(os.path.join(GOC, "js"))) + ["../chung.js", "../recovery.js"]:
        if not t.endswith(".js"):
            continue
        nguon = open(os.path.join(GOC, "js", t), encoding="utf-8").read()
        ten |= set(re.findall(r'callApi\(\s*["\']([A-Za-z_][A-Za-z0-9_]*)["\']', nguon))
        ten |= set(re.findall(r'pywebview\.api\.([A-Za-z_][A-Za-z0-9_]*)', nguon))
    assert "recover_workspace" in ten and "open_workspace" in ten
    from recovery import RecoveryAPI
    thieu = sorted(n for n in ten if not hasattr(PipelineAPI, n) and not hasattr(RecoveryAPI, n))
    assert thieu == []


# ===========================================================================
# H. Chạy với đường dẫn CSDL trong argv
# ===========================================================================

def test_argv_co_duong_dan_y_nhu_truoc_khi_co_workspace(tmp_path, monkeypatch):
    import main
    goc = tmp_path / "goc"
    goc.mkdir()
    (goc / "app.db").write_bytes(b"")                    # app.db cạnh chương trình: KHÔNG được di trú
    db = str(tmp_path / "rieng" / "du-lieu.db")
    os.makedirs(os.path.dirname(db))
    monkeypatch.setattr(main, "BASE_DIR", str(goc))
    monkeypatch.setattr(sys, "argv", ["main.py", db])
    mo = []
    monkeypatch.setattr(main, "_show_ui", lambda title, page, js_api, *a, **k: mo.append((title, page, js_api)))
    main.main()
    (tieu_de, trang, api), = mo
    assert trang == "index.html" and tieu_de == main.APP_TITLE
    assert api.db_path == os.path.abspath(db)
    assert api._goc_ws is None
    assert sorted(os.listdir(goc)) == ["app.db"]                       # không workspaces/, không ghi chú
    st = api.get_workspace_state()["data"]
    assert st["enabled"] is False and st["chon"] is True and st["slug"] is None
    for ten in ("list_workspaces", "list_templates"):
        r = getattr(api, ten)()
        assert not r["ok"] and r["errors"][0]["code"] == "ws_tat_che_do"
    for r in (api.open_workspace("x"), api.create_workspace("x"), api.recover_workspace("x"),
              api.import_workspace("")):
        assert not r["ok"] and r["errors"][0]["code"] == "ws_tat_che_do"
    # sao lưu và tệp CSV nằm cạnh CSDL được chỉ định, y như trước
    assert api.create_or_update_club("a", "A", 3, 0, "")["ok"]
    assert api.create_student_if_missing("s1", "S")["ok"] and api.submit_preferences("s1", ["a"])["ok"]
    assert api.run_pipeline(seed=1)["ok"]
    ten = sorted(os.listdir(os.path.dirname(db)))
    assert "du-lieu.db" in ten and "match_results.csv" in ten
    assert any(t.startswith("du-lieu.db.bak-") for t in ten)


def test_argv_ket_qua_trung_khit_voi_workspace_cung_du_lieu(tmp_path, monkeypatch):
    """Cùng dữ liệu, cùng seed: chạy bằng đường dẫn CSDL riêng và chạy trong workspace "Trường học"
    cho ra từng dòng match_results GIỐNG HỆT (bất biến 1)."""
    import shutil
    demo = os.path.join(GOC, "du_lieu_test", "app_DEMO_da_cham_diem.db")
    rieng = str(tmp_path / "rieng.db")
    shutil.copy(demo, rieng)
    a = PipelineAPI(rieng, thu_muc_xuat=str(tmp_path))
    goc = str(tmp_path / "goc")
    os.makedirs(goc)
    shutil.copy(demo, os.path.join(goc, "app.db"))
    assert ws.di_chuyen_db_cu(goc)
    b = PipelineAPI(ws.duong_dan_db(goc, "truong-hoc"), thu_muc_xuat=str(tmp_path), thu_muc_goc_ws=goc)
    for seed in (1, 2, 3):
        assert a.run_pipeline(seed=seed, force_redraw_stb=True)["ok"]
        assert b.run_pipeline(seed=seed, force_redraw_stb=True)["ok"]
        sql = "SELECT * FROM match_results ORDER BY student_id, buoi"
        with a._ket_noi_doc() as ca, b._ket_noi_doc() as cb:
            assert [tuple(r) for r in ca.execute(sql)] == [tuple(r) for r in cb.execute(sql)]
            # fetchall (không fetchone): câu SELECT còn dang dở giữ khoá đọc và chặn lần chạy sau
            assert ca.execute("SELECT luat_xep FROM run_history ORDER BY run_id DESC").fetchall()[0][0] is None
            assert cb.execute("SELECT luat_xep FROM run_history ORDER BY run_id DESC").fetchall()[0][0] is None


# ===========================================================================
# I. Tệp sinh ra nằm trong thư mục workspace ĐANG MỞ
# ===========================================================================

def _tat_ca_tep(goc):
    ra = []
    for thu, _, tep in os.walk(goc):
        ra += [os.path.relpath(os.path.join(thu, t), goc).replace(os.sep, "/") for t in tep]
    return sorted(ra)


def test_sao_luu_csv_va_ban_xuat_lui_nam_trong_workspace_dang_mo(goc, tmp_path, monkeypatch):
    import api_xuat
    monkeypatch.delenv("RBDA_THU_MUC_TAI_VE", raising=False)
    monkeypatch.setattr(api_xuat, "thu_muc_tai_ve", lambda: "")      # máy không có thư mục Tải xuống
    slugs = [ws.tao(goc, ten, None) for ten in ("Một", "Hai", "Ba")]
    api = PipelineAPI(ws.duong_dan_db(goc, slugs[0]), thu_muc_goc_ws=goc)   # KHÔNG chỉ định thu_muc_xuat
    for lan, slug in enumerate(slugs * 2):
        assert api.open_workspace(slug)["ok"]
        cid, sid = "c%d" % lan, "s%d" % lan
        assert api.create_or_update_club(cid, cid, 3, 0, "")["ok"]
        assert api.create_student_if_missing(sid, sid)["ok"]
        assert api.submit_preferences(sid, [cid])["ok"]
        assert api.run_pipeline(seed=lan % 3 + 1)["ok"]      # hạt giống đã khoá thì giữ nguyên
        r = api.export_csv()
        assert r["ok"], r["errors"]
        r = api.tao_so_nhap_mau()
        assert r["ok"], r["errors"]
        thu_muc = os.path.dirname(ws.duong_dan_db(goc, slug))
        assert os.path.dirname(r["data"]["path"]) == thu_muc
    tep = _tat_ca_tep(goc)
    assert [t for t in tep if "/" not in t] == []                    # không gì rơi ra ngoài thư mục gốc
    for slug in slugs:
        rieng = [t for t in tep if t.startswith("workspaces/%s/" % slug)]
        assert "workspaces/%s/match_results.csv" % slug in rieng
        assert any(t.startswith("workspaces/%s/app.db.bak-" % slug) for t in rieng)
        assert any(t.endswith("SO_NHAP_CLB.xlsx") or "SO_NHAP_CLB (" in t for t in rieng)
    # các bản xuất không bị trộn: match_results.csv của mỗi workspace chỉ có học sinh của nó
    import csv
    for i, slug in enumerate(slugs):
        with open(os.path.join(goc, "workspaces", slug, "match_results.csv"), encoding="utf-8-sig") as f:
            ids = {row[0] for row in csv.reader(f)} - {"student_id", "Mã học sinh", ""}
        assert ids <= {"s%d" % i, "s%d" % (i + 3)}, (slug, ids)
