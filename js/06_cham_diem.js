/* js/06_cham_diem.js — Thẻ 05 — Chấm điểm mù.

   Một phần của giao diện chính, tách từ app.js cũ. Các tệp js/ là SCRIPT
   THƯỜNG (không phải ES module) nạp theo đúng thứ tự trong index.html và
   dùng chung một phạm vi — như một tệp duy nhất trước đây. Không dùng ES
   module vì mở trang bằng file:// thì trình duyệt chặn chúng.
*/
"use strict";

/* ------------------------------------------------------------------ *
 * 7. TAB 5 — NHẬP ĐIỂM
 * ------------------------------------------------------------------ */

let currentScoringClub = null;

/* Luat diem cua khong gian lam viec dang mo (get_luat_diem). Mac dinh = truong
   hoc: moi CLB mot diem rieng, the nay hien. Nap lai moi lan mo workspace
   (napLuatDiem, goi tu js/075_workspace.js). */
let LUAT_DIEM = { priority: "score", score_scope: "per_slot", tier_mode: "reserve" };

/* Nap luat roi ap len giao dien: chi xep theo nhom (priority "tier") thi KHONG
   co diem nao quyet dinh gi -> an han the Nhap diem; dang o the do thi chuyen
   ve the Van hanh. */
function napLuatDiem() {
  return callApi("get_luat_diem").then((res) => {
    if (res.ok && res.data) LUAT_DIEM = res.data;
    const chiNhom = LUAT_DIEM.priority === "tier";
    const nut = document.querySelector('.nav-item[data-tab="scoring"]');
    if (nut) nut.hidden = chiNhom;
    if (chiNhom && currentTabName() === "scoring") doiThe("pipeline");
  });
}

function loadScoringTab() {
  el("scoringWorkArea").hidden = true;
  currentScoringClub = null;
  const theoNguoi = LUAT_DIEM.score_scope === "per_person";
  el("scoringOverviewPanel").hidden = theoNguoi;
  el("scoringPersonArea").hidden = !theoNguoi;
  if (theoNguoi) loadScoringPersons();
  else loadScoringOverview();
}

