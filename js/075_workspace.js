/* js/075_workspace.js — Không gian làm việc (workspace): màn chọn, ô đổi ở thanh
   bên và trình tạo 4 bước.

   Một phần của giao diện chính. Các tệp js/ là SCRIPT THƯỜNG (không phải ES
   module), nạp theo thứ tự trong index.html và dùng chung một phạm vi. Tệp này
   nạp SAU 02–07 (dùng donSachTheVanHanh, donSachSauKhiXoaDuLieu, doiThe…) và
   TRƯỚC 08_khoi_dong.js (gọi khoiDongTheoWorkspace từ init()).

   Chế độ: backend có thư mục gốc workspace thì list_workspaces trả ok và ô đổi
   hiện ra; chạy bằng một tệp dữ liệu chỉ định riêng thì nó trả ws_disabled và
   toàn bộ phần này im lặng — giao diện chạy y như trước.

   ĐỔI WORKSPACE KHÔNG TẢI LẠI TRANG. Backend đổi `db_path` rồi giao diện nạp lại
   dữ liệu theo đúng đường mở app: dọn trạng thái mỗi thẻ như sau "Xoá dữ
   liệu" (donSachTheVanHanh + donSachSauKhiXoaDuLieu — hàng chờ nhập, em đang
   mở, CLB đang mở, hạt giống đã khoá...) rồi nạp thẻ đang xem (loadPipelineTab
   cho thanh bên). Thẻ khác tự nạp khi bấm vào (doiThe). Trạng thái cũ không
   được sang workspace mới: một sổ đang chờ nhập mà nằm lại thì sẽ nhập nhầm
   vào workspace khác.
*/
"use strict";

/* ------------------------------------------------------------------ *
 * 10. KHÔNG GIAN LÀM VIỆC
 * ------------------------------------------------------------------ */

const WS_DANH_TU = ["person", "slot", "session", "group", "score"];

const WS = {
  batChoPhep: false,   // backend co thu muc goc workspace
  hienTai: null,       // slug workspace dang mo (null = chua mo cai nao)
  ten: "",             // ten hien thi cua workspace dang mo
  ds: [],              // list_workspaces: items
  mau: [],             // list_templates
  view: "chon",        // "chon" | "ten" | "tao"
  tenMode: null,       // { kieu: "rename"|"duplicate"|"template", slug, ten }
  wiz: null,           // trang thai trinh tao
  buoc: 1,
  dangLam: false,      // chan bam doi khi yeu cau dang bay
  truocKhiMo: null,    // phan tu co focus truoc khi mo hop thoai
};

const WS_VIEW = {
  chon: { id: "wsViewChon", tieuDe: "wsTieuDeChon", viec: "btnWsMoi" },
  ten:  { id: "wsViewTen",  tieuDe: "wsTieuDeTen",  viec: "wsTenMoi" },
  tao:  { id: "wsViewTao",  tieuDe: "wsTieuDeTao",  viec: "wsTen" },
};

function wsMaLoi(res) {
  return res && res.errors && res.errors[0] && res.errors[0].code;
}

function wsNhanNganh(nganh) {
  const khoa = "ws_industry_" + nganh;
  const chu = t(khoa);
  return chu === khoa ? String(nganh) : chu;
}

/* "2026-10-14T09:30:05" -> "2026-10-14 09:30" */
function wsNgayGio(iso) {
  return String(iso || "").replace("T", " ").slice(0, 16);
}

/* ---- Ô đổi ở thanh bên ---- */

function wsCapNhatCongTac() {
  const nut = el("btnWorkspace");
  if (!nut) return;
  nut.hidden = !WS.batChoPhep;
  nut.title = t("ws_switcher_title");
  nut.dataset.slug = WS.hienTai || "";
  el("wsTenHienTai").textContent = WS.hienTai ? WS.ten : t("ws_chua_mo");
}

/* ---- Hộp thoại: mở, đóng, đổi màn, phím tắt ---- */

function wsMoHop(view) {
  const ov = el("wsOverlay");
  if (ov.hidden) WS.truocKhiMo = document.activeElement;
  ov.hidden = false;
  wsDoiView(view);
}

