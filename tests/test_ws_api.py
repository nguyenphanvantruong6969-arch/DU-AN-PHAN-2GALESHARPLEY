"""API workspace của PipelineAPI (api_workspace.py)."""

import base64
import io
import os
import sqlite3
import threading
import zipfile

import pytest

import cau_hinh_ws as cfgws
import workspace as w
from api import PipelineAPI
from i18n_errors import MESSAGES


@pytest.fixture
def root(tmp_path):
    return str(tmp_path / "goc")


@pytest.fixture
def xuat(tmp_path):
    p = tmp_path / "xuat"
    p.mkdir()
    return str(p)


@pytest.fixture
def api_ws(root, xuat):
    """PipelineAPI ở chế độ workspace, chưa mở workspace nào."""
    os.makedirs(root)
    return PipelineAPI(None, thu_muc_xuat=xuat, thu_muc_goc=root)


def ma_loi(res):
    assert res["ok"] is False and res["data"] is None
    return res["errors"][0]["code"]


def _tao(api, ten, cfg=None):
    res = api.create_workspace(ten, cfg)
    assert res["ok"], res
    return res["data"]["slug"]


def _b64(duong):
    with open(duong, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ---------- chế độ tắt ----------

def test_che_do_csdl_don_moi_ham_workspace_bao_tat(api, xuat):
    cuoc_goi = [
        lambda: api.list_workspaces(),
        lambda: api.list_templates(),
        lambda: api.open_workspace("a"),
        lambda: api.create_workspace("A", {}),
        lambda: api.rename_workspace("a", "B"),
        lambda: api.delete_workspace("a", "XOA"),
        lambda: api.duplicate_workspace("a", "B", True),
        lambda: api.save_as_template("a", "M"),
        lambda: api.export_workspace("a"),
        lambda: api.import_workspace("eA=="),
        lambda: api.get_workspace_config(),
        lambda: api.update_workspace_config({}),
    ]
    db_truoc = api.db_path
    for goi in cuoc_goi:
        assert ma_loi(goi()) == "ws_disabled"
    assert api.db_path == db_truoc
    assert not os.path.exists(os.path.join(os.path.dirname(db_truoc), "workspaces"))


def test_ma_loi_workspace_co_ban_dich_vi_va_en():
    for ma in ("ws_disabled", "ws_not_found", "ws_none_open", "ws_name_required",
               "ws_delete_confirmation_mismatch", "ws_invalid", "ws_zip_invalid",
               "error_workspace"):
        assert MESSAGES[ma]["vi"] and MESSAGES[ma]["en"], ma


def test_none_chi_hop_le_o_che_do_workspace(tmp_path):
    with pytest.raises(ValueError):
        PipelineAPI(None)


def test_ham_workspace_la_ham_cong_khai_nhung_trang_thai_thi_khong():
    cong_khai = {n for n in dir(PipelineAPI) if not n.startswith("_")}
    for ten in ("list_workspaces", "open_workspace", "create_workspace",
                "rename_workspace", "delete_workspace", "duplicate_workspace",
                "save_as_template", "export_workspace", "import_workspace",
                "get_workspace_config", "update_workspace_config",
                "list_templates"):
        assert ten in cong_khai
    # pywebview đưa mọi tên không có '_' đầu lên giao diện
    assert not {n for n in cong_khai if n.startswith("ws")}


# ---------- danh sách / tạo ----------

def test_chua_mo_workspace_nao(api_ws):
    res = api_ws.list_workspaces()
    assert res == {"ok": True, "data": {"current": None, "items": []}, "errors": []}
    assert api_ws.db_path is None


def test_tao_roi_liet_ke_khong_tu_mo(api_ws):
    slug = _tao(api_ws, "Trường A", {"industry": "custom"})
    assert slug == "truong-a"
    d = api_ws.list_workspaces()["data"]
    assert d["current"] is None
    (it,) = d["items"]
    assert (it["slug"], it["name"], it["industry"]) == (
        "truong-a", "Trường A", "custom")
    assert api_ws.db_path is None


def test_tao_trung_ten_them_hau_to(api_ws):
    assert _tao(api_ws, "A") == "a"
    assert _tao(api_ws, "A") == "a-2"


def test_tao_cau_hinh_sai_hoac_ten_trong(api_ws):
    res = api_ws.create_workspace("X", {"rules": {"max_choices": 99}})
    assert ma_loi(res) == "ws_invalid"
    assert "max_choices" in res["errors"][0]["params"]["detail"]
    for ten in ("", "  ", None):
        assert ma_loi(api_ws.create_workspace(ten, {})) == "ws_name_required"
    assert api_ws.list_workspaces()["data"]["items"] == []


# ---------- mở ----------

def test_mo_workspace_doi_db_path_va_tra_cau_hinh(api_ws, root):
    slug = _tao(api_ws, "Công ty", {"rules": {"max_choices": 4}})
    res = api_ws.open_workspace(slug)
    assert res["ok"]
    assert res["data"]["slug"] == slug and res["data"]["name"] == "Công ty"
    assert res["data"]["config"]["rules"]["max_choices"] == 4
    assert api_ws.db_path == os.path.join(root, "workspaces", slug, "app.db")
    assert api_ws.list_workspaces()["data"]["current"] == slug


def test_mo_nang_luoc_do_csdl_cu(api_ws, root):
    slug = _tao(api_ws, "Cũ")
    db = os.path.join(root, "workspaces", slug, "app.db")
    conn = sqlite3.connect(db)
    conn.execute("DROP TABLE workspace_settings")
    conn.execute("DROP TABLE dau_van_tay_chay")
    conn.commit()
    conn.close()
    res = api_ws.open_workspace(slug)
    assert res["ok"]
    assert res["data"]["config"] == dict(cfgws.MAC_DINH_TRUONG_HOC)
    conn = sqlite3.connect(db)
    ten = {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}
    conn.close()
    assert {"workspace_settings", "dau_van_tay_chay"} <= ten


def test_du_lieu_hai_workspace_tach_biet(api_ws):
    a, b = _tao(api_ws, "A"), _tao(api_ws, "B")
    api_ws.open_workspace(a)
    assert api_ws.create_or_update_club("clb_a", "CLB A", 3, 0, "")["ok"]
    api_ws.open_workspace(b)
    assert api_ws.list_clubs_admin()["data"] == []
    assert api_ws.create_or_update_club("clb_b", "CLB B", 5, 0, "")["ok"]
    api_ws.open_workspace(a)
    assert [c["club_id"] for c in api_ws.list_clubs_admin()["data"]] == ["clb_a"]
    api_ws.open_workspace(b)
    assert [c["club_id"] for c in api_ws.list_clubs_admin()["data"]] == ["clb_b"]


def test_mo_xoa_bo_nho_dem_xuat(api_ws):
    slug = _tao(api_ws, "A")
    api_ws._bo_nho_xuat = {("x",): 1}
    api_ws.open_workspace(slug)
    assert api_ws._bo_nho_xuat is None


@pytest.mark.parametrize("slug", ["khong-co", "../x", "", None, "_trash"])
def test_mo_sai_ma_giu_nguyen_workspace_dang_mo(api_ws, slug):
    dang_mo = _tao(api_ws, "Đang mở")
    api_ws.open_workspace(dang_mo)
    db = api_ws.db_path
    assert ma_loi(api_ws.open_workspace(slug)) == "ws_not_found"
    assert api_ws.db_path == db
    assert api_ws.list_workspaces()["data"]["current"] == dang_mo


def test_mo_csdl_hong_bao_loi_va_giu_nguyen(api_ws, root):
    tot, xau = _tao(api_ws, "Tốt"), _tao(api_ws, "Xấu")
    with open(os.path.join(root, "workspaces", xau, "app.db"), "wb") as f:
        f.write(b"khong phai sqlite")
    api_ws.open_workspace(tot)
    db = api_ws.db_path
    assert ma_loi(api_ws.open_workspace(xau)) == "error_workspace"
    assert api_ws.db_path == db


def test_mo_cho_khoa_ghi_nen_khong_doi_giua_luc_dang_ghi(api_ws):
    a, b = _tao(api_ws, "A"), _tao(api_ws, "B")
    api_ws.open_workspace(a)
    db_a = api_ws.db_path
    da_vao, cho_xong = threading.Event(), threading.Event()
    thay = {}

    def giu_khoa():
        with api_ws._khoa_ghi:         # như run_pipeline đang chạy
            da_vao.set()
            cho_xong.wait(5)
            thay["db_trong_luc_giu"] = api_ws.db_path

    t1 = threading.Thread(target=giu_khoa)
    t1.start()
    assert da_vao.wait(5)
    t2 = threading.Thread(target=lambda: api_ws.open_workspace(b))
    t2.start()
    t2.join(0.4)
    assert t2.is_alive(), "open_workspace phải chờ khoá ghi"
    cho_xong.set()
    t1.join(5)
    t2.join(5)
    assert thay["db_trong_luc_giu"] == db_a
    assert api_ws.db_path != db_a


# ---------- đổi tên / nhân bản ----------

def test_doi_ten_giu_slug_va_cap_nhat_tieu_de(api_ws):
    slug = _tao(api_ws, "Cũ")
    api_ws.open_workspace(slug)
    assert api_ws.rename_workspace(slug, "  Mới  ")["data"] == {
        "slug": slug, "name": "Mới"}
    (it,) = api_ws.list_workspaces()["data"]["items"]
    assert it["slug"] == slug and it["name"] == "Mới"
    assert api_ws.get_workspace_config()["data"]["name"] == "Mới"


def test_doi_ten_sai(api_ws):
    slug = _tao(api_ws, "A")
    assert ma_loi(api_ws.rename_workspace(slug, " ")) == "ws_name_required"
    assert ma_loi(api_ws.rename_workspace("khong-co", "B")) == "ws_not_found"


def test_nhan_ban_co_va_khong_du_lieu(api_ws):
    goc = _tao(api_ws, "Gốc", {"rules": {"max_choices": 3}})
    api_ws.open_workspace(goc)
    api_ws.create_or_update_club("clb_a", "CLB A", 3, 0, "")
    co = api_ws.duplicate_workspace(goc, "Có dữ liệu", True)["data"]["slug"]
    khong = api_ws.duplicate_workspace(goc, "Không dữ liệu", False)["data"]["slug"]
    assert api_ws.db_path.endswith(os.path.join(goc, "app.db"))  # không tự mở
    api_ws.open_workspace(co)
    assert [c["club_id"] for c in api_ws.list_clubs_admin()["data"]] == ["clb_a"]
    assert api_ws.get_workspace_config()["data"]["rules"]["max_choices"] == 3
    api_ws.open_workspace(khong)
    assert api_ws.list_clubs_admin()["data"] == []
    cfg = api_ws.get_workspace_config()["data"]
    assert cfg["rules"]["max_choices"] == 3 and cfg["name"] == "Không dữ liệu"


def test_nhan_ban_mac_dinh_la_kem_du_lieu(api_ws):
    goc = _tao(api_ws, "Gốc")
    api_ws.open_workspace(goc)
    api_ws.create_or_update_club("clb_a", "CLB A", 3, 0, "")
    moi = api_ws.duplicate_workspace(goc, "Bản sao")["data"]["slug"]
    api_ws.open_workspace(moi)
    assert len(api_ws.list_clubs_admin()["data"]) == 1


def test_nhan_ban_sai(api_ws):
    goc = _tao(api_ws, "Gốc")
    assert ma_loi(api_ws.duplicate_workspace(goc, "", True)) == "ws_name_required"
    assert ma_loi(api_ws.duplicate_workspace("khong-co", "B", True)) == "ws_not_found"


# ---------- xoá ----------

@pytest.mark.parametrize("xac_nhan", ["", "xoa", "XOA ", None, "DELETE"])
def test_xoa_thieu_xac_nhan_khong_lam_gi(api_ws, root, xac_nhan):
    slug = _tao(api_ws, "A")
    assert ma_loi(api_ws.delete_workspace(slug, xac_nhan)) == \
        "ws_delete_confirmation_mismatch"
    assert os.path.isfile(os.path.join(root, "workspaces", slug, "app.db"))
    assert not os.path.exists(os.path.join(root, "workspaces", "_trash"))
    assert [f for f in os.listdir(os.path.join(root, "workspaces", slug))
            if f.startswith("app.db.bak-")] == []  # kiểm trước, sao lưu sau


def test_xoa_mac_dinh_la_chua_xac_nhan(api_ws):
    slug = _tao(api_ws, "A")
    assert ma_loi(api_ws.delete_workspace(slug)) == "ws_delete_confirmation_mismatch"


def test_xoa_dom_vao_thung_rac_kem_ban_sao_luu(api_ws, root):
    slug = _tao(api_ws, "A")
    res = api_ws.delete_workspace(slug, "XOA")
    assert res["ok"] and res["data"]["was_open"] is False
    rac = res["data"]["trash"]
    assert os.path.dirname(rac) == os.path.join(root, "workspaces", "_trash")
    assert any(f.startswith("app.db.bak-") for f in os.listdir(rac))
    assert api_ws.list_workspaces()["data"]["items"] == []


def test_xoa_workspace_dang_mo_thi_dong_no(api_ws):
    a, b = _tao(api_ws, "A"), _tao(api_ws, "B")
    api_ws.open_workspace(a)
    res = api_ws.delete_workspace(a, "XOA")
    assert res["ok"] and res["data"]["was_open"] is True
    assert api_ws.db_path is None
    d = api_ws.list_workspaces()["data"]
    assert d["current"] is None and [x["slug"] for x in d["items"]] == [b]


def test_xoa_workspace_khac_khong_dong_cai_dang_mo(api_ws):
    a, b = _tao(api_ws, "A"), _tao(api_ws, "B")
    api_ws.open_workspace(a)
    assert api_ws.delete_workspace(b, "XOA")["data"]["was_open"] is False
    assert api_ws.list_workspaces()["data"]["current"] == a


def test_xoa_that_bai_thi_workspace_dang_mo_van_mo(api_ws, monkeypatch):
    a = _tao(api_ws, "A")
    api_ws.open_workspace(a)
    db = api_ws.db_path

    def hong(*args, **kw):
        raise OSError("tep dang bi khoa")

    monkeypatch.setattr(w, "xoa", hong)
    assert ma_loi(api_ws.delete_workspace(a, "XOA")) == "error_workspace"
    assert api_ws.db_path == db
    assert api_ws.list_workspaces()["data"]["current"] == a


def test_xoa_sai_ma(api_ws):
    assert ma_loi(api_ws.delete_workspace("khong-co", "XOA")) == "ws_not_found"


# ---------- mẫu ----------

def test_luu_mau_roi_liet_ke(api_ws):
    slug = _tao(api_ws, "Công ty", {
        "industry": "company",
        "labels": {"person": {"vi": "Nhân viên", "en": "Employee"}}})
    api_ws.open_workspace(slug)
    api_ws.create_or_update_club("clb_a", "CLB A", 3, 0, "")
    assert api_ws.save_as_template(slug, "Mẫu công ty")["data"] == {
        "slug": "mau-cong-ty"}
    mau = api_ws.list_templates()["data"]
    assert [m["slug"] for m in mau] == ["truong-hoc", "mau-cong-ty"]
    assert mau[0]["builtin"] is True and mau[1]["industry"] == "company"
    moi = _tao(api_ws, "Công ty khác", mau[1]["config"])
    api_ws.open_workspace(moi)
    assert api_ws.list_clubs_admin()["data"] == []        # mẫu không mang dữ liệu
    assert api_ws.get_workspace_config()["data"]["labels"]["person"]["en"] == "Employee"


def test_luu_mau_sai(api_ws):
    slug = _tao(api_ws, "A")
    assert ma_loi(api_ws.save_as_template(slug, " ")) == "ws_name_required"
    assert ma_loi(api_ws.save_as_template("khong-co", "M")) == "ws_not_found"


# ---------- zip ----------

def test_xuat_vao_thu_muc_xuat_khong_de_len_nhau(api_ws, xuat):
    slug = _tao(api_ws, "Xuất")
    r1 = api_ws.export_workspace(slug)
    r2 = api_ws.export_workspace(slug)
    assert r1["ok"] and r2["ok"]
    assert os.path.dirname(r1["data"]["path"]) == xuat
    assert r1["data"]["name"] == os.path.basename(r1["data"]["path"])
    assert r1["data"]["path"] != r2["data"]["path"]
    assert zipfile.ZipFile(r1["data"]["path"]).namelist() == ["app.db"]
    assert ma_loi(api_ws.export_workspace("khong-co")) == "ws_not_found"


def test_xuat_roi_nhap_khu_hoi(api_ws, root):
    slug = _tao(api_ws, "Khứ hồi", {"rules": {"max_choices": 6}})
    api_ws.open_workspace(slug)
    api_ws.create_or_update_club("clb_a", "CLB A", 3, 0, "")
    duong = api_ws.export_workspace(slug)["data"]["path"]
    res = api_ws.import_workspace(_b64(duong))
    assert res["ok"] and res["data"]["slug"] == "khu-hoi-2"   # trùng -> đổi slug
    assert api_ws.list_workspaces()["data"]["current"] == slug  # nhập không tự mở
    api_ws.open_workspace("khu-hoi-2")
    assert [c["club_id"] for c in api_ws.list_clubs_admin()["data"]] == ["clb_a"]
    assert api_ws.get_workspace_config()["data"]["rules"]["max_choices"] == 6


def test_nhap_zip_xau_bi_tu_choi(api_ws):
    nhi_phan = io.BytesIO()
    with zipfile.ZipFile(nhi_phan, "w") as z:
        z.writestr("../evil.db", b"x")
        z.writestr("app.db", b"x")
    for payload in (base64.b64encode(nhi_phan.getvalue()).decode(),
                    base64.b64encode(b"khong phai zip").decode(),
                    "", None):
        assert ma_loi(api_ws.import_workspace(payload)) == "ws_zip_invalid"
    assert api_ws.list_workspaces()["data"]["items"] == []


def test_nhap_khong_de_lai_tep_tam(api_ws, root):
    api_ws.import_workspace(base64.b64encode(b"khong phai zip").decode())
    ws = os.path.join(root, "workspaces")
    assert not os.path.isdir(ws) or os.listdir(ws) == []


# ---------- cấu hình ----------

def test_cau_hinh_cua_workspace_dang_mo(api_ws):
    slug = _tao(api_ws, "A")
    api_ws.open_workspace(slug)
    cfg = api_ws.get_workspace_config()["data"]
    cfg["rules"]["max_choices"] = 8
    cfg["labels"]["slot"] = {"vi": "Dự án", "en": ""}
    res = api_ws.update_workspace_config(cfg)
    assert res["ok"] and res["data"]["labels"]["slot"]["en"] == "Dự án"
    assert api_ws.get_workspace_config()["data"] == res["data"]
    assert cfgws.doc_cau_hinh(api_ws.db_path) == res["data"]


def test_cau_hinh_theo_slug_khong_can_mo(api_ws):
    slug = _tao(api_ws, "A", {"industry": "event"})
    assert api_ws.get_workspace_config(slug)["data"]["industry"] == "event"
    assert api_ws.update_workspace_config({"industry": "custom"}, slug)["ok"]
    assert api_ws.get_workspace_config(slug)["data"]["industry"] == "custom"
    assert api_ws.db_path is None


def test_cau_hinh_chua_mo_workspace(api_ws):
    assert ma_loi(api_ws.get_workspace_config()) == "ws_none_open"
    assert ma_loi(api_ws.update_workspace_config({})) == "ws_none_open"
    assert ma_loi(api_ws.get_workspace_config("khong-co")) == "ws_not_found"


def test_cap_nhat_cau_hinh_sai_khong_ghi(api_ws):
    slug = _tao(api_ws, "A", {"rules": {"max_choices": 4}})
    api_ws.open_workspace(slug)
    res = api_ws.update_workspace_config({"rules": {"max_choices": 0}})
    assert ma_loi(res) == "ws_invalid"
    assert api_ws.get_workspace_config()["data"]["rules"]["max_choices"] == 4


# ---------- chưa mở workspace thì lỗi không làm sập ----------

def test_loi_chua_mo_workspace_van_ghi_vet_duoc(api_ws, root, monkeypatch):
    """`_loi_co_ghi_vet` không được nổ khi db_path là None."""
    monkeypatch.setattr(w, "danh_sach", lambda r: (_ for _ in ()).throw(OSError("x")))
    res = api_ws.list_workspaces()
    assert res["ok"] is False and res["errors"][0]["code"] == "error_workspace"
    assert os.path.exists(os.path.join(root, "loi_ung_dung.txt"))
