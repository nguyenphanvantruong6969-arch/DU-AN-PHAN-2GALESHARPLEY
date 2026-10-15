# -*- coding: utf-8 -*-
"""Sinh và soát bộ dữ liệu đầu vào cho phần mềm phân bổ câu lạc bộ (RB-DA).

Ba chế độ:

    python sinh_du_lieu.py tao   --spec truong.json --ra ./bo_moi
    python sinh_du_lieu.py ngau  --ra ./bo_moi  --hoc-sinh 180 --buoi thu_2,thu_4,thu_6
    python sinh_du_lieu.py soat  ./bo_moi

`tao`  — dựng từ một bản khai báo JSON tường minh (bạn nắm toàn quyền).
`ngau` — dựng một trường ngẫu nhiên nhưng HỢP LỆ, tất định theo `--seed`.
`soat` — soát một bộ đã có, không sửa gì.

WORKSPACE (không phải trường học): thêm `--cau-hinh config.json` (cùng khuôn với hàng
'config' của bảng workspace_settings) để sổ dùng nhãn, trần nguyện vọng / thi và luật
điểm / nhóm của workspace đó; hoặc `ngau --kich-ban company|event` để dựng sẵn một công ty
(300 nhân viên, 12 dự án, KPI theo người, nhóm cứng) hay một sự kiện (800 khách, 24 workshop
trong 3 phiên, chỉ theo hạng vé). KHÔNG truyền `--cau-hinh` / `--kich-ban` thì đầu ra y hệt
bản trước khi có workspace (trường học).

Đầu ra là MỘT tệp: `SO_NHAP_CLB.xlsx` — Sổ nhập CLB, đúng tệp phần mềm nhận
(xem `so_nhap.py` ở gốc kho mã). `soat` đọc được cả sổ lẫn bộ ba CSV cũ.

NGUYÊN TẮC: sổ luôn đi ra từ MỘT nguồn trong bộ nhớ, và mọi phép soát chạy
TRƯỚC khi ghi. Sai một điều là không ghi gì — sinh ra một bộ dữ liệu hỏng
còn tệ hơn không sinh gì, vì nó trông y như thật.

Đoạn mã này KHÔNG tự sửa dữ liệu sai. Sửa giúp là giấu mất chỗ sai.
"""

import argparse
import csv
import io
import json
import os
import random
import re
import sys
import unicodedata
import zipfile

# so_nhap.py (định nghĩa Sổ nhập CLB) nằm ở gốc kho mã; bản đóng gói (.zip)
# để một bản sao ngay cạnh script này — ưu tiên bản cạnh script.
_DAY = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(_DAY, "..", "..", "..", "..")))
sys.path.insert(0, _DAY)
import so_nhap  # noqa: E402
import nhan_ws  # noqa: E402  (đi kèm so_nhap.py; không phụ thuộc gì)

# Trần do chính phần mềm áp, không phải do đoạn mã này nghĩ ra.
# Xem `rbda_priority_pipeline.TRAN_NGUYEN_VONG_MOI_BUOI` / `TRAN_CLB_THI_MOI_BUOI`.
TRAN_NGUYEN_VONG_MOI_BUOI = 10   # = giới hạn câu hỏi Ranking của Microsoft Forms
TRAN_CLB_THI_MOI_BUOI = 5

# Tệp ghi ra.
TEN_SO = "SO_NHAP_CLB.xlsx"

# Bộ ba tệp CSV cũ — chỉ còn để `soat` đọc các bộ đã có.
TEN_TEP = {
    "clb": "01_danh_sach_CLB.csv",
    "thi": "02_chon_CLB_muon_thi.csv",
    "nv": "03_xep_hang_nguyen_vong.csv",
}

# Nhãn buổi phần mềm nhận ra được (còn nhận nhiều cách viết khác; đây là
# cách viết chuẩn nên dùng khi sinh mới).
BUOI_CHUAN = ["thu_2", "thu_3", "thu_4", "thu_5", "thu_6", "thu_7", "chu_nhat"]


# ---------------------------------------------------------------------------
# CẤU HÌNH WORKSPACE (--cau-hinh) — nhãn và luật của workspace
# ---------------------------------------------------------------------------
#
# Cùng khuôn với hàng 'config' của bảng workspace_settings trong app.db (xem
# `cau_hinh_ws.py` ở gốc kho mã). Đoạn mã này KHÔNG import cau_hinh_ws: skill đóng
# gói được chỉ có so_nhap.py, i18n_errors.py, nhan_ws.py. Nên phép chuẩn hoá dưới
# đây là bản chép gọn của `cau_hinh_ws.chuan_hoa`, và tests/test_skill_sinh_du_lieu.py
# so hai bản với nhau để chúng không lệch.

NGANH = ("school", "company", "event", "custom")
UU_TIEN = ("score", "tier", "score+tier")
CHE_DO_NHOM = ("reserve", "strict")
PHAM_VI_DIEM = ("per_slot", "per_person")

LUAT_MAC_DINH = {"max_choices": TRAN_NGUYEN_VONG_MOI_BUOI, "max_tests": TRAN_CLB_THI_MOI_BUOI,
                 "priority": "score", "tier_mode": "reserve", "score_scope": "per_slot",
                 "tiers": []}


def cau_hinh_mac_dinh():
    """Cấu hình của trường học: thiếu gì lấy nấy."""
    return {"name": "", "industry": "school", "labels": nhan_ws.sao_nhan_mac_dinh(),
            "rules": json.loads(json.dumps(LUAT_MAC_DINH))}


