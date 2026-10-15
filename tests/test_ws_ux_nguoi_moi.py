"""Vòng thử "người dùng MỚI" (TASK 11, UX_PILOT_NOTES.md): mỗi mục đã sửa có một test ở đây.

Hai người dùng giả định chưa từng thấy phần mềm — một chuyên viên nhân sự (công ty: KPI theo người,
nhóm xếp cứng) và một người tổ chức sự kiện (chỉ theo hạng vé, 3 phiên). Họ mở phần mềm, tạo
workspace, tải sổ mẫu, nạp, chạy, đọc kết quả, xuất Excel. Những chỗ họ vấp mà sửa được thì sửa;
test ở đây giữ cho chúng khỏi quay lại.

Phần A không cần trình duyệt. Phần B dùng Chromium thật (bỏ qua nếu máy không có).
"""

# ruff: noqa: F811, F401  (fixture `ba_ws` nhập từ tệp khác rồi dùng làm tham số: cách pytest nạp fixture dùng chung)
import io
import json
import os
import re
import subprocess

import pytest

import i18n_errors
import nhan_ws
import so_nhap
from test_ws_e2e import ba_ws  # (fixture module-scoped: ba workspace đã chạy xong)
from test_ws_nhan import _STUB, can_node, _chay_js, node
from test_ws_so_nhap import _bytes, _clb, _doc, _hs

openpyxl = pytest.importorskip("openpyxl")

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NHAN_CTY = {"person": {"vi": "Nhân viên", "en": "Employee"}, "slot": {"vi": "Dự án", "en": "Project"},
            "session": {"vi": "Quý", "en": "Quarter"}, "group": {"vi": "Cấp bậc", "en": "Level"},
            "score": {"vi": "KPI", "en": "KPI"}}
NHAN_SK = {"person": {"vi": "Khách tham dự", "en": "Attendee"}, "slot": {"vi": "Workshop", "en": "Workshop"},
           "session": {"vi": "Phiên", "en": "Slot"}, "group": {"vi": "Hạng vé", "en": "Ticket"},
           "score": {"vi": "Điểm", "en": "Score"}}
CFG_CTY = {"labels": NHAN_CTY, "rules": {"max_choices": 3, "max_tests": 2, "priority": "score+tier",
                                         "tier_mode": "strict", "score_scope": "per_person",
                                         "tiers": ["Senior", "Mid", "Junior"]}}
CFG_SK = {"labels": NHAN_SK, "rules": {"max_choices": 2, "max_tests": 0, "priority": "tier",
                                       "tier_mode": "strict", "score_scope": "per_slot",
                                       "tiers": ["VIP", "Member", "Guest"]}}
TU_TRUONG = re.compile(r"học sinh|câu lạc bộ|\bCLB\b|giáo viên|thời khoá|\bem\b|Tin học|Bóng rổ|chinh_sach",
                       re.IGNORECASE)


# ====================================================================== A. không cần trình duyệt

def _tieu_de(wb, ten):
    return [c.value for c in wb[ten][1]]


def test_sheet_tier_only_khong_con_cot_diem_va_nhap_lai_khong_loi():
    """Sổ mẫu của workspace chỉ-theo-nhóm không có "Điểm 1, Điểm 2…" (bảng "đã thi" vô nghĩa)."""
    clubs = [_clb("w1", "Workshop 1"), _clb("w2", "Workshop 2")]
    hs = [_hs("K1", "Khách 1", [{"club_id": "w1", "thi": False, "diem": ""},
                                {"club_id": "w2", "thi": False, "diem": ""}], nhom="VIP")]
    du = _bytes(clubs, hs, cfg=CFG_SK)
    wb = openpyxl.load_workbook(io.BytesIO(du))
    tieu_de = _tieu_de(wb, "2. Khách tham dự")
    assert tieu_de[:3] == ["Mã HS", "Họ tên", "Hạng vé"]
    assert [t for t in tieu_de if t.startswith("Điểm")] == []
    assert tieu_de[3:5] == ["NV1", "NV2"]
    doc = _doc(du, cfg=CFG_SK)
    assert not doc["loi"], doc["loi"]
    assert [x["club_id"] for x in doc["students"][0]["nv"]] == ["w1", "w2"]
    assert doc["students"][0]["reserve_group"] == "VIP"