function wsDoiView(view) {
  WS.view = view;
  Object.keys(WS_VIEW).forEach((k) => { el(WS_VIEW[k].id).hidden = k !== view; });
  el("wsHop").setAttribute("aria-labelledby", WS_VIEW[view].tieuDe);
  /* Chua mo workspace nao thi khong co duong thoat: man chon la cua vao. */
  el("btnWsDong").hidden = !WS.hienTai;
  const viec = el(WS_VIEW[view].viec);
  if (viec) {
    viec.focus();
    if (view === "ten" && viec.select) viec.select();
  }
}

/* `ep`: dong ca khi chua mo workspace nao (dung ngay sau khi mo xong). */
function wsDongHop(ep) {
  if (!WS.hienTai && !ep) return false;
  el("wsOverlay").hidden = true;
  const quayLai = WS.truocKhiMo;
  WS.truocKhiMo = null;
  if (quayLai && quayLai.isConnected && quayLai.focus) quayLai.focus();
  return true;
}

function wsPhimTat(ev) {
  const ov = el("wsOverlay");
  if (ov.hidden) return;
  if (ev.key === "Escape") {
    ev.preventDefault();
    if (WS.view === "chon") wsDongHop();
    else wsVeManChon();
    return;
  }
  if (ev.key === "Enter" && WS.view === "tao" &&
      ev.target && ev.target.tagName === "INPUT" && ev.target.type !== "checkbox") {
    ev.preventDefault();
    const tiep = el("btnWsTiep").hidden ? el("btnWsTao") : el("btnWsTiep");
    tiep.click();
    return;
  }
  if (ev.key !== "Tab") return;
  /* Giu Tab trong hop thoai: khong cho focus lot ra man hinh phia sau. */
  const duoc = Array.from(el("wsHop").querySelectorAll(
    "button, input, select, textarea, [tabindex='0']"))
    .filter((n) => !n.disabled && !n.hidden && n.type !== "hidden" && n.offsetParent !== null);
  if (!duoc.length) return;
  const dau = duoc[0];
  const cuoi = duoc[duoc.length - 1];
  if (ev.shiftKey && document.activeElement === dau) {
    ev.preventDefault();
    cuoi.focus();
  } else if (!ev.shiftKey && document.activeElement === cuoi) {
    ev.preventDefault();
    dau.focus();
  }
}

/* ---- Màn chọn ---- */

function wsMoManChon() {
  wsMoHop("chon");
  return wsTaiDanhSach();
}

function wsVeManChon() {
  wsDoiView("chon");
  wsTaiDanhSach();
}

function wsTaiDanhSach() {
  return callApi("list_workspaces").then((res) => {
    const oLoi = el("wsLoiDanhSach");
    if (!res.ok) {
      WS.ds = [];
      oLoi.textContent = t("ws_list_error") + " " + trErrs(res.errors).join(" ");
      wsVeDanhSach();
      return res;
    }
    oLoi.textContent = "";
    WS.ds = res.data.items;
    WS.hienTai = res.data.current;
    const dangMo = WS.ds.find((w) => w.slug === WS.hienTai);
    if (dangMo) WS.ten = dangMo.name;
    wsCapNhatCongTac();
    wsVeDanhSach();
    return res;
  });
}

function wsNutHang(khoa, lop, theo, onClick) {
  const nut = document.createElement("button");
  nut.type = "button";
  nut.className = "btn " + lop + " btn-nho";
  nut.setAttribute("data-i18n", khoa);
  nut.textContent = t(khoa);
  nut.setAttribute("aria-describedby", theo);
  if (onClick) nut.addEventListener("click", onClick);
  return nut;
}

