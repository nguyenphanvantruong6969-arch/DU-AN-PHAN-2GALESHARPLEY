"""Màn chọn workspace, nút đổi ở thanh bên và trình hướng dẫn — bằng TRÌNH DUYỆT THẬT.

Cùng khuôn với các test_giao_dien_*.py: Playwright + Chromium, cầu nối
browser_host. Máy nào không có playwright/Chromium thì bỏ qua cả tệp.
"""

import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
import workspace as ws  # noqa: E402
from api import PipelineAPI  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from _trinh_duyet import CHROMIUM  # noqa: E402


def _dung(tmp_path, ten_ws=("Trường học",), da_chon=True, che_do_ws=True):
    goc = tmp_path / "goc"
    goc.mkdir(exist_ok=True)
    xuat = tmp_path / "xuat"
    xuat.mkdir(exist_ok=True)
    slugs = [ws.tao(str(goc), ten, None) for ten in ten_ws]
    if che_do_ws:
        api = PipelineAPI(ws.duong_dan_db(str(goc), slugs[0]), thu_muc_xuat=str(xuat),
                          thu_muc_goc_ws=str(goc), ws_da_chon=da_chon)
    else:
        api = PipelineAPI(ws.duong_dan_db(str(goc), slugs[0]), thu_muc_xuat=str(xuat))
    return api, str(goc)


