# CHANGELOG

## 2026-10-16 — Trang thi 12 CLB: xuất sổ nhập .xlsx và chỉ tiêu (demo, ngoài sổ đăng ký)

Dữ liệu mô phỏng. Phạm vi thu hẹp theo yêu cầu: chỉ cần tệp xuất nhập được vào kiosk và trang chạy được trên Vercel.
- **Chỉ tiêu.** Trang giáo viên có ô chỉ tiêu cho 60 CLB, nhận số nguyên từ 1 đến 999, bắt buộc. Thiếu hoặc sai thì cả nút `.xlsx` và nút CSV "1. CLB" đều bị chặn và báo rõ CLB nào.
- **Sổ nhập .xlsx.** Nút "Tải sổ nhập (.xlsx)" tạo `SO_NHAP_CLB.xlsx` với hai trang `1. CLB` và `2. Học sinh` theo `so_nhap.py` (`COT_CLB`, `COT_HS_DAU`). Điểm từng CLB lấy từ `chamTheoCLB`. Tên CLB ở trang `1. CLB` lấy trực tiếp từ dữ liệu đề (hiện không có tên trùng).
- **Không thêm thư viện.** Bộ ghi `.xlsx` viết bằng JavaScript thuần: gói ZIP không nén, CRC-32 tính tay, ô chữ dạng `inlineStr`.
- **Kiểm.** Test `test_bo_ghi_xlsx_doc_duoc_bang_openpyxl`: openpyxl đọc đúng từng ô, kể cả `&`, `<` và chữ bắt đầu bằng `=`. Test Chromium: xuất bị chặn khi thiếu chỉ tiêu; sau khi nhập thì tệp xuất qua `so_nhap.doc_so_nhap` không có lỗi; HS 101 có điểm 10 và 5. Ký tự điều khiển trong tên, điểm 0 (phải là ô số 0, không phải ô trống), và các chỉ tiêu sai (`0`, `-1`, `2.5`, `1e3`, `007`, `1000`, khoảng trắng) đều có test. Tệp xuất được đọc bằng `read_only` như kiosk.
- **Tách trang.** `index.html` cho học sinh, không có phần giáo viên. `giao_vien.html` cho giáo viên. Cả hai sinh từ một khuôn. Hàm chấm vẫn nằm trong mã của trang học sinh nhưng không có giao diện nào dùng đến.
- **Ký tự điều khiển.** Bộ ghi `.xlsx` bỏ các ký tự điều khiển không hợp lệ trong XML (ví dụ dấu ngắt mềm chép từ Word), để một ô lỗi không làm hỏng cả sổ.
- **Chưa kiểm.** Chưa mở tệp bằng Excel thật (lần rà soát độc lập đã mở bằng LibreOffice). Đáp án vẫn nằm trong HTML, ai xem mã nguồn cũng thấy. Phiếu `.json` không có chữ ký nên có thể bị sửa trước khi gửi. `giao_vien.html` không có xác thực.
- **Triển khai.** Chỉ tải thư mục `docs/thi_12_clb/` (gồm `index.html` và `giao_vien.html`) lên Vercel như dự án tĩnh, không tải mã nguồn.
- Sinh lại: `python mau_forms_thi_clb/tao_trang_thi_12_clb.py`.

## 2026-10-16 — Trang thi 12 CLB mỗi buổi: học sinh chỉ làm đề của CLB đã chọn (ngoài sổ đăng ký, theo yêu cầu chủ dự án)

Dữ liệu mô phỏng. `docs/thi_12_clb/index.html` là một tệp HTML tự chứa (không CDN, không máy chủ), do
`mau_forms_thi_clb/tao_trang_thi_12_clb.py` sinh ra từ `mau_forms_thi_clb/de_thi_12_clb.py`. Không sửa tay.
- **Dữ liệu.** Năm buổi, mỗi buổi 12 CLB, tổng 60 CLB; mỗi CLB 2 câu. 50 CLB đầu lấy từ bộ mẫu (không đổi).
  10 CLB mới (2 mỗi buổi, 20 câu) có `nhap=True`: **bản nháp do trợ lý soạn, chưa được giáo viên duyệt**, không dùng
  cho thi thật khi chưa duyệt. Sau rà soát, hai nhiễu vô lý (Khiêu vũ Q2, Ảo thuật Q2) đã được thay. Giáo viên cần soát thêm: Đàn tranh Q1 (16 hay 21 dây tuỳ loại đàn), Cắm hoa Q2 (câu hỏi ý kiến), Đấu kiếm Q1 (nhiễu "Ánh sáng"). Biểu mẫu Google Forms và `TAO_GOOGLE_FORM.gs` không đổi (vẫn 50 CLB, 212 câu).
- **Luồng học sinh.** Xếp Top 1–10 (thả xuống, không bắt buộc); tick tối đa 5 CLB mỗi buổi (có thể 0 đến 5);
  chọn CLB làm bài trước trong số CLB đã tick; làm đề của CLB đó; CLB tiếp theo chỉ là CLB đã tick và đứng sau CLB
  vừa làm; hết thì chọn "Em không thi thêm CLB nào buổi này". Đề của CLB không được chọn không được dựng trong trang.
- **Khác biểu mẫu Google.** Trang chỉ đưa ra CLB đã tick ở bước chọn đầu và bước tiếp theo (biểu mẫu đưa mọi CLB
  đứng sau). Trang chỉ có Top 1–10 (10 ô xếp); CLB không nằm trong Top 1–10 không được tính điểm, theo `chamTheoCLB`.
- **Nộp và giáo viên.** Khi nộp, trình duyệt tự tải tệp phiếu `.json`; học sinh thấy "đã nộp" và được dặn gửi tệp
  cho giáo viên. Việc gửi phiếu là thủ công (tạm thời). Phiếu có thời điểm nộp (`nop_luc`); giáo viên được chấm theo thời điểm đó, nên "giữ phiếu đầu" là bản nộp sớm nhất, không phụ thuộc thứ tự chọn tệp. Tệp trùng nội dung được bỏ. Trang giáo viên nạp nhiều tệp phiếu, hiện bảng và cảnh báo;
  tải trang "1. CLB" và "2. Học sinh" dưới dạng CSV (có BOM, trích dẫn đúng) để dán vào `SO_NHAP_CLB.xlsx`. Chưa kiểm
  được nạp thẳng vào phần mềm; chỉ tiêu, suất ưu tiên và nhóm ưu tiên của "1. CLB" phải điền tay.
- **Tệp sửa tay.** Trang chỉ cho Top 1–10, nhưng phiếu có thể bị sửa: trang giáo viên bỏ Top 11 trở lên trước khi
  chấm và báo mã học sinh bị bỏ.
- **Mã và ô CSV.** Mã học sinh toàn khoảng trắng bị chặn ở trang học sinh (trước đây phiếu qua được rồi bị bỏ khi chấm). Ô CSV bắt đầu bằng `=`, `+`, `-`, `@` được thêm dấu nháy đơn, cùng quy tắc với `api_chung.py`.
- **Đáp án.** Đáp án 20 câu mới được xáo bằng đúng `tg.xao` của bộ mẫu. Nếu không xáo, đáp án đúng nằm ở vị trí đầu
  trong 16/20 câu và học sinh chọn đầu được 80% điểm mà không cần biết bài.
- **Chấm.** Dùng lại khối LOGIC của `tao_website_mau.py`, đã đối chiếu với `.gs` trên chín kịch bản phiếu.
- **Giới hạn.** Khoá đề chỉ là khoá trong giao diện: mã nguồn đọc được. Không đăng nhập, không kiểm danh.
- **Kiểm.** `tests/test_trang_thi_12_clb.py` (16 test): 60 CLB, 12 mỗi buổi, 2 câu mỗi CLB, mã và tên không trùng,
  10 CLB nháp, đáp án CLB mới đã xáo; tệp khớp bản sinh lại; mọi câu chữ trợ giúp đang hiển thị có trong `.gs`; logic trùng
  `chamTheoCLB` của `.gs` trên chín kịch bản; kịch bản riêng của 12 CLB: không thi CLB nào (không điểm, không cảnh
  báo), thi CLB không xếp Top (không điểm, có cảnh báo). Chromium (luồng chính ở 390px): chỉ đề CLB đã chọn được dựng; tick tối đa 5; mã trống bị chặn;
  CLB tiếp theo chỉ là CLB đứng sau; nộp tự tải phiếu; nộp lại chấm theo thời điểm nộp, tệp trùng bị bỏ; điểm trong CSV đúng (10 và 5); Top 11 bị bỏ; ô công thức có dấu nháy; sổ "1. CLB" đủ
  60 dòng; không tràn ngang.
- **Rà soát.** Một vòng rà soát có kiểm chứng (ba góc nhìn, ba người phản bác mỗi lỗi) tìm được các lỗi nêu trên và đã
  sửa. Các phát hiện bị bác bỏ không được sửa; trong đó có chất lượng đề và câu chữ đã được giáo viên duyệt ghi chú.
- Sinh lại: `python mau_forms_thi_clb/tao_trang_thi_12_clb.py`.

## 2026-10-16 — Trang web mẫu đăng ký CLB: giới thiệu và mô phỏng biểu mẫu (ngoài sổ đăng ký, theo yêu cầu chủ dự án)

