"""Các thư mục KHÔNG GIAN LÀM VIỆC (workspace) trên đĩa.

Bố cục dưới thư mục gốc `root` (thư mục chứa .exe, xem main.py):

    root/workspaces/<slug>/app.db      mỗi workspace một CSDL riêng, cấu hình nằm
                                       TRONG app.db (xem cau_hinh_ws.py)
    root/workspaces/_trash/<slug>-<giờ>/   workspace đã xoá — KHÔNG xoá hẳn
    root/templates/<slug>.json         mẫu cấu hình (chỉ cấu hình, không dữ liệu)

Mọi hàm nhận `root` làm tham số; module không giữ trạng thái toàn cục, nên test
chỉ cần một thư mục tạm. `slug` là tên thư mục và KHÔNG đổi khi đổi tên hiển thị
(`doi_ten` chỉ sửa `config.name`): đường dẫn ổn định, bản sao lưu vẫn tìm thấy.

Quy tắc xuyên suốt: không bao giờ xoá dữ liệu của người dùng. Xoá = sao lưu rồi
dời vào `_trash`; ghi tệp = ghi tệp tạm rồi đổi tên; thao tác dở thì dọn đúng
thư mục MÌNH vừa tạo, không đụng gì khác.
"""

from __future__ import annotations

import copy
import datetime
import json
import os
import re
import shutil
import sqlite3
import tempfile
import zipfile

from cau_hinh_ws import (
    MAC_DINH_TRUONG_HOC,
    chuan_hoa_cau_hinh,
    doc_cau_hinh,
    ghi_cau_hinh,
)
from rbda_priority_pipeline import connect_db, init_db
from so_nhap import bo_dau

TEN_DB = "app.db"
THU_MUC_WS = "workspaces"
THU_MUC_RAC = "_trash"
THU_MUC_MAU = "templates"

TEN_MAC_DINH = "Trường học"
SLUG_MAC_DINH = "truong-hoc"

# Thư mục tạm khi chuyển app.db cũ. `workspaces/` chỉ xuất hiện (đổi tên một
# phát, nguyên tử) khi MỌI THỨ đã xong — xem `di_chuyen_db_cu`.
_THU_MUC_DANG_CHUYEN = "_dang_chuyen_workspaces"
TEP_GHI_CHU_CHUYEN = "DA_CHUYEN_SANG_WORKSPACES.txt"

_SLUG_TOI_DA = 60
_RE_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
_DAU_SQLITE = b"SQLite format 3\x00"
# Tệp phụ của SQLite: chuyển app.db mà bỏ lại `-journal` thì mất khả năng
# hoàn tác một lần ghi dở — app.db lúc đó có thể hỏng.
_DUOI_TEP_PHU = ("-journal", "-wal", "-shm")


# ---------------------------------------------------------------- tiện ích

def _duong_ws(root: str) -> str:
    return os.path.join(root, THU_MUC_WS)


def _slug_tu_ten(ten: str) -> str:
    """'Câu lạc bộ A (2025)' -> 'cau-lac-bo-a'. Rỗng thì 'workspace'."""
    s = "-".join(bo_dau(ten).split())[:_SLUG_TOI_DA].strip("-")
    return s or "workspace"


def _ten_hop_le(ten, nhan_: str = "Tên") -> str:
    if not isinstance(ten, str) or not ten.strip():
        raise ValueError("%s không được để trống" % nhan_)
    return ten.strip()


def _dau_thoi_gian() -> str:
    return datetime.datetime.now().strftime("%Y%m%d-%H%M%S")


def _cap_thu_muc(thu_muc_cha: str, goc: str) -> tuple[str, str]:
    """Tạo thư mục mới tên `goc`, `goc-2`, `goc-3`… (cái đầu chưa có).

    `os.mkdir` là phép kiểm-và-tạo nguyên tử, nên hai lệnh cùng lúc không bao
    giờ nhận cùng một slug.
    """
    os.makedirs(thu_muc_cha, exist_ok=True)
    n = 1
    while True:
        ten = goc if n == 1 else "%s-%d" % (goc, n)
        duong = os.path.join(thu_muc_cha, ten)
        try:
            os.mkdir(duong)
            return ten, duong
        except FileExistsError:
            n += 1


