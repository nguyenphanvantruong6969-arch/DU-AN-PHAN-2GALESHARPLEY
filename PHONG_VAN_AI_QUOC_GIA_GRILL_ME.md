# GRILL ME — Bộ câu hỏi phỏng vấn Cuộc thi Sáng tạo trẻ Quốc gia về AI 2026 (Bảng B)

> **Dự án:** Phần mềm sắp xếp học sinh vào câu lạc bộ ngoại khóa ứng dụng thuật toán chấp nhận trì hoãn (Gale–Shapley) — trong kho là **RB-DA** (Reserve-Based Deferred Acceptance).
> **Hồ sơ nộp:** ngày 20/09/2026. **Tệp này lập:** 15/10/2026.
> **Phản hồi đã nhận:** *"Điểm mạnh: Đề tài phù hợp với môi trường học đường, sử dụng thuật toán phù hợp."*
>
> **Tệp này KHÔNG có đáp án.** Có chủ đích: em phải tự nói ra thì mới hiểu. Mỗi câu có
> ba thứ: **câu hỏi**, **vì sao họ hỏi**, **tra ở đâu trong kho** để em tự tìm lại dữ kiện.
> Các nhận xét, diễn giải, kết luận trong đề tài phải do chính Truong nói bằng lời của mình.
>
> **Khác với `BAO_VE_BO_CAU_HOI.md`:** tệp cũ luyện cho vòng nội bộ, tập trung lý thuyết ghép cặp
> (27 câu). Tệp này luyện cho **vòng quốc gia về AI**, nên thêm bốn thứ tệp cũ chưa có:
> (1) *"AI nằm ở đâu trong sản phẩm?"*, (2) *vai trò của AI trong quá trình làm*,
> (3) *câu hỏi từ AI quét mã*, (4) *đối chiếu từng con số trong hồ sơ với kho mã*.

---

## 0. Cách dùng

| Mục | Số câu | Cách luyện |
|---|---|---|
| **A. Phi kỹ thuật** (vấn đề, người dùng, tác động, đạo đức, dùng AI, thương mại) | 30 | Nói to, 60–90 giây/câu, không nhìn tài liệu |
| **B. Kỹ thuật** (thuật toán, dữ liệu, kiến trúc, kiểm thử, hiệu năng) | 36 | Nói to, có thể vẽ lên giấy |
| **C. "AI quét mã"** — câu hỏi sinh ra từ chính các dòng mã | 24 | Mở đúng hàm, đọc, rồi trả lời |
| **D. Đối chiếu hồ sơ ↔ kho mã** (bảng các con số) | 16 dòng | Mỗi dòng: em chốt được câu trả lời một câu |
| **E. Tính năng và điểm đặc biệt** | — | Học để *chủ động nói*, không đợi bị hỏi |
| **F. Tình huống & demo trực tiếp** | 12 | Tập thao tác thật trên máy |
| **G. Ba bản chốt + kế hoạch ôn** | — | Thuộc ý, không thuộc chữ |

**Tự chấm mỗi câu (0 / 1 / 2):**
- **0** — không trả lời được hoặc trả lời sai dữ kiện.
- **1** — đúng ý nhưng dài dòng, thiếu con số, hoặc phải nhìn tài liệu.
- **2** — gọn, có ít nhất một con số hoặc ví dụ cụ thể, nói được trong 60–90 giây.

**Chuẩn:** Phần A và B đạt ≥ 70% tổng điểm; **Phần C và D không được có câu nào 0** — đó là chỗ
người ta bắt lỗi dễ nhất, vì chỉ cần mở mã hay mở hồ sơ ra là thấy.

> **Việc cần làm ngay:** hồ sơ chỉ cho em biết phần *điểm mạnh*. Nếu ban giám khảo có ghi
> *"điểm cần cải thiện"* hoặc điểm số từng tiêu chí, hãy dán vào để tinh chỉnh bộ câu hỏi này.
> Những câu nằm ở Phần A.1 và A.2 (AI nằm ở đâu, tính mới) là phần có khả năng cao
> nhất bị hỏi tiếp, vì cuộc thi mang tên **"Trí tuệ nhân tạo"**.

---
---

# PHẦN A — CÂU HỎI PHI KỸ THUẬT

## A.1 — "AI" nằm ở đâu? (nhóm câu rủi ro nhất)

### A1.1 — Gale–Shapley có phải là trí tuệ nhân tạo không?
- **Vì sao hỏi:** cuộc thi là *AI*. Thuật toán của em là thuật toán xác định, không học từ dữ liệu, không có mạng nơ-ron.
- **Em phải tự trả lời được:** (a) theo định nghĩa nào thì thuật toán ghép cặp thuộc phạm trù AI? (b) nếu không thuộc, vì sao đội em vẫn dự thi bảng này? (c) có nói *"có"* hay *"không"* thì câu tiếp theo là gì?
- **Tra:** mục 5 của hồ sơ ("Công cụ, mô hình… AI đã sử dụng") — hồ sơ liệt kê Claude Code là công cụ AI, còn thuật toán lõi không nằm trong mục này.
- **Bẫy:** né câu hỏi, hoặc nói quá lên *"phần mềm của em dùng AI"* rồi bị hỏi *"mô hình nào, huấn luyện trên dữ liệu gì"*.

### A1.2 — Trong sản phẩm cuối cùng, chỗ nào có AI chạy khi người dùng bấm nút?
- **Vì sao hỏi:** phân biệt *"AI dùng để làm ra sản phẩm"* với *"AI nằm trong sản phẩm"*.
- **Tự kiểm:** phần mềm chạy **offline**, không gọi API nào. Em nói thẳng điều đó như thế nào, và nó là điểm mạnh hay điểm yếu theo cách em trình bày?
- **Tra:** `main.py`, `requirements.txt` (có thư viện học máy nào không?), `browser_host.py` (chỉ nghe `127.0.0.1`).

### A1.3 — Nếu bỏ hết AI ra khỏi quá trình làm, em có làm ra được sản phẩm này không? Bằng gì, trong bao lâu?
- **Vì sao hỏi:** đo mức độ em *hiểu và kiểm soát* so với mức em *được làm hộ*.
- **Tự kiểm:** em tự viết được phần nào mà không cần AI? Em giải thích được hàm nào từng dòng?
- **Tra:** `BAN_GIAO.md` mục 3 ("Học sinh tự viết" so với "AI viết mới") và `git log` — **kho này chỉ có lịch sử từ 08/10/2026 (bản chụp), 64 trên 66 commit mang tên tác giả "Claude"**; AI quét lịch sử sẽ thấy điều đó. Em có nhật ký prompt ở mục 9 hồ sơ để chứng minh quá trình thật?

### A1.4 — Em dùng AI để làm gì cụ thể, và AI *không được* làm gì trong dự án này?
- **Vì sao hỏi:** hồ sơ nói *"Claude Code… Lập trình"* — quá chung. Ban giám khảo cần ranh giới.
- **Tra:** `CLAUDE.md` mục "Liêm chính học thuật": mọi số liệu là dữ liệu mô phỏng; phần nhận xét, diễn giải, kết luận do học sinh tự viết; AI được ghi vào nhật ký AI.
- **Bẫy:** khẳng định *"em tự viết hết"* rồi bị mở `git log` ra đối chiếu. **Trung thực thắng.**

### A1.5 — Làm sao em biết mã do AI viết là đúng? Em kiểm bằng cách nào mà không chỉ tin vào AI?
- **Vì sao hỏi:** câu hỏi cốt lõi của kỹ sư dùng AI.
- **Em cần nêu được:** ít nhất ba lớp kiểm chứng *độc lập với AI* — gợi ý để em tự tìm: kiểm bằng định nghĩa toán học (`verify_stability`), vét cạn so với một cơ chế khác, test hồi quy băm kết quả từng em.
- **Tra:** `tests/test_ket_qua_khong_doi.py`, `docs/NGHIEN_CUU_TOI_UU.md` TN1 (2.088 thể hiện vét cạn).

### A1.6 — AI từng viết sai điều gì mà em phát hiện ra? Kể một lỗi cụ thể.
- **Vì sao hỏi:** chứng minh em *thực sự đọc*, không chỉ chấp nhận mã.
- **Gợi ý nguồn để em chọn lỗi mình hiểu rõ nhất:** `BAN_GIAO.md` — lỗi cấp số STB `MAX(stb)+1` đặt học sinh đến muộn vĩnh viễn ở cuối; lỗi điểm "ẩn" sau khi bỏ tick; lỗi `csv.Sniffer`; lỗi `set_window()` treo ứng dụng. Chọn **một** lỗi, kể được: triệu chứng → nguyên nhân → cách đo → cách sửa → test canh.
- **Bẫy:** kể quá nhiều lỗi mà không giải thích sâu được lỗi nào.

### A1.7 — Nếu một mô hình AI khác (hoặc phiên bản khác) viết lại toàn bộ, kết quả có giống không? Em biết bằng gì?
- **Tra:** `tests/test_ket_qua_khong_doi.py` (băm kết quả từng em trên nhiều bộ mẫu), `CLAUDE.md` bất biến số 1.

---

## A.2 — Vấn đề, tính mới, đóng góp

### A2.1 — Vấn đề của em là gì, trong một câu?
- Hồ sơ mục 1: xếp theo thứ tự đăng ký → em có đam mê nhưng đăng ký muộn bị mất chỗ. Em nói lại được trong **một câu** không nhìn tài liệu?