def test_sheet_chi_theo_nhom_van_doc_duoc_so_cu_con_cot_diem_trong():
    """Sổ cũ (còn cột Điểm k, để trống) vẫn nạp được vào workspace chỉ-theo-nhóm."""
    cu = _bytes([_clb("w1", "W1")], [_hs("K1", "K", [{"club_id": "w1", "thi": False, "diem": ""}])])
    doc = _doc(cu, cfg=CFG_SK)
    assert not doc["loi"], doc["loi"]


def test_sheet_van_giu_cot_diem_khi_co_diem_theo_cho():
    """Chỉ `priority = tier` bỏ cột điểm; điểm theo chỗ (cả khi nhóm cứng) vẫn có "Điểm k"."""
    cfg = {"labels": NHAN_SK, "rules": {"priority": "score+tier", "tier_mode": "strict",
                                        "score_scope": "per_slot", "tiers": ["VIP"]}}
    wb = openpyxl.load_workbook(io.BytesIO(_bytes([_clb("w1", "W1")], [], cfg=cfg)))
    assert "Điểm 1" in _tieu_de(wb, "2. Khách tham dự")


@pytest.mark.parametrize("cfg", [CFG_CTY, CFG_SK], ids=["cong_ty", "su_kien"])
def test_huong_dan_sheet_khong_con_chu_truong_hoc_va_giai_thich_cot_co_dinh(cfg):
    dong = so_nhap.huong_dan(cfg)
    chu = "\n".join(dong)
    # "Tên CLB" / "Mã CLB" là TIÊU ĐỀ CỘT (hợp đồng, xem mục lớn trong UX_PILOT_NOTES.md): được nhắc
    # nguyên chữ, kèm lời giải thích nghĩa của cột
    chu_ngoai_tieu_de = chu.replace("Tên CLB", "").replace("Mã CLB", "")
    assert not TU_TRUONG.search(chu_ngoai_tieu_de), TU_TRUONG.findall(chu_ngoai_tieu_de)
    # tiêu đề cột giữ nguyên (hợp đồng) nên hướng dẫn phải nói cột đó là gì
    nhan = cfg["labels"]
    assert 'Cột "Tên CLB" (tên %s)' % nhan["slot"]["vi"].lower() in chu
    assert 'Cột "Mã HS" (mã %s)' % nhan["person"]["vi"].lower() in chu
    assert "NV = nguyện vọng" in chu
    # các bước đánh số liên tục, không nhảy cóc
    so_buoc = [int(m) for m in re.findall(r"^Bước (\d+)\.", chu, re.M)]
    assert so_buoc == list(range(1, len(so_buoc) + 1))


def test_huong_dan_chi_theo_nhom_khong_nhac_diem_va_thi():
    chu = "\n".join(so_nhap.huong_dan(CFG_SK))
    assert "Điểm" not in chu and "chữ  thi" not in chu and "đã thi" not in chu
    assert "không có tác dụng" in chu            # cột Suất ưu tiên vô nghĩa khi nhóm xếp cứng


def test_huong_dan_kpi_khong_noi_da_thi():
    chu = "\n".join(so_nhap.huong_dan(CFG_CTY))
    assert "đã thi" not in chu and "KPI" in chu


def test_huong_dan_mac_dinh_truong_hoc_khong_doi():
    assert so_nhap.huong_dan(None) == so_nhap.HUONG_DAN
    assert so_nhap.huong_dan({"rules": {}}) == so_nhap.HUONG_DAN


def test_ten_tep_so_nhap_theo_nhan_cho_xep():
    assert nhan_ws.ten_tep_so_nhap(None) == "SO_NHAP_CLB"
    assert nhan_ws.ten_tep_so_nhap(nhan_ws.sao_nhan_mac_dinh()) == "SO_NHAP_CLB"
    assert nhan_ws.ten_tep_so_nhap(NHAN_CTY) == "SO_NHAP_DU_AN"
    assert nhan_ws.ten_tep_so_nhap(NHAN_SK) == "SO_NHAP_WORKSHOP"
    assert nhan_ws.ten_tep_so_nhap({"slot": {"vi": "???", "en": "x"}}) == "SO_NHAP"


