"""Luật xếp của không gian làm việc: nhóm cứng, chỉ theo nhóm, điểm theo người."""

import inspect
import json
import os
import random
import sqlite3

import pytest

import cau_hinh_ws as cfgws
import rbda_priority_pipeline as rp
from _ket_qua_bo_du_lieu import tat_ca
from api import PipelineAPI

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLDEN = os.path.join(GOC, "tests", "du_lieu_ws", "ket_qua_truoc_luat.json")


def _luat(**kw):
    r = {"max_choices": 10, "max_tests": 5, "priority": "score", "tier_mode": "reserve",
         "score_scope": "per_slot", "tiers": []}
    r.update(kw)
    return r


def _mo_ws(tmp_path, **luat):
    root = tmp_path / "goc"
    root.mkdir(exist_ok=True)
    api = PipelineAPI(None, thu_muc_xuat=str(tmp_path), thu_muc_goc=str(root))
    cfg = {"name": "X", "rules": _luat(**luat)}
    slug = api.create_workspace("X", cfg)["data"]["slug"]
    assert api.open_workspace(slug)["ok"]
    return api


def _dat_luat(db, **luat):
    cfgws.ghi_cau_hinh(db, {"rules": _luat(**luat)})


def _hs(api, sid, prefs, nhom=""):
    assert api.create_student_if_missing(sid, "HS " + sid)["ok"]
    if nhom:
        assert api.set_student_reserve_group(sid, nhom)["ok"]
    assert api.submit_preferences(sid, prefs)["ok"]


def _ket_qua(api):
    with api._ket_noi_doc() as cur:
        return {r[0]: r[1] for r in cur.execute(
            "SELECT student_id, club_id FROM match_results")}


# ------------------------------------------------------------------ #
# compute_club_priority
# ------------------------------------------------------------------ #

def test_chu_ky_khong_nhan_thu_hang_nguyen_vong():
    ten = list(inspect.signature(rp.compute_club_priority).parameters)
    assert ten == ["club_id", "applicants_for_club", "tested_scores_for_club",
                   "stb_lottery", "tier_rank"]
    assert not any("pref" in t or "nguyen" in t for t in ten)


def test_tier_rank_nhom_dung_truoc_diem_roi_da_cham_roi_stb():
    stb = {"a": 5, "b": 1, "c": 2, "d": 3, "e": 4, "f": 6}
    diem = {"a": 9.0, "b": 2.0, "c": 7.0}          # d, e, f chưa chấm
    hang = {"a": 1, "b": 0, "c": 0, "d": 0, "e": 1}   # f không có nhóm
    kq = rp.compute_club_priority("x", list("abcdef"), diem, stb, tier_rank=hang)
    # nhóm 0: c (7) rồi b (2) đã chấm, rồi d chưa chấm; nhóm 1: a (9) rồi e; cuối: f
    assert kq == ["c", "b", "d", "a", "e", "f"]


def test_tier_rank_cung_diem_thi_stb_phan_xu_va_ma_hs_la_khoa_cuoi():
    kq = rp.compute_club_priority("x", ["m", "n", "o"], {"m": 5.0, "n": 5.0, "o": 5.0},
                                  {"m": 3, "n": 3, "o": 1}, tier_rank={})
    assert kq == ["o", "m", "n"]


def test_khong_co_tier_rank_van_la_hai_tang_nhu_cu():
    stb = {"a": 5, "b": 1, "c": 2}
    diem = {"a": 9.0, "b": 2.0}
    assert rp.compute_club_priority("x", ["a", "b", "c"], diem, stb) == ["a", "b", "c"]
    assert rp.compute_club_priority("x", ["c", "b", "a"], diem, stb, None) == ["a", "b", "c"]


def test_thieu_stb_van_bao_loi_o_che_do_nhom():
    with pytest.raises(ValueError, match="STB"):
        rp.compute_club_priority("x", ["a"], {}, {}, tier_rank={})