Dữ liệu mô phỏng. `docs/website_mau/index.html` là một tệp HTML tự chứa (không CDN, không máy chủ), do
`mau_forms_thi_clb/tao_website_mau.py` sinh ra từ cùng dữ liệu đề với `TAO_GOOGLE_FORM.gs`.
- **Nội dung.** Phần giới thiệu quy trình và quy tắc so trùng mã. Phần mô phỏng đúng bản Google hiện tại:
  Top 1–10 thả xuống, tick tối đa 5 CLB, thi lần lượt, "Không thi thêm", chữ trợ giúp lấy từ cùng nguồn.
  Phần sổ nhập mẫu chấm bằng quy tắc của `chamTheoCLB` (khoá so trùng chỉ bỏ khoảng trắng; hoa thường giữ
  cả hai và có cảnh báo) và hiện bảng "1. CLB", "2. Học sinh", "Cảnh báo".
- **Không làm.** Không chạy xếp CLB trên trang; không thay thế Google Forms thật; không gửi dữ liệu đi đâu.
- **Kiểm.** `test_trang_web_mau_khop_tep_da_sinh` (tệp khớp bản sinh lại); `test_trang_web_dung_cau_tro_giup_cua_bieu_mau`
  (chữ trợ giúp có nguồn trong `.gs`); `test_trang_web_cham_giong_chamtheoclb` (Node: chín kịch bản phiếu, so hàng
  học sinh và cảnh báo của trang với `chamTheoCLB`). Kiểm tay bằng Chromium: một phiếu đầy đủ, nộp, ba phiếu mẫu,
  không tràn ngang ở 390px.
- Sinh lại: `python mau_forms_thi_clb/tao_website_mau.py`.

## 2026-10-15 — Biểu mẫu Google Forms CLB: sáu điểm Cao và Trung của bản phân tích (ngoài sổ đăng ký, theo yêu cầu chủ dự án)

Nguồn: bảng "Điểm cần cải thiện", mục 1–6, của sơ đồ biểu mẫu. Số liệu là dữ liệu mô phỏng.
- **Mục 1, khoá so trùng mã học sinh (sửa).** `chamTheoCLB` (`mau_forms_thi_clb/tao_google_forms.py`, khuôn `MAU`) và
  `xu_li_raw.py` so trùng bằng khoá chỉ bỏ khoảng trắng (đúng bộ `\s` của JavaScript): `HS 001` và `HS001` là một
  người, và mã ghi ra là mã đã gõ của phiếu đầu. Không gộp hoa thường: kiosk coi `HS001` và `hs001` là hai em
  (`mau_csv/vi_du_day_du/GIAI_THICH.md`), nên hai phiếu chỉ khác hoa thường được giữ cả hai và có cảnh báo
  `ma_khac_hoa_thuong` để giáo viên soát. Email gom mã theo cùng khoá. Kiểm: `test_ma_chi_khac_khoang_trang_la_mot_hoc_sinh`
  và `test_ma_chi_khac_hoa_thuong_giu_ca_hai_va_canh_bao` (Node), `test_ma_chi_khac_khoang_trang_la_nop_trung`,
  `test_ma_chi_khac_hoa_thuong_giu_ca_hai_va_bao_cao` và `test_khoang_trang_khop_giua_skill_va_apps_script`
  (đối chiếu mọi mã điểm Unicode với JavaScript). `DINH_DANG_RAW.md` mục 3 và mục 6 cập nhật.
- **Mục 3 và 5, chữ trợ giúp trên form (sửa).** Trang Top, ô tick, câu "thi CLB nào trước" và "CLB tiếp theo" nêu rõ
  điều kiện được chấm điểm và thứ tự chọn. Câu chọn CLB đầu nói rõ "đứng đầu danh sách, không phải Top 1" và cách chọn "Em không thi CLB nào buổi này";
  trang Top chỉ nhắc ô tick ở buổi có CLB thi. Kiểm: `test_google_forms_noi_ro_dieu_kien_duoc_cham_diem`. Tiêu đề câu hỏi không đổi.
- **Mục 2, gõ nhầm mã (chỉ tài liệu, cần kiểm).** `HUONG_DAN_TUNG_BUOC.md` thêm dòng xử lí: xoá đúng phiếu, học sinh nộp lại.
  Chưa xác nhận được sau khi xoá học sinh có nộp lại được không. Không tự bật `setLimitOneResponsePerUser` hay
  `setCollectEmail`: hai cài đặt này đổi ai được nộp, và cần quyết định của nhà trường.
- **Mục 4, công bố điểm (chỉ tài liệu).** Bước 2.2 của hướng dẫn thành "bắt buộc trước khi gửi", thêm bước 5 kiểm lại trước khi gửi.
  Không thêm lệnh Apps Script về công bố điểm vì chưa kiểm được API.
- **Mục 6, chặn trùng nguyện vọng (chưa sửa).** Cần quyết định của tác giả: vì sao biểu mẫu đã bỏ lưới. Chưa đổi.
- **Không đổi** cột CSV, hợp đồng raw, hay `dem_cau` (212 câu). Sinh lại `TAO_GOOGLE_FORM.gs` và `HUONG_DAN_TUNG_BUOC.md`
  bằng đúng khuôn; vòng tròn skill và `test_ma_google_forms_khop_du_lieu` vẫn khớp.
## 2026-10-15 — Google Forms: kết quả chấm thành MỘT tệp SO_NHAP_CLB.xlsx (ngoài sổ đăng ký, theo yêu cầu chủ dự án)

`chamTheoCLB` trước đây ghi bốn tệp (BANG_DIEM, SO_NHAP_CLB, RAW_PHIEU, DAP_AN). Nay chỉ ghi một tệp
`SO_NHAP_CLB.xlsx` với sáu trang: `1. CLB`, `2. Học sinh` (phần mềm nạp), `Bảng điểm`, `Cảnh báo`, `Raw`, `Đáp án`.
- **Khuôn mẫu.** `mau_forms_thi_clb/tao_google_forms.py`: gộp vào một bảng tính rồi xuất một lần; bỏ `taoTepNap_`,
  `taoSoNhap_`. `TAO_GOOGLE_FORM.gs` sinh lại từ khuôn, không sửa tay.
- **Bộ xử lý raw.** `xu_li_raw.py` đọc trang `Raw` và `Đáp án` từ tệp gộp; tệp `RAW_PHIEU.xlsx` / `DAP_AN.xlsx`
  rời vẫn chạy như cũ. Thêm chốt chặn: `--ra` trùng tệp đầu vào thì dừng, không ghi gì.
- **Tài liệu.** `tao_form.py` (HUONG_DAN_TUNG_BUOC.md sinh lại), `tao_huong_dan_google.py`,
  `tao_huong_dan_toan_bo.py`, `SKILL.md` của xu-li-raw-forms, `DINH_DANG_RAW.md`, `dong_goi_skill.py`.
  `docs/PROMPTS_WORKSPACE.md` và `chuyen_forms_sang_phan_mem.py` (công cụ Python riêng, còn ghi `BANG_DIEM.xlsx`) giữ nguyên.
- **Test mới.** `tests/test_so_nhap_gop_sau_trang.py`: 500 học sinh, tệp sáu trang nạp vào phần mềm thật, không
  cảnh báo, chạy được phân bổ; và chặn ghi đè. `tests/test_skill_xu_li_raw.py`: tệp gộp cho cùng kết quả như hai
  tệp rời. Cập nhật hai chỗ khoá tên tệp cũ trong `test_mau_forms_thi_clb.py` và `test_skill_tao_google_form.py`.
- **Chưa kiểm được.** Apps Script thật (chỉ kiểm bằng bản giả lập Node). Dữ liệu là mô phỏng, học sinh hư cấu.

## 2026-10-15 — Workspace: Việt hoá sạch màn chọn và sửa bảng (ngoài sổ đăng ký, theo yêu cầu chủ dự án; chồng lấn Z1)

Ở giao diện tiếng Việt, màn chọn workspace còn "workspace" và ".zip" lẫn trong câu, và bảng bị vỡ.
Giao diện tiếng Anh giữ nguyên chữ cũ. Không đổi backend, thuật toán hay hợp đồng `{ok, data, errors}`.
- **Chữ tiếng Việt.** "workspace" → "không gian làm việc"; ".zip" → "tệp nén" (nút Xuất tệp nén / Nhập tệp nén,
  câu nhắc, thông báo). Sửa trong `i18n.js` (khối `vi`, các khoá `ws_*`), `i18n_errors.py` (sáu mã `ws_*` và bốn
  câu có "Workspace này"), `index.html` (chữ mặc định của nút thanh bên); `i18n_loi.js` sinh lại bằng
  `tao_i18n_js.py`. "thư mục _trash" giữ nguyên vì là tên thư mục thật trên đĩa.
- **Chuỗi do backend đặt, không đổi theo ngôn ngữ.** Tên mẫu dựng sẵn "Trường học" nay dịch ở JS theo khoá mới
  `ws_mau_truong_hoc` (vi "Trường học", en "School"); cột "Sửa lần cuối" hiện `15/10/2026 12:19:20` ở tiếng Việt,
  giữ `2026-10-15 12:19:20` ở tiếng Anh (`js/075_workspace.js`: `wsTenMau`, `wsDinhDangNgay`).
- **Bảng.** `display:flex` đặt thẳng lên `<td>` làm ô mất kiểu `table-cell`: nền hàng "Đang mở" dừng giữa chừng,
  đường kẻ lệch, nút Xoá rớt dòng. Nay `<td class="ws-cot-hanh-dong">` chứa `<div class="ws-hanh-dong">` (flex);
  hộp thoại rộng 1040px; cột Tên về font chữ thường (trước đó dùng font mã của `.data-table td:first-child`);
  `select` / `textarea` trong trình hướng dẫn kế thừa font. Màn hẹp thì sáu nút xuống dòng gọn trong ô.