### A2.2 — Tại sao đây là vấn đề *thật*, không phải vấn đề em tự dựng ra?
- **Tra:** mục 3 hồ sơ — dữ liệu khảo sát (MS Form) và dữ liệu nhà trường. **Em còn con số khảo sát cụ thể không** (bao nhiêu em trả lời, bao nhiêu % thấy bất công)? *Lưu ý: trong kho chỉ có bộ câu hỏi (`docs/KHAO_SAT_CAU_HOI.md`), em cần mang kết quả khảo sát thật theo.*

### A2.3 — Đã có ai làm việc này chưa? Khác gì?
- **Tra:** `docs/ke_hoach/BOI_CANH_DU_AN.md` mục 3 ghi đã khảo sát 1.170 bài báo (2019–2026) và *"không có bài nào nghiên cứu riêng phân bổ CLB trường học"*; nhưng cũng ghi rõ **một số tên tác giả/tiêu đề trong danh sách sai, phải kiểm qua Crossref/arXiv trước khi trích dẫn**.
- **Bẫy:** nói *"chưa ai làm"* mà không có bằng chứng. An toàn hơn: *"em chưa tìm thấy… em đã tìm ở đâu, bằng từ khóa gì"*.

### A2.4 — Tính mới của em là gì? Phân biệt "dùng lại" và "đóng góp".
- **Tra:** `BAO_VE_BO_CAU_HOI.md` (Câu chốt số 2), `docs/CO_CHE_THUAT_TOAN.md`. Gale–Shapley (1962) và dự trữ mềm (Kominers & Sönmez 2016) là của người khác — em *ghép* và *thích nghi* điều gì cho bối cảnh trường? Em nói ba thứ: cái mượn, cái ghép, cái tự làm.

### A2.5 — Tại sao không dùng Google Form + Excel, hoặc một app xếp lịch có sẵn?
- Giám khảo phi kỹ thuật rất hay hỏi câu này.

### A2.6 — Sản phẩm của em khác gì so với "ai đăng ký trước được trước" về mặt *công bằng*? Cho một ví dụ có số.
- **Tra:** `docs/CO_CHE_THUAT_TOAN.md` Lớp 3 — thí nghiệm học sinh đến muộn: cách cũ cho **0** em mới giành được suất, công bằng kỳ vọng ~3,3, sau sửa **TB 3,5**.
- **Chú ý:** con số này là về *cơ chế chèn số bốc thăm*, không phải so với "đăng ký trước được trước". Hai chuyện khác nhau — đừng nhập nhằng (xem D.3).

---

## A.3 — Người dùng và tác động

### A3.1 — Ai thực sự dùng phần mềm này, ngồi ở đâu, ngày nào trong năm?
- Hồ sơ mục 2: học sinh, câu lạc bộ, ban quản lý. Trên thực tế ai bấm nút "chạy"? Ai nhập dữ liệu? Có cần đào tạo không? (`HUONG_DAN_SU_DUNG.md`, 14 mục).

### A3.2 — Đã có người dùng thật nào chạy chưa? Họ nói gì? Họ là ai?
- **Câu rất nguy hiểm.** Hồ sơ mục 7: *"Về phản hồi từ người dùng thực tế, khi chạy thử trên máy Windows, người dùng xác nhận…"*. Trong `BAN_GIAO.md` (02/09), người xác nhận là **chính học sinh làm dự án**. Nếu giám khảo hỏi *"người dùng thực tế là ai"*, em trả lời thế nào cho đúng sự thật mà vẫn không tự hạ thấp?
- **Gợi ý hành động:** trước buổi phỏng vấn, nếu có thể, nhờ **một giáo viên hoặc cán bộ đoàn** chạy thử và ghi lại nhận xét bằng văn bản.

### A3.3 — Giáo viên không rành công nghệ có dùng được không? Em đã thử với ai chưa?
- **Tra:** `HUONG_DAN_SU_DUNG.md`, `mau_csv/HUONG_DAN_SO_NHAP.md`, Sổ nhập Excel một tệp.

### A3.4 — Nhà trường sẽ tiết kiệm được gì? Em đo bằng gì?
- **Tra:** mục 7 hồ sơ — 0,011 giây là thời gian *chạy thuật toán*, **không phải** thời gian của quy trình thật (thu phiếu, chấm điểm, nhập liệu, kiểm tra). Con số nào đại diện cho "tiết kiệm nhân lực"? Nếu chưa đo, em nói thế nào cho trung thực?

### A3.5 — Học sinh không được nguyện vọng nào thì sao? Phần mềm giúp gì cho em đó?
- **Tra:** 12/120 em chưa được xếp trong bộ mẫu chính. `get_data_health_report`, danh sách "chưa được xếp" (đầu ra hồ sơ mục 6). Phần mềm đề xuất gì cho các em này?

### A3.6 — Có em nào cảm thấy kết quả bất công thì khiếu nại bằng cách nào? Phần mềm có giải thích được không?
- **Tra:** mục 8 hồ sơ — *"bổ sung màn hình giải trình kết quả cho từng học sinh"* là **hướng phát triển, chưa làm**. Hiện chỉ có `rejection_log` trong `MatchResult` (nhật ký vòng nào em bị từ chối CLB nào). Em dùng nó trả lời khiếu nại thế nào?

---

## A.4 — Đạo đức, công bằng, dữ liệu cá nhân

### A4.1 — Dữ liệu của học sinh (chủ yếu là trẻ vị thành niên) được lưu ở đâu, ai xem được?
- **Tra:** `app.db` là một tệp SQLite **không đăng nhập** (`BAN_GIAO.md` quyết định 5), chạy offline. Em bảo vệ dữ liệu bằng gì? Nếu máy bị mất thì sao? Nếu một người không có quyền mở máy thì sao?
- **Tự tra thêm:** quy định hiện hành của Việt Nam về bảo vệ dữ liệu cá nhân (Nghị định 13/2023/NĐ-CP và luật bảo vệ dữ liệu cá nhân mới) — em phải tự đọc lại điều khoản về dữ liệu của người dưới 16 tuổi và nói được hai ba điều, không được đoán.

### A4.2 — Hồ sơ nói dữ liệu AI *sinh ra*, nhưng mục 3 cũng nói dữ liệu *khảo sát* và dữ liệu *của nhà trường*. Dữ liệu nào đã vào phần mềm? Có xin phép chưa?
- **Mục 4 hồ sơ viết:** *"bảo đảm dữ liệu được sử dụng phù hợp quy định"* (mục 3). Em chứng minh được bằng văn bản nào? Dữ liệu nhà trường đã được ẩn danh chưa?

### A4.3 — "Suất dự trữ" ưu tiên cho nhóm nào? Ai quyết định? Có phân biệt đối xử không?
- **Tra:** `reserve_group`, `reserve_capacity`. `BAN_GIAO.md` ghi bộ dữ liệu cố tình chỉnh điểm nhóm dự trữ thấp hơn để suất dự trữ *phải làm việc* — **không phải nhận định về học sinh diện chính sách**. Em phải nói rõ: phần mềm là *công cụ*, nhà trường là bên đặt chính sách.

### A4.4 — Chấm điểm thi tuyển có công bằng không? Phần mềm đảm bảo gì?
- **Tra:** `api_cham_diem.py` (chấm điểm mù: giám khảo không thấy STB/thứ hạng nguyện vọng), `compute_club_priority` docstring: tính "mù" là ràng buộc *ở tầng quy trình/giao diện*, **hàm không tự kiểm tra được**. Em nói điều đó thế nào cho thành thật?

### A4.5 — Bốc thăm có "công bằng" thật không? Học sinh có thể nghi ngờ phần mềm gian lận. Chứng minh thế nào?
- **Tra:** `docs/GIAI_DAP_BOC_THAM.md`; `generate_stb_lottery` (seed cố định, `sorted(set(...))` trước khi xáo); khóa seed sau lần chạy đầu; `run_history` không bao giờ bị ghi đè. Ai kiểm toán được? Có thể chạy lại ra đúng kết quả không?

### A4.6 — Có thể ai đó chỉnh `app.db` bằng tay để thiên vị một em không? Phần mềm phát hiện được không?
- **Tra:** `dau_van_tay_du_lieu` (dấu vân tay SHA-256 của dữ liệu quyết định kết quả) và `get_trang_thai_ket_qua`; ràng buộc CSDL (`FOREIGN KEY`, `CHECK`). Nó phát hiện được *thay đổi sau khi chạy*, nhưng có chống được người có quyền chạy lại nhiều lần để chọn kết quả vừa ý không? (`GIAI_DAP_BOC_THAM.md` Câu 3.)

---

## A.5 — Quá trình làm việc, thời gian, đội

### A5.1 — Ai làm gì trong đội? Em đóng góp cụ thể phần nào?
- Hồ sơ ký tên "Đại diện đội thi" ở Đức Nhuận. Em chuẩn bị một câu trả lời **cho từng thành viên**, không nói chung chung.

### A5.2 — Em mất bao lâu, qua những giai đoạn nào? Phiên bản đầu tiên trông thế nào?
- **Tra:** `BAN_GIAO.md` — mã học sinh tự viết upload 26/08/2026; commit đầu `57f2e82`. Mục 9 hồ sơ có lịch sử prompt và hình ảnh minh chứng. Em phải *xem lại* tệp đó và thuộc 3 mốc.

### A5.3 — Phần khó nhất em gặp phải là gì? Em giải quyết ra sao?
- **Tra:** chọn một trong: lỗi 24/25 (cửa sổ pywebview treo — `_window` gạch dưới là bắt buộc), lỗi dự trữ làm hàm lựa chọn không còn là thứ tự tuyến tính, hoặc việc Windows chặn assembly từ Internet. Chọn **một**, kể như một câu chuyện có đầu có cuối.