def _cap_workspace(root: str, ten: str) -> tuple[str, str]:
    return _cap_thu_muc(_duong_ws(root), _slug_tu_ten(ten))


def _db_cua(root: str, slug: str) -> str:
    """Đường dẫn app.db của workspace `slug`; sai slug / không có thì ValueError.

    Kiểm dạng slug trước khi ghép đường dẫn: `slug` đến từ giao diện, và
    '../..' không được phép trỏ ra ngoài `workspaces/`.
    """
    if not isinstance(slug, str) or not _RE_SLUG.match(slug):
        raise ValueError("Mã workspace không hợp lệ: %r" % (slug,))
    db = os.path.join(_duong_ws(root), slug, TEN_DB)
    if not os.path.isfile(db):
        raise ValueError("Không có workspace %r" % slug)
    return db


def _chep_db(nguon: str, dich: str, *, du_phong_chep_tep: bool = False) -> None:
    """Chép CSDL bằng SQLite backup API (như `PipelineAPI._backup_db`).

    Không chép tệp thô: tiến trình khác đang ghi thì tệp thô có thể là trạng
    thái nửa-ghi. Bản dở dang bị xoá để khỏi mang tên của một bản tốt.
    `du_phong_chep_tep`: nguồn hỏng không đọc được bằng backup API thì chép
    nguyên tệp — dùng cho bản sao lưu trước khi xoá, vì một workspace hỏng vẫn
    phải xoá được và vẫn phải còn bản để cứu.
    """
    try:
        src = connect_db(nguon)
        try:
            dst = sqlite3.connect(dich)
            try:
                src.backup(dst)
            finally:
                dst.close()
        finally:
            src.close()
    except BaseException as e:
        try:
            os.remove(dich)
        except OSError:
            pass
        if du_phong_chep_tep and isinstance(e, sqlite3.Error):
            shutil.copy2(nguon, dich)
            return
        raise


def _ghi_json_nguyen_tu(duong: str, doi_tuong) -> None:
    tam = duong + ".tmp"
    with open(tam, "w", encoding="utf-8") as f:
        json.dump(doi_tuong, f, ensure_ascii=False, indent=2)
    os.replace(tam, duong)


def _don_thu_muc_vua_tao(duong: str) -> None:
    shutil.rmtree(duong, ignore_errors=True)


# ---------------------------------------------------------------- danh sách

def danh_sach(root: str) -> list[dict]:
    """Các workspace dưới `root/workspaces/*/app.db`, sắp theo slug.

    Mỗi phần tử: `{slug, name, industry, path, modified}`. `path` là đường dẫn
    app.db (thứ mà `PipelineAPI(path)` cần). `modified` là giờ sửa app.db, ISO
    `YYYY-MM-DDTHH:MM:SS`. Thư mục bắt đầu bằng `_` (`_trash`, thư mục tạm) bị
    bỏ qua. `name` rỗng thì dùng slug. Một app.db hỏng vẫn được liệt kê (để
    người dùng còn thấy và mở màn phục hồi), với cấu hình mặc định.
    """
    ws = _duong_ws(root)
    if not os.path.isdir(ws):
        return []
    kq = []
    for slug in sorted(os.listdir(ws)):
        if slug.startswith("_"):
            continue
        db = os.path.join(ws, slug, TEN_DB)
        if not os.path.isfile(db):
            continue
        cfg = doc_cau_hinh(db)
        kq.append({
            "slug": slug,
            "name": cfg["name"] or slug,
            "industry": cfg["industry"],
            "path": db,
            "modified": datetime.datetime.fromtimestamp(
                os.path.getmtime(db)).strftime("%Y-%m-%dT%H:%M:%S"),
        })
    return kq


# ---------------------------------------------------------------- tạo / sửa