- **Test mới (viết trước, thấy đỏ rồi mới sửa).** `tests/test_giao_dien_tieng_viet_sach.py`: thêm "workspace" vào
  danh sách cấm và một test quét thô chữ "zip". `tests/test_ws_giao_dien.py`: tiếng Việt không còn
  workspace/zip ở màn chọn và cả bốn bước hướng dẫn; tiếng Anh không còn chữ có dấu tiếng Việt ở màn chọn và ba
  bước đầu; tên mẫu và ngày đổi theo ngôn ngữ; bảng vẽ đúng (ô hành động là `table-cell`, mọi ô cao bằng hàng,
  sáu nút một dòng, nền phủ cả hàng, tên không dùng font mã).
- **Ảnh chụp chuỗi làm mới có chủ đích.** `tests/du_lieu_ws/chuoi_truoc_khi_co_nhan.json`: chỉ 24 chuỗi `vi` đã đổi
  (5 mã lỗi `ws_*`, 19 khoá `ws_*` của giao diện); `test_ws_nhan.py` vẫn so toàn bộ phần còn lại như cũ.

## 2026-10-15 — Skill `tao-workspace-tu-raw` và hai bộ dữ liệu thử (ngoài sổ đăng ký, theo yêu cầu chủ dự án)

- **Skill mới `.claude/skills/tao-workspace-tu-raw/`**: raw bất kỳ (Excel/CSV tự do, Google/Microsoft Forms, hai
  tệp tách rời, văn bản dán) → workspace `.zip` nạp sẵn dữ liệu + Sổ nhập theo nhãn + `BAO_CAO_SOAT.md`.
  Bốn dạng nguyện vọng (`cot_xep_hang`, `mot_o`, `dong_dai`, `ma_tran`), đủ luật workspace, điểm theo chỗ / theo
  người. Đoán rồi hỏi duyệt; chỉ tiêu bắt buộc hỏi; sai một điều không ghi tệp nào; kiểm bằng `import_so_nhap` +
  báo cáo sức khoẻ + chạy thử; từ chối ghi đầu ra vào kho git (dữ liệu người thật). Không đụng mã sản phẩm.
  Test: `tests/test_skill_tao_workspace.py` (21 ca).
- **Bộ dữ liệu thử (mô phỏng)**: `du_lieu_test/bo_thu_chuong_trinh/` (trường 3 buổi, 180 học sinh) và
  `du_lieu_test/bo_thu_workspace/` (workspace "Công ty Bình Minh", zip nạp sẵn, kèm script sinh lại).

## 2026-10-14 — Sửa lỗi CI Windows của PR #1 (24 test đỏ; Linux đạt)

Bộ test Windows đỏ 24 ca trong khi Linux xanh. Hai nguyên nhân, một thật của sản phẩm và một của test:
- **Lỗi sản phẩm — `connect_db` rò kết nối khi tệp không phải SQLite.** PRAGMA đầu tiên ném mà kết nối chưa
  được đóng. Trên Linux không ai hay; trên Windows tệp đang mở không dời / xoá / đổi tên được (WinError 32 / 5),
  nên **xoá một workspace hỏng, nhập zip có `app.db` hỏng (thư mục tạm không dọn được), di trú `app.db` cũ hỏng**
  đều hỏng đúng lúc người dùng cần. Nay `connect_db` đóng kết nối rồi mới ném lại. Bộ dò
  `tests/test_ws_ket_noi_dong.py` bắt lỗi kiểu này NGAY TRÊN LINUX (kết nối bị huỷ mà chưa `close()`), và phủ các
  đường workspace / zip / di trú / chạy xếp. Vì sao Linux không thấy: kết nối sqlite3 của CPython 3.11 nằm trong vòng
  tham chiếu vòng (bộ nhớ đệm câu lệnh) nên chỉ nhả tệp khi GC chạy.
- **Lỗi của test.** (1) `with sqlite3.connect(db) as c` chỉ commit, KHÔNG đóng — các helper của
  `test_ws_registry.py` / `test_ws_sua_loi_3.py` nay dùng `contextlib.closing`. (2) Tiến trình con của
  `test_tham_khao_verify_nhanh.py` in tiếng Việt ra cp1252 nên `UnicodeEncodeError`: nay chạy `python -X utf8` và
  đọc đầu ra bằng UTF-8 (tái hiện được trên Linux bằng `LC_ALL=C PYTHONUTF8=0 PYTHONCOERCECLOCALE=0`: 33 ca đỏ
  trước, 0 sau). (3) So đường dẫn bằng `'/'` ghép tay: dùng `os.path.join`. (4) `write_text` / `open(..., "w")` thiếu
  `encoding="utf-8"` với nội dung tiếng Việt.

## 2026-10-14 — Workspace: vòng sửa lỗi thứ ba (hai lượt /code-review cuối, trước khi gộp vào main)

Mỗi mục có test trong `tests/test_ws_sua_loi_3.py` (viết trước, đỏ trước khi sửa):
- **Đọc cấu hình NGHIÊM ở nơi quyết định.** `run_pipeline`, `check_data_integrity`, trần nguyện vọng / thi
  (nhập tay, CSV, sổ), chấm điểm theo CLB đọc bằng `doc_cau_hinh(nghiem=True)` (`PipelineAPI._luat_nghiem`).
  Cấu hình có mà đọc không được (JSON hỏng, khoá của bản khác, CSDL bị khoá) thì dừng với lỗi mới
  `ws_cau_hinh_hong`, không lặng lẽ chạy bằng luật trường học rồi ghi `luat_xep = NULL`. `get_data_health_report`
  vẫn trả báo cáo nhưng thêm cảnh báo mức cao. `run_pipeline` đọc cấu hình MỘT lần (trước: hai lần, hai kết
  nối). Không có hàng cấu hình = mặc định, như cũ.
- `workspace.nhap_zip`: cấu hình trong zip đọc không được thì từ chối cả zip (trước: ghi mặc định đè lên luật thật).
- `update_workspace_config`: cập nhật MỘT PHẦN giữ nguyên phần không nhắc tới (`cau_hinh_ws.tron_len`); trước
  đây trộn lên mặc định trường học nên `{"name": "X"}` đặt lại mọi luật. Cấu hình cũ hỏng thì từ chối.
- `reset_student_entry` ("Sửa lại từ đầu") KHÔNG xoá `diem_ca_nhan` nữa (điểm do giáo viên chấm, không gắn
  với ô tick). *Đổi hành vi so với bản trước; test cũ đổi theo.*
- `delete_workspace` trên workspace "mở tạm" chuyển `db_path` sang workspace còn lại (không để trỏ vào `_trash`).
- `submit_club_scores` từ chối (`scoring_not_per_slot`) khi workspace chấm theo người hoặc `priority = tier`;
  CSV có điểm ở các chế độ đó: không lưu, cảnh báo `csv_score_ignored_mode`.
- Dấu vân tay kết quả, `run_history.luat_xep` và `run_full_pipeline` dùng luật HIỆU LỰC
  (`luat_xep_hieu_luc`): danh sách nhóm khi nhóm không cứng, `score_scope` khi chỉ theo nhóm... không còn
  làm kết quả báo "cũ". Luật mặc định không đổi (vân tay cũ giữ nguyên).
- Sổ nhập: cột điểm sai kiểu chấm (cột "Điểm k" ở workspace chấm theo người, hoặc cột "Điểm" đơn ở workspace
  chấm theo CLB) mà có dữ liệu thì báo `so_nhap_diem_sai_che_do` (trước: bỏ lặng lẽ, điểm mất).
- `xuat_zip` không nén chính zip đích (nằm trong thư mục workspace) và bỏ mọi `*.zip` trong thư mục.
- `main.khoi_dong_workspace`: bỏ qua workspace hỏng khi còn workspace lành (không còn rơi vào màn phục hồi vì một
  workspace hỏng); chỉ khi không cái nào mở được mới ném `WorkspaceKhoiDongHong(db_path)` cho màn phục hồi. Màn
  phục hồi dùng đúng tệp hỏng, hoặc workspace gần nhất khi `app.db` cũ đã di trú (trước: trỏ vào `app.db` không
  còn, "bắt đầu lại" đẻ ra tệp mồ côi).
- Nhóm cứng: nhập CSV không còn cảnh báo `csv_reserve_group_unknown` cho tên nhóm.
- Dọn: bỏ `main.chon_db_path` (chỉ test dùng) và khoá `bo_diem` của `tham_so_luat` (không ai đọc); tên trang
  Excel của tệp xuất dùng chung `so_nhap._ten_sheet`; docstring `cau_hinh_ws.py` nói đúng việc cấu hình
  nối vào thuật toán.
- `docs/ke_hoach/TIEN_DO.md`: thêm hàng WS (ngoài sổ) và ghi chú chồng lấn ở Z1, Z2 (chưa đóng mục).
- Hai việc còn lại sau vòng này (cùng ngày):
  - Mã lỗi riêng `ws_cau_hinh_hong` ở MỌI chỗ phụ thuộc cấu hình (trước chỉ ở chạy xếp / kiểm tra dữ liệu / báo
    cáo sức khoẻ; còn lại ra lỗi chung): nhập tay nguyện vọng và thi, nhập CSV, chấm điểm theo CLB và theo
    người, đọc / xem trước sổ nhập, tạo sổ mẫu, xuất dữ liệu đầu vào, hồ sơ học sinh, trạng thái kết quả. Bố
    cục sổ và tệp xuất cũng đọc cấu hình NGHIÊM (trước: đoán bằng mặc định trường học). Nhãn hiển thị vẫn
    đọc dễ tính. Test: `tests/test_ws_sua_loi_3.py` (mục P).
  - Màn phục hồi lúc khởi động được kiểm bằng `main.main()` thật và Chromium thật
    (`tests/test_ws_phuc_hoi.py`): đúng tệp hỏng trong thư mục workspace, thấy bản sao lưu cạnh nó, bấm
    "Khôi phục" đưa workspace về đúng dữ liệu, lần khởi động sau vào giao diện chính, và lỗi không nêu tệp thì
    dùng workspace gần nhất chứ không phải `app.db` cũ đã di trú.

