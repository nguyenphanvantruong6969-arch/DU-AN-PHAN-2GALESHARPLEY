"""Thư mục workspace trên đĩa: workspace.py và cách main.py dùng nó."""

import json
import os
import sqlite3
import sys
import zipfile

import pytest

import cau_hinh_ws as cfgws
import workspace as w
from rbda_priority_pipeline import init_db


# ---------- tiện ích ----------

def _them_clb(db, club_id="A", ten="Cờ vua"):
    conn = sqlite3.connect(db)
    conn.execute(
        "INSERT INTO clubs (club_id, name, capacity) VALUES (?, ?, 10)",
        (club_id, ten))
    conn.commit()
    conn.close()


def _clb(db):
    conn = sqlite3.connect(db)
    try:
        return conn.execute(
            "SELECT club_id, name FROM clubs ORDER BY club_id").fetchall()
    finally:
        conn.close()


def _db_cu(root, voi_clb=True):
    """Dựng app.db kiểu BẢN CŨ: ngay trong root, chưa có bảng workspace_settings."""
    db = os.path.join(root, "app.db")
    init_db(db)
    if voi_clb:
        _them_clb(db)
    conn = sqlite3.connect(db)
    conn.execute("DROP TABLE workspace_settings")
    conn.commit()
    conn.close()
    return db


def _zip_tay(duong, muc):
    with zipfile.ZipFile(duong, "w") as z:
        for ten, noi_dung in muc.items():
            z.writestr(ten, noi_dung)
    return str(duong)


@pytest.fixture
def root(tmp_path):
    return str(tmp_path)


# ---------- tao / danh_sach ----------

def test_danh_sach_rong_khi_chua_co_thu_muc(root):
    assert w.danh_sach(root) == []


def test_tao_va_danh_sach(root):
    slug = w.tao(root, "Câu lạc bộ Đại học", {"industry": "custom"})
    assert slug == "cau-lac-bo-dai-hoc"
    (ws,) = w.danh_sach(root)
    assert ws["slug"] == slug
    assert ws["name"] == "Câu lạc bộ Đại học"
    assert ws["industry"] == "custom"
    assert ws["path"] == os.path.join(root, "workspaces", slug, "app.db")
    assert os.path.isfile(ws["path"])
    assert len(ws["modified"]) == 19 and ws["modified"][10] == "T"
    assert cfgws.doc_cau_hinh(ws["path"])["name"] == "Câu lạc bộ Đại học"


def test_tao_khong_cfg_dung_mac_dinh_truong_hoc(root):
    slug = w.tao(root, "Trường A")
    cfg = cfgws.doc_cau_hinh(os.path.join(root, "workspaces", slug, "app.db"))
    assert cfg == dict(cfgws.MAC_DINH_TRUONG_HOC, name="Trường A")


def test_ten_trong_cfg_thua_ten_tham_so(root):
    slug = w.tao(root, "Tên thật", {"name": "Tên khác"})
    assert w.danh_sach(root)[0]["name"] == "Tên thật"
    assert slug == "ten-that"


def test_slug_trung_them_hau_to(root):
    assert w.tao(root, "Trường Học") == "truong-hoc"
    assert w.tao(root, "truong hoc") == "truong-hoc-2"
    assert w.tao(root, "TRƯỜNG-HỌC!") == "truong-hoc-3"
    assert [x["slug"] for x in w.danh_sach(root)] == [
        "truong-hoc", "truong-hoc-2", "truong-hoc-3"]


def test_ten_toan_ky_hieu_van_co_slug(root):
    assert w.tao(root, "(***)") == "workspace"
    assert w.tao(root, "???") == "workspace-2"


def test_ten_rat_dai_bi_cat(root):
    slug = w.tao(root, "a" * 300)
    assert len(slug) <= 60


@pytest.mark.parametrize("ten", ["", "   ", None])
def test_ten_trong_bi_tu_choi_va_khong_tao_gi(root, ten):
    with pytest.raises(ValueError):
        w.tao(root, ten)
    assert not os.path.exists(os.path.join(root, "workspaces"))