def tao(root: str, name: str, cfg: dict | None = None) -> str:
    """Tạo workspace mới tên `name`; trả về slug.

    `cfg` (có thể một phần, hoặc None = mặc định trường học) được kiểm bằng
    `ghi_cau_hinh`; `name` luôn thắng `cfg["name"]`. Cấu hình sai thì ném
    ValueError TRƯỚC khi tạo bất cứ thứ gì.
    """
    name = _ten_hop_le(name, "Tên workspace")
    cfg = dict(cfg or {})
    cfg["name"] = name
    chuan_hoa_cau_hinh(cfg)
    slug, thu_muc = _cap_workspace(root, name)
    try:
        db = os.path.join(thu_muc, TEN_DB)
        init_db(db)
        ghi_cau_hinh(db, cfg)
    except BaseException:
        _don_thu_muc_vua_tao(thu_muc)
        raise
    return slug


def doi_ten(root: str, slug: str, new_name: str) -> None:
    """Đổi tên hiển thị (`config.name`). Thư mục giữ nguyên slug."""
    new_name = _ten_hop_le(new_name, "Tên workspace")
    db = _db_cua(root, slug)
    cfg = doc_cau_hinh(db)
    cfg["name"] = new_name
    ghi_cau_hinh(db, cfg)


def xoa(root: str, slug: str) -> str:
    """Xoá workspace: sao lưu app.db, rồi dời CẢ thư mục vào `_trash`.

    Không xoá tệp nào. Bản sao lưu `app.db.bak-<giờ>` nằm trong thư mục (cùng
    quy ước với `_backup_db`, nên màn phục hồi tìm thấy) và đi theo vào thùng
    rác. Sao lưu lỗi thì không dời gì. Trả về đường dẫn trong `_trash`. Khôi
    phục = tự dời thư mục đó về `workspaces/`.

    Người gọi phải đóng `PipelineAPI` đang mở workspace này trước (Windows
    không dời được thư mục có tệp đang mở).
    """
    db = _db_cua(root, slug)
    thu_muc = os.path.dirname(db)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    _chep_db(db, os.path.join(thu_muc, "%s.bak-%s" % (TEN_DB, ts)),
             du_phong_chep_tep=True)
    rac = os.path.join(_duong_ws(root), THU_MUC_RAC)
    _, dich = _cap_thu_muc(rac, "%s-%s" % (slug, _dau_thoi_gian()))
    os.rmdir(dich)  # thư mục rỗng do chính _cap_thu_muc vừa tạo; chỉ giữ chỗ tên
    shutil.move(thu_muc, dich)
    return dich


def nhan_ban(root: str, slug: str, new_name: str, kem_du_lieu: bool) -> str:
    """Nhân bản workspace `slug` thành `new_name`; trả về slug mới.

    `kem_du_lieu=True`: chép CSDL bằng backup API (cả dữ liệu lẫn cấu hình).
    `False`: CSDL mới, trống, cùng cấu hình.
    """
    new_name = _ten_hop_le(new_name, "Tên workspace")
    nguon = _db_cua(root, slug)
    if not kem_du_lieu:
        return tao(root, new_name, doc_cau_hinh(nguon))
    slug_moi, thu_muc = _cap_workspace(root, new_name)
    try:
        dich = os.path.join(thu_muc, TEN_DB)
        _chep_db(nguon, dich)
        init_db(dich)
        cfg = doc_cau_hinh(dich)
        cfg["name"] = new_name
        ghi_cau_hinh(dich, cfg)
    except BaseException:
        _don_thu_muc_vua_tao(thu_muc)
        raise
    return slug_moi


# ---------------------------------------------------------------- mẫu