function wsVeDanhSach() {
  const khung = el("wsDanhSach");
  clear(khung);
  el("wsRong").hidden = WS.ds.length > 0;
  WS.ds.forEach((w) => {
    const laHienTai = w.slug === WS.hienTai;
    const hang = document.createElement("div");
    hang.className = "ws-hang" + (laHienTai ? " is-hien-tai" : "");
    hang.setAttribute("role", "listitem");
    hang.dataset.slug = w.slug;

    const thongTin = document.createElement("div");
    thongTin.className = "ws-hang-tt";
    const dong1 = document.createElement("div");
    dong1.className = "ws-hang-ten-dong";
    const ten = document.createElement("span");
    ten.className = "ws-hang-ten";
    ten.id = "wsTenHang-" + w.slug;
    ten.textContent = w.name;
    dong1.appendChild(ten);
    if (laHienTai) {
      const nhan = document.createElement("span");
      nhan.className = "ws-nhan-hien-tai";
      nhan.setAttribute("data-i18n", "ws_badge_current");
      nhan.textContent = t("ws_badge_current");
      dong1.appendChild(nhan);
    }
    const meta = document.createElement("div");
    meta.className = "ws-hang-meta";
    meta.textContent = t("ws_meta", {
      industry: wsNhanNganh(w.industry), modified: wsNgayGio(w.modified),
    });
    thongTin.appendChild(dong1);
    thongTin.appendChild(meta);

    const nutBam = document.createElement("div");
    nutBam.className = "ws-hang-nut";
    const theo = ten.id;
    nutBam.appendChild(wsNutHang("ws_btn_open", "btn-primary", theo, () => wsMo(w.slug)));
    nutBam.appendChild(wsNutHang("ws_btn_rename", "btn-secondary", theo,
      () => wsMoHopTen("rename", w)));
    nutBam.appendChild(wsNutHang("ws_btn_duplicate", "btn-secondary", theo,
      () => wsMoHopTen("duplicate", w)));
    const nutXuat = wsNutHang("ws_btn_export", "btn-secondary", theo, null);
    nutXuat.addEventListener("click", () => wsXuat(w, nutXuat));
    nutBam.appendChild(nutXuat);
    nutBam.appendChild(wsNutHang("ws_btn_template", "btn-secondary", theo,
      () => wsMoHopTen("template", w)));
    const nutXoa = wsNutHang("ws_btn_delete", "btn-danger", theo, null);
    /* Nut xac nhan hai buoc co san (chung.js): bam mot lan chi doi nhan. */
    armTwoStepConfirm(nutXoa, () => t("ws_btn_delete_confirm"), () => wsXoa(w), 4000);
    nutBam.appendChild(nutXoa);

    hang.appendChild(thongTin);
    hang.appendChild(nutBam);
    khung.appendChild(hang);
  });
}

/* ---- Mở / xoá / xuất / nhập ---- */

/* Nap lai du lieu cua MOI the cho workspace vua mo (xem dau tep). */
function wsTaiLaiDuLieu() {
  hsDaChon.clear();
  donSachSauKhiXoaDuLieu();
  donSachTheVanHanh();
  loadPipelineTab();            // o so, canh bao du lieu, thanh ben
  const the = currentTabName();
  if (the !== "pipeline") doiThe(the);
}

function wsMo(slug) {
  if (slug === WS.hienTai) {
    wsDongHop();
    return;
  }
  const lam = () => {
    if (WS.dangLam) return;
    WS.dangLam = true;
    callApi("open_workspace", slug).then((res) => {
      WS.dangLam = false;
      if (!res.ok) {
        showErrorToast(res.errors);
        return;
      }
      WS.hienTai = slug;
      WS.ten = res.data.name;
      wsCapNhatCongTac();
      wsDongHop(true);
      showToast(t("ws_toast_opened", { name: res.data.name }), "success");
      wsTaiLaiDuLieu();
    });
  };
  /* Dang soan do dang o the Nhap tai cho: canh bao truoc, bam lan hai moi di. */
  if (WS.hienTai && typeof roiDiNeuDuoc === "function") roiDiNeuDuoc(lam, "ws:" + slug);
  else lam();
}

function wsXoa(w) {
  if (WS.dangLam) return;
  WS.dangLam = true;
  callApi("delete_workspace", w.slug, "XOA").then((res) => {
    WS.dangLam = false;
    if (!res.ok) {
      showErrorToast(res.errors);
      return;
    }
    showToast(t("ws_toast_deleted", { name: w.name, path: res.data.trash }), "success");
    if (res.data.was_open) {
      WS.hienTai = null;
      WS.ten = "";
      wsCapNhatCongTac();
    }
    wsDoiView("chon");           // cap nhat nut dong (da het workspace dang mo)
    wsTaiDanhSach();
  });
}

function wsXuat(w, nut) {
  khiBan(nut, () => callApi("export_workspace", w.slug)).then((res) => {
    if (!res.ok) {
      showErrorToast(res.errors);
      return;
    }
    showToast(t("ws_toast_exported", { path: res.data.path }), "success");
    callApi("mo_thu_muc", res.data.path);
  });
}

