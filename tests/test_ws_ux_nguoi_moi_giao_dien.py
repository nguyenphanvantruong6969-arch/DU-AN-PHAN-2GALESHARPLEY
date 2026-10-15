"""Vòng thử "người dùng MỚI" — phần GIAO DIỆN THẬT (Chromium). Xem UX_PILOT_NOTES.md.

Dùng ba workspace của tests/test_ws_e2e.py (trường học, công ty KPI theo người nhóm cứng, sự kiện
chỉ-theo-hạng-vé 3 phiên). Mỗi test ứng với một mục "Đã sửa" trong ghi chú. Máy không có
playwright/Chromium thì bỏ qua cả tệp.
"""

# ruff: noqa: F811  (fixture `mo` nhập từ tệp khác rồi dùng làm tham số: cách pytest nạp fixture dùng chung)
import re

import pytest

pytest.importorskip("playwright", reason="chưa cài playwright")

from test_ws_e2e_giao_dien import _doc_cac_the, _sang, mo  # noqa: E402,F401

TU_TRUONG = re.compile(r"học sinh|câu lạc bộ|\bCLB\b|giáo viên|thời khoá|\bem\b", re.IGNORECASE)


def _chu(page, vung):
    """Chữ NHÌN THẤY của một vùng (display:none không tính)."""
    return page.locator(vung).inner_text()


def _vao(page, the):
    page.click('button[data-tab="%s"]' % the)
    page.wait_for_timeout(700)


def _mo_rong_ket_qua(page):
    """Thẻ Kết quả gấp sẵn các bảng: mở hết ra để đọc chữ trong đó."""
    _vao(page, "results")
    if "Mở rộng" in page.locator("#btnThuGonTatCa").inner_text():
        page.locator("#btnThuGonTatCa").click()
        page.wait_for_timeout(500)


def _chon_nguoi_dau(page):
    """Mở vùng làm việc của thẻ Nhập tại chỗ (các bước chỉ hiện sau khi chọn một người)."""
    page.wait_for_selector("#studentSearchResults .hs-card")
    page.locator("#studentSearchResults .hs-card").first.click()
    page.wait_for_selector("#fallbackWorkArea", state="visible")


# ------------------------------------------------------------------ sự kiện: chỉ theo hạng vé

def test_su_kien_the_nhap_tai_cho_khong_con_buoc_chon_cho_du_thi(mo):
    page, api, goc, (truong, cty, sk), loi = mo
    _sang(page, sk, "Hội nghị XYZ")
    _vao(page, "fallback")
    _chon_nguoi_dau(page)
    assert page.locator("#fallbackBuocThi").is_hidden()
    assert page.locator("#btnSubmitPreferences").is_visible()      # còn bước xếp nguyện vọng
    mo_ta = _chu(page, "#view-fallback .view-desc")
    assert "dự thi" not in mo_ta and "hai bước" not in mo_ta
    assert mo_ta.endswith("xếp hạng nguyện vọng.")
    chu = _chu(page, "#view-fallback")
    assert "dự thi" not in chu.lower() and "thiếu workshop" not in chu.lower()
    assert "Bước 2" not in chu                                     # chỉ còn một bước, khỏi đánh số
    assert not loi, loi


def test_su_kien_the_hoc_vien_khong_bao_thieu_du_thi(mo):
    """Thẻ từng khách trong danh sách không báo "Thiếu workshop dự thi" khi không có bước ấy."""
    page, api, goc, (truong, cty, sk), loi = mo
    _sang(page, sk, "Hội nghị XYZ")
    _vao(page, "fallback")
    page.wait_for_selector("#studentSearchResults .hs-card")
    the = _chu(page, "#studentSearchResults")
    assert "dự thi" not in the.lower() and "DỰ THI" not in the
    assert "Đã nhập đủ" in the or "Chưa nhập gì" in the
    # và có thẻ nào cũng không có hàng "chọn dự thi"
    assert page.locator("#studentSearchResults .hs-card-dong.chi-thi:visible").count() == 0


def test_su_kien_the_quan_ly_khong_con_du_tru_va_goi_dung_hang_ve(mo):
    page, api, goc, (truong, cty, sk), loi = mo
    _sang(page, sk, "Hội nghị XYZ")
    _vao(page, "admin")
    assert page.locator("#clubFormReserveCapacity").is_hidden()
    assert page.locator("#clubFormReserveGroup").is_hidden()
    chu = _chu(page, "#view-admin")
    assert "dự trữ" not in chu.lower()
    assert "hạng vé" in chu.lower() and "hạng vé" in _chu(page, "#view-admin h1").lower()
    assert page.locator("#bulkReserveGroupInput").get_attribute("placeholder") == "Hạng vé cần gán"
    assert "hạng vé hiện tại" in chu.lower()           # tiêu đề cột viết hoa bằng CSS
    nav = page.locator('button[data-tab="admin"]').inner_text().lower()
    assert "dự trữ" not in nav and "hạng vé" in nav
    assert not loi, loi