def luu_mau(root: str, slug: str, ten_mau: str) -> str:
    """Lưu CẤU HÌNH (không dữ liệu) của `slug` làm mẫu; trả về slug của mẫu.

    Tệp: `root/templates/<slug-của-ten_mau>.json`, nội dung là cấu hình với
    `name` = `ten_mau`. Lưu lại cùng tên thì GHI ĐÈ mẫu cũ (sửa mẫu). Slug
    `truong-hoc` dành cho mẫu dựng sẵn nên mẫu của người dùng lấy `truong-hoc-2`.
    """
    ten_mau = _ten_hop_le(ten_mau, "Tên mẫu")
    cfg = chuan_hoa_cau_hinh(doc_cau_hinh(_db_cua(root, slug)))
    cfg["name"] = ten_mau
    mslug = _slug_tu_ten(ten_mau)
    if mslug == SLUG_MAC_DINH:
        mslug += "-2"
    thu_muc = os.path.join(root, THU_MUC_MAU)
    os.makedirs(thu_muc, exist_ok=True)
    _ghi_json_nguyen_tu(os.path.join(thu_muc, mslug + ".json"), cfg)
    return mslug


def danh_sach_mau(root: str) -> list[dict]:
    """Mẫu cấu hình: mẫu dựng sẵn "Trường học" luôn đứng đầu, rồi mẫu đã lưu.

    Mỗi phần tử: `{slug, name, industry, builtin, config}`; `config` đưa thẳng
    được cho `tao(root, name, config)`. Tệp mẫu hỏng/sai bị bỏ qua, không làm
    hỏng cả danh sách.
    """
    san = copy.deepcopy(MAC_DINH_TRUONG_HOC)
    san["name"] = TEN_MAC_DINH
    kq = [{
        "slug": SLUG_MAC_DINH, "name": TEN_MAC_DINH, "industry": san["industry"],
        "builtin": True, "config": san,
    }]
    thu_muc = os.path.join(root, THU_MUC_MAU)
    if not os.path.isdir(thu_muc):
        return kq
    for tep in sorted(os.listdir(thu_muc)):
        if not tep.endswith(".json"):
            continue
        mslug = tep[:-len(".json")]
        try:
            with open(os.path.join(thu_muc, tep), encoding="utf-8") as f:
                cfg = chuan_hoa_cau_hinh(json.load(f))
        except (OSError, ValueError):  # JSONDecodeError là ValueError
            continue
        kq.append({
            "slug": mslug, "name": cfg["name"] or mslug,
            "industry": cfg["industry"], "builtin": False, "config": cfg,
        })
    return kq


# ---------------------------------------------------------------- zip

def xuat_zip(root: str, slug: str, dest_path: str) -> str:
    """Xuất workspace ra `dest_path` (.zip) chỉ gồm `app.db`.

    app.db được chụp bằng backup API trước khi nén; cấu hình nằm trong đó nên
    zip tự đủ. Ghi tệp tạm rồi đổi tên: `dest_path` không bao giờ dở dang.
    """
    db = _db_cua(root, slug)
    dich_thu_muc = os.path.dirname(os.path.abspath(dest_path))
    os.makedirs(dich_thu_muc, exist_ok=True)
    tam_zip = dest_path + ".tmp"
    with tempfile.TemporaryDirectory(prefix="rbda_xuat_") as tam:
        anh = os.path.join(tam, TEN_DB)
        _chep_db(db, anh)
        try:
            with zipfile.ZipFile(tam_zip, "w", zipfile.ZIP_DEFLATED) as z:
                z.write(anh, TEN_DB)
            os.replace(tam_zip, dest_path)
        except BaseException:
            try:
                os.remove(tam_zip)
            except OSError:
                pass
            raise
    return dest_path


def _ten_muc_an_toan(ten: str) -> str:
    """Chuẩn hoá tên mục zip, hoặc ValueError nếu có thể thoát khỏi thư mục đích."""
    chuan = ten.replace("\\", "/")
    phan = chuan.split("/")
    if (
        "\x00" in chuan
        or chuan.startswith("/")
        or re.match(r"^[A-Za-z]:", chuan)
        or ".." in phan
    ):
        raise ValueError("Tệp zip chứa đường dẫn không an toàn: %r" % ten)
    return chuan