function wsNhapZip(file) {
  if (!file) return;
  const reader = new FileReader();
  reader.onload = () => {
    callApi("import_workspace", bufferSangBase64(reader.result)).then((res) => {
      if (!res.ok) {
        showErrorToast(res.errors);
        return;
      }
      showToast(t("ws_toast_imported", { slug: res.data.slug }), "success");
      wsTaiDanhSach();
    });
  };
  reader.onerror = () => showToast(t("ws_file_read_error"), "error");
  reader.readAsArrayBuffer(file);
}

/* ---- Hộp đặt tên: đổi tên / nhân bản / lưu làm mẫu ---- */

const WS_TIEU_DE_TEN = {
  rename: "ws_rename_title", duplicate: "ws_duplicate_title", template: "ws_template_title",
};
const WS_GOI_Y_TEN = { rename: "", duplicate: "ws_duplicate_hint", template: "ws_template_hint" };

function wsVeChuHopTen() {
  const m = WS.tenMode;
  if (!m) return;
  el("wsTieuDeTen").textContent = t(WS_TIEU_DE_TEN[m.kieu]);
  el("wsGoiYTen").textContent = WS_GOI_Y_TEN[m.kieu] ? t(WS_GOI_Y_TEN[m.kieu]) : "";
}

function wsMoHopTen(kieu, w) {
  WS.tenMode = { kieu, slug: w.slug, ten: w.name };
  el("wsTenMoi").value = kieu === "duplicate" ? w.name + " (2)" : w.name;
  el("wsNhanKemDuLieu").hidden = kieu !== "duplicate";
  el("wsKemDuLieu").checked = true;
  el("wsLoiTen").textContent = "";
  wsVeChuHopTen();
  wsDoiView("ten");
}

function wsLuuTen() {
  const m = WS.tenMode;
  const ten = el("wsTenMoi").value.trim();
  if (!m) return;
  if (!ten) {
    el("wsLoiTen").textContent = t("ws_v_name");
    el("wsTenMoi").focus();
    return;
  }
  const goi = () => {
    if (m.kieu === "rename") return callApi("rename_workspace", m.slug, ten);
    if (m.kieu === "duplicate") {
      return callApi("duplicate_workspace", m.slug, ten, el("wsKemDuLieu").checked);
    }
    return callApi("save_as_template", m.slug, ten);
  };
  khiBan(el("btnWsTenLuu"), goi).then((res) => {
    if (!res.ok) {
      el("wsLoiTen").textContent = trErrs(res.errors).join(" ");
      return;
    }
    const khoa = { rename: "ws_toast_renamed", duplicate: "ws_toast_duplicated",
                   template: "ws_toast_template_saved" }[m.kieu];
    showToast(t(khoa, { name: ten }), "success");
    if (m.kieu === "rename" && m.slug === WS.hienTai) {
      WS.ten = ten;
      wsCapNhatCongTac();
    }
    wsVeManChon();
  });
}

/* ------------------------------------------------------------------ *
 * Trình tạo 4 bước
 * ------------------------------------------------------------------ */

/* Trang thai trinh tao tu mot cau hinh (mau). `en` trung `vi` nghia la o tieng
   Anh da de trong luc luu — hien lai o trong de sua chu Viet van keo theo. */
function wsTrangThaiTuCauHinh(cfg, ten, mauSlug) {
  const nhan = {};
  WS_DANH_TU.forEach((dt) => {
    const c = (cfg.labels && cfg.labels[dt]) || {};
    nhan[dt] = { vi: c.vi || "", en: c.en && c.en !== c.vi ? c.en : "" };
  });
  const r = cfg.rules || {};
  return {
    ten: ten || "",
    nganh: cfg.industry || "school",
    mau: mauSlug,
    nhan,
    luat: {
      max_choices: r.max_choices,
      max_tests: r.max_tests === undefined ? null : r.max_tests,
      priority: r.priority || "score",
      tier_mode: r.tier_mode || "reserve",
      score_scope: r.score_scope || "per_slot",
      tiers: Array.isArray(r.tiers) ? r.tiers.slice() : [],
    },
  };
}

function wsCauHinhTuTrangThai() {
  const w = WS.wiz;
  const labels = {};
  WS_DANH_TU.forEach((dt) => { labels[dt] = { vi: w.nhan[dt].vi, en: w.nhan[dt].en }; });
  return {
    name: w.ten,
    industry: w.nganh,
    labels,
    rules: {
      max_choices: w.luat.max_choices,
      max_tests: w.luat.max_tests,
      priority: w.luat.priority,
      tier_mode: w.luat.tier_mode,
      score_scope: w.luat.score_scope,
      tiers: w.luat.tiers.slice(),
    },
  };
}

