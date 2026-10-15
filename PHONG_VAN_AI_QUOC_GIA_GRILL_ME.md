# GRILL ME — Câu hỏi phỏng vấn (mức học sinh THPT)

> **Dự án:** Phần mềm sắp xếp học sinh vào câu lạc bộ (CLB) bằng thuật toán Gale–Shapley.
> **Cuộc thi:** Sáng tạo trẻ Quốc gia về Trí tuệ nhân tạo 2026 — Bảng B.
> **Phản hồi đã có:** *"Đề tài phù hợp với môi trường học đường, sử dụng thuật toán phù hợp."*
>
> Tệp này **không có đáp án** — Truong tự trả lời bằng lời của mình.
> Mỗi câu có **gợi ý ý chính** để biết câu trả lời tốt nên chạm tới những ý nào.
> Nếu muốn bản khó hơn (câu hỏi từ AI quét mã, đối chiếu từng con số): xem `PHONG_VAN_AI_QUOC_GIA_NANG_CAO.md`.

**Cách luyện:** nói to thành tiếng, mỗi câu khoảng 1 phút, dùng từ đơn giản như đang giải thích cho bạn cùng lớp. Tự chấm: ✅ trôi chảy · 🔶 còn ấp úng · ❌ chưa biết.

---

## PHẦN 1 — Làm quen (câu mở đầu, gần như chắc chắn được hỏi)

**1. Em hãy giới thiệu dự án trong 1 phút.**
- Ý chính: vấn đề → cách giải quyết → kết quả → hạn chế. Nêu vấn đề *trước*, tên thuật toán *sau*.

**2. Vì sao em chọn đề tài này?**
- Ý chính: một chuyện thật ở trường Việt Úc (xếp CLB theo thứ tự đăng ký, em đam mê nhưng đăng ký muộn thì mất chỗ).

**3. Vấn đề của trường trước đây là gì?**
- Ý chính: dựa vào thứ tự đăng ký; chưa xét nguyện vọng; CLB khó chọn được bạn phù hợp; xử lý tay tốn thời gian.

**4. Ai sẽ dùng phần mềm này? Họ được lợi gì?**
- Ý chính: học sinh (được xếp theo nguyện vọng), CLB (chọn bạn phù hợp, không vượt sức chứa), nhà trường (nhanh, minh bạch).

**5. Phần mềm của em làm được gì? Kể 3 chức năng chính.**
- Gợi ý: nhập dữ liệu từ Excel và kiểm tra lỗi, chạy thuật toán xếp CLB, xuất kết quả và biểu đồ. (Xem thêm Phần 5.)

---

## PHẦN 2 — Về AI (cuộc thi là về AI nên rất hay bị hỏi)

**6. Phần mềm của em dùng AI ở đâu?**
- Ý chính cần nghĩ kỹ: AI giúp em **viết** phần mềm (Claude Code). Bản thân phần mềm chạy bằng **thuật toán** xác định, không phải mô hình học máy. Em nói thẳng điều này, rồi nói vì sao thuật toán là lựa chọn hợp lý (kết quả giải thích và kiểm tra được, công bằng).

**7. Thuật toán Gale–Shapley có phải AI không?**
- Gợi ý: đây là câu dễ bị hỏi. Em nên chuẩn bị 2–3 câu: nó là thuật toán ra quyết định tự động, không học từ dữ liệu; vì sao em vẫn thấy phù hợp với cuộc thi.

**8. Em dùng AI để làm gì trong dự án? Phần nào là em tự làm?**
- Ý chính: trung thực. Mã nguồn có AI tham gia viết; em là người đặt yêu cầu, chọn thuật toán, kiểm tra kết quả, quyết định thiết kế, và viết phần nhận xét kết luận.

**9. Làm sao em biết mã AI viết ra là đúng?**
- Ý chính: em không chỉ tin AI. Có bước kiểm tra riêng: kiểm tra "cặp phá vỡ" (xem câu 17), chạy hàng nghìn test tự động, thử trên nhiều bộ dữ liệu.

**10. AI có từng viết sai không? Em phát hiện thế nào?**
- Gợi ý chọn **một** lỗi em hiểu rõ nhất để kể: ví dụ lỗi học sinh đăng ký muộn luôn bị xếp cuối (số bốc thăm), nên không bao giờ được chỗ. Kể: thấy gì → vì sao sai → sửa thế nào → kết quả sau sửa (từ 0 lên trung bình 3,5 em).

**11. Nếu không có AI thì em có làm được sản phẩm này không?**
- Ý chính: trung thực về mức độ. Em hiểu thuật toán cốt lõi và giải thích được; AI giúp tăng tốc phần lập trình giao diện, kiểm thử.

