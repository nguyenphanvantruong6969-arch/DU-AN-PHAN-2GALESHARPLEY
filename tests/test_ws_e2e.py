"""Kịch bản đầu-cuối nhiều workspace (TASK 7): chuyển tay "trường học cũ" -> "công ty" -> "sự kiện",
nhập sổ mẫu, chạy xếp, đổi qua lại, và kiểm KẾT QUẢ KHÔNG TRỘN.

Trình tự:
  a. Di trú một BẢN SAO của du_lieu_test/app_DEMO_da_cham_diem.db (CSDL cũ, chưa có cột `buoi`)
     vào workspace "Trường học".
  b. Dựng workspace công ty (điểm KPI theo NGƯỜI, nhóm xếp CỨNG) và workspace sự kiện (chỉ theo
     nhóm, 3 phiên).
  c. Mỗi workspace: sinh Sổ nhập mẫu (`tao_so_nhap_mau`), điền dữ liệu, nạp, chạy xếp; đổi qua
     lại giữa ba cái và đối chiếu mọi thứ đọc được (kết quả, nhãn, luật, sao lưu, tệp CSV).
  d. `verify_stability` trên KẾT QUẢ ĐÃ LƯU của cả ba (dựng lại từ CSDL, độc lập với lần chạy).
"""

import base64
import csv
import hashlib
import io
import os
import random
import shutil
from types import SimpleNamespace

import pytest

import rbda_priority_pipeline as rp
import workspace as ws
from api import PipelineAPI

openpyxl = pytest.importorskip("openpyxl")

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMO = os.path.join(GOC, "du_lieu_test", "app_DEMO_da_cham_diem.db")

CONG_TY = {
    "name": "Công ty ABC", "industry": "company",
    "labels": {
        "person": {"vi": "Nhân viên", "en": "Employee"},
        "slot": {"vi": "Dự án", "en": "Project"},
        "session": {"vi": "Ca", "en": "Shift"},
        "group": {"vi": "Cấp bậc", "en": "Level"},
        "score": {"vi": "KPI", "en": "KPI"},
    },
    "rules": {"max_choices": 4, "max_tests": 2, "priority": "score+tier",
              "tier_mode": "strict", "score_scope": "per_person",
              "tiers": ["Quản lý", "Chuyên viên", "Nhân viên mới"]},
}

SU_KIEN = {
    "name": "Hội nghị XYZ", "industry": "event",
    "labels": {
        "person": {"vi": "Khách", "en": "Guest"},
        "slot": {"vi": "Workshop", "en": "Workshop"},
        "session": {"vi": "Phiên", "en": "Track"},
        "group": {"vi": "Hạng vé", "en": "Ticket"},
        "score": {"vi": "Điểm", "en": "Score"},
    },
    "rules": {"max_choices": 2, "max_tests": 0, "priority": "tier",
              "tier_mode": "strict", "score_scope": "per_slot",
              "tiers": ["VIP", "Diễn giả", "Thường"]},
}


def _b64_wb(wb):
    b = io.BytesIO()
    wb.save(b)
    return base64.b64encode(b.getvalue()).decode()


def _dung_ba_workspace(tmp_path):
    """Dựng cả ba workspace trong `tmp_path` rồi trả (goc, api, slug_truong, slug_cty, slug_sk).

    (a) bản sao DEMO (CSDL cũ, chưa có cột `buoi`) di trú vào "Trường học" rồi chạy xếp;
    (b) workspace công ty và sự kiện;
    (c) mỗi cái: sinh sổ mẫu qua API, điền, nạp, chạy xếp."""
    goc = tmp_path / "goc"
    goc.mkdir()
    shutil.copy(DEMO, goc / "app.db")
    assert ws.di_chuyen_db_cu(str(goc)) is True
    xuat = tmp_path / "xuat"
    xuat.mkdir()
    api = PipelineAPI(ws.duong_dan_db(str(goc), ws.SLUG_TRUONG_HOC),
                      thu_muc_xuat=str(xuat), thu_muc_goc_ws=str(goc))
    rng = random.Random(7)
    truong = ws.SLUG_TRUONG_HOC
    assert api.run_pipeline(seed=3)["ok"]

    cty = api.create_workspace("Công ty ABC", CONG_TY)["data"]["slug"]
    sk = api.create_workspace("Hội nghị XYZ", SU_KIEN)["data"]["slug"]

    assert api.open_workspace(cty)["ok"]
    r = api.import_so_nhap(_dien_so_cong_ty(api, rng))
    assert r["ok"], r["errors"]
    assert api.run_pipeline(seed=5)["ok"]

    assert api.open_workspace(sk)["ok"]
    r = api.import_so_nhap(_dien_so_su_kien(api, rng))
    assert r["ok"], r["errors"]
    assert api.run_pipeline(seed=9)["ok"]
    return str(goc), api, truong, cty, sk