function wsBatDauTao() {
  callApi("list_templates").then((res) => {
    if (!res.ok) {
      showErrorToast(res.errors);
      return;
    }
    WS.mau = res.data;
    const goc = WS.mau.find((m) => m.builtin) || WS.mau[0];
    WS.wiz = wsTrangThaiTuCauHinh(goc.config, "", goc.slug);
    WS.buoc = 1;
    el("wsLoiBuoc").textContent = "";
    wsDoiView("tao");
    wsVeBuoc();
  });
}

/* Doc cac o cua buoc `n` vao WS.wiz. Tra ve khoa loi (chuoi) neu `kiem` va o sai. */
function wsDocBuoc(n, kiem) {
  const w = WS.wiz;
  if (n === 1) {
    w.ten = el("wsTen").value.trim();
    w.nganh = el("wsNganh").value;
    if (kiem && !w.ten) return "ws_v_name";
  } else if (n === 2) {
    WS_DANH_TU.forEach((dt) => {
      w.nhan[dt].vi = el("wsNhan-" + dt + "-vi").value.trim();
      w.nhan[dt].en = el("wsNhan-" + dt + "-en").value.trim();
    });
    if (kiem && WS_DANH_TU.some((dt) => !w.nhan[dt].vi)) return "ws_v_vi";
  } else if (n === 3) {
    const l = w.luat;
    const mc = String(el("wsMaxChoices").value).trim();
    const mt = String(el("wsMaxTests").value).trim();
    const khongGioiHan = el("wsKhongGioiHan").checked;
    l.priority = el("wsUuTien").value;
    l.tier_mode = el("wsCheDoNhom").value;
    l.score_scope = el("wsPhamViDiem").value;
    if (/^\d+$/.test(mc)) l.max_choices = Number(mc);
    if (khongGioiHan) l.max_tests = null;
    else if (/^\d+$/.test(mt)) l.max_tests = Number(mt);
    if (l.tier_mode === "strict") {
      l.tiers = el("wsNhom").value.split("\n").map((x) => x.trim()).filter(Boolean);
    }
    if (kiem) {
      if (!/^\d+$/.test(mc) || Number(mc) < 1 || Number(mc) > 20) return "ws_v_choices";
      if (!khongGioiHan && (!/^\d+$/.test(mt) || Number(mt) > 20)) return "ws_v_tests";
      if (new Set(l.tiers).size !== l.tiers.length) return "ws_v_tiers_dup";
    }
  }
  return null;
}

function wsDatTrangThaiOLuat() {
  el("wsMaxTests").disabled = el("wsKhongGioiHan").checked;
  el("wsNhom").disabled = el("wsCheDoNhom").value !== "strict";
}

/* Ve lai noi dung cua buoc hien tai tu WS.wiz. */
function wsVeBuoc() {
  const w = WS.wiz;
  const n = WS.buoc;
  [1, 2, 3, 4].forEach((i) => { el("wsB" + i).hidden = i !== n; });
  document.querySelectorAll("#wsBuoc li").forEach((li) => {
    const i = Number(li.dataset.buoc);
    li.classList.toggle("is-dang-lam", i === n);
    li.classList.toggle("is-xong", i < n);
    if (i === n) li.setAttribute("aria-current", "step");
    else li.removeAttribute("aria-current");
  });
  el("wsBuocNoi").textContent = t("ws_step_of", { n });
  el("btnWsLui").hidden = n === 1;
  el("btnWsTiep").hidden = n === 4;
  el("btnWsTao").hidden = n !== 4;

  if (n === 1) {
    el("wsTen").value = w.ten;
    el("wsNganh").value = w.nganh;
    const ds = el("wsMau");
    clear(ds);
    WS.mau.forEach((m) => {
      const o = document.createElement("option");
      o.value = m.slug;
      o.textContent = m.builtin ? t("ws_template_builtin", { name: m.name }) : m.name;
      ds.appendChild(o);
    });
    ds.value = w.mau;
  } else if (n === 2) {
    wsVeTuVung();
  } else if (n === 3) {
    el("wsMaxChoices").value = w.luat.max_choices;
    el("wsKhongGioiHan").checked = w.luat.max_tests === null;
    el("wsMaxTests").value = w.luat.max_tests === null ? "" : w.luat.max_tests;
    el("wsUuTien").value = w.luat.priority;
    el("wsCheDoNhom").value = w.luat.tier_mode;
    el("wsPhamViDiem").value = w.luat.score_scope;
    el("wsNhom").value = w.luat.tiers.join("\n");
    wsDatTrangThaiOLuat();
  } else {
    wsVeXemLai();
  }
  const dau = { 1: "wsTen", 2: "wsNhan-person-vi", 3: "wsMaxChoices", 4: "btnWsTao" }[n];
  if (el(dau)) el(dau).focus();
}