## 2026-10-14 — Workspace: ghép các nhánh và vòng sửa lỗi sau review (/code-review trên 4 nhánh)

Ghép `practical-faraday` (nền), `cool-hamilton` (tài liệu) và `upbeat-ride` vào nhánh này; bản workspace
cũ của nhánh còn ở `backup/nifty-truoc-khi-ghep`. Sửa các lỗi còn lại, mỗi lỗi một test
(`tests/test_ws_sua_loi_2.py`):
- `workspace.xoa`: workspace có `app.db` hỏng vẫn xoá được (sao lưu rơi về chép tệp thô, rồi dời vào `_trash`).
- `workspace.nhap_zip`: trần 500 MB giải nén cho cả zip, đếm BYTE THẬT khi chép (tiêu đề zip khai sao cũng
  được); bỏ `app.db-journal/-wal/-shm` và `*.bak-*` trong zip (SQLite tự phát lại nhật ký có sẵn); từ chối mục mã hoá.
- Slug: cắt ở 60 ký tự; `con`, `nul`, `com1`... (tên thiết bị Windows) thành `ws-<tên>`.
- `delete_workspace`: workspace "mở tạm" lúc khởi động nhiều workspace (người dùng chưa chọn) xoá được.
- `run_history.luat_xep` (cột mới, `ADD COLUMN`, không dựng lại bảng): JSON luật xếp đã dùng; NULL = luật mặc
  định của trường học (dòng cũ và workspace mặc định không đổi). `get_run_history` trả cột này.
- `run_full_pipeline` (đường thử nghiệm) từ chối chạy khi workspace có luật khác mặc định, thay vì xếp sai
  âm thầm.
- Nhãn workspace bắt đầu bằng `=`, `+`, `-`, `@` bị từ chối (`cau_hinh_ws.chuan_hoa`): nhãn thành tiêu đề cột / tên
  sheet của Sổ nhập, và openpyxl ghi `=...` thành ô công thức thật; nhãn có thể đến từ zip nhập vào. Cấu hình
  như thế đọc lại ra mặc định.
- Test giao diện `test_moi_o_so_tren_man_hinh_cap_nhat_ngay_sau_khi_xoa` hết chập chờn: `#lastRunLine` và
  `#statStudents` do hai lời gọi API riêng điền, test từng assert ngay mà không chờ. Nay chờ `#lastRunLine`, và
  làm chậm `get_last_run_info` 600 ms để thứ tự trả về là chắc chắn (bản assert ngay đỏ ổn định với độ trễ này).
- `docs/ke_hoach/tham_khao`: `verify_stability_nhanh` nhận `bo_qua_du_tru`; bộ nạp `_chung.nap_rb` nạp thêm
  `nhan_ws` (từ bản có workspace, `i18n_errors` import nó), bản build cũ không có thì vẫn nạp được.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng S (/code-review trên vòng R: 6 điểm, không lỗi đúng/sai — vòng sạch)

- Không sửa hành vi. Ba điểm "móc lỗi chặn cả `import json`" là đúng hành vi: tệp `json.py` cạnh mã vẫn che được
  `json`, và lần chạy thật (thư mục đứng đầu sys.path) cũng hỏng ở chính móc đó — sai là ở LỜI: dòng CHANGELOG
  vòng R và chú thích test ghi "thư viện chuẩn" thay vì "dựng sẵn / đóng băng". Đã sửa lời (đánh dấu tại chỗ),
  docstring `_tu_thu_muc` (dòng tóm tắt còn ghi "nghi ngờ thì coi là có"), và thêm ca `import json` bị từ chối
  vào test làm chốt (228 ca, 2 bỏ qua tuỳ môi trường).
- `_khong_the_bi_che` nhớ theo tên (`functools.cache`).
- Bác: tên đã có trong `sys.modules` của tiến trình đo — `sys.modules` của lần chạy thật là của tiến trình khác;
  chỉ đáng kể khi có móc đường dẫn hỏng, đã báo lỗi rõ.
- Vòng lặp 2 dừng tại đây theo tiêu chí "một vòng không còn lỗi đúng/sai được xác nhận".

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng R (/code-review trên vòng Q: 6 điểm, sửa 5, bác 1)

Không điểm nào làm phép đo chạy nhầm mã; đều là chẩn đoán, độ chặt của test và một ca từ chối thừa hiếm gặp.
- `_chung`: lỗi khi xét một tên (móc đường dẫn hỏng với thư mục, lỗi trong bộ tìm / PathFinder) -> SystemExit nêu
  đúng tên và lỗi gốc, thay vì báo nhầm thành "mô-đun anh em"; lỗi móc với thư mục chỉ nêu khi thật sự cần xét
  một tên (mã chỉ import mô-đun dựng sẵn / đóng băng không bị chặn; *sửa ở vòng S: bản đầu ghi nhầm
  "thư viện chuẩn"*).
- Luật "dựng sẵn / đóng băng không bị che" còn một chỗ, đứng trước phép xét thư mục trong `la_ten`.
- Test (227 ca, 2 bỏ qua tuỳ môi trường): bộ tìm cài thêm ghi mọi tên ngoài thư viện chuẩn (không chỉ hai tên);
  ca lỗi PathFinder kiểm cả lỗi gốc và đặt mục lỗi cuối sys.path; 1 ca mới. 3 ca thất bại với bản vòng Q.
- Bác: PathFinder chạy các móc đường dẫn trên sys.path khi xét phần namespace — đó chính là việc mọi import của
  mã được đo làm trong cùng tiến trình; docstring ghi rõ điều này.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng Q (/code-review trên vòng P: 7 điểm, sửa 5, bác 2)

- `_chung`: mô-đun dựng sẵn / đóng băng ngoài `sys.stdlib_module_names` (`__phello__`, `xxsubtype`) lại được nhận
  (hồi quy của vòng P: bỏ ngoại lệ của vòng O mà không thay bằng `_khong_the_bi_che`).
- Móc đường dẫn ném lỗi khác ImportError với thư mục đã chọn -> SystemExit rõ (PathFinder cũng chỉ bỏ qua
  ImportError); mọi lỗi khi tìm phần namespace (kể cả PathFinder trên sys.path) -> coi là có, từ chối rõ — không
  còn traceback. Không móc nào nhận thư mục -> trả ngay hàm luôn "không".
- Test (226 ca, 2 bỏ qua tuỳ môi trường): 3 ca mới, đều thất bại với bản vòng P (đã kiểm là lỗi thật, không phải
  lỗi cú pháp của mã test); bộ tìm cài thêm trong test chỉ ghi tên đang xét (không bắt nhầm import khác);
  `_chay_tien_trinh_moi` nối mã test sau một dòng mới (mã bắt đầu bằng `def` / `try` không còn thành lỗi cú pháp
  lặng lẽ).
- Bác:
  - Không dùng `sys.path_importer_cache[thu_muc]` của tiến trình đo: lần chạy thật là một tiến trình khác, bộ
    nhớ đệm trống, dựng bộ tìm từ `sys.path_hooks` — đúng như kịch bản làm.
  - Mô-đun đóng băng ở tiến trình đo nhưng không đóng băng ở lần chạy thật với cờ / bản Python khác: như vòng O —
    phép đo chạy trong chính trình thông dịch này, đối chiếu là nạp bình thường trong cùng trình thông dịch.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng P (/code-review trên vòng O: 7 điểm, sửa 7)

- `_chung`: **rút lại** việc hỏi các bộ tìm cài thêm trong `sys.meta_path` (vòng O). Đã tái hiện: hỏi
  `DistutilsMetaFinder` của setuptools về `distutils` / `pip` làm đổi trạng thái tiến trình đo; một bộ tìm chuyển
  tiếp cho PathFinder (kiểu móc của pytest / typeguard) làm tệp `pytest.py` cạnh mã lọt qua — lần chạy thật thư
  mục đứng đầu sys.path nên chính bộ tìm đó trả tệp cạnh mã (đo nhầm mã, lặng lẽ).
- Luật mới, bảo thủ (nghi ngờ thì từ chối rõ, không bao giờ đo nhầm): chỉ mô-đun dựng sẵn / đóng băng (hai bộ
  tìm của CPython, không tác dụng phụ) được coi là không thể bị che; bộ tìm của thư mục dựng từ `sys.path_hooks`
  như PathFinder làm (móc đường dẫn kiểu Hy thêm đuôi mới cũng được tính), lỗi khi tìm thì coi là có; phần
  namespace chỉ được nhận khi PathFinder trên sys.path tìm được mô-đun / gói thường. Tên do bộ tìm cài thêm cung
  cấp mà thư mục cũng có thì bị từ chối (ca `hookmod/` của vòng O đổi từ "nhận" sang "từ chối, không gọi bộ tìm").
- Một hàm phân loại duy nhất (`_tu_thu_muc`, nhớ theo tên); bỏ `_bo_tim_truoc_cung_cap` và lần gọi lặp trong
  `la_ten`.