def test_su_kien_the_ket_qua_khong_con_chu_du_tru(mo):
    page, api, goc, (truong, cty, sk), loi = mo
    _sang(page, sk, "Hội nghị XYZ")
    _mo_rong_ket_qua(page)
    chu = _chu(page, "#view-results")
    assert "dự trữ" not in chu.lower(), re.findall(r".{0,30}dự trữ.{0,30}", chu, re.I | re.S)
    assert page.locator("#duTruPanel").is_hidden()
    assert page.locator(".fill-legend .is-reserve").is_hidden()
    assert "Đã xếp" in _chu(page, ".fill-legend")
    assert not loi, loi


def test_su_kien_thanh_ben_khong_co_the_cham_diem_va_lich_khong_noi_tuan(mo):
    page, api, goc, (truong, cty, sk), loi = mo
    _sang(page, sk, "Hội nghị XYZ")
    assert page.locator('button[data-tab="scoring"]').is_hidden()
    _vao(page, "pipeline")
    # Chọn phiên để chạy lại một phần: câu nhắc không nói "trong tuần" (từ của trường học)
    chu = _chu(page, "#view-pipeline")
    assert "trong tuần" not in chu
    assert not loi, loi


def test_su_kien_ten_phien_doc_duoc_khong_phai_ma_noi_bo(mo):
    """Ô chọn phiên để chạy, chip phiên và các bảng nói "Phiên 2", không nói `phien_2`."""
    page, api, goc, (truong, cty, sk), loi = mo
    _sang(page, sk, "Hội nghị XYZ")
    _vao(page, "pipeline")
    chip = page.locator("#chonBuoiChip .buoi-chip")
    assert chip.count() == 3
    assert [chip.nth(i).inner_text() for i in range(3)] == ["Phiên 1", "Phiên 2", "Phiên 3"]
    tu = page.locator("#chonBuoiTu option")
    assert [tu.nth(i).inner_text() for i in range(3)] == ["Phiên 1", "Phiên 2", "Phiên 3"]
    assert [tu.nth(i).get_attribute("value") for i in range(3)] == ["phien_1", "phien_2", "phien_3"]  # giá trị gửi đi không đổi
    assert "phien_" not in _chu(page, "#view-pipeline")
    _mo_rong_ket_qua(page)
    chu = _chu(page, "#view-results")
    assert "phien_" not in chu
    assert "Phiên 2" in chu
    _vao(page, "admin")
    assert "phien_" not in _chu(page, "#view-admin")
    assert not loi, loi


# ------------------------------------------------------------------ công ty: KPI theo người

def test_cong_ty_thay_the_nhap_kpi_nhung_khong_con_buoc_du_thi_va_du_tru(mo):
    page, api, goc, (truong, cty, sk), loi = mo
    _sang(page, cty, "Công ty ABC")
    assert page.locator('button[data-tab="scoring"]').is_visible()
    _vao(page, "scoring")
    assert "KPI" in _chu(page, "#view-scoring")
    _vao(page, "fallback")
    _chon_nguoi_dau(page)
    assert page.locator("#fallbackBuocThi").is_hidden()
    assert "dự thi" not in _chu(page, "#view-fallback").lower()
    _vao(page, "admin")
    assert page.locator("#clubFormReserveCapacity").is_hidden()
    assert "dự trữ" not in _chu(page, "#view-admin").lower()
    assert "cấp bậc" in _chu(page, "#view-admin h1").lower()
    # lời cảnh báo khi xuất vẫn nói tới KPI (có điểm), không nhắc "giáo viên"
    canh_bao = _chu(page, "#view-admin .xuat-canh-bao")
    assert "KPI" in canh_bao and "giáo viên" not in canh_bao
    assert not loi, loi


def test_su_kien_canh_bao_xuat_khong_noi_toi_diem(mo):
    page, api, goc, (truong, cty, sk), loi = mo
    _sang(page, sk, "Hội nghị XYZ")
    _vao(page, "admin")
    canh_bao = _chu(page, "#view-admin .xuat-canh-bao")
    assert "điểm" not in canh_bao.lower() and "bốc thăm" in canh_bao
    assert not loi, loi