def chuan_hoa_cau_hinh(cfg):
    """(cấu hình đầy đủ, [lỗi]). Trộn `cfg` lên mặc định trường học rồi kiểm.

    Thiếu khoá = mặc định. Khai `vi` mà bỏ `en` thì `en` = `vi`. Có lỗi thì cấu hình trả về là None.
    """
    loi = []
    if not isinstance(cfg, dict):
        return None, ["cấu hình phải là một đối tượng JSON (dict)"]
    la = sorted(set(cfg) - {"name", "industry", "labels", "rules"})
    if la:
        loi.append("khoá cấu hình không hợp lệ: %s" % ", ".join(map(str, la)))
    for muc in ("labels", "rules"):
        if muc in cfg and not isinstance(cfg[muc], dict):
            loi.append("'%s' phải là một đối tượng JSON" % muc)
    if loi:
        return None, loi

    kq = cau_hinh_mac_dinh()
    ten = cfg.get("name", "")
    if not isinstance(ten, str):
        loi.append("name phải là chuỗi")
    else:
        kq["name"] = ten.strip()
    if cfg.get("industry", "school") not in NGANH:
        loi.append("industry phải là một trong %s" % list(NGANH))
    else:
        kq["industry"] = cfg.get("industry", "school")

    for dt, cap in (cfg.get("labels") or {}).items():
        if dt not in nhan_ws.DANH_TU:
            loi.append("danh từ không hợp lệ trong labels: %s (chỉ có %s)"
                       % (dt, list(nhan_ws.DANH_TU)))
            continue
        if not isinstance(cap, dict):
            loi.append("labels.%s phải là {'vi': ..., 'en': ...}" % dt)
            continue
        vi, en = cap.get("vi"), cap.get("en")
        if not isinstance(vi, str) or not vi.strip():
            loi.append("labels.%s.vi không được để trống" % dt)
            continue
        if en is not None and not isinstance(en, str):
            loi.append("labels.%s.en phải là chuỗi" % dt)
            continue
        vi, en = vi.strip(), (en or "").strip()
        if len(vi) > 60 or len(en) > 60:
            loi.append("labels.%s dài quá 60 ký tự" % dt)
            continue
        # Chữ mở đầu bằng = + - @ bị Excel hiểu là công thức (nhãn thành tiêu đề cột).
        if any(x[:1] in ("=", "+", "-", "@") for x in (vi, en)):
            loi.append("labels.%s không được bắt đầu bằng = + - @" % dt)
            continue
        kq["labels"][dt] = {"vi": vi, "en": en or vi}

    luat = cfg.get("rules") or {}
    la = sorted(set(luat) - set(LUAT_MAC_DINH))
    if la:
        loi.append("luật không hợp lệ: %s" % ", ".join(map(str, la)))
    for k, v in luat.items():
        if k in LUAT_MAC_DINH:
            kq["rules"][k] = v
    r = kq["rules"]

    def so_nguyen(v):
        return isinstance(v, int) and not isinstance(v, bool)

    if not so_nguyen(r["max_choices"]) or not 1 <= r["max_choices"] <= 20:
        loi.append("max_choices phải là số nguyên từ 1 đến 20, nhận %r" % (r["max_choices"],))
    if r["max_tests"] is not None and (not so_nguyen(r["max_tests"])
                                       or not 0 <= r["max_tests"] <= 20):
        loi.append("max_tests phải là số nguyên từ 0 đến 20 hoặc null (không giới hạn), nhận %r"
                   % (r["max_tests"],))
    for khoa, cho_phep in (("priority", UU_TIEN), ("tier_mode", CHE_DO_NHOM),
                           ("score_scope", PHAM_VI_DIEM)):
        if r[khoa] not in cho_phep:
            loi.append("%s phải là một trong %s, nhận %r" % (khoa, list(cho_phep), r[khoa]))
    t = r["tiers"]
    if not isinstance(t, list) or not all(isinstance(x, str) and x.strip() for x in t):
        loi.append("tiers phải là danh sách tên nhóm (chuỗi không rỗng)")
    else:
        r["tiers"] = [x.strip() for x in t]
        if len(r["tiers"]) > 50:
            loi.append("tiers có quá nhiều nhóm (tối đa 50)")
        khoa = {}
        for x in r["tiers"]:
            if len(x) > 60:
                loi.append("tên nhóm '%s…' dài quá 60 ký tự" % x[:20])
            k = khoa_nhom(x)
            if not k:
                loi.append("tên nhóm %r không có chữ nào" % x)
            elif k in khoa:
                loi.append("tiers có tên nhóm trùng nhau: %r và %r" % (khoa[k], x))
            khoa[k] = x
    return (None, loi) if loi else (kq, [])


def khoa_nhom(ten):
    """Khoá so khớp tên nhóm — bản chép của `rbda_priority_pipeline.khoa_ten_nhom`:
    bỏ dấu, hoa/thường, mọi dấu câu và khoảng trắng là một dấu tách.
    "Quản lý", "quan_ly" và "QUAN  LY" cùng một khoá."""
    s = unicodedata.normalize("NFD", str(ten or "").replace("đ", "d").replace("Đ", "D"))
    s = "".join(c for c in s if not unicodedata.combining(c)).casefold()
    return " ".join(re.sub(r"[\W_]+", " ", s).split())


def doc_cau_hinh(duong):
    """Đọc tệp --cau-hinh: hoặc đúng khuôn 'config', hoặc tệp mẫu của phần mềm
    ({"name": ..., "config": {...}}). Sai thì thoát với danh sách lỗi."""
    try:
        with io.open(duong, encoding="utf-8") as f:
            tho = json.load(f)
    except (OSError, ValueError) as e:
        raise SystemExit("Không đọc được --cau-hinh %s: %s" % (duong, e))
    if isinstance(tho, dict) and isinstance(tho.get("config"), dict) \
            and not ({"labels", "rules", "industry"} & set(tho)):
        tho = dict(tho["config"], **({"name": tho["name"]} if "name" in tho
                                     and "name" not in tho["config"] else {}))
    cfg, loi = chuan_hoa_cau_hinh(tho)
    if loi:
        raise SystemExit("--cau-hinh không hợp lệ:\n" + "\n".join("   ✗ " + e for e in loi))
    return cfg


def la_cau_hinh_truong_hoc(cfg):
    """Cấu hình có luật VÀ nhãn y hệt trường học mặc định? (tên workspace không tính)"""
    mac = cau_hinh_mac_dinh()
    return (cfg is None or (cfg["industry"] == "school" and cfg["labels"] == mac["labels"]
                            and cfg["rules"] == mac["rules"]))


def tran_nv(cfg):
    return cfg["rules"]["max_choices"] if cfg else TRAN_NGUYEN_VONG_MOI_BUOI


def tran_thi(cfg):
    """Số CLB dự thi tối đa mỗi buổi; None = không giới hạn."""
    return cfg["rules"]["max_tests"] if cfg else TRAN_CLB_THI_MOI_BUOI


def diem_theo_nguoi(cfg):
    """Một điểm cho cả người (thay vì điểm từng chỗ)? priority 'tier' thì không có điểm nào."""
    return bool(cfg) and cfg["rules"]["score_scope"] == "per_person" \
        and cfg["rules"]["priority"] != "tier"


def khong_dung_diem(cfg):
    return bool(cfg) and cfg["rules"]["priority"] == "tier"


def nhom_cung(cfg):
    """Nhóm xếp cứng (hạng nhóm đứng trước điểm, bỏ suất dự trữ)?"""
    return bool(cfg) and (cfg["rules"]["tier_mode"] == "strict"
                          or cfg["rules"]["priority"] == "tier")


# ---------------------------------------------------------------------------
# SOÁT — dùng chung cho cả sinh mới lẫn kiểm bộ đã có
# ---------------------------------------------------------------------------