@pytest.fixture(scope="module")
def ba_ws(tmp_path_factory):
    """Ba workspace đã chạy xong, dùng chung cho các test CHỈ ĐỌC trong tệp này."""
    goc, api, truong, cty, sk = _dung_ba_workspace(tmp_path_factory.mktemp("e2e"))
    return SimpleNamespace(goc=goc, api=api, truong=truong, cty=cty, sk=sk)


def _ghi_dong(sheet, so_dong, gia_tri):
    """Ghi một dòng vào sheet của sổ mẫu. KHÔNG dùng append(): sổ mẫu đã định dạng sẵn hàng nghìn
    dòng trống nên append rơi xuống cuối và bị đọc là dòng 1501."""
    for cot, v in enumerate(gia_tri, start=1):
        sheet.cell(row=so_dong, column=cot, value=v)


def _dong_clb(tieu_de, **gia_tri):
    """Một dòng sheet CLB theo đúng thứ tự cột của tệp mẫu (cột không nhắc tới để trống)."""
    return [gia_tri.get(t) for t in tieu_de]


def _dien_so_cong_ty(api, rng):
    """Sổ mẫu của công ty (6 dự án, 24 nhân viên): KPI là MỘT cột cho cả dòng."""
    ra = api.tao_so_nhap_mau()
    assert ra["ok"], ra["errors"]
    wb = openpyxl.load_workbook(ra["data"]["path"])
    assert wb.sheetnames[:2] == ["1. Dự án", "2. Nhân viên"]
    du_an = wb["1. Dự án"]
    tieu_de = [c.value for c in du_an[1]]
    for i in range(1, 7):
        _ghi_dong(du_an, i + 1, _dong_clb(
            tieu_de, **{"Tên CLB": "Dự án %d" % i, "Chỉ tiêu": 4, "Mã CLB": "da%d" % i}))
    nv = wb["2. Nhân viên"]
    assert [c.value for c in nv[1]][:4] == ["Mã HS", "Họ tên", "Cấp bậc", "KPI"]
    cap = CONG_TY["rules"]["tiers"]
    for k in range(24):
        chon = rng.sample(range(1, 7), rng.randint(2, 4))
        _ghi_dong(nv, k + 2, ["NV%02d" % k, "Nhân viên %d" % k, rng.choice(cap),
                              rng.randint(50, 100)] + ["Dự án %d" % i for i in chon])
    return _b64_wb(wb)


def _dien_so_su_kien(api, rng):
    """Sổ mẫu của sự kiện: 3 phiên x 3 workshop, 30 khách chỉ có HẠNG VÉ (không điểm).

    Hai bước như người vận hành thật: nạp trước sheet workshop (sổ trống học sinh), rồi sinh lại
    sổ mẫu — lúc đó phần mềm đã biết có 3 phiên nên mẫu mới có đủ 3 x 2 cột nguyện vọng."""
    ra = api.tao_so_nhap_mau()
    assert ra["ok"], ra["errors"]
    wb = openpyxl.load_workbook(ra["data"]["path"])
    assert wb.sheetnames[:2] == ["1. Workshop", "2. Khách"]
    ws_clb = wb["1. Workshop"]
    tieu_de = [c.value for c in ws_clb[1]]
    dong, ten_theo_phien = 1, {}
    for p in (1, 2, 3):
        for w in (1, 2, 3):
            dong += 1
            ten = "Workshop %d.%d" % (p, w)
            _ghi_dong(ws_clb, dong, _dong_clb(
                tieu_de, **{"Tên CLB": ten, "Buổi": "phien_%d" % p, "Chỉ tiêu": 4,
                            "Mã CLB": "w%d_%d" % (p, w)}))
            ten_theo_phien.setdefault(p, []).append(ten)
    r = api.import_so_nhap(_b64_wb(wb))
    assert r["ok"], r["errors"]

    ra = api.tao_so_nhap_mau()
    assert ra["ok"], ra["errors"]
    wb = openpyxl.load_workbook(ra["data"]["path"])
    khach = wb["2. Khách"]
    tieu_de = [c.value for c in khach[1]]
    assert tieu_de[:3] == ["Mã HS", "Họ tên", "Hạng vé"]
    assert [t for t in tieu_de if str(t or "").startswith("NV")] == ["NV%d" % i for i in range(1, 7)]
    cap = SU_KIEN["rules"]["tiers"]
    for k in range(30):
        nvong = []
        for p in (1, 2, 3):
            nvong += rng.sample(ten_theo_phien[p], 2)
        dong = {"Mã HS": "K%02d" % k, "Họ tên": "Khách %d" % k, "Hạng vé": rng.choice(cap)}
        dong.update({"NV%d" % (i + 1): ten for i, ten in enumerate(nvong)})
        _ghi_dong(khach, k + 2, [dong.get(t) for t in tieu_de])
    return _b64_wb(wb)


