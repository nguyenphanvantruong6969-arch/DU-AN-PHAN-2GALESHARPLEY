"""Cấu hình của một KHÔNG GIAN LÀM VIỆC (workspace): từ vựng và luật chạy.

Mỗi workspace là một thư mục có app.db riêng; cấu hình nằm TRONG app.db đó,
bảng `workspace_settings(key, value)`, dạng JSON dưới khoá `config`. Nhờ vậy
sao lưu / chép app.db là mang theo cả cấu hình — không có tệp cấu hình thứ hai
để lệch nhau.

THIẾU DÒNG, THIẾU KHOÁ = MẶC ĐỊNH CỦA TRƯỜNG HỌC (`MAC_DINH_TRUONG_HOC`). Vì
thế app.db dựng bằng bản cũ, và mọi test cũ, chạy y hệt trước đây.

Module này chỉ LƯU và ĐỌC cấu hình. Nó không đổi hành vi thuật toán: việc cho
thuật toán/giao diện đọc cấu hình là việc của các bước sau.
"""

from __future__ import annotations

import copy
import json
import os
import sqlite3

from rbda_priority_pipeline import (
    TRAN_CLB_THI_MOI_BUOI,
    TRAN_NGUYEN_VONG_MOI_BUOI,
    connect_db,
    init_db,
)

KHOA_CAU_HINH = "config"

# Các giá trị hợp lệ — nguồn duy nhất, cho cả bước kiểm lẫn (sau này) giao diện chọn.
CAC_NGANH = ("school", "company", "event", "custom")
CAC_UU_TIEN = ("score", "tier", "score+tier")
CAC_CHE_DO_NHOM = ("reserve", "strict")
CAC_PHAM_VI_DIEM = ("per_slot", "per_person")

# Trần cứng của hai giới hạn. Không phải chính sách trường: chỉ chặn số vô lý.
TRAN_TOI_DA_NGUYEN_VONG = 20
TRAN_TOI_DA_THI = 20

# Năm danh từ của giao diện. Thứ tự giữ nguyên để đọc/ghi ổn định.
CAC_DANH_TU = ("person", "slot", "session", "group", "score")

MAC_DINH_TRUONG_HOC = {
    "name": "",
    "industry": "school",
    "labels": {
        "person": {"vi": "Học sinh", "en": "Student"},
        "slot": {"vi": "Câu lạc bộ", "en": "Club"},
        "session": {"vi": "Buổi", "en": "Session"},
        "group": {"vi": "Nhóm ưu tiên", "en": "Priority group"},
        "score": {"vi": "Điểm", "en": "Score"},
    },
    "rules": {
        "max_choices": TRAN_NGUYEN_VONG_MOI_BUOI,
        "max_tests": TRAN_CLB_THI_MOI_BUOI,
        "priority": "score",
        "tier_mode": "reserve",
        "score_scope": "per_slot",
        "tiers": [],
    },
}


def _tron_sau(mac_dinh, ghi_de):
    """Trộn `ghi_de` lên bản sao của `mac_dinh`; trả bản mới, không sửa đầu vào.

    Dict trộn từng khoá. Mọi giá trị khác (số, chuỗi, list `tiers`, `None` của
    `max_tests` = không giới hạn) THAY HẲN. Chỗ mặc định là dict mà giá trị lưu
    không phải dict (vd `"labels": {"person": "x"}`) thì bỏ giá trị lưu: một
    cấu hình hỏng không được làm hỏng cấu trúc mà code phía sau tin là có.
    """
    kq = copy.deepcopy(mac_dinh)
    if not isinstance(ghi_de, dict):
        return kq
    for k, v in ghi_de.items():
        if k in kq and isinstance(kq[k], dict):
            if isinstance(v, dict):
                kq[k] = _tron_sau(kq[k], v)
        else:
            kq[k] = copy.deepcopy(v)
    return kq


def doc_cau_hinh(db_path: str) -> dict:
    """Cấu hình của workspace = dòng `config` trộn lên mặc định trường học.

    KHÔNG BAO GIỜ ném lỗi và không tạo gì: tệp chưa có, chưa có bảng, chưa có
    dòng, JSON hỏng hay không phải dict đều trả về mặc định.
    """
    if not os.path.isfile(db_path):
        return copy.deepcopy(MAC_DINH_TRUONG_HOC)
    try:
        conn = connect_db(db_path)
        try:
            dong = conn.execute(
                "SELECT value FROM workspace_settings WHERE key = ?",
                (KHOA_CAU_HINH,),
            ).fetchone()
        finally:
            conn.close()
    except sqlite3.Error:
        return copy.deepcopy(MAC_DINH_TRUONG_HOC)
    if not dong or dong[0] is None:
        return copy.deepcopy(MAC_DINH_TRUONG_HOC)
    try:
        da_luu = json.loads(dong[0])
    except (TypeError, ValueError):
        return copy.deepcopy(MAC_DINH_TRUONG_HOC)
    return _tron_sau(MAC_DINH_TRUONG_HOC, da_luu)