# ------------------------------------------------------------------ #
# xay_tier_rank / tham_so_luat
# ------------------------------------------------------------------ #

def test_xay_tier_rank_chuan_hoa_nhan_va_bo_em_ngoai_danh_sach():
    sv = {"a": {"reserve_group": "hang_a"}, "b": {"reserve_group": "hang_b"},
          "c": {"reserve_group": None}, "d": {"reserve_group": "khac"},
          "e": {"reserve_group": ""}}
    kq = rp.xay_tier_rank(sv, ["Hạng A", " hạng-B ", "", "Hạng A"])
    assert kq == {"a": 0, "b": 1}
    assert rp.xay_tier_rank(sv, []) == {}
    assert rp.chuan_hoa_nhom("Hạng A") == "hang_a" == rp.chuan_hoa_nhom("hang-a")


def test_tham_so_luat_mac_dinh_la_duong_chay_cu():
    for rules in (None, {}, _luat(), _luat(priority="score+tier"),
                  _luat(priority="score+tier", tier_mode="reserve", tiers=["a"])):
        assert rp.tham_so_luat(rules, {"s": {"reserve_group": "a"}}) == {
            "tier_rank": None, "bo_qua_du_tru": False}


def test_tham_so_luat_nhom_cung():
    sv = {"s": {"reserve_group": "a"}, "t": {"reserve_group": "zz"}}
    for rules in (_luat(tier_mode="strict", tiers=["a"]),
                  _luat(priority="tier", tiers=["a"])):
        assert rp.tham_so_luat(rules, sv) == {"tier_rank": {"s": 0}, "bo_qua_du_tru": True}


def test_luat_mac_dinh_cua_thuat_toan_khop_cau_hinh_workspace():
    r = cfgws.MAC_DINH_TRUONG_HOC["rules"]
    for k, v in rp.LUAT_XEP_MAC_DINH.items():
        assert r[k] == v, k


# ------------------------------------------------------------------ #
# run_rbda — nhóm cứng
# ------------------------------------------------------------------ #

def _du_lieu_nho(reserve_capacity=0, capacity=1):
    clubs = {"c": {"capacity": capacity, "reserve_capacity": reserve_capacity,
                   "reserve_group": "x", "buoi": rp.BUOI_MAC_DINH}}
    return clubs


def test_nhom_cung_thang_diem_con_mac_dinh_thi_diem_thang():
    students = {"cao_diem": {"reserve_group": "thuong"}, "uu_tien": {"reserve_group": "vip"}}
    prefs = {"cao_diem": ["c"], "uu_tien": ["c"]}
    app = {"c": ["cao_diem", "uu_tien"]}
    diem = {"c": {"cao_diem": 9.0, "uu_tien": 3.0}}
    stb = {"cao_diem": 1, "uu_tien": 2}
    clubs = _du_lieu_nho()
    fn = rp.default_reserve_eligible_fn(students, clubs)
    mac_dinh = rp.run_rbda(students, clubs, diem, app, prefs, stb, fn)
    assert mac_dinh.assignment == {"cao_diem": "c", "uu_tien": None}
    hang = rp.xay_tier_rank(students, ["vip", "thuong"])
    cung = rp.run_rbda(students, clubs, diem, app, prefs, stb, fn,
                       tier_rank=hang, bo_qua_du_tru=True)
    assert cung.assignment == {"cao_diem": None, "uu_tien": "c"}
    assert rp.verify_stability(cung, clubs, prefs, fn, True) == []


