"""Đổi workspace trên GIAO DIỆN THẬT (Chromium): sau khi đổi, không thẻ nào còn dữ liệu, nhãn hay
luật của workspace trước; bảng chọn cứu được một workspace hỏng giữa các workspace lành.

Dùng ba workspace của tests/test_ws_e2e.py. Máy không có playwright/Chromium thì bỏ qua cả tệp.
"""

import os

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")
from playwright.sync_api import sync_playwright  # noqa: E402

import browser_host  # noqa: E402
import workspace as ws  # noqa: E402
from _trinh_duyet import CHROMIUM  # noqa: E402
from test_ws_e2e import _dung_ba_workspace  # noqa: E402

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAC_THE = ("pipeline", "results", "fallback", "admin", "scoring")


@pytest.fixture
def mo(tmp_path):
    """mo() -> (page, api, goc, slugs, loi). Ba workspace đã chạy xong, đang mở "Trường học"."""
    if CHROMIUM is None:
        pytest.skip("khong tim thay Chromium")
    goc, api, truong, cty, sk = _dung_ba_workspace(tmp_path)
    assert api.open_workspace(truong)["ok"]
    url = browser_host.serve(api, GOC, "index.html", open_browser=False)
    pw = sync_playwright().start()
    br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
    page = br.new_page(bypass_csp=True)
    loi = []
    page.on("pageerror", lambda e: loi.append(str(e)))
    page.goto(url)
    page.wait_for_selector("#dropZone")
    yield page, api, goc, (truong, cty, sk), loi
    br.close()
    pw.stop()


def _doc_cac_the(page):
    """Chữ nhìn thấy của từng thẻ, sau khi bấm sang thẻ đó và chờ nạp xong."""
    ra = {}
    for the in CAC_THE:
        nut = page.locator('button[data-tab="%s"]' % the)
        if not nut.is_visible():
            ra[the] = None          # luật của workspace ẩn thẻ này (chỉ-theo-nhóm không chấm điểm)
            continue
        nut.click()
        page.wait_for_timeout(700)
        ra[the] = page.locator("#view-%s" % the).inner_text()
    page.click('button[data-tab="pipeline"]')
    return ra


def _sang(page, slug, ten):
    page.locator("#btnWorkspace").click()
    page.locator('button[data-slug="%s"][data-hanh-dong="mo"]' % slug).click()
    page.wait_for_function(
        "n => document.querySelector('#wsTenHienTai').textContent === n", arg=ten, timeout=10000)
    page.wait_for_selector("#dropZone")
    page.wait_for_timeout(500)


# mã chỉ có ở MỘT workspace (xem tests/test_ws_e2e.py): mã học sinh/nhân viên/khách và mã CLB
DAU = {"truong": ("HS0", "clb_"), "cty": ("NV0", "da1"), "sk": ("K0", "w1_1")}


def _chi_co(the, cua, tat_ca=DAU):
    """Chữ của thẻ có dấu hiệu của `cua` và KHÔNG có dấu hiệu của hai workspace kia."""
    dung = [d for d in tat_ca[cua] if d in the]
    sai = [d for khac, ds in tat_ca.items() if khac != cua for d in ds if d in the]
    return dung, sai