def nhap_zip(root: str, zip_path: str) -> str:
    """Nhập workspace từ zip do `xuat_zip` tạo; trả về slug.

    * MỌI mục có đường dẫn tuyệt đối hoặc '..' → từ chối cả tệp (zip-slip),
      kể cả khi mục đó không phải app.db.
    * Phải có `app.db` (ở gốc, hoặc trong đúng một thư mục — zip do người dùng
      tự nén thư mục). Chỉ app.db được giải nén, các mục khác bị bỏ qua.
    * Phải là CSDL SQLite nguyên vẹn của phần mềm này; được nâng lên lược đồ
      hiện tại bằng `init_db`.
    * Slug lấy từ tên trong cấu hình; trùng thì thêm -2, -3 như `tao`.
    """
    try:
        z = zipfile.ZipFile(zip_path)
    except (zipfile.BadZipFile, OSError) as e:
        raise ValueError("Không đọc được tệp zip: %s" % e)
    with z:
        muc = {_ten_muc_an_toan(i.filename): i for i in z.infolist()
               if not i.is_dir()}
        chon = None
        if TEN_DB in muc:
            chon = muc[TEN_DB]
        else:
            ung_vien = [t for t in muc if t.count("/") == 1
                        and t.endswith("/" + TEN_DB)]
            if len(ung_vien) == 1:
                chon = muc[ung_vien[0]]
        if chon is None:
            raise ValueError("Tệp zip không có app.db")

        ws = _duong_ws(root)
        os.makedirs(ws, exist_ok=True)
        tam = tempfile.mkdtemp(prefix="_nhap_", dir=ws)  # `_`: danh_sach bỏ qua
        thu_muc_moi = None
        try:
            db_tam = os.path.join(tam, TEN_DB)
            with z.open(chon) as nguon, open(db_tam, "wb") as dich:
                shutil.copyfileobj(nguon, dich)
            cfg = _kiem_va_nang_cap_db(db_tam)
            ten = cfg["name"] or os.path.splitext(os.path.basename(zip_path))[0]
            slug, thu_muc_moi = _cap_workspace(root, ten)
            os.replace(db_tam, os.path.join(thu_muc_moi, TEN_DB))
            if not cfg["name"]:
                ghi_cau_hinh(os.path.join(thu_muc_moi, TEN_DB),
                             dict(cfg, name=ten))
            return slug
        except BaseException:
            if thu_muc_moi:
                _don_thu_muc_vua_tao(thu_muc_moi)
            raise
        finally:
            _don_thu_muc_vua_tao(tam)


def _kiem_va_nang_cap_db(db: str) -> dict:
    """Kiểm `db` là CSDL của phần mềm, nâng lược đồ; trả về cấu hình của nó."""
    with open(db, "rb") as f:
        if f.read(len(_DAU_SQLITE)) != _DAU_SQLITE:
            raise ValueError("app.db trong zip không phải CSDL SQLite")
    try:
        conn = sqlite3.connect(db)
        try:
            ok = conn.execute("PRAGMA quick_check").fetchone()
            co_hs = conn.execute(
                "SELECT 1 FROM sqlite_master "
                "WHERE type = 'table' AND name = 'students'").fetchone()
        finally:
            conn.close()
    except sqlite3.Error as e:
        raise ValueError("app.db trong zip bị hỏng: %s" % e)
    if not ok or ok[0] != "ok":
        raise ValueError("app.db trong zip bị hỏng (quick_check không đạt)")
    if not co_hs:
        raise ValueError("app.db trong zip không phải CSDL của phần mềm này")
    init_db(db)
    return doc_cau_hinh(db)


# ---------------------------------------------------------------- app.db cũ

def _tep_cua_db_cu(root: str) -> list[str]:
    """Tên các tệp cần chuyển: app.db, tệp phụ của nó, và app.db.bak-*."""
    tep = []
    for ten in sorted(os.listdir(root)):
        if not os.path.isfile(os.path.join(root, ten)):
            continue
        if (
            ten == TEN_DB
            or ten in [TEN_DB + d for d in _DUOI_TEP_PHU]
            or ten.startswith(TEN_DB + ".bak-")
        ):
            tep.append(ten)
    return tep