def test_nhom_cung_khong_chay_luot_du_tru_mem():
    """Một suất dành cho nhóm x: mặc định x1 giữ nó dù đứng cuối; chế độ cứng
    không có suất dự trữ nào — nhóm xếp đầu giữ cả hai suất."""
    students = {"y1": {"reserve_group": "y"}, "y2": {"reserve_group": "y"},
                "x1": {"reserve_group": "x"}}
    prefs = {s: ["c"] for s in students}
    app = {"c": list(students)}
    stb = {"y1": 1, "y2": 2, "x1": 3}
    clubs = _du_lieu_nho(reserve_capacity=1, capacity=2)
    fn = rp.default_reserve_eligible_fn(students, clubs)
    mem = rp.run_rbda(students, clubs, {}, app, prefs, stb, fn)
    assert {s for s, c in mem.assignment.items() if c} == {"x1", "y1"}
    assert mem.matched_tier["x1"] == "reserve"
    cung = rp.run_rbda(students, clubs, {}, app, prefs, stb, fn,
                       tier_rank=rp.xay_tier_rank(students, ["y", "x"]), bo_qua_du_tru=True)
    assert {s for s, c in cung.assignment.items() if c} == {"y1", "y2"}
    assert set(cung.matched_tier.values()) == {"general"}


def test_chi_theo_nhom_roi_stb_diem_bi_bo(tmp_path):
    """priority tier: điểm không quyết định gì, kể cả điểm đã chấm sẵn."""
    api = _mo_ws(tmp_path, priority="tier", tiers=["vip", "thuong"])
    assert api.create_or_update_club("c", "C", 1, 0, "")["ok"]
    _hs(api, "cao", ["c"], "thuong")
    _hs(api, "vip", ["c"], "vip")
    _hs(api, "vip2", ["c"], "vip")
    with sqlite3.connect(api.db_path) as con:          # điểm cũ còn sót trong CSDL
        for sid, d in (("cao", 10.0), ("vip", 1.0), ("vip2", 9.0)):
            con.execute("INSERT INTO club_test_selection VALUES (?, 'c')", (sid,))
            con.execute("INSERT INTO club_scores VALUES (?, 'c', ?)", (sid, d))
    du_lieu = rp.load_from_sqlite(api.db_path)
    assert du_lieu[2] == {"c": {}}                     # tested_scores rỗng
    assert api.run_pipeline(42)["ok"]
    with api._ket_noi_doc() as cur:
        stb = {r[0]: r[1] for r in cur.execute("SELECT student_id, stb_number FROM students")}
    thang = _ket_qua(api)
    nguoi_thang = [s for s, c in thang.items() if c == "c"]
    assert len(nguoi_thang) == 1
    # nhóm vip trước nhóm thuong; trong cùng nhóm: số bốc thăm nhỏ hơn
    assert nguoi_thang[0] == min(("vip", "vip2"), key=lambda s: stb[s])


# ------------------------------------------------------------------ #
# Điểm theo người
# ------------------------------------------------------------------ #

def test_diem_theo_nguoi_trai_ra_moi_cho_da_dang_ky(tmp_path):
    api = _mo_ws(tmp_path, score_scope="per_person")
    for cid in ("a", "b", "c"):
        assert api.create_or_update_club(cid, cid.upper(), 2, 0, "")["ok"]
    _hs(api, "s1", ["a", "b"])
    _hs(api, "s2", ["c"])
    _hs(api, "s3", ["a"])
    assert api.submit_person_scores([{"student_id": "s1", "score": "8,5"},
                                     {"student_id": "s2", "score": 6}])["ok"]
    with sqlite3.connect(api.db_path) as con:        # điểm theo chỗ còn sót: bị bỏ
        con.execute("INSERT INTO club_test_selection VALUES ('s3', 'a')")
        con.execute("INSERT INTO club_scores VALUES ('s3', 'a', 9.9)")
    students, clubs, tested, applicants, prefs, _ = rp.load_from_sqlite(api.db_path)
    assert tested == {"a": {"s1": 8.5}, "b": {"s1": 8.5}, "c": {"s2": 6.0}}
    assert "s3" not in tested["a"]
    # engine không đổi: cùng dữ liệu đã trải thì run_rbda cho kết quả ổn định
    # và người có điểm cao hơn thắng chỗ tranh nhau
    with sqlite3.connect(api.db_path) as con:
        con.execute("UPDATE clubs SET capacity = 1 WHERE club_id = 'a'")
    assert api.submit_person_scores([{"student_id": "s3", "score": 3}])["ok"]
    assert api.run_pipeline(7)["ok"]
    kq = _ket_qua(api)
    assert kq["s1"] == "a" and kq["s3"] is None


