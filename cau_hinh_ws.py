"""
cau_hinh_ws.py
==============
Cấu hình của một không gian làm việc (workspace): TỪ VỰNG (5 danh từ, mỗi
danh từ có nhãn vi/en) và LUẬT XẾP. Lưu TRONG app.db của chính workspace đó,
bảng `workspace_settings(key, value)`, một hàng khoá 'config' chứa JSON.

Giá trị mặc định là của TRƯỜNG HỌC (`MAC_DINH_TRUONG_HOC`). Thiếu hàng, hỏng
JSON, hay thiếu một khoá đều cho ra mặc định — nên CSDL cũ và mọi test cũ chạy
y như trước khi có module này.

Module này CHỈ đọc/ghi/kiểm cấu hình; việc dùng nó nằm ở chỗ khác. Các luật xếp
(`priority`, `tier_mode`, `score_scope`, `tiers`) được rbda_priority_pipeline.py
đọc (qua `luat_xep_cua`, `tham_so_luat`) và thật sự đổi AI ĐƯỢC SUẤT, dấu vân tay
kết quả và `run_history.luat_xep`; `max_choices`/`max_tests` là trần nhập liệu của
api_*.py; nhãn đi vào giao diện, sổ nhập và tệp xuất. Sửa cấu hình là sửa kết quả:
nơi quyết định (chạy xếp, trần nhập) phải đọc bằng `doc_cau_hinh(nghiem=True)`.
"""

from __future__ import annotations

import copy
import json
import os
import sqlite3

from nhan_ws import DANH_TU, NHAN_MAC_DINH
from rbda_priority_pipeline import (
    TRAN_CLB_THI_MOI_BUOI,
    TRAN_NGUYEN_VONG_MOI_BUOI,
    connect_db,
    khoa_ten_nhom,
)

KHOA_CAU_HINH = "config"

# Năm danh từ (DANH_TU, nguồn duy nhất ở nhan_ws.py): mọi nhãn hiển thị đều đi qua
# chúng, nên tập này là cố định — gõ sai tên danh từ phải báo lỗi chứ không được
# lặng lẽ thành một nhãn mồ côi.

NGANH = ("school", "company", "event", "custom")
UU_TIEN = ("score", "tier", "score+tier")
CHE_DO_NHOM = ("reserve", "strict")
PHAM_VI_DIEM = ("per_slot", "per_person")

# Trần hợp lệ của hai con số luật (khoảng đóng).
_MAX_CHOICES_TOI_DA = 20
_MAX_TESTS_TOI_DA = 20

# Trần độ dài của các chuỗi trong cấu hình. Cấu hình đến từ NGOÀI (zip nhập vào, JSON giao diện
# gửi lên, hay một app.db sửa tay) và đi khắp nơi: tiêu đề cửa sổ, tên sheet, cột Excel, thẻ
# giao diện. Chuỗi khổng lồ chỉ có thể là lỗi hay tấn công; một cấu hình thật không bao giờ cần.
TRAN_TEN = 300          # tên workspace (tiêu đề cửa sổ cắt ở 200; slug cắt ở 60)
TRAN_NHAN = 60          # mỗi nhãn vi/en và mỗi tên nhóm
TRAN_SO_NHOM = 50       # số nhóm trong `rules.tiers`
TRAN_JSON_BYTE = 64 * 1024   # kích thước JSON cấu hình được phép ĐỌC từ CSDL

# max_choices / max_tests lấy từ hai hằng của thuật toán — KHÔNG gõ lại con số
# lần thứ hai ở đây, để đổi trần ở một nơi thì mặc định đổi theo.
MAC_DINH_TRUONG_HOC = {
    "name": "",
    "industry": "school",
    "labels": copy.deepcopy(NHAN_MAC_DINH),
    "rules": {
        "max_choices": TRAN_NGUYEN_VONG_MOI_BUOI,
        "max_tests": TRAN_CLB_THI_MOI_BUOI,
        "priority": "score",
        "tier_mode": "reserve",
        "score_scope": "per_slot",
        "tiers": [],
    },
}


def _tron_sau(mac_dinh: dict, ghi_de: dict) -> dict:
    """Trộn `ghi_de` lên bản sao của `mac_dinh`; dict trộn đệ quy, còn lại thay hẳn.

    Danh sách (`tiers`) và `None` (`max_tests` = không giới hạn) THAY chứ không
    trộn: `None` là một giá trị có nghĩa, không phải "thiếu".
    """
    kq = copy.deepcopy(mac_dinh)
    for khoa, gia_tri in ghi_de.items():
        if isinstance(gia_tri, dict) and isinstance(kq.get(khoa), dict):
            kq[khoa] = _tron_sau(kq[khoa], gia_tri)
        else:
            kq[khoa] = copy.deepcopy(gia_tri)
    return kq


