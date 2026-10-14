"""Cấu hình workspace: lưu trong bảng `workspace_settings` của app.db."""

import copy
import sqlite3

import pytest

import cau_hinh_ws as ws
from rbda_priority_pipeline import (
    TRAN_CLB_THI_MOI_BUOI,
    TRAN_NGUYEN_VONG_MOI_BUOI,
    init_db,
)


@pytest.fixture
def db(tmp_path):
    p = str(tmp_path / "app.db")
    init_db(p)
    return p


def _luu_tho(db_path, value):
    conn = sqlite3.connect(db_path)
    conn.execute(
        "INSERT OR REPLACE INTO workspace_settings (key, value) VALUES ('config', ?)",
        (value,),
    )
    conn.commit()
    conn.close()


def _co_bang(db_path):
    conn = sqlite3.connect(db_path)
    try:
        return conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='workspace_settings'"
        ).fetchone() is not None
    finally:
        conn.close()


# ---------- mặc định ----------

def test_mac_dinh_lay_tran_tu_hang_so_thuat_toan():
    r = ws.MAC_DINH_TRUONG_HOC["rules"]
    assert r["max_choices"] == TRAN_NGUYEN_VONG_MOI_BUOI
    assert r["max_tests"] == TRAN_CLB_THI_MOI_BUOI
    assert (r["priority"], r["tier_mode"], r["score_scope"], r["tiers"]) == (
        "score", "reserve", "per_slot", [])


def test_csdl_moi_tra_ve_mac_dinh(db):
    assert _co_bang(db)
    assert ws.doc_cau_hinh(db) == ws.MAC_DINH_TRUONG_HOC


def test_csdl_cu_chua_co_bang_tra_ve_mac_dinh_va_khong_ghi_gi(tmp_path):
    p = str(tmp_path / "cu.db")
    conn = sqlite3.connect(p)
    conn.execute("CREATE TABLE students (student_id TEXT PRIMARY KEY, name TEXT)")
    conn.commit()
    conn.close()
    assert not _co_bang(p)
    assert ws.doc_cau_hinh(p) == ws.MAC_DINH_TRUONG_HOC
    assert not _co_bang(p)  # đọc không có tác dụng phụ


def test_tep_chua_ton_tai_tra_ve_mac_dinh(tmp_path):
    p = tmp_path / "khong_co.db"
    assert ws.doc_cau_hinh(str(p)) == ws.MAC_DINH_TRUONG_HOC
    assert not p.exists()


def test_init_db_tao_bang_trong_csdl_cu(tmp_path):
    p = str(tmp_path / "cu.db")
    init_db(p)
    conn = sqlite3.connect(p)
    conn.execute("DROP TABLE workspace_settings")
    conn.commit()
    conn.close()
    assert not _co_bang(p)
    init_db(p)
    assert _co_bang(p)
    init_db(p)  # idempotent


def test_ghi_vao_csdl_cu_tu_tao_bang(tmp_path):
    p = str(tmp_path / "cu.db")
    conn = sqlite3.connect(p)
    conn.execute("CREATE TABLE students (student_id TEXT PRIMARY KEY, name TEXT)")
    conn.commit()
    conn.close()
    ws.ghi_cau_hinh(p, {"name": "Công ty A"})
    assert ws.doc_cau_hinh(p)["name"] == "Công ty A"


def test_doc_tra_ban_sao_khong_dong_vao_mac_dinh(db):
    cfg = ws.doc_cau_hinh(db)
    cfg["rules"]["tiers"].append("x")
    cfg["labels"]["person"]["vi"] = "Sửa"
    assert ws.MAC_DINH_TRUONG_HOC["rules"]["tiers"] == []
    assert ws.doc_cau_hinh(db) == ws.MAC_DINH_TRUONG_HOC


# ---------- ghi / đọc ----------

def test_khu_hoi_ghi_roi_doc(db):
    cfg = copy.deepcopy(ws.MAC_DINH_TRUONG_HOC)
    cfg.update(name="Hội chợ việc làm", industry="event")
    cfg["labels"]["person"] = {"vi": "Ứng viên", "en": "Candidate"}
    cfg["rules"].update(
        max_choices=3, max_tests=None, priority="tier", tier_mode="strict",
        score_scope="per_person", tiers=["Hạng A", "Hạng B"])
    ghi = ws.ghi_cau_hinh(db, cfg)
    assert ghi == cfg
    assert ws.doc_cau_hinh(db) == cfg