def test_doi_workspace_khong_the_nao_con_du_lieu_cua_cai_truoc(mo):
    page, api, goc, (truong, cty, sk), loi = mo
    tat_ca = {}
    tat_ca["truong"] = _doc_cac_the(page)
    _sang(page, cty, "Công ty ABC")
    tat_ca["cty"] = _doc_cac_the(page)
    _sang(page, sk, "Hội nghị XYZ")
    tat_ca["sk"] = _doc_cac_the(page)
    _sang(page, truong, "Trường học")
    quay_ve = _doc_cac_the(page)

    for cua, cac_the in tat_ca.items():
        # thẻ nào nạp danh sách thì phải có dữ liệu của workspace đó (và chỉ của nó)
        # (thẻ Kết quả gấp sẵn các bảng nên mã không hiện; ở đó chỉ kiểm không có mã của cái khác)
        for the in ("fallback", "admin"):
            dung, sai = _chi_co(cac_the[the], cua)
            assert dung, (cua, the)
            assert sai == [], (cua, the, sai)
        for the in CAC_THE:
            if cac_the[the] is not None:
                assert _chi_co(cac_the[the], cua)[1] == [], (cua, the)

    # luật chỉ-theo-nhóm của sự kiện ẩn thẻ Chấm điểm; luật ấy không được dính sang hai cái kia,
    # kể cả khi quay lại (thẻ hiện lại đúng theo luật của trường học)
    assert tat_ca["sk"]["scoring"] is None
    assert tat_ca["truong"]["scoring"] and tat_ca["cty"]["scoring"] and quay_ve["scoring"]

    # nhãn của từng workspace nằm trong CHỮ trên thẻ — và không rò sang nhau
    assert "nhân viên" in tat_ca["cty"]["pipeline"] and "học sinh" not in tat_ca["cty"]["pipeline"].lower()
    assert "dự án" in tat_ca["cty"]["pipeline"]
    assert "KPI" in tat_ca["cty"]["scoring"] and "KPI" not in tat_ca["truong"]["scoring"]
    assert "khách" in tat_ca["sk"]["pipeline"] and "workshop" in tat_ca["sk"]["pipeline"].lower()
    assert "học sinh" in tat_ca["truong"]["pipeline"] and "nhân viên" not in tat_ca["truong"]["pipeline"]
    # về lại trường học: chữ y như lần đầu (không dính nhãn công ty/sự kiện)
    for the in CAC_THE:
        assert quay_ve[the] == tat_ca["truong"][the], the
    assert not loi, loi


def test_the_van_hanh_cua_su_kien_khong_con_chu_cua_truong_hoc(mo):
    """Cảnh báo dữ liệu (thẻ Vận hành) tính theo LUẬT của workspace đang mở."""
    page, api, goc, (truong, cty, sk), loi = mo
    _sang(page, sk, "Hội nghị XYZ")
    # sự kiện có 3 phiên: bảng "Lịch sử sắp xếp" ghi 3 phiên và luật chỉ-theo-nhóm
    page.click('button[data-tab="pipeline"]')
    chu = page.locator("#view-pipeline").inner_text()
    assert "học sinh" not in chu.lower() and "câu lạc bộ" not in chu.lower().replace("sổ nhập clb", "")
    _sang(page, truong, "Trường học")
    assert api.db_path == ws.duong_dan_db(goc, truong)
    assert not loi, loi


def test_workspace_hong_giua_cac_workspace_lanh_khoi_phuc_duoc_tu_bang_chon(mo):
    page, api, goc, (truong, cty, sk), loi = mo
    db = ws.duong_dan_db(goc, sk)
    ws._chep_db(db, db + ".bak-20260101_000000_000000")          # một bản sao lưu lành
    with open(db, "wb") as f:
        f.write(b"khong phai sqlite " * 300)

    page.locator("#btnWorkspace").click()
    page.wait_for_selector('tr[data-slug="%s"]' % sk)
    dong = page.locator('tr[data-slug="%s"]' % sk)
    assert dong.locator(".ws-badge-hong").count() == 1
    # các workspace khác vẫn liệt kê bình thường và không gắn nhãn hỏng
    assert page.locator('tr[data-slug="%s"] .ws-badge-hong' % cty).count() == 0
    assert page.locator('tr[data-slug="%s"] button[data-hanh-dong="mo"]' % cty).is_enabled()
    # dòng hỏng chỉ có Khôi phục và Xoá — không có nút nào đòi đọc app.db
    assert dong.locator('button[data-hanh-dong="khoi_phuc"]').count() == 1
    assert dong.locator('button[data-hanh-dong="mo"]').count() == 0

    dong.locator('button[data-hanh-dong="khoi_phuc"]').click()
    page.wait_for_function(
        "s => !document.querySelector('tr[data-slug=\"' + s + '\"] .ws-badge-hong')", arg=sk, timeout=10000)
    assert dong.locator('button[data-hanh-dong="mo"]').count() == 1
    assert api.db_path == ws.duong_dan_db(goc, truong)           # vẫn ở workspace đang mở
    page.locator("#wsBtnDong").click()
    _sang(page, sk, "Hội nghị XYZ")                              # và mở được cái vừa cứu
    assert "K0" in _doc_cac_the(page)["admin"]
    assert not loi, loi