function wsVeTuVung() {
  const khung = el("wsTuVung");
  clear(khung);
  WS_DANH_TU.forEach((dt) => {
    const hang = document.createElement("div");
    hang.className = "ws-tu-vung-hang";
    const ten = document.createElement("div");
    ten.className = "ws-tu-vung-ten";
    ten.textContent = t("ws_noun_" + dt);
    hang.appendChild(ten);
    ["vi", "en"].forEach((ngon) => {
      const nhan = document.createElement("label");
      nhan.className = "ws-truong ws-nho";
      const chu = document.createElement("span");
      chu.textContent = t("ws_lang_" + ngon);
      const o = document.createElement("input");
      o.type = "text";
      o.className = "text-input";
      o.id = "wsNhan-" + dt + "-" + ngon;
      o.maxLength = 40;
      o.autocomplete = "off";
      o.value = WS.wiz.nhan[dt][ngon];
      o.setAttribute("aria-label", t("ws_noun_" + dt) + ": " + t("ws_lang_" + ngon));
      if (ngon === "en") o.placeholder = t("ws_en_placeholder");
      nhan.appendChild(chu);
      nhan.appendChild(o);
      hang.appendChild(nhan);
    });
    khung.appendChild(hang);
  });
}

function wsDong(khung, nhan, giaTri) {
  const d = document.createElement("div");
  d.className = "ws-xem-lai-dong";
  const a = document.createElement("dt");
  a.textContent = nhan;
  const b = document.createElement("dd");
  b.textContent = giaTri;
  d.appendChild(a);
  d.appendChild(b);
  khung.appendChild(d);
}

function wsVeXemLai() {
  const w = WS.wiz;
  const khung = el("wsXemLai");
  clear(khung);
  const dl = document.createElement("dl");
  wsDong(dl, t("ws_r_name"), w.ten);
  wsDong(dl, t("ws_r_industry"), wsNhanNganh(w.nganh));
  WS_DANH_TU.forEach((dt) => {
    const c = w.nhan[dt];
    wsDong(dl, t("ws_noun_" + dt), c.vi + " / " + (c.en || c.vi));
  });
  const l = w.luat;
  wsDong(dl, t("ws_r_max_choices"), String(l.max_choices));
  wsDong(dl, t("ws_r_max_tests"), l.max_tests === null ? t("ws_review_no_limit") : String(l.max_tests));
  wsDong(dl, t("ws_r_priority"), t({ "score": "ws_opt_priority_score", "tier": "ws_opt_priority_tier",
    "score+tier": "ws_opt_priority_score_tier" }[l.priority]));
  wsDong(dl, t("ws_r_tier_mode"), t(l.tier_mode === "strict" ? "ws_opt_tier_strict" : "ws_opt_tier_reserve"));
  wsDong(dl, t("ws_r_score_scope"), t(l.score_scope === "per_person"
    ? "ws_opt_scope_per_person" : "ws_opt_scope_per_slot"));
  if (l.tier_mode === "strict") {
    wsDong(dl, t("ws_r_tiers"), l.tiers.length ? l.tiers.join(" › ") : t("ws_review_none"));
  }
  khung.appendChild(dl);
}

function wsBuocTiep() {
  const loi = wsDocBuoc(WS.buoc, true);
  el("wsLoiBuoc").textContent = loi ? t(loi) : "";
  if (loi) return;
  WS.buoc += 1;
  wsVeBuoc();
}

function wsBuocLui() {
  wsDocBuoc(WS.buoc, false);
  el("wsLoiBuoc").textContent = "";
  WS.buoc -= 1;
  wsVeBuoc();
}