# ------------------------------------------------------------------ trường học: không đổi, và đổi lại được

def test_truong_hoc_van_day_du_va_doi_qua_lai_khong_dinh_luat(mo):
    page, api, goc, (truong, cty, sk), loi = mo
    truoc = _doc_cac_the(page)
    _vao(page, "fallback")
    _chon_nguoi_dau(page)
    assert page.locator("#fallbackBuocThi").is_visible()
    assert "Bước 2. Xếp hạng nguyện vọng" in _chu(page, "#view-fallback")
    _vao(page, "admin")
    assert page.locator("#clubFormReserveCapacity").is_visible()
    assert "dự trữ" in _chu(page, "#view-admin h1")

    for slug, ten in ((sk, "Hội nghị XYZ"), (cty, "Công ty ABC"), (sk, "Hội nghị XYZ")):
        _sang(page, slug, ten)
        _vao(page, "admin")
        assert page.locator("#clubFormReserveCapacity").is_hidden(), ten
    _sang(page, truong, "Trường học")
    _vao(page, "admin")
    assert page.locator("#clubFormReserveCapacity").is_visible()
    assert "dự trữ" in _chu(page, "#view-admin h1")
    _vao(page, "fallback")
    _chon_nguoi_dau(page)
    assert page.locator("#fallbackBuocThi").is_visible()
    sau = _doc_cac_the(page)
    for the in truoc:
        if the != "fallback":                              # thẻ này vừa chọn một người nên khác
            assert sau[the] == truoc[the], the             # còn lại: chữ y như lần đầu
    assert not loi, loi


@pytest.mark.parametrize("nguoi", ["cty", "sk"])
def test_khong_the_nao_cua_cong_ty_hay_su_kien_con_tu_cua_truong_hoc(mo, nguoi):
    page, api, goc, (truong, cty, sk), loi = mo
    slug, ten = (cty, "Công ty ABC") if nguoi == "cty" else (sk, "Hội nghị XYZ")
    _sang(page, slug, ten)
    _mo_rong_ket_qua(page)                                   # đọc cả các bảng gấp sẵn
    cac_the = _doc_cac_the(page)
    for the, chu in cac_the.items():
        if chu is None:
            continue
        thua = TU_TRUONG.findall(chu)
        assert thua == [], (nguoi, the, thua)
    assert not loi, loi


# ------------------------------------------------------------------ thẻ Nhập điểm: bố cục và thanh tiến độ

def _khung(page, vung):
    return page.evaluate("v => { const b = document.querySelector(v).getBoundingClientRect();"
                         " return [Math.round(b.left), Math.round(b.width)]; }", vung)


def test_the_nhap_diem_cung_cot_voi_cac_the_khac_khong_bi_co_hep_giua_trang(mo):
    """Thẻ ít nội dung (Nhập điểm) từng co còn ~620px và lệch giữa trang vì .main là phần tử lưới
    margin:auto; mọi thẻ phải chiếm cùng một khung nội dung."""
    page, api, goc, (truong, cty, sk), loi = mo
    _vao(page, "pipeline")
    khung_chuan = _khung(page, "#view-pipeline")
    _vao(page, "scoring")
    assert _khung(page, "#view-scoring") == khung_chuan
    assert _khung(page, "#view-scoring .panel") == khung_chuan           # bảng tiến độ rộng bằng cột
    for the in ("results", "fallback", "admin"):
        _vao(page, the)
        assert _khung(page, "#view-%s" % the) == khung_chuan, the
    _sang(page, cty, "Công ty ABC")                                         # bảng KPI theo người cũng vậy
    _vao(page, "scoring")
    assert _khung(page, "#view-scoring #scoringPersonArea") == khung_chuan
    assert not loi, loi


def test_thanh_tien_do_cham_diem_to_dung_ti_le(mo):
    """Thanh "Đã chấm" là <span> nên width/height từng không có tác dụng: thanh luôn rỗng."""
    page, api, goc, (truong, cty, sk), loi = mo
    _vao(page, "scoring")
    ds = [d for d in api.get_scoring_overview()["data"] if d["n_applicants"] > 0]
    assert ds
    thanh = page.locator("#scoringOverviewBody .scoring-progress-bar")
    assert thanh.count() == len(ds)
    for i, d in enumerate(ds):
        rong_thanh = thanh.nth(i).evaluate("e => e.getBoundingClientRect().width")
        phan = thanh.nth(i).locator(".scoring-progress-fill").evaluate(
            "e => { const b = e.getBoundingClientRect(); return [b.width, b.height]; }")
        assert phan[1] > 0, d                                              # có chiều cao
        mong = rong_thanh * round(100 * d["n_scored"] / d["n_applicants"]) / 100
        assert abs(phan[0] - mong) < 1, (d, phan, mong)
    assert not loi, loi