def test_cfg_sai_khong_de_lai_thu_muc(root):
    with pytest.raises(ValueError, match="max_choices"):
        w.tao(root, "X", {"rules": {"max_choices": 99}})
    assert w.danh_sach(root) == []
    assert not os.path.exists(os.path.join(root, "workspaces", "x"))


def test_danh_sach_bo_qua_trash_va_thu_muc_khong_co_db(root):
    w.tao(root, "Một")
    ws = os.path.join(root, "workspaces")
    os.makedirs(os.path.join(ws, "_trash", "cu-20200101-000000"))
    os.makedirs(os.path.join(ws, "_nhap_tam"))
    os.makedirs(os.path.join(ws, "rong"))
    assert [x["slug"] for x in w.danh_sach(root)] == ["mot"]


def test_danh_sach_van_liet_ke_db_hong(root):
    slug = w.tao(root, "Hỏng")
    db = os.path.join(root, "workspaces", slug, "app.db")
    with open(db, "wb") as f:
        f.write(b"khong phai sqlite")
    (ws,) = w.danh_sach(root)
    assert ws["slug"] == slug and ws["name"] == slug


# ---------- doi_ten ----------

def test_doi_ten_giu_nguyen_slug(root):
    slug = w.tao(root, "Tên cũ", {"rules": {"max_choices": 4}})
    w.doi_ten(root, slug, "Tên mới")
    (ws,) = w.danh_sach(root)
    assert ws["slug"] == slug and ws["name"] == "Tên mới"
    assert cfgws.doc_cau_hinh(ws["path"])["rules"]["max_choices"] == 4


def test_doi_ten_sai(root):
    slug = w.tao(root, "A")
    with pytest.raises(ValueError):
        w.doi_ten(root, slug, "  ")
    with pytest.raises(ValueError):
        w.doi_ten(root, "khong-co", "B")


@pytest.mark.parametrize("slug", ["../x", "..", "a/b", "A", "", "_trash", None])
def test_slug_xau_bi_tu_choi_khong_thoat_khoi_workspaces(root, slug):
    w.tao(root, "A")
    for ham in (lambda: w.doi_ten(root, slug, "B"),
                lambda: w.xoa(root, slug),
                lambda: w.nhan_ban(root, slug, "B", True),
                lambda: w.luu_mau(root, slug, "M"),
                lambda: w.xuat_zip(root, slug, os.path.join(root, "z.zip"))):
        with pytest.raises(ValueError):
            ham()


# ---------- xoa ----------

def test_xoa_dom_vao_trash_va_co_ban_sao_luu(root):
    slug = w.tao(root, "Sẽ xoá")
    db = os.path.join(root, "workspaces", slug, "app.db")
    _them_clb(db)
    rac = w.xoa(root, slug)
    assert w.danh_sach(root) == []
    assert not os.path.exists(os.path.join(root, "workspaces", slug))
    assert os.path.dirname(rac) == os.path.join(root, "workspaces", "_trash")
    assert os.path.basename(rac).startswith(slug + "-")
    sao_luu = [f for f in os.listdir(rac) if f.startswith("app.db.bak-")]
    assert len(sao_luu) == 1
    # bản sao lưu đọc được và còn dữ liệu; app.db gốc cũng còn nguyên trong thùng
    assert _clb(os.path.join(rac, sao_luu[0])) == [("A", "Cờ vua")]
    assert _clb(os.path.join(rac, "app.db")) == [("A", "Cờ vua")]


def test_xoa_hai_lan_cung_slug_khong_de_nhau(root):
    r1 = w.xoa(root, w.tao(root, "Lặp"))
    r2 = w.xoa(root, w.tao(root, "Lặp"))
    assert r1 != r2 and os.path.isdir(r1) and os.path.isdir(r2)


def test_xoa_db_hong_van_xoa_duoc_va_giu_ban_sao(root):
    slug = w.tao(root, "Hỏng")
    db = os.path.join(root, "workspaces", slug, "app.db")
    with open(db, "wb") as f:
        f.write(b"khong phai sqlite")
    rac = w.xoa(root, slug)
    assert any(f.startswith("app.db.bak-") for f in os.listdir(rac))


