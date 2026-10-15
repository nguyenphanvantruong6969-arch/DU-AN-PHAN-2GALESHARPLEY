# UX_PILOT_NOTES — thử phần mềm như người dùng MỚI (hai ngành ngoài trường học)

> **Đọc trước khi dùng các con số hay nhận xét ở đây.**
> - Hai "người dùng" dưới đây do **AI đóng vai** theo lời nhờ của chủ dự án. Đây là một lượt **đi thử có kịch bản** (cognitive walkthrough) trên giao diện thật, **không phải nghiên cứu người dùng** và không có người thật nào được hỏi. Đừng trích nó như kết quả khảo sát.
> - Dữ liệu là **MÔ PHỎNG** (`du_lieu_test/bo_cong_ty`, `du_lieu_test/bo_su_kien`): tên người, tên dự án, tên workshop đều bịa. Các con số "289/300", "799/800" chỉ cho biết chương trình chạy trọn hành trình, không nói gì về chất lượng của thuật toán.
> - Tệp này là tài liệu vận hành. Phần nhận xét, diễn giải trong báo cáo đề tài vẫn do học sinh tự viết.

## 1. Cách đã thử

Chạy **đúng đường người dùng thật đi**: `python main.py` trong thư mục tạm (không có pywebview nên chương trình rơi sang chế độ dự phòng `browser_host.py`), mở URL của nó bằng Playwright + Chromium trong `/opt/pw-browsers`. Một tập lệnh trình duyệt giả chỉ **ghi URL ra tệp** (biến `RBDA_BROWSER`), thư mục tải về được chuyển hướng bằng `RBDA_THU_MUC_TAI_VE`. Không đụng vào kho mã: các tệp chạy được chép sang thư mục tạm.

| | Người A — chuyên viên nhân sự | Người B — người tổ chức sự kiện |
|---|---|---|
| Lời nhờ | "Xếp 300 nhân viên vào 12 đội dự án theo KPI, cấp bậc cao được ưu tiên trước." | "Xếp 800 khách vào 24 workshop trong 3 khung giờ, khách VIP trước." |
| Nhãn đặt trong trình hướng dẫn | Nhân viên / Dự án / Quý / Cấp bậc / KPI | Khách tham dự / Workshop / Phiên / Hạng vé / Điểm |
| Luật | tối đa 3 nguyện vọng; nhóm trước rồi đến điểm; nhóm xếp cứng Senior > Mid > Junior; **một KPI cho cả người** | tối đa 2 nguyện vọng mỗi phiên; **chỉ theo hạng vé** VIP > Member > Guest; không điểm |
| Dữ liệu | `du_lieu_test/bo_cong_ty/SO_NHAP.xlsx` | `du_lieu_test/bo_su_kien/SO_NHAP.xlsx` |
| Kết quả chạy | 289/300 có dự án, 90,3% được nguyện vọng 1 | 799/800 có workshop |

Hành trình mỗi người (26 màn, đánh số trong tên ảnh): mở phần mềm lần đầu → bảng chọn workspace → trình hướng dẫn 4 bước (thông tin, từ vựng, luật, xem lại) → thẻ Vận hành của workspace trống → **tải sổ nhập mẫu** → **bấm Chạy khi chưa có dữ liệu** → nạp nhầm một sổ của ngành khác, nạp nhầm sổ trường học → nạp đúng sổ → cảnh báo dữ liệu → chạy → thẻ Kết quả (thu gọn rồi mở rộng) → **xuất Excel** (mở tệp `.xlsx` và đọc cả sáu trang) → thẻ Nhập tại chỗ, Quản lý, Nhập điểm, Vận hành lần cuối.

- Ảnh chụp: `docs/ux_pilot/anh_chup/truoc/{nhan_su,su_kien}/` (**trước** khi sửa) và `docs/ux_pilot/anh_chup/sau/{nhan_su,su_kien}/` (**sau**). Mỗi ảnh `NN_tên.png` có `NN_tên.txt` là chữ nhìn thấy trên màn đó; ảnh dài được cắt thành `_khoiNN.png`. `ghi_chu_may.json` giữ tiêu đề cột, chữ hướng dẫn của sổ mẫu và nội dung từng trang của tệp Excel đã xuất.
- Chạy lại: `python docs/ux_pilot/chay_pilot.py --ra <thư mục> --nguoi nhan_su` (hoặc `su_kien`); `docs/ux_pilot/hanh_trinh.py` là kịch bản từng người; `docs/ux_pilot/nen_anh.py` nén ảnh (PNG 128 màu) trước khi đưa vào kho.
- Ảnh "trước" chụp ở trạng thái của kho ngay trước vòng này (đã có tính năng nhãn từ vựng nhưng chưa có các sửa dưới đây).