### A5.4 — Điều gì em làm sai ban đầu và đã học được?
- Câu hỏi mở nhưng giám khảo rất thích. Đừng kể lỗi quá nhỏ.

---

## A.6 — Thương mại, mở rộng, tương lai

### A6.1 — Có thể dùng cho trường khác, ngành khác không? Cần sửa gì?
- **Tra:** `CLAUDE.md` — kế hoạch tổng quát hóa cho 12 ngành, 33 mục (`docs/ke_hoach/SO_DANG_KY_33_MUC.md`); hồ sơ mục 8: *"xếp lớp tự chọn… phân công"*. Phần mềm đã có `workspace.py`, `api_workspace.py`, `cau_hinh_ws.py`, `nhan_ws.py` (không gian làm việc cấu hình luật xếp, nhãn). **Em cần mở ra đọc để nói được nó làm gì** — hiện tại em có chắc chắn nó chạy thật chưa hay mới là thiết kế?

### A6.2 — Có bán được không? Ai trả tiền?
- Hồ sơ không nói thương mại (và `BOI_CANH_DU_AN.md` ghi *"Mô hình kinh doanh để sau"*). Em có nên nói điều này không, và nói thế nào để không bị coi là thiếu tầm nhìn?

### A6.3 — Việc phần mềm chưa có chữ ký số khiến Windows cảnh báo — ai dám cài?
- Hồ sơ mục 8 đã tự nêu hạn chế này. Em chuẩn bị phương án: `ky_va_tin_cay.ps1`, `HUONG_DAN_CAI_DAT.md`. **Nhưng đọc kỹ C.17: cách em xử lý có thể khiến chính bộ quét mã nghi ngờ.**

### A6.4 — Nếu có 800 học sinh thật chạy vào đầu năm học thì có chuyện gì xảy ra mà em chưa lường tới?
- **Tra:** các hạn chế tự nêu trong mục 8 (10 nguyện vọng, 5 CLB thi/buổi); các bộ `bo_*` trong `du_lieu_test/` đều ≤ 200 em; `thu_tai/` đo tới 5.000 em nhưng bằng dữ liệu tự sinh.

---
---

# PHẦN B — CÂU HỎI KỸ THUẬT

## B.1 — Thuật toán lõi

### B1.1 — Vẽ lên giấy: Deferred Acceptance chạy qua 4 học sinh, 2 CLB (sức chứa 1 và 2). Mỗi vòng ai đề nghị, ai bị từ chối?
- **Tra:** `run_rbda` (L456). Tập cho ví dụ nhỏ: `du_lieu_test/vi_du_huong_dan/` (10 em, 4 CLB). Em phải làm tay được, không dùng máy.

### B1.2 — "Trì hoãn" nghĩa là gì? Hệ quả cụ thể của việc không chốt ngay?
- **Bẫy:** *"trì hoãn là chờ đến cuối mới xét"* — sai. Xét ngay mỗi vòng; chỉ kết quả là tạm (`held[club_id]`).

### B1.3 — Thuật toán luôn dừng không? Tối đa bao nhiêu vòng? Vì sao?
- **Tra:** docstring `max_rounds` trong `run_rbda`: số vòng ≤ độ dài danh sách nguyện vọng dài nhất vì mỗi vòng mỗi em chưa có chỗ tiến đúng một nguyện vọng. Nhưng `docs/ke_hoach/BOI_CANH_DU_AN.md` mục 5 lại ghi *"thực tế khác docstring"* (trung vị 9, lớn nhất 37 vòng ở danh sách 3 mục — số liệu từ 204 lần thử tải). **Em phải hiểu vì sao hai điều này mâu thuẫn trước khi bị hỏi.** (Gợi ý: nhiều buổi? hay chọn khác nhau? — em tự điều tra.)

### B1.4 — Độ phức tạp thời gian là bao nhiêu? Vì sao 5.000 em × 10 CLB chậm hơn 5.000 em × 100 CLB (nếu đúng)?
- **Tra:** `BAO_VE_BO_CAU_HOI.md` T2.6; `du_lieu_test/thu_tai/README.md`. Con số 7,65 giây ở hồ sơ mục 7 là *chỉ bước phân bổ, lần chạy lâu nhất* (xem D.5).

### B1.5 — Định lý Gale–Shapley 1962 đảm bảo những gì? Điều kiện của nó là gì? Điều kiện đó còn đúng với suất dự trữ của em không?
- **Tra:** `docs/CO_CHE_THUAT_TOAN.md` — mục "Báo cáo và phần mềm: còn đúng MỘT chỗ lệch". Hàm lựa chọn có dự trữ **không phải một thứ tự tuyến tính** (phản ví dụ A > B > C > D). Em phải nói được: tại sao kết quả vẫn ổn định (tính thay thế + luật cầu tổng) và đã kiểm bằng gì (221.220 cặp nhóm, 0 vi phạm).

### B1.6 — "Tính thay thế" (substitutability) là gì? Giải thích cho một học sinh lớp 12.
- **Tra:** `CLAUDE.md` bất biến 8 và quy tắc 5: mọi hàm lựa chọn mới phải qua test thay thế được và luật tổng cầu trước khi đăng ký.

### B1.7 — "Dự trữ mềm" khác "dự trữ cứng" thế nào? Cho ví dụ số.
- **Tra:** `club_choice_function` (L377); test `test_suat_du_tru_thua_tu_chuyen_sang_luot_chung`. Vì sao phải *tính lại phân nhóm ở mỗi vòng* chứ không tính một lần? (Chú thích trong mã, và Lớp 2 của `CO_CHE_THUAT_TOAN.md`.)

### B1.8 — Nếu `reserve_capacity = 0` ở mọi CLB thì phần mềm còn lại gì?
- **Tra:** `CO_CHE_THUAT_TOAN.md` "Nếu trường KHÔNG dùng suất dự trữ": thu về DA thuần; đo được ~1/5 số em đổi CLB khi bỏ dự trữ.

### B1.9 — Vì sao học sinh là bên đề nghị chứ không phải CLB?
- **Tra:** `docs/NGHIEN_CUU_TOI_UU.md` TN1, TN2, `BAO_VE_BO_CAU_HOI.md` T3.8. Tối ưu cho phía nào? Số liệu TN2.

### B1.10 — Hiện tượng "khai gian nguyện vọng" là gì? Vì sao DA học sinh đề nghị chống được nhưng Boston thì không?
- **Tra:** TN3 — vét cạn 1.400 lượt, RB-DA **0/1.400**, Boston **258/1.400 (18,43%)**. Phép dò chứng minh gì và *không* chứng minh gì? (xem B.7.)

### B1.11 — Vì sao `compute_club_priority` không được nhận thứ hạng nguyện vọng của học sinh?
- **Tra:** docstring hàm (L123). Từ khóa: *endogeneity*, *strategy-proofness*. Em giải thích bằng một ví dụ: nếu CLB ưu tiên "em xếp CLB mình là NV1" thì em nào được lợi khi nói dối?

### B1.12 — Hai tầng ưu tiên: vì sao Tầng 1 luôn đứng trước Tầng 2 mà không xen kẽ? Có bất công với em không thi không?
- **Tra:** `compute_club_priority` — khóa sắp `(-điểm, stb, mã)`. Chính sách của trường, không phải của thuật toán — nhưng ai chịu trách nhiệm đặt chính sách đó?

### B1.13 — Tại sao dùng bốc thăm *một lần dùng chung* thay vì mỗi CLB bốc riêng?
- **Tra:** `CO_CHE_THUAT_TOAN.md` Lớp 3; `GIAI_DAP_BOC_THAM.md`. Hệ quả tới tính ổn định và công bằng?

### B1.14 — Mã học sinh có "kéo" thứ hạng bốc thăm không? Em kiểm bằng gì?
- **Tra:** `GIAI_DAP_BOC_THAM.md` — tương quan mã/số bốc thăm *đổi dấu qua 8 khối seed* → là nhiễu. **Đừng nói** *"số bốc thăm dựa trên mã học sinh"*.

### B1.15 — Học sinh đến muộn: chèn số thế nào cho công bằng? Giải thích hai tính chất được bảo đảm.
- **Tra:** `chen_stb_cho_hoc_sinh_moi` (L1279): thứ tự tương đối của em cũ không đổi; em mới rơi đều vào dàn số. Vì sao cách `MAX(stb)+1` cũ là sai?

### B1.16 — Kết quả có tối ưu Pareto không?
- **Câu bắt buộc đúng.** Hồ sơ mục 8 đã tự nêu: **không**; 32/140 em có thể cùng lên nếu phá 92 cặp ghép. Em phải nói được: vì sao *ổn định* và *Pareto tối ưu* không thể có cùng lúc, và vì sao em chọn ổn định.
- **Tra:** `NGHIEN_CUU_TOI_UU.md` TN5. Phân biệt **cặp phá vỡ** (học sinh–CLB, là lỗi) với **cặp đôi cùng có lợi** (học sinh–học sinh, là đánh đổi đã biết).

### B1.17 — "1,1% số học sinh có kết cục thay đổi theo bốc thăm" nghĩa là gì? Đo thế nào?
- **Tra:** `CO_CHE_THUAT_TOAN.md` Lớp 3 — đổi seed thì 1,1% đổi *kết cục có suất / không suất*; 0 cặp phá vỡ ở mọi seed trong 600 lần chạy. **Chú ý hồ sơ không nêu nguồn "600 lần"** (xem `BAO_VE_RA_SOAT_BAO_CAO.md` B7).

