"""
nhan_ws.py
==========
Từ vựng của workspace: điền nhãn (Học sinh / Câu lạc bộ / Buổi / Nhóm ưu tiên /
Điểm, hay "Nhân viên / Dự án / …") vào câu chữ có chỗ giữ `{person}`, `{slot}`…

KHÔNG phụ thuộc gì (không import cau_hinh_ws, không import rbda_priority_pipeline)
vì i18n_errors.py — mà rbda_priority_pipeline.py import — cũng dùng nó. Bản đối
xứng ở phía giao diện là `nounText` trong i18n.js; hai bản PHẢI cho cùng kết quả
(tests/test_ws_nhan.py so từng ca).

Cú pháp chỗ giữ:  {danh_tu}  hoặc  {danh_tu_<cờ>}  với danh_tu thuộc DANH_TU
và <cờ> là một hay nhiều chữ trong "lpsacuv", ví dụ {slot_sl}:
    l  chữ thường                   {person_l}  -> "học sinh"
    p  số nhiều (chỉ tiếng Anh)     {person_p}  -> "Students"
    s  dạng viết tắt                {slot_s}    -> "CLB" (chỉ khi nhãn đúng là
                                                  "Câu lạc bộ"; nhãn khác không
                                                  có dạng viết tắt nên giữ nguyên)
    a  kèm mạo từ a/an (chỉ tiếng Anh)  {slot_la} -> "a club", "an employee"
    c  viết hoa chữ đầu của kết quả     {person_lac} -> "A student"
    u  VIẾT HOA TOÀN BỘ                 {slot_u}    -> "CÂU LẠC BỘ" (tiêu đề in hoa)
    v  luôn lấy nhãn TIẾNG VIỆT         {score_v}   -> "Điểm" (cả trong câu tiếng Anh)
       — dùng khi câu nhắc đến chữ có thật trên một tệp tiếng Việt (tiêu đề cột, tên
       sheet của Sổ nhập), vì tệp luôn viết bằng nhãn `vi`.
Cờ ghép được ({slot_sl}), áp theo thứ tự s -> l -> p -> a -> c -> u. Chữ viết tắt (toàn
chữ HOA, như "CLB", "HR") không bị hạ thường.

Vì sao có cờ `s`: tiếng Việt của trường học viết "CLB" ở rất nhiều chỗ, nhưng nhãn
chuẩn là "Câu lạc bộ". Không có dạng viết tắt thì chữ hiện lên màn hình đổi đi
so với trước khi có workspace — và quy tắc của dự án là với mặc định trường học
mọi chuỗi phải GIỐNG HỆT.
"""

from __future__ import annotations

import copy
import re

DANH_TU = ("person", "slot", "session", "group", "score")

# Nhãn MẶC ĐỊNH của trường học — nguồn duy nhất; cau_hinh_ws.py lấy từ đây.
NHAN_MAC_DINH = {
    "person": {"vi": "Học sinh", "en": "Student"},
    "slot": {"vi": "Câu lạc bộ", "en": "Club"},
    "session": {"vi": "Buổi", "en": "Session"},
    "group": {"vi": "Nhóm ưu tiên", "en": "Priority group"},
    "score": {"vi": "Điểm", "en": "Score"},
}

# Dạng viết tắt đã quen dùng (vi). Chỉ áp cho ĐÚNG nhãn này.
_VIET_TAT = {("slot", "Câu lạc bộ"): "CLB"}

# Bảy TỪ CỦA TRƯỜNG HỌC không phải danh từ nghiệp vụ nhưng cũng sai chỗ ở công ty hay sự kiện:
# "em" (gọi học sinh), "giáo viên", "Nhà trường", "trường", "tuần", "thời khoá biểu". Trường học mặc định (nhãn `person`
# vẫn là "Học sinh") giữ ĐÚNG từ cũ — mọi chuỗi mặc định giống hệt trước khi có chỗ giữ này —
# còn workspace khác nhận từ trung tính: "em" -> nhãn người (chữ thường), "giáo viên" ->
# "người" ("người phụ trách", "người chấm KPI"), "Nhà trường" -> "Bộ phận phụ trách".
# Đối xứng ở phía giao diện: TU_TRUONG_HOC trong i18n.js.
TU_TRUONG_HOC = {
    # từ: (vi trường học, vi khác, en trường học, en khác); None = lấy nhãn `person` chữ thường.
    # Từ "khác" được phép chứa chỗ giữ danh từ (vd. {session_l}); nó được điền tiếp một lượt.
    "em": ("em", None, None, None),
    "gv": ("giáo viên", "người", "teachers", "staff"),
    "nt": ("Nhà trường", "Bộ phận phụ trách", "The school", "The organiser"),
    "truong": ("trường", "đơn vị", "school", "organisation"),
    "tuan": ("tuần", "đợt xếp", "week", "round"),
    "tkb": ("Thời khoá biểu", "Lịch xếp", "Timetable", "Schedule"),
    "tkbt": ("Thời khoá biểu tuần", "Lịch xếp theo {session_l}",
             "The week each {person_l} gets", "The {session_l} schedule each {person_l} gets"),
}