**Kết luận chung của lượt thử:** chạy trọn được cả hai hành trình, không có lỗi chặn. Chỗ vướng nằm ở **chữ và những thứ thừa** — người mới liên tục gặp từ của trường học, ô và cột nói về thứ ngành họ không có, và vài lời nhắc không chỉ ra việc cần làm tiếp.

## 2. Đã sửa (có test)

Cột "Test" là tệp và tên test; `A` = `tests/test_ws_ux_nguoi_moi.py` (không cần trình duyệt), `G` = `tests/test_ws_ux_nguoi_moi_giao_dien.py` (Chromium thật). Mọi chuỗi mới có **cả vi và en**.

### 2.1 Từ của trường học còn lọt vào

| # | Ở đâu (ảnh) | Trước | Sau | Test |
|---|---|---|---|---|
| S1 | Thẻ Vận hành: gợi ý nhập, ô thả, báo lỗi "không phải sổ nhập" / "chỉ nhận .xlsx" (`11`–`14`) | "Sổ nhập **CLB**", "Kéo Sổ nhập CLB vào đây" | "Sổ nhập **dự án**" / "**workshop**" theo nhãn | `A::test_loi_sai_so_nhap_noi_cach_sua…`, `G::test_khong_the_nao_cua_cong_ty_hay_su_kien_con_tu_cua_truong_hoc` |
| S2 | Thẻ Kết quả, Quản lý, Excel, lỗi tệp lớn (`19`, `24`) | "không gửi cho **giáo viên** chấm KPI", "**Trường** tự quyết định…", "tệp danh sách của một **trường**", "**Nhà trường** cần xếp tay", "Số **em** đã có dự án", "Mỗi **em** một dòng", "**Thời khoá biểu** tuần", "cả **tuần**" | "người chấm KPI", "Đơn vị tự quyết định…", "một đơn vị", "Bộ phận phụ trách", "Số **nhân viên** đã có dự án", "Lịch xếp theo quý", "cả đợt xếp" (cơ chế `{em} {gv} {nt} {truong} {tuan} {tkb} {tkbt}`: chỉ ra từ của trường học khi nhãn người vẫn là "Học sinh") | `A::test_xlsx_*`, `G::test_khong_the_nao…`; `tests/test_ws_nhan.py` (chuỗi trường học giữ **y nguyên** từng byte) |
| S3 | Tên tệp tải về (`11`, `21`) | `SO_NHAP_CLB.xlsx` | `SO_NHAP_DU_AN.xlsx`, `SO_NHAP_WORKSHOP.xlsx` | `A::test_ten_tep_so_nhap_theo_nhan_cho_xep`, `A::test_so_nhap_xuat_dau_vao_dat_ten_theo_nhan_cho_xep` |
| S4 | Trình hướng dẫn tạo workspace (`03`, `07`) | ô tên gợi ý "Trường Trung học A, năm học 2026"; ô nhóm gợi ý "Khối 12 / Khối 11 / Khối 10"; "Suất dự trữ mềm **(như trường học)**"; "Mỗi chỗ một điểm riêng **(như trường học)**" | ví dụ trung tính; nhãn lựa chọn **ngắn**, lời giải thích nằm ngay dưới ô và đổi theo lựa chọn | `G::test_wizard_buoc1_va_buoc3_khong_con_vi_du_cua_truong_hoc`, `A::test_chu_trinh_huong_dan_da_sua…` |
| S5 | Sheet "Hướng dẫn" trong sổ mẫu (`ghi_chu_may.json`) | ví dụ "HS001 Nguyễn Văn An — Tin học, Bóng rổ", "nhóm chinh_sach", "đã thi" | ví dụ "001 … Dự án A, Dự án B"; KPI "đã được chấm" chứ không "đã thi" | `A::test_huong_dan_sheet_khong_con_chu_truong_hoc…`, `A::test_huong_dan_kpi_khong_noi_da_thi`, `A::test_huong_dan_mac_dinh_truong_hoc_khong_doi` |
| S6 | **Mã buổi nội bộ** hiện ra người dùng: chip và ô "Từ … đến" ở thẻ Vận hành (`10`, `16`), bảng ở thẻ Kết quả, thẻ Quản lý, cảnh báo dữ liệu ("**Phiên phien_1** có tổng 12 chỗ"), mọi trang Excel | `phien_1`, `phien_2` | "Phiên 1", "Phiên 2" (giá trị gửi đi vẫn là mã; cảnh báo gộp "phiên Phiên 1" thành "phiên 1") | `G::test_su_kien_ten_phien_doc_duoc…`, `A::test_ten_buoi_*`, `A::test_cau_loi_hien_ten_phien…` (JS == Python từng chữ), `A::test_xlsx_su_kien_ten_phien_dep_o_moi_trang` |