def _nhan_thieu_en_lay_vi(goc: dict, da_tron: dict) -> None:
    """Danh từ mà `goc` có `vi` nhưng không có `en` thì `en` = `vi`.

    Trộn đệ quy sẽ lấp chỗ trống đó bằng `en` MẶC ĐỊNH ("Student" cạnh
    "Nhân viên") — sai. Nhãn là một cặp đi cùng nhau; đã đặt `vi` mới thì
    `en` không đặt phải rơi về chính `vi` đó, đúng như quy tắc ghi.
    """
    nhan_goc = goc.get("labels")
    if not isinstance(nhan_goc, dict):
        return
    for dt, cap in nhan_goc.items():
        if (isinstance(cap, dict) and dt in da_tron["labels"]
                and "vi" in cap and not cap.get("en")):
            da_tron["labels"][dt]["en"] = da_tron["labels"][dt]["vi"]


def _kiem_chuoi(chu: str, ten_truong: str, toi_da: int) -> None:
    """Chuỗi hiển thị trong cấu hình: không quá `toi_da` ký tự, không ký tự điều khiển.

    NUL và các ký tự điều khiển phá tên tệp, tên sheet và dòng log; không nhãn thật nào cần."""
    if len(chu) > toi_da:
        raise ValueError("%s dài quá %d ký tự." % (ten_truong, toi_da))
    if any(ord(c) < 32 or ord(c) == 127 for c in chu):
        raise ValueError("%s chứa ký tự điều khiển." % ten_truong)


def _la_so_nguyen(v) -> bool:
    # bool là lớp con của int: True không được lọt qua như "1".
    return isinstance(v, int) and not isinstance(v, bool)


def _chuan_hoa(cfg) -> dict:
    """Trộn `cfg` lên mặc định, kiểm, và trả bản ĐẦY ĐỦ đã chuẩn hoá.

    Ném ValueError với câu nói rõ trường nào sai. Không sửa `cfg` của người gọi.
    """
    try:
        return _chuan_hoa_that(cfg)
    except RecursionError:
        # Từ điển lồng hàng nghìn tầng: trộn/sao chép sâu đệ quy tới tràn ngăn xếp.
        raise ValueError("Cấu hình lồng quá sâu.") from None