def test_ghi_de_len_lan_truoc(db):
    ws.ghi_cau_hinh(db, {"name": "A"})
    ws.ghi_cau_hinh(db, {"name": "B"})
    assert ws.doc_cau_hinh(db)["name"] == "B"
    conn = sqlite3.connect(db)
    n = conn.execute("SELECT COUNT(*) FROM workspace_settings").fetchone()[0]
    conn.close()
    assert n == 1


def test_max_tests_none_giu_nguyen_qua_json(db):
    ws.ghi_cau_hinh(db, {"rules": {"max_tests": None}})
    assert ws.doc_cau_hinh(db)["rules"]["max_tests"] is None


def test_cau_hinh_mot_phan_tron_voi_mac_dinh(db):
    _luu_tho(db, '{"rules": {"max_choices": 4}, "labels": {"slot": {"vi": "Dự án"}}}')
    cfg = ws.doc_cau_hinh(db)
    assert cfg["rules"]["max_choices"] == 4
    assert cfg["rules"]["max_tests"] == TRAN_CLB_THI_MOI_BUOI
    assert cfg["rules"]["priority"] == "score"
    assert cfg["labels"]["slot"] == {"vi": "Dự án", "en": "Club"}
    assert cfg["labels"]["person"] == {"vi": "Học sinh", "en": "Student"}
    assert cfg["industry"] == "school"


def test_ghi_mot_phan_duoc_dien_day_bang_mac_dinh(db):
    ghi = ws.ghi_cau_hinh(db, {"rules": {"max_choices": 7}})
    assert ghi["rules"]["max_choices"] == 7
    assert ghi["rules"]["max_tests"] == TRAN_CLB_THI_MOI_BUOI
    assert ghi["labels"] == ws.MAC_DINH_TRUONG_HOC["labels"]


@pytest.mark.parametrize("tho", [
    "{khong phai json", "", "[1, 2]", '"chuoi"', "null", "42",
])
def test_json_hong_hoac_sai_kieu_tra_ve_mac_dinh(db, tho):
    _luu_tho(db, tho)
    assert ws.doc_cau_hinh(db) == ws.MAC_DINH_TRUONG_HOC


def test_gia_tri_null_trong_bang_tra_ve_mac_dinh(db):
    _luu_tho(db, None)
    assert ws.doc_cau_hinh(db) == ws.MAC_DINH_TRUONG_HOC


def test_cau_truc_sai_ben_trong_khong_pha_nhan(db):
    _luu_tho(db, '{"labels": {"person": "Học sinh"}, "rules": 5}')
    cfg = ws.doc_cau_hinh(db)
    assert cfg == ws.MAC_DINH_TRUONG_HOC
    assert ws.nhan(cfg, "person", "en") == "Student"


# ---------- kiểm tra đầu vào ----------

@pytest.mark.parametrize("gia_tri", [0, 21, -1, "5", 2.5, True, None])
def test_max_choices_sai(db, gia_tri):
    with pytest.raises(ValueError, match="max_choices"):
        ws.ghi_cau_hinh(db, {"rules": {"max_choices": gia_tri}})


@pytest.mark.parametrize("gia_tri", [1, 20])
def test_max_choices_bien_hop_le(db, gia_tri):
    ws.ghi_cau_hinh(db, {"rules": {"max_choices": gia_tri}})
    assert ws.doc_cau_hinh(db)["rules"]["max_choices"] == gia_tri


@pytest.mark.parametrize("gia_tri", [-1, 21, "3", 1.5, True])
def test_max_tests_sai(db, gia_tri):
    with pytest.raises(ValueError, match="max_tests"):
        ws.ghi_cau_hinh(db, {"rules": {"max_tests": gia_tri}})


@pytest.mark.parametrize("gia_tri", [0, 20, None])
def test_max_tests_hop_le(db, gia_tri):
    ws.ghi_cau_hinh(db, {"rules": {"max_tests": gia_tri}})
    assert ws.doc_cau_hinh(db)["rules"]["max_tests"] == gia_tri


@pytest.mark.parametrize("khoa", ["priority", "tier_mode", "score_scope"])
@pytest.mark.parametrize("gia_tri", ["", "khac", None, 1])
def test_gia_tri_liet_ke_sai(db, khoa, gia_tri):
    with pytest.raises(ValueError, match=khoa):
        ws.ghi_cau_hinh(db, {"rules": {khoa: gia_tri}})