def _la_so_nguyen(v) -> bool:
    # bool là con của int: `True` không được tính là "1 lựa chọn".
    return isinstance(v, int) and not isinstance(v, bool)


def _kiem_chon(ten, v, hop_le):
    if v not in hop_le:
        raise ValueError(
            "%s phải là một trong %s, nhận được %r"
            % (ten, ", ".join(hop_le), v)
        )


def chuan_hoa_cau_hinh(cfg) -> dict:
    """Trộn `cfg` lên mặc định, kiểm, rồi trả bản đầy đủ đã chuẩn hoá.

    Sai thì ném `ValueError` với câu nói rõ trường nào sai. Nhãn `en` trống
    được thay bằng `vi`. Khoá lạ được giữ nguyên (cấu hình của bản mới hơn
    không bị bản cũ làm rơi).
    """
    if not isinstance(cfg, dict):
        raise ValueError("Cấu hình phải là một dict")
    # `_tron_sau` lặng lẽ bỏ phần sai cấu trúc (đúng cho đọc cấu hình hỏng);
    # khi GHI thì phải báo, không thì người dùng tưởng đã lưu.
    for khoa in ("labels", "rules"):
        if khoa in cfg and not isinstance(cfg[khoa], dict):
            raise ValueError("%s phải là một dict" % khoa)
    for danh_tu, cap in (cfg.get("labels") or {}).items():
        if not isinstance(cap, dict):
            raise ValueError("Nhãn %s phải là dict có khoá vi/en" % danh_tu)
    kq = _tron_sau(MAC_DINH_TRUONG_HOC, cfg)

    if not isinstance(kq["name"], str):
        raise ValueError("name phải là chuỗi")
    kq["name"] = kq["name"].strip()
    _kiem_chon("industry", kq["industry"], CAC_NGANH)

    luat = kq["rules"]
    mc = luat["max_choices"]
    if not _la_so_nguyen(mc) or not 1 <= mc <= TRAN_TOI_DA_NGUYEN_VONG:
        raise ValueError(
            "max_choices phải là số nguyên từ 1 đến %d, nhận được %r"
            % (TRAN_TOI_DA_NGUYEN_VONG, mc)
        )
    mt = luat["max_tests"]
    if mt is not None and (
        not _la_so_nguyen(mt) or not 0 <= mt <= TRAN_TOI_DA_THI
    ):
        raise ValueError(
            "max_tests phải là số nguyên từ 0 đến %d hoặc None (không giới hạn), "
            "nhận được %r" % (TRAN_TOI_DA_THI, mt)
        )
    _kiem_chon("priority", luat["priority"], CAC_UU_TIEN)
    _kiem_chon("tier_mode", luat["tier_mode"], CAC_CHE_DO_NHOM)
    _kiem_chon("score_scope", luat["score_scope"], CAC_PHAM_VI_DIEM)

    tiers = luat["tiers"]
    if not isinstance(tiers, list) or not all(
        isinstance(t, str) and t.strip() for t in tiers
    ):
        raise ValueError("tiers phải là danh sách tên nhóm (chuỗi không rỗng)")
    luat["tiers"] = [t.strip() for t in tiers]
    if len(set(luat["tiers"])) != len(luat["tiers"]):
        raise ValueError("tiers có tên nhóm trùng nhau")

    for danh_tu in CAC_DANH_TU:
        nhan_ = kq["labels"][danh_tu]
        vi, en = nhan_.get("vi"), nhan_.get("en")
        if not isinstance(vi, str) or not vi.strip():
            raise ValueError("Nhãn %s.vi không được để trống" % danh_tu)
        if en is not None and not isinstance(en, str):
            raise ValueError("Nhãn %s.en phải là chuỗi" % danh_tu)
        vi = vi.strip()
        nhan_["vi"] = vi
        nhan_["en"] = (en or "").strip() or vi
    return kq


def ghi_cau_hinh(db_path: str, cfg: dict) -> dict:
    """Kiểm rồi ghi cấu hình vào `workspace_settings`; trả bản đã chuẩn hoá.

    `cfg` có thể chỉ có một phần: phần thiếu lấy từ mặc định. Bản GHI là bản
    đầy đủ đã chuẩn hoá. Kiểm xong mới mở CSDL, nên đầu vào sai không để lại gì.
    """
    kq = chuan_hoa_cau_hinh(cfg)
    init_db(db_path)
    conn = connect_db(db_path)
    try:
        conn.execute(
            "INSERT INTO workspace_settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (KHOA_CAU_HINH, json.dumps(kq, ensure_ascii=False)),
        )
        conn.commit()
    finally:
        conn.close()
    return kq


def nhan(cfg: dict, noun: str, lang: str = "vi") -> str:
    """Nhãn của danh từ `noun` bằng `lang`; thiếu/trống thì lùi về `vi`.

    `cfg` là kết quả `doc_cau_hinh`. Danh từ lạ → `KeyError` (lỗi lập trình,
    không phải lỗi người dùng nên không nuốt).
    """
    cap = cfg["labels"][noun]
    if lang != "vi":
        v = cap.get(lang)
        if isinstance(v, str) and v.strip():
            return v
    return cap["vi"]