def soat(clb, hs, cfg=None):
    """Trả về danh sách lỗi. Rỗng = hợp lệ.

    `clb`: [{club_id, name, capacity, reserve_capacity, reserve_group, buoi}]
    `hs` : [{student_id, name, reserve_group, nguyen_vong: {buoi: [club_id]},
             diem: {club_id: float|str}, diem_ca_nhan: float|str (tuỳ chọn)}]
    `cfg`: cấu hình workspace đã chuẩn hoá (`chuan_hoa_cau_hinh`); None = trường học.
           Đổi: trần nguyện vọng / thi, điểm theo người hay theo chỗ, nhóm xếp cứng.
    """
    loi = []
    t_nv, t_thi = tran_nv(cfg), tran_thi(cfg)
    theo_nguoi = diem_theo_nguoi(cfg)
    hang = {khoa_nhom(g) for g in cfg["rules"]["tiers"]} if nhom_cung(cfg) else None

    ma = [c["club_id"] for c in clb]
    if len(ma) != len(set(ma)):
        loi.append("có mã câu lạc bộ bị trùng trong danh sách")
    tap_ma = set(ma)
    buoi_cua = {c["club_id"]: (c.get("buoi") or "") for c in clb}

    for c in clb:
        if not c["club_id"]:
            loi.append("có câu lạc bộ thiếu mã")
        try:
            suc = int(c["capacity"])
        except (TypeError, ValueError):
            loi.append("%s: sức chứa không phải số" % c["club_id"])
            continue
        if suc <= 0:
            loi.append("%s: sức chứa phải lớn hơn 0" % c["club_id"])
        du = int(c.get("reserve_capacity") or 0)
        if du < 0:
            loi.append("%s: chỉ tiêu dự trữ âm" % c["club_id"])
        if du > suc:
            loi.append("%s: chỉ tiêu dự trữ (%d) lớn hơn sức chứa (%d)"
                       % (c["club_id"], du, suc))
        if du > 0 and not (c.get("reserve_group") or "").strip():
            loi.append("%s: có chỉ tiêu dự trữ nhưng không ghi nhóm dự trữ"
                       % c["club_id"])

    # Khai buổi thì phải khai cho MỌI câu lạc bộ. Khai một nửa thì những câu
    # lạc bộ bỏ trống bị gom chung một buổi, và học sinh chỉ vào được một
    # trong số chúng — phần mềm cảnh báo đúng chuyện này.
    co_buoi = [c["club_id"] for c in clb if (c.get("buoi") or "").strip()]
    if co_buoi and len(co_buoi) != len(clb):
        loi.append("chỉ %d/%d câu lạc bộ khai buổi — khai thì phải khai hết, "
                   "hoặc bỏ trống hết" % (len(co_buoi), len(clb)))

    ma_hs = [h["student_id"] for h in hs]
    if len(ma_hs) != len(set(ma_hs)):
        loi.append("có mã học sinh bị trùng")

    for h in hs:
        sid = h["student_id"]
        if not sid:
            loi.append("có học sinh thiếu mã")
            continue

        for b, ds in (h.get("nguyen_vong") or {}).items():
            if len(ds) != len(set(ds)):
                loi.append("%s · %s: nguyện vọng trùng nhau" % (sid, b))
            if len(ds) > t_nv:
                loi.append("%s · %s: %d nguyện vọng, vượt trần %d mỗi buổi"
                           % (sid, b, len(ds), t_nv))
            for cid in ds:
                if cid not in tap_ma:
                    loi.append("%s · %s: mã '%s' không có trong danh sách câu lạc bộ"
                               % (sid, b, cid))
                elif buoi_cua[cid] != b:
                    loi.append("%s: %s nằm ở cột buổi %s nhưng sinh hoạt %s"
                               % (sid, cid, b, buoi_cua[cid] or "(không khai)"))

        theo_buoi = {}
        for cid in (h.get("diem") or {}):
            if cid not in tap_ma:
                loi.append("%s: chấm điểm cho mã '%s' không có thật" % (sid, cid))
                continue
            b = buoi_cua[cid]
            theo_buoi.setdefault(b, []).append(cid)
            # Diem cho mot CLB em khong xep nguyen vong la diem khong dung
            # toi — va gan nhu chac chan la go lech cot.
            if cid not in (h.get("nguyen_vong") or {}).get(b, []):
                loi.append("%s: dự thi %s nhưng không xếp nguyện vọng câu lạc bộ đó"
                           % (sid, cid))
        for b, ds in theo_buoi.items():
            if t_thi is not None and len(ds) > t_thi:
                loi.append("%s · %s: dự thi %d câu lạc bộ, vượt trần %d mỗi buổi"
                           % (sid, b, len(ds), t_thi))

        if cfg is not None:
            # Luật workspace. Điểm theo NGƯỜI thì không có điểm từng chỗ (phần mềm đọc cột điểm
            # chung, bỏ cột "Điểm k"); nhóm xếp cứng thì ai có nguyện vọng cũng phải mang một
            # nhóm có trong luật, không thì bị xếp sau cùng mà không ai báo.
            if theo_nguoi and h.get("diem"):
                loi.append("%s: workspace chấm điểm theo người, không có điểm từng chỗ" % sid)
            dn = h.get("diem_ca_nhan")
            if dn not in (None, ""):
                if not theo_nguoi:
                    loi.append("%s: có điểm theo người nhưng workspace không chấm điểm theo người"
                               % sid)
                else:
                    try:
                        if float(str(dn).replace(",", ".")) < 0:
                            raise ValueError
                    except ValueError:
                        loi.append("%s: điểm theo người %r không phải số không âm" % (sid, dn))
            if hang is not None and any((h.get("nguyen_vong") or {}).values()) \
                    and khoa_nhom(h.get("reserve_group")) not in hang:
                loi.append("%s: nhóm %r không có trong rules.tiers — sẽ bị xếp sau cùng"
                           % (sid, h.get("reserve_group") or ""))

    # Canh bao muc do "khong hong nhung nen biet" — van tra ve de nguoi dung
    # thay, nhung khong chan viec ghi.
    return loi


def canh_bao_men(clb, hs, cfg=None):
    """Những điều không sai nhưng nên biết trước khi chạy."""
    ra = []
    if khong_dung_diem(cfg) and any(h.get("diem") or h.get("diem_ca_nhan") for h in hs):
        ra.append("workspace chỉ xếp theo nhóm (priority = tier): mọi điểm trong sổ bị bỏ qua")
    if diem_theo_nguoi(cfg):
        thieu = [h["student_id"] for h in hs
                 if any((h.get("nguyen_vong") or {}).values())
                 and h.get("diem_ca_nhan") in (None, "")]
        if thieu:
            ra.append("%d em chưa có điểm theo người — chỉ được xét theo số bốc thăm, sau người "
                      "đã có điểm (ví dụ %s)" % (len(thieu), ", ".join(thieu[:3])))

    # Hai phia phai chuan hoa nhan buoi GIONG NHAU. Truong mot buoi thi cau
    # lac bo mang nhan rong con nguyen vong cung mang nhan rong; doi mot phia
    # thanh "__mac_dinh__" la hai ben khong con gap nhau, va bang canh bao noi
    # "0 em / 69 cho" — mot cau vo nghia, va vo nghia theo kieu nghe rat that.
    def nhan(b):
        return b or "__mac_dinh__"

    tong_cho = {}
    for c in clb:
        b = nhan(c.get("buoi"))
        tong_cho[b] = tong_cho.get(b, 0) + int(c["capacity"])
    muon = {}
    for h in hs:
        for b, ds in (h.get("nguyen_vong") or {}).items():
            if ds:
                muon[nhan(b)] = muon.get(nhan(b), 0) + 1
    for b in sorted(set(tong_cho) | set(muon)):
        cho, em = tong_cho.get(b, 0), muon.get(b, 0)
        if cho and em / cho > 3:
            ra.append("buổi %s chọi %.1f lần (%d em / %d chỗ) — sẽ có nhiều "
                      "em trượt buổi đó" % (b, em / cho, em, cho))
        if cho and em < cho * 0.5:
            ra.append("buổi %s thừa chỗ (%d em / %d chỗ)" % (b, em, cho))
    khong_nv = [h["student_id"] for h in hs
                if not any((h.get("nguyen_vong") or {}).values())]
    if khong_nv:
        ra.append("%d em không khai nguyện vọng nào cả tuần — các em đó chắc "
                  "chắn trắng tay" % len(khong_nv))
    return ra