### 2.2 Nhãn đọc dở

| # | Ở đâu | Trước | Sau | Test |
|---|---|---|---|---|
| L1 | Trình hướng dẫn, bước 3 (`07`) | "Số **mục dự thi** tối đa mỗi đợt" — không ai biết "mục dự thi" là gì | "Số chỗ mỗi người được chọn dự thi, tối đa mỗi đợt" + một dòng giải thích khi nào dùng; **ẩn** khi không có điểm riêng từng chỗ | `G::test_wizard_chi_theo_nhom…`, `G::test_wizard_diem_mot_nguoi…`, `G::test_wizard_o_du_thi_an_roi_thi_gia_tri_hong…` |
| L2 | Thanh bên (`01`) | khối "Workspace / Trường học" trông như một nhãn, không ai biết bấm vào là đổi hay tạo workspace | "Workspace · bấm để đổi/tạo" | `G::test_nut_workspace_o_thanh_ben_noi_ro…` |

### 2.3 Bước chưa rõ

| # | Ở đâu | Trước | Sau | Test |
|---|---|---|---|---|
| B1 | Bấm **Chạy** khi chưa nạp gì (`12`) | chạy "thành công": "Sắp xếp xong: 0/0 nhân viên có dự án, sau 0 vòng", **ghi thêm một dòng lịch sử** | báo lỗi nói việc cần làm: "Chưa có dữ liệu để sắp xếp: cần ít nhất một nhân viên và một dự án. Hãy nạp Sổ nhập dự án ở phần Nhập dữ liệu trước."; không ghi lịch sử | `G::test_chay_khi_chua_co_du_lieu…` |
| B2 | Ô Cảnh báo dữ liệu khi chưa nạp gì (`10`–`12`) | "Không thấy vấn đề nào. **Dữ liệu đã sẵn sàng.**" | "Chưa có dữ liệu để kiểm tra. Bấm Tải sổ nhập mẫu, điền sổ rồi nạp vào ô phía trên." | cùng test trên |
| B3 | Trình hướng dẫn, bước 3 (`08`) — người A phải đoán ba ô tác động lẫn nhau (cách xếp, cách dùng nhóm, phạm vi điểm) | không giải thích; "Chỉ theo nhóm" vẫn cho chọn hai ô vô nghĩa | lời giải thích dưới từng ô; "Chỉ theo nhóm" hiện ghi chú "hai mục … bị bỏ qua, chọn gì cũng không đổi kết quả"; bước 4 (xem lại) bỏ các dòng vô nghĩa. **Không khoá ô** vì test cũ `test_wizard_chon_mau_dien_san_ca_bon_buoc` giữ hành vi chọn được | `G::test_wizard_*` |
| B4 | Thẻ Nhập tại chỗ của workspace **không có bước dự thi** (`23`) | "Làm hai bước: chọn dự án dự thi và xếp hạng…", "Bước 1. Chọn dự án dự thi", "Bước 2…", mỗi thẻ người báo "**Thiếu dự án dự thi**" / "DỰ ÁN DỰ THI: Chưa chọn" | một bước duy nhất "Xếp hạng nguyện vọng"; thẻ người chỉ báo "Đã nhập đủ / Chưa nhập gì" | `G::test_su_kien_the_nhap_tai_cho…`, `G::test_su_kien_the_hoc_vien_khong_bao_thieu_du_thi`, `G::test_cong_ty_thay_the_nhap_kpi…` |
| B5 | Tóm tắt trước khi bấm Nhập (`15`) | "… 614 nguyện vọng · **0 lượt thi**" | bỏ "lượt thi" khi luật không có điểm riêng từng chỗ | `A::test_chu_trinh_huong_dan…` (có khoá `so_nhap_tom_tat_khong_thi`) |