- Test (223 ca, 2 bỏ qua tuỳ môi trường): ca bộ tìm cài thêm của vòng O thay bằng 2 ca bảo thủ (kèm kiểm bộ tìm
  không bị gọi lần nào) + 1 ca `sys.path_hooks`; cả 3 thất bại với bản vòng O.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng O (/code-review trên vòng N: 7 điểm, sửa 5, bác 2)

- `_chung`: sửa tận gốc luật mô-đun anh em — bỏ các luật tự bắt chước hệ thống import (`_anh_em`,
  `_nap_truoc_filefinder`, `_mo_dun_thuong_ngoai`; bốn vòng K–N mỗi vòng lại thấy một chỗ lệch) và hỏi chính các
  bộ tìm theo đúng thứ tự import: bộ tìm trong `sys.meta_path` đứng trước PathFinder (dựng sẵn, đóng băng, móc
  cài thêm) → FileFinder của thư mục đã chọn → PathFinder trên sys.path (gói thường thắng phần namespace).
  Không gọi PathFinder với thư mục đã chọn (giữ sys.path_importer_cache sạch); kết quả nhớ theo tên trong một lần nạp.
- Tên do bộ tìm đứng trước PathFinder cung cấp được nhận (vòng N từ chối nhầm khi có thư mục dữ liệu cùng tên).
- Docstring `_import_la` theo luật mới. Test dựng sẵn / đóng băng bỏ qua trên trình thông dịch không đóng băng `os`.
- Test (221 ca, 2 bỏ qua tuỳ môi trường): 1 ca mới thất bại với bản vòng N; mọi ca của vòng K–N vẫn qua với
  cách làm mới (lưới hồi quy cho lần viết lại).
- Bác:
  - Tệp cạnh mã trùng tên mô-đun đóng băng trên một trình thông dịch KHÁC (phiên bản cũ, `-X frozen_modules=off`):
    kịch bản đo chạy mã trong chính trình thông dịch đang chạy; đối chiếu là nạp bình thường trong cùng trình
    thông dịch đó, không phải một bản Python khác.
  - Thư mục hiện hành nằm trên sys.path của tiến trình kiểm (`python -m`, pytest) che phần namespace: cách chạy
    ghi trong CLAUDE.md (`python <kịch bản> <thư mục>`) không đưa thư mục hiện hành vào sys.path; tình huống cần
    hai bản kho mã lệch nhau ở đúng một tên — xa thực tế, không đáng thêm mã.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng N (/code-review trên vòng M: 8 điểm, sửa 5, bác 3)

- `_chung` (luật mô-đun anh em): mô-đun dựng sẵn / đóng băng (`time`, `os`…) xét TRƯỚC — BuiltinImporter /
  FrozenImporter chạy trước FileFinder nên tệp cùng tên cạnh mã không che được (vòng M từ chối nhầm). Thư mục
  không `__init__` cạnh mã chỉ được nhận khi tên là mô-đun / gói THƯỜNG trên sys.path (PathFinder); gói
  namespace đã cài thì thư mục được gộp vào (`nsgoi.helper` chạy thật lấy từ thư mục) — từ chối (vòng M nhận nhầm).
- Docstring `_import_la` theo luật hiện hành; `importlib.machinery.all_suffixes()`; `with os.scandir(...)`.
- Test (220 ca, 1 bỏ qua khi chạy bằng root): 2 ca mới, đều thất bại với bản vòng M.
- Bác, kèm đường đã lần:
  - Thoát tiến trình qua bí danh (`_s.exit`, `from os import _exit`, `os.abort`) và nhánh except ghi bằng
    thuộc tính / biến bộ (`except errors.ImportError`, `except _LOI`): luật import tuỳ chọn chỉ còn áp cho tên
    KHÔNG có trong thư mục; với tên đó, chạy thật và chạy dưới kịch bản tìm trên cùng sys.path nên hành xử
    giống nhau — sai ở đây chỉ làm thông báo lỗi muộn hơn, không làm phép đo đo nhầm mã. Theo dõi bí danh tốn
    mã hơn lợi ích.
  - Thư mục dữ liệu namespace (vd `mau_csv/`) trong try/except ImportError vẫn bị từ chối: chạy thật gán một
    gói namespace rỗng, dưới kịch bản gán None — hai lần chạy đi hai nhánh khác nhau, từ chối là đúng.
  - Chi phí stat cho mỗi thư mục con: vài chục lần stat mỗi lần nạp, không đáng kể.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng M (/code-review trên vòng L: 10 điểm, sửa 9, bác 1)

- `_chung` (luật mô-đun anh em) bám đúng FileFinder: tính cả bản biên dịch không nguồn (`.pyc`); tên tệp là
  phần trước ĐÚNG đuôi (tệp `random.old.py` không phải `random`); thư mục không có `__init__` chỉ là phần gói
  namespace — không che thư viện chuẩn / gói đã cài, chỉ bị coi là anh em khi tên không có ở đâu khác (vòng L
  từ chối nhầm mã hợp lệ khi có thư mục dữ liệu tên `random/`, `csv/`...).
- Import tuỳ chọn: thân lớp chạy ngay nên được đường lui che (vòng L từ chối nhầm); xét nhánh except ĐẦU TIÊN
  bắt được ImportError theo thứ tự (kể cả `except Exception`), nhánh kết thúc bằng ném lại hay
  `sys.exit` / `os._exit` / `exit` / `quit` không phải đường lui. Điều kiện động (`if STRICT: raise`) không xét
  được tĩnh — coi là đường lui, ghi trong docstring.
- Chỉ kiểm / biên dịch các mô-đun CÒN THIẾU (i18n_errors đã nạp đúng bản thì không đọc lại), dựng đủ rồi mới
  gán. Spec không có bộ nạp và `cached = None` (vòng L chỉ đặt `__cached__`, `__spec__` vẫn trỏ .pyc và
  `importlib.reload` đi vòng qua phép kiểm). `functools.cache` thay danh sách tự chế.
- Test (218 ca, 1 bỏ qua khi chạy bằng root): 8 ca mới thất bại với bản vòng L (ca gói thường `random/__init__.py` đã đúng từ vòng L, giữ
  làm chốt chặn khi thu hẹp luật thư mục).
- Bác: nhãn "ngoài sổ" trái quy tắc 1 của CLAUDE.md — quy tắc cho phép khi đã hỏi; việc này do Truong (chủ dự
  án) yêu cầu trực tiếp, nhãn ghi đúng điều đó.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng L (/code-review trên vòng K: 9 điểm, sửa 8, sửa một phần 1)

- `_chung` (kiểm import): thêm luật **mô-đun anh em** — tên có mặt trong thư mục đã chọn (tệp .py, mô-đun mở
  rộng, thư mục) mà không được phép thì luôn bị từ chối, kể cả nằm trong `try/except ImportError` hay trùng tên
  gói đã cài (vòng K để lọt: `try: import rbda_priority_pipeline` trong i18n_errors; tệp `openpyxl.py` cạnh mã).
  Import tuỳ chọn chỉ được che khi nằm trực tiếp trong khối try (không vào thân hàm / lớp định nghĩa ở đó) và
  nhánh except không chỉ ném lại; nhận cả `except*`. Danh sách gói đã cài quét một lần, chỉ khi cần.
- Kiểm và biên dịch CẢ HAI tệp trước khi chạy tệp nào (vòng K chạy i18n_errors rồi mới đọc mô-đun chính).
  Thông báo nêu đúng tệp được import gì (i18n_errors: không mô-đun nào của kho mã, vì nó nạp trước).
- `__cached__ = None` (không trỏ tới .pyc không tồn tại); `compile(..., dont_inherit=True)`.
- Test (209 ca): khôi phục test "không thêm mục cache bộ tìm" (bỏ ở vòng K là sai: nó chặn hồi quy kiểu chèn
  tạm sys.path); 9 ca mới, đều thất bại với bản vòng K.
- Bác phần còn lại của điểm 6 (không dùng bộ nhớ đệm .pyc): cố ý từ vòng H–I (bản .pyc cũ từng bị dùng nhầm);
  phân tích + biên dịch mô-đun chính tốn ~46 ms mỗi tiến trình, không đáng kể so với phép đo.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng K (/code-review trên vòng J: 10 điểm, sửa 9, bác 1)

- `_chung` (kiểm import tĩnh của vòng J): nhận cả gói đã cài trong site-packages (theo `importlib.metadata.packages_distributions`) — vòng J đã thu hẹp quá mức mà CHANGELOG không ghi; bỏ qua import tuỳ chọn trong khối `try/except ImportError`; `i18n_errors` (nạp trước) không được import `rbda_priority_pipeline` (sẽ lấy nhầm bản khác); import tương đối báo đúng tên mô-đun (`.helpers`, không phải `.helpers.f`); bỏ điều kiện thừa `__future__`.
- Kiểm và biên dịch NGAY LÚC NẠP từ đúng bản đã đọc (`compile(cây ast)` rồi `exec`): không còn khe giữa lúc kiểm và lúc chạy; lỗi đọc / cú pháp / byte NUL thành SystemExit rõ; đã nạp đúng thư mục thì trả bản đã nạp mà không đọc lại tệp.
- Test (199 ca): bỏ test cache không thể thất bại (vòng J); 5 test mới, đều thất bại với bản vòng J.
- Bác: một tệp tên trùng thư viện chuẩn (vd `random.py`) chen trên sys.path — mối nguy chung của mọi chương trình Python, ngoài phạm vi kịch bản; phép kiểm theo đường dẫn của vòng I từng có báo nhầm nặng hơn.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng J (/code-review trên vòng I: 9 điểm, sửa 9)