# ---------------------------------------------------------------------------
# GHI
# ---------------------------------------------------------------------------

def thanh_so(clb, hs):
    """(clb, hs) của skill -> (clubs, students) cho `so_nhap.ghi_so_nhap`.

    Nguyện vọng các buổi nối thành MỘT danh sách theo thứ tự buổi: sổ nhập
    không chia cột theo buổi, phần mềm tự chia theo buổi của từng CLB.
    Điểm đặt ngay cạnh nguyện vọng của CLB đó.
    """
    ds_buoi = []
    for c in clb:                      # giu thu tu xuat hien, khong sap lai
        b = c.get("buoi") or ""
        if b not in ds_buoi:
            ds_buoi.append(b)
    clubs = [{
        "club_id": c["club_id"], "name": c.get("name") or c["club_id"],
        "capacity": int(c["capacity"]),
        "reserve_capacity": int(c.get("reserve_capacity") or 0),
        "reserve_group": c.get("reserve_group") or "", "buoi": c.get("buoi") or "",
    } for c in clb]
    students = []
    for h in hs:
        nv = h.get("nguyen_vong") or {}
        diem = h.get("diem") or {}
        thu_tu = [cid for b in ds_buoi + [b for b in nv if b not in ds_buoi]
                  for cid in nv.get(b, [])]
        sv = {
            "student_id": h["student_id"], "name": h.get("name") or "",
            "reserve_group": h.get("reserve_group") or "",
            "nv": [{"club_id": cid, "thi": cid in diem, "diem": diem.get(cid, "")}
                   for cid in thu_tu],
        }
        if h.get("diem_ca_nhan") not in (None, ""):
            sv["diem_ca_nhan"] = h["diem_ca_nhan"]      # workspace chấm điểm theo NGƯỜI
        students.append(sv)
    return clubs, students


def ghi_bo(thu_muc, clb, hs, cfg=None, ten_tep=TEN_SO, co_dinh=False):
    """Ghi Sổ nhập CLB. GỌI SAU KHI soát() đã trả về rỗng. Trả [đường dẫn].

    `cfg`: cấu hình workspace (nhãn → tên sheet, tiêu đề cột; trần → số cột NV; điểm theo người
    → MỘT cột điểm). None = đúng sổ trường học như trước khi có workspace.
    `co_dinh`: ghi xlsx TẤT ĐỊNH (xem `co_dinh_xlsx`)."""
    os.makedirs(thu_muc, exist_ok=True)
    p = os.path.join(thu_muc, ten_tep)
    clubs, students = thanh_so(clb, hs)
    if cfg is None:
        so_nhap.ghi_so_nhap(p, clubs, students)
    else:
        so_nhap.ghi_so_nhap(p, clubs, students, cfg=cfg)
    if co_dinh:
        co_dinh_xlsx(p)
    return [p]


_GIO_CO_DINH = "2026-01-01T00:00:00Z"


def co_dinh_xlsx(duong):
    """Viết lại .xlsx sao cho CÙNG DỮ LIỆU thì CÙNG TỪNG BYTE.

    openpyxl ghi giờ hiện tại vào docProps/core.xml (created/modified) và vào giờ của từng mục zip,
    nên hai lần sinh cùng một seed vẫn khác nhau vài byte. Với bộ dữ liệu commit vào kho, mỗi lần
    sinh lại là một diff vô nghĩa. Hàm này chỉ đổi những chỗ giờ đó; nội dung không đổi."""
    with zipfile.ZipFile(duong) as z:
        muc = [(i.filename, z.read(i.filename)) for i in z.infolist()]
    tam = duong + ".tmp"
    with zipfile.ZipFile(tam, "w", zipfile.ZIP_DEFLATED) as z:
        for ten, nd in muc:
            if ten == "docProps/core.xml":
                nd = re.sub(rb"(<dcterms:(?:created|modified)[^>]*>)[^<]*",
                            rb"\g<1>" + _GIO_CO_DINH.encode(), nd)
            info = zipfile.ZipInfo(ten, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, nd)
    os.replace(tam, duong)


# ---------------------------------------------------------------------------
# ĐỌC LẠI một bộ đã có (cho chế độ `soat`)
# ---------------------------------------------------------------------------

def doc_so(duong, cfg=None):
    """Đọc một Sổ nhập CLB về đúng dạng (clb, hs) mà `soat` dùng.

    `cfg`: cấu hình workspace của sổ (tên sheet và tiêu đề cột theo nhãn). Sổ của workspace
    khác trường học mà không truyền cấu hình thì không nhận ra được là sổ."""
    import openpyxl

    wb = openpyxl.load_workbook(duong, read_only=True, data_only=True)
    try:
        if not so_nhap.la_so_nhap(wb.sheetnames, cfg):
            raise SystemExit("%s không phải Sổ nhập CLB%s" % (duong, "" if cfg else
                             " (sổ của workspace khác trường học thì thêm --cau-hinh config.json)"))
        du = so_nhap.doc_so_nhap(wb, cfg=cfg)
    finally:
        wb.close()
    if du["loi"]:
        import i18n_errors
        raise SystemExit("Sổ nhập có lỗi:\n" + "\n".join(
            "   ✗ " + d for d in i18n_errors.format_all(du["loi"])))
    clb = [{k: c[k] for k in ("club_id", "name", "capacity", "reserve_capacity",
                              "reserve_group", "buoi")} for c in du["clubs"]]
    buoi_cua = {c["club_id"]: c["buoi"] for c in clb}
    hs = []
    for s in du["students"]:
        nv, diem = {}, {}
        for x in s["nv"]:
            nv.setdefault(buoi_cua.get(x["club_id"], ""), []).append(x["club_id"])
            if x["thi"]:
                diem[x["club_id"]] = x["diem"]
        em = {"student_id": s["student_id"], "name": s["name"],
              "reserve_group": s["reserve_group"] or "", "nguyen_vong": nv, "diem": diem}
        dn = so_nhap.diem_cua_nguoi(s) if cfg else None
        if dn is not None:
            em["diem_ca_nhan"] = dn
        hs.append(em)
    return clb, hs


def doc_bo(thu_muc, cfg=None):
    """Đọc Sổ nhập CLB (tệp .xlsx, hoặc thư mục có SO_NHAP_CLB.xlsx), hoặc
    bộ ba CSV cũ trong thư mục."""
    if thu_muc.lower().endswith((".xlsx", ".xlsm")):
        return doc_so(thu_muc, cfg)
    if os.path.exists(os.path.join(thu_muc, TEN_SO)):
        return doc_so(os.path.join(thu_muc, TEN_SO), cfg)

    def doc(ten):
        p = os.path.join(thu_muc, ten)
        if not os.path.exists(p):
            raise SystemExit("Không thấy %s" % p)
        with io.open(p, encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))

    clb = []
    for r in doc(TEN_TEP["clb"]):
        clb.append({
            "club_id": (r.get("club_id") or "").strip(),
            "name": (r.get("name") or "").strip(),
            "capacity": (r.get("capacity") or "0").strip(),
            "reserve_capacity": (r.get("reserve_capacity") or "0").strip() or 0,
            "reserve_group": (r.get("reserve_group") or "").strip(),
            "buoi": (r.get("buoi") or "").strip(),
        })

    hs = {}
    for r in doc(TEN_TEP["nv"]):
        sid = (r.get("student_id") or "").strip()
        em = hs.setdefault(sid, {"student_id": sid,
                                 "name": (r.get("name") or "").strip(),
                                 "reserve_group": (r.get("reserve_group") or "").strip(),
                                 "nguyen_vong": {}, "diem": {}})
        for k, v in r.items():
            if not k or not v or "_pref_" not in k:
                continue
            b = k.rsplit("_pref_", 1)[0]
            em["nguyen_vong"].setdefault(b, []).append(v.strip())

    for r in doc(TEN_TEP["thi"]):
        sid = (r.get("student_id") or "").strip()
        em = hs.setdefault(sid, {"student_id": sid, "name": "", "reserve_group": "",
                                 "nguyen_vong": {}, "diem": {}})
        for k, v in r.items():
            if k and k.startswith("test_club_") and v:
                so = k[len("test_club_"):]
                em["diem"][v.strip()] = (r.get("score_" + so) or "").strip()

    return clb, list(hs.values())