_GHI_CHU_CHUYEN = (
    "Phần mềm đã được nâng cấp để hỗ trợ nhiều không gian làm việc (workspace), "
    "mỗi workspace có cơ sở dữ liệu riêng. Cơ sở dữ liệu cũ của thầy cô (app.db "
    "và các bản sao lưu app.db.bak-*) đã được chuyển nguyên vẹn, không mất dữ "
    "liệu, sang thư mục workspaces\\truong-hoc với tên \"Trường học\". Thầy cô "
    "không cần làm gì thêm; nếu cần, có thể sao lưu thư mục workspaces để giữ "
    "toàn bộ dữ liệu."
)


def di_chuyen_db_cu(root: str) -> str | None:
    """Chuyển `root/app.db` cũ vào `root/workspaces/truong-hoc/`.

    Chỉ chạy khi `root/app.db` có VÀ `root/workspaces/` chưa có. Trả về
    'truong-hoc' nếu vừa chuyển, ngược lại None. Chạy lại là an toàn.

    CHỐNG MẤT DỮ LIỆU KHI BỊ NGẮT. Điều kiện chạy lại là "chưa có
    `workspaces/`", nên nếu tạo `workspaces/` ngay từ đầu rồi sập giữa chừng,
    lần sau sẽ không bao giờ chuyển tiếp và app.db cũ nằm mồ côi — người dùng
    thấy workspace trống và tưởng mất dữ liệu. Vì vậy mọi việc làm trong thư
    mục tạm `_dang_chuyen_workspaces/`; chỉ khi xong hết mới đổi tên nó thành
    `workspaces/` (một phép đổi tên). Sập giữa chừng thì lần sau thấy thư mục
    tạm và làm tiếp phần còn lại. Tệp chỉ được dời (không xoá), và không ghi
    đè tệp đã có ở đích.

    Cấu hình được ghi bằng `ghi_cau_hinh`; app.db hỏng thì bỏ qua bước đó (vẫn
    dời để màn phục hồi mở được đúng tệp).
    """
    ws = _duong_ws(root)
    tam = os.path.join(root, _THU_MUC_DANG_CHUYEN)
    cu = os.path.join(root, TEN_DB)
    if os.path.exists(ws):
        return None
    if not (os.path.isfile(cu) or os.path.isdir(tam)):
        return None

    dich = os.path.join(tam, SLUG_MAC_DINH)
    os.makedirs(dich, exist_ok=True)
    for ten in _tep_cua_db_cu(root):
        d = os.path.join(dich, ten)
        if not os.path.exists(d):
            os.replace(os.path.join(root, ten), d)

    db = os.path.join(dich, TEN_DB)
    if os.path.isfile(db):
        try:
            ghi_cau_hinh(db, {"name": TEN_MAC_DINH})
        except Exception:
            pass

    with open(os.path.join(root, TEP_GHI_CHU_CHUYEN), "w",
              encoding="utf-8-sig") as f:
        f.write(_GHI_CHU_CHUYEN + "\n")
    os.rename(tam, ws)
    return SLUG_MAC_DINH


# ---------------------------------------------------------------- khởi động

def chon_de_mo(root: str) -> str:
    """Đường dẫn app.db mà `main.py` mở khi không có tham số dòng lệnh.

    Chuyển app.db cũ nếu cần; không có workspace nào thì tạo "Trường học"
    mặc định; đúng một thì mở nó. Từ hai trở lên: mở cái sửa gần nhất (tạm
    thời — giao diện chọn workspace sẽ thay chỗ này).
    """
    di_chuyen_db_cu(root)
    ds = danh_sach(root)
    if not ds:
        tao(root, TEN_MAC_DINH)
        ds = danh_sach(root)
    return max(ds, key=lambda w: w["modified"])["path"]