- `_chung`: đính chính vòng I — phép kiểm "mô-đun anh em" chạy SAU khi nạp nên bỏ lọt import bên trong hàm (đúng kiểu import của mã này; đã tái hiện), từ chối nhầm mô-đun C của thư viện chuẩn trên Windows (`<base>\DLLs`), không dùng tham số `thu_muc`, và để lại mô-đun lạ trong sys.modules. Thay bằng kiểm TĨNH trước khi chạy gì: đọc cả hai tệp nguồn bằng `ast`, lấy mọi import (đầu tệp lẫn trong hàm, kể cả import tương đối) và từ chối tên không thuộc `sys.stdlib_module_names` hay `i18n_errors` / `rbda_priority_pipeline`. Bỏ `_thu_muc_chuan`, `_phu_thuoc_la` (không còn đoán theo đường dẫn, không còn sysconfig). Hai tệp thật của kho qua kiểm (không import lạ).
- Test (195 ca): 4 ca import lạ (đầu tệp, trong hàm, anh em ngay thư mục chọn, import tương đối — đều thất bại với bản vòng I) và kiểm không mô-đun nào bị nạp; 1 ca nhận mô-đun C của thư viện chuẩn; 1 ca thư mục chưa có mục cache vẫn không có sau khi nạp.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng I (/code-review trên vòng H: 9 điểm, sửa 8, bác 1)

- `_chung.nap_rb` (thư mục), sửa tận gốc theo điểm "sai tầng": bỏ hẳn cơ chế đoán tệp Python sẽ nạp (`sys.path_hooks`, bộ tìm riêng, các ca .so / gói / namespace — thêm dần từ vòng C tới H). Nay nạp THẲNG `<thư mục>/<tên>.py` bằng `spec_from_file_location`: bản biên dịch cũ, gói cùng tên, gói namespace nằm cạnh không thể chen vào; không đụng sys.path hay cache bộ tìm; không còn đường lỗi traceback từ bộ tìm hay loader cũ. Đổi hành vi có chủ đích: thư mục chỉ có bản biên dịch không kèm nguồn (.pyc) nay bị TỪ CHỐI (kịch bản đo mã nguồn) — đảo lại phần nhận .pyc của vòng C–D.
- Mới: nếu mã được nạp import thêm mô-đun ngoài thư viện chuẩn / site-packages (vd một phiên bản khác import mô-đun anh em, lấy nhầm từ thư mục khác trên sys.path), từ chối thay vì đo lẫn mã. Mã hiện tại chỉ import thư viện chuẩn và `i18n_errors` (đã kiểm).
- Test (190 ca): viết lại nhóm test bộ nạp thư mục theo thiết kế mới (8 test thất bại với bản vòng H vì hành vi đổi có chủ đích hoặc vì mô-đun anh em trước đây lọt).
- Bác: khoá import và "đọc lại sys.modules sau exec" của bộ import — kịch bản chạy một luồng, và `_nap_co_kiem` đã kiểm nguồn của mục sys.modules sau khi nạp.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng H (/code-review trên vòng G: 6 điểm, sửa 6)

- `_chung.nap_rb` (thư mục), sửa tận gốc: không còn import theo tên qua sys.path nữa. Hỏi bộ tìm mà CHÍNH Python dùng (gọi `sys.path_hooks` như PathFinder, kể cả hook tuỳ biến, nhưng tạo mới và không ghi cache) lấy spec cho từng mô-đun, rồi nạp ĐÚNG spec đó (`module_from_spec` + `exec_module`, đặt vào sys.modules trước như import). Hệ quả: dự đoán và lần nạp thật không thể lệch; bỏ toàn bộ phần sửa / khôi phục sys.path và `sys.path_importer_cache` (vòng G bỏ sót bước xoá mục cũ trước khi import nên có thể đi qua bộ tìm cũ hoặc mục None — đã tái hiện bằng test); thư mục mất quyền giữa chừng vẫn báo lỗi đọc.
- Test (193 ca): test cache tự gieo mục sẵn có (không còn đúng vô nghĩa khi cache trống); test thư mục đã ở trên sys.path với mục cache cũ None (thất bại với bản vòng G).

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng G (/code-review trên vòng F: 8 điểm, sửa 7, bác 1)

- `_chung`: đính chính vòng F — `nap_rb` vẫn để lại bộ tìm tệp của thư mục trong `sys.path_importer_cache` (vòng F chỉ dọn ở `_tep_se_nap`; đã tái hiện). Nay `_tep_se_nap` dùng một `FileFinder` RIÊNG (cùng thứ tự loại tệp như mặc định) nên không đụng cache toàn cục, và bước import của `nap_rb` trả mục cache về như cũ (không để lại cho thư mục tạm, không thay bộ tìm sẵn có). Kiểm đọc được thư mục bằng `os.scandir` (rẻ); lỗi OSError khi tìm thành SystemExit; docstring nói rõ thư mục không có `<tên>.py` thì nhận đúng thứ Python nạp.
- Test (192 ca): test chmod 000 thật (bỏ qua khi chạy root hay Windows; CI Linux chạy được); `.pyc` trong `__pycache__` bỏ qua khi `cache_tag` là None; 2 test cache bộ tìm (thất bại với bản vòng F); test giả lập lỗi quyền đổi sang `os.scandir` (thất bại với bản vòng F chỉ vì vòng F dùng `os.listdir`).
- Bác: thư mục chỉ có gói `rbda_priority_pipeline/__init__.py` (không có `.py`) được nhận — đúng ý: đó là mã Python sẽ chạy khi import từ thư mục đó; docstring đã ghi rõ.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng F (/code-review trên vòng E: 7 điểm, sửa 6, bác 1)

Không điểm nào làm phép đo sai; đều là thông báo lỗi và độ vững của test.
- `_chung._tep_se_nap`: thư mục không đọc được báo đúng "Không đọc được thư mục" (FileFinder nuốt lỗi quyền rồi trả None nên trước đây báo nhầm "không có mô-đun"); tạo bộ tìm tệp mới mỗi lần và không để lại trong `sys.path_importer_cache`; thông báo nêu cả khả năng "gói cùng tên nằm cạnh". `nap_rb` kiểm mô-đun chính trước, nên thư mục sai báo thiếu `rbda_priority_pipeline`.
- Test (190 ca): test `__pycache__` ghi .pyc vào đúng chỗ và kiểm là có (không thành vô nghĩa khi đặt PYTHONPYCACHEPREFIX); 4 test mới, đều thất bại với bản vòng E.
- Bác: gọi `nap_rb` lần hai trên cùng thư mục sau khi tệp trong đó đổi giữa chừng thì bị từ chối — chỉ là từ chối (đòi tiến trình mới), không bao giờ đo nhầm mã.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng E (/code-review trên vòng D: 8 điểm, sửa 7, bác 1)

- `_chung.nap_rb`, sửa tận gốc: bỏ các luật đoán theo tên tệp (`_co_mo_dun`, phần tiền tố của `_cung_nguon`); hỏi chính bộ import của Python (`importlib.machinery.PathFinder.find_spec`) tệp nào sẽ được nạp từ thư mục, rồi đòi đúng tệp đó sau khi nạp. Hệ quả: .pyc có thẻ trong `__pycache__` (Python không nạp) và hậu tố mở rộng của hệ khác không còn bị nhận nhầm; thư mục chỉ có `__pycache__` báo SystemExit rõ thay vì traceback; bản mở rộng cũ chen trước tệp nguồn vẫn bị từ chối; gói namespace bị chặn ngay ở bước kiểm trước (không phụ thuộc sys.path của máy); thông báo nêu đúng tệp mong đợi; lỗi đọc thư mục thành SystemExit; thông báo "đã nạp nơi khác" nêu nguồn thật (gói namespace, mục None).
- Test (186 ca): 2 test cho hàm mới `_tep_se_nap` (thất bại với bản vòng D chỉ vì hàm chưa có) và 1 test hành vi qua `nap_rb` (thất bại thật với bản vòng D).
- Bác: điểm cũ float và điểm mới Decimal cùng giá trị bị coi là "đổi" — giữ, vì đổi kiểu có thể đổi thứ hạng thật: `Decimal('7.1') > 7.1` (float 7.1 là 7,0999…), nên từ chối là đúng.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng D (/code-review trên vòng C: 6 điểm, sửa 6)

- `_chung.nap_rb`: sửa lỗi do vòng C đưa vào — khi thư mục CÓ `<tên>.py`, chỉ nhận đúng tệp đó; một bản biên dịch cũ (.so/.pyd) nằm cạnh mà Python ưu tiên nạp trước bị từ chối (trước đây vòng C nhận nó và đo nhầm mã cũ). Bản biên dịch không kèm nguồn chỉ được nhận khi KHÔNG có .py, nay cho cả mô-đun chính; gói namespace chen vào được nêu đúng nơi (thay vì "None").
- `exp_resume.kiem_tien_de`: nhận điểm Decimal (không là numbers.Real); chỉ kiểm điểm của dữ liệu mới (điểm em cũ đã phải bằng hệt dữ liệu cũ).
- Test (184 ca): bỏ test tiền đề không có khẳng định (luôn xanh), giữ lý do thành chú thích; 4 test mới, đều thất bại với bản vòng C.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng C (/code-review trên vòng B: 8 điểm, sửa 7, bác 1)