def _chuan_hoa_that(cfg) -> dict:
    if not isinstance(cfg, dict):
        raise ValueError("Cấu hình phải là một từ điển (dict).")

    la_khoa_la = set(cfg) - set(MAC_DINH_TRUONG_HOC)
    if la_khoa_la:
        raise ValueError("Khoá cấu hình không hợp lệ: %s." % ", ".join(sorted(map(str, la_khoa_la))))

    for muc in ("labels", "rules"):
        if muc in cfg and not isinstance(cfg[muc], dict):
            raise ValueError("'%s' phải là một từ điển (dict)." % muc)

    kq = _tron_sau(MAC_DINH_TRUONG_HOC, cfg)
    _nhan_thieu_en_lay_vi(cfg, kq)

    # --- tên, ngành ---
    if not isinstance(kq["name"], str):
        raise ValueError("name phải là chuỗi.")
    kq["name"] = kq["name"].strip()
    _kiem_chuoi(kq["name"], "name", TRAN_TEN)
    if kq["industry"] not in NGANH:
        raise ValueError("industry phải là một trong %s, nhận %r." % (list(NGANH), kq["industry"]))

    # --- nhãn ---
    la_dt = set(kq["labels"]) - set(DANH_TU)
    if la_dt:
        raise ValueError("Danh từ không hợp lệ trong labels: %s (chỉ có %s)."
                         % (", ".join(sorted(map(str, la_dt))), list(DANH_TU)))
    for dt in DANH_TU:
        cap = kq["labels"][dt]
        if not isinstance(cap, dict):
            raise ValueError("labels.%s phải là {'vi': ..., 'en': ...}." % dt)
        vi, en = cap.get("vi"), cap.get("en")
        if not isinstance(vi, str) or not vi.strip():
            raise ValueError("labels.%s.vi không được để trống." % dt)
        if en is not None and not isinstance(en, str):
            raise ValueError("labels.%s.en phải là chuỗi." % dt)
        vi = vi.strip()
        en = (en or "").strip()
        _kiem_chuoi(vi, "labels.%s.vi" % dt, TRAN_NHAN)
        _kiem_chuoi(en, "labels.%s.en" % dt, TRAN_NHAN)
        # Nhãn thành tiêu đề cột / tên sheet của Sổ nhập và tệp xuất. Chữ mở đầu bằng = + - @
        # bị Excel hiểu thành công thức (openpyxl ghi "=..." thành ô công thức thật), mà nhãn
        # có thể đến từ zip nhập vào. Không chấp nhận; đọc cấu hình hỏng thì rơi về mặc định.
        for ngon, chu in (("vi", vi), ("en", en)):
            if chu[:1] in ("=", "+", "-", "@"):
                raise ValueError("labels.%s.%s không được bắt đầu bằng '%s' "
                                 "(Excel sẽ hiểu là công thức)." % (dt, ngon, chu[0]))
        kq["labels"][dt] = {"vi": vi, "en": en or vi}

    # --- luật ---
    luat = kq["rules"]
    la_luat = set(luat) - set(MAC_DINH_TRUONG_HOC["rules"])
    if la_luat:
        raise ValueError("Luật không hợp lệ: %s." % ", ".join(sorted(map(str, la_luat))))

    mc = luat["max_choices"]
    if not _la_so_nguyen(mc) or not 1 <= mc <= _MAX_CHOICES_TOI_DA:
        raise ValueError("max_choices phải là số nguyên từ 1 đến %d, nhận %r."
                         % (_MAX_CHOICES_TOI_DA, mc))

    mt = luat["max_tests"]
    if mt is not None and (not _la_so_nguyen(mt) or not 0 <= mt <= _MAX_TESTS_TOI_DA):
        raise ValueError("max_tests phải là số nguyên từ 0 đến %d hoặc None (không giới hạn), nhận %r."
                         % (_MAX_TESTS_TOI_DA, mt))

    for khoa, cho_phep in (("priority", UU_TIEN), ("tier_mode", CHE_DO_NHOM),
                           ("score_scope", PHAM_VI_DIEM)):
        if luat[khoa] not in cho_phep:
            raise ValueError("%s phải là một trong %s, nhận %r." % (khoa, list(cho_phep), luat[khoa]))

    tiers = luat["tiers"]
    if not isinstance(tiers, list) or not all(isinstance(t, str) and t.strip() for t in tiers):
        raise ValueError("tiers phải là danh sách tên nhóm (chuỗi không rỗng).")
    if len(tiers) > TRAN_SO_NHOM:
        raise ValueError("tiers có quá nhiều nhóm (tối đa %d)." % TRAN_SO_NHOM)
    luat["tiers"] = [t.strip() for t in tiers]
    khoa_da_co = {}
    for t in luat["tiers"]:
        _kiem_chuoi(t, "tên nhóm trong tiers", TRAN_NHAN)
        # Thuật toán so nhóm bằng `khoa_ten_nhom` (bỏ dấu, hoa/thường, `_` `-`, khoảng trắng):
        # "Quản lý" và "quan_ly" là MỘT nhóm, nên hai tên đó trong cùng danh sách là nhập sai
        # chứ không phải hai hạng — hạng thứ hai sẽ không bao giờ có người.
        khoa = khoa_ten_nhom(t)
        if not khoa:
            raise ValueError("tên nhóm %r không có chữ nào." % t)
        if khoa in khoa_da_co:
            raise ValueError("tiers có tên nhóm trùng nhau: %r và %r." % (khoa_da_co[khoa], t))
        khoa_da_co[khoa] = t

    return kq


def tron_len(da_luu: dict, moi: dict) -> dict:
    """Trộn cấu hình `moi` (có thể chỉ một phần) lên cấu hình `da_luu` của workspace.

    Khác `chuan_hoa` (trộn lên mặc định trường học): đây là cho CẬP NHẬT — phần `moi` không
    nhắc tới thì giữ nguyên như đã lưu. `labels`: thay nguyên CẶP vi/en của danh từ nào được
    nhắc tới (nhãn là một cặp đi cùng nhau, xem `_nhan_thieu_en_lay_vi`); `rules`: thay từng
    khoá; khoá cấp trên (name, industry...): thay. Không sửa đầu vào, không kiểm — người gọi
    đưa kết quả qua `ghi_cau_hinh`.
    """
    kq = copy.deepcopy(da_luu)
    if not isinstance(moi, dict):
        return kq
    for khoa, gia_tri in moi.items():
        if khoa in ("labels", "rules") and isinstance(gia_tri, dict) \
                and isinstance(kq.get(khoa), dict):
            kq[khoa].update(copy.deepcopy(gia_tri))
        else:
            kq[khoa] = copy.deepcopy(gia_tri)
    return kq


def chuan_hoa(cfg: dict) -> dict:
    """Kiểm `cfg` (có thể thiếu khoá) và trả bản đầy đủ đã chuẩn hoá — không ghi gì.

    Cho nơi khác cần biết một cấu hình có hợp lệ không TRƯỚC khi làm việc tốn
    kém (vd dựng thư mục workspace). Ném ValueError như `ghi_cau_hinh`.
    """
    return _chuan_hoa(cfg)