### 2.4 Thông báo lỗi chưa nói cách sửa

| # | Ở đâu | Trước | Sau | Test |
|---|---|---|---|---|
| E1 | Nạp sổ có người khai quá số nguyện vọng ở workspace **một buổi** | "… 4 nguyện vọng ở quý **-**, tối đa 3 mỗi quý. Bớt nguyện vọng của quý này." — dấu "-" là chỗ giữ của "không có buổi" | "Sheet "2. Nhân viên", dòng 7 (NV07): 4 nguyện vọng, tối đa 3. Bớt nguyện vọng cho đủ." (và bản "thi"); nhiều buổi vẫn nói tên buổi đẹp ("Phiên 2") | `A::test_loi_qua_tran_*` (Python, JS, đi hết đường từ sổ thật) |
| E2 | Chạy khi chưa có dữ liệu | không có thông báo | xem B1 | `G::test_chay_khi_chua_co_du_lieu…` |

Các lỗi còn lại đã đọc ở lượt thử (nạp sổ ngành khác, nạp sổ trường học) đều **nói rõ việc cần làm** ("Hãy bấm Tải sổ nhập mẫu, điền vào sổ đó rồi nạp lại", kèm tên hai sheet cần có) nên giữ nguyên.

### 2.5 Bảng kết quả vô nghĩa với ngành

"Nhóm xếp cứng" (`tier_mode = strict` hay `priority = tier`) **bỏ qua suất dự trữ** (`rbda_priority_pipeline.nhom_xep_cung`), nên mọi nơi nói về suất dự trữ chỉ toàn số 0 hay chữ "Thường". Các mục dưới đây áp dụng **chỉ cho workspace nhóm cứng**; trường học mặc định không đổi chữ nào (có test riêng).

| # | Ở đâu | Trước | Sau | Test |
|---|---|---|---|---|
| R1 | Thẻ Kết quả (`19`, `20`) | chú giải "Suất thường / Vào bằng suất dự trữ / Còn trống"; bảng "Suất dự trữ đã dùng"; cột "Loại chỗ", "Nhãn dự trữ" | "Đã xếp / Còn trống"; bảng và cột bị ẩn; cột nhóm mang tên nhóm ("Hạng vé") | `G::test_su_kien_the_ket_qua_khong_con_chu_du_tru` |
| R2 | Thẻ Quản lý (`24`) | "Quản lý dự án **& dự trữ**", ô "Suất dự trữ", "Nhãn dự trữ", bảng có hai cột đó, "Gán nhãn dự trữ…" | "Quản lý dự án & **cấp bậc**", ô và cột dự trữ ẩn, "Gán cấp bậc và xuất hồ sơ nhân viên", "Cấp bậc cần gán" | `G::test_su_kien_the_quan_ly_khong_con_du_tru…`, `G::test_cong_ty_thay_the_nhap_kpi…`, `G::test_truong_hoc_van_day_du_va_doi_qua_lai_khong_dinh_luat` |
| R3 | Lời nhắc khi xuất (`20`, `24`) | "Tệp xuất có **điểm chấm** và số bốc thăm" — workspace **không có điểm** | "Tệp xuất có số bốc thăm của từng khách tham dự. Chỉ chia sẻ cho người phụ trách sắp xếp." | `G::test_su_kien_canh_bao_xuat_khong_noi_toi_diem` |
| R4 | Tệp Excel kết quả (`21`) | cột "Diện trúng tuyển" (Thường/Dự trữ) và "Nhóm dự trữ" ở mọi trang; "Trong đó diện dự trữ", "Chỉ tiêu dự trữ" (cả trong bảng tải theo phiên); mục "SUẤT DỰ TRỮ DÙNG TỚI ĐÂU"; nhóm in dạng mã nội bộ (`quan_ly`, `mid`) | các cột và mục đó bị bỏ; cột nhóm mang tên nhóm ("Hạng vé", "Cấp bậc") và hiện **tên trong luật** ("Quản lý") | `A::test_xlsx_su_kien_nhom_cung…`, `A::test_xlsx_cong_ty_cot_nhom_mang_ten_cap_bac…`, `A::test_xlsx_truong_hoc_van_dung_chu_cu` |
| R5 | **Sổ mẫu** và sổ "dữ liệu đầu vào" xuất ra của workspace **chỉ theo hạng vé** (`11`) | sheet khách có "NV1, **Điểm 1**, NV2, **Điểm 2**…" và hướng dẫn nói về "thi" — đúng ví dụ "cột đã thi trong workspace chỉ có hạng" | không có cột điểm; hướng dẫn gọn, các bước đánh số liền; **vẫn đọc được** sổ cũ có cột điểm bỏ trống | `A::test_sheet_tier_only_khong_con_cot_diem_va_nhap_lai_khong_loi`, `A::test_sheet_chi_theo_nhom_van_doc_duoc_so_cu…`, `A::test_sheet_van_giu_cot_diem_khi_co_diem_theo_cho`, `A::test_so_nhap_mau_su_kien_khong_co_cot_diem…` |
| R6 | Sổ mẫu — chỉ dẫn cho các cột có tên cố định | "Tên CLB và Chỉ tiêu là bắt buộc", "Mã HS là bắt buộc" — người nhân sự không biết "CLB", "HS" là gì | "Cột "Tên CLB" (tên dự án) …", "Cột "Mã HS" (mã nhân viên) …", "NV = nguyện vọng"; ghi rõ cột "Suất ưu tiên" vô tác dụng khi xếp theo thứ hạng | `A::test_huong_dan_sheet_khong_con_chu_truong_hoc_va_giai_thich_cot_co_dinh` |

