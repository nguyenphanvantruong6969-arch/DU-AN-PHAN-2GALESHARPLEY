"""Chạy phần mềm trên các bộ dữ liệu của du_lieu_test với seed cố định.

Dùng cho test "luật mặc định cho đúng kết quả như trước": GOLDEN
(tests/du_lieu_ws/ket_qua_truoc_luat.json) được sinh từ mã TRƯỚC khi có luật
nhóm / điểm theo người, rồi so lại mỗi lần chạy bộ test.
"""

import os
import sqlite3
import sys

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in (GOC, os.path.join(GOC, "du_lieu_test")):
    if p not in sys.path:
        sys.path.insert(0, p)

from api import PipelineAPI  # noqa: E402
from do_anh_huong_seed import BO_DU_LIEU, nap_bo  # noqa: E402

SEED = 42


def ket_qua(thu_muc, files, ap_dung=None):
    """Nạp `files`, (tuỳ chọn) gọi `ap_dung(api)`, chạy với SEED, trả các dòng kết quả."""
    db = nap_bo(str(thu_muc), files)
    api = PipelineAPI(db)
    if ap_dung:
        ap_dung(api)
    res = api.run_pipeline(SEED)
    assert res["ok"], res
    conn = sqlite3.connect(db)
    try:
        return [list(r) for r in conn.execute(
            "SELECT student_id, buoi, club_id, matched_tier, rank_in_student_pref "
            "FROM match_results ORDER BY student_id, buoi")]
    finally:
        conn.close()


def tat_ca(thu_muc_goc, ap_dung=None):
    ra = {}
    for i, (ten, files) in enumerate(BO_DU_LIEU):
        tm = os.path.join(str(thu_muc_goc), "b%d" % i)
        os.makedirs(tm)
        ra[ten.split()[0]] = ket_qua(tm, files, ap_dung)
    return ra