# ---- thông báo lỗi cho workspace một buổi: không nói "ở quý -"

def _loi_qua_tran(ma, buoi, **them):
    return {"code": ma, "params": dict(sheet="2. Nhân viên", dong=7, student_id="NV07", n=4, tran=3,
                                       buoi=buoi, **them)}


@pytest.mark.parametrize("ma", ["so_nhap_qua_tran_nv", "so_nhap_qua_tran_thi"])
def test_loi_qua_tran_mot_buoi_khong_noi_buoi_gach_ngang(ma):
    for lang in ("vi", "en"):
        thang = i18n_errors.format_message(ma, _loi_qua_tran(ma, "-")["params"], lang, nhan=NHAN_CTY)
        assert " -," not in thang and " - " not in thang and "Quý -" not in thang, thang
        assert "NV07" in thang and "3" in thang and "4" in thang
        trong = i18n_errors.format_message(ma, _loi_qua_tran(ma, "")["params"], lang, nhan=NHAN_CTY)
        assert trong == thang


@pytest.mark.parametrize("ma", ["so_nhap_qua_tran_nv", "so_nhap_qua_tran_thi"])
def test_loi_qua_tran_nhieu_buoi_van_noi_ten_buoi(ma):
    thang = i18n_errors.format_message(ma, _loi_qua_tran(ma, "Phiên 2")["params"], "vi", nhan=NHAN_SK)
    assert "Phiên 2" in thang


@can_node
@pytest.mark.parametrize("ma", ["so_nhap_qua_tran_nv", "so_nhap_qua_tran_thi"])
def test_loi_qua_tran_js_giong_python(ma):
    """Biến thể "không buổi" ở i18n.js trùng từng chữ với bên Python."""
    for buoi in ("-", "", "Phiên 2"):
        loi = _loi_qua_tran(ma, buoi)
        ra = _chay_js({"nhan": NHAN_CTY, "loi": [loi]})
        for lang in ("vi", "en"):
            mong = i18n_errors.format_message(ma, loi["params"], lang, nhan=NHAN_CTY)
            assert ra[lang]["_loi"][0] == mong, (buoi, lang)


def test_loi_qua_tran_that_tu_so_nhap_mot_buoi_dung_bien_the():
    """Đi hết đường từ sổ thật: 4 nguyện vọng, trần 3, một buổi -> câu không có dấu gạch."""
    clubs = [_clb(c, c.upper()) for c in "abcde"]
    hs = [_hs("NV1", "n", [{"club_id": c, "thi": False, "diem": ""} for c in "abcd"])]
    cfg = {"labels": NHAN_CTY, "rules": {"max_choices": 3}}
    loi = _doc(_bytes(clubs, hs, cfg=cfg), cfg=cfg)["loi"]
    assert [x["code"] for x in loi] == ["so_nhap_qua_tran_nv"]
    assert loi[0]["params"]["buoi"] == "-"
    assert " -," not in i18n_errors.format_message(loi[0]["code"], loi[0]["params"], "vi", nhan=NHAN_CTY)


def test_loi_qua_tran_nhieu_buoi_that_goi_buoi_bang_ten_dep():
    """Mã buổi `phien_2` -> "Phiên 2" trong câu lỗi (nhãn buổi của workspace là Phiên)."""
    clubs = [_clb("a", "A", buoi="phien_1"), _clb("b", "B", buoi="phien_2"),
             _clb("c", "C", buoi="phien_2"), _clb("d", "D", buoi="phien_2")]
    hs = [_hs("K1", "k", [{"club_id": c, "thi": False, "diem": ""} for c in "bcd"])]
    cfg = {"labels": NHAN_SK, "rules": {"max_choices": 2, "priority": "tier", "tier_mode": "strict",
                                        "tiers": ["VIP"]}}
    loi = _doc(_bytes(clubs, hs, cfg=cfg), cfg=cfg)["loi"]
    assert [x["code"] for x in loi] == ["so_nhap_qua_tran_nv"]
    assert loi[0]["params"]["buoi"] == "Phiên 2"