# ------------------------------------------------------------------ người dùng mới tìm nút workspace

def test_nut_workspace_o_thanh_ben_noi_ro_bam_vao_de_doi_hoac_tao(mo):
    """Người mới thấy "Workspace: Trường học" tưởng là nhãn; nút phải nói bấm vào làm được gì."""
    page, api, goc, (truong, cty, sk), loi = mo
    chu = page.locator("#btnWorkspace").inner_text()
    assert "bấm để đổi/tạo" in chu
    page.locator("#btnWorkspace").click()
    page.wait_for_selector("#wsBtnMoi", state="visible", timeout=10000)   # danh sách vẽ sau lời gọi backend
    assert not loi, loi


def _tom_tat_khi_chon_so(page, api):
    """Chọn Sổ nhập (xuất từ workspace ĐANG MỞ) và đọc dòng tóm tắt trước khi bấm Nhập."""
    duong = api.export_du_lieu_dau_vao()["data"]["path"]
    page.set_input_files("#fileAny", duong)
    page.wait_for_selector("#importQueue:not([hidden])", timeout=15000)
    page.wait_for_function("() => /Sẵn sàng nhập/.test(document.querySelector('#importQueue').innerText)",
                           timeout=15000)
    return _chu(page, "#importQueue")


def test_tom_tat_truoc_khi_nhap_bo_luot_thi_khi_workspace_khong_co_diem_rieng(mo):
    page, api, goc, (truong, cty, sk), loi = mo
    _sang(page, sk, "Hội nghị XYZ")
    chu = _tom_tat_khi_chon_so(page, api)
    assert "Sẵn sàng nhập: 9 workshop" in chu and "nguyện vọng" in chu
    assert "lượt thi" not in chu
    # công ty (KPI một điểm cho cả người) cũng không có "lượt thi"
    page.locator("#btnClearQueue").click()
    _sang(page, cty, "Công ty ABC")
    chu = _tom_tat_khi_chon_so(page, api)
    assert "Sẵn sàng nhập: 6 dự án" in chu and "lượt thi" not in chu
    # trường học: còn "lượt thi" như cũ
    page.locator("#btnClearQueue").click()
    _sang(page, truong, "Trường học")
    assert "lượt thi" in _tom_tat_khi_chon_so(page, api)
    assert not loi, loi


# ------------------------------------------------------------------ chưa có dữ liệu

def test_chay_khi_chua_co_du_lieu_bao_viec_can_lam_va_khong_ghi_lich_su(mo):
    page, api, goc, (truong, cty, sk), loi = mo
    page.locator("#btnWorkspace").click()
    page.locator("#wsBtnMoi").click()
    page.fill("#wzTen", "Trống")
    page.locator("#wzTiep").click()
    page.fill("#wzNhan_person_vi", "Nhân viên")
    page.fill("#wzNhan_slot_vi", "Dự án")
    page.locator("#wzTiep").click()
    page.locator("#wzTiep").click()
    page.locator("#wzTao").click()
    page.wait_for_function(
        "n => document.querySelector('#wsTenHienTai').textContent === n", arg="Trống", timeout=10000)
    page.wait_for_selector("#dropZone")
    page.wait_for_timeout(500)
    # Cảnh báo dữ liệu không được nói "Dữ liệu đã sẵn sàng" khi chưa nạp gì
    chu = _chu(page, "#healthSummary")
    assert "sẵn sàng" not in chu and "Tải sổ nhập mẫu" in chu
    n_truoc = len(api.get_run_history()["data"])
    page.locator("#btnRun").click()
    page.wait_for_selector("#toastStack .toast.is-error", timeout=5000)
    thong_bao = page.locator("#toastStack .toast.is-error").first.inner_text()
    assert "Chưa có dữ liệu để sắp xếp" in thong_bao and "Sổ nhập dự án" in thong_bao
    assert page.locator("#btnRun").is_enabled()
    assert len(api.get_run_history()["data"]) == n_truoc              # không ghi một lần chạy rỗng
    assert not loi, loi


# ------------------------------------------------------------------ trình hướng dẫn

def _toi_buoc3(page, ten="Thử luật"):
    page.locator("#btnWorkspace").click()
    page.locator("#wsBtnMoi").click()
    page.fill("#wzTen", ten)
    page.locator("#wzTiep").click()
    page.locator("#wzTiep").click()