def test_diem_theo_nguoi_che_do_mac_dinh_van_dung_club_scores(tmp_path):
    api = PipelineAPI(str(tmp_path / "app.db"))
    api.create_or_update_club("a", "A", 2, 0, "")
    _hs(api, "s1", ["a"])
    api.submit_test_selection("s1", ["a"])
    api.submit_club_scores("a", [{"student_id": "s1", "score": 7}])
    with sqlite3.connect(api.db_path) as con:         # cột mới có giá trị cũng bị bỏ qua
        con.execute("UPDATE students SET diem_ca_nhan = 99 WHERE student_id = 's1'")
    assert rp.load_from_sqlite(api.db_path)[2] == {"a": {"s1": 7.0}}


def test_api_cham_diem_theo_nguoi(tmp_path):
    api = _mo_ws(tmp_path, score_scope="per_person")
    api.create_or_update_club("a", "A", 2, 0, "")
    _hs(api, "s1", ["a"])
    api.create_student_if_missing("s9", "Không đăng ký")
    ds = api.get_person_scoring_list()["data"]
    assert [p["student_id"] for p in ds["persons"]] == ["s1"]
    assert set(ds["persons"][0]) == {"student_id", "name", "score"}     # mù: không STB
    assert ds["n_scored"] == 0
    res = api.submit_person_scores([
        {"student_id": "s1", "score": "7,25"}, {"student_id": "s9", "score": 5},
        {"student_id": "s1x", "score": 5}])
    assert res["ok"] and res["data"]["n_saved"] == 1
    assert [w["code"] for w in res["data"]["warnings"]] == ["score_not_applicant"] * 2
    assert api.get_person_scoring_list()["data"]["persons"][0]["score"] == 7.25
    bad = api.submit_person_scores([{"student_id": "s1", "score": "abc"}])
    assert bad["data"]["warnings"][0]["code"] == "score_not_a_number"
    neg = api.submit_person_scores([{"student_id": "s1", "score": -1}])
    assert neg["data"]["warnings"][0]["code"] == "score_negative"
    assert api.submit_person_scores([{"student_id": "s1", "score": ""}])["ok"]   # xoá
    assert api.get_person_scoring_list()["data"]["persons"][0]["score"] is None
    assert api.submit_person_scores([])["errors"][0]["code"] == "scores_must_be_nonempty_list"


def test_cham_theo_nguoi_bi_chan_o_che_do_theo_cho(tmp_path):
    api = _mo_ws(tmp_path)
    assert api.get_person_scoring_list()["errors"][0]["code"] == "diem_khong_theo_nguoi"
    assert api.submit_person_scores([{"student_id": "s", "score": 1}])[
        "errors"][0]["code"] == "diem_khong_theo_nguoi"
    assert api.get_luat_diem()["data"] == {
        "priority": "score", "score_scope": "per_slot", "tier_mode": "reserve"}


def test_cot_diem_ca_nhan_duoc_them_vao_csdl_cu(tmp_path):
    db = str(tmp_path / "cu.db")
    with sqlite3.connect(db) as con:        # bảng students của bản cũ: chưa có cột mới
        con.execute("CREATE TABLE students (student_id TEXT PRIMARY KEY, name TEXT, "
                    "stb_number INTEGER, reserve_group TEXT)")
        con.execute("INSERT INTO students (student_id, name) VALUES ('s', 'S')")
    assert rp.di_tru_schema(db) == ["students.diem_ca_nhan"]
    with sqlite3.connect(db) as con:
        assert con.execute("SELECT diem_ca_nhan FROM students").fetchone() == (None,)
    assert rp.di_tru_schema(db) == []                  # chạy lại không làm gì