_RE_CHO_GIU = re.compile(
    r"\{(?:(person|slot|session|group|score)(?:_([lpsacuv]+))?|(em|gv|nt|truong|tuan|tkb|tkbt)(_[cu])?)\}")


def la_truong_hoc(nhan: dict | None) -> bool:
    """Nhãn người còn là "Học sinh" mặc định? Từ của trường học chỉ dùng khi đúng vậy."""
    return nhan_ngon_ngu(nhan, "person", "vi") == NHAN_MAC_DINH["person"]["vi"]


def tu_phu(tu: str, nhan: dict | None = None, lang: str = "vi") -> str:
    """Một trong `TU_TRUONG_HOC`: từ trường học nếu workspace còn là trường học, không thì từ trung tính."""
    vi_t, vi_k, en_t, en_k = TU_TRUONG_HOC[tu]
    truong = la_truong_hoc(nhan)
    if lang == "vi":
        chu, khac = vi_t, vi_k
    else:
        chu, khac = (en_t, en_k) if en_t is not None else (None, None)
    if truong and chu is not None:
        return dien(chu, nhan, lang)
    if not truong and khac is not None:
        return dien(khac, nhan, lang)               # có thể chứa {session_l}…
    return dang_chu(nhan, "person", "l", lang)      # "em" -> nhãn người


def nhan_ngon_ngu(nhan: dict | None, danh_tu: str, lang: str = "vi") -> str:
    """Nhãn của `danh_tu` theo `lang`; en trống hoặc thiếu thì rơi về vi.

    Danh từ không khai (hoặc khai rỗng) thì lấy NGUYÊN cặp mặc định trường học.
    Khai `vi` mà bỏ `en` thì `en` = `vi` đó (không phải `en` mặc định: "Student"
    đứng cạnh "Nhân viên" là sai).
    """
    cap = ((nhan or {}).get(danh_tu)) or NHAN_MAC_DINH[danh_tu]
    vi = str(cap.get("vi") or "").strip() or NHAN_MAC_DINH[danh_tu]["vi"]
    if lang == "vi":
        return vi
    return str(cap.get(lang) or "").strip() or vi


def _so_nhieu(chu: str, lang: str) -> str:
    """Tiếng Anh thêm s/es/ies; tiếng Việt không có số nhiều."""
    if lang != "en" or not chu or not _la_chu_anh(chu):
        return chu
    thuong = chu.lower()
    if re.search(r"(s|x|z|ch|sh)$", thuong):
        return chu + "es"
    if re.search(r"[^aeiou]y$", thuong):
        return chu[:-1] + "ies"
    return chu + "s"


def _ha_thuong(chu: str) -> str:
    # Chữ viết tắt (CLB, HR) giữ nguyên: "clb" không phải một từ.
    if chu.isupper():
        return chu
    return chu.lower()


_RE_LATIN_DON = re.compile(r"[A-Za-z][A-Za-z '\-]*")


def _la_chu_anh(chu: str) -> bool:
    """Nhãn có đúng là chữ Anh (chỉ chữ cái Latin không dấu) không?

    Nhãn `en` để trống thì rơi về nhãn tiếng Việt; thêm "s" hay "a/an" vào chữ
    Việt đó ("nhân viêns", "a nhân viên") là sai. Nhãn tiếng Anh thật gần như
    luôn là chữ Latin không dấu, nên chỉ chúng được chia số nhiều / thêm mạo từ.
    """
    return bool(_RE_LATIN_DON.fullmatch(chu))


def dang_chu(nhan: dict | None, danh_tu: str, co: str = "", lang: str = "vi") -> str:
    """Một chỗ giữ đã giải: nhãn + cờ ("l", "p", "s", "a", "c" hoặc ghép, vd "sl")."""
    if "v" in co:
        lang = "vi"
    chu = nhan_ngon_ngu(nhan, danh_tu, lang)
    if "s" in co and lang == "vi":
        chu = _VIET_TAT.get((danh_tu, chu), chu)
    # Hạ thường TRƯỚC khi chia số nhiều: "HR" giữ nguyên rồi mới thành "HRs".
    if "l" in co:
        chu = _ha_thuong(chu)
    if "p" in co:
        chu = _so_nhieu(chu, lang)
    if "a" in co and lang == "en" and chu and _la_chu_anh(chu):
        # Chọn a/an theo CHỮ CÁI đầu ("an employee", "a user"): đủ cho nhãn ngắn
        # người ta đặt; các ngoại lệ về âm ("an hour") không đáng thêm luật.
        chu = ("an " if chu[0].lower() in "aeiou" else "a ") + chu
    if "c" in co and chu:
        chu = chu[0].upper() + chu[1:]
    if "u" in co:
        chu = chu.upper()
    return chu