def test_wizard_buoc1_va_buoc3_khong_con_vi_du_cua_truong_hoc(mo):
    page, api, goc, (truong, cty, sk), loi = mo
    page.locator("#btnWorkspace").click()
    page.locator("#wsBtnMoi").click()
    assert "Trường" not in (page.locator("#wzTen").get_attribute("placeholder") or "")
    page.fill("#wzTen", "A")
    page.locator("#wzTiep").click()
    page.locator("#wzTiep").click()
    chu = _chu(page, "#wsHop")
    assert "như trường học" not in chu and "Khối" not in (page.locator("#wzTiers").get_attribute("placeholder") or "")
    # lời giải thích nằm dưới ô chọn (nhãn chọn ngắn, khỏi bị cắt), thay cho "như trường học"
    assert "nhường lại cho người khác" in page.locator("#wzTierModeGoiY").inner_text()
    page.select_option("#wzTierMode", "strict")
    assert "luôn được xếp trước nhóm thấp hơn" in page.locator("#wzTierModeGoiY").inner_text()
    assert "nhường lại" not in page.locator("#wzTierModeGoiY").inner_text()
    assert "điểm khác nhau ở từng chỗ" in page.locator("#wzScoreScopeGoiY").inner_text()
    page.select_option("#wzScoreScope", "per_person")
    assert "cho cả người" in page.locator("#wzScoreScopeGoiY").inner_text()
    assert not loi, loi


def test_wizard_chi_theo_nhom_noi_ro_hai_muc_bi_bo_qua_va_an_so_cho_du_thi(mo):
    page, api, goc, (truong, cty, sk), loi = mo
    _toi_buoc3(page)
    assert page.locator("#wzMaxTests").is_visible()
    page.select_option("#wzPriority", "tier")
    assert page.locator("#wzMaxTests").is_hidden()
    assert page.locator("#wzGhiChuChiNhom").is_visible()
    assert "bị bỏ qua" in page.locator("#wzGhiChuChiNhom").inner_text()
    # không khoá: hành vi cũ (chọn "suất dự trữ mềm" mà vẫn dùng danh sách nhóm) được giữ nguyên
    assert page.locator("#wzTierMode").is_enabled() and page.locator("#wzScoreScope").is_enabled()
    assert page.locator("#wzTiers").is_enabled()                  # thứ tự nhóm là thứ cần nhập
    page.select_option("#wzPriority", "score")
    assert page.locator("#wzMaxTests").is_visible()
    assert page.locator("#wzTierMode").is_enabled() and page.locator("#wzGhiChuChiNhom").is_hidden()
    assert not loi, loi


def test_wizard_diem_mot_nguoi_mot_so_an_o_du_thi(mo):
    page, api, goc, (truong, cty, sk), loi = mo
    _toi_buoc3(page)
    page.select_option("#wzScoreScope", "per_person")
    assert page.locator("#wzMaxTests").is_hidden()
    assert page.locator("#wzTierMode").is_enabled()               # điểm theo người vẫn dùng được nhóm cứng
    page.select_option("#wzScoreScope", "per_slot")
    assert page.locator("#wzMaxTests").is_visible()
    assert not loi, loi


def test_wizard_o_du_thi_an_roi_thi_gia_tri_hong_khong_chan_buoc_tiep(mo):
    """Ô đã ẩn thì không được chặn người dùng bằng lỗi họ không thấy chỗ sửa."""
    page, api, goc, (truong, cty, sk), loi = mo
    _toi_buoc3(page)
    page.fill("#wzMaxTests", "")
    page.select_option("#wzPriority", "tier")
    page.locator("#wzTiep").click()
    assert page.locator("#wzLoi").is_hidden() or not page.locator("#wzLoi").inner_text().strip()
    assert page.locator("#rvPriority").is_visible()               # sang được bước 4
    assert page.locator("#rvMaxTests").count() == 0                # và bước 4 không hiện dòng vô nghĩa
    assert page.locator("#rvTierMode").count() == 0 and page.locator("#rvScoreScope").count() == 0
    assert not loi, loi


def test_wizard_tom_tat_van_hien_so_du_thi_khi_co_diem_rieng_tung_cho(mo):
    page, api, goc, (truong, cty, sk), loi = mo
    _toi_buoc3(page)
    page.locator("#wzTiep").click()
    assert page.locator("#rvMaxTests").is_visible()
    assert page.locator("#rvTierMode").is_visible() and page.locator("#rvScoreScope").is_visible()
    assert not loi, loi
