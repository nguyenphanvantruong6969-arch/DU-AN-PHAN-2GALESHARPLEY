"""Không gian làm việc (workspace): danh sách, mở, tạo, đổi tên, xoá, nhân
bản, mẫu, xuất/nhập .zip và cấu hình.

Một phần của PipelineAPI (xem api.py) — mọi hàm public ở đây vẫn là hàm của
PipelineAPI và giao diện gọi được như cũ. Phần lưu trên đĩa nằm ở
`workspace.py`, phần cấu hình ở `cau_hinh_ws.py`; tệp này chỉ là lớp mỏng nối
chúng với giao diện theo hợp đồng `{ok, data, errors}`.

CHẾ ĐỘ. PipelineAPI có thư mục gốc workspace (`thu_muc_goc`, do main.py đưa
vào) thì ở chế độ workspace; chạy bằng một đường dẫn CSDL chỉ định thì KHÔNG,
và mọi hàm ở đây trả lỗi `ws_disabled`.

ĐỔI WORKSPACE ĐANG MỞ là đổi `self.db_path`. Việc đó diễn ra dưới `_khoa_ghi`
— cùng khoá mà mọi thao tác ghi và run_pipeline giữ — nên không lời gọi nào
đang dở trên CSDL cũ khi con trỏ đổi sang CSDL mới. Mọi kết nối của PipelineAPI
đều mở rồi đóng ngay trong từng lời gọi, nên thư mục của một workspace đã đóng
dời đi được (xoá).
"""

import base64
import binascii
import datetime
import os
import tempfile

import cau_hinh_ws
import workspace
from api_chung import duong_dan_khong_de, thu_muc_tai_ve
from i18n_errors import err
from i18n_errors import phan_hoi_loi as _fail
from i18n_errors import phan_hoi_ok as _ok
from rbda_priority_pipeline import init_db


class _ChuaMoWorkspace(Exception):
    """Cần workspace đang mở mà chưa mở cái nào."""


class _TenTrong(ValueError):
    """Tên rỗng."""