def test_xoa_slug_khong_co(root):
    with pytest.raises(ValueError):
        w.xoa(root, "khong-co")


# ---------- nhan_ban ----------

def test_nhan_ban_kem_du_lieu(root):
    slug = w.tao(root, "Gốc", {"rules": {"max_choices": 3}})
    _them_clb(os.path.join(root, "workspaces", slug, "app.db"))
    moi = w.nhan_ban(root, slug, "Bản chép", True)
    assert moi == "ban-chep"
    db = os.path.join(root, "workspaces", moi, "app.db")
    assert _clb(db) == [("A", "Cờ vua")]
    cfg = cfgws.doc_cau_hinh(db)
    assert cfg["name"] == "Bản chép" and cfg["rules"]["max_choices"] == 3
    # gốc không bị đụng
    assert cfgws.doc_cau_hinh(
        os.path.join(root, "workspaces", slug, "app.db"))["name"] == "Gốc"


def test_nhan_ban_khong_du_lieu(root):
    slug = w.tao(root, "Gốc", {"rules": {"max_choices": 3}, "industry": "event"})
    _them_clb(os.path.join(root, "workspaces", slug, "app.db"))
    moi = w.nhan_ban(root, slug, "Bản trống", False)
    db = os.path.join(root, "workspaces", moi, "app.db")
    assert _clb(db) == []
    cfg = cfgws.doc_cau_hinh(db)
    assert cfg["name"] == "Bản trống"
    assert cfg["rules"]["max_choices"] == 3 and cfg["industry"] == "event"
    assert _clb(os.path.join(root, "workspaces", slug, "app.db")) != []


def test_nhan_ban_trung_ten_them_hau_to(root):
    slug = w.tao(root, "Gốc")
    assert w.nhan_ban(root, slug, "Gốc", True) == "goc-2"
    assert w.nhan_ban(root, slug, "Gốc", False) == "goc-3"


def test_nhan_ban_nguon_hong_khong_de_lai_thu_muc(root):
    slug = w.tao(root, "Gốc")
    with open(os.path.join(root, "workspaces", slug, "app.db"), "wb") as f:
        f.write(b"khong phai sqlite")
    with pytest.raises(Exception):
        w.nhan_ban(root, slug, "Bản", True)
    assert [x["slug"] for x in w.danh_sach(root)] == [slug]
    assert not os.path.exists(os.path.join(root, "workspaces", "ban"))


# ---------- mẫu ----------

def test_danh_sach_mau_luon_co_mau_truong_hoc(root):
    (mau,) = w.danh_sach_mau(root)
    assert mau["builtin"] is True and mau["name"] == "Trường học"
    assert mau["config"]["rules"] == cfgws.MAC_DINH_TRUONG_HOC["rules"]
    assert mau["config"]["labels"] == cfgws.MAC_DINH_TRUONG_HOC["labels"]


def test_luu_mau_chi_ghi_cau_hinh(root):
    slug = w.tao(root, "Công ty", {
        "industry": "company",
        "labels": {"person": {"vi": "Nhân viên", "en": "Employee"}},
        "rules": {"max_choices": 5}})
    _them_clb(os.path.join(root, "workspaces", slug, "app.db"))
    ms = w.luu_mau(root, slug, "Mẫu công ty")
    assert ms == "mau-cong-ty"
    tep = os.path.join(root, "templates", "mau-cong-ty.json")
    with open(tep, encoding="utf-8") as f:
        noi_dung = json.load(f)
    assert noi_dung["name"] == "Mẫu công ty"
    assert noi_dung["rules"]["max_choices"] == 5
    assert "Cờ vua" not in json.dumps(noi_dung, ensure_ascii=False)  # không dữ liệu
    ds = w.danh_sach_mau(root)
    assert [m["slug"] for m in ds] == ["truong-hoc", "mau-cong-ty"]
    mau = ds[1]
    assert mau["builtin"] is False and mau["industry"] == "company"
    # dùng được ngay để tạo workspace mới
    moi = w.tao(root, "Công ty B", mau["config"])
    cfg = cfgws.doc_cau_hinh(
        os.path.join(root, "workspaces", moi, "app.db"))
    assert cfg["labels"]["person"]["en"] == "Employee" and cfg["name"] == "Công ty B"