---

## PHẦN 3 — Thuật toán (nói bằng lời đơn giản)

**12. Thuật toán Gale–Shapley hoạt động thế nào? Cho ví dụ nhỏ.**
- Ý chính: mỗi bạn đề nghị vào CLB mình thích nhất → CLB giữ tạm những bạn tốt nhất trong sức chứa, từ chối bạn còn lại → bạn bị từ chối đề nghị CLB tiếp theo → lặp đến khi không ai cần đổi.
- Luyện: tự làm tay với 4 bạn và 2 CLB trên giấy.

**13. "Chấp nhận trì hoãn" nghĩa là gì?**
- Ý chính: CLB **giữ tạm**, chưa chốt. Nếu sau đó có bạn tốt hơn đề nghị thì CLB đổi người. Chỉ khi hết vòng mới là kết quả cuối.

**14. Vì sao dùng thuật toán này mà không xếp theo thứ tự đăng ký?**
- Ý chính: xếp theo thứ tự đăng ký không xét nguyện vọng và độ phù hợp; Gale–Shapley xét cả hai phía.

**15. CLB chọn học sinh dựa vào tiêu chí gì?**
- Ý chính: hai tầng. Tầng 1: bạn có thi CLB đó → xếp theo điểm. Tầng 2: bạn không thi → xếp theo số bốc thăm. Tầng 1 luôn đứng trước Tầng 2.

**16. Khi hai bạn bằng điểm, ai được chọn?**
- Ý chính: bốc thăm. Mỗi bạn có đúng **một** số bốc thăm dùng chung cho mọi CLB; cùng dữ liệu và cùng hạt giống (seed) thì ra cùng kết quả, nên kiểm tra lại được.

**17. "Cặp phá vỡ" là gì? Vì sao em kiểm tra nó?**
- Ý chính: là một bạn và một CLB cùng muốn bỏ kết quả hiện tại để ghép với nhau. Nếu **không có** cặp phá vỡ thì kết quả "ổn định" — không ai có lý do để xin đổi. Phần mềm kiểm tra tự động sau mỗi lần chạy.

**18. "Suất dự trữ" là gì?**
- Ý chính: CLB có thể dành một số suất cho một nhóm nào đó (do nhà trường quy định). Nếu không đủ bạn thuộc nhóm đó thì suất tự mở cho mọi người — nên gọi là "dự trữ mềm". Không dùng thì đặt bằng 0.

**19. Nếu bạn học sinh khai không thật nguyện vọng thì có lợi không?**
- Ý chính: với cách này thì khai thật là tốt nhất. Em đã thử rất nhiều trường hợp và không thấy trường hợp khai gian nào có lợi (0/1.400). Cách "Boston" (ai chọn trước được trước) thì có khoảng 18,43% trường hợp khai gian có lợi.

**20. Kết quả có phải tốt nhất cho mọi người không?**
- Ý chính: **không** — và hồ sơ đã nói thẳng. Với 140 em, có 32 em có thể cùng được nguyện vọng cao hơn, nhưng đổi như vậy sẽ làm kết quả mất ổn định. Em chọn **ổn định** thay vì tối ưu tuyệt đối. Biết nói điều này là điểm cộng.

**21. Bốc thăm có công bằng không? Ai chứng minh được?**
- Ý chính: bốc thăm làm một lần, khóa lại; có thể chạy lại ra đúng kết quả; không phụ thuộc thứ tự nhập dữ liệu; lịch sử các lần chạy được lưu, không ghi đè.

**22. Bạn đăng ký muộn có bị thiệt không?**
- Ý chính: không còn. Bạn đến muộn được chèn vào dàn số bốc thăm một vị trí **ngẫu nhiên đều**, thứ tự các bạn cũ giữ nguyên. Trước khi sửa, bạn đến muộn luôn bị xếp cuối.

---

## PHẦN 4 — Dữ liệu và kiểm thử

**23. Dữ liệu em dùng từ đâu?**
- Ý chính: ba nguồn như hồ sơ: dữ liệu mô phỏng, khảo sát học sinh (MS Form), mẫu thu nguyện vọng của trường. Nói rõ phần nào là mô phỏng.

**24. Dữ liệu mô phỏng có giống thực tế không?**
- Ý chính: trung thực. Bộ mô phỏng chính được thiết kế **cho cạnh tranh cao** để thuật toán phải làm việc, nên con số "59% được nguyện vọng 1" không đại diện cho phân bố thật của trường.

**25. Em đã thử phần mềm với bao nhiêu học sinh?**
- Ý chính: 120, 140 học sinh (bộ chính), thử tải tới 5.000 học sinh và 100 CLB (dữ liệu tự sinh). Trường thật khoảng 800 học sinh, 20 CLB.