def _anh_chup(api):
    """Mọi thứ MỘT workspace cho thấy ở các thẻ: kết quả, nhãn, luật, danh sách, lịch sử chạy."""
    ra = {}
    with api._ket_noi_doc() as cur:
        ra["ket_qua"] = sorted(tuple(r) for r in cur.execute(
            "SELECT student_id, buoi, club_id FROM match_results"))
        ra["hoc_sinh"] = sorted(r[0] for r in cur.execute("SELECT student_id FROM students"))
        ra["clb"] = sorted(r[0] for r in cur.execute("SELECT club_id FROM clubs"))
        ra["luat_xep"] = [r[0] for r in cur.execute(
            "SELECT luat_xep FROM run_history ORDER BY run_id")]
    cfg = api.get_workspace_state()["data"]
    ra["ten"], ra["nhan_clb"] = cfg["name"], cfg["config"]["labels"]["slot"]["vi"]
    ra["luat"] = cfg["config"]["rules"]
    ra["slug"] = cfg["slug"]
    return ra


def _chay(api, seed):
    r = api.run_pipeline(seed=seed)
    assert r["ok"], r
    return r


def _dung_ket_qua_da_luu(api):
    """Chạy lại thuật toán từ dữ liệu TRONG CSDL (luật của workspace, số bốc thăm đã khoá)
    và trả (kết quả lưu == kết quả chạy lại, các cặp phá vỡ của `verify_stability`)."""
    luat = api._luat_nghiem()
    (hs, clb, diem, ung_vien, nv, stb), _ = rp.load_from_sqlite_kem_dau_van_tay(api.db_path, luat)
    tham_so = rp.tham_so_luat(luat, hs)
    du_tru = rp.default_reserve_eligible_fn(hs, clb)
    with api._ket_noi_doc() as cur:
        seed = cur.execute("SELECT seed FROM run_meta WHERE id = 1").fetchone()[0]
        da_luu = {(r[0], r[1]): r[2] for r in cur.execute(
            "SELECT student_id, buoi, club_id FROM match_results")}
    kq = rp.run_rbda_nhieu_buoi(
        hs, clb, diem, ung_vien, nv, stb, is_reserve_eligible_fn=du_tru, seed=seed,
        tier_rank=tham_so["tier_rank"], bo_qua_du_tru=tham_so["bo_qua_du_tru"])
    chay_lai = {(sid, b): cid for sid, theo in kq.assignment.items() for b, cid in theo.items()}
    van_de = []
    nhom = rp.nhom_theo_buoi(clb)
    for buoi, kq_b in kq.per_buoi.items():
        clb_b, _, _, nv_b = rp.cat_du_lieu_theo_buoi(buoi, nhom[buoi], clb, diem, ung_vien, nv)
        van_de += rp.verify_stability(kq_b, clb_b, nv_b, du_tru,
                                      bo_qua_du_tru=tham_so["bo_qua_du_tru"])
    return da_luu == chay_lai, van_de, len(da_luu)




# ===========================================================================
# Các phép kiểm — dùng chung `ba_ws` (CHỈ ĐỌC; test nào ghi thì tự dựng riêng)
# ===========================================================================

def _chuyen(ba, slug):
    assert ba.api.open_workspace(slug)["ok"]
    assert ba.api.db_path == ws.duong_dan_db(ba.goc, slug)
    return ba.api


def _ids(ds, khoa="student_id"):
    return {x[khoa] for x in ds}