def test_luu_mau_cung_ten_ghi_de_va_khong_chiem_slug_dung_san(root):
    slug = w.tao(root, "A")
    w.luu_mau(root, slug, "Mẫu")
    w.doi_ten(root, slug, "A2")
    w.luu_mau(root, slug, "Mẫu")
    assert len(os.listdir(os.path.join(root, "templates"))) == 1
    assert w.luu_mau(root, slug, "Trường học") == "truong-hoc-2"
    ds = w.danh_sach_mau(root)
    assert ds[0]["builtin"] is True and sum(m["builtin"] for m in ds) == 1


def test_mau_hong_bi_bo_qua(root):
    os.makedirs(os.path.join(root, "templates"))
    with open(os.path.join(root, "templates", "hong.json"), "w") as f:
        f.write("{khong phai json")
    with open(os.path.join(root, "templates", "sai.json"), "w") as f:
        f.write('{"rules": {"max_choices": 99}}')
    assert [m["slug"] for m in w.danh_sach_mau(root)] == ["truong-hoc"]


# ---------- zip ----------

def test_zip_khu_hoi(root, tmp_path):
    slug = w.tao(root, "Xuất", {"rules": {"max_choices": 6}})
    _them_clb(os.path.join(root, "workspaces", slug, "app.db"))
    dich = str(tmp_path / "ra" / "xuat.zip")
    assert w.xuat_zip(root, slug, dich) == dich
    with zipfile.ZipFile(dich) as z:
        assert z.namelist() == ["app.db"]
    root2 = str(tmp_path / "may_khac")
    moi = w.nhap_zip(root2, dich)
    assert moi == "xuat"
    db = os.path.join(root2, "workspaces", moi, "app.db")
    assert _clb(db) == [("A", "Cờ vua")]
    cfg = cfgws.doc_cau_hinh(db)
    assert cfg["name"] == "Xuất" and cfg["rules"]["max_choices"] == 6
    assert not os.path.exists(dich + ".tmp")
    # không rác: chỉ còn đúng thư mục workspace
    assert os.listdir(os.path.join(root2, "workspaces")) == [moi]


def test_nhap_zip_trung_slug_doi_ten_nhu_tao(root, tmp_path):
    slug = w.tao(root, "Trùng")
    dich = str(tmp_path / "t.zip")
    w.xuat_zip(root, slug, dich)
    assert w.nhap_zip(root, dich) == "trung-2"
    assert w.nhap_zip(root, dich) == "trung-3"
    assert len(w.danh_sach(root)) == 3


@pytest.mark.parametrize("ten", [
    "../evil.db", "a/../../evil.db", "/abs/evil.db", "\\abs\\evil.db",
    "C:\\evil.db", "C:/evil.db", "..\\evil.db", "x\\..\\..\\evil.db",
])
def test_zip_slip_bi_tu_choi(root, tmp_path, ten):
    slug = w.tao(root, "Hợp lệ")
    db = os.path.join(root, "workspaces", slug, "app.db")
    with open(db, "rb") as f:
        db_bytes = f.read()
    z = _zip_tay(tmp_path / "xau.zip", {"app.db": db_bytes, ten: b"x"})
    truoc = sorted(os.listdir(os.path.join(root, "workspaces")))
    with pytest.raises(ValueError, match="không an toàn"):
        w.nhap_zip(root, z)
    assert sorted(os.listdir(os.path.join(root, "workspaces"))) == truoc
    assert not os.path.exists(os.path.join(os.path.dirname(root), "evil.db"))


def test_zip_slip_voi_app_db_la_muc_xau(root, tmp_path):
    z = _zip_tay(tmp_path / "xau.zip", {"../app.db": b"x"})
    with pytest.raises(ValueError, match="không an toàn"):
        w.nhap_zip(root, z)