### B1.18 — Nhiều buổi: vì sao các buổi độc lập với nhau? Điều kiện nào mà nếu bỏ thì mất tính chất?
- **Tra:** khối chú thích "VÌ SAO PHẦN NÀY CHỈ LÀ CẮT — GỌI — GHÉP" trước `run_rbda_nhieu_buoi`; `stb_ngay` / `stb_tuan` / `stb_co_bu` (TN7).

## B.2 — Dữ liệu và đầu vào

### B2.1 — Dữ liệu đầu vào gồm những gì, ai cung cấp phần nào, định dạng nào?
- **Tra:** hồ sơ mục 6 (CLB, đăng ký dự thi, điểm, xếp hạng nguyện vọng) và `so_nhap.py` — *Sổ nhập CLB*, một tệp Excel hai trang (`1. CLB`, `2. Học sinh`).

### B2.2 — "Kiểm tra sức khỏe dữ liệu 8 loại cảnh báo" gồm những gì? Kể được 5 loại.
- **Chú ý:** `get_data_health_report` (api.py L251) trong mã hiện tại có **nhiều hơn 8 mã cảnh báo** (đếm thô bằng grep khoảng 20). Em chọn nói *"8 loại chính"* hay cập nhật con số? Phải nhất quán với hồ sơ. Gợi ý nhóm: thiếu điểm, thiếu nguyện vọng, nhóm dự trữ mồ côi, thi quá trần, quá tải, điểm bất thường, điểm không đăng ký thi…

### B2.3 — "Tách riêng dòng không hợp lệ kèm cảnh báo, phần còn lại vẫn nạp" — vì sao không dừng cả lần nạp?
- Đánh đổi giữa *an toàn* và *tiện*. Hậu quả nếu người nhập không đọc cảnh báo?

### B2.4 — Excel làm mất số 0 đầu mã học sinh: phát hiện thế nào?
- **Tra:** `api_nhap.py`; `BAN_GIAO.md` quyết định 13 — `student_id` **phân biệt** hoa/thường (chỉ cảnh báo, không tự gộp), `club_id` thì **không**. Vì sao khác nhau?

### B2.5 — Vì sao không đoán loại tệp CSV khi tiêu đề không đủ kết luận?
- **Tra:** `BAN_GIAO.md` quyết định 7, `detect_csv_kind()` — dữ liệu vào sai bảng mà vẫn báo thành công.

### B2.6 — Dữ liệu mô phỏng được sinh thế nào? Có "đúng thực tế" không?
- **Câu cực kỳ quan trọng.** `BAN_GIAO.md`: bộ chính được **cố ý thiết kế để cạnh tranh cao** (3 CLB "hot" trọng số 10, 3 CLB "nguội" 0,75, suất dự trữ đặt ở CLB chật) — *"không mô phỏng phân bố tự nhiên"*. Vậy **59% nguyện vọng 1** trong hồ sơ nghĩa là gì? Có thể dùng nó như bằng chứng chất lượng không?
- **Tra:** `du_lieu_test/tao_du_lieu_test.py` (seed 2026). **Hồ sơ mục 3 viết: "Dữ liệu này được AI sinh ra và không trải qua quá trình thu thập"** — còn trong kho là *script có seed*, không phải AI sinh trực tiếp từng dòng. Em chốt cách nói chính xác.

## B.3 — Kiến trúc và triển khai

### B3.1 — Vẽ sơ đồ kiến trúc: pywebview, `api.py`, SQLite, HTML/JS. Dữ liệu đi theo đường nào khi bấm "Chạy"?
- **Tra:** `CLAUDE.md` bản đồ mã; `api.py` `_run_pipeline_da_khoa`.

### B3.2 — Pipeline có 5 bước theo thứ tự nào, và vì sao thứ tự đó là bất biến?
- **Tra:** `CLAUDE.md` bất biến 5: sao lưu → kiểm dữ liệu → khóa seed/STB → giải → sanity/verify → ghi trong **một giao dịch** → xuất; lỗi thì rollback. Điều gì xảy ra nếu có **một** cặp phá vỡ? (rollback **toàn bộ** lần chạy, kể cả số STB vừa vẽ.)

### B3.3 — Vì sao SQLite chứ không phải server, không phải file JSON?
- **Tra:** quyết định 1 và 5 trong `BAN_GIAO.md`: không WAL (sao lưu USB bằng copy tay có thể thiếu dữ liệu), `journal_mode=DELETE`, `synchronous=FULL`, `busy_timeout=15000`; offline-first, không đăng nhập.

### B3.4 — Sao lưu 10 bản hoạt động ra sao? Khôi phục thế nào nếu app.db hỏng?
- **Tra:** `PipelineAPI._backup_db` (api.py L766) dùng SQLite Backup API, `_MAX_BACKUPS`; `recovery.py`, `recovery.html`. Hồ sơ mục 8 lại ghi *"bổ sung chức năng sao lưu và khôi phục **chủ động**"* là hướng phát triển — em phân biệt *tự động* (đã có) và *chủ động* (chưa) thế nào?

### B3.5 — Vì sao có chế độ dự phòng mở bằng trình duyệt? Có an toàn không?
- **Tra:** `browser_host.py`: chỉ nghe `127.0.0.1`, mọi lời gọi API kèm token ngẫu nhiên (`secrets`, `compare_digest`), chặn tên máy lạ. Bản vá lỗi 13 (`EventSource("/__alive__")`) vì sao ping bằng `setInterval` hỏng?

### B3.6 — "Hợp đồng `{ok, data, errors}`" là gì? Vì sao quan trọng?
- **Tra:** `CLAUDE.md` bất biến 6, `i18n_errors.py` → `tao_i18n_js.py` → `i18n_loi.js` (một nguồn thông báo lỗi song ngữ; test `test_i18n_sync.py` canh bản sinh).

### B3.7 — Phần mềm xuất những tệp nào? Vì sao xuất cạnh `app.db`? Vì sao `utf-8-sig`?
- **Tra:** `BAN_GIAO.md` quyết định 9; `_an_toan_cho_excel` (ô bắt đầu `= + - @` bị Excel tính như công thức).

### B3.8 — Đóng gói thế nào? `PyInstaller + GitHub Actions` làm gì? Em tái lập bản `.exe` thế nào?
- **Tra:** `kiosk.spec`, `build_windows.bat`, workflow *Build Windows executable (rbda-kiosk)*; test `test_dong_goi_*`. Lưu ý: **kho này không chứa bản build thật**.

## B.4 — Kiểm thử

### B4.1 — Con số kiểm thử nào đúng: 663, 831, 1.160 hay 1.515?
- Xem D.2. Em phải biết **vì sao** có bốn con số và con số trong hồ sơ nghĩa là gì.

### B4.2 — `verify_stability` làm gì, vì sao dùng chính `club_choice_function`, không dùng bảng ưu tiên tĩnh?
- **Tra:** `verify_stability` (L606). Em đọc được và giải thích vòng lặp `for candidate_cid in prefs[:current_idx]`: chỉ xét CLB em *thích hơn* CLB hiện tại.

### B4.3 — "Test hồi quy băm kết quả từng em" nghĩa là gì? Vì sao quan trọng khi AI sửa mã?
- **Tra:** `tests/test_ket_qua_khong_doi.py`, `CLAUDE.md` bất biến 1.

### B4.4 — Bộ dữ liệu "cố tình tạo lỗi" cài những lỗi gì? Phần mềm bắt hết không?
- **Tra:** `TEST_04_CO_LOI_CO_Y.xlsx` — *cố ý sai 6 chỗ*; `SO_NHAP_CO_LOI_CO_Y.xlsx`.

### B4.5 — "Vét cạn" ở quy mô nhỏ (7 em, 4 CLB) suy ra được gì cho 800 em?
- **Tra:** `BAO_VE_BO_CAU_HOI.md` T3.6. Hạn chế: bằng chứng tồn tại cho phản ví dụ nhỏ, **không phải chứng minh**.

### B4.6 — Test giao diện bằng Playwright + Chromium: có test nào chập chờn không?
- **Tra:** `BAN_GIAO.md` mục 5 — `test_moi_o_so_tren_man_hinh_cap_nhat_ngay_sau_khi_xoa` đỏ 1 trên 2 lần chạy toàn bộ ngày 02/09; chưa sửa, cố ý. Trả lời đúng như tài liệu đã ghi: *"không phải lỗi sản phẩm, chập chờn do thời gian chờ"*.

### B4.7 — Phần mềm đã chạy được trên **Windows thật** nhưng máy phát triển là Linux. Em biết gì và *không* biết gì?
- **Tra:** `BAN_GIAO.md`: *"Máy phát triển là Linux — hai lớp xử lý này CHƯA CHẠY THẬT lần nào"* (trước 02/09), rồi học sinh tự xác nhận chạy ổn trên Windows. Nguồn của khẳng định là **chính học sinh**, không phải log.

## B.5 — Giới hạn

### B5.1 — Giới hạn 10 nguyện vọng và 5 CLB thi: vì sao? Có bỏ được không?
- **Tra:** `TRAN_NGUYEN_VONG_MOI_BUOI = 10` (giới hạn của câu Ranking trên Microsoft Forms) và `TRAN_CLB_THI_MOI_BUOI = 5` (chính sách trường, không phải kỹ thuật) — hai lý do **khác nhau**, đừng gộp. Hằng khai báo **hai lần** (Python và `js/05_quan_ly.js`): rủi ro lệch.