class WorkspaceMixin:
    _XOA_WS_XAC_NHAN = "XOA"

    # ------------------------------------------------------------ nền

    def _ws_chay(self, viec, slug=""):
        """Chạy `viec()` dưới khoá ghi và gói kết quả thành `{ok, data, errors}`.

        Một chỗ duy nhất đổi ngoại lệ của `workspace` / `cau_hinh_ws` thành lỗi
        có mã (dịch được): chưa mở workspace → `ws_none_open`; tên trống →
        `ws_name_required`; mã sai hoặc không có → `ws_not_found`; zip hỏng →
        `ws_zip_invalid`; dữ liệu nhập sai → `ws_invalid`; còn lại ghi vết vào
        tệp log như mọi hàm khác.
        """
        if not self._ws_goc:
            return _fail(err("ws_disabled"))
        try:
            with self._khoa_ghi:
                return _ok(viec())
        except _ChuaMoWorkspace:
            return _fail(err("ws_none_open"))
        except _TenTrong:
            return _fail(err("ws_name_required"))
        except workspace.KhongCoWorkspace:
            return _fail(err("ws_not_found", slug=str(slug)))
        except workspace.TepZipSai as e:
            return _fail(err("ws_zip_invalid", detail=str(e)))
        except ValueError as e:
            return _fail(err("ws_invalid", detail=str(e)))
        except Exception as e:
            return _fail(self._loi_co_ghi_vet(err("error_workspace", detail=str(e))))

    def _ws_db(self, slug=None):
        """app.db của `slug`, hoặc của workspace đang mở khi `slug` là None."""
        if slug is None:
            if not self.db_path:
                raise _ChuaMoWorkspace()
            return self.db_path
        return workspace.duong_db(self._ws_goc, slug)

    @staticmethod
    def _ws_ten(ten):
        if not isinstance(ten, str) or not ten.strip():
            raise _TenTrong()
        return ten.strip()

    # ------------------------------------------------------------ luật đang áp dụng

    def _luat_ws(self) -> dict:
        """`rules` của workspace đang mở (thiếu khoá = mặc định trường học).

        Đọc từ CSDL mỗi lần gọi: một lời gọi cần luật chỉ gọi vài lần, và đọc lại
        thì sửa cấu hình có hiệu lực ngay, không cần cache nào để làm mới.
        """
        return cau_hinh_ws.doc_cau_hinh(self.db_path)["rules"]

    def _tran_thi(self):
        """Trần số chỗ được thi mỗi đợt (None = không giới hạn).

        Điểm theo NGƯỜI (`score_scope = "per_person"`) thì không có việc "chọn chỗ
        để thi": một điểm áp cho mọi nguyện vọng, nên mọi nguyện vọng đều là chỗ
        được thi và trần thi không còn nghĩa — không giới hạn.
        """
        luat = self._luat_ws()
        return None if luat.get("score_scope") == "per_person" else luat["max_tests"]

    def _cau_hinh_so_nhap(self):
        """`cfg` cho so_nhap.py: None nếu nhãn và luật là mặc định trường học.

        Không gian làm việc chưa đổi gì thì sổ nhập phải là đúng tệp như trước
        nay, từng ô một — nên đưa None chứ không đưa bản cấu hình mặc định (bản
        đó cho số cột NV theo `max_choices`, không theo mức 15 của sổ cũ).
        """
        cfg = cau_hinh_ws.doc_cau_hinh(self.db_path)
        mac_dinh = cau_hinh_ws.MAC_DINH_TRUONG_HOC
        if (cfg["labels"] == mac_dinh["labels"] and cfg["rules"] == mac_dinh["rules"]):
            return None
        return {"labels": cfg["labels"], "rules": cfg["rules"]}

    # ------------------------------------------------------------ danh sách

    def list_workspaces(self):
        """`data = {current, items}`; `current` là slug đang mở (None = chưa mở)."""
        return self._ws_chay(lambda: {
            "current": self._ws_slug,
            "items": workspace.danh_sach(self._ws_goc),
        })

    def list_templates(self):
        """Mẫu cấu hình: mẫu "Trường học" dựng sẵn luôn đứng đầu."""
        return self._ws_chay(lambda: workspace.danh_sach_mau(self._ws_goc))

    # ------------------------------------------------------------ mở / tạo

    def open_workspace(self, slug: str):
        """Mở workspace `slug`: đổi `db_path`, nâng lược đồ, trả cấu hình.

        Bộ nhớ đệm gắn với CSDL cũ (`_bo_nho_xuat`, chỉ có trong lúc xuất)
        được xoá. Mở lỗi (CSDL hỏng...) thì workspace đang mở giữ nguyên.
        """
        def viec():
            db = workspace.duong_db(self._ws_goc, slug)
            init_db(db)
            cfg = cau_hinh_ws.doc_cau_hinh(db)
            self.db_path = db
            self._ws_slug = slug
            self._bo_nho_xuat = None
            return {"slug": slug, "name": cfg["name"] or slug, "config": cfg}
        return self._ws_chay(viec, slug)

    def create_workspace(self, name: str, cfg: dict = None):
        """Tạo workspace mới (KHÔNG mở nó). `data = {slug}`."""
        def viec():
            return {"slug": workspace.tao(self._ws_goc, self._ws_ten(name), cfg)}
        return self._ws_chay(viec)

    def rename_workspace(self, slug: str, new_name: str):
        def viec():
            workspace.doi_ten(self._ws_goc, slug, self._ws_ten(new_name))
            return {"slug": slug, "name": new_name.strip()}
        return self._ws_chay(viec, slug)

    def duplicate_workspace(self, slug: str, new_name: str, kem_du_lieu: bool = True):
        """Nhân bản `slug`; `kem_du_lieu=False` chỉ chép cấu hình. `data = {slug}`."""
        def viec():
            return {"slug": workspace.nhan_ban(
                self._ws_goc, slug, self._ws_ten(new_name), bool(kem_du_lieu))}
        return self._ws_chay(viec, slug)

    # ------------------------------------------------------------ xoá

    def delete_workspace(self, slug: str, xac_nhan: str = ""):
        """Xoá workspace: sao lưu rồi dời vào `_trash` (không xoá hẳn tệp nào).

        `xac_nhan` phải đúng "XOA" — như `reset_data`: một hàm xoá mà gọi
        nhầm được từ JS là không chấp nhận được. Xoá đúng workspace đang mở thì
        đóng nó trước (`current` thành None); giao diện quay về màn chọn.
        """
        if not self._ws_goc:
            return _fail(err("ws_disabled"))
        # Kiểm TRƯỚC, làm SAU: đảo thứ tự thì gọi nhầm vẫn đẻ ra bản sao lưu.
        if xac_nhan != self._XOA_WS_XAC_NHAN:
            return _fail(err("ws_delete_confirmation_mismatch"))

        def viec():
            workspace.duong_db(self._ws_goc, slug)  # sai mã thì khỏi đóng gì
            dang_mo = self._ws_slug == slug
            if dang_mo:
                self.db_path = None
                self._ws_slug = None
                self._bo_nho_xuat = None
            try:
                rac = workspace.xoa(self._ws_goc, slug)
            except BaseException:
                if dang_mo:
                    # Xoá lỗi thì workspace vẫn còn đó: mở lại như cũ.
                    self.db_path = workspace.duong_db(self._ws_goc, slug)
                    self._ws_slug = slug
                raise
            return {"slug": slug, "trash": rac, "was_open": dang_mo}
        return self._ws_chay(viec, slug)

    # ------------------------------------------------------------ mẫu / zip

    def save_as_template(self, slug: str, ten_mau: str):
        """Lưu CẤU HÌNH của `slug` (không dữ liệu) làm mẫu. `data = {slug}`."""
        def viec():
            return {"slug": workspace.luu_mau(
                self._ws_goc, slug, self._ws_ten(ten_mau))}
        return self._ws_chay(viec, slug)

    def export_workspace(self, slug: str):
        """Xuất `slug` ra .zip trong thư mục xuất (Tải xuống). `data = {path, name}`.

        Tên tệp không đè tệp đã có (`x.zip` → `x (2).zip`), như mọi tệp xuất.
        """
        def viec():
            workspace.duong_db(self._ws_goc, slug)
            thu_muc = self.thu_muc_xuat or thu_muc_tai_ve()
            if not (thu_muc and os.path.isdir(thu_muc)
                    and os.access(thu_muc, os.W_OK)):
                thu_muc = self._ws_goc          # lùi về cạnh chương trình
            ten = "%s-%s.zip" % (slug, datetime.date.today().strftime("%Y%m%d"))
            dich = duong_dan_khong_de(os.path.join(thu_muc, ten))
            workspace.xuat_zip(self._ws_goc, slug, dich)
            return {"path": dich, "name": os.path.basename(dich)}
        return self._ws_chay(viec, slug)

    def import_workspace(self, file_base64: str):
        """Nhập workspace từ .zip (gửi lên dạng base64). `data = {slug}`.

        Slug trùng thì tự thêm -2, -3... Không mở workspace vừa nhập.
        """
        def viec():
            try:
                du_lieu = base64.b64decode(file_base64 or "", validate=False)
            except (binascii.Error, ValueError):
                raise workspace.TepZipSai("Dữ liệu tải lên không phải base64")
            if not du_lieu:
                raise workspace.TepZipSai("Tệp zip rỗng")
            with tempfile.TemporaryDirectory(prefix="rbda_nhap_") as tam:
                duong_zip = os.path.join(tam, "nhap.zip")
                with open(duong_zip, "wb") as f:
                    f.write(du_lieu)
                return {"slug": workspace.nhap_zip(self._ws_goc, duong_zip)}
        return self._ws_chay(viec)

    # ------------------------------------------------------------ cấu hình

    def get_workspace_config(self, slug: str = None):
        """Cấu hình (đã trộn mặc định) của `slug`, hoặc của workspace đang mở."""
        return self._ws_chay(
            lambda: cau_hinh_ws.doc_cau_hinh(self._ws_db(slug)), slug or "")

    def update_workspace_config(self, cfg: dict, slug: str = None):
        """Kiểm rồi ghi cấu hình; trả bản đã chuẩn hoá. Sai thì `ws_invalid`."""
        return self._ws_chay(
            lambda: cau_hinh_ws.ghi_cau_hinh(self._ws_db(slug), cfg), slug or "")