def test_zip_khong_co_app_db(root, tmp_path):
    z = _zip_tay(tmp_path / "thieu.zip", {"readme.txt": b"hi", "a/b/app.db": b"x"})
    with pytest.raises(ValueError, match="app.db"):
        w.nhap_zip(root, z)


@pytest.mark.parametrize("noi_dung", [b"khong phai sqlite", b"SQLite format 3\x00" + b"x" * 200])
def test_zip_app_db_hong(root, tmp_path, noi_dung):
    z = _zip_tay(tmp_path / "h.zip", {"app.db": noi_dung})
    with pytest.raises(ValueError):
        w.nhap_zip(root, z)
    assert w.danh_sach(root) == []
    assert os.listdir(os.path.join(root, "workspaces")) == []  # không rác tạm


def test_zip_sqlite_la_khong_phai_cua_phan_mem(root, tmp_path):
    la = str(tmp_path / "la.db")
    c = sqlite3.connect(la)
    c.execute("CREATE TABLE khac (x)")
    c.commit()
    c.close()
    with open(la, "rb") as f:
        z = _zip_tay(tmp_path / "la.zip", {"app.db": f.read()})
    with pytest.raises(ValueError, match="không phải CSDL của phần mềm"):
        w.nhap_zip(root, z)


def test_tep_khong_phai_zip(root, tmp_path):
    p = tmp_path / "x.zip"
    p.write_bytes(b"khong phai zip")
    with pytest.raises(ValueError):
        w.nhap_zip(root, str(p))
    with pytest.raises(ValueError):
        w.nhap_zip(root, str(tmp_path / "khong_co.zip"))


def test_zip_nen_trong_mot_thu_muc_va_db_cu_duoc_nang_cap(root, tmp_path):
    cu = _db_cu(str(tmp_path), voi_clb=True)  # thiếu workspace_settings
    with open(cu, "rb") as f:
        z = _zip_tay(tmp_path / "t.zip", {"Truong cu/app.db": f.read(),
                                          "Truong cu/ghi_chu.txt": b"bo qua"})
    slug = w.nhap_zip(root, z)
    assert slug == "t"  # cấu hình chưa có tên -> lấy tên tệp zip
    db = os.path.join(root, "workspaces", slug, "app.db")
    assert _clb(db) == [("A", "Cờ vua")]
    assert cfgws.doc_cau_hinh(db)["name"] == "t"
    assert os.listdir(os.path.join(root, "workspaces", slug)) == ["app.db"]


# ---------- di_chuyen_db_cu ----------

def test_di_chuyen_giu_du_lieu(root):
    _db_cu(root)
    with open(os.path.join(root, "app.db.bak-20250101_000000_000000"), "wb") as f:
        f.write(b"ban sao luu")
    assert w.di_chuyen_db_cu(root) == "truong-hoc"
    dich = os.path.join(root, "workspaces", "truong-hoc")
    assert not os.path.exists(os.path.join(root, "app.db"))
    assert not os.path.exists(os.path.join(root, "app.db.bak-20250101_000000_000000"))
    assert sorted(os.listdir(dich)) == [
        "app.db", "app.db.bak-20250101_000000_000000"]
    assert _clb(os.path.join(dich, "app.db")) == [("A", "Cờ vua")]
    assert cfgws.doc_cau_hinh(os.path.join(dich, "app.db"))["name"] == "Trường học"
    (ws,) = w.danh_sach(root)
    assert ws["slug"] == "truong-hoc" and ws["name"] == "Trường học"
    ghi_chu = os.path.join(root, "DA_CHUYEN_SANG_WORKSPACES.txt")
    with open(ghi_chu, encoding="utf-8-sig") as f:
        assert "workspaces" in f.read()
    # thư mục tạm không còn
    assert not os.path.exists(os.path.join(root, "_dang_chuyen_workspaces"))