### B5.2 — Hồ sơ nói MS Forms; hai kỹ năng trong kho nói Google Forms. Vậy thu phiếu bằng cái nào?
- **Tra:** `.claude/skills/tao-google-form-clb`, `xu-li-raw-forms`; docstring đầu `rbda_priority_pipeline.py` (MS Forms). Em chốt một câu: trường dùng nền tảng nào, phần mềm hỗ trợ cái nào, phần kia là tính năng bổ sung.

### B5.3 — Giới hạn lớn nhất của dự án là gì? Em nói trước thay vì đợi bị hỏi như thế nào?
- **Tra:** `BAO_VE_BO_CAU_HOI.md` mục "Hai hạn chế phải chuẩn bị sẵn để CHỦ ĐỘNG nêu": chỉ có dữ liệu mô phỏng; vét cạn nhỏ; không Pareto.

---
---

# PHẦN C — CÂU HỎI "AI QUÉT MÃ"

> **Cách nghĩ:** một bộ quét mã (AI hoặc công cụ tĩnh) đọc *tất cả* tệp cùng lúc, không biết
> bối cảnh học sinh, và sẽ báo những chỗ *trông có vẻ* nguy hiểm, mâu thuẫn hoặc quá lớn. Mỗi
> câu dưới đây là một thứ nó có thể thấy được thật sự trong kho. **Em phải mở đúng hàm, đọc, rồi quyết định:** đây là lỗi thật cần sửa, hay quyết định có chủ ý cần giải thích?
> Số dòng đối chiếu ngày 15/10/2026; có thể trôi — định vị theo tên hàm.

## C.1 — Mâu thuẫn tài liệu ↔ mã (dễ bị bắt nhất)

### C1.1 — `run_rbda` (rbda_priority_pipeline.py L456) có docstring nói *"đã đối chiếu khớp 100% với `03_reference_rbda.py`… (xem `compare_with_reference.py`)"*, nhưng docstring đầu tệp (L14–19) nói các tệp đó *"CHƯA BAO GIỜ được đưa vào kho"*.
- **Câu hỏi giám khảo:** *"Bằng chứng nào cho tuyên bố 'khớp 100%' khi không có tệp tham chiếu?"*
- **Em phải quyết:** sửa docstring cho thống nhất (việc nhỏ, nên làm trước buổi phỏng vấn) và chuẩn bị câu trả lời: kiểm chứng *hiện có thể tái lập* là gì (`verify_stability`, vét cạn TN1, test hồi quy)?

### C1.2 — `max_rounds=1000` và chú thích *"gấp 100 lần mức cần"*, nhưng `BOI_CANH_DU_AN.md` ghi đo thực tế trung vị 9 và lớn nhất 37 vòng cho danh sách 3 mục (docstring nói số vòng = độ dài danh sách).
- **Câu hỏi:** *"Chú thích trong mã mâu thuẫn với số đo của chính em?"* — em điều tra: số vòng có thật sự bị chặn bởi độ dài danh sách không? (Gợi ý: khi một CLB đẩy một em đang giữ ra, em đó phải đề nghị lại — kiểm lập luận *"mỗi vòng, mỗi em chưa có chỗ tiến đúng một nguyện vọng"* xem còn đúng trong mọi trường hợp không.) Nếu chú thích sai thì sửa.

### C1.3 — Hồ sơ nói *"thuật toán Gale–Shapley"*, mã nói *"RB-DA / Deferred Acceptance"*, báo cáo từng nói *"Sharpley"*.
- **Câu hỏi:** *"Đây là thuật toán gì, của ai?"* — tên đúng là **Gale–Shapley** (`CLAUDE.md` có nhắc sửa lỗi chính tả "Sharpley" trong báo cáo gốc). Em phân biệt được: Gale–Shapley (1962), Deferred Acceptance, RB-DA (tên đội đặt cho ghép Gale–Shapley + dự trữ mềm + STB + ưu tiên hai tầng)?

### C1.4 — Báo cáo vẫn mô hình CLB là *"một danh sách ưu tiên Q_j"*, nhưng `club_choice_function` thực tế không phải một thứ tự tuyến tính khi có dự trữ.
- **Tra:** `CO_CHE_THUAT_TOAN.md` đầu tệp; `BAO_VE_RA_SOAT_BAO_CAO.md` B1–B2. AI quét tài liệu *và* mã sẽ thấy hai mô hình khác nhau. Em giải thích: vì sao khác, vì sao vẫn đúng.

## C.2 — Cấu trúc và chất lượng mã

### C2.1 — `rbda_priority_pipeline.py` dài ~2.460 dòng, gộp **thuật toán + schema + I/O SQLite + di trú CSDL + sinh dữ liệu mẫu + hàm tìm kiếm tiếng Việt**.
- **Câu hỏi:** *"Vì sao module thuật toán lại chứa cả `connect_db`, `di_tru_schema`, `seed_sample_data`, `khop_tim`? Đó có phải 'God module' không?"* — em có lý do lịch sử (`DEFAULT_SCHEMA` là nguồn duy nhất, giữ cho các script đo dùng chung), nhưng cũng phải thừa nhận đánh đổi. Nếu có thêm thời gian, em tách thế nào mà không làm đổi kết quả (bất biến 1)?

### C2.2 — Khoảng **70 khối `except Exception`** trong các tệp `api*.py` (đếm thô bằng grep) đều trả về `{ok: false}`.
- **Câu hỏi:** *"Nuốt mọi ngoại lệ có che giấu lỗi không?"* — em giải thích: đây là *hợp đồng* giữa JS và Python (`{ok, data, errors}`), lỗi vẫn được báo thành mã lỗi song ngữ. Nhưng có chỗ nào ngoại lệ bị nuốt *không báo gì* không? Hãy phân loại các khối `except Exception:` **không có `as e`**: `api.py` ~L760 chỉ rollback rồi `raise` lại (đúng), còn `api_chung.py` ~L112 và ~L127 là `pass` rồi lùi xuống phương án khác (tìm thư mục Windows). Em mở từng chỗ và nói được vì sao mỗi chỗ chấp nhận được, hoặc chỗ nào nên ghi log.

### C2.3 — Thông báo lỗi trong `run_rbda` (L579–584) và `club_choice_function` viết **tiếng Việt không dấu**, trong khi hầu hết mã khác có dấu. `i18n_errors.py` lại là "một nguồn thông báo lỗi".
- **Câu hỏi:** *"Hai ngôn ngữ, hai quy ước, và `ValueError` bằng tiếng Việt không dấu — chuẩn nào?"* — chỗ nào đi qua `err(...)` (có i18n), chỗ nào là chuỗi thô (đối với lập trình viên)?

### C2.4 — Phân tầng ưu tiên lúc đầu chỉ có `compute_club_priority`, sau đó thêm `uu_tien_theo_nhom`, `tier_rank`, `bo_qua_du_tru`, `luat_xep_*`… Tham số mặc định giữ hành vi cũ.
- **Câu hỏi:** *"Nhiều cờ như vậy làm số đường chạy tăng; làm sao biết đường nào đang được dùng và đường mặc định vẫn giống hệt?"* — `CLAUDE.md` bất biến 1 và test `test_ket_qua_khong_doi.py`.

### C2.5 — Kho có nhiều tài liệu lớn (`BAN_GIAO.md` 1.844 dòng, `KE_HOACH_SUA_THIET_KE.md`, báo cáo `.docx`, poster, slide) cạnh mã.
- **Câu hỏi:** *"Tài liệu nhiều hơn mã? Cái nào là nguồn đúng khi hai tài liệu mâu thuẫn?"* Ví dụ: `BAN_GIAO.md` ghi 1.160 test, `CLAUDE.md` ghi 1.515 ca / 89 tệp (10/10/2026), hồ sơ ghi 663 lượt.

### C2.6 — Chú thích rất dài, kể lịch sử lỗi trong chính mã (ví dụ `generate_stb_lottery`, `chen_stb_cho_hoc_sinh_moi`, đầu `rbda_priority_pipeline.py`).
- **Câu hỏi:** *"Chú thích tường thuật nhật ký lỗi có thuộc về mã không? Dễ lỗi thời."* Em bảo vệ: *vì sao* quan trọng hơn *cái gì*; nhưng hãy chọn một chú thích bạn thấy có giá trị nhất để dẫn ra.

## C.3 — Bảo mật (khả năng bị cảnh báo cao)

### C3.1 — `chan_doan.go_dau_tai_ve()` **xóa luồng NTFS `Zone.Identifier`** khỏi mọi `.dll/.exe/.pyd` trong gói, chạy trước `import webview`.
- **Câu hỏi quét mã:** *"Chương trình gỡ dấu 'tải từ Internet' của chính nó — đây là hành vi che giấu nguồn gốc kiểu phần mềm độc hại."* Em trả lời: vì sao cần (Windows/.NET Framework từ chối nạp assembly mang dấu, gây lỗi pythonnet), phạm vi chỉ trong thư mục của gói, không cần quyền admin — và **vì sao đây là cách chữa triệu chứng chứ chưa phải cách tốt nhất** (chữ ký số mới là cách đúng).

### C3.2 — `PhanBoCauLacBo.exe.config` có `loadFromRemoteSources enabled="true"`.
- **Câu hỏi:** *"Cấu hình này hạ rào bảo vệ .NET — rủi ro là gì?"* Phải nói được: nó cho phép nạp assembly từ nguồn 'từ xa'; vì sao chấp nhận ở đây (gói tự chứa, offline), và biện pháp thay thế.