**26. Phần mềm chạy nhanh cỡ nào?**
- Ý chính: 120 học sinh mất khoảng 0,011 giây. Với 5.000 học sinh, 100 CLB: 7,65 giây — đó là thời gian **bước xếp**, không phải cả quy trình nhập dữ liệu và xuất kết quả.

**27. Em kiểm thử bằng cách nào?**
- Ý chính: test tự động (pytest, Playwright cho giao diện); bộ dữ liệu cố tình có lỗi; kiểm tra "cặp phá vỡ"; so sánh kết quả trước/sau khi sửa. (Con số test: kiểm tra lại ở phần "Trước ngày phỏng vấn".)

**28. Dữ liệu sai thì phần mềm xử lý thế nào?**
- Ý chính: dòng sai được tách riêng kèm cảnh báo (nêu rõ dòng nào, cột nào), các dòng đúng vẫn xử lý. Có bước kiểm "sức khỏe dữ liệu" trước khi chạy (ví dụ: thiếu điểm, Excel làm mất số 0 đầu mã học sinh).

**29. Nếu máy tắt đột ngột khi đang chạy thì sao?**
- Ý chính: dữ liệu được sao lưu trước khi chạy (giữ 10 bản); toàn bộ lần chạy là một giao dịch — lỗi thì hủy hết, không để kết quả dở dang.

**30. Có người dùng thật thử chưa?**
- Ý chính: **trung thực.** Hiện chủ yếu em tự chạy thử trên máy Windows. Nên (nếu kịp) nhờ một thầy cô chạy thử và ghi nhận xét. Nói rõ dữ liệu vận hành thật là hướng phát triển.

---

## PHẦN 5 — Sản phẩm và điểm đặc biệt (nên chủ động nói)

**31. Phần mềm này có gì khác biệt hoặc đặc biệt?**
Chọn 4–5 ý em tự tin nhất:
- Chạy **offline hoàn toàn**, một tệp `.exe`, không cần đăng nhập.
- Nhập dữ liệu bằng **một tệp Excel** (Sổ nhập CLB), tự nhận diện loại tệp.
- **Kiểm tra sức khỏe dữ liệu** trước khi chạy — bắt các lỗi âm thầm làm sai kết quả.
- **Chấm điểm mù:** người chấm không thấy số bốc thăm hay nguyện vọng của bạn.
- **Kiểm tra tính ổn định** tự động sau mỗi lần chạy.
- **Bốc thăm tái lập được**, khóa lại, có lịch sử mỗi lần chạy.
- Xử lý **bạn đến muộn** công bằng.
- Hỗ trợ **nhiều buổi** trong tuần.
- **Sao lưu tự động**, có màn hình phục hồi khi dữ liệu hỏng.
- Có biểu đồ kết quả, so sánh với lần chạy trước, xuất file cho từng CLB và từng học sinh.
- Giao diện **song ngữ Việt/Anh**; tìm kiếm tên tiếng Việt có dấu hoặc không dấu.

**32. Giới hạn hiện tại của phần mềm?**
- Ý chính (tự nêu trong hồ sơ): tối đa 10 nguyện vọng, 5 CLB thi mỗi buổi; chưa tối ưu Pareto; bốc thăm làm 1,1% học sinh đổi kết cục; chưa có chữ ký số nên Windows cảnh báo; dữ liệu mới là mô phỏng.

**33. Vì sao giới hạn 10 nguyện vọng và 5 CLB thi?**
- Ý chính: 10 là giới hạn câu hỏi xếp hạng của Microsoft Forms; 5 là quy định của nhà trường (chấm thi nhiều hơn thì không xuể).

**34. Hướng phát triển tiếp theo?**
- Ý chính: chạy thử một đợt thực tế để lấy số liệu; màn hình giải thích kết quả cho từng học sinh; cho nhà trường tự đặt trần nguyện vọng; mở rộng sang xếp lớp tự chọn hoặc phân công.

---

## PHẦN 6 — Đạo đức, an toàn dữ liệu, làm việc nhóm

**35. Dữ liệu học sinh được bảo vệ thế nào?**
- Ý chính: chạy offline, dữ liệu nằm trên máy của nhà trường, không gửi lên mạng. Thành thật: hiện chưa có mật khẩu — hướng cải thiện là thêm khóa mở ứng dụng và xóa dữ liệu sau khi dùng.

**36. Dữ liệu của nhà trường em dùng đã được cho phép chưa?**
- Ý chính: nói rõ dữ liệu nào được cung cấp, đã ẩn danh chưa. (Em chuẩn bị câu trả lời đúng sự thật.)