def test_gia_tri_liet_ke_hop_le(db):
    for p in ("score", "tier", "score+tier"):
        for m in ("reserve", "strict"):
            for s in ("per_slot", "per_person"):
                ws.ghi_cau_hinh(db, {"rules": {
                    "priority": p, "tier_mode": m, "score_scope": s}})
                assert ws.doc_cau_hinh(db)["rules"]["priority"] == p


def test_industry_sai(db):
    with pytest.raises(ValueError, match="industry"):
        ws.ghi_cau_hinh(db, {"industry": "bank"})
    for ng in ("school", "company", "event", "custom"):
        ws.ghi_cau_hinh(db, {"industry": ng})


@pytest.mark.parametrize("tiers", ["A", [1], [""], ["A", "A"], [" "], None])
def test_tiers_sai(db, tiers):
    with pytest.raises(ValueError, match="tiers"):
        ws.ghi_cau_hinh(db, {"rules": {"tiers": tiers}})


@pytest.mark.parametrize("vi", ["", "   ", None, 5])
def test_nhan_vi_trong_hoac_sai_kieu(db, vi):
    with pytest.raises(ValueError, match="person.vi"):
        ws.ghi_cau_hinh(db, {"labels": {"person": {"vi": vi, "en": "X"}}})


def test_nhan_sai_cau_truc(db):
    with pytest.raises(ValueError, match="person"):
        ws.ghi_cau_hinh(db, {"labels": {"person": "Học sinh"}})
    with pytest.raises(ValueError, match="labels"):
        ws.ghi_cau_hinh(db, {"labels": []})
    with pytest.raises(ValueError, match="rules"):
        ws.ghi_cau_hinh(db, {"rules": "x"})
    with pytest.raises(ValueError):
        ws.ghi_cau_hinh(db, "khong phai dict")


def test_dau_vao_sai_khong_ghi_gi(db):
    ws.ghi_cau_hinh(db, {"name": "Giữ"})
    with pytest.raises(ValueError):
        ws.ghi_cau_hinh(db, {"name": "Mất", "rules": {"max_choices": 99}})
    assert ws.doc_cau_hinh(db)["name"] == "Giữ"


def test_dau_vao_sai_khong_tao_tep(tmp_path):
    p = tmp_path / "moi.db"
    with pytest.raises(ValueError):
        ws.ghi_cau_hinh(str(p), {"rules": {"max_choices": 0}})
    assert not p.exists()


def test_ghi_khong_sua_cfg_dau_vao(db):
    cfg = {"labels": {"person": {"vi": "Ứng viên", "en": ""}}}
    snap = copy.deepcopy(cfg)
    ws.ghi_cau_hinh(db, cfg)
    assert cfg == snap


# ---------- nhãn: en -> vi ----------

def test_en_trong_thi_ghi_la_vi(db):
    for en in ("", "   ", None):
        ws.ghi_cau_hinh(db, {"labels": {"person": {"vi": "Ứng viên", "en": en}}})
        cfg = ws.doc_cau_hinh(db)
        assert cfg["labels"]["person"] == {"vi": "Ứng viên", "en": "Ứng viên"}


def test_nhan_tra_dung_ngon_ngu(db):
    cfg = ws.doc_cau_hinh(db)
    assert ws.nhan(cfg, "person", "vi") == "Học sinh"
    assert ws.nhan(cfg, "person", "en") == "Student"
    assert ws.nhan(cfg, "slot") == "Câu lạc bộ"


def test_nhan_lui_ve_vi_khi_thieu_en(db):
    cfg = {"labels": {"slot": {"vi": "Dự án"}}}
    assert ws.nhan(cfg, "slot", "en") == "Dự án"
    cfg = {"labels": {"slot": {"vi": "Dự án", "en": ""}}}
    assert ws.nhan(cfg, "slot", "en") == "Dự án"
    assert ws.nhan(cfg, "slot", "fr") == "Dự án"  # ngôn ngữ lạ cũng lùi về vi


def test_nhan_danh_tu_la_la_loi_lap_trinh(db):
    with pytest.raises(KeyError):
        ws.nhan(ws.doc_cau_hinh(db), "khong_co", "vi")