### C3.3 — `ky_va_tin_cay.ps1` — kịch bản PowerShell tin cậy chứng chỉ.
- **Câu hỏi:** *"Hướng dẫn người dùng chạy script thêm chứng chỉ vào kho tin cậy của máy — người dùng cuối làm sao biết script an toàn?"* Mở tệp, đọc từng dòng, và chuẩn bị giải thích nó chạy gì, thêm gì, xóa được không.

### C3.4 — `browser_host.py` mở một máy chủ HTTP cục bộ.
- **Câu hỏi:** *"Máy chủ cục bộ có bị tấn công từ trang web khác (CSRF, DNS rebinding) không?"* Trả lời dựa trên mã: chỉ `127.0.0.1`, token ngẫu nhiên mỗi lần khởi động, `compare_digest`, chặn `Host` lạ, trang HTML cũng đòi token, không phục vụ `app.db` tùy tiện (`GET /app.db`). Mở đầu tệp xem bạn nhớ được bao nhiêu lớp.

### C3.5 — `api_xuat.py` (~L660–690) `mo_thu_muc` dùng `os.startfile` / `subprocess.Popen([lenh, thu_muc])`, hàm gọi được từ JavaScript.
- **Câu hỏi:** *"Gọi tiến trình hệ thống từ một đường dẫn do client truyền — command injection / path traversal?"* Em trả lời: không qua shell, `realpath` + `commonpath`, chỉ mở thư mục nằm trong gốc xuất hợp lệ, có test `test_mo_thu_muc.py`. Có `# noqa: S606` — vì sao cần?

### C3.6 — `api_quan_ly.py` (~L205–215) ghép chuỗi SQL bằng f-string: `f"SELECT COUNT(*) FROM students s{where_clause}"`.
- **Câu hỏi:** *"SQL injection?"* Em phải đọc được: `where_clause` là chuỗi **cố định** do mã tạo; giá trị người dùng đi qua tham số `?`. Rồi cho thêm: có chỗ nào f-string SQL khác mà phần ghép *không* cố định không? Hãy `grep` và tự duyệt từng chỗ.

### C3.7 — `app.db` không mã hóa, không đăng nhập, chứa tên học sinh.
- **Câu hỏi:** *"Dữ liệu cá nhân trẻ em, không mã hóa, không kiểm soát truy cập — chấp nhận được?"* Cân nhắc: mô hình đe dọa là máy kiosk trong phòng của giáo viên; nhưng nếu giám khảo nói đó là rủi ro, em đề xuất lớp nào (mã hóa tệp, mật khẩu mở ứng dụng, xóa dữ liệu sau năm học)? Tránh nói *"không cần"*.

## C.4 — Thuật toán và tính tái lập

### C4.1 — `generate_stb_lottery` dùng `random.Random(seed)`; `CLAUDE.md` bất biến 3 nói *"sinh bằng crc32 (không dùng hash())"*. Có `crc32` ở đâu trong hai hàm này không?
- **Câu hỏi:** *"Mô tả không khớp mã?"* Mở `_seed_cua_buoi` (L894) và `sinh_stb_theo_buoi` (L911) để xem `crc32` thật sự nằm ở đâu (seed theo buổi). Em phải chỉ đúng chỗ.

### C4.2 — Cùng seed ⇒ cùng kết quả: đúng với mọi phiên bản Python không?
- **Câu hỏi:** *"`random.shuffle` có ổn định giữa các phiên bản Python không?"* Em đã khóa Python 3.11 qua PyInstaller, nhưng vẫn phải nói được phạm vi lời hứa: *tái lập trên cùng bản chạy; qua phiên bản khác không bảo đảm*.

### C4.3 — Khóa số bốc thăm sau lần chạy đầu: nếu quản trị viên *không thích* kết quả thì làm gì?
- **Tra:** vẽ lại cần xác nhận hai bước, để lại dấu vết trong `run_history` (không bao giờ ghi đè hay xóa). Còn nếu người dùng **xóa `app.db`** rồi chạy lại với seed khác thì sao? (Xem `GIAI_DAP_BOC_THAM.md` Câu 3.) Phần mềm chống được *thử-nhiều-lần-rồi-chọn* ở mức nào, và không chống được ở mức nào?

### C4.4 — `compute_club_priority` có khóa phá hòa cuối là **mã học sinh** (`sid`). 
- **Câu hỏi:** *"Mã học sinh chen vào thứ tự ưu tiên — có thiên vị em mã nhỏ không?"* Chú thích nói số bốc thăm là hoán vị 0..n-1 nên bình thường **không bao giờ trùng**; khóa `sid` chỉ để quyết định trong trường hợp dữ liệu hỏng. Em phải nói được **khi nào** nhánh này có thể xảy ra (CSDL không có UNIQUE trên `stb_number`).

### C4.5 — `club_choice_function`: `rank.get(s, len(rank))` — một học sinh không có trong `rank` bị xếp *cuối*.
- **Câu hỏi:** *"Điều gì xảy ra nếu thiếu thứ hạng — im lặng hay lỗi?"* Khi nào một em có mặt trong pool nhưng không nằm trong `rank`? (Nhất là qua `verify_stability`, nơi có dòng `if sid not in rank: continue`.)

## C.5 — "Vai trò AI" trong chính mã

### C5.1 — Mã nhắc nhiều lần đến "bản tham chiếu", "đối chiếu", "reference" mà không có trong kho.
- Gộp với C1.1: tốt nhất chuẩn bị sẵn *một trang* "những gì có thể tái lập" để mở cho giám khảo thay vì tranh luận.

### C5.2 — Trong kho có các thư mục `.claude/skills/` (sinh dữ liệu, tạo Google Form, xử lý raw, tạo workspace) và `docs/PROMPTS_WORKSPACE.md`.
- **Câu hỏi:** *"Đây là AI nằm trong sản phẩm hay trong quy trình? Người dùng cuối có dùng không?"* — em nói rõ: đây là *kỹ năng của Claude Code* giúp người vận hành chuẩn bị dữ liệu, **không** chạy trong `.exe`.

### C5.3 — `CLAUDE.md` trong kho chứa chỉ dẫn cho trợ lý AI (bất biến, quy tắc, "dừng và hỏi khi…").
- **Câu hỏi:** *"Em viết chỉ dẫn cho AI để nó không phá thuật toán — đó có phải một kỹ thuật 'prompt engineering' em tự thiết kế không?"* Đây có thể là một **điểm mạnh về quy trình** nếu em giải thích được 3 bất biến vì sao tồn tại.

---
---

# PHẦN D — ĐỐI CHIẾU HỒ SƠ ↔ KHO MÃ

> Đây là các câu khẳng định **trong hồ sơ nộp**. Với mỗi dòng, em phải có *một câu trả lời đúng
> sự thật*. Cột "Rủi ro" là điều em cần giải quyết **trước** buổi phỏng vấn.