def test_dau_van_tay_mac_dinh_khong_doi_va_doi_theo_luat_va_diem(tmp_path):
    api = _mo_ws(tmp_path)
    api.create_or_update_club("a", "A", 2, 0, "")
    _hs(api, "s1", ["a"])

    def vt():
        with api._ket_noi_doc() as cur:
            return rp.dau_van_tay_du_lieu(cur)

    mac_dinh = vt()
    # score+tier KHÁC luật mặc định về chữ (dù cách xếp y hệt): dấu vân tay đổi,
    # để kết quả cũ báo "dữ liệu đã đổi" khi đổi luật.
    _dat_luat(api.db_path, priority="score+tier")
    assert vt() != mac_dinh
    _dat_luat(api.db_path)
    assert vt() == mac_dinh                             # về mặc định thì về đúng dấu cũ
    _dat_luat(api.db_path, score_scope="per_person")
    truoc = vt()
    api.submit_person_scores([{"student_id": "s1", "score": 5}])
    assert vt() != truoc                                # sửa điểm người -> kết quả cũ đi


# ------------------------------------------------------------------ #
# Ổn định (verify_stability) trên dữ liệu ngẫu nhiên, mỗi chế độ
# ------------------------------------------------------------------ #

def _du_lieu_ngau_nhien(seed, n_hs=40, n_clb=5):
    rng = random.Random(seed)
    nhom = ["vip", "kha", "thuong", None]
    students = {"s%02d" % i: {"reserve_group": rng.choice(nhom)} for i in range(n_hs)}
    clubs = {"c%d" % j: {"capacity": rng.randint(2, 8), "reserve_capacity": 0,
                         "reserve_group": rng.choice(["vip", "kha", None]),
                         "buoi": rp.BUOI_MAC_DINH} for j in range(n_clb)}
    for c in clubs.values():
        c["reserve_capacity"] = rng.randint(0, c["capacity"]) if c["reserve_group"] else 0
    prefs = {s: rng.sample(list(clubs), rng.randint(1, n_clb)) for s in students}
    app = {c: [s for s in students if c in prefs[s]] for c in clubs}
    diem = {c: {s: round(rng.uniform(0, 10), 1) for s in app[c] if rng.random() < 0.6}
            for c in clubs}
    stb = {s: i + 1 for i, s in enumerate(rng.sample(list(students), len(students)))}
    return students, clubs, diem, app, prefs, stb


@pytest.mark.parametrize("che_do", ["mac_dinh", "nhom_cung", "chi_nhom", "theo_nguoi"])
def test_xep_on_dinh_tren_du_lieu_ngau_nhien(che_do):
    for seed in range(25):
        students, clubs, diem, app, prefs, stb = _du_lieu_ngau_nhien(seed)
        kw = {}
        if che_do == "nhom_cung":
            kw = {"tier_rank": rp.xay_tier_rank(students, ["vip", "kha", "thuong"]),
                  "bo_qua_du_tru": True}
        elif che_do == "chi_nhom":
            diem = {c: {} for c in clubs}               # bỏ điểm như bộ nạp làm
            kw = {"tier_rank": rp.xay_tier_rank(students, ["thuong", "vip"]),
                  "bo_qua_du_tru": True}
        elif che_do == "theo_nguoi":
            rng = random.Random(seed)                   # một điểm cho cả người
            mot = {s: round(rng.uniform(0, 10), 1) for s in students if rng.random() < 0.7}
            diem = {c: {s: mot[s] for s in app[c] if s in mot} for c in clubs}
        fn = rp.default_reserve_eligible_fn(students, clubs)
        kq = rp.run_rbda(students, clubs, diem, app, prefs, stb, fn, **kw)
        assert rp.verify_stability(kq, clubs, prefs, fn, kw.get("bo_qua_du_tru", False)) == [], (
            che_do, seed)
        # nhóm cứng thật sự cứng: ở mỗi CLB, người trúng không bị người nhóm
        # thấp hơn (đã đăng ký cùng CLB, bị từ chối) vượt mặt khi cùng được chọn
        if che_do == "nhom_cung":
            for cid, xep in kq.base_rank.items():
                hang = kw["tier_rank"]
                thu_tu = sorted(xep, key=xep.get)
                gia = [hang.get(s, 99) for s in thu_tu]
                assert gia == sorted(gia), (seed, cid)