def test_loi_sai_so_nhap_noi_cach_sua_khong_chua_clb_cua_truong_hoc():
    """Báo lỗi "không phải sổ nhập" và "quá lớn" gọi đúng tên sổ của workspace, kèm cách sửa."""
    for ma, tham_so in (("so_nhap_khong_phai_so", {}), ("so_nhap_chi_nhan_xlsx", {}),
                        ("file_too_large", {"size_mb": 50, "max_mb": 10})):
        for lang in ("vi", "en"):
            chu = i18n_errors.format_message(ma, tham_so, lang, nhan=NHAN_CTY)
            assert "CLB" not in chu.replace("Mã CLB", "") and "Club" not in chu, (ma, lang, chu)
            assert "trường" not in chu.lower() and "school" not in chu.lower(), (ma, lang, chu)
    chu = i18n_errors.format_message("so_nhap_khong_phai_so", {}, "vi", nhan=NHAN_CTY)
    assert "Tải sổ nhập mẫu" in chu and '"1. Dự án"' in chu and '"2. Nhân viên"' in chu


def test_chuoi_mac_dinh_truong_hoc_cua_cac_thong_bao_khong_doi():
    """Mặc định trường học vẫn ra đúng chữ cũ (không ai bị đổi chữ vì vòng thử này)."""
    chu = i18n_errors.format_message("so_nhap_chi_nhan_xlsx", {}, "vi")
    assert "Sổ nhập CLB" in chu
    chu = i18n_errors.format_message("file_too_large", {"size_mb": 50, "max_mb": 10}, "vi")
    assert "của một trường" in chu


# ---- chữ của trình hướng dẫn tạo workspace

@can_node
def test_chu_trinh_huong_dan_da_sua_khong_con_gia_dinh_truong_hoc():
    khoa = ["ws_r_max_tests", "ws_r_ss_per_person", "ws_r_ss_per_slot", "ws_r_tiers_ph",
            "ws_r_tm_reserve", "ws_r_tm_strict", "ws_v_max_tests", "ws_wz_ten_ph"]
    ra = _chay_js({"khoa": khoa})
    for lang in ("vi", "en"):
        for k in khoa:
            chu = ra[lang][k]
            assert chu and "{" not in chu, (lang, k, chu)
            assert "như trường học" not in chu and "as in schools" not in chu, (lang, k)
            assert "Khối" not in chu and "Trường" not in chu, (lang, k)
    assert "dự thi" in ra["vi"]["ws_r_max_tests"]
    # đủ hai ngôn ngữ: mọi khoá mới của vòng này có cả vi và en
    moi = ["legend_general_cung", "th_reserve_group_cung", "nav_admin_cung", "admin_title_cung",
           "admin_desc_cung", "admin_reserve_assign_title_cung", "placeholder_reserve_group_apply_cung",
           "th_current_reserve_group_cung", "xuat_canh_bao_khong_diem", "fallback_desc_khong_thi",
           "fallback_step2_title_khong_thi", "fallback_step2_hint_khong_thi", "so_nhap_tom_tat_khong_thi",
           "health_chua_co_du_lieu", "chay_chua_co_du_lieu", "ws_r_max_tests_goi_y", "ws_r_chi_nhom_ghi_chu"]
    ra = _chay_js({"khoa": moi, "tham_so": {"max_choices": 3, "n_clb": 1, "n_hoc_sinh": 2, "n_buoi": 1,
                                              "n_nguyen_vong": 3}, "nhan": NHAN_CTY})
    for lang in ("vi", "en"):
        for k in moi:
            assert ra[lang][k] and ra[lang][k] != k, (lang, k)


# ---- mã buổi hiện thành tên người đọc được ("Phiên 2", không phải `phien_2`)

MA_BUOI = ["phien_1", "phien_12", "slot_2", "Slot_2", "thu_2", "chu_nhat", "phien_", "phien_x", "", "kho_1"]