### 2.6 Lỗi giao diện phát hiện lúc sửa

- `.ws-truong { display:flex }` ghi đè thuộc tính `hidden`, nên ô "số chỗ dự thi" ở trình hướng dẫn không ẩn được. Đã thêm `.ws-truong[hidden] { display:none }` (`G::test_wizard_chi_theo_nhom…`).

## 3. Việc lớn — **chưa sửa**, kèm lý do

Xếp theo mức người dùng mới vướng nặng hay nhẹ.

1. **Không có mẫu theo ngành; chọn "Loại" không điền gì.** Ở bước 1 của trình hướng dẫn, chọn "Công ty" hay "Sự kiện" chỉ gắn nhãn loại: bước 2 vẫn hiện "Học sinh / Câu lạc bộ…" và bước 3 vẫn là luật trường học (`05`, `07`). Chỉ có mẫu dựng sẵn "Trường học". Người A muốn "KPI, cấp cao trước" phải tự chọn đúng tổ hợp ba ô (nhóm trước rồi điểm + nhóm cứng + một điểm cho cả người), người B phải biết "chỉ theo nhóm". *Hướng:* thêm mẫu dựng sẵn "Công ty (KPI + cấp bậc)" và "Sự kiện (hạng vé)" — có thể lấy thẳng `du_lieu_test/bo_cong_ty/config.json`, `bo_su_kien/config.json` — và cho "Loại" điền sẵn nhãn. *Vì sao chưa:* đó là quyết định sản phẩm (mẫu nào, luật mặc định nào) và đụng `workspace.danh_sach_mau` cùng test đếm mẫu.
2. **Lần đầu mở là cả một giao diện "học sinh / CLB".** Phần mềm mở sẵn workspace "Trường học"; người dùng ngành khác phải tự tìm cách đổi (đã thêm lời nhắc ở khối Workspace nhưng chưa đủ). *Hướng:* lần chạy đầu (chưa có workspace do người dùng tạo) mở thẳng bảng chọn, kèm các mẫu của mục 1. *Vì sao chưa:* thay đổi luồng khởi động, cần kiểm bằng pywebview thật (môi trường này không có) và rà lại các test khởi động.
3. **Tiêu đề cột của sổ nhập và CSV vẫn là của trường học:** "Tên CLB", "Mã CLB", "Mã HS", "NV1…", "Suất ưu tiên", "Buổi" (và CSV: `Mã học sinh`, `student_id`…). Chữ hướng dẫn trong sổ đã giải thích nghĩa từng cột (mục R6) nhưng người nhân sự vẫn nhìn thấy "CLB". *Hướng:* cho `so_nhap` **đọc cả hai** tiêu đề (cũ và theo nhãn), ghi theo nhãn. *Vì sao chưa:* tiêu đề cột là **hợp đồng** (CLAUDE.md, bất biến 7): phải đổi cùng bộ đọc, skill `sinh-du-lieu-clb`, `TAI_LIEU_DU_LIEU.md`, mẫu Forms và nhiều test; cần chủ dự án quyết định.
4. **Chữ "workspace"** (tiếng Anh) nằm khắp giao diện tiếng Việt: "Tạo workspace mới", "Tên workspace", khối ở thanh bên. Người nhân sự không có từ này. *Hướng:* chọn một thuật ngữ Việt ("bộ dữ liệu", "đợt xếp"…). *Vì sao chưa:* hàng chục chuỗi trong i18n, test, tài liệu và ảnh chụp chuỗi; cần thống nhất thuật ngữ trước.
5. **"Chọi", "tỉ lệ chọi", "Chọi cao nhất"** là tiếng lóng tuyển sinh (số người trên một chỗ). Ở sự kiện/công ty nên là "tỉ lệ đăng ký / chỗ". Có trong thẻ Kết quả, thẻ Quản lý và cả cột Excel; cột Excel là hợp đồng với script đo.
6. **Trang Excel "Thống kê" và "Dấu vết" cho workspace một buổi** vẫn có cột "Quý" toàn "—", và dòng "Số quý lần chạy này phủ: 1", "Quý đã chạy: —". Bảng này dùng chung với tệp tổng hợp CSV nên bỏ cột thì đổi cả CSV.
7. **Sổ mẫu vẫn có cột "Suất ưu tiên" và cột nhóm ở sheet dự án/workshop** khi nhóm xếp cứng (cột vô tác dụng; hướng dẫn đã nói "để trống"). Bỏ cột sẽ dịch vị trí cột và các ô kiểm tra dữ liệu, và làm sổ xuất ra mất giá trị đã nạp (dù vô tác dụng).
8. **Từ vựng thuật toán** ("Số khởi tạo bốc thăm", "Bốc thăm lại…", "Khoá số bốc thăm") chưa có một câu giải thích ngắn cho người không biết "bốc thăm một lần dùng chung". Cần viết bằng giọng của từng ngành.
9. **Thẻ "Nhập tại chỗ" (kiosk)** là tên của riêng trường học; ở công ty/sự kiện nó là "nhập tay từng người". Chưa đổi tên thẻ vì tên nằm trong ảnh chụp chuỗi và tài liệu.
10. **Thẻ Kết quả gấp sẵn** các bảng (danh sách xếp, nhân viên chưa có chỗ…): người mới mở ra chỉ thấy các con số tóm tắt và phải bấm "Mở rộng tất cả" mới thấy danh sách. Là lựa chọn thiết kế có chủ ý (nhiều bảng dài), nên chỉ ghi lại.
11. **Trình hướng dẫn bước 2 đòi cả tiếng Việt lẫn tiếng Anh cho năm danh từ** trước khi người dùng thấy gì (ô tiếng Anh để trống thì dùng tiếng Việt, đã ghi). Với người chỉ dùng tiếng Việt thì thừa; cân nhắc gập phần tiếng Anh lại.

## 4. Còn lại để kiểm

- Chưa thử bằng **pywebview/WebView2 thật** (môi trường không có); mọi thứ ở trên chạy qua chế độ dự phòng trình duyệt, vốn dùng cùng `index.html` và cùng lớp `PipelineAPI`.
- Chưa thử ngôn ngữ **tiếng Anh** đầu-cuối qua trình duyệt; chuỗi mới có đủ vi/en và có test đối xứng JS–Python, nhưng chưa có ảnh chụp bản tiếng Anh.
- Hai người A và B dùng **sổ đã điền sẵn** của bộ mô phỏng; chưa thử người mới **tự điền tay** sổ mẫu (chỗ dễ vấp nhất: gõ sai tên dự án, bỏ trống mã).