def test_xep_nhieu_buoi_voi_nhom_cung_on_dinh():
    for seed in range(10):
        students, clubs, diem, app, prefs, stb = _du_lieu_ngau_nhien(seed, 30, 6)
        for i, cid in enumerate(sorted(clubs)):
            clubs[cid]["buoi"] = "thu_2" if i % 2 else "thu_3"
        fn = rp.default_reserve_eligible_fn(students, clubs)
        kw = {"tier_rank": rp.xay_tier_rank(students, ["vip", "kha"]), "bo_qua_du_tru": True}
        kq = rp.run_rbda_nhieu_buoi(students, clubs, diem, app, prefs, stb, fn, seed=seed, **kw)
        ra = rp.verify_stability_tuan(kq, clubs, prefs, fn, True)
        assert all(v == [] for v in ra.values()), (seed, ra)


@pytest.mark.parametrize("luat", [
    {"tier_mode": "strict", "tiers": ["vip", "kha"]},
    {"priority": "tier", "tiers": ["vip", "kha"]},
    {"score_scope": "per_person"},
])
def test_run_pipeline_qua_chot_on_dinh_o_moi_che_do(tmp_path, luat):
    """run_pipeline tự chạy sanity + verify_stability trước khi ghi: ok = ổn định."""
    for seed in range(3):
        sub = tmp_path / ("s%d" % seed)
        sub.mkdir()
        api = _mo_ws(sub, **luat)
        rng = random.Random(seed)
        for j in range(4):
            api.create_or_update_club("c%d" % j, "C%d" % j, rng.randint(2, 5),
                                      rng.randint(0, 1), "vip" if j == 0 else "")
        for i in range(30):
            sid = "s%02d" % i
            _hs(api, sid, rng.sample(["c0", "c1", "c2", "c3"], rng.randint(1, 4)),
                rng.choice(["vip", "kha", "", "thuong"]))
        if luat.get("score_scope") == "per_person":
            api.submit_person_scores([{"student_id": "s%02d" % i, "score": rng.randint(0, 10)}
                                      for i in range(30) if rng.random() < 0.7])
        res = api.run_pipeline(seed + 1)
        assert res["ok"], res["errors"]


# ------------------------------------------------------------------ #
# Cảnh báo sức khoẻ dữ liệu
# ------------------------------------------------------------------ #

def _ma_canh_bao(api):
    res = api.get_data_health_report()
    assert res["ok"], res
    return {w["code"]: w for w in res["data"]["warnings"]}


def test_canh_bao_nhom_cung_co_nguoi_chua_co_nhom(tmp_path):
    api = _mo_ws(tmp_path, tier_mode="strict", tiers=["vip", "kha"])
    api.create_or_update_club("a", "A", 3, 0, "")
    _hs(api, "co", ["a"], "vip")
    _hs(api, "khong", ["a"])
    _hs(api, "la", ["a"], "nhom_la")
    api.create_student_if_missing("chua_dk", "Chưa đăng ký")     # chưa đăng ký: không tính
    w = _ma_canh_bao(api)["health_strict_chua_co_nhom"]
    assert w["params"]["n"] == 2 and w["severity"] == "high"
    assert "khong" in w["params"]["sample"] and "la" in w["params"]["sample"]
    assert "chua_dk" not in w["params"]["sample"]
    # đủ nhóm thì hết cảnh báo
    api.set_student_reserve_group("khong", "kha")
    api.set_student_reserve_group("la", "vip")
    assert "health_strict_chua_co_nhom" not in _ma_canh_bao(api)