def test_ten_buoi_python():
    assert nhan_ws.ten_buoi("phien_2", NHAN_SK) == "Phiên 2"
    assert nhan_ws.ten_buoi("phien_2", NHAN_SK, "en") == "Slot 2"       # nhãn en của workspace
    assert nhan_ws.ten_buoi("slot_3", NHAN_SK) == "Phiên 3"             # nhận cả tiền tố tiếng Anh
    assert nhan_ws.ten_buoi("thu_2", NHAN_SK) == "thu_2"                 # mã khác giữ nguyên
    assert nhan_ws.ten_buoi("ca_1", NHAN_CTY) == "ca_1"                  # "ca" không phải nhãn buổi của công ty
    assert nhan_ws.ten_buoi("quy_1", NHAN_CTY) == "Quý 1"                # không dấu, hoa thường: "Quý" -> quy


@can_node
def test_ten_buoi_js_giong_python():
    """`I18N.tenBuoi` (dùng ở mọi bảng, ô chọn và chip buổi) trùng từng chữ với `nhan_ws.ten_buoi`."""
    script = (_STUB + """
global.window = {}; require(process.argv[1]); require(process.argv[2]);
window.dispatchEvent = () => {};
const I = window.I18N; const cfg = JSON.parse(process.argv[3]);
const ra = {};
for (const [ten, nhan] of Object.entries(cfg.nhan)) {
  I.setLabels(nhan); ra[ten] = {};
  for (const lang of ["vi", "en"]) ra[ten][lang] = cfg.ma.map((m) => I.tenBuoi(m, lang));
}
process.stdout.write(JSON.stringify(ra));""")
    nhan = {"sk": NHAN_SK, "cty": NHAN_CTY, "mac_dinh": nhan_ws.sao_nhan_mac_dinh()}
    ra = json.loads(subprocess.run(
        [node, "-e", script, "--", os.path.join(GOC, "i18n_loi.js"), os.path.join(GOC, "i18n.js"),
         json.dumps({"nhan": nhan, "ma": MA_BUOI})],
        capture_output=True, text=True, check=True, encoding="utf-8").stdout)
    for ten, n in nhan.items():
        for lang in ("vi", "en"):
            mong = [nhan_ws.ten_buoi(m, n, lang) for m in MA_BUOI]
            assert ra[ten][lang] == mong, (ten, lang, ra[ten][lang], mong)


def _tham_so_buoi(ma):
    return {"health_oversubscribed_buoi": dict(buoi="phien_1", n_seats=12, n_students=30, n_short=18),
            "max_pref_moi_buoi": dict(buoi="phien_2", tran=3),
            "so_nhap_qua_tran_nv": dict(sheet="s", dong=1, student_id="K1", buoi="phien_2", n=4, tran=3)}[ma]


@pytest.mark.parametrize("ma", ["health_oversubscribed_buoi", "max_pref_moi_buoi", "so_nhap_qua_tran_nv"])
def test_cau_loi_hien_ten_phien_khong_hien_ma_noi_bo(ma):
    """"Phiên phien_1 có tổng 12 chỗ" (cảnh báo dữ liệu) -> "Phiên 1 có tổng 12 chỗ"."""
    for lang in ("vi", "en"):
        chu = i18n_errors.format_message(ma, _tham_so_buoi(ma), lang, nhan=NHAN_SK)
        assert "phien_" not in chu, chu
        ten = nhan_ws.nhan_ngon_ngu(NHAN_SK, "session", lang)
        assert not re.search(r"(%s)\s+%s" % (ten, ten), chu, re.I), chu        # không "phiên Phiên 1"
        assert re.search(r"%s \d" % ten, chu, re.I), chu


def test_cau_loi_truong_hoc_giu_nguyen_ma_buoi():
    """Trường học: `thu_3` không phải mã dạng "<nhãn buổi>_<số>", câu giữ y nguyên."""
    chu = i18n_errors.format_message("max_pref_moi_buoi", {"buoi": "thu_3", "tran": 10}, "vi")
    assert "thu_3" in chu