- `exp_resume.kiem_tien_de`: một luật `_so_hop_le` cho mọi số mà `compute_club_priority` sắp (số bốc thăm và điểm): điểm là chuỗi CSV, None, bool, pd.NA hay NaN đều bị từ chối bằng ValueError rõ (trước đây chuỗi / None lọt kiểm rồi gây TypeError giữa `resume_da` — đã tái hiện).
- `_chung.nap_rb`: nhận bản biên dịch không kèm nguồn (`i18n_errors.pyc` trong đúng thư mục) thay vì báo "nạp nhầm"; thông báo lỗi sau khi nạp nêu đúng nguồn thực và nguồn mong đợi.
- Test (181 ca): test tiền đề về NaN chuyển thành tự bỏ qua nếu sau này mã sản phẩm xử lý NaN xác định (không chặn bản sửa đúng); thêm 8 ca điểm không hợp lệ (2 ca NaN thất bại với bản vòng B chỉ vì đổi thông báo lỗi; 6 ca chuỗi / None / bool là lỗi thật) và 1 ca `.pyc`.
- Hồ sơ: đính chính câu "6 test mới đều thất bại" của vòng B; cập nhật ngày ở TIEN_DO.md.
- Bác: từ chối NaN cả ở điểm không ảnh hưởng thứ hạng (em không có trong apps, điểm nhập trước của em mới) — giữ, vì thận trọng: chỉ tốn một lần chạy lại toàn bộ, không bao giờ cho kết quả sai.

## 2026-10-10 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng B (/code-review trên vòng A: 7 điểm, sửa 5, bác 2)

- `_chung.nap_rb`: kiểm SAU khi nạp rằng mỗi mô-đun đến đúng từ thư mục / bản build đã chọn — thư mục thiếu `i18n_errors.py` trước đây lặng lẽ lấy tệp cùng tên ở chỗ khác trên sys.path (đã tái hiện), nay từ chối và gỡ mô-đun; mục sys.modules không rõ nguồn (None, mô-đun giả) báo rõ; tệp build không chứa mô-đun cần thiết báo SystemExit thay vì KeyError.
- `exp_resume.kiem_tien_de`: TỪ CHỐI điểm NaN (cả em cũ lẫn em mới) — `compute_club_priority` cho thứ tự phụ thuộc thứ tự đầu vào khi có NaN (đã tái hiện), nên vòng A coi NaN == NaN là sai; chưa nạp mô-đun rbda là RuntimeError (lỗi cài đặt, để người gọi bắt ValueError rồi chạy lại toàn bộ không nuốt mất).
- Test (174 ca): 7 test mới — 6 thất bại với bản vòng A; 1 là test tiền đề chỉ chạy mã sản phẩm (`compute_club_priority` với NaN) nên không phân biệt hai bản (đính chính ở vòng C).
- Bác: (1) em mới đã có trong apps/điểm của dữ liệu cũ làm `resume_da` lệch — thử 5.000 thể hiện ngẫu nhiên có trường hợp này: 0 lệch; (2) bản nhanh gọi `club_choice_function` một lần mỗi CLB làm chậm — đo 10.000 HS: 0,037 s so với 0,034 s, không đáng kể so với giá trị (khớp mọi kiểm tra đầu vào của bản gốc).

## 2026-10-09 — GĐ0 (việc tiếp, ngoài sổ) — vòng lặp 2, vòng A (2 lần /code-review trên 2386dd7: 20 điểm ~15 khác nhau)

Quyết định của Truong: KHÔNG sửa mã sản phẩm (phân xử em không có thứ hạng trong `club_choice_function` vẫn hoãn); lặp tới khi một vòng không còn lỗi đúng đắn.
- `exp_resume.kiem_tien_de`: mọi vi phạm là ValueError (kể cả chưa nạp rbda); bỏ em mới ở CẢ dữ liệu cũ khi so điểm / apps (điểm nhập trước cho em đến muộn không còn báo nhầm "em cũ đổi"); nhóm dự trữ '' và None coi như một (như `default_reserve_eligible_fn`); điểm NaN không đổi không bị báo đổi; kiểm thứ tự bốc thăm sắp một lần; `resume_test` dùng bản rbda đã nạp.
- `de_xuat_verify_nhanh.py`: lần đầu xét mỗi CLB, gọi đúng lời gọi `club_choice_function` của bản gốc (đang giữ + ứng viên, hàm đủ tư cách và thứ hạng thật) — mọi kiểm tra đầu vào, hiện tại và sau này, chạy y hệt.
- `_chung.py`: một hàm `_nap_co_kiem` cho cả thư mục lẫn bản build (kiểm "đã nạp nơi khác", trả bản đã nạp, gỡ mô-đun dở dang); thư mục lấy theo đường dẫn người dùng đưa (không theo đích liên kết); đường dẫn không tồn tại báo rõ; đọc được tệp PyInstaller < 6 (mục `PYZ-00.pyz`, mục lục dict).
- Test (169 ca): 7 test mới, đều thất bại với bản trước; chuỗi so lỗi chính xác ("thứ tự bốc thăm"); đường dẫn Windows dự phòng thật sự viết khác.
- Bác: gộp đoạn mồi 4 dòng (lý do như trước); thay `compute_club_priority` bằng chèn bisect trong `resume_da` (ghi ở DOI_CHIEU, để khi làm G1); sửa phân xử trong `club_choice_function` (chủ dự án hoãn).

## 2026-10-09 — GĐ0 (việc tiếp, ngoài sổ) — vòng sửa 4 (/code-review trên vòng 3: 9 điểm, sửa 8, bác một phần 1)

- `exp_resume.kiem_tien_de`: số bốc thăm phải là số thực (không chuỗi CSV, không bool, không NaN) — báo ValueError rõ; kiểm sức chứa dùng bản rbda đã nạp kể cả khi `exp_resume.rb` chưa gán (trước đây lặng lẽ bỏ qua).
- `_chung.nap_rb`: so đường dẫn như hệ điều hành (liên kết, hoa/thường Windows) khi nạp lại cùng .exe; nhánh thư mục nạp hỏng cũng gỡ mô-đun dở dang như nhánh bản build.
- Test (162 ca): lần đầu có test cho đường nạp `.exe` (tệp PyInstaller tối thiểu dựng trong test): nạp, nạp lại qua đường dẫn khác, nạp hỏng không để mô-đun dở dang, lệch phiên bản Python; danh sách cấm cả `.index`/`.count`; dùng đúng một bản `_chung` trong tiến trình; sửa chú thích sai (v + 20).
- Bác một phần: kiểm sức chứa trong `kiem_tien_de` lặp lại luật của `club_choice_function` — giữ, vì cần nêu tên CLB trước khi làm việc và chỉ tốn một lần gọi mỗi CLB.

## 2026-10-09 — GĐ0 (việc tiếp, ngoài sổ) — vòng sửa 3 (/code-review trên vòng 1–2: 10 điểm, sửa 8, bác 2)

- `exp_resume.kiem_tien_de`: nhận số bốc thăm kiểu số bất kỳ (numpy.int64...), chỉ thiếu / None mới là lỗi; báo rõ CLB có sức chứa mới không hợp lệ (giảm dưới suất dự trữ) thay vì lỗi chung chung về sau.
- `_chung.nap_rb`: thư mục — luôn nạp cả `i18n_errors` từ cùng thư mục (kể cả khi mô-đun chính đã có sẵn); bản build — nạp lại cùng tệp .exe trả bản đã nạp thay vì từ chối; nạp hỏng thì gỡ mô-đun dở dang khỏi sys.modules.
- Test (154 ca): test khoá phá hoà nay phân biệt được bản đúng với bản cũ (thêm ca tách cặp trùng giữ thứ tự, bản chỉ so số bốc thăm từ chối nhầm; đã thử đột biến); bỏ test đo giây, thay bằng danh sách cấm tra `in` (bảo đảm không quét danh sách); dùng chung bộ nạp `_chung.nap_canh`.
- Bác: (1) `verify_stability_nhanh` import `i18n_errors` theo tên — giống hệt bản gốc `verify_stability`, và `nap_rb` bảo đảm cùng thư mục; (2) sửa cách phân xử em không có thứ hạng trong `club_choice_function` — mã sản phẩm, cần mục trong sổ (đã ghi ở DOI_CHIEU_KHO_MA.md).

## 2026-10-09 — GĐ0 (việc tiếp, ngoài sổ) — vòng sửa 2 (/code-review trên vòng 1: 9 điểm, sửa 8, bác 1)

- `exp_resume.kiem_tien_de`: so thứ tự bốc thăm bằng đúng khoá phá hoà của `compute_club_priority` (số bốc thăm, mã em) — số trùng trước đây lọt kiểm; thiếu hoặc rỗng số bốc thăm báo ValueError rõ thay vì KeyError/TypeError.
- `de_xuat_verify_nhanh.py`: luôn gọi hàm đủ tư cách cho ứng viên như bản gốc (trước đây bỏ qua khi CLB còn chỗ, nên lỗi của hàm đó không lộ ra giống bản gốc).
- `_chung.nap_rb`: từ chối cả `i18n_errors` nạp từ nơi khác; bỏ đường dẫn khỏi sys.path sau khi nạp; bản build từ chối khi tiến trình đã nạp mô-đun, và `__file__` của mô-đun nạp từ .exe là đường dẫn ảo trong tệp .exe (trước đây là đường dẫn tương đối, có thể trùng tệp của kho).
- Test: 150 ca; bỏ ngưỡng giây tuyệt đối (chập chờn trên CI), thay bằng tỉ lệ thời gian khi dữ liệu gấp 8 lần.
- Bác: gộp đoạn mồi nạp `_chung` (5 dòng) trong hai kịch bản — không gộp được mà không sửa sys.path (chính là lỗi đã sửa ở vòng trước).