| # | Hồ sơ nói (mục) | Kho mã / tài liệu cho thấy | Rủi ro | Em chốt câu nào? |
|---|---|---|---|---|
| D.1 | Dữ liệu mô phỏng *"được AI sinh ra"* (mục 3) | Sinh bằng script có seed: `du_lieu_test/tao_du_lieu_test.py` (seed 2026); bộ chính cố ý thiết kế cạnh tranh cao | Giám khảo hỏi *"AI sinh hay script"* | Cách nói chính xác về nguồn gốc dữ liệu |
| D.2 | *"663 lượt kiểm thử tự động trên ba bộ dữ liệu"* (mục 7) | Không tìm thấy số 663 ở đâu trong kho. `CLAUDE.md`: 89 tệp, **1.515 ca** (10/10/2026); `BAN_GIAO.md`: 831→1.160 tùy thời điểm | Con số không truy nguyên được; thấp hơn hiện tại | Giải thích 663 là gì (ca test? lượt chạy? tại thời điểm nào?), và nay là bao nhiêu |
| D.3 | *"tỉ lệ trục lợi bằng khai gian giảm từ 18,4% xuống 0%"* — đặt trong câu **"trước và sau khi khắc phục lỗi công bằng"** (mục 7) | Trong `NGHIEN_CUU_TOI_UU.md` TN3, **18,43% là của cơ chế Boston** (258/1.400), RB-DA là 0/1.400. Không phải "trước/sau khi sửa lỗi" của chính RB-DA. Lỗi công bằng đã sửa là chuyện *chèn STB* (0 → TB 3,5 em) | **Đây là điểm nhầm lẫn có thể bị xem là sai sự thật** | Phân biệt rõ hai phát hiện: (1) so với Boston; (2) sửa lỗi STB. Không gộp chung |
| D.4 | *"số học sinh đăng ký muộn… tăng từ 0 lên trung bình 3,5 em bằng mức kỳ vọng"* | Khớp `CO_CHE_THUAT_TOAN.md`: 20 em cũ + 10 em mới, 10 suất; kỳ vọng ~3,3; TB 3,5 (20 seed) | Nên nói rõ *"kịch bản thử nhỏ, đều Tầng 2"* | Mô tả đúng quy mô thí nghiệm |
| D.5 | 5.000 HS / 100 CLB *"hoàn tất trong 7,65 giây"* (mục 7) | `BAO_VE_RA_SOAT_BAO_CAO.md` A1: 7,65 s là cột `t_phan_bo_giay` — **chỉ bước phân bổ**, lần chạy lâu nhất, không phải toàn bộ từ bấm nút | Gán nhầm phạm vi thời gian | Nói *"bước phân bổ"*, không nói *"toàn bộ"* |
| D.6 | 120 em: 108/120 xếp, 59% NV1, 0,011 s, 0 cảnh báo (mục 7) | Khớp `BAN_GIAO.md` (30/08). Nhưng bộ cố ý cạnh tranh cao, **không mô phỏng phân bố tự nhiên** | 59% NV1 có thể bị đọc như chất lượng thực tế | Nêu rõ: thiết kế để thuật toán *phải làm việc* |
| D.7 | *"140/140 em đều được xếp"* (mục 7) | `bo_sach` 140 em / 12 CLB; 0 cảnh báo | Có phải vì dữ liệu dễ (đủ chỗ)? | Giải thích tổng sức chứa ≥ 140 và vì sao con số này không phải thành tích |
| D.8 | *"người dùng xác nhận phần mềm khởi động… không lỗi"* (mục 7) | `BAN_GIAO.md` 02/09: người xác nhận là **học sinh làm dự án**, sau khi vá lỗi 25 | Bị coi là người dùng thật | Nói trung thực + (nếu có thể) bổ sung xác nhận độc lập |
| D.9 | *"32/140 em… đánh đổi bằng việc phá vỡ 92 cặp ghép"* (mục 8) | Khớp `SO_LIEU_DA_KIEM_CHUNG.md`, `BAO_VE_BO_CAU_HOI.md` T3.1 (16 chu trình, 32/140; hạng TB 2,100→1,771, sinh 92 cặp phá vỡ). Lưu ý các chu trình dài hơn 2 | Dễ nhầm với *"85 cặp đôi cùng có lợi"* (seed 42) | Phân biệt "cặp phá vỡ" (HS–CLB) và "cặp đôi cùng có lợi" (HS–HS) |
| D.10 | *"yếu tố bốc thăm khiến 1,1% số học sinh có kết cục thay đổi"* | Khớp `CO_CHE_THUAT_TOAN.md` Lớp 3. "kết cục" = có/không có suất | Hiểu nhầm là "1,1% đổi CLB" | Định nghĩa "kết cục" trước khi nói |
| D.11 | *"kiểm tra sức khỏe dữ liệu 8 loại cảnh báo"* (mục 4) | `get_data_health_report` có nhiều hơn (đếm thô ~20 mã) | Giám khảo mở mã đếm | Thống nhất: "8 nhóm chính" hay cập nhật hồ sơ |
| D.12 | *"sao lưu trước và sau mỗi lần chạy"* (mục 4) / *"tự động sao lưu 10 bản"* (mục 8) | `_backup_db` sao lưu **trước** khi chạy; giữ `_MAX_BACKUPS` bản. "Sau khi chạy" có sao lưu riêng không? Kiểm tra mã | Có thể không khớp "sau" | Đọc `_run_pipeline_da_khoa`: chỗ nào sao lưu, chỗ nào chụp `ket_qua_truoc` |
| D.13 | *"tối đa 10 nguyện vọng và 5 CLB dự thi mỗi buổi"* (mục 8) | `TRAN_NGUYEN_VONG_MOI_BUOI=10`, `TRAN_CLB_THI_MOI_BUOI=5`; hằng khai báo hai nơi (Python, JS) | Giám khảo hỏi *"vì sao 5?"* | Hai lý do khác nhau (công cụ Forms vs chính sách trường) |
| D.14 | Công cụ: *"Claude Code… Opus 5.0 và Sonnet 5.0"* (mục 5) | Tên mô hình thực tế phải đối chiếu **lịch sử prompt (mục 9)**; kho chỉ có tác giả commit "Claude" | Ghi sai phiên bản/mô hình | Kiểm lại từ nhật ký thật rồi nói đúng |
| D.15 | Mục 3 liệt kê *khảo sát MS Form* và *dữ liệu nhà trường* | Kho chỉ có **bộ câu hỏi** khảo sát, không có **kết quả** | Không có số liệu để dẫn | Mang theo kết quả: n, các % chính |
| D.16 | *"Đối tượng sử dụng: Học sinh/CLB/Nhà trường"* (mục 2), hướng phát triển *"màn hình giải trình kết quả cho từng học sinh"* (mục 8) | Chưa làm (chỉ có `rejection_log`) | Cam kết quá lớn | Rõ ràng: đã có gì, chưa có gì |

---
---

# PHẦN E — TÍNH NĂNG VÀ ĐIỀU ĐẶC BIỆT (CHỦ ĐỘNG NÓI)

> Đây là những thứ **nên nói trước khi bị hỏi**. Mỗi mục: một câu, và một con số hoặc một ví dụ.
> Đánh dấu ✅ khi em tự nói trọn trong 30 giây.

## E.1 — Điều đặc biệt của thuật toán

- [ ] **Không phải Gale–Shapley nguyên bản.** Là **RB-DA**: học sinh đề nghị + dự trữ mềm hai lượt + bốc thăm một lần dùng chung + ưu tiên hai tầng (thi / không thi). Mỗi lớp ra đời từ hoàn cảnh trường: có CLB thi tuyển, có CLB không.
- [ ] **Kiểm chứng ổn định bằng chính hàm lựa chọn** (không dùng bảng tĩnh): `verify_stability`. Có cặp phá vỡ → **rollback cả lần chạy**.
- [ ] **Chống khai gian đã vét cạn:** 0/1.400 lượt khai gian có lợi dưới RB-DA, so với 258/1.400 dưới Boston.
- [ ] **Bốc thăm có thể kiểm toán:** một số/em, dùng chung mọi CLB, tái lập theo seed, khóa sau lần chạy đầu, không phụ thuộc thứ tự nhập.
- [ ] **Công bằng cho em đến muộn:** chèn số ngẫu nhiên đều, giữ thứ tự tương đối của em cũ (0 → TB 3,5 em giành được suất).
- [ ] **Nhiều buổi:** mỗi buổi một lần chạy độc lập, ổn định cả tuần = ổn định từng buổi.
- [ ] **Thừa nhận giới hạn bằng số:** không tối ưu Pareto (32/140 em), 1,1% đổi kết cục theo bốc thăm, dữ liệu mô phỏng.

## E.2 — Điều đặc biệt của sản phẩm

- [ ] **Offline hoàn toàn, một tệp `.exe`, không đăng nhập** — phù hợp máy kiosk trường học.
- [ ] **Sổ nhập CLB:** *một* tệp Excel hai trang thay cho ba tệp nạp; tự nhận diện loại tệp; dòng sai tách riêng kèm cảnh báo nêu *mục và cột*, phần còn lại vẫn nạp.
- [ ] **Bắt lỗi âm thầm** (các lỗi làm sai kết quả mà vẫn báo thành công): Excel làm mất số 0 đầu, mã trùng hoa/thường, nhãn dự trữ viết khác nhau (`chinh_sach` vs `Chính sách`), điểm "ẩn" sau khi bỏ tick, thi quá 5 CLB sau khi CLB đổi buổi.
- [ ] **Chấm điểm mù:** giám khảo không thấy số bốc thăm hay thứ hạng nguyện vọng khi chấm.
- [ ] **Sao lưu và phục hồi:** SQLite Backup API, giữ 10 bản, màn hình phục hồi khi `app.db` hỏng; mọi lần chạy ghi thêm một dòng `run_history`, không bao giờ ghi đè.
- [ ] **Một giao dịch duy nhất:** lỗi giữa chừng thì không có gì bị ghi nửa vời.
- [ ] **"Kết quả có thể đã cũ":** dấu vân tay SHA-256 của dữ liệu quyết định kết quả; sửa dữ liệu sau khi chạy thì phần mềm báo.
- [ ] **So sánh với lần chạy trước:** ai đổi CLB, ai mất suất, ai được suất.
- [ ] **Xuất dữ liệu có tuỳ chọn:** kết quả tổng, từng CLB, danh sách chưa xếp, hồ sơ từng học sinh, dữ liệu đầu vào nạp lại được; chống tiêm công thức Excel (`= + - @`).
- [ ] **Tìm kiếm tiếng Việt:** bỏ dấu, `đ→d`, không phân biệt hoa/thường (`khop_tim`).
- [ ] **Song ngữ Việt/Anh**, thông báo lỗi chỉ có một nguồn.
- [ ] **Chế độ dự phòng** mở bằng cửa sổ trình duyệt riêng khi cửa sổ gốc không chạy được, có token và chỉ nghe `127.0.0.1`.
- [ ] **Chẩn đoán:** `loi_khoi_dong.txt`, hiện đường chạy nào ở góc thanh bên.
- [ ] **Bộ kỹ năng cho người vận hành** (`.claude/skills`): sinh/soát dữ liệu, tạo Google Form, xử lý raw từ Forms, dựng workspace — *trong quy trình, không nằm trong `.exe`*.

## E.3 — Điều đặc biệt của quá trình làm

- [ ] **Quy trình có kỷ luật với AI:** `CLAUDE.md` đặt bất biến (kết quả mặc định trùng khít qua mọi thay đổi; hàm ưu tiên không được đọc thứ hạng nguyện vọng; run_history không bị ghi đè) — AI không được phá.
- [ ] **Test trước, sửa sau:** test thất bại theo tiêu chí kiểm nhận rồi mới sửa; test canh từng lỗi đã sửa (25 lỗi, 10 lỗi "im lặng").
- [ ] **Số liệu đều truy nguyên được** tới script đo trong `du_lieu_test/` (tái lập một lệnh).
- [ ] **Nói thẳng số liệu là mô phỏng** và chưa có dữ liệu vận hành thật.
- [ ] **Kế hoạch tổng quát hóa** cho 12 ngành đã được đánh giá (không phải lời hứa bán hàng).