@can_node
@pytest.mark.parametrize("ma", ["health_oversubscribed_buoi", "max_pref_moi_buoi", "so_nhap_qua_tran_nv"])
def test_cau_loi_ten_phien_js_giong_python(ma):
    loi = {"code": ma, "params": _tham_so_buoi(ma)}
    ra = _chay_js({"nhan": NHAN_SK, "loi": [loi]})
    for lang in ("vi", "en"):
        assert ra[lang]["_loi"][0] == i18n_errors.format_message(ma, loi["params"], lang, nhan=NHAN_SK), lang


# ====================================================================== tệp Excel kết quả theo ngành

TU_TRUONG_XLSX = re.compile(r"học sinh|câu lạc bộ|giáo viên|thời khoá|\bem\b|nhà trường|cả tuần|\btuần\b",
                            re.IGNORECASE)


def _xuat_xlsx(ba_ws, slug, tmp_path):
    """Mở workspace `slug`, xuất sổ Excel kết quả, trả {tên trang: [[ô…]…]} (chữ của mọi ô)."""
    assert ba_ws.api.open_workspace(slug)["ok"]
    ra = ba_ws.api.export_ket_qua(str(tmp_path / ("kq_%s.xlsx" % slug)))
    assert ra["ok"], ra["errors"]
    wb = openpyxl.load_workbook(ra["data"]["path"])
    return {ws.title: [[("" if c is None else str(c)) for c in row] for row in ws.iter_rows(values_only=True)]
            for ws in wb.worksheets}


def _tat_ca_chu(trang):
    return "\n".join(c for dong in trang.values() for hang in [dong] for h in hang for c in h if c)


def _hang_tieu_de(trang, *tu_khoa):
    """Hàng tiêu đề chứa đủ mọi từ khoá (một trang có thể có nhiều bảng cùng cột "Mã …")."""
    return next(h for h in trang if all(k in h for k in tu_khoa))


def test_xlsx_su_kien_nhom_cung_khong_con_cot_va_chu_cua_suat_du_tru_va_truong_hoc(ba_ws, tmp_path):
    trang = _xuat_xlsx(ba_ws, ba_ws.sk, tmp_path)
    chu = _tat_ca_chu(trang)
    assert not TU_TRUONG_XLSX.search(chu), TU_TRUONG_XLSX.findall(chu)
    assert "dự trữ" not in chu.lower() and "diện trúng tuyển" not in chu.lower()
    # sự kiện nhiều phiên: trang danh sách là LỊCH XẾP (mỗi phiên một cột), không phải "thời khoá biểu"
    lich = trang["Danh sách khách"]
    assert lich[0][0] == "LỊCH XẾP WORKSHOP CẢ ĐỢT XẾP", lich[0][0]
    assert _hang_tieu_de(lich, "Mã khách", "Phiên 1", "Phiên 3")
    # trang từng workshop: cột nhóm mang tên "Hạng vé" (không phải "Nhóm dự trữ" / "Diện trúng tuyển")
    theo = trang["Theo workshop"]
    tieu_de = _hang_tieu_de(theo, "Mã khách", "Hạng vé")
    assert "Nhóm dự trữ" not in tieu_de and "Diện trúng tuyển" not in tieu_de
    cot_hang = tieu_de.index("Hạng vé")
    hang_ve = {h[cot_hang] for h in theo if len(h) > cot_hang and h[cot_hang] and h != tieu_de
               and h[0].isdigit()}
    assert hang_ve and hang_ve <= {"VIP", "Diễn giả", "Thường"}, hang_ve   # tên trong luật
    tk = trang["Thống kê"]
    chu_tk = _tat_ca_chu({"tk": tk})
    assert "SUẤT DỰ TRỮ" not in chu_tk and "Trong đó diện dự trữ" not in chu_tk
    assert "TỪNG WORKSHOP" in chu_tk


def test_xlsx_su_kien_ten_phien_dep_o_moi_trang(ba_ws, tmp_path):
    trang = _xuat_xlsx(ba_ws, ba_ws.sk, tmp_path)
    chu = _tat_ca_chu(trang)
    assert "phien_" not in chu, re.findall(r".{0,20}phien_.{0,20}", chu)
    assert "Phiên 1" in chu and "Phiên 3" in chu
    dau_vet = trang[next(t for t in trang if t.startswith("Dấu vết"))]
    cac_dong = {h[0]: h[1] for h in dau_vet if len(h) > 1}
    assert cac_dong["Phiên đã chạy"] == "Phiên 1, Phiên 2, Phiên 3"