def test_canh_bao_chi_theo_nhom_cung_tinh_la_nhom_cung(tmp_path):
    api = _mo_ws(tmp_path, priority="tier", tiers=["vip"])
    api.create_or_update_club("a", "A", 3, 0, "")
    _hs(api, "khong", ["a"])
    assert "health_strict_chua_co_nhom" in _ma_canh_bao(api)


def test_canh_bao_theo_nguoi_chua_co_diem_va_bo_canh_bao_theo_cho(tmp_path):
    api = _mo_ws(tmp_path, score_scope="per_person")
    api.create_or_update_club("a", "A", 3, 0, "")
    _hs(api, "co", ["a"])
    _hs(api, "chua", ["a"])
    api.submit_person_scores([{"student_id": "co", "score": 8}])
    with sqlite3.connect(api.db_path) as con:       # tick thi mà chưa chấm theo chỗ
        con.execute("INSERT INTO club_test_selection VALUES ('chua', 'a')")
    ma = _ma_canh_bao(api)
    assert ma["health_per_person_chua_co_diem"]["params"]["n"] == 1
    assert "chua" in ma["health_per_person_chua_co_diem"]["params"]["sample"]
    assert "health_scoring_none" not in ma and "health_scoring_partial" not in ma
    api.submit_person_scores([{"student_id": "chua", "score": 4}])
    assert "health_per_person_chua_co_diem" not in _ma_canh_bao(api)


def test_canh_bao_mac_dinh_giu_nguyen_va_khong_co_canh_bao_moi(tmp_path):
    api = _mo_ws(tmp_path)
    api.create_or_update_club("a", "A", 3, 0, "")
    _hs(api, "s", ["a"])
    api.submit_test_selection("s", ["a"])
    ma = _ma_canh_bao(api)
    assert "health_scoring_none" in ma                       # chấm theo chỗ: vẫn báo
    assert not {"health_strict_chua_co_nhom", "health_per_person_chua_co_diem"} & set(ma)


# ------------------------------------------------------------------ #
# Luật mặc định = kết quả y như trước
# ------------------------------------------------------------------ #

def test_luat_mac_dinh_cho_ket_qua_y_nhu_truoc_tren_bo_du_lieu_that(tmp_path):
    truoc = json.load(open(GOLDEN, encoding="utf-8"))
    nay = json.loads(json.dumps(tat_ca(tmp_path), sort_keys=True))
    assert nay == truoc


def test_luat_tuong_duong_mac_dinh_cung_cho_ket_qua_y_nhu_truoc(tmp_path):
    """Đã ghi cấu hình tường minh (mặc định, và score+tier/reserve — cùng cách xếp)."""
    truoc = json.load(open(GOLDEN, encoding="utf-8"))
    for luat in (_luat(), _luat(priority="score+tier")):
        sub = tmp_path / json.dumps(luat["priority"])
        sub.mkdir()
        nay = tat_ca(sub, ap_dung=lambda api, l=luat: _dat_luat(api.db_path, **l))
        assert json.loads(json.dumps(nay, sort_keys=True)) == truoc, luat


def test_che_do_cung_thay_doi_ket_qua_that_su_tren_bo_du_lieu(tmp_path):
    """Đối chứng ngược: nếu chế độ cứng không làm gì thì các test trên vô nghĩa."""
    truoc = json.load(open(GOLDEN, encoding="utf-8"))
    nay = tat_ca(tmp_path, ap_dung=lambda api: _dat_luat(
        api.db_path, tier_mode="strict", tiers=["khoi10", "chinh_sach"]))
    assert json.loads(json.dumps(nay, sort_keys=True)) != truoc
