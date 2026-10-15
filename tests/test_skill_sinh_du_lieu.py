# -*- coding: utf-8 -*-
"""Canh bộ sinh dữ liệu đầu vào của skill `sinh-du-lieu-clb`.

Một bộ sinh dữ liệu mà sinh ra dữ liệu phần mềm không nuốt được thì tệ hơn
không có: người dùng tin nó, mang bộ dữ liệu đi, rồi mới phát hiện hỏng ở
bước nhập — lúc đó không biết lỗi ở bộ sinh hay ở tay mình.

Nên phép kiểm ở đây KHÔNG phải là "đoạn mã chạy không lỗi". Phép kiểm là
**nhập bộ nó vừa sinh vào chính phần mềm, và đếm cảnh báo**. Tiêu chuẩn: 0
cảnh báo khi nhập, 0 cảnh báo sức khoẻ dữ liệu, chạy phân bổ được.

BA BẢO ĐẢM của bộ sinh, và ĐỐI CHỨNG NGƯỢC cho từng cái — đã chạy thật:

| Bỏ bảo đảm nào | Kết quả |
|---|---|
| chỉ gán nhóm dự trữ mà **có câu lạc bộ đặt suất** | 3 test ĐỎ (`csv_reserve_group_unknown`, `health_orphan_student_group`) |
| mỗi em **ít nhất một nguyện vọng** cả tuần | 2 test ĐỎ (`health_student_no_preferences`) |
| nhóm nào có câu lạc bộ đặt suất thì **phải có người** | 1 test ĐỎ (`health_club_group_no_students`) |

Cả ba lỗi đó **không lỗi cú pháp, không ném exception, không sai lược đồ**.
Chỉ phép kiểm "nhập vào phần mềm thật rồi đếm cảnh báo" mới thấy chúng — đó
là lý do tệp này không kiểm bằng cách đọc CSV mà kiểm bằng cách chạy phần mềm.
"""

import base64
import importlib.util
import io
import json
import os
import re
import sys

import pytest

openpyxl = pytest.importorskip("openpyxl")

GOC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(GOC, ".claude", "skills", "sinh-du-lieu-clb",
                      "scripts", "sinh_du_lieu.py")