# ---------------------------------------------------------------------------
# SINH NGẪU NHIÊN nhưng HỢP LỆ
# ---------------------------------------------------------------------------

_HO = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Vũ", "Đỗ", "Bùi", "Ngô",
       "Dương", "Lý", "Hồ", "Đặng", "Phan", "Trịnh", "Mai", "Chu", "Tạ"]
_DEM = ["Văn", "Thị", "Minh", "Gia", "Bảo", "Khánh", "Hoài", "Quốc", "Thanh", "Anh"]
_TEN = ["An", "Bình", "Chi", "Dũng", "Giang", "Hà", "Huy", "Khanh", "Lan",
        "Mai", "Nam", "Ngân", "Nhi", "Phúc", "Quân", "Sương", "Tuấn", "Uyên",
        "Việt", "Xuân", "Yến", "Linh", "Thảo", "Vy"]

_CHU_DE = [
    ("clb_bongro", "CLB Bóng rổ"), ("clb_bongda", "CLB Bóng đá"),
    ("clb_covua", "CLB Cờ vua"), ("clb_vanhoc", "CLB Văn học"),
    ("clb_tinhoc", "CLB Tin học"), ("clb_robotics", "CLB Robotics"),
    ("clb_mythuat", "CLB Mỹ thuật"), ("clb_amnhac", "CLB Âm nhạc"),
    ("clb_nauan", "CLB Nấu ăn"), ("clb_lamvuon", "CLB Làm vườn"),
    ("clb_tienganh", "CLB Tiếng Anh"), ("clb_khoahoc", "CLB Khoa học"),
    ("clb_nhiepanh", "CLB Nhiếp ảnh"), ("clb_khieuvu", "CLB Khiêu vũ"),
    ("clb_tranhbien", "CLB Tranh biện"), ("clb_tinhnguyen", "CLB Tình nguyện"),
    ("clb_dangian", "CLB Trò chơi dân gian"), ("clb_thuvien", "CLB Thư viện"),
    ("clb_bcs", "CLB Báo chí"), ("clb_coking", "CLB Cờ tướng"),
]