def dien(mau: str, nhan: dict | None = None, lang: str = "vi",
         thoat_ngoac: bool = False) -> str:
    """Thay mọi `{person}`, `{slot_l}`… trong `mau` bằng nhãn, và `{em}` `{gv}` `{nt}` `{truong}`
    bằng từ của trường học hay từ trung tính (xem `TU_TRUONG_HOC`).

    Chỉ chạm tới chỗ giữ danh từ: mọi `{tham_so}` khác để nguyên cho `str.format`
    hay bộ điền của giao diện. `nhan` None = mặc định trường học.

    `thoat_ngoac`: gấp đôi `{` `}` TRONG nhãn đã điền (`{{`, `}}`) — dùng khi chuỗi
    kết quả còn phải đi qua `str.format`, để nhãn người dùng đặt có ngoặc nhọn thì
    không bị coi là tham số.
    """
    if not isinstance(mau, str) or "{" not in mau:
        return mau

    def doi(m):
        if m.group(3):
            chu = tu_phu(m.group(3), nhan, lang)
            if m.group(4) == "_c" and chu:          # _c: viết hoa chữ đầu
                chu = chu[0].upper() + chu[1:]
            elif m.group(4) == "_u":                # _u: VIẾT HOA TOÀN BỘ
                chu = chu.upper()
        else:
            chu = dang_chu(nhan, m.group(1), m.group(2) or "", lang)
        return chu.replace("{", "{{").replace("}", "}}") if thoat_ngoac else chu

    return _RE_CHO_GIU.sub(doi, mau)


def sao_nhan_mac_dinh() -> dict:
    return copy.deepcopy(NHAN_MAC_DINH)


def _khong_dau_gon(chu: str) -> str:
    """'Phiên' -> 'phien' (chỉ chữ và số, hạ thường) — để so nhãn với tiền tố của mã buổi."""
    import unicodedata
    s = unicodedata.normalize("NFD", str(chu or "").replace("đ", "d").replace("Đ", "D"))
    return re.sub(r"[^a-z0-9]+", "", "".join(c for c in s if not unicodedata.combining(c)).lower())


def ten_tep_so_nhap(nhan: dict | None = None) -> str:
    """Tên tệp (không đuôi) của Sổ nhập: `SO_NHAP_CLB` với nhãn chỗ xếp mặc định, còn lại
    `SO_NHAP_<NHÃN CHỖ XẾP KHÔNG DẤU>` ("Dự án" -> `SO_NHAP_DU_AN`). Tên tệp là thứ người dùng
    mới nhìn thấy đầu tiên, nên không để chữ "CLB" nằm trong sổ của công ty hay sự kiện."""
    if nhan_ngon_ngu(nhan, "slot", "vi") == NHAN_MAC_DINH["slot"]["vi"]:
        return "SO_NHAP_CLB"
    import unicodedata
    goc = unicodedata.normalize(
        "NFD", nhan_ngon_ngu(nhan, "slot", "vi").replace("đ", "d").replace("Đ", "D"))
    khong_dau = "".join(c for c in goc if not unicodedata.combining(c))
    tu = re.sub(r"[^A-Za-z0-9]+", "_", khong_dau).strip("_").upper()
    return "SO_NHAP_" + tu if tu else "SO_NHAP"


def ten_buoi(ma: str, nhan: dict | None = None, lang: str = "vi") -> str:
    """Tên buổi cho người đọc: mã `phien_1` -> "Phiên 1" khi tiền tố trùng nhãn của danh từ `session`.

    Chỉ đổi mã dạng `<chữ>_<số>` mà `<chữ>` trùng (không dấu, hoa/thường) với nhãn vi HOẶC en của
    `session`, rồi viết bằng nhãn của ngôn ngữ đang dùng ("Track 1" trong giao diện tiếng Anh).
    Mã khác (`thu_2`, `chu_nhat`, tên tự đặt) giữ nguyên. Mã trống / buổi mặc định do bên gọi
    xử lý trước. Đối xứng với `tenBuoi` trong js/05_quan_ly.js.
    """
    m = re.fullmatch(r"([a-z0-9]+)_(\d+)", ma or "")
    if not m:
        return ma
    for ngon in ("vi", "en"):
        if _khong_dau_gon(nhan_ngon_ngu(nhan, "session", ngon)) == m.group(1):
            return "%s %s" % (nhan_ngon_ngu(nhan, "session", lang), m.group(2))
    return ma