def test_ba_workspace_khac_nhau_that_su(ba_ws):
    """Điều kiện để các phép "không trộn" bên dưới có nghĩa."""
    a_t = _anh_chup(_chuyen(ba_ws, ba_ws.truong))
    a_c = _anh_chup(_chuyen(ba_ws, ba_ws.cty))
    a_s = _anh_chup(_chuyen(ba_ws, ba_ws.sk))
    assert (len(a_t["hoc_sinh"]), len(a_c["hoc_sinh"]), len(a_s["hoc_sinh"])) == (120, 24, 30)
    assert {b for _, b, _ in a_s["ket_qua"]} == {"phien_1", "phien_2", "phien_3"}
    assert {b for _, b, _ in a_c["ket_qua"]} == {rp.BUOI_MAC_DINH}
    assert a_t["luat"]["priority"] == "score" and a_t["luat_xep"] == [None]
    assert a_c["luat"]["score_scope"] == "per_person" and a_c["luat"]["tier_mode"] == "strict"
    assert a_s["luat"]["priority"] == "tier"
    assert a_c["luat_xep"][0] and a_s["luat_xep"][0] and a_c["luat_xep"] != a_s["luat_xep"]
    # ba tập mã không giao nhau
    assert not (set(a_t["hoc_sinh"]) & set(a_c["hoc_sinh"]) or set(a_c["hoc_sinh"]) & set(a_s["hoc_sinh"]))
    assert not (set(a_t["clb"]) & set(a_c["clb"]) or set(a_c["clb"]) & set(a_s["clb"]))


def test_doi_qua_lai_nhieu_lan_moi_the_chi_thay_du_lieu_cua_workspace_dang_mo(ba_ws):
    api = ba_ws.api
    mong = {slug: _anh_chup(_chuyen(ba_ws, slug)) for slug in (ba_ws.truong, ba_ws.cty, ba_ws.sk)}
    dem = {ba_ws.truong: (120, 10), ba_ws.cty: (24, 6), ba_ws.sk: (30, 9)}
    tien_to = {ba_ws.truong: "HS0", ba_ws.cty: "NV0", ba_ws.sk: "K0"}      # tìm theo mã, không theo tên
    for _ in range(3):
        for slug in (ba_ws.truong, ba_ws.cty, ba_ws.sk, ba_ws.cty, ba_ws.truong):
            _chuyen(ba_ws, slug)
            # thẻ Vận hành
            d = api.get_dashboard_status()["data"]
            assert (d["n_students"], d["n_clubs"]) == dem[slug] and d["has_results"]
            assert api.get_workspace_state()["data"]["slug"] == slug
            assert [h["luat_xep"] for h in api.get_run_history()["data"]] == mong[slug]["luat_xep"]
            # thẻ Kết quả
            ket_qua = api.get_match_results()["data"]
            ids = {r["student_id"] for r in (ket_qua["results"] if isinstance(ket_qua, dict) else ket_qua)}
            assert ids and ids <= set(mong[slug]["hoc_sinh"])
            tkb = api.get_thoi_khoa_bieu()["data"]
            assert _ids(tkb["hoc_sinh"]) == set(mong[slug]["hoc_sinh"])
            assert len(tkb["ds_buoi"]) == (3 if slug == ba_ws.sk else 1)
            assert _ids(api.get_club_fill_stats()["data"], "club_id") == set(mong[slug]["clb"])
            # thẻ Nhập tại chỗ
            for khac, tt in tien_to.items():
                tim = api.search_students(tt)["data"]
                assert (len(tim) > 0) == (khac == slug), (slug, khac)
            # thẻ Quản lý
            assert _ids(api.list_clubs_admin()["data"], "club_id") == set(mong[slug]["clb"])
            sv = api.list_students_admin(page_size=500)["data"]
            assert sv["total"] == len(mong[slug]["hoc_sinh"])
            assert _ids(sv["rows"]) == set(mong[slug]["hoc_sinh"])
            # nguyên trạng thái, đối chiếu từng dòng với lần đầu
            assert _anh_chup(api) == mong[slug]