def test_xlsx_cong_ty_cot_nhom_mang_ten_cap_bac_va_hien_ten_trong_luat(ba_ws, tmp_path):
    trang = _xuat_xlsx(ba_ws, ba_ws.cty, tmp_path)
    chu = _tat_ca_chu(trang)
    assert not TU_TRUONG_XLSX.search(chu), TU_TRUONG_XLSX.findall(chu)
    assert "dự trữ" not in chu.lower()
    ds = trang["Danh sách nhân viên"]
    tieu_de = _hang_tieu_de(ds, "Mã nhân viên", "Tên dự án")
    assert "Cấp bậc" in tieu_de and "Nhóm dự trữ" not in tieu_de
    cot = tieu_de.index("Cấp bậc")
    cap = {h[cot] for h in ds[ds.index(tieu_de) + 1:] if len(h) > cot and h[cot]}
    assert cap and cap <= {"Quản lý", "Chuyên viên", "Nhân viên mới"}, cap       # không phải quan_ly
    huong_dan = _tat_ca_chu({"hd": trang["Hướng dẫn"]})
    assert "Số nhân viên đã có dự án" in huong_dan and "Số nhân viên chưa có chỗ" in huong_dan


def test_xlsx_truong_hoc_van_dung_chu_cu(ba_ws, tmp_path):
    """Trường học mặc định: tệp xuất không đổi — vẫn "em", "giáo viên", cột diện trúng tuyển."""
    trang = _xuat_xlsx(ba_ws, ba_ws.truong, tmp_path)
    chu = _tat_ca_chu(trang)
    assert "Số em đã có câu lạc bộ" in chu or "Số em đã có CLB" in chu
    assert "giáo viên" in chu
    ds = trang["Danh sách học sinh"]
    tieu_de = _hang_tieu_de(ds, "Mã học sinh")
    assert "Diện trúng tuyển" in tieu_de and "Nhóm dự trữ" in tieu_de
    assert "SUẤT DỰ TRỮ DÙNG TỚI ĐÂU" in _tat_ca_chu({"tk": trang["Thống kê"]})


def test_so_nhap_xuat_dau_vao_dat_ten_theo_nhan_cho_xep(ba_ws, tmp_path):
    for slug, mong in ((ba_ws.cty, "SO_NHAP_DU_AN"), (ba_ws.sk, "SO_NHAP_WORKSHOP"), (ba_ws.truong, "SO_NHAP_CLB")):
        assert ba_ws.api.open_workspace(slug)["ok"]
        ten = os.path.basename(ba_ws.api.tao_so_nhap_mau()["data"]["path"])
        assert ten.startswith(mong) and ten.endswith(".xlsx"), (slug, ten)
        ten = os.path.basename(ba_ws.api.export_du_lieu_dau_vao()["data"]["path"])
        assert re.fullmatch(mong + r"_\d{8}_\d{4}\.xlsx", ten), (slug, ten)


def test_so_nhap_mau_su_kien_khong_co_cot_diem_nhung_nhap_lai_duoc(ba_ws):
    """Sổ mẫu và sổ xuất của sự kiện (chỉ theo hạng vé) không có "Điểm 1…"; nạp lại không lỗi."""
    assert ba_ws.api.open_workspace(ba_ws.sk)["ok"]
    for ra in (ba_ws.api.tao_so_nhap_mau(), ba_ws.api.export_du_lieu_dau_vao()):
        wb = openpyxl.load_workbook(ra["data"]["path"])
        tieu_de = [c.value for c in wb["2. Khách"][1]]
        assert not [t for t in tieu_de if str(t).startswith("Điểm")], tieu_de
    import base64
    with open(ba_ws.api.export_du_lieu_dau_vao()["data"]["path"], "rb") as f:
        du = base64.b64encode(f.read()).decode()
    xem = ba_ws.api.xem_truoc_so_nhap(du)
    assert xem["ok"], xem["errors"]
    assert not xem["data"].get("loi"), xem["data"].get("loi")