@pytest.fixture
def mo_trang(tmp_path):
    """Gọi mo_trang(...) -> (page, api, goc, loi). Đóng trình duyệt khi test xong."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    dong = []

    def mo(**kw):
        api, goc = _dung(tmp_path, **kw)
        url = browser_host.serve(api, GOC, "index.html", open_browser=False)
        pw = sync_playwright().start()
        br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
        dong.append((br, pw))
        page = br.new_page(bypass_csp=True)
        loi = []
        page.on("pageerror", lambda e: loi.append(str(e)))
        page.goto(url)
        page.wait_for_selector("#dropZone")
        return page, api, goc, loi

    yield mo
    for br, pw in dong:
        br.close()
        pw.stop()


def _ten_o_dau(page):
    return page.locator("#wsTenHienTai").inner_text()


def _cho_ten(page, ten):
    page.wait_for_function(
        "n => document.querySelector('#wsTenHienTai').textContent === n", arg=ten, timeout=10000)


def _tao_qua_wizard(page, ten, nganh="company", vi_nguoi=None, en_nguoi=None):
    page.locator("#wsBtnMoi").click()
    page.fill("#wzTen", ten)
    page.select_option("#wzNganh", nganh)
    page.locator("#wzTiep").click()
    if vi_nguoi:
        page.fill("#wzNhan_person_vi", vi_nguoi)
        page.fill("#wzNhan_person_en", en_nguoi or "")
    page.locator("#wzTiep").click()
    page.locator("#wzTiep").click()
    page.locator("#wzTao").click()


# ------------------------------------------------------------------ chuyển qua lại

def test_tao_chuyen_sang_roi_chuyen_ve_thi_ten_o_dau_doi(mo_trang):
    page, api, goc, loi = mo_trang()
    assert page.locator("#btnWorkspace").is_visible()
    assert _ten_o_dau(page) == "Trường học"

    page.locator("#btnWorkspace").click()
    assert page.locator("#wsOverlay").is_visible()
    dang_mo = page.locator('tr[data-slug="truong-hoc"] .ws-badge')
    assert dang_mo.count() == 1

    _tao_qua_wizard(page, "Công ty ABC", vi_nguoi="Nhân viên", en_nguoi="Employee")
    _cho_ten(page, "Công ty ABC")                       # đã tải lại, đang ở workspace mới
    assert page.locator("#wsOverlay").is_hidden()
    assert api.db_path == ws.duong_dan_db(goc, "cong-ty-abc")
    cfg = api.get_workspace_config()["data"]["config"]
    assert cfg["industry"] == "company"
    assert cfg["labels"]["person"] == {"vi": "Nhân viên", "en": "Employee"}

    page.locator("#btnWorkspace").click()
    page.locator('button[data-slug="truong-hoc"][data-hanh-dong="mo"]').click()
    _cho_ten(page, "Trường học")                        # và quay về
    assert api.db_path == ws.duong_dan_db(goc, "truong-hoc")
    assert not loi, loi


def test_ten_o_dau_doi_theo_ten_sau_khi_doi_ten(mo_trang):
    page, api, goc, loi = mo_trang()
    page.locator("#btnWorkspace").click()
    page.locator('button[data-slug="truong-hoc"][data-hanh-dong="doi_ten"]').click()
    page.fill(".ws-sua-ten", "Năm học 2026")
    page.locator("#wsBtnLuuSua").click()
    _cho_ten(page, "Năm học 2026")
    assert os.path.isdir(os.path.join(goc, "workspaces", "truong-hoc"))
    assert not loi, loi


# ------------------------------------------------------------------ màn chọn lúc khởi động

def test_nhieu_workspace_luc_khoi_dong_thi_phai_chon(mo_trang):
    page, api, goc, loi = mo_trang(ten_ws=("Alpha", "Beta"), da_chon=False)
    page.wait_for_selector("#wsOverlay:not([hidden])")
    assert page.locator("#wsBtnDong").count() == 0        # chưa chọn thì không đóng được
    page.keyboard.press("Escape")
    assert page.locator("#wsOverlay").is_visible()
    assert page.locator(".ws-badge").count() == 0         # chưa cái nào "đang mở"

    page.locator('button[data-slug="beta"][data-hanh-dong="mo"]').click()
    _cho_ten(page, "Beta")
    assert page.locator("#wsOverlay").is_hidden()
    assert api.db_path == ws.duong_dan_db(goc, "beta")
    assert not loi, loi


def test_mot_workspace_thi_khong_hien_man_chon_luc_khoi_dong(mo_trang):
    page, _, _, loi = mo_trang()
    assert page.locator("#wsOverlay").is_hidden()
    page.locator("#btnWorkspace").click()
    page.wait_for_selector("#wsBtnDong")                  # mở tay thì đóng được
    page.keyboard.press("Escape")
    assert page.locator("#wsOverlay").is_hidden()
    assert not loi, loi


def test_chay_voi_duong_dan_csdl_rieng_thi_khong_co_gi_cua_workspace(mo_trang):
    page, _, _, loi = mo_trang(che_do_ws=False)
    assert page.locator("#btnWorkspace").is_hidden()
    assert page.locator("#wsOverlay").is_hidden()
    assert not loi, loi


# ------------------------------------------------------------------ trình hướng dẫn

def test_wizard_bat_loi_o_buoc_1_va_chi_di_tiep_khi_hop_le(mo_trang):
    page, _, _, loi = mo_trang()
    page.locator("#btnWorkspace").click()
    page.locator("#wsBtnMoi").click()
    page.locator("#wzTiep").click()                       # chưa gõ tên
    assert page.locator("#wzLoi").is_visible()
    assert page.locator("#wzTen").is_visible()            # vẫn ở bước 1

    page.fill("#wzTen", "A")
    page.locator("#wzTiep").click()
    assert page.locator("#wzNhan_person_vi").is_visible()  # sang bước 2
    page.fill("#wzNhan_slot_vi", "")
    page.locator("#wzTiep").click()
    assert page.locator("#wzLoi").is_visible()            # ô tiếng Việt trống

    page.fill("#wzNhan_slot_vi", "Dự án")
    page.fill("#wzNhan_slot_en", "")                      # en trống = dùng tiếng Việt
    page.locator("#wzTiep").click()
    page.fill("#wzMaxChoices", "99")
    page.locator("#wzTiep").click()
    assert page.locator("#wzLoi").is_visible()            # 99 > 20
    page.fill("#wzMaxChoices", "3")
    page.locator("#wzKhongGioiHan").check()
    assert page.locator("#wzMaxTests").is_disabled()
    page.locator("#wzTiep").click()

    assert page.locator("#rvMaxChoices").inner_text() == "3"
    assert page.locator("#rvMaxTests").inner_text() == "Không giới hạn"
    assert page.locator("#rvNhan_slot").inner_text() == "Dự án / Dự án"   # en trống = dùng vi
    assert not loi, loi


def test_wizard_chon_mau_dien_san_ca_bon_buoc(mo_trang):
    page, api, goc, loi = mo_trang()
    cfg = {"industry": "company",
           "labels": {"person": {"vi": "Nhân viên", "en": "Employee"}},
           "rules": {"max_choices": 3, "max_tests": None, "priority": "tier",
                     "tier_mode": "strict", "score_scope": "per_person",
                     "tiers": ["Quản lý", "Nhân viên"]}}
    slug = api.create_workspace("Công ty gốc", cfg)["data"]["slug"]
    api.save_as_template(slug, "Mẫu công ty")

    page.locator("#btnWorkspace").click()
    page.locator("#wsBtnMoi").click()
    page.fill("#wzTen", "Chi nhánh")
    page.select_option("#wzMau", label="Mẫu công ty")
    assert page.input_value("#wzTen") == "Chi nhánh"      # tên đã gõ được giữ
    assert page.input_value("#wzNganh") == "company"
    page.locator("#wzTiep").click()
    assert page.input_value("#wzNhan_person_vi") == "Nhân viên"
    assert page.input_value("#wzNhan_person_en") == "Employee"
    page.locator("#wzTiep").click()
    assert page.input_value("#wzMaxChoices") == "3"
    assert page.locator("#wzKhongGioiHan").is_checked()
    assert page.input_value("#wzPriority") == "tier"
    assert page.input_value("#wzTierMode") == "strict"
    assert page.input_value("#wzScoreScope") == "per_person"
    assert page.input_value("#wzTiers") == "Quản lý\nNhân viên"
    assert page.locator("#wzTiers").is_enabled()

    page.select_option("#wzTierMode", "reserve")           # chỉ sửa được danh sách khi strict
    assert page.locator("#wzTiers").is_disabled()
    page.select_option("#wzTierMode", "strict")
    page.locator("#wzTiep").click()
    page.locator("#wzTao").click()
    _cho_ten(page, "Chi nhánh")
    moi = api.get_workspace_config()["data"]["config"]
    assert moi["rules"]["tiers"] == ["Quản lý", "Nhân viên"] and moi["rules"]["max_tests"] is None
    assert not loi, loi


def test_wizard_quay_lai_giu_nguyen_chu_da_go(mo_trang):
    page, _, _, loi = mo_trang()
    page.locator("#btnWorkspace").click()
    page.locator("#wsBtnMoi").click()
    page.fill("#wzTen", "Giữ tên")
    page.locator("#wzTiep").click()
    page.fill("#wzNhan_group_vi", "Cấp bậc")
    page.locator("#wzLui").click()
    assert page.input_value("#wzTen") == "Giữ tên"
    page.locator("#wzTiep").click()
    assert page.input_value("#wzNhan_group_vi") == "Cấp bậc"
    page.locator("#wzHuy").click()
    assert page.locator("#wsBtnMoi").is_visible()
    assert not loi, loi


# ------------------------------------------------------------------ hành động trên danh sách

def test_xoa_hai_buoc_dua_vao_thung_rac(mo_trang):
    page, api, goc, loi = mo_trang(ten_ws=("Giữ", "Bỏ"))
    page.locator("#btnWorkspace").click()
    assert page.locator('button.ws-xoa[data-slug="giu"]').is_disabled()   # đang mở: không xoá
    nut = page.locator('button.ws-xoa[data-slug="bo"]')
    nhan = nut.inner_text()
    nut.click()
    assert nut.inner_text() != nhan                        # lần 1 chỉ đổi nhãn
    assert os.path.isdir(os.path.join(goc, "workspaces", "bo"))
    nut.click()
    page.wait_for_selector('tr[data-slug="bo"]', state="detached")
    assert not os.path.exists(os.path.join(goc, "workspaces", "bo"))
    assert len(os.listdir(os.path.join(goc, "workspaces", "_trash"))) == 1
    assert not loi, loi


def test_nhan_ban_va_xuat_nhap_zip(mo_trang):
    page, api, goc, loi = mo_trang()
    api.create_or_update_club("A", "CLB A", 3, 0, None)
    page.locator("#btnWorkspace").click()
    page.locator('button[data-slug="truong-hoc"][data-hanh-dong="nhan_ban"]').click()
    page.fill(".ws-sua-ten", "Bản nhân")
    page.locator("#wsBtnLuuSua").click()
    page.wait_for_selector('tr[data-slug="ban-nhan"]')

    page.locator('button[data-slug="ban-nhan"][data-hanh-dong="xuat"]').click()
    page.wait_for_function(
        "document.querySelector('#toastStack').innerText.indexOf('.zip') !== -1", timeout=8000)
    duong = [f for f in os.listdir(api.thu_muc_xuat) if f.endswith(".zip")]
    assert duong, "chua thay tep zip trong thu muc xuat"

    page.set_input_files("#wsFileZip", os.path.join(api.thu_muc_xuat, duong[0]))
    page.wait_for_selector('tr[data-slug="ban-nhan-2"]', timeout=8000)
    assert not loi, loi


def test_doi_ngon_ngu_khi_man_chon_dang_mo(mo_trang):
    page, _, _, loi = mo_trang()
    page.locator("#btnWorkspace").click()
    assert "Chọn workspace" in page.locator("#wsHop").inner_text()
    page.evaluate("window.I18N.setLang('en')")   # nút EN nằm sau màn chọn nên không bấm được
    page.wait_for_function("document.documentElement.lang === 'en'")
    chu = page.locator("#wsHop").inner_text()
    assert "Choose a workspace" in chu and "Chọn workspace" not in chu
    assert not loi, loi


def test_cau_noi_trinh_duyet_khong_bao_dong_cua_so_khi_tai_lai_de_doi_workspace(tmp_path):
    """Đổi workspace = tải lại trang. `pagehide` của cầu nối báo "đã đóng" và tắt máy
    chủ, nên nó phải bỏ qua khi cờ __DANG_TAI_LAI bật (trang vừa tải lại sẽ không còn
    gì để kết nối). Test trình duyệt ở trên chứng minh bằng hành vi; đây là lưới chặn
    cho máy không có Chromium."""
    import urllib.request

    api, _ = _dung(tmp_path)
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    with urllib.request.urlopen(url) as r:
        html = r.read().decode("utf-8")
    assert html.index("if (window.__DANG_TAI_LAI) return;") < html.index("navigator.sendBeacon")
    assert "__DANG_TAI_LAI" in open(os.path.join(GOC, "js", "075_workspace.js"),
                                    encoding="utf-8").read()