## 2026-10-09 — GĐ0 (việc tiếp, ngoài sổ; chuẩn bị Z4, G1) — rà soát mã lượt 3, vòng sửa 1 (3 lần /code-review, ~27 điểm)

- `exp_resume.py` (G1), sửa tận gốc: `resume_da(res0, cu, moi, new_ids)` nhận cả dữ liệu cũ lẫn mới; `kiem_tien_de` (O(dữ liệu), dùng tập hợp) kiểm và TỪ CHỐI với thông báo rõ mọi thay đổi không phải "thêm ràng buộc": em nộp lại / mã trùng, đóng CLB, tăng sức chứa, đổi dự trữ, đổi nguyện vọng / điểm / nhóm / thứ tự bốc thăm của em cũ, em cũ xếp CLB mới mở, apps thiếu nguyện vọng (kể cả res0 lập từ apps thiếu). Hỗ trợ thêm GIẢM sức chứa (chọn lại trên tập đang giữ). Em mới không có dòng nguyện vọng không còn KeyError. `resume_test` đo riêng thời gian kiểm tiền đề.
- `de_xuat_verify_nhanh.py` (Z4): chữ ký trùng `verify_stability` (bỏ tham số `err`, dùng `err` của i18n_errors); chuẩn bị từng CLB một cách lười (chỉ CLB thật sự được xét, như bản gốc); kiểm sức chứa bằng `club_choice_function` của mô-đun đã nạp với ứng viên thật.
- `_chung.py`: `nap_canh` là bản duy nhất của bộ nạp theo đường dẫn; `nap_rb(thu_muc)` báo lỗi khi tiến trình đã nạp bản từ nơi khác (trước đây lặng lẽ trả bản cũ); bản build: báo rõ khi lệch phiên bản Python, đọc được mục lục PYZ dạng dict của PyInstaller cũ.
- `kiem_verify_nhanh.py`: `is not None` khi chọn em để hoán đổi.
- Test: 145 ca (vi sai tiếp tục/chạy lại có giảm sức chứa, CLB mới, em không nguyện vọng; một ca từ chối cho mỗi vi phạm; kiểm tiền đề tuyến tính; bản nhanh không đọc CLB không ai xét; `nap_rb` cùng thư mục / khác thư mục / tiến trình mới).
- Kiểm vi sai ngoài bộ test: `resume_da` = `run_rbda` trên 20.000 thể hiện ngẫu nhiên (có giảm sức chứa, CLB mới); bản nhanh = bản gốc trên 60.000 thể hiện (gồm 3.195 ca sức chứa sai, cùng thông báo lỗi).
- Chưa sửa (mã sản phẩm, cần mục trong sổ): `club_choice_function` xếp em không có thứ hạng bằng `len(rank)` rồi theo thứ tự pool — ghi trong DOI_CHIEU_KHO_MA.md.

## 2026-10-08 — GĐ0 (việc tiếp, ngoài sổ; chuẩn bị Z4, G1, Z6) — rà soát mã lượt 2 (/code-review, 18 điểm)

- `de_xuat_verify_nhanh.py` (Z4): không còn nhập `loi_suc_chua` theo tên và không chép thông báo lỗi; kiểm sức chứa bằng chính `club_choice_function` của mô-đun đã nạp (kho mã hay bản build cũ), nên cùng luật, cùng thông báo.
- `exp_resume.py` (G1): `is not None` ở mọi chỗ (trước đây `held` và `nxt` lệch nhau với CLB có mã rỗng); bỏ ID CLB không tồn tại khỏi tập tính lại thứ hạng; CLB mới sau lần chạy cũ không còn KeyError; em không có dòng nguyện vọng dùng `prefs.get(s, [])` như `run_rbda`.
- `kiem_verify_nhanh.py`, `exp_resume.py`: nạp `_chung` và bản nhanh theo đường dẫn (không sửa sys.path); phần chạy của `kiem_verify_nhanh.py` đặt trong `main()`.
- `tests/test_tham_khao_verify_nhanh.py`: 85 ca (86 sau rà soát bổ sung). Thêm biến đổi kết quả làm CLB thừa/thiếu người, bỏ chỗ; ca thật "em trong nguyện vọng nhưng không trong apps"; dự trữ 0 / một phần / bằng sức chứa; so thông báo lỗi; em mới có diện dự trữ và điểm thi, CLB mới, nguyện vọng trỏ CLB không có, em không có nguyện vọng; kiểm `nap_rb` và `gen`; kiểm phép so sánh không rỗng. Nạp kịch bản theo đường dẫn. 16 ca thất bại với bản `exp_resume.py` trước sửa.
- Rà soát bổ sung (Sonnet, kiểm vi sai ngẫu nhiên): bản nhanh khớp bản gốc trên 600.000 thể hiện (kể cả thứ hạng trùng, sức chứa sai); `resume_da` lệch chạy lại khi em có trong nguyện vọng nhưng không trong apps (em không thứ hạng trùng nhau, phân xử theo thứ tự pool). Đường thật không có ca này (`hop_ung_vien`); `resume_da` nay ghi rõ tiền đề và từ chối dữ liệu như vậy; thêm test phản ví dụ (86 ca).
- Tài liệu: mã tiến độ `RS` (không có trong sổ) đổi thành `GĐ0`; số test trong CLAUDE.md đếm lại; sửa hai dòng mâu thuẫn / lỗi thời trong `DOI_CHIEU_KHO_MA.md`.

## 2026-10-08 — GĐ0 (việc tiếp, ngoài sổ; chuẩn bị Z4, G1, Z6) — rà soát mã lượt 1 (/code-review, 10 điểm)

- `docs/ke_hoach/tham_khao/de_xuat_verify_nhanh.py` (bản đề xuất cho Z4): khớp `club_choice_function` ở mọi ca biên — em đang giữ chỗ không có trong `base_rank` xếp cuối (`rank.get(s, len(rank))`) thay vì ném KeyError; thứ hạng trùng dùng `bisect_right` (khớp sắp xếp ổn định; test mới tìm ra lệch khi dùng `bisect_left`); kiểm `loi_suc_chua` và ném cùng ValueError; `is not None` khi gom em đang giữ; gọi hàm đủ tư cách một lần cho mỗi em.
- `exp_resume.py` (nguyên mẫu G1): bỏ qua nguyện vọng trỏ tới CLB không tồn tại như `run_rbda`; nhập được từ test (phần chạy đặt trong `__main__`, numpy chỉ nạp khi đo).
- Mới `docs/ke_hoach/tham_khao/_chung.py`: một bản duy nhất của bộ nạp `nap_rb` (báo lỗi rõ khi tệp không phải PyInstaller) và bộ sinh `gen`; bỏ bản sao và import thừa trong hai kịch bản.
- `pyproject.toml`: bỏ loại trừ ruff cho `docs/ke_hoach/tham_khao` (đã sửa lỗi lint); giữ loại `docs/*` khỏi đo phủ.
- Test mới `tests/test_tham_khao_verify_nhanh.py` (43 ca, không cần numpy).
- `CLAUDE.md`: cập nhật bản đồ mã theo kho (api.py L784–1364, rollback L1107–1119, `_BANG_RANG_BUOC`, Sổ nhập), số test, thời gian chạy, lệnh verify cần numpy, `CHANGELOG.md`.
- Chạy lại: `kiem_verify_nhanh.py` → `TAT_CA_GIONG_NHAU True` (7/7); `exp_resume.py` → 38/38 khớp chạy lại.

## 2026-10-08 — Giai đoạn 0 (chỉ đọc và đo)

- Môi trường: `.venv` (Python 3.11.17) cài `requirements-dev.txt` và `numpy`; `matching` 1.4.3 cài thêm chỉ để so sánh sau này (Q5), không thêm vào requirements.
- Gói kế hoạch đã có trước đó (commit 7c4f423): `CLAUDE.md`, `docs/ke_hoach/*`, và các loại trừ trong `pyproject.toml` (ruff: `docs/ke_hoach/tham_khao`; phủ: `docs/*`). Giai đoạn 0 không sửa các tệp này.
- Thêm `docs/ke_hoach/DOI_CHIEU_KHO_MA.md`: đối chiếu 33 mục của sổ với kho, kết quả đo và trả lời câu hỏi mở mục 9 của `BOI_CANH_DU_AN.md`.
- Cập nhật `docs/ke_hoach/TIEN_DO.md`: GĐ0 xong; Z1–Z7 đánh dấu chưa.
- Không sửa mã sản phẩm (`.py`, `.js`, `.html`, `.css`).

Số đo chính (dữ liệu mô phỏng):
- Bộ test: 1.287 ca đạt, 0 hỏng, 0 bỏ qua, 0 lỗi; phủ 91,06 %; thời gian 1.352 s. Ruff: sạch.
- Verify nhanh: khớp hoàn toàn ở 7/7 cấu hình (`TAT_CA_GIONG_NHAU True`); 10.000 HS: 6,53 s so với 0,042 s.
- 5.000 HS, 10 CLB: `run_rbda` 0,18 s; `verify_stability` 2,09 s (≈92 % thời gian kiểm tra); 0 cặp phá vỡ.
- Tiếp tục DA từ trạng thái cũ: khớp chạy lại 38/38 lần.
- Sổ 33 mục: 29 đúng, 3 khác (Z1, Z4, Z6), 1 sai (C1).