def doc_cau_hinh(db_path: str, nghiem: bool = False) -> dict:
    """Cấu hình của workspace ở `db_path`, trộn lên mặc định trường học.

    Mặc định không bao giờ ném: tệp chưa có, bảng chưa có (CSDL cũ), hàng chưa có, JSON
    hỏng, hay giá trị không qua được kiểm đều cho ra mặc định. Đọc KHÔNG tạo
    tệp hay bảng — chỉ ghi mới làm vậy. Luôn trả bản sao mới.

    `nghiem=True` dành cho nơi ĐỌC RỒI GHI LẠI cấu hình (đổi tên, nhân bản, lưu mẫu):
    "mặc định" thay cho một cấu hình hiện có mà đọc không được (JSON hỏng, khoá lạ do bản
    phần mềm mới hơn ghi, CSDL đang bị khoá…) rồi được ghi đè lên chính nó là xoá lặng lẽ
    nhãn và luật của workspace. Ở chế độ này, CHỈ ba trường hợp "chưa có cấu hình" (tệp,
    bảng, hàng chưa có) cho ra mặc định; còn lại ném ValueError / sqlite3.Error.
    """
    mac_dinh = copy.deepcopy(MAC_DINH_TRUONG_HOC)
    if not os.path.isfile(db_path):
        return mac_dinh
    try:
        conn = connect_db(db_path)
        try:
            co_bang = conn.execute(
                "SELECT 1 FROM sqlite_master WHERE type = 'table' AND name = 'workspace_settings'"
            ).fetchone()
            if not co_bang:
                return mac_dinh
            # Kích thước đo trong SQL, TRƯỚC khi nạp giá trị: một hàng khổng lồ trong app.db sửa
            # tay không được kéo cả tiến trình tới hết bộ nhớ chỉ để rồi bị từ chối.
            dong = conn.execute(
                "SELECT CASE WHEN length(CAST(value AS BLOB)) <= ? THEN value END, "
                "length(CAST(value AS BLOB)) FROM workspace_settings WHERE key = ?",
                (TRAN_JSON_BYTE, KHOA_CAU_HINH),
            ).fetchone()
        finally:
            conn.close()
        if not dong or (dong[0] is None and dong[1] is None):
            return mac_dinh
        if dong[0] is None:
            raise ValueError("Cấu hình dài %d byte, quá trần %d." % (dong[1], TRAN_JSON_BYTE))
        return _chuan_hoa(json.loads(dong[0]))
    except (sqlite3.Error, ValueError, RecursionError) as e:
        # json.JSONDecodeError là con của ValueError, nên một câu bắt đủ cả JSON hỏng lẫn giá
        # trị sai. JSON lồng hàng chục nghìn tầng làm `json.loads` tràn ngăn xếp: RecursionError
        # KHÔNG phải ValueError, và để lọt thì chỉ một app.db xấu làm sập cả danh sách workspace.
        if nghiem:
            if isinstance(e, RecursionError):
                raise ValueError("Cấu hình lồng quá sâu.") from None
            raise
        return mac_dinh


def ghi_cau_hinh(db_path: str, cfg: dict) -> dict:
    """Kiểm rồi ghi cấu hình. Trả về bản đầy đủ đã chuẩn hoá và đã ghi.

    `cfg` có thể thiếu khoá (trộn lên mặc định). Ghi BẢN ĐẦY ĐỦ chứ không ghi
    phần thiếu: luật là thứ làm ra kết quả đã công bố, nên đổi mặc định trong
    mã sau này không được lặng lẽ đổi luật của một workspace đã tạo.

    Raises:
        ValueError: `cfg` sai — chưa ghi gì.
    """
    day_du = _chuan_hoa(cfg)
    conn = connect_db(db_path)
    try:
        # Tự dựng bảng: workspace dựng từ CSDL cũ chưa qua init_db vẫn ghi được.
        conn.execute(
            "CREATE TABLE IF NOT EXISTS workspace_settings (key TEXT PRIMARY KEY, value TEXT)")
        conn.execute(
            "INSERT OR REPLACE INTO workspace_settings (key, value) VALUES (?, ?)",
            (KHOA_CAU_HINH, json.dumps(day_du, ensure_ascii=False)),
        )
        conn.commit()
    finally:
        conn.close()
    return day_du


def nhan(cfg: dict, noun: str, lang: str) -> str:
    """Nhãn của danh từ `noun` theo ngôn ngữ `lang`; thiếu hay rỗng thì rơi về vi."""
    if noun not in DANH_TU:
        raise ValueError("Danh từ không hợp lệ: %r (chỉ có %s)." % (noun, list(DANH_TU)))
    cap = (cfg.get("labels") or {}).get(noun) or MAC_DINH_TRUONG_HOC["labels"][noun]
    return cap.get(lang) or cap.get("vi") or MAC_DINH_TRUONG_HOC["labels"][noun]["vi"]