def test_nhan_va_luat_di_theo_workspace_dang_mo(ba_ws):
    api = ba_ws.api
    # --- nhãn trong tệp xuất và sổ mẫu ---
    mong_trang = {ba_ws.truong: ("Danh sách học sinh", "Theo CLB", "1. CLB", "2. Học sinh"),
                  ba_ws.cty: ("Danh sách nhân viên", "Theo dự án", "1. Dự án", "2. Nhân viên"),
                  ba_ws.sk: ("Danh sách khách", "Theo workshop", "1. Workshop", "2. Khách")}
    for slug in (ba_ws.truong, ba_ws.cty, ba_ws.sk, ba_ws.truong, ba_ws.sk):
        _chuyen(ba_ws, slug)
        ds, theo, sh_clb, sh_hs = mong_trang[slug]
        r = api.export_ket_qua()
        assert r["ok"], r["errors"]
        wb = openpyxl.load_workbook(r["data"]["path"])
        assert wb.sheetnames[1:3] == [ds, theo]
        r = api.tao_so_nhap_mau()
        assert openpyxl.load_workbook(r["data"]["path"]).sheetnames[:2] == [sh_clb, sh_hs]
        # --- đọc nhãn thẳng từ API cấu hình ---
        cfg = api.get_workspace_config()["data"]["config"]
        assert cfg["name"] == api.get_workspace_state()["data"]["name"]

    # --- trần nhập liệu: mỗi workspace dùng trần của CHÍNH nó, kể cả sau khi đổi qua lại ---
    for _ in range(2):
        _chuyen(ba_ws, ba_ws.cty)
        r = api.submit_preferences("NV00", ["da1", "da2", "da3", "da4", "da5"])
        assert r["errors"][0]["code"] == "pref_too_many" and r["errors"][0]["params"]["tran"] == 4
        r = api.submit_test_selection("NV00", ["da1", "da2", "da3"])
        assert r["errors"][0]["code"] == "thi_too_many" and r["errors"][0]["params"]["tran"] == 2
        _chuyen(ba_ws, ba_ws.sk)
        r = api.submit_preferences("K00", ["w1_1", "w1_2", "w1_3"])
        assert r["errors"][0]["code"] == "max_pref_moi_buoi" and r["errors"][0]["params"]["tran"] == 2
        r = api.submit_test_selection("K00", ["w1_1"])
        assert r["errors"][0]["params"]["tran"] == 0
        _chuyen(ba_ws, ba_ws.truong)
        r = api.submit_preferences("HS001", ["clb_amnhac"] * 2)
        assert r["errors"][0]["code"] == "duplicate_preference_in_list"      # không phải lỗi trần
        assert api._tran_nguyen_vong() == 10 and api._tran_thi() == 5

    # --- thẻ Chấm điểm: điểm theo người chỉ có ở công ty ---
    _chuyen(ba_ws, ba_ws.cty)
    r = api.get_person_scoring_list()
    assert r["ok"] and len(r["data"]["persons"]) == 24
    for slug in (ba_ws.truong, ba_ws.sk):
        _chuyen(ba_ws, slug)
        assert api.get_person_scoring_list()["errors"][0]["code"] == "scoring_not_per_person"
    _chuyen(ba_ws, ba_ws.cty)
    assert not api.submit_club_scores("da1", [])["ok"]


def test_tep_sinh_ra_nam_trong_thu_muc_cua_workspace_dang_mo(ba_ws):
    goc = ba_ws.goc
    # gốc chỉ có thư mục workspaces/ và ghi chú di trú; không app.db, sao lưu hay CSV lạc ra ngoài
    assert sorted(os.listdir(goc)) == ["DA_CHUYEN_SANG_WORKSPACES.txt", "workspaces"]
    assert sorted(os.listdir(os.path.join(goc, "workspaces"))) == sorted(
        [ba_ws.truong, ba_ws.cty, ba_ws.sk])

    dem = {}
    for slug in (ba_ws.truong, ba_ws.cty, ba_ws.sk):
        thu_muc = os.path.join(goc, "workspaces", slug)
        ten = os.listdir(thu_muc)
        assert "app.db" in ten and "match_results.csv" in ten, (slug, ten)
        assert any(t.startswith("app.db.bak-") for t in ten)
        dem[slug] = sum(1 for t in ten if t.startswith("app.db.bak-"))

    # sao lưu mới chỉ rơi vào workspace đang mở
    for slug in (ba_ws.cty, ba_ws.truong, ba_ws.sk):
        api = _chuyen(ba_ws, slug)
        moi = api._backup_db()
        assert os.path.dirname(moi) == os.path.join(goc, "workspaces", slug)
        dem[slug] += 1
        for khac in dem:
            n = sum(1 for t in os.listdir(os.path.join(goc, "workspaces", khac))
                    if t.startswith("app.db.bak-"))
            assert n == dem[khac], (slug, khac)
        assert sorted(os.listdir(goc)) == ["DA_CHUYEN_SANG_WORKSPACES.txt", "workspaces"]

    # match_results.csv của mỗi workspace chỉ có học sinh của nó
    tien_to = {ba_ws.truong: "HS", ba_ws.cty: "NV", ba_ws.sk: "K"}
    for slug, tt in tien_to.items():
        with open(os.path.join(goc, "workspaces", slug, "match_results.csv"), encoding="utf-8-sig") as f:
            dong = list(csv.reader(f))
        ma = {d[0] for d in dong[1:] if d}
        assert ma and all(m.startswith(tt) for m in ma), (slug, sorted(ma)[:5])