/* Diem theo NGUOI: mot o diem cho moi nguoi, thay cho mot o cho moi (nguoi, cho). */
function loadScoringPersons() {
  return callApi("get_person_scoring_list").then((res) => {
    const body = el("scoringPersonBody");
    clear(body);
    if (!res.ok) {
      showErrorToast(res.errors);
      return;
    }
    el("scoringPersonEmpty").hidden = res.data.persons.length > 0;
    res.data.persons.forEach((a) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td>${esc(a.student_id)}</td><td>${esc(a.name)}</td>`;
      const td = document.createElement("td");
      const input = document.createElement("input");
      input.type = "text";           /* xem ghi chu o openScoringClub: khong dung type=number */
      input.inputMode = "decimal";
      input.className = "score-input";
      input.dataset.studentId = a.student_id;
      input.setAttribute("aria-label", a.student_id);
      if (a.score !== null && a.score !== undefined) input.value = a.score;
      td.appendChild(input);
      tr.appendChild(td);
      body.appendChild(tr);
    });
  });
}

function loadScoringOverview() {
  callApi("get_scoring_overview").then((res) => {
    const body = el("scoringOverviewBody");
    const emptyState = el("scoringOverviewEmpty");
    clear(body);
    const withApplicants = res.ok ? res.data.filter((c) => c.n_applicants > 0) : [];
    if (!res.ok || !withApplicants.length) {
      emptyState.hidden = false;
      return;
    }
    emptyState.hidden = true;
    withApplicants.forEach((c) => {
      const pct = c.n_applicants > 0 ? Math.round((c.n_scored / c.n_applicants) * 100) : 0;
      const tr = document.createElement("tr");
      const tdProgress = document.createElement("td");
      tdProgress.innerHTML =
        `<span class="scoring-progress-bar"><span class="scoring-progress-fill" style="width:${pct}%"></span></span>` +
        `${c.n_scored}/${c.n_applicants}`;
      tr.innerHTML = `<td>${esc(c.club_id)}</td><td>${esc(c.name)}</td><td>${esc(c.n_applicants)}</td>`;
      tr.appendChild(tdProgress);
      const tdAction = document.createElement("td");
      const btn = document.createElement("button");
      btn.className = "btn-row-link";
      btn.textContent = t("btn_score_link");
      btn.addEventListener("click", () => openScoringClub(c.club_id));
      tdAction.appendChild(btn);
      tr.appendChild(tdAction);
      body.appendChild(tr);
    });
  });
}

function openScoringClub(clubId) {
  return callApi("get_club_applicants_for_scoring", clubId).then((res) => {
    if (!res.ok) {
      showErrorToast(res.errors);
      return;
    }
    currentScoringClub = clubId;
    el("scoringWorkArea").hidden = false;
    el("scoringClubLabel").textContent = `${res.data.club_name} (${res.data.club_id})`;

    const body = el("scoringTableBody");
    clear(body);
    res.data.applicants.forEach((a) => {
      const tr = document.createElement("tr");
      const tdInput = document.createElement("td");
      const input = document.createElement("input");
      /* KHONG dung type="number". Trinh duyet NUOT mat dau phay va con
         bao la hop le: go "8,5" thi .value tra ve "85" va
         validity.valid === true. Diem bi nhan len 10 lan, im lang. Da
         do trong Chromium that, ca locale en-US lan vi-VN.

         Ma "8,5" la cach viet thap phan BINH THUONG cua tieng Viet —
         khong phai go nham, ma go dung thoi quen rồi máy hiểu sai.
         Backend doc bang _doc_diem() nen nhan ca dau phay lan dau cham. */
      input.type = "text";
      input.inputMode = "decimal";   // may cam ung van hien ban phim so
      input.className = "score-input";
      input.dataset.studentId = a.student_id;
      if (a.score !== null && a.score !== undefined) input.value = a.score;
      tdInput.appendChild(input);
      tr.innerHTML = `<td>${esc(a.student_id)}</td><td>${esc(a.name)}</td>`;
      tr.appendChild(tdInput);
      body.appendChild(tr);
    });
  });
}

function initScoringHandlers() {
  el("btnSavePersonScores").addEventListener("click", () => {
    const inputs = document.querySelectorAll("#scoringPersonBody .score-input");
    inputs.forEach((input) => {
      input.classList.remove("is-invalid");
      input.removeAttribute("title");
      input.removeAttribute("aria-invalid");
    });
    const scores = Array.from(inputs).map((input) => ({
      student_id: input.dataset.studentId,
      score: input.value === "" ? null : input.value,
    }));
    khiBan(el("btnSavePersonScores"), () => callApi("submit_person_scores", scores)).then((res) => {
      if (!res.ok) {
        feedbackErrors(el("scoringPersonFeedback"), res.errors);
        return;
      }
      const boQua = res.data.warnings || [];
      const oTheoHs = new Map(Array.from(inputs, (i) => [i.dataset.studentId, i]));
      boQua.forEach((w) => {
        const sid = w && w.params && w.params.student_id;
        const input = sid === undefined || sid === null ? null : oTheoHs.get(String(sid));
        if (!input) return;
        input.classList.add("is-invalid");
        input.setAttribute("aria-invalid", "true");
        input.title = trErr(w);
      });
      if (boQua.length) {
        const cau = t("feedback_scores_saved_mot_phan", { n: res.data.n_saved, k: boQua.length });
        feedback(el("scoringPersonFeedback"), cau, true);
        showToast(cau + "\n" + trErrs(boQua).join("\n"), "warn");
      } else {
        feedback(el("scoringPersonFeedback"), t("feedback_person_scores_saved", { n: res.data.n_saved }), false);
      }
    });
  });

  el("btnSaveScores").addEventListener("click", () => {
    if (!currentScoringClub) return;
    const inputs = document.querySelectorAll("#scoringTableBody .score-input");
    inputs.forEach((input) => {
      input.classList.remove("is-invalid");
      input.removeAttribute("title");
      input.removeAttribute("aria-invalid");
    });
    const scores = Array.from(inputs).map((input) => ({
      student_id: input.dataset.studentId,
      score: input.value === "" ? null : input.value,
    }));
    khiBan(el("btnSaveScores"), () => callApi("submit_club_scores", currentScoringClub, scores)).then((res) => {
      if (res.ok) {
        const boQua = res.data.warnings || [];
        if (boQua.length) {
          /* O nao bi bo qua thi TO DO dung o do, kem ly do. Truoc day chi
             bao ly do cua o DAU TIEN trong mot thong bao 3,6 giay, con dong
             chu xanh "Da luu" khien nguoi cham tuong da luu het. */
          const oTheoHs = new Map(Array.from(inputs, (i) => [i.dataset.studentId, i]));
          boQua.forEach((w) => {
            const sid = w && w.params && w.params.student_id;
            const input = sid === undefined || sid === null ? null : oTheoHs.get(String(sid));
            if (!input) return;
            input.classList.add("is-invalid");
            input.setAttribute("aria-invalid", "true");
            input.title = trErr(w);
          });
          const cau = t("feedback_scores_saved_mot_phan", { n: res.data.n_saved, k: boQua.length });
          feedback(el("scoringFeedback"), cau, true);
          showToast(cau + "\n" + trErrs(boQua).join("\n"), "warn");
        } else {
          feedback(el("scoringFeedback"), t("feedback_scores_saved", { n: res.data.n_saved }), false);
        }
        loadScoringOverview();
      } else {
        feedbackErrors(el("scoringFeedback"), res.errors);
      }
    });
  });
}