---
---

# PHẦN F — TÌNH HUỐNG VÀ DEMO TRỰC TIẾP

> Giám khảo có thể bảo em *"chạy cho tôi xem"*. Hãy tập đến mức không nhìn bàn phím.

### F.1 — Demo 3 phút: từ tệp Excel đến kết quả.
1. Mở phần mềm với `du_lieu_test/vi_du_huong_dan/` (10 em, 4 CLB) hoặc `SO_NHAP_MAU_120HS_3BUOI.xlsx`.
2. Nạp Sổ nhập. Chỉ ra cảnh báo (nếu có).
3. Xem **Bảng sức khỏe dữ liệu**.
4. Chạy. Mở thẻ **Kết quả**: tóm tắt, mức đáp ứng nguyện vọng, biểu đồ lấp đầy.
5. Xuất tệp, mở thư mục.
- **Câu hỏi đi kèm:** nếu cửa sổ không mở, em làm gì? (chế độ dự phòng, `loi_khoi_dong.txt`.)

### F.2 — "Nạp tệp có lỗi cố ý cho tôi xem."
- Dùng `SO_NHAP_CO_LOI_CO_Y.xlsx` hoặc `TEST_04_CO_LOI_CO_Y.xlsx`. Em đọc to từng cảnh báo và giải thích vì sao đó là lỗi.

### F.3 — "Đổi seed — kết quả đổi bao nhiêu?"
- Đổi hạt giống (nút *Vẽ lại*, xác nhận 2 bước). Em nói trước dự đoán (khoảng 1,1% đổi kết cục có suất), rồi chạy xem. Điều gì xảy ra với `run_history`?

### F.4 — "Thêm một học sinh đến muộn."
- Thêm em mới, chạy lại. Em giải thích: em mới nhận số bốc thăm thế nào, em cũ bị ảnh hưởng thế nào, vì sao thứ tự tương đối của em cũ không đổi.

### F.5 — "Tăng sức chứa một CLB lên 1 chỗ nữa."
- Ai được lợi? Có thể có cặp phá vỡ không? (Đã chạy lại toàn bộ.) Phần mềm có hỗ trợ "chạy lại từng phần" không? (`chi_buoi`.)

### F.6 — "Một em rút lui sau khi công bố."
- Hiện phần mềm làm gì? `CLAUDE.md` nêu đây là **mục tiêu tương lai** ("xử lý thay đổi theo thời gian"). Em nói trung thực: đã có, chưa có.

### F.7 — "Giả sử không có điểm thi nào cả. Kết quả là gì?"
- Mọi em rơi vào Tầng 2, chỉ còn bốc thăm (`BAN_GIAO.md`: cột điểm phải nhập). Cảnh báo `health_scoring_none` hiện ra?

### F.8 — "Hai CLB cùng buổi, một em chọn cả hai."
- Em chỉ vào được một. Cách thuật toán xử lý? (Các CLB cùng `buoi` là trùng giờ.)

### F.9 — "Em nào đó nói: 'tôi xếp CLB A là nguyện vọng 1 nên phải được vào'." Em trả lời sao?
- Thứ hạng nguyện vọng của học sinh **không** ảnh hưởng ưu tiên của CLB. Vì sao đây là *tính chất*, không phải thiếu sót?

### F.10 — "Một phụ huynh khiếu nại: con tôi giỏi, thi điểm cao mà bị loại."
- Em dùng `rejection_log`, điểm, số bốc thăm (nếu hòa), sức chứa CLB để giải thích. Em có chuẩn bị mẫu trả lời văn bản?

### F.11 — "Tôi sửa `app.db` bằng tay một giá trị rồi mở phần mềm lên. Chuyện gì xảy ra?"
- Ràng buộc CSDL, `soat_vi_pham_rang_buoc`, dấu vân tay "kết quả có thể đã cũ", CSDL bẩn không bị phần mềm đụng tới, bảng sức khỏe chỉ ra.

### F.12 — "Chạy thử trên 5.000 học sinh cho tôi xem."
- `du_lieu_test/thu_tai/` — em chạy được không, thời gian bao lâu, và con số *7,65 s* nghĩa là gì? (Lưu ý: dữ liệu tự sinh.)

---
---

# PHẦN G — BA BẢN CHỐT VÀ KẾ HOẠCH ÔN

## G.1 — Ba bản chốt (thuộc *ý*, không thuộc *chữ*)

Em tự viết bằng lời của mình; chỉ để khung gợi ý.

**G.1.1 — 60 giây giới thiệu dự án.** Phải có theo thứ tự: *vấn đề thật* → *ai chịu thiệt* → *cách làm* → *kết quả có con số* → *giới hạn thành thật*. Không nhắc tên thuật toán trước khi nêu vấn đề.

**G.1.2 — "AI ở đâu trong dự án?"** Một câu trả lời thống nhất, nhất quán với hồ sơ, đủ ba lớp: (a) AI giúp em làm ra sản phẩm (đã ghi nhật ký); (b) sản phẩm cuối là một thuật toán xác định có thể kiểm chứng, không phải hộp đen; (c) vì sao tính kiểm chứng được là điểm mạnh với bài toán công bằng của học sinh.

**G.1.3 — "Khi thật sự không biết".** *"Em chưa kiểm chứng điều này. Điều em biết chắc là…; em sẽ kiểm bằng cách…"* Tuyệt đối không bịa số.

## G.2 — Việc nên làm trước buổi phỏng vấn (xếp theo ưu tiên)

1. **Sửa chú thích mâu thuẫn trong mã** (C1.1, C1.2): docstring `run_rbda` nhắc bản tham chiếu không có trong kho; chú thích `max_rounds` so với số đo thực tế. Đây là việc nhỏ, giảm nguy cơ bị bắt lỗi. *(Theo `CLAUDE.md`, mỗi thay đổi gắn một mã mục trong sổ đăng ký — em hỏi trợ lý trước khi sửa.)*
2. **Chốt cách nói về các con số D.2, D.3, D.5, D.8.** Đây là bốn điểm dễ bị xem là sai sự thật nhất.
3. **Tìm lại số liệu khảo sát (D.15)** — hồ sơ nêu nhưng kho không có kết quả.
4. **Chuẩn bị một trang "kiểm chứng tái lập được"**: danh sách lệnh để chạy lại các số liệu chính (`do_*.py` trong `du_lieu_test/`).
5. **Chuẩn bị câu trả lời cho C3.1–C3.3** (gỡ dấu Zone.Identifier, `loadFromRemoteSources`, script PowerShell) — những thứ bộ quét an ninh dễ cờ đỏ nhất.
6. **Tập demo (Phần F)** trên đúng máy sẽ dùng, ít nhất 3 lần.

## G.3 — Lịch ôn lặp lại (spaced recall)

| Mốc | Làm gì |
|---|---|
| **Hôm nay** | Đọc hết tệp này. Trả lời nhanh Phần A.1, A.2 và D (tự chấm). |
| **+1 ngày** | Làm lại các câu chấm 0–1. Làm Phần B.1 (thuật toán) trên giấy. |
| **+3 ngày** | Làm Phần C (mở mã thật). Tập 3 bản chốt G.1. |
| **+5 ngày** | Làm Phần F (demo) ít nhất hai lần, bấm giờ. |
| **+7 ngày / trước ngày phỏng vấn** | Làm lại các câu còn 0–1, ngủ đủ. Mang theo: hồ sơ, kết quả khảo sát, nhật ký prompt, laptop đã cài sẵn. |

**Kế hoạch dự phòng nếu lỡ lịch:**
- *Mất 1 buổi:* bỏ Phần B.4–B.5, giữ A.1, A.2, D, G.1.
- *Chỉ còn 30 phút:* đọc đúng bảng Phần D, thuộc G.1.1 và G.1.2, tập F.1.

---

## Phụ lục — Nguồn nên mở khi ôn

| Nội dung | Tệp |
|---|---|
| Cơ chế năm lớp, chỗ lệch với báo cáo | `docs/CO_CHE_THUAT_TOAN.md` |
| 7 thí nghiệm TN1–TN7 | `docs/NGHIEN_CUU_TOI_UU.md` |
| Bốc thăm, seed, thứ tự nhập | `docs/GIAI_DAP_BOC_THAM.md` |
| Nhiều buổi | `docs/KE_HOACH_NHIEU_BUOI.md` |
| Bộ số liệu đã kiểm chứng | `du_lieu_test/SO_LIEU_DA_KIEM_CHUNG.md` |
| Lịch sử lỗi, quyết định đã chốt | `BAN_GIAO.md` |
| Rà soát báo cáo (con số gán nhầm, thiếu tham khảo) | `BAO_VE_RA_SOAT_BAO_CAO.md` |
| 27 câu luyện bảo vệ vòng nội bộ | `BAO_VE_BO_CAU_HOI.md` |
| Bối cảnh tổng quát hóa 12 ngành | `docs/ke_hoach/BOI_CANH_DU_AN.md` |

---

*Tệp này do AI soạn dựa trên việc đọc kho mã và hồ sơ dự thi; đây là **bộ câu hỏi**, không chứa nhận định
khoa học hay đáp án. Phần trả lời, diễn giải và kết luận do chính Truong viết và nói bằng lời của mình.
Các con số "đếm thô" (số mã cảnh báo, số khối `except Exception`) lấy bằng `grep` ngày 15/10/2026 — hãy
tự đếm lại trước khi dẫn.*