/* Doi mau o buoc 1: dien lai MOI buoc tu mau, chi giu ten da go. */
function wsDoiMau() {
  const ten = el("wsTen").value.trim();
  const m = WS.mau.find((x) => x.slug === el("wsMau").value);
  if (!m) return;
  WS.wiz = wsTrangThaiTuCauHinh(m.config, ten, m.slug);
  wsVeBuoc();
}

function wsTao() {
  /* Ba buoc dau da duoc doc va kiem khi bam "Tiep"; o buoc 4 cac o cua chung
     dang an, nen lay thang tu WS.wiz, khong doc lai tu DOM. */
  const cfg = wsCauHinhTuTrangThai();
  khiBan(el("btnWsTao"), () => callApi("create_workspace", WS.wiz.ten, cfg)).then((res) => {
    if (!res.ok) {
      el("wsLoiBuoc").textContent = trErrs(res.errors).join(" ");
      return;
    }
    showToast(t("ws_toast_created", { name: WS.wiz.ten }), "success");
    wsDoiView("chon");
    wsTaiDanhSach().then(() => wsMo(res.data.slug));
  });
}

/* ------------------------------------------------------------------ *
 * Khởi động và đổi ngôn ngữ
 * ------------------------------------------------------------------ */

function wsLamLaiTheoNgonNgu() {
  wsCapNhatCongTac();
  if (el("wsOverlay").hidden) return;
  if (WS.view === "chon") wsVeDanhSach();
  else if (WS.view === "ten") wsVeChuHopTen();
  else if (WS.wiz) {
    wsDocBuoc(WS.buoc, false);     // giu chu dang go truoc khi ve lai
    wsVeBuoc();
  }
}

function initWorkspaceHandlers() {
  el("btnWorkspace").addEventListener("click", wsMoManChon);
  el("btnWsDong").addEventListener("click", () => wsDongHop());
  document.querySelectorAll(".ws-ngon-ngu").forEach((nut) => {
    nut.addEventListener("click", () => {
      window.I18N.setLang(window.I18N.getLang() === "vi" ? "en" : "vi");
    });
  });
  el("wsOverlay").addEventListener("mousedown", (ev) => {
    if (ev.target === el("wsOverlay") && WS.view === "chon") wsDongHop();
  });
  el("wsOverlay").addEventListener("keydown", wsPhimTat);

  el("btnWsMoi").addEventListener("click", wsBatDauTao);
  el("btnWsNhap").addEventListener("click", () => el("wsFileZip").click());
  el("wsFileZip").addEventListener("change", () => {
    const f = el("wsFileZip").files && el("wsFileZip").files[0];
    wsNhapZip(f);
    el("wsFileZip").value = "";
  });

  el("wsFormTen").addEventListener("submit", (ev) => {
    ev.preventDefault();
    wsLuuTen();
  });
  el("btnWsTenHuy").addEventListener("click", wsVeManChon);

  el("btnWsHuy").addEventListener("click", wsVeManChon);
  el("btnWsLui").addEventListener("click", wsBuocLui);
  el("btnWsTiep").addEventListener("click", wsBuocTiep);
  el("btnWsTao").addEventListener("click", wsTao);
  el("wsMau").addEventListener("change", wsDoiMau);
  el("wsKhongGioiHan").addEventListener("change", wsDatTrangThaiOLuat);
  el("wsCheDoNhom").addEventListener("change", wsDatTrangThaiOLuat);

  window.addEventListener("langchange", wsLamLaiTheoNgonNgu);
}

/* Goi tu init() (08_khoi_dong.js), thay cho loadPipelineTab() truc tiep.

   Che do workspace + da co workspace dang mo: nap du lieu nhu truoc. Chua mo
   cai nao: hien man chon va CHUA nap gi — moi lenh doc deu cho ra loi khi chua
   co CSDL. Che do CSDL don (hoac khong goi duoc): chay y nhu truoc day. */
function khoiDongTheoWorkspace() {
  callApi("list_workspaces").then((res) => {
    if (!res.ok || !res.data || !Array.isArray(res.data.items)) {
      loadPipelineTab();
      return;
    }
    WS.batChoPhep = true;
    WS.ds = res.data.items;
    WS.hienTai = res.data.current;
    const dangMo = WS.ds.find((w) => w.slug === WS.hienTai);
    WS.ten = dangMo ? dangMo.name : (WS.hienTai || "");
    wsCapNhatCongTac();
    if (WS.hienTai) loadPipelineTab();
    else wsMoManChon();
  });
}