def test_di_chuyen_chay_hai_lan_an_toan(root):
    _db_cu(root)
    assert w.di_chuyen_db_cu(root) == "truong-hoc"
    db = os.path.join(root, "workspaces", "truong-hoc", "app.db")
    _them_clb(db, "B", "Bóng đá")
    truoc = _clb(db)
    assert w.di_chuyen_db_cu(root) is None
    assert w.di_chuyen_db_cu(root) is None
    assert _clb(db) == truoc
    assert [x["slug"] for x in w.danh_sach(root)] == ["truong-hoc"]


def test_di_chuyen_khong_lam_gi_khi_khong_co_db_cu(root):
    assert w.di_chuyen_db_cu(root) is None
    assert not os.path.exists(os.path.join(root, "workspaces"))
    assert not os.path.exists(os.path.join(root, "_dang_chuyen_workspaces"))
    assert not os.path.exists(os.path.join(root, "DA_CHUYEN_SANG_WORKSPACES.txt"))


def test_di_chuyen_khong_lam_gi_khi_da_co_workspaces(root):
    w.tao(root, "Mới")
    cu = _db_cu(root)
    assert w.di_chuyen_db_cu(root) is None
    assert os.path.isfile(cu)  # db cũ để nguyên, không bị đụng
    assert [x["slug"] for x in w.danh_sach(root)] == ["moi"]


def test_di_chuyen_dem_theo_ca_tep_phu_journal(root, monkeypatch):
    """`-journal` phải đi cùng app.db TRƯỚC khi SQLite mở nó lần đầu ở chỗ mới
    (journal nóng được phát lại khi mở; bỏ lại thì mất bước hoàn tác)."""
    _db_cu(root)
    with open(os.path.join(root, "app.db-journal"), "wb") as f:
        f.write(b"nhat ky")
    thay = {}
    ghi_that = w.ghi_cau_hinh

    def ghi_theo_doi(db, cfg):
        thay["tep"] = sorted(os.listdir(os.path.dirname(db)))
        return ghi_that(db, cfg)

    monkeypatch.setattr(w, "ghi_cau_hinh", ghi_theo_doi)
    w.di_chuyen_db_cu(root)
    assert thay["tep"] == ["app.db", "app.db-journal"]
    assert not os.path.exists(os.path.join(root, "app.db-journal"))


def test_di_chuyen_lam_tiep_sau_khi_bi_ngat(root):
    """Sập sau khi dời app.db nhưng trước khi tạo workspaces/ -> lần sau làm tiếp."""
    _db_cu(root)
    with open(os.path.join(root, "app.db.bak-1"), "wb") as f:
        f.write(b"ban sao luu")
    tam = os.path.join(root, "_dang_chuyen_workspaces", "truong-hoc")
    os.makedirs(tam)
    os.replace(os.path.join(root, "app.db"), os.path.join(tam, "app.db"))
    assert not os.path.exists(os.path.join(root, "workspaces"))
    assert w.di_chuyen_db_cu(root) == "truong-hoc"
    dich = os.path.join(root, "workspaces", "truong-hoc")
    assert sorted(os.listdir(dich)) == ["app.db", "app.db.bak-1"]
    assert _clb(os.path.join(dich, "app.db")) == [("A", "Cờ vua")]


def test_di_chuyen_khong_ghi_de_db_da_dang_chuyen(root):
    """Lần sau có app.db TRỐNG mới ở root (vd 'bắt đầu mới') thì không đè bản thật."""
    _db_cu(root)
    tam = os.path.join(root, "_dang_chuyen_workspaces", "truong-hoc")
    os.makedirs(tam)
    os.replace(os.path.join(root, "app.db"), os.path.join(tam, "app.db"))
    init_db(os.path.join(root, "app.db"))  # app.db rỗng mới
    w.di_chuyen_db_cu(root)
    assert _clb(os.path.join(root, "workspaces", "truong-hoc", "app.db")) == [
        ("A", "Cờ vua")]


def test_di_chuyen_db_hong_van_dem_di(root):
    with open(os.path.join(root, "app.db"), "wb") as f:
        f.write(b"khong phai sqlite")
    assert w.di_chuyen_db_cu(root) == "truong-hoc"
    with open(os.path.join(root, "workspaces", "truong-hoc", "app.db"), "rb") as f:
        assert f.read() == b"khong phai sqlite"