**37. Một bạn không được vào CLB mình thích thì phần mềm giải thích thế nào?**
- Ý chính: ghi lại bạn bị từ chối ở vòng nào, vì CLB đã đủ chỗ và có bạn xếp trên (điểm hoặc bốc thăm). Màn hình giải trình chi tiết cho từng bạn là hướng phát triển.

**38. Suất dự trữ có thiên vị không?**
- Ý chính: phần mềm là công cụ; nhà trường quyết định chính sách ưu tiên nhóm nào. Dữ liệu mô phỏng chỉ để thử cơ chế, không nhận xét về nhóm học sinh thật nào.

**39. Ai làm gì trong đội? Em đóng góp phần nào?**
- Ý chính: nói cụ thể từng người. Em chuẩn bị 2–3 câu về phần của chính em.

**40. Khó khăn lớn nhất em gặp khi làm?**
- Gợi ý chọn một: ứng dụng không mở được trên Windows (lỗi cửa sổ bị treo), hoặc lỗi công bằng với bạn đăng ký muộn, hoặc dữ liệu Excel bị mất số 0 đầu.

**41. Em học được gì từ dự án?**
- Câu mở, trả lời bằng trải nghiệm thật: thuật toán, cách làm việc với AI có kiểm tra, cách nói thật về giới hạn.

---

## PHẦN 7 — Demo (nếu được yêu cầu "chạy cho tôi xem")

Tập đến khi làm trôi trong 3 phút:
1. Mở phần mềm → nạp Sổ nhập Excel.
2. Cho xem bảng cảnh báo / kiểm tra sức khỏe dữ liệu.
3. Bấm chạy → mở thẻ **Kết quả**: số em được xếp, % nguyện vọng 1, biểu đồ lấp đầy CLB.
4. Xuất kết quả → mở thư mục chứa tệp.
5. (Nếu hỏi) nạp tệp có lỗi cố ý để chứng minh phần mềm bắt lỗi.

Chuẩn bị luôn: nếu cửa sổ không mở được thì làm gì? (chế độ dự phòng mở bằng trình duyệt.)

---

## Ba câu cần thuộc ý

1. **Giới thiệu 1 phút:** vấn đề thật → thuật toán → kết quả có con số → hạn chế trung thực.
2. **"AI ở đâu?":** AI giúp em làm ra sản phẩm và em kiểm tra lại kỹ; sản phẩm là thuật toán minh bạch, kiểm chứng được — phù hợp với bài toán cần công bằng cho học sinh.
3. **Khi không biết:** *"Em chưa kiểm tra điều này. Điều em chắc chắn là…, và em sẽ kiểm tra bằng cách…"* — không bịa số liệu.

---

## Trước ngày phỏng vấn — kiểm tra lại 4 con số trong hồ sơ

Đây là những chỗ dễ bị hỏi lại và dễ nói nhầm:

| Con số | Điều cần nhớ đúng |
|---|---|
| **18,4% → 0%** (khai gian) | 18,4% là của cơ chế **Boston**, còn thuật toán của em là 0%. Đừng nói đó là "trước và sau khi em sửa lỗi". Lỗi em sửa là chuyện bạn đến muộn (0 → 3,5 em). |
| **663 lượt kiểm thử** | Kho mã hiện ghi 1.515 ca test (10/10/2026). Nhớ 663 là con số tính ở thời điểm nào và đo cái gì. |
| **7,65 giây** (5.000 em) | Chỉ là thời gian bước xếp, không phải cả quy trình. |
| **"Người dùng thực tế xác nhận"** | Hiện người xác nhận chủ yếu là em. Nếu có thể, nhờ một thầy cô chạy thử và ghi nhận xét. |

Thêm hai việc nên làm: mang theo **kết quả khảo sát** (bao nhiêu bạn trả lời, kết quả chính) và **nhật ký prompt** (mục 9 hồ sơ).

---

## Lịch ôn

| Mốc | Làm gì |
|---|---|
| Hôm nay | Đọc hết, tự chấm ✅🔶❌ |
| +1 ngày | Làm lại các câu 🔶❌; làm tay ví dụ thuật toán (câu 12) |
| +3 ngày | Tập 3 câu cần thuộc ý + Phần 2 (AI) |
| +5 ngày | Tập demo (Phần 7) hai lần |
| Trước ngày phỏng vấn | Xem lại bảng 4 con số; ngủ đủ |

*Nếu chỉ còn 30 phút:* câu 1, 6, 7, 12, 17, 20, 30 và bảng 4 con số.

---

*Tệp do AI soạn dựa trên hồ sơ và kho mã. Đây là bộ câu hỏi và gợi ý ý chính; phần trả lời và nhận xét do Truong tự viết và nói bằng lời của mình.*