@pytest.fixture(scope="module")
def sdl():
    """Nạp đoạn mã của skill như một module."""
    if not os.path.exists(SCRIPT):
        pytest.skip("khong thay script cua skill")
    spec = importlib.util.spec_from_file_location("sinh_du_lieu", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _nhap_va_dem_canh_bao(api, thu_muc):
    """Nạp Sổ nhập CLB qua đúng cửa giao diện dùng.
    Trả (tổng cảnh báo khi nhập, cảnh báo sức khoẻ dữ liệu)."""
    with open(os.path.join(thu_muc, "SO_NHAP_CLB.xlsx"), "rb") as f:
        kq = api.import_so_nhap(base64.b64encode(f.read()).decode())
    assert kq["ok"], kq
    tong = len(kq["data"].get("warnings") or [])
    # Bo qua DUNG MOT ma: buoi it cho hon so em xep buoi do. Do la su that
    # ve do choi, khong phai loi du lieu — bo sinh ra co y chat cho de ket qua
    # co nghia. Loc theo MA chu khong theo muc "info": loc theo muc thi moi
    # canh bao "info" them sau nay cung lot qua ma khong ai hay.
    canh_bao = api.get_data_health_report()["data"]["warnings"]
    return tong, sum(1 for w in canh_bao
                     if w["code"] != "health_oversubscribed_buoi")


# ------------------------------------------------------------------ #
# PHÉP KIỂM CHÍNH: phần mềm thật có nuốt được không
# ------------------------------------------------------------------ #

# Bon cau hinh chon co chu y, khong phai chon bua:
#   - truong TI HON (12 em): moi loi "nhom mo coi" deu lo ra o day, vi xac
#     suat 22% gan nhom tren 12 em rat de boc ra thieu mot nhom;
#   - truong mot buoi: nhanh `pref_N` khac han nhanh `<buoi>_pref_N`;
#   - truong 6 buoi: nhieu buoi nhat, nhieu cau lac bo nhat;
#   - truong 200 em: kich thuoc that.
# Da quet rong hon truoc khi chot: 160 cau hinh (12/20/60/200 em x 5 cach
# chia buoi x 2-3 CLB moi buoi x 4 hat giong) — 0 cau hinh hong.
@pytest.mark.parametrize("n_hs,ds_buoi,seed", [
    (12, ["thu_2", "thu_4"], 99),
    (40, [""], 5),
    (90, ["thu_2", "thu_3", "thu_4", "thu_5", "thu_6", "thu_7"], 7),
    (200, ["thu_2", "thu_4", "thu_6"], 42),
    # Cau hinh nay co mat vi MOT ly do: no la cau hinh duy nhat trong 160 cau
    # da quet lam lo bao dam "nhom nao co cau lac bo dat suat thi phai co
    # nguoi". 20 em x 22% co nhom, boc ra toan mot nhom -> ba cau lac bo giu
    # cho cho mot dien khong ai thuoc. Bo cau hinh nay di la bao dam do het
    # duoc canh.
    (20, ["thu_2", "thu_3", "thu_4", "thu_5", "thu_6", "thu_7"], 99),
])
def test_bo_ngau_nhien_nhap_sach(sdl, api, tmp_path, n_hs, ds_buoi, seed):
    """Phép kiểm thật: nhập vào phần mềm và đếm cảnh báo."""
    clb, hs = sdl.sinh_ngau_nhien(n_hs, ds_buoi, 3, seed)
    assert sdl.soat(clb, hs) == []
    ra = str(tmp_path / "bo")
    sdl.ghi_bo(ra, clb, hs)

    n_nhap, n_suc_khoe = _nhap_va_dem_canh_bao(api, ra)
    assert n_nhap == 0, "sinh ra du lieu lam phan mem canh bao khi nhap"
    assert n_suc_khoe == 0

    kq = api.run_pipeline(seed=42)
    assert kq["ok"], kq
    qua = [c for c in api.get_club_fill_stats()["data"]
           if c["matched"] > c["capacity"]]
    assert qua == []


def test_truong_mot_buoi_cung_nhap_sach(sdl, api, tmp_path):
    """Trường một buổi: cột Buổi của sổ để trống hết."""
    clb, hs = sdl.sinh_ngau_nhien(40, [""], 3, seed=5)
    ra = str(tmp_path / "bo1")
    assert sdl.ghi_bo(ra, clb, hs) == [os.path.join(ra, "SO_NHAP_CLB.xlsx")]
    assert os.listdir(ra) == ["SO_NHAP_CLB.xlsx"], "chi duoc ghi MOT tep"

    clb_doc, hs_doc = sdl.doc_bo(ra)
    assert {c["buoi"] for c in clb_doc} == {""}, "truong mot buoi khong duoc co buoi"
    assert len(hs_doc) == 40

    n_nhap, n_suc_khoe = _nhap_va_dem_canh_bao(api, ra)
    assert (n_nhap, n_suc_khoe) == (0, 0)


def test_cung_hat_giong_cho_ra_cung_bo(sdl):
    """Tất định — nếu không thì không tái lập được một lần đo nào."""
    a = sdl.sinh_ngau_nhien(30, ["thu_2", "thu_4"], 2, seed=9)
    b = sdl.sinh_ngau_nhien(30, ["thu_2", "thu_4"], 2, seed=9)
    assert a == b


# ------------------------------------------------------------------ #
# BỘ SOÁT: bắt được cái gì
# ------------------------------------------------------------------ #

def test_soat_bat_ma_clb_khong_co_that(sdl):
    clb = [{"club_id": "clb_a", "name": "A", "capacity": 5,
            "reserve_capacity": 0, "reserve_group": "", "buoi": "thu_2"}]
    hs = [{"student_id": "HS1", "name": "X", "reserve_group": "",
           "nguyen_vong": {"thu_2": ["clb_khong_co"]}, "diem": {}}]
    loi = sdl.soat(clb, hs)
    assert any("clb_khong_co" in e for e in loi), loi


def test_soat_bat_clb_nam_sai_cot_buoi(sdl):
    clb = [{"club_id": "clb_a", "name": "A", "capacity": 5,
            "reserve_capacity": 0, "reserve_group": "", "buoi": "thu_4"}]
    hs = [{"student_id": "HS1", "name": "X", "reserve_group": "",
           "nguyen_vong": {"thu_2": ["clb_a"]}, "diem": {}}]
    assert any("thu_2" in e and "thu_4" in e for e in sdl.soat(clb, hs))


def test_soat_bat_hai_tran_moi_buoi(sdl):
    clb = [{"club_id": "c%02d" % i, "name": "C", "capacity": 5,
            "reserve_capacity": 0, "reserve_group": "", "buoi": "thu_2"}
           for i in range(12)]
    ma = [c["club_id"] for c in clb]
    hs = [{"student_id": "HS1", "name": "X", "reserve_group": "",
           "nguyen_vong": {"thu_2": ma[:11]},          # 11 > tran 10
           "diem": {c: "8,0" for c in ma[:6]}}]        # 6  > tran 5
    loi = sdl.soat(clb, hs)
    assert any("vượt trần %d" % sdl.TRAN_NGUYEN_VONG_MOI_BUOI in e for e in loi), loi
    assert any("vượt trần %d" % sdl.TRAN_CLB_THI_MOI_BUOI in e for e in loi), loi


def test_soat_bat_diem_cho_clb_em_khong_khai_nguyen_vong(sdl):
    """Điểm không dùng tới — và gần như chắc chắn là gõ lệch cột."""
    clb = [{"club_id": "clb_a", "name": "A", "capacity": 5,
            "reserve_capacity": 0, "reserve_group": "", "buoi": "thu_2"},
           {"club_id": "clb_b", "name": "B", "capacity": 5,
            "reserve_capacity": 0, "reserve_group": "", "buoi": "thu_2"}]
    hs = [{"student_id": "HS1", "name": "X", "reserve_group": "",
           "nguyen_vong": {"thu_2": ["clb_a"]}, "diem": {"clb_b": "8,0"}}]
    assert any("clb_b" in e for e in sdl.soat(clb, hs))


def test_soat_bat_du_tru_lon_hon_suc_chua_va_thieu_nhom(sdl):
    clb = [{"club_id": "clb_a", "name": "A", "capacity": 3,
            "reserve_capacity": 5, "reserve_group": "chinh_sach", "buoi": ""},
           {"club_id": "clb_b", "name": "B", "capacity": 5,
            "reserve_capacity": 2, "reserve_group": "", "buoi": ""}]
    loi = sdl.soat(clb, [])
    assert any("lớn hơn sức chứa" in e for e in loi), loi
    assert any("không ghi nhóm dự trữ" in e for e in loi), loi


def test_soat_bat_khai_buoi_nua_voi(sdl):
    """Khai buổi cho một nửa câu lạc bộ thì nửa kia bị gom chung một buổi."""
    clb = [{"club_id": "clb_a", "name": "A", "capacity": 5,
            "reserve_capacity": 0, "reserve_group": "", "buoi": "thu_2"},
           {"club_id": "clb_b", "name": "B", "capacity": 5,
            "reserve_capacity": 0, "reserve_group": "", "buoi": ""}]
    assert any("khai thì phải khai hết" in e for e in sdl.soat(clb, []))


def test_soat_bat_ma_hoc_sinh_trung(sdl):
    clb = [{"club_id": "clb_a", "name": "A", "capacity": 5,
            "reserve_capacity": 0, "reserve_group": "", "buoi": ""}]
    hs = [{"student_id": "HS1", "name": "X", "reserve_group": "",
           "nguyen_vong": {"": ["clb_a"]}, "diem": {}}] * 2
    assert any("trùng" in e for e in sdl.soat(clb, hs))


# ------------------------------------------------------------------ #
# SAI THÌ KHÔNG GHI TỆP NÀO
# ------------------------------------------------------------------ #

def test_spec_sai_thi_khong_ghi_tep_nao(sdl, tmp_path):
    """Một bộ dữ liệu hỏng còn tệ hơn không có, vì nó trông y như thật."""
    spec = {
        "cau_lac_bo": [{"club_id": "clb_a", "name": "A", "capacity": 0,
                        "reserve_capacity": 0, "reserve_group": "",
                        "buoi": "thu_2"}],
        "hoc_sinh": [{"student_id": "HS1", "name": "X", "reserve_group": "",
                      "nguyen_vong": {"thu_2": ["clb_a"]}, "diem": {}}],
    }
    p = tmp_path / "spec.json"
    with io.open(str(p), "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False)
    ra = tmp_path / "ra"

    ma = sdl.main(["tao", "--spec", str(p), "--ra", str(ra)])
    assert ma != 0, "spec sai ma van tra ve ma thoat 0"
    assert not ra.exists() or list(ra.iterdir()) == [], "da ghi tep du spec sai"


def test_soat_bo_mau_da_kiem_chung(sdl):
    """Bộ `mau_csv/vi_du_day_du/` (cả sổ lẫn bộ ba CSV) phải qua được chính
    bộ soát này — hai thứ nói về cùng một định dạng thì không được mâu thuẫn."""
    bo = os.path.join(GOC, "mau_csv", "vi_du_day_du")
    if not os.path.isdir(bo):
        pytest.skip("chua co bo mau")
    clb, hs = sdl.doc_bo(os.path.join(bo, "SO_NHAP_CLB_vi_du.xlsx"))
    assert sdl.soat(clb, hs) == []
    assert len(clb) == 9 and len(hs) == 24


def test_vong_tron_ghi_roi_doc_lai_so(sdl, tmp_path):
    clb, hs = sdl.sinh_ngau_nhien(30, ["thu_2", "thu_5"], 3, seed=3)
    ra = str(tmp_path / "vt")
    sdl.ghi_bo(ra, clb, hs)
    clb2, hs2 = sdl.doc_bo(ra)
    assert [c["club_id"] for c in clb2] == [c["club_id"] for c in clb]
    goc = {h["student_id"]: h for h in hs}
    for h in hs2:
        g = goc[h["student_id"]]
        assert {b: ds for b, ds in h["nguyen_vong"].items()} == \
            {b: ds for b, ds in g["nguyen_vong"].items() if ds}
        assert set(h["diem"]) == set(g["diem"])


# ------------------------------------------------------------------ #
# SKILL.md phải mô tả đúng đoạn mã đi kèm
# ------------------------------------------------------------------ #

def test_skill_md_neu_dung_hai_tran(sdl):
    p = os.path.join(os.path.dirname(os.path.dirname(SCRIPT)), "SKILL.md")
    with io.open(p, encoding="utf-8") as f:
        s = f.read()
    assert "%d nguyện vọng mỗi buổi" % sdl.TRAN_NGUYEN_VONG_MOI_BUOI in s
    assert "%d câu lạc bộ dự thi mỗi buổi" % sdl.TRAN_CLB_THI_MOI_BUOI in s


def test_tran_trong_skill_khop_voi_tran_cua_phan_mem(sdl):
    """Trần do phần mềm áp, không phải do bộ sinh nghĩ ra. Hai bên trôi khỏi
    nhau thì bộ sinh sẽ đẻ ra dữ liệu bị phần mềm gạt."""
    sys.path.insert(0, GOC)
    import rbda_priority_pipeline as loi
    assert sdl.TRAN_NGUYEN_VONG_MOI_BUOI == loi.TRAN_NGUYEN_VONG_MOI_BUOI
    assert sdl.TRAN_CLB_THI_MOI_BUOI == loi.TRAN_CLB_THI_MOI_BUOI


# ====================================================================== #
# WORKSPACE (--cau-hinh / --kich-ban): nhãn, luật, hai kịch bản dựng sẵn
# ====================================================================== #
#
# Ba điều phải giữ:
#   1. KHÔNG truyền cấu hình thì đầu ra y hệt bản trước khi có workspace (so với ảnh chụp
#      tests/du_lieu_ws/sinh_du_lieu_truoc_cau_hinh.json, chụp từ bản cũ);
#   2. cùng seed -> cùng dữ liệu, và có cấu hình thì cùng TỪNG BYTE;
#   3. mọi sổ sinh ra nhập vào một workspace mang đúng cấu hình đó với 0 lỗi, 0 cảnh báo khi nhập,
#      0 cảnh báo sức khoẻ dữ liệu (trừ `health_oversubscribed_buoi`), và chạy xếp được.

import hashlib  # noqa: E402
import subprocess  # noqa: E402
import zipfile  # noqa: E402

import cau_hinh_ws  # noqa: E402
import workspace  # noqa: E402
from api import PipelineAPI  # noqa: E402

ANH_CHUP = os.path.join(GOC, "tests", "du_lieu_ws", "sinh_du_lieu_truoc_cau_hinh.json")
BO_DUNG_SAN = {"company": "bo_cong_ty", "event": "bo_su_kien"}


def _chay_cli(*args, cwd=None):
    r = subprocess.run([sys.executable, SCRIPT] + [str(a) for a in args], capture_output=True,
                       text=True, encoding="utf-8", cwd=cwd)
    return r


def _bam_xlsx(duong, bo_gio=True):
    """{tên mục: sha256} của một .xlsx; `bo_gio` bỏ docProps/core.xml (giờ ghi tệp)."""
    with zipfile.ZipFile(duong) as z:
        return {n: hashlib.sha256(z.read(n)).hexdigest() for n in sorted(z.namelist())
                if not (bo_gio and n == "docProps/core.xml")}


# ---------------------------------------------------------------- 1. mặc định không đổi

def test_khong_cau_hinh_thi_dau_ra_y_het_ban_truoc_khi_co_workspace(tmp_path):
    """Ba lần chạy chụp từ bản cũ: từng mục của .xlsx (trừ giờ ghi tệp) và cả chữ in ra."""
    with io.open(ANH_CHUP, encoding="utf-8") as f:
        truoc = json.load(f)
    assert len(truoc) == 3
    for lenh, mong in truoc.items():
        args = lenh.split()
        ra = str(tmp_path / ("ra%d" % abs(hash(lenh))))
        r = _chay_cli(args[0], "--ra", ra, *args[1:])
        assert r.returncode == 0, r.stderr
        that = {"stdout": r.stdout.replace(ra, "<RA>"),
                **_bam_xlsx(os.path.join(ra, "SO_NHAP_CLB.xlsx"))}
        assert that == mong, lenh
        assert os.listdir(ra) == ["SO_NHAP_CLB.xlsx"]          # không config.json lạc vào


def test_cau_hinh_truong_hoc_ro_rang_cung_ra_dung_bo_cu(tmp_path, sdl):
    """`--cau-hinh` trỏ tới cấu hình Y HỆT trường học (hay rỗng {}) là cùng bộ, cùng nội dung sổ."""
    for i, noi_dung in enumerate(({}, cau_hinh_ws.MAC_DINH_TRUONG_HOC)):
        p = tmp_path / ("truong%d.json" % i)
        p.write_text(json.dumps(noi_dung), encoding="utf-8")
        a, b = str(tmp_path / ("a%d" % i)), str(tmp_path / ("b%d" % i))
        assert _chay_cli("ngau", "--ra", a, "--hoc-sinh", "40", "--seed", "5").returncode == 0
        assert _chay_cli("ngau", "--ra", b, "--hoc-sinh", "40", "--seed", "5",
                         "--cau-hinh", p).returncode == 0
        assert _bam_xlsx(os.path.join(a, "SO_NHAP_CLB.xlsx")) == \
            _bam_xlsx(os.path.join(b, "SO_NHAP_CLB.xlsx"))


# ---------------------------------------------------------------- 2. tất định

@pytest.mark.parametrize("kich_ban", ["company", "event"])
def test_cung_seed_cung_tung_byte_voi_cau_hinh(tmp_path, kich_ban):
    ra = [str(tmp_path / ("lan%d" % i)) for i in range(3)]
    for i, seed in enumerate((7, 7, 8)):
        r = _chay_cli("ngau", "--kich-ban", kich_ban, "--hoc-sinh", "60", "--seed", seed,
                      "--ra", ra[i])
        assert r.returncode == 0, r.stderr
    tep = lambda d: open(os.path.join(d, "SO_NHAP_CLB.xlsx"), "rb").read()      # noqa: E731
    assert tep(ra[0]) == tep(ra[1])                      # CÙNG TỪNG BYTE, kể cả giờ ghi tệp
    assert tep(ra[0]) != tep(ra[2])                      # seed khác thì khác
    cfg = lambda d: open(os.path.join(d, "config.json"), "rb").read()           # noqa: E731
    assert cfg(ra[0]) == cfg(ra[1]) == cfg(ra[2])        # cấu hình không phụ thuộc seed


@pytest.mark.parametrize("kich_ban", ["company", "event"])
def test_cung_seed_cung_du_lieu_trong_bo_nho(sdl, kich_ban):
    cfg, _ = sdl.chuan_hoa_cau_hinh(sdl.KICH_BAN[kich_ban]["cau_hinh"])
    kb = sdl.KICH_BAN[kich_ban]
    ds = [x for x in kb["buoi"].split(",") if x] or [""]

    def sinh(seed):
        return sdl.sinh_theo_cau_hinh(cfg, 80, ds, kb["clb_moi_buoi"], seed,
                                      tien_to_ma=kb["tien_to_ma"])
    assert sinh(11) == sinh(11) and sinh(11) != sinh(12)


# ---------------------------------------------------------------- 3. nhập sạch vào workspace khớp

def _tao_workspace(tmp_path, cfg, ten="Thử"):
    goc = str(tmp_path / "goc")
    os.makedirs(goc, exist_ok=True)
    slug = workspace.tao(goc, ten, cfg)
    xuat = str(tmp_path / "xuat")
    os.makedirs(xuat, exist_ok=True)
    return PipelineAPI(workspace.duong_dan_db(goc, slug), thu_muc_xuat=xuat, thu_muc_goc_ws=goc)


def _nhap_sach_va_chay(api, duong_so):
    """Nhập sổ vào workspace: 0 lỗi, 0 cảnh báo nhập, 0 cảnh báo sức khoẻ (trừ độ chọi), chạy được."""
    with open(duong_so, "rb") as f:
        kq = api.import_so_nhap(base64.b64encode(f.read()).decode())
    assert kq["ok"], kq["errors"]
    assert (kq["data"].get("warnings") or []) == []
    canh_bao = [w["code"] for w in api.get_data_health_report()["data"]["warnings"]
                if w["code"] != "health_oversubscribed_buoi"]
    assert canh_bao == []
    r = api.run_pipeline(seed=42)
    assert r["ok"], r
    return kq["data"]


def _rules(**r):
    return {"max_choices": 3, "max_tests": 2, **r}


# Mỗi dòng: một HỌ cấu hình có chủ ý, không phải ngẫu nhiên.
CAU_HINH_KHAC = {
    # nhãn riêng, vẫn điểm theo chỗ, không giới hạn thi
    "diem_theo_cho_khong_gioi_han_thi": {
        "industry": "custom",
        "labels": {"person": {"vi": "Học viên", "en": "Trainee"},
                   "slot": {"vi": "Lớp", "en": "Class"}, "score": {"vi": "Điểm thi", "en": "Exam"}},
        "rules": _rules(max_choices=5, max_tests=None)},
    # điểm theo chỗ, chỉ cho thi tối đa 1
    "diem_theo_cho_thi_1": {"industry": "custom", "rules": _rules(max_choices=2, max_tests=1)},
    # không ai được thi
    "khong_ai_thi": {"industry": "custom", "rules": _rules(max_tests=0)},
    # điểm theo người nhưng nhóm là suất dự trữ mềm (tiers không dùng)
    "diem_theo_nguoi_du_tru_mem": {
        "industry": "company",
        "labels": {"person": {"vi": "Nhân viên", "en": "Employee"}, "score": {"vi": "KPI", "en": "KPI"}},
        "rules": _rules(score_scope="per_person", tiers=["A", "B"])},
    # điểm theo người + nhóm cứng 3 hạng
    "diem_theo_nguoi_nhom_cung": {
        "industry": "company",
        "rules": _rules(priority="score+tier", tier_mode="strict", score_scope="per_person",
                        tiers=["Quản lý", "Chuyên viên", "Nhân viên mới"])},
    # điểm theo chỗ + nhóm cứng (hạng đứng trước điểm từng chỗ)
    "diem_theo_cho_nhom_cung": {
        "industry": "custom",
        "rules": _rules(priority="score", tier_mode="strict", tiers=["Khối 12", "Khối 11"])},
    # chỉ theo nhóm, hai hạng, một nguyện vọng
    "chi_theo_nhom_hai_hang": {
        "industry": "event", "rules": _rules(max_choices=1, priority="tier", tiers=["VIP", "Thường"])},
    # chỉ theo nhóm, năm hạng
    "chi_theo_nhom_nam_hang": {
        "industry": "event",
        "rules": _rules(priority="tier", tiers=["Kim cương", "Vàng", "Bạc", "Đồng", "Phổ thông"])},
    # chỉ theo nhóm nhưng khai điểm theo người (vô nghĩa, bị bỏ qua)
    "chi_theo_nhom_diem_theo_nguoi": {
        "industry": "event", "rules": _rules(priority="tier", score_scope="per_person",
                                             tiers=["VIP", "Khách"])},
}


@pytest.mark.parametrize("ten", sorted(CAU_HINH_KHAC))
@pytest.mark.parametrize("ds_buoi", [[""], ["thu_2", "thu_4", "thu_6"]], ids=["mot_buoi", "ba_buoi"])
def test_so_sinh_theo_cau_hinh_nhap_sach_vao_workspace_khop(tmp_path, sdl, ten, ds_buoi):
    cfg, loi = sdl.chuan_hoa_cau_hinh(CAU_HINH_KHAC[ten])
    assert not loi, loi
    clb, hs = sdl.sinh_theo_cau_hinh(cfg, 90, ds_buoi, 4, seed=31)
    assert sdl.soat(clb, hs, cfg) == []
    [duong] = sdl.ghi_bo(str(tmp_path / "bo"), clb, hs, cfg, co_dinh=True)

    # đọc lại bằng chính bộ đọc của skill, với cấu hình
    clb2, hs2 = sdl.doc_bo(duong, cfg)
    assert [c["club_id"] for c in clb2] == [c["club_id"] for c in clb] and len(hs2) == len(hs)
    assert sdl.soat(clb2, hs2, cfg) == []

    api = _tao_workspace(tmp_path, cfg)
    _nhap_sach_va_chay(api, duong)


@pytest.mark.parametrize("kich_ban", ["company", "event"])
def test_kich_ban_dung_san_dung_quy_mo_va_nhap_sach(tmp_path, sdl, kich_ban):
    ra = str(tmp_path / "bo")
    r = _chay_cli("ngau", "--kich-ban", kich_ban, "--ra", ra, "--ten-tep", "SO_NHAP.xlsx")
    assert r.returncode == 0, r.stderr
    assert sorted(os.listdir(ra)) == ["SO_NHAP.xlsx", "config.json"]

    with io.open(os.path.join(ra, "config.json"), encoding="utf-8") as f:
        cfg = json.load(f)
    # cấu hình ghi ra là cấu hình ĐẦY ĐỦ, và phần mềm nhận nó y nguyên
    assert cfg == cau_hinh_ws.chuan_hoa(cfg)
    assert cfg == sdl.chuan_hoa_cau_hinh(cfg)[0]

    clb, hs = sdl.doc_bo(os.path.join(ra, "SO_NHAP.xlsx"), cfg)
    assert sdl.soat(clb, hs, cfg) == []
    nhom = {}
    for h in hs:
        nhom[h["reserve_group"]] = nhom.get(h["reserve_group"], 0) + 1
    if kich_ban == "company":
        assert (len(hs), len(clb)) == (300, 12) and {c["buoi"] for c in clb} == {""}
        assert cfg["rules"]["tiers"] == ["Senior", "Mid", "Junior"]
        assert nhom == {"Senior": 30, "Mid": 90, "Junior": 180}              # 10% / 30% / 60%
        kpi = [h["diem_ca_nhan"] for h in hs]
        assert len(kpi) == 300 and all(0 <= x <= 100 for x in kpi) and len(set(kpi)) > 100
        assert all(not h["diem"] for h in hs)                                # KHÔNG điểm từng chỗ
        assert cfg["rules"]["score_scope"] == "per_person" and cfg["rules"]["tier_mode"] == "strict"
        assert max(len(ds) for h in hs for ds in h["nguyen_vong"].values()) <= 3
    else:
        assert (len(hs), len(clb)) == (800, 24)
        assert sorted({c["buoi"] for c in clb}) == ["phien_1", "phien_2", "phien_3"]
        assert all(sum(1 for c in clb if c["buoi"] == b) == 8 for b in {c["buoi"] for c in clb})
        assert cfg["rules"]["tiers"] == ["VIP", "Member", "Guest"] and cfg["rules"]["priority"] == "tier"
        assert nhom == {"VIP": 80, "Member": 240, "Guest": 480}
        assert all(not h["diem"] and "diem_ca_nhan" not in h for h in hs)    # KHÔNG điểm nào
        assert max(len(ds) for h in hs for ds in h["nguyen_vong"].values()) <= 2
    # tên người và tên chỗ bằng tiếng Việt, lấy từ bảng tên sẵn có
    assert all(h["name"].split()[0] in sdl._HO for h in hs)
    assert all(re.search(r"[À-ỹ]", c["name"]) or c["name"].isascii() for c in clb)

    api = _tao_workspace(tmp_path, cfg, cfg["name"])
    _nhap_sach_va_chay(api, os.path.join(ra, "SO_NHAP.xlsx"))
    # nhãn nằm đúng trong sổ: tên sheet và tiêu đề cột theo workspace
    wb = openpyxl.load_workbook(os.path.join(ra, "SO_NHAP.xlsx"))
    ten_ba = {"company": ("1. Dự án", "2. Nhân viên", ["Mã HS", "Họ tên", "Cấp bậc", "KPI", "NV1"]),
              "event": ("1. Workshop", "2. Khách tham dự", ["Mã HS", "Họ tên", "Hạng vé", "NV1"])}
    s1, s2, dau = ten_ba[kich_ban]
    assert wb.sheetnames[:2] == [s1, s2]
    assert [c.value for c in wb[s2][1]][:len(dau)] == dau


@pytest.mark.parametrize("kich_ban", ["company", "event"])
def test_bo_du_lieu_da_commit_la_dung_dau_ra_cua_lenh_ghi_trong_readme(tmp_path, kich_ban):
    """`du_lieu_test/bo_cong_ty` và `bo_su_kien` tái lập ĐÚNG TỪNG BYTE bằng lệnh trong README
    (xlsx đã được ghi tất định), và README là một đoạn mô tả mô phỏng + cách nạp."""
    thu_muc = os.path.join(GOC, "du_lieu_test", BO_DUNG_SAN[kich_ban])
    assert sorted(os.listdir(thu_muc)) == ["README.md", "SO_NHAP.xlsx", "config.json"]
    readme = io.open(os.path.join(thu_muc, "README.md"), encoding="utf-8").read()
    lenh = re.search(r"`python (\.claude/skills/sinh-du-lieu-clb/scripts/sinh_du_lieu\.py [^`]+)`", readme)
    assert lenh, "README phải ghi lệnh sinh lại"
    args = lenh.group(1).split()[1:]
    assert args[args.index("--kich-ban") + 1] == kich_ban
    assert "MÔ PHỎNG" in readme and "SO_NHAP.xlsx" in readme and "config.json" in readme

    ra = str(tmp_path / "lai")
    args[args.index("--ra") + 1] = ra
    r = _chay_cli(*args)
    assert r.returncode == 0, r.stderr
    for t in ("SO_NHAP.xlsx", "config.json"):
        assert open(os.path.join(ra, t), "rb").read() == open(os.path.join(thu_muc, t), "rb").read(), t


# ---------------------------------------------------------------- soát theo luật workspace

def _clb(cid, buoi=""):
    return {"club_id": cid, "name": cid, "capacity": 5, "reserve_capacity": 0,
            "reserve_group": "", "buoi": buoi}


def _hs(sid, nv, diem=None, nhom="", **them):
    return {"student_id": sid, "name": "X", "reserve_group": nhom,
            "nguyen_vong": {"": nv}, "diem": diem or {}, **them}


def _cfg(sdl, **luat):
    cfg, loi = sdl.chuan_hoa_cau_hinh({"rules": luat})
    assert not loi, loi
    return cfg


def test_soat_theo_tran_cua_workspace_thay_vi_10_va_5(sdl):
    clb = [_clb("c%02d" % i) for i in range(12)]
    ma = [c["club_id"] for c in clb]
    em = _hs("A", ma[:4], {c: "8,0" for c in ma[:3]})
    assert sdl.soat(clb, [em]) == []                                   # trường học: 4 NV, 3 thi: được
    loi = sdl.soat(clb, [em], _cfg(sdl, max_choices=3, max_tests=2))
    assert any("vượt trần 3" in e for e in loi) and any("vượt trần 2" in e for e in loi), loi
    # không giới hạn thi (None): 8 nguyện vọng, 8 bài thi đều được; trần 5 của trường học không áp
    em8 = _hs("B", ma[:8], {c: "8,0" for c in ma[:8]})
    assert sdl.soat(clb, [em8], _cfg(sdl, max_choices=8, max_tests=None)) == []
    assert any("vượt trần 5" in e for e in sdl.soat(clb, [em8]))
    # max_tests = 0: ai dự thi cũng là lỗi
    assert any("vượt trần 0" in e for e in sdl.soat(clb, [_hs("C", ma[:1], {ma[0]: "9"})],
                                                    _cfg(sdl, max_tests=0)))


def test_soat_diem_theo_nguoi_nhom_cung_va_chi_theo_nhom(sdl):
    clb = [_clb("a"), _clb("b")]
    cung = _cfg(sdl, priority="score+tier", tier_mode="strict", score_scope="per_person",
                tiers=["Senior", "Mid"])
    tot = _hs("A", ["a"], nhom="senior", diem_ca_nhan=88.5)       # 'senior' khớp 'Senior' (chuẩn hoá)
    assert sdl.soat(clb, [tot], cung) == []
    assert any("không có trong rules.tiers" in e for e in sdl.soat(clb, [_hs("B", ["a"], nhom="Khac",
                                                                          diem_ca_nhan=1)], cung))
    assert any("không có trong rules.tiers" in e for e in sdl.soat(clb, [_hs("B", ["a"],
                                                                           diem_ca_nhan=1)], cung))
    assert any("điểm theo người" in e for e in sdl.soat(
        clb, [_hs("C", ["a"], {"a": "7"}, "Mid", diem_ca_nhan=5)], cung))      # có điểm từng chỗ
    assert any("không phải số" in e for e in sdl.soat(
        clb, [_hs("D", ["a"], nhom="Mid", diem_ca_nhan="tam")], cung))
    assert any("không phải số" in e for e in sdl.soat(
        clb, [_hs("E", ["a"], nhom="Mid", diem_ca_nhan=-3)], cung))
    # thiếu điểm theo người: không phải lỗi, là cảnh báo mềm
    thieu = _hs("F", ["a"], nhom="Mid")
    assert sdl.soat(clb, [thieu], cung) == []
    assert any("chưa có điểm theo người" in w for w in sdl.canh_bao_men(clb, [thieu], cung))
    # trường học không có điểm theo người
    assert any("không chấm điểm theo người" in e
               for e in sdl.soat(clb, [_hs("G", ["a"], diem_ca_nhan=3)]) + sdl.soat(
                   clb, [_hs("G", ["a"], diem_ca_nhan=3)], _cfg(sdl)))
    # chỉ theo nhóm: điểm bị bỏ qua -> cảnh báo mềm
    tier = _cfg(sdl, priority="tier", tiers=["VIP"])
    assert any("bị bỏ qua" in w for w in sdl.canh_bao_men(
        clb, [_hs("H", ["a"], {"a": "6"}, "VIP")], tier))


def test_cau_hinh_ngu_nghia_nhom_cung_ma_tiers_rong_bi_tu_choi_khi_sinh(sdl):
    cfg, _ = sdl.chuan_hoa_cau_hinh({"rules": {"tier_mode": "strict"}})
    with pytest.raises(SystemExit):
        sdl.sinh_theo_cau_hinh(cfg, 20, [""], 3, seed=1)


# ---------------------------------------------------------------- bản chuẩn hoá cấu hình không lệch phần mềm

HOP_LE = [
    {}, {"name": "  Tên  "}, {"industry": "event"}, {"labels": {"slot": {"vi": "Dự án"}}},
    {"labels": {"person": {"vi": "Khách", "en": "Guest"}, "score": {"vi": "KPI", "en": ""}}},
    {"rules": {"max_choices": 1, "max_tests": None}},
    {"rules": {"max_choices": 20, "max_tests": 0, "priority": "tier", "tiers": ["A", " B "]}},
    {"rules": {"tier_mode": "strict", "score_scope": "per_person", "priority": "score+tier",
               "tiers": ["Quản lý", "Chuyên viên"]}},
]
XAU = [
    [], "x", {"khoa_la": 1}, {"industry": "bank"}, {"name": 5}, {"labels": []}, {"rules": 3},
    {"labels": {"lạ": {"vi": "x"}}}, {"labels": {"slot": {"vi": ""}}}, {"labels": {"slot": "Dự án"}},
    {"labels": {"slot": {"vi": "=SUM(A1)"}}}, {"labels": {"slot": {"vi": "a", "en": "+b"}}},
    {"labels": {"slot": {"vi": "x" * 61}}}, {"labels": {"slot": {"vi": "a", "en": 5}}},
    {"rules": {"max_choices": 0}}, {"rules": {"max_choices": 21}}, {"rules": {"max_choices": "3"}},
    {"rules": {"max_choices": True}}, {"rules": {"max_tests": -1}}, {"rules": {"max_tests": 21}},
    {"rules": {"priority": "x"}}, {"rules": {"tier_mode": "x"}}, {"rules": {"score_scope": "x"}},
    {"rules": {"khoa_la": 1}}, {"rules": {"tiers": "A"}}, {"rules": {"tiers": ["A", ""]}},
    {"rules": {"tiers": ["A", "A"]}}, {"rules": {"tiers": ["Quản lý", "quan_ly"]}},
    {"rules": {"tiers": ["???"]}}, {"rules": {"tiers": ["x" * 61]}},
    {"rules": {"tiers": ["t%d" % i for i in range(51)]}},
]


@pytest.mark.parametrize("cfg", HOP_LE, ids=lambda c: json.dumps(c, ensure_ascii=False)[:50])
def test_chuan_hoa_cau_hinh_cua_skill_cho_dung_ket_qua_cua_phan_mem(sdl, cfg):
    cua_skill, loi = sdl.chuan_hoa_cau_hinh(cfg)
    assert not loi, loi
    assert cua_skill == cau_hinh_ws.chuan_hoa(cfg)


@pytest.mark.parametrize("cfg", XAU, ids=lambda c: json.dumps(c, ensure_ascii=False)[:50])
def test_chuan_hoa_cau_hinh_cua_skill_tu_choi_dung_nhung_gi_phan_mem_tu_choi(sdl, cfg):
    cua_skill, loi = sdl.chuan_hoa_cau_hinh(cfg)
    assert cua_skill is None and loi
    with pytest.raises(ValueError):
        cau_hinh_ws.chuan_hoa(cfg)


def test_khoa_nhom_cua_skill_giong_khoa_cua_thuat_toan(sdl):
    import rbda_priority_pipeline as rp
    for ten in ["Quản lý", "quan_ly", "QUAN  LY", "Khối  12", "khoi-12", "Khối 1 2",
                "A+", "???", "", None, "Đặc biệt", "x_y-z"]:
        assert sdl.khoa_nhom(ten) == rp.khoa_ten_nhom(ten), repr(ten)


# ---------------------------------------------------------------- dòng lệnh

def test_cau_hinh_hong_thi_khong_ghi_tep_nao(tmp_path):
    xau = tmp_path / "xau.json"
    xau.write_text(json.dumps({"rules": {"max_choices": 99}}), encoding="utf-8")
    ra = tmp_path / "ra"
    r = _chay_cli("ngau", "--ra", ra, "--cau-hinh", xau)
    assert r.returncode != 0 and "max_choices" in (r.stderr + r.stdout)
    assert not ra.exists()
    r = _chay_cli("ngau", "--ra", ra, "--cau-hinh", tmp_path / "khong-co.json")
    assert r.returncode != 0 and not ra.exists()


def test_cau_hinh_nhan_ca_tep_mau_cua_phan_mem(tmp_path, sdl):
    """Tệp mẫu do `workspace.luu_mau` ghi ({"name", "config"}) cũng dùng được làm --cau-hinh."""
    goc = str(tmp_path / "goc")
    slug = workspace.tao(goc, "Công ty", sdl.KICH_BAN["company"]["cau_hinh"])
    mau = workspace.luu_mau(goc, slug, "Mẫu công ty")
    cfg = sdl.doc_cau_hinh(mau)
    assert cfg["labels"]["slot"]["vi"] == "Dự án" and cfg["name"] == "Mẫu công ty"
    assert cfg["rules"]["tiers"] == ["Senior", "Mid", "Junior"]


def test_soat_so_cua_workspace_can_dung_cau_hinh(tmp_path, sdl):
    ra = str(tmp_path / "bo")
    assert _chay_cli("ngau", "--kich-ban", "company", "--hoc-sinh", "50", "--ra", ra).returncode == 0
    so, cfg = os.path.join(ra, "SO_NHAP_CLB.xlsx"), os.path.join(ra, "config.json")
    r = _chay_cli("soat", so, "--cau-hinh", cfg)
    assert r.returncode == 0, r.stderr
    assert "50 nhân viên" in r.stdout and "12 dự án" in r.stdout and "KPI theo nhân viên" in r.stdout
    r = _chay_cli("soat", so)                                       # thiếu cấu hình: nói rõ phải làm gì
    assert r.returncode != 0 and "--cau-hinh" in (r.stderr + r.stdout)


def test_ngau_ghi_de_tuy_chon_len_kich_ban(tmp_path):
    ra = str(tmp_path / "bo")
    r = _chay_cli("ngau", "--kich-ban", "event", "--hoc-sinh", "50", "--buoi", "phien_1,phien_2",
                  "--clb-moi-buoi", "4", "--ra", ra)
    assert r.returncode == 0, r.stderr
    assert "8 workshop · 2 phiên · 50 khách tham dự" in r.stdout


def test_skill_md_mo_ta_cau_hinh_va_hai_kich_ban():
    p = os.path.join(os.path.dirname(os.path.dirname(SCRIPT)), "SKILL.md")
    s = io.open(p, encoding="utf-8").read()
    mo_ta = s.split("---")[1]
    for cum in ("dữ liệu công ty", "dữ liệu sự kiện", "workspace"):
        assert cum in mo_ta, cum
    for cum in ("--cau-hinh", "--kich-ban company", "--kich-ban event", "du_lieu_test/bo_cong_ty",
                "du_lieu_test/bo_su_kien", "rules.max_choices", "per_person", "rules.tiers"):
        assert cum in s, cum