def sinh_ngau_nhien(n_hs, ds_buoi, clb_moi_buoi, seed, do_choi=1.15,
                    ti_le_du_tru=0.35, ti_le_co_thi=0.34):
    """Một trường ngẫu nhiên nhưng luôn hợp lệ. Tất định theo `seed`.

    `do_choi` — tổng chỗ so với số học sinh. 1.15 nghĩa là chỗ nhiều hơn nhu
    cầu 15%, đủ chật để kết quả có ý nghĩa, đủ rộng để không quá nửa trường
    trắng tay.
    """
    rnd = random.Random(seed)
    if clb_moi_buoi * len(ds_buoi) > len(_CHU_DE):
        raise SystemExit("Chỉ có %d chủ đề câu lạc bộ sẵn, không đủ cho %d câu lạc bộ"
                         % (len(_CHU_DE), clb_moi_buoi * len(ds_buoi)))

    chu_de = _CHU_DE[:]
    rnd.shuffle(chu_de)
    nhom_du_tru = ["chinh_sach", "khoi_10"]

    clb, k = [], 0
    for b in ds_buoi:
        # Tong cho moi buoi ~ n_hs * do_choi / so buoi, chia deu cho cac CLB
        cho_buoi = max(clb_moi_buoi, int(round(n_hs * do_choi / len(ds_buoi))))
        phan = [cho_buoi // clb_moi_buoi] * clb_moi_buoi
        for i in range(cho_buoi - sum(phan)):
            phan[i] += 1
        for i in range(clb_moi_buoi):
            cid, ten = chu_de[k]; k += 1
            suc = max(2, phan[i])
            co_du = rnd.random() < ti_le_du_tru
            clb.append({
                "club_id": cid, "name": ten, "capacity": suc,
                "reserve_capacity": max(1, int(suc * 0.2)) if co_du else 0,
                "reserve_group": rnd.choice(nhom_du_tru) if co_du else "",
                "buoi": b,
            })

    theo_buoi = {}
    for c in clb:
        theo_buoi.setdefault(c["buoi"], []).append(c["club_id"])
    co_thi = {c["club_id"] for c in clb if rnd.random() < ti_le_co_thi}

    # CHI GAN NHOM MA CO CAU LAC BO THAT SU DANH SUAT CHO.
    #
    # Gan bua tu bang `nhom_du_tru` thi gap truong hop khong cau lac bo nao
    # dat suat cho "khoi_10" — luc do nhung em mang nhan do co mot cai nhan
    # khong dem lai gi o bat ky dau. Phan mem goi do la "nhom mo coi" va
    # canh bao muc CAO, dung. Do duoc: truong 3 cau lac bo, 40 em -> 9 em
    # mang nhan mo coi va 2 canh bao khi nhap.
    nhom_co_that = sorted({c["reserve_group"] for c in clb if c["reserve_group"]})

    hs = []
    for i in range(1, n_hs + 1):
        sid = "HS%03d" % i
        ten = "%s %s %s" % (rnd.choice(_HO), rnd.choice(_DEM), rnd.choice(_TEN))
        nhom = (rnd.choice(nhom_co_that)
                if nhom_co_that and rnd.random() < 0.22 else "")
        nv, diem = {}, {}
        for b, ds in theo_buoi.items():
            # Mot so em bo trong ca mot buoi — ngay do em ban. Day la du lieu
            # HOP LE, khong phai thieu sot.
            if rnd.random() < 0.12:
                nv[b] = []
                continue
            k_nv = min(len(ds), rnd.randint(1, min(3, len(ds))))
            chon = rnd.sample(ds, k_nv)
            nv[b] = chon
            # Chi cham diem cho CLB em CO khai nguyen vong va CLB do co thi
            for cid in chon:
                if cid in co_thi and rnd.random() < 0.8:
                    if len([c for c in diem if c in theo_buoi[b]]) < TRAN_CLB_THI_MOI_BUOI:
                        # Dau phay thap phan — dung cach Excel ban tieng Viet luu
                        diem[cid] = "%.1f" % rnd.uniform(4.0, 10.0).__round__(1)
                        diem[cid] = diem[cid].replace(".", ",")

        # MOI EM PHAI KHAI IT NHAT MOT NGUYEN VONG CA TUAN.
        #
        # Bo trong MOT buoi la "ngay do em ban" — hop le. Bo trong MOI buoi
        # la "em khong dang ky gi ca", va phan mem canh bao dung: em do chac
        # chan trang tay, khong phai vi thua ai ma vi chua bao gio vao cuoc.
        # O truong mot buoi, xac suat 12% ay ap len ca "tuan", nen khong chan
        # thi cu 100 em lai co ~12 em nhu vay.
        if not any(nv.values()):
            b = rnd.choice(list(theo_buoi))
            nv[b] = [rnd.choice(theo_buoi[b])]

        hs.append({"student_id": sid, "name": ten, "reserve_group": nhom,
                   "nguyen_vong": nv, "diem": diem})

    # VA CHIEU NGUOC LAI: moi nhom co cau lac bo dat suat thi phai co NGUOI.
    #
    # Day la mat guong cua khoi tren. Mot cau lac bo giu 1 cho cho
    # "chinh_sach" ma ca truong khong em nao thuoc dien do thi cho ay khong
    # ai nhan duoc — phan mem canh bao `health_club_group_no_students`, dung.
    # Truong it hoc sinh moi gap: 20 em, moi em 22% co nhom, boc ra toan
    # "khoi_10" la chuyen binh thuong. Do duoc: 1 tren 90 cau hinh da thu.
    for g in nhom_co_that:
        if any(h["reserve_group"] == g for h in hs):
            continue
        # Uu tien em CHUA co nhom de khong cuop nhan cua nhom khac.
        chua = [h for h in hs if not h["reserve_group"]] or hs
        rnd.choice(chua)["reserve_group"] = g

    return clb, hs


# ---------------------------------------------------------------------------
# SINH THEO CẤU HÌNH WORKSPACE (--cau-hinh / --kich-ban)
# ---------------------------------------------------------------------------
#
# Một hàm RIÊNG, không đụng `sinh_ngau_nhien`: bộ dữ liệu trường học đã commit trong kho được
# trích dẫn trong tài liệu, nên đường mặc định phải ra đúng như cũ từng byte (có test canh).
# Khác trường học ở ba chỗ:
#   * chỗ ngồi tính theo số người THẬT SỰ khai nguyện vọng ở buổi đó (trường học chia tổng chỗ
#     cho các buổi vì mỗi em chỉ vào một hai CLB cả tuần; công ty và sự kiện thì mọi người đều
#     phải có một chỗ ở MỖI buổi), có hệ số "hot" khác nhau giữa các chỗ để có chỗ chật chỗ rộng;
#   * điểm: theo NGƯỜI (một con số), theo CHỖ (như trường học), hoặc không có (chỉ theo nhóm);
#   * nhóm: xếp cứng thì mỗi người mang đúng một nhóm trong `rules.tiers`, chia theo tỉ lệ.

_DU_AN_CONG_TY = [
    "Nền tảng thanh toán", "Ứng dụng di động", "Kho dữ liệu doanh nghiệp",
    "Chăm sóc khách hàng đa kênh", "Cổng thông tin đối tác", "Bảo mật và tuân thủ",
    "Trải nghiệm người dùng", "Tự động hoá kiểm thử", "Hạ tầng đám mây",
    "Phân tích kinh doanh", "Trợ lý ảo nội bộ", "Quản lý chuỗi cung ứng",
    "Tích hợp ERP", "Báo cáo quản trị", "Cổng tuyển dụng nội bộ", "Quản lý kho vận",
]
_WORKSHOP_SU_KIEN = [
    "Trí tuệ nhân tạo trong doanh nghiệp", "Khởi nghiệp tinh gọn", "Kể chuyện bằng dữ liệu",
    "An toàn thông tin cho đội nhóm", "Thiết kế trải nghiệm người dùng",
    "Xây dựng thương hiệu cá nhân", "Quản lý dự án linh hoạt", "Marketing nội dung",
    "Tài chính cho người khởi nghiệp", "Chuyển đổi số ngành bán lẻ", "Lãnh đạo từ xa",
    "Tự động hoá quy trình", "Đàm phán và thuyết phục", "Phân tích dữ liệu với Excel",
    "Làm ứng dụng không cần code", "Kinh tế tuần hoàn", "Quản trị rủi ro",
    "Podcast và video ngắn", "Thuyết trình tự tin", "Xây dựng cộng đồng",
    "Blockchain trong thực tế", "Bán hàng B2B", "Văn hoá doanh nghiệp",
    "Sức khoẻ tinh thần nơi làm việc", "Năng lượng xanh", "Nhập môn học máy",
    "Cân bằng công việc và cuộc sống", "Gọi vốn đầu tư",
    "Thương mại điện tử xuyên biên giới", "Quản lý thời gian",
]


def _ma_tu_ten(tien_to, ten):
    """'Nền tảng thanh toán' -> 'da_nentangthanhtoan' (chữ thường, không dấu, không cách)."""
    chu = re.sub(r"[^a-z0-9]+", "", so_nhap.khong_dau(ten))
    return "%s_%s" % (tien_to, chu[:28])


def _danh_sach_ten(nganh):
    """[(club_id, tên)] theo ngành của cấu hình."""
    if nganh == "company":
        return [(_ma_tu_ten("da", t), "Dự án " + t) for t in _DU_AN_CONG_TY]
    if nganh == "event":
        return [(_ma_tu_ten("ws", t), t) for t in _WORKSHOP_SU_KIEN]
    return _CHU_DE[:]


def ti_le_nhom_mac_dinh(n):
    """Tỉ lệ người trong từng nhóm, nhóm tốt nhất đứng đầu và NHỎ nhất (người ở hạng cao thì ít).
    3 nhóm: 10% / 30% / 60%. Số khác: 1 nhóm 100%; 2 nhóm 30/70; 4 nhóm 5/15/30/50; còn lại 1:2:4:8…"""
    co_san = {1: [1.0], 2: [0.3, 0.7], 3: [0.1, 0.3, 0.6], 4: [0.05, 0.15, 0.3, 0.5]}
    if n in co_san:
        return co_san[n]
    w = [2 ** i for i in range(n)]
    return [x / sum(w) for x in w]


def chia_theo_ti_le(n, ti_le):
    """Chia n người theo tỉ lệ, đúng TỔNG n (phần dư cho nhóm có phần lẻ lớn nhất)."""
    tong = float(sum(ti_le))
    tho = [n * x / tong for x in ti_le]
    dem = [int(x) for x in tho]
    con = n - sum(dem)
    for i in sorted(range(len(tho)), key=lambda i: (-(tho[i] - dem[i]), i))[:con]:
        dem[i] += 1
    return dem


def _chon_co_trong_so(rnd, ds, trong_so, k):
    """k phần tử không trùng, xác suất theo trọng số (Efraimidis–Spirakis). Tất định theo rnd."""
    khoa = {x: rnd.random() ** (1.0 / trong_so[x]) for x in ds}
    return sorted(ds, key=lambda x: -khoa[x])[:k]


def sinh_theo_cau_hinh(cfg, n_hs, ds_buoi, clb_moi_buoi, seed, do_choi=1.15, ten_clb=None,
                       tien_to_ma="HS", ti_le_bo_buoi=0.12, ti_le_nhom=None,
                       ti_le_du_tru=0.35, ti_le_co_thi=0.34):
    """Dữ liệu ngẫu nhiên nhưng HỢP LỆ theo cấu hình workspace `cfg`. Tất định theo `seed`.

    `do_choi`: tổng chỗ mỗi buổi so với số người khai nguyện vọng buổi đó (1.15 = nhiều hơn 15%).
    `ti_le_bo_buoi`: xác suất một người bỏ trống cả một buổi (bận). Công ty một buổi: 0.
    `ti_le_nhom`: tỉ lệ người theo từng nhóm trong `rules.tiers` (mặc định `ti_le_nhom_mac_dinh`).
    """
    rnd = random.Random(seed)
    r = cfg["rules"]
    cung, theo_nguoi = nhom_cung(cfg), diem_theo_nguoi(cfg)
    khong_diem = khong_dung_diem(cfg)
    if cung and not r["tiers"]:
        raise SystemExit("Luật xếp nhóm cứng (tier_mode = strict hay priority = tier) mà rules.tiers "
                         "rỗng — không có nhóm nào để gán cho ai.")
    t_nv, t_thi = r["max_choices"], r["max_tests"]

    chu_de = list(ten_clb) if ten_clb else _danh_sach_ten(cfg["industry"])
    if clb_moi_buoi * len(ds_buoi) > len(chu_de):
        raise SystemExit("Chỉ có %d tên sẵn, không đủ cho %d chỗ (%d × %d buổi)"
                         % (len(chu_de), clb_moi_buoi * len(ds_buoi), clb_moi_buoi, len(ds_buoi)))
    rnd.shuffle(chu_de)
    nhom_du_tru = ["chinh_sach", "khoi_10"]

    clb, k = [], 0
    for b in ds_buoi:
        tong = max(2 * clb_moi_buoi, int(round(n_hs * (1 - ti_le_bo_buoi) * do_choi)))
        w = [rnd.uniform(0.6, 1.4) for _ in range(clb_moi_buoi)]
        for i in range(clb_moi_buoi):
            cid, ten = chu_de[k]
            k += 1
            suc = max(2, int(round(tong * w[i] / sum(w))))
            co_du = (not cung) and rnd.random() < ti_le_du_tru
            clb.append({"club_id": cid, "name": ten, "capacity": suc,
                        "reserve_capacity": max(1, int(suc * 0.2)) if co_du else 0,
                        "reserve_group": rnd.choice(nhom_du_tru) if co_du else "",
                        "buoi": b})

    theo_buoi = {}
    for c in clb:
        theo_buoi.setdefault(c["buoi"], []).append(c["club_id"])
    do_hot = {c["club_id"]: rnd.uniform(0.5, 1.5) for c in clb}   # chỗ nào được chuộng hơn
    co_thi = {c["club_id"] for c in clb if rnd.random() < ti_le_co_thi}
    nhom_co_that = sorted({c["reserve_group"] for c in clb if c["reserve_group"]})

    nhom_cua = []
    if cung:
        dem = chia_theo_ti_le(n_hs, ti_le_nhom or ti_le_nhom_mac_dinh(len(r["tiers"])))
        nhom_cua = [g for g, c in zip(r["tiers"], dem) for _ in range(c)]
        rnd.shuffle(nhom_cua)

    hs = []
    for i in range(1, n_hs + 1):
        sid = "%s%03d" % (tien_to_ma, i)
        ten = "%s %s %s" % (rnd.choice(_HO), rnd.choice(_DEM), rnd.choice(_TEN))
        if cung:
            nhom = nhom_cua[i - 1]
        else:
            nhom = (rnd.choice(nhom_co_that)
                    if nhom_co_that and rnd.random() < 0.22 else "")
        nv, diem = {}, {}
        for b, ds in theo_buoi.items():
            if rnd.random() < ti_le_bo_buoi:
                nv[b] = []
                continue
            k_nv = min(len(ds), rnd.randint(1, min(3, len(ds), t_nv)))
            chon = _chon_co_trong_so(rnd, ds, do_hot, k_nv)
            nv[b] = chon
            if theo_nguoi or khong_diem:
                continue
            for cid in chon:
                if cid in co_thi and rnd.random() < 0.8:
                    if t_thi is None or len([c for c in diem if c in theo_buoi[b]]) < t_thi:
                        diem[cid] = ("%.1f" % rnd.uniform(4.0, 10.0)).replace(".", ",")
        if not any(nv.values()):
            b = rnd.choice(list(theo_buoi))
            nv[b] = [rnd.choice(theo_buoi[b])]
        em = {"student_id": sid, "name": ten, "reserve_group": nhom,
              "nguyen_vong": nv, "diem": diem}
        if theo_nguoi:
            # KPI: quanh 72, lệch chuẩn 13, kẹp trong 0–100, một số lẻ.
            em["diem_ca_nhan"] = round(min(100.0, max(0.0, rnd.gauss(72, 13))), 1)
        hs.append(em)

    if not cung:
        for g in nhom_co_that:
            if any(h["reserve_group"] == g for h in hs):
                continue
            chua = [h for h in hs if not h["reserve_group"]] or hs
            rnd.choice(chua)["reserve_group"] = g
    return clb, hs


KICH_BAN = {
    "company": {
        "mo_ta": "công ty: 300 nhân viên, 12 dự án, 1 đợt, KPI 0–100 theo người, Senior > Mid > Junior",
        "cau_hinh": {
            "name": "Công ty Cổ phần Ánh Dương (mô phỏng)", "industry": "company",
            "labels": {"person": {"vi": "Nhân viên", "en": "Employee"},
                       "slot": {"vi": "Dự án", "en": "Project"},
                       "session": {"vi": "Quý", "en": "Quarter"},
                       "group": {"vi": "Cấp bậc", "en": "Level"},
                       "score": {"vi": "KPI", "en": "KPI"}},
            "rules": {"max_choices": 3, "max_tests": 0, "priority": "score+tier",
                      "tier_mode": "strict", "score_scope": "per_person",
                      "tiers": ["Senior", "Mid", "Junior"]}},
        "hoc_sinh": 300, "buoi": "", "clb_moi_buoi": 12, "do_choi": 1.1,
        "tien_to_ma": "NV", "ti_le_bo_buoi": 0.0,
    },
    "event": {
        "mo_ta": "sự kiện: 800 khách, 24 workshop trong 3 phiên, chỉ theo hạng vé VIP > Member > Guest",
        "cau_hinh": {
            "name": "Hội nghị Chuyển đổi số 2026 (mô phỏng)", "industry": "event",
            "labels": {"person": {"vi": "Khách tham dự", "en": "Attendee"},
                       "slot": {"vi": "Workshop", "en": "Workshop"},
                       "session": {"vi": "Phiên", "en": "Track"},
                       "group": {"vi": "Hạng vé", "en": "Ticket"},
                       "score": {"vi": "Điểm", "en": "Score"}},
            "rules": {"max_choices": 2, "max_tests": 0, "priority": "tier",
                      "tier_mode": "strict", "score_scope": "per_slot",
                      "tiers": ["VIP", "Member", "Guest"]}},
        "hoc_sinh": 800, "buoi": "phien_1,phien_2,phien_3", "clb_moi_buoi": 8, "do_choi": 1.08,
        "tien_to_ma": "KH", "ti_le_bo_buoi": 0.04,
    },
}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _in_ket_qua(clb, hs, loi, canh_bao, cfg=None):
    if loi:
        print("KHÔNG HỢP LỆ — %d lỗi:" % len(loi), file=sys.stderr)
        for e in loi:
            print("   ✗", e, file=sys.stderr)
        return 1
    n_ca_nhan = sum(1 for h in hs if h.get("diem_ca_nhan") not in (None, ""))
    # Gọi các danh từ bằng nhãn của workspace (mặc định trường học cho ra đúng chữ cũ).
    nhan = cfg["labels"] if cfg else None

    def goi(dt):
        return nhan_ws.dang_chu(nhan, dt, "l", "vi")

    # Điểm từng chỗ chỉ nhắc khi workspace có loại điểm đó; điểm theo người thì nhắc điểm theo người.
    co_diem_cho = not (diem_theo_nguoi(cfg) or khong_dung_diem(cfg))
    print("Hợp lệ: %d %s · %d %s · %d %s%s%s"
          % (len(clb), goi("slot"), len({c.get("buoi") or "" for c in clb}), goi("session"),
             len(hs), goi("person"),
             " · %d ô %s" % (sum(len(h.get("diem") or {}) for h in hs), goi("score"))
             if co_diem_cho else "",
             " · %d %s theo %s" % (n_ca_nhan, goi("score"), goi("person")) if n_ca_nhan else ""))
    for w in canh_bao:
        print("   ⚠", w)
    return 0


def _them_tham_so_cau_hinh(p):
    p.add_argument("--cau-hinh", default=None, metavar="config.json",
                   help="cấu hình workspace (cùng khuôn hàng 'config' của workspace_settings): "
                        "nhãn, trần nguyện vọng / thi, điểm theo người hay theo chỗ, nhóm. "
                        "Bỏ trống = trường học như trước")


def main(argv=None):
    # Cua so lenh / ong dan tren Windows mac dinh la cp1252: in tieng Viet
    # se nem UnicodeEncodeError va script thoat voi ma 1.
    for _luong in (sys.stdout, sys.stderr):
        if hasattr(_luong, "reconfigure"):
            _luong.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="lenh", required=True)

    a = sub.add_parser("tao", help="dựng từ bản khai báo JSON")
    a.add_argument("--spec", required=True)
    a.add_argument("--ra", required=True)
    a.add_argument("--ten-tep", default=TEN_SO, help="tên tệp sổ ghi ra (mặc định %s)" % TEN_SO)
    _them_tham_so_cau_hinh(a)

    b = sub.add_parser("ngau", help="dựng một trường ngẫu nhiên nhưng hợp lệ")
    b.add_argument("--ra", required=True)
    b.add_argument("--hoc-sinh", type=int, default=None, help="số người (mặc định 120)")
    b.add_argument("--buoi", default=None, help="vd thu_2,thu_4,thu_6 — bỏ trống = một buổi")
    b.add_argument("--clb-moi-buoi", type=int, default=None, help="số chỗ mỗi buổi (mặc định 3)")
    b.add_argument("--seed", type=int, default=42)
    b.add_argument("--do-choi", type=float, default=None, help="mặc định 1.15")
    b.add_argument("--ten-tep", default=TEN_SO, help="tên tệp sổ ghi ra (mặc định %s)" % TEN_SO)
    b.add_argument("--kich-ban", choices=sorted(KICH_BAN), default=None,
                   help="dựng sẵn: " + "; ".join("%s = %s" % (k, v["mo_ta"])
                                                for k, v in sorted(KICH_BAN.items()))
                        + ". Ghi thêm config.json cạnh sổ. Các tuỳ chọn khác vẫn ghi đè được")
    _them_tham_so_cau_hinh(b)

    c = sub.add_parser("soat", help="soát một sổ nhập (hoặc bộ ba CSV cũ), không sửa gì")
    c.add_argument("thu_muc", help="tệp SO_NHAP_CLB.xlsx, hoặc thư mục chứa nó / bộ ba CSV")
    _them_tham_so_cau_hinh(c)

    ns = p.parse_args(argv)
    cfg = doc_cau_hinh(ns.cau_hinh) if ns.cau_hinh else None

    if ns.lenh == "soat":
        clb, hs = doc_bo(ns.thu_muc, cfg)
        return _in_ket_qua(clb, hs, soat(clb, hs, cfg), canh_bao_men(clb, hs, cfg), cfg)

    kb = None
    if ns.lenh == "tao":
        with io.open(ns.spec, encoding="utf-8") as f:
            spec = json.load(f)
        clb, hs = spec["cau_lac_bo"], spec["hoc_sinh"]
    else:
        kb = KICH_BAN[ns.kich_ban] if ns.kich_ban else None
        if kb and not ns.cau_hinh:
            cfg, _ = chuan_hoa_cau_hinh(kb["cau_hinh"])
        kb = kb or {}

        def chon(gia_tri, khoa, mac_dinh):
            return gia_tri if gia_tri is not None else kb.get(khoa, mac_dinh)

        n_hs = chon(ns.hoc_sinh, "hoc_sinh", 120)
        chuoi_buoi = chon(ns.buoi, "buoi", "")
        clb_moi_buoi = chon(ns.clb_moi_buoi, "clb_moi_buoi", 3)
        do_choi = chon(ns.do_choi, "do_choi", 1.15)
        ds_buoi = [x.strip() for x in chuoi_buoi.split(",") if x.strip()] or [""]
        la = [b for b in ds_buoi if b and b not in BUOI_CHUAN]
        if la and not kb:
            print("Nhãn buổi lạ: %s (nên dùng: %s)" % (", ".join(la),
                  ", ".join(BUOI_CHUAN)), file=sys.stderr)
        if la_cau_hinh_truong_hoc(cfg) and not ns.kich_ban:
            # Trường học (hoặc cấu hình y hệt trường học): đúng bộ sinh cũ, từng byte.
            clb, hs = sinh_ngau_nhien(n_hs, ds_buoi, clb_moi_buoi, ns.seed, do_choi)
        else:
            clb, hs = sinh_theo_cau_hinh(
                cfg, n_hs, ds_buoi, clb_moi_buoi, ns.seed, do_choi,
                tien_to_ma=kb.get("tien_to_ma", "HS"),
                ti_le_bo_buoi=kb.get("ti_le_bo_buoi", 0.12))

    loi = soat(clb, hs, cfg)
    ma = _in_ket_qua(clb, hs, loi, canh_bao_men(clb, hs, cfg), cfg)
    if ma:
        print("\nKhông ghi tệp nào.", file=sys.stderr)
        return ma
    # Có cấu hình thì ghi xlsx TẤT ĐỊNH (cùng seed -> cùng từng byte); không thì như trước.
    for d in ghi_bo(ns.ra, clb, hs, cfg, ns.ten_tep, co_dinh=cfg is not None):
        print("   →", d)
    if ns.lenh == "ngau" and ns.kich_ban:
        dich = os.path.join(ns.ra, "config.json")
        with io.open(dich, "w", encoding="utf-8", newline="\n") as f:
            json.dump(cfg, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("   →", dich)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