# ---------- tim_workspace_hong + main ----------

def test_tim_workspace_hong(root):
    assert w.tim_workspace_hong(root) is None
    w.tao(root, "Tốt")
    assert w.tim_workspace_hong(root) is None
    xau = w.tao(root, "Xấu")
    db = os.path.join(root, "workspaces", xau, "app.db")
    with open(db, "wb") as f:
        f.write(b"khong phai sqlite")
    duong, loi = w.tim_workspace_hong(root)
    assert duong == db and isinstance(loi, sqlite3.DatabaseError)


@pytest.fixture
def main_mod(monkeypatch, tmp_path):
    import main

    monkeypatch.setattr(main, "BASE_DIR", str(tmp_path))
    mo = []
    monkeypatch.setattr(
        main, "_show_ui", lambda title, page, api, **k: mo.append((page, api)))
    return main, mo


def test_main_khong_tham_so_chuyen_db_cu_va_chua_mo_workspace_nao(
        main_mod, monkeypatch, tmp_path):
    main, mo = main_mod
    monkeypatch.setattr(sys, "argv", ["main.py"])
    _db_cu(str(tmp_path))
    main.main()
    page, api = mo[0]
    assert page == "index.html"
    assert api.db_path is None  # màn chọn workspace sẽ mở (js/075_workspace.js)
    assert not (tmp_path / "app.db").exists()
    assert _clb(str(tmp_path / "workspaces" / "truong-hoc" / "app.db")) == [
        ("A", "Cờ vua")]
    r = api.list_workspaces()
    assert r["ok"] and r["data"]["current"] is None
    assert [x["slug"] for x in r["data"]["items"]] == ["truong-hoc"]


def test_main_khong_tham_so_va_chua_co_gi(main_mod, monkeypatch, tmp_path):
    main, mo = main_mod
    monkeypatch.setattr(sys, "argv", ["main.py"])
    main.main()
    assert mo[0][0] == "index.html"
    assert mo[0][1].list_workspaces()["data"]["items"] == []


def test_main_co_tham_so_khong_dung_den_workspace(main_mod, monkeypatch, tmp_path):
    main, mo = main_mod
    _db_cu(str(tmp_path))  # app.db cũ ở thư mục chương trình: không được đụng
    dang_ky = tmp_path / "rieng" / "khac.db"
    dang_ky.parent.mkdir()
    monkeypatch.setattr(sys, "argv", ["main.py", str(dang_ky)])
    main.main()
    assert mo[0][0] == "index.html"
    assert mo[0][1].db_path == str(dang_ky)
    assert mo[0][1].list_workspaces()["errors"][0]["code"] == "ws_disabled"
    assert not (tmp_path / "workspaces").exists()
    assert (tmp_path / "app.db").exists()
    assert not (tmp_path / "DA_CHUYEN_SANG_WORKSPACES.txt").exists()


def test_main_workspace_hong_ra_man_hinh_phuc_hoi_dung_tep(
        main_mod, monkeypatch, tmp_path):
    main, mo = main_mod
    monkeypatch.setattr(sys, "argv", ["main.py"])
    slug = w.tao(str(tmp_path), "Hỏng")
    db = tmp_path / "workspaces" / slug / "app.db"
    db.write_bytes(b"khong phai sqlite")
    main.main()
    page, api = mo[0]
    assert page == "recovery.html"
    assert type(api).__name__ == "RecoveryAPI"
    assert api.db_path == str(db)


def test_main_loi_chuan_bi_workspace_ra_man_hinh_phuc_hoi(main_mod, monkeypatch):
    main, mo = main_mod
    monkeypatch.setattr(sys, "argv", ["main.py"])

    def hong(root):
        raise OSError("thu muc chi doc")

    monkeypatch.setattr(main.workspace, "di_chuyen_db_cu", hong)
    main.main()
    assert mo[0][0] == "recovery.html"