def test_on_dinh_tren_ket_qua_da_luu_cua_ca_ba_workspace(ba_ws):
    for slug in (ba_ws.truong, ba_ws.cty, ba_ws.sk):
        api = _chuyen(ba_ws, slug)
        giong, van_de, n = _dung_ket_qua_da_luu(api)
        assert giong, "%s: kết quả lưu khác kết quả chạy lại từ cùng dữ liệu" % slug
        assert van_de == [], (slug, van_de)
        assert n > 0
        # báo cáo sức khoẻ dữ liệu không có cảnh báo mức cao sau khi chạy
        bao = api.get_data_health_report()["data"]
        assert bao["n_high"] == 0, (slug, bao["warnings"])


def test_nhom_cung_that_su_xep_theo_nhom_o_cong_ty(ba_ws):
    """Hạng nhóm đứng TRƯỚC điểm: không ai được xét sau một người nhóm kém hơn ở cùng dự án mà
    họ đã đặt nguyện vọng, trừ khi họ đã được suất tốt hơn (nguyện vọng cao hơn)."""
    api = _chuyen(ba_ws, ba_ws.cty)
    luat = api._luat_nghiem()
    (hs, clb, diem, ung_vien, nv, stb), _ = rp.load_from_sqlite_kem_dau_van_tay(api.db_path, luat)
    hang = rp.tham_so_luat(luat, hs)["tier_rank"]
    assert set(hang) == set(hs)                       # ai cũng có nhóm khớp luật
    with api._ket_noi_doc() as cur:
        xep = {r[0]: r[1] for r in cur.execute("SELECT student_id, club_id FROM match_results")}
    for sid, cid in xep.items():
        if cid is None:
            continue
        thu_hang = nv[sid].index(cid)
        # người nhóm kém hơn đang giữ suất mà sid muốn hơn suất hiện tại? Nếu có, sid là cặp phá vỡ.
        for khac, c2 in xep.items():
            if c2 in nv[sid][:thu_hang] and hang[khac] > hang[sid]:
                raise AssertionError("%s (nhóm %d) thua %s (nhóm %d) ở %s dù thích hơn" % (
                    sid, hang[sid], khac, hang[khac], c2))


def test_chay_lai_mot_workspace_khong_dong_toi_hai_cai_con_lai(tmp_path):
    goc, api, truong, cty, sk = _dung_ba_workspace(tmp_path)
    truoc = {slug: _anh_chup(_chuyen(SimpleNamespace(api=api, goc=goc), slug))
             for slug in (truong, sk)}
    def bam(slug):
        with open(ws.duong_dan_db(goc, slug), "rb") as f:
            return hashlib.sha256(f.read()).hexdigest()

    bam_db = {slug: bam(slug) for slug in (truong, sk)}

    api.open_workspace(cty)
    assert api.create_student_if_missing("NV99", "Nhân viên mới")["ok"]
    assert api.submit_preferences("NV99", ["da1", "da2"])["ok"]
    r = api.run_pipeline(seed=5)
    assert r["ok"], r
    with api._ket_noi_doc() as cur:
        assert cur.execute("SELECT COUNT(*) FROM match_results WHERE student_id='NV99'").fetchone()[0] == 1
        assert cur.execute("SELECT COUNT(*) FROM run_history").fetchone()[0] == 2

    for slug in (truong, sk):
        assert bam(slug) == bam_db[slug]
        assert _anh_chup(_chuyen(SimpleNamespace(api=api, goc=goc), slug)) == truoc[slug]
        assert len(api.get_run_history()["data"]) == 1
