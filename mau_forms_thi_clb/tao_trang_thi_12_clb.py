# -*- coding: utf-8 -*-
"""Sinh docs/thi_12_clb/index.html: trang thi 12 CLB mỗi buổi, một tệp HTML tự chứa.

Học sinh xếp Top 1–10 mỗi buổi, tick CLB muốn thi (tối đa 5 mỗi buổi, có thể 0 đến 5), rồi chỉ
làm đề của những CLB đã chọn. Khi nộp, học sinh chỉ thấy "đã nộp" và tải được tệp phiếu (.json).
Giáo viên nạp nhiều tệp phiếu, trang chấm bằng logic của chamTheoCLB và tải sổ học sinh (CSV).

Logic chấm lấy từ khối LOGIC của tao_website_mau (đã kiểm đối chiếu với TAO_GOOGLE_FORM.gs).
Dữ liệu 60 CLB lấy từ de_thi_12_clb.du_lieu(). Không sửa tay tệp HTML: sửa nguồn rồi chạy:

    python mau_forms_thi_clb/tao_trang_thi_12_clb.py
"""

import json
import os
import sys

THU_MUC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THU_MUC)
import de_thi_12_clb  # noqa: E402  (60 CLB: 50 của bộ mẫu và 10 nháp)
import tao_website_mau as tw  # noqa: E402  (khối LOGIC chấm, đã đối chiếu với .gs)

RA = os.path.normpath(os.path.join(THU_MUC, os.pardir, "docs", "thi_12_clb", "index.html"))

# Chữ trợ giúp dùng đúng các câu của biểu mẫu Google (xem CAU_TRO_GIUP_CO_NGUON). Riêng trang này
# có thêm một câu về trần Top 1–10 vì chỉ có 10 ô xếp; không có trong biểu mẫu.
TRO_GIUP = {
    "top": ("Top 1 là CLB em thích nhất. Bấm vào từng Top để chọn CLB trong danh sách. "
            "Mỗi CLB chỉ chọn một lần. Không muốn thêm thì để (Bỏ trống). "
            "Muốn CLB được chấm điểm: xếp CLB đó ở một Top, tick ở ô bên dưới, rồi làm bài thi. "
            "Trang này chỉ có Top 1 đến Top 10."),
    "tick": ("Không thi CLB nào thì bỏ trống. CLB được chấm điểm khi vừa được xếp ở một Top, "
             "vừa được tick ở đây, và vừa được làm bài."),
    "first": ("Chọn CLB đứng trên cùng (đứng đầu trong danh sách) trong số các CLB em đã tick. "
              "Không thi CLB nào thì chọn \"Em không thi CLB nào buổi này\". "
              "Làm xong thì chỉ chọn được CLB đứng sau."),
    "tiep": ("Chỉ hiện các CLB đứng sau CLB vừa làm. "
             "Chọn CLB em đã tick tiếp theo; hết rồi thì chọn Không thi thêm."),
}

# Các câu phải có nguyên văn trong biểu mẫu Google (test kiểm trong tao_google_forms.noi_dung()).
CAU_TRO_GIUP_CO_NGUON = [
    "Top 1 là CLB em thích nhất.",
    "Bấm vào từng Top để chọn CLB trong danh sách.",
    "Mỗi CLB chỉ chọn một lần.",
    "Muốn CLB được chấm điểm: xếp CLB đó ở một Top, tick ở ô bên dưới, rồi làm bài thi.",
    "Không thi CLB nào thì bỏ trống.",
    "CLB được chấm điểm khi vừa được xếp ở một Top, vừa được tick ở đây, và vừa được làm bài.",
    "Chọn CLB đứng trên cùng (đứng đầu trong danh sách) trong số các CLB em đã tick.",
    "Làm xong thì chỉ chọn được CLB đứng sau.",
    "Chỉ hiện các CLB đứng sau CLB vừa làm.",
    "Chọn CLB em đã tick tiếp theo; hết rồi thì chọn Không thi thêm.",
]

KHUON = r"""<!doctype html>
<html lang="vi">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Thi tuyển CLB: 12 câu lạc bộ mỗi buổi</title>
<style>__CSS__</style>
</head>
<body>
<main>
<header class="hero">
  <span class="badge">Bản thử · dữ liệu mô phỏng</span>
  <h1>Thi tuyển CLB: 12 câu lạc bộ mỗi buổi</h1>
  <p>Em xếp các CLB muốn vào (Top 1 đến Top 10 mỗi buổi), tick những CLB muốn thi (tối đa 5 mỗi buổi, có thể thi 0 đến 5 CLB), rồi chỉ làm đề của những CLB em đã chọn. Sau khi nộp, em sẽ không thấy điểm; giáo viên sẽ chấm.</p>
  <nav class="top"><a href="#thi">Làm bài</a><a href="#gv">Giáo viên</a></nav>
</header>

<section id="thi" class="card">
  <h2>Làm bài</h2>
  <div id="form"></div>
</section>

<section id="gv" class="card">
  <h2>Giáo viên: nạp phiếu và tải sổ học sinh</h2>
  <p class="muted">Chọn các tệp phiếu (.json) học sinh đã gửi. Trang chấm lại theo đáp án và hiện bảng. Hai tệp CSV dùng để dán vào hai trang "1. CLB" và "2. Học sinh" của SO_NHAP_CLB.xlsx; chưa kiểm được nạp thẳng vào phần mềm. Cột chỉ tiêu, suất ưu tiên và nhóm ưu tiên của trang "1. CLB" phải điền tay.</p>
  <input type="file" id="gv-tep" accept=".json,application/json" multiple>
  <p id="gv-so" class="muted"></p>
  <h3>Chỉ tiêu mỗi CLB (bắt buộc trước khi tải sổ nhập)</h3>
  <p class="help">Số nguyên dương. Kiosk không nhận sổ khi chỉ tiêu trống hoặc sai.</p>
  <div id="gv-chi-tieu"></div>
  <div class="toolbar">
    <button class="btn" id="gv-tai-xlsx">Tải sổ nhập (.xlsx)</button>
    <button class="btn ghost" id="gv-tai-clb">Tải trang "1. CLB" (CSV)</button>
    <button class="btn ghost" id="gv-tai-so">Tải trang "2. Học sinh" (CSV)</button>
    <button class="btn ghost" id="gv-tai-canh">Tải cảnh báo (CSV)</button>
    <button class="btn ghost" id="gv-xoa">Xoá danh sách đã nạp</button>
  </div>
  <div id="gv-ket-qua" class="tablewrap"></div>
  <h3>Cảnh báo</h3>
  <div id="gv-canh" class="tablewrap"></div>
</section>

<footer>Trang này do <code>mau_forms_thi_clb/tao_trang_thi_12_clb.py</code> sinh ra từ dữ liệu trong <code>de_thi_12_clb.py</code>. Đề của 10 CLB mới là bản nháp, chờ giáo viên duyệt. Không sửa tay.</footer>
</main>
<script>
/*LOGIC-BEGIN*/
__LOGIC__
/*LOGIC-END*/
const TRO_GIUP = __TRO_GIUP__;

/*XLSX-BEGIN*/
// Bộ ghi .xlsx tối thiểu, không thư viện: gói ZIP không nén, mỗi trang là một sheet với ô chữ inlineStr.
// danhSach: [{ten, dong: [[ô, ô, ...], ...]}]. Ô rỗng hoặc null thì bỏ; số thì ghi thành số.
function dungXlsx(danhSach){
  const enc = new TextEncoder();
  const bang = new Uint32Array(256);
  for(let n = 0; n < 256; n++){
    let c = n;
    for(let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1;
    bang[n] = c >>> 0;
  }
  function crc(b){
    let c = 0xFFFFFFFF;
    for(let i = 0; i < b.length; i++) c = bang[(c ^ b[i]) & 0xFF] ^ (c >>> 8);
    return (c ^ 0xFFFFFFFF) >>> 0;
  }
  function xml(s){
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&apos;');
  }
  function cot(n){
    let s = '';
    n++;
    while(n > 0){ const r = (n - 1) % 26; s = String.fromCharCode(65 + r) + s; n = Math.floor((n - 1) / 26); }
    return s;
  }
  const KHAI = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n';
  function trang(dong){
    let x = KHAI + '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>';
    dong.forEach(function(r, i){
      x += '<row r="' + (i + 1) + '">';
      r.forEach(function(v, j){
        if(v === '' || v === null || v === undefined) return;
        const ref = cot(j) + (i + 1);
        if(typeof v === 'number') x += '<c r="' + ref + '"><v>' + v + '</v></c>';
        else x += '<c r="' + ref + '" t="inlineStr"><is><t xml:space="preserve">' + xml(v) + '</t></is></c>';
      });
      x += '</row>';
    });
    return x + '</sheetData></worksheet>';
  }
  const tep = [];
  tep.push(['[Content_Types].xml', KHAI + '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">' +
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>' +
    '<Default Extension="xml" ContentType="application/xml"/>' +
    '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>' +
    danhSach.map(function(s, i){ return '<Override PartName="/xl/worksheets/sheet' + (i + 1) +
      '.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'; }).join('') +
    '</Types>']);
  tep.push(['_rels/.rels', KHAI + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' +
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>' +
    '</Relationships>']);
  tep.push(['xl/workbook.xml', KHAI + '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" ' +
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>' +
    danhSach.map(function(s, i){ return '<sheet name="' + xml(s.ten) + '" sheetId="' + (i + 1) + '" r:id="rId' + (i + 1) + '"/>'; }).join('') +
    '</sheets></workbook>']);
  tep.push(['xl/_rels/workbook.xml.rels', KHAI + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' +
    danhSach.map(function(s, i){ return '<Relationship Id="rId' + (i + 1) + '" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet' + (i + 1) + '.xml"/>'; }).join('') +
    '</Relationships>']);
  danhSach.forEach(function(s, i){ tep.push(['xl/worksheets/sheet' + (i + 1) + '.xml', trang(s.dong)]); });

  const phan = [], dau = [];
  let pos = 0;
  tep.forEach(function(mucTep){
    const tenB = enc.encode(mucTep[0]), dl = enc.encode(mucTep[1]), c = crc(dl);
    const h = new DataView(new ArrayBuffer(30));
    h.setUint32(0, 0x04034b50, true); h.setUint16(4, 20, true); h.setUint16(6, 0x0800, true);
    h.setUint16(8, 0, true); h.setUint16(10, 0, true); h.setUint16(12, 0x21, true);
    h.setUint32(14, c, true); h.setUint32(18, dl.length, true); h.setUint32(22, dl.length, true);
    h.setUint16(26, tenB.length, true); h.setUint16(28, 0, true);
    phan.push(new Uint8Array(h.buffer), tenB, dl);
    const cd = new DataView(new ArrayBuffer(46));
    cd.setUint32(0, 0x02014b50, true); cd.setUint16(4, 20, true); cd.setUint16(6, 20, true);
    cd.setUint16(8, 0x0800, true); cd.setUint16(10, 0, true); cd.setUint16(12, 0, true);
    cd.setUint16(14, 0x21, true); cd.setUint32(16, c, true); cd.setUint32(20, dl.length, true);
    cd.setUint32(24, dl.length, true); cd.setUint16(28, tenB.length, true);
    cd.setUint16(30, 0, true); cd.setUint16(32, 0, true); cd.setUint16(34, 0, true);
    cd.setUint16(36, 0, true); cd.setUint32(38, 0, true); cd.setUint32(42, pos, true);
    dau.push(new Uint8Array(cd.buffer), tenB);
    pos += 30 + tenB.length + dl.length;
  });
  const cdDai = dau.reduce(function(n, b){ return n + b.length; }, 0);
  const kt = new DataView(new ArrayBuffer(22));
  kt.setUint32(0, 0x06054b50, true); kt.setUint16(8, tep.length, true); kt.setUint16(10, tep.length, true);
  kt.setUint32(12, cdDai, true); kt.setUint32(16, pos, true);
  const tong = new Uint8Array(pos + cdDai + 22);
  let p = 0;
  phan.concat(dau).forEach(function(b){ tong.set(b, p); p += b.length; });
  tong.set(new Uint8Array(kt.buffer), p);
  return tong;
}
/*XLSX-END*/

(function(){
  'use strict';
  function $(s){ return document.querySelector(s); }
  function esc(s){
    return String(s == null ? '' : s).replace(/[&<>"']/g, function(c){
      return {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[c];
    });
  }

  // Trang theo thứ tự: mỗi buổi là trang buổi, trang xếp Top và tick, trang CLB thi đầu tiên,
  // rồi trang đề và trang "tiếp theo" cho từng CLB. Chỉ trang hiện tại được dựng.
  const TRANG = [{loai: 'info'}];
  const NGAY = [];
  BUOI.forEach(function(d, k){
    const coThi = d.clubs.filter(function(c){ return c.de.length; });
    const ng = {d: d, k: k, coThi: coThi, iDi: 0, iTop: 0, iFirst: -1, iExam: [], iTiep: []};
    ng.iDi = TRANG.push({loai: 'di', k: k}) - 1;
    ng.iTop = TRANG.push({loai: 'top', k: k}) - 1;
    if(coThi.length){
      ng.iFirst = TRANG.push({loai: 'first', k: k}) - 1;
      coThi.forEach(function(c, i){
        ng.iExam.push(TRANG.push({loai: 'exam', k: k, i: i}) - 1);
        ng.iTiep.push(i + 1 < coThi.length ? TRANG.push({loai: 'tiep', k: k, i: i}) - 1 : -1);
      });
    }
    NGAY.push(ng);
  });
  TRANG.push({loai: 'nop'});
  const IDX_NOP = TRANG.length - 1;
  function tiepNgay(k){ return k + 1 < NGAY.length ? NGAY[k + 1].iDi : IDX_NOP; }

  function moi(thongBao){ return {cur: 0, path: [0], ans: {}, loi: '', thongBao: thongBao || ''}; }
  let st = moi();
  let DA_NOP = null;
  const GV = [];      // phiếu đã nạp, kèm thời điểm nộp
  const DA_NAP = {};  // nội dung tệp đã nạp, để bỏ bản sao
  // Chấm theo thời điểm nộp, không theo thứ tự chọn tệp: "giữ phiếu đầu" là bản nộp sớm nhất.
  function phieuTheoNopLuc(){
    return GV.slice().sort(function(a, b){
      const x = a.nop_luc || '￿', y = b.nop_luc || '￿';
      return x < y ? -1 : (x > y ? 1 : 0);
    }).map(function(w){ return w.phieu; });
  }

  // CLB đã tick trong buổi (theo thứ tự buổi). Chỉ các CLB này được chọn để làm bài.
  function daTick(ng){
    const dang = st.ans['chon-' + ng.d.ma] || [];
    return ng.coThi.filter(function(c){ return dang.indexOf(nhan(c)) >= 0; });
  }
  // Các nhãn CLB đã xếp trong Top 1–10 của buổi.
  function xepTop(ng){
    const ds = [];
    for(let k = 1; k <= 10; k++){
      const v = st.ans[ng.d.ma + '-top-' + k];
      if(v && v !== BO_TRONG) ds.push(v);
    }
    return ds;
  }
  // Trang chọn đầu: chỉ các CLB đã tick. Trang "tiếp theo" sau CLB ở vị trí i: chỉ CLB đã tick đứng sau.
  function luaChonDau(ng){
    return daTick(ng).map(nhan).concat([KHONG_THI]);
  }
  function luaChonTiep(ng, i){
    return daTick(ng).filter(function(c){ return ng.coThi.indexOf(c) > i; }).map(nhan).concat([DUNG]);
  }
  // Bỏ câu trả lời không còn hợp lệ (ví dụ vừa bỏ tick CLB đó).
  function donDep(key, ops){
    if(st.ans[key] !== undefined && ops.indexOf(st.ans[key]) < 0) delete st.ans[key];
  }

  // Trang kế tiếp khi bấm Tiếp, theo câu trả lời hiện có (-1 nếu chưa hợp lệ).
  function sang(idx){
    const p = TRANG[idx], a = st.ans;
    if(p.loai === 'info') return NGAY[0].iDi;
    const ng = NGAY[p.k], ma = ng.d.ma;
    if(p.loai === 'di') return a['di-' + ma] === CO_BUOI ? ng.iTop : tiepNgay(p.k);
    if(p.loai === 'top') return ng.coThi.length ? ng.iFirst : tiepNgay(p.k);
    if(p.loai === 'first'){
      const v = a['thi-' + ma];
      if(v === KHONG_THI) return tiepNgay(p.k);
      const c = daTick(ng).find(function(x){ return nhan(x) === v; });
      return c ? ng.iExam[ng.coThi.indexOf(c)] : -1;
    }
    if(p.loai === 'exam') return ng.iTiep[p.i] >= 0 ? ng.iTiep[p.i] : tiepNgay(p.k);
    if(p.loai === 'tiep'){
      const v = a['thi-sau-' + ng.coThi[p.i].id];
      if(v === DUNG) return tiepNgay(p.k);
      const c = daTick(ng).find(function(x){ return nhan(x) === v && ng.coThi.indexOf(x) > p.i; });
      return c ? ng.iExam[ng.coThi.indexOf(c)] : -1;
    }
    return -1;
  }

  function thieu(idx){
    const p = TRANG[idx], a = st.ans;
    if(p.loai === 'info'){
      if(!String(a.student_id || '').trim()) return 'Em cần ghi mã học sinh.';
      if(!String(a.name || '').trim()) return 'Em cần ghi họ và tên.';
      return '';
    }
    if(p.loai === 'di') return a['di-' + NGAY[p.k].d.ma] ? '' : 'Em cần chọn có hoặc không.';
    if(p.loai === 'first') return a['thi-' + NGAY[p.k].d.ma] ? '' : 'Em cần chọn một CLB, hoặc chọn Không thi.';
    if(p.loai === 'exam'){
      const c = NGAY[p.k].coThi[p.i];
      for(let j = 0; j < c.de.length; j++){
        if(!a[c.id + '-' + (j + 1)]) return 'Em cần trả lời đủ các câu của đề.';
      }
      return '';
    }
    if(p.loai === 'tiep') return a['thi-sau-' + NGAY[p.k].coThi[p.i].id] ? '' : 'Em cần chọn một lựa chọn.';
    return '';
  }

  // Khoá câu trả lời của một trang: chỉ những trang đã đi qua mới được gửi.
  function keysOf(idx){
    const p = TRANG[idx];
    if(p.loai === 'info') return ['student_id', 'name'];
    if(p.loai === 'nop') return [];
    const ng = NGAY[p.k], ma = ng.d.ma;
    if(p.loai === 'di') return ['di-' + ma];
    if(p.loai === 'top'){
      const ks = [];
      for(let k = 1; k <= 10; k++) ks.push(ma + '-top-' + k);
      ks.push('chon-' + ma);
      return ks;
    }
    if(p.loai === 'first') return ['thi-' + ma];
    if(p.loai === 'exam'){
      const c = ng.coThi[p.i];
      return c.de.map(function(_, j){ return c.id + '-' + (j + 1); });
    }
    if(p.loai === 'tiep') return ['thi-sau-' + ng.coThi[p.i].id];
    return [];
  }

  function head(t, sub){ return '<h3>' + esc(t) + '</h3>' + (sub ? '<p class="help">' + esc(sub) + '</p>' : ''); }

  function radios(key, legend, opts){
    let h = '<fieldset class="q"><legend>' + esc(legend) + '</legend>';
    opts.forEach(function(o){
      h += '<label class="opt"><input type="radio" name="' + esc(key) + '" data-key="' + esc(key) + '" value="' + esc(o) + '"' +
        (st.ans[key] === o ? ' checked' : '') + '><span>' + esc(o) + '</span></label>';
    });
    return h + '</fieldset>';
  }

  function oText(key, legend, placeholder){
    return '<fieldset class="q"><legend>' + esc(legend) + '</legend><input type="text" data-key="' + esc(key) +
      '" value="' + esc(st.ans[key] || '') + '" placeholder="' + esc(placeholder) + '" autocomplete="off"></fieldset>';
  }

  function tomTat(){
    const dong = [];
    st.path.forEach(function(idx){
      const p = TRANG[idx];
      if(p.loai === 'nop') return;
      if(p.loai === 'info'){
        dong.push(['Thí sinh', (st.ans.name || '') + ' (' + (st.ans.student_id || '') + ')']);
        return;
      }
      const ng = NGAY[p.k];
      if(p.loai === 'di'){
        dong.push([ng.d.ten, st.ans['di-' + ng.d.ma] === CO_BUOI ? 'Có sinh hoạt' : 'Bận buổi này']);
      } else if(p.loai === 'top'){
        const tops = xepTop(ng);
        dong.push([ng.d.ten + ': xếp Top', tops.length ? tops.join('; ') : 'Không xếp CLB nào']);
        const chon = st.ans['chon-' + ng.d.ma] || [];
        dong.push([ng.d.ten + ': CLB muốn thi', chon.length ? chon.join('; ') : 'Không thi CLB nào']);
      } else if(p.loai === 'exam'){
        const c = ng.coThi[p.i];
        const da = c.de.filter(function(_, j){ return st.ans[c.id + '-' + (j + 1)]; }).length;
        dong.push(['Đề ' + c.name, 'Đã trả lời ' + da + '/' + c.de.length + ' câu']);
      } else if(p.loai === 'first'){
        dong.push([ng.d.ten + ': làm bài trước', st.ans['thi-' + ng.d.ma] || '']);
      } else if(p.loai === 'tiep'){
        dong.push([ng.d.ten + ': làm tiếp theo', st.ans['thi-sau-' + ng.coThi[p.i].id] || '']);
      }
    });
    return bang(['Mục', 'Lựa chọn'], dong);
  }

  function noiDung(p){
    if(p.loai === 'info') return head('Thông tin thí sinh', 'Ghi đúng mã trên thẻ học sinh.') +
      oText('student_id', 'Mã học sinh', 'Ví dụ: HS001') + oText('name', 'Họ và tên', 'Họ và tên học sinh');
    if(p.loai === 'nop') return head('Xem lại lựa chọn', 'Bấm "Nộp bài": trình duyệt sẽ tải tệp phiếu về máy, em gửi tệp đó cho giáo viên. Em sẽ không thấy điểm; giáo viên sẽ chấm.') + tomTat();
    const ng = NGAY[p.k], ma = ng.d.ma;
    if(p.loai === 'di') return head(ng.d.ten, '') +
      radios('di-' + ma, 'Em có đăng ký sinh hoạt ' + ng.d.ten + ' không?', [CO_BUOI, KHONG_BUOI]);
    if(p.loai === 'top'){
      let h = head(ng.d.ten + ': xếp Top và tick CLB muốn thi', TRO_GIUP.top);
      const cacNhan = [BO_TRONG].concat(ng.d.clubs.map(nhan));
      for(let k = 1; k <= 10; k++){
        const key = ma + '-top-' + k;
        h += '<label class="rowsel"><span>Top ' + k + '</span><select data-key="' + esc(key) + '">' +
          '<option value="">Chọn CLB</option>' +
          cacNhan.map(function(o){ return '<option value="' + esc(o) + '"' + (st.ans[key] === o ? ' selected' : '') + '>' + esc(o) + '</option>'; }).join('') +
          '</select></label>';
      }
      if(!ng.coThi.length) return h;
      const dang = st.ans['chon-' + ma] || [];
      h += '<fieldset class="q"><legend>Chọn CLB em muốn thi ' + esc(ng.d.ten) + ' (tối đa ' + TRAN_THI + ', có thể thi 0 đến ' + TRAN_THI + ' CLB)</legend>' +
        '<p class="help">' + esc(TRO_GIUP.tick) + '</p>';
      ng.coThi.forEach(function(c){
        const o = nhan(c);
        h += '<label class="opt"><input type="checkbox" data-chon="1" data-key="chon-' + esc(ma) + '" value="' + esc(o) + '"' +
          (dang.indexOf(o) >= 0 ? ' checked' : '') + '><span>' + esc(o) + '</span></label>';
      });
      return h + '</fieldset>';
    }
    if(p.loai === 'first'){
      const ops = luaChonDau(ng);
      donDep('thi-' + ma, ops);
      const chuaXep = daTick(ng).filter(function(c){ return xepTop(ng).indexOf(nhan(c)) < 0; });
      let h = head(ng.d.ten + ': chọn CLB làm bài trước', TRO_GIUP.first);
      if(chuaXep.length){
        h += '<p class="warnbox">CLB chưa được xếp trong Top 1 đến Top 10 sẽ không được tính điểm: ' +
          esc(chuaXep.map(function(c){ return c.name; }).join(', ')) + '.</p>';
      }
      if(!daTick(ng).length) h += '<p class="help">Em chưa tick CLB nào buổi này. Chọn Không thi.</p>';
      return h + radios('thi-' + ma, 'Em thi CLB nào trước? Chỉ hiện các CLB em đã tick.', ops);
    }
    if(p.loai === 'exam'){
      const c = ng.coThi[p.i];
      let h = head('Đề thi ' + c.name, 'Mỗi câu ' + DIEM_CAU + ' điểm. Trả lời đủ các câu để đi tiếp.');
      c.de.forEach(function(q, j){ h += radios(c.id + '-' + (j + 1), q.q, q.opts); });
      return h;
    }
    if(p.loai === 'tiep'){
      const c = ng.coThi[p.i];
      const ops = luaChonTiep(ng, p.i);
      donDep('thi-sau-' + c.id, ops);
      return head(ng.d.ten + ': CLB làm tiếp theo', TRO_GIUP.tiep) +
        radios('thi-sau-' + c.id, 'Em thi CLB nào tiếp theo? Chỉ còn các CLB em đã tick và đứng sau CLB vừa làm.', ops);
    }
    return '';
  }

  function bang(tieu, dong){
    let h = '<table><thead><tr>' + tieu.map(function(t){ return '<th>' + esc(t) + '</th>'; }).join('') + '</tr></thead><tbody>';
    if(!dong.length) h += '<tr><td colspan="' + tieu.length + '" class="muted">Không có dòng nào.</td></tr>';
    dong.forEach(function(r){
      h += '<tr>' + tieu.map(function(_, i){ return '<td>' + esc(r[i] == null ? '' : r[i]) + '</td>'; }).join('') + '</tr>';
    });
    return h + '</tbody></table>';
  }

  function render(){
    const p = TRANG[st.cur];
    let h = '';
    if(st.thongBao){
      h += '<div class="ok">' + esc(st.thongBao) +
        (DA_NOP ? ' <button class="btn ghost" id="tai-phieu">Tải lại tệp phiếu (.json)</button>' : '') + '</div>';
    }
    h += '<div class="pagebox">' + noiDung(p) + '</div>';
    h += '<div class="nav"><button class="btn ghost" id="quay"' + (st.path.length < 2 ? ' disabled' : '') + '>Quay lại</button>';
    h += '<div>' + (p.loai === 'nop' ? '<button class="btn" id="nop">Nộp bài</button>' : '<button class="btn" id="tiep">Tiếp</button>') + '</div></div>';
    h += st.loi ? '<p class="err">' + esc(st.loi) + '</p>' : '';
    h += '<p><button class="linkbtn" id="lam-lai">Làm lại từ đầu</button></p>';
    $('#form').innerHTML = h;
  }

  function tiepTrang(){
    const loi = thieu(st.cur);
    if(loi){ st.loi = loi; render(); return; }
    const nx = sang(st.cur);
    if(nx < 0){ st.loi = 'Lựa chọn này không còn hợp lệ. Em hãy chọn lại.'; render(); return; }
    st.cur = nx; st.path.push(nx); st.loi = ''; st.thongBao = '';
    render();
    $('#thi').scrollIntoView({behavior: 'smooth', block: 'start'});
  }

  function nopBai(){
    const phieu = {};
    st.path.forEach(function(idx){
      keysOf(idx).forEach(function(k){ if(st.ans[k] !== undefined) phieu[k] = st.ans[k]; });
    });
    DA_NOP = {loai: 'phieu_thi_12_clb', nop_luc: new Date().toISOString(), phieu: phieu};
    taiPhieu();
    st = moi('Đã nộp bài của ' + (phieu.name || 'thí sinh') + '. Nếu trình duyệt chưa tải tệp phiếu, bấm nút bên dưới. Em gửi tệp phiếu cho giáo viên. Cảm ơn em.');
    render();
  }
  function taiPhieu(){
    taiTep('phieu_' + String(DA_NOP.phieu.student_id || 'thi_sinh').replace(/[^A-Za-z0-9]+/g, '_') + '.json',
      new Blob([JSON.stringify(DA_NOP, null, 1)], {type: 'application/json'}));
  }

  function onChange(e){
    const el = e.target;
    if(!el || !el.getAttribute || !el.getAttribute('data-key')) return;
    if(e.type === 'input' && el.type !== 'text') return;
    if(e.type === 'change' && el.type === 'text') return;
    const key = el.getAttribute('data-key');
    if(el.type === 'checkbox'){
      const cac = Array.prototype.slice.call(document.querySelectorAll('input[type=checkbox][data-key="' + key + '"]:checked'))
        .map(function(x){ return x.value; });
      if(cac.length > TRAN_THI){
        el.checked = false;
        st.loi = 'Chỉ được tick tối đa ' + TRAN_THI + ' CLB trong một buổi.';
        render();
        return;
      }
      if(cac.length) st.ans[key] = cac; else delete st.ans[key];
      st.loi = '';
      render();
      return;
    }
    if(el.value === '') delete st.ans[key]; else st.ans[key] = el.value;
    st.loi = '';
    if(el.type !== 'text') render();
  }

  $('#form').addEventListener('change', onChange);
  $('#form').addEventListener('input', onChange);
  $('#form').addEventListener('click', function(e){
    const b = e.target.closest ? e.target.closest('button') : null;
    if(!b) return;
    if(b.id === 'quay' && st.path.length > 1){
      st.path.pop(); st.cur = st.path[st.path.length - 1]; st.loi = ''; st.thongBao = '';
      render();
    } else if(b.id === 'tiep'){
      tiepTrang();
    } else if(b.id === 'nop'){
      nopBai();
    } else if(b.id === 'tai-phieu'){
      taiPhieu();
    } else if(b.id === 'lam-lai'){
      st = moi();
      render();
    }
  });

  function taiTep(ten, blob){
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = ten;
    document.body.appendChild(a);
    a.click();
    setTimeout(function(){ URL.revokeObjectURL(a.href); a.remove(); }, 0);
  }
  function taiCSV(ten, rows){
    const dong = rows.map(function(r){
      return r.map(function(x){
        // Ô bắt đầu bằng = + - @ (hoặc tab, CR) có thêm dấu nháy đơn để Excel không chạy như công thức.
        // Cùng quy tắc với api_chung.py; api_nhap.py gỡ dấu này khi nạp lại.
        const s = x == null ? '' : String(x);
        const an = /^[=+\-@\t\r]/.test(s) ? "'" + s : s;
        return /[",\n\r]/.test(an) ? '"' + an.replace(/"/g, '""') + '"' : an;
      }).join(',');
    }).join('\r\n');
    taiTep(ten, new Blob(['﻿' + dong], {type: 'text/csv;charset=utf-8'}));
  }
  function docTep(file){
    return new Promise(function(resolve, reject){
      const r = new FileReader();
      r.onload = function(){ resolve(r.result); };
      r.onerror = reject;
      r.readAsText(file, 'utf-8');
    });
  }
  function renderGV(){
    const kq = chamTheoCLB(phieuTheoNopLuc());
    $('#gv-ket-qua').innerHTML = bang(kq.hs[0], kq.hs.slice(1));
    $('#gv-canh').innerHTML = bang(kq.canh[0], kq.canh.slice(1));
  }
  $('#gv-tep').addEventListener('change', function(e){
    const files = Array.prototype.slice.call(e.target.files || []);
    Promise.all(files.map(docTep)).then(function(texts){
      const loi = [], top11 = [];
      let trung = 0;
      texts.forEach(function(t, i){
        let obj = null;
        try { obj = JSON.parse(t); } catch(err){ obj = null; }
        if(!(obj && obj.loai === 'phieu_thi_12_clb' && obj.phieu)){ loi.push(files[i].name); return; }
        // Cùng nội dung (kể cả thời điểm nộp) thì là cùng một tệp đã nạp rồi: bỏ bản sao.
        const khoa = JSON.stringify(obj);
        if(DA_NAP[khoa]){ trung++; return; }
        DA_NAP[khoa] = true;
        const p = obj.phieu;
        let coTop11 = false;
        // Trang chỉ cho Top 1–10, nhưng tệp có thể bị sửa tay: bỏ Top 11 trở lên trước khi chấm.
        Object.keys(p).forEach(function(k){
          const m = /-top-(\d+)$/.exec(k);
          if(m && Number(m[1]) > 10){ delete p[k]; coTop11 = true; }
        });
        if(coTop11) top11.push(String(p.student_id || files[i].name));
        GV.push({nop_luc: String(obj.nop_luc || ''), phieu: p});
      });
      $('#gv-so').textContent = 'Đã nạp ' + GV.length + ' phiếu.' +
        (trung ? ' Bỏ ' + trung + ' tệp trùng nội dung.' : '') +
        (loi.length ? ' Không đọc được: ' + loi.join(', ') + '.' : '') +
        (top11.length ? ' Đã bỏ Top 11 trở lên (trang chỉ có Top 1–10) của: ' + top11.join(', ') + '.' : '');
      renderGV();
    });
  });
  $('#gv-tai-clb').addEventListener('click', function(){ taiCSV('1_CLB.csv', chamTheoCLB(phieuTheoNopLuc()).clb); });
  $('#gv-tai-so').addEventListener('click', function(){ taiCSV('2_Hoc_sinh.csv', chamTheoCLB(phieuTheoNopLuc()).hs); });
  $('#gv-tai-canh').addEventListener('click', function(){ taiCSV('canh_bao.csv', chamTheoCLB(phieuTheoNopLuc()).canh); });
  $('#gv-xoa').addEventListener('click', function(){
    GV.length = 0;
    Object.keys(DA_NAP).forEach(function(k){ delete DA_NAP[k]; });
    $('#gv-so').textContent = '';
    $('#gv-tep').value = '';
    renderGV();
  });

  // Chỉ tiêu do giáo viên nhập. Giữ trong bộ nhớ trang; tải lại trang thì nhập lại.
  const CHI_TIEU = {};
  function veChiTieu(){
    let h = '';
    BUOI.forEach(function(d){
      h += '<h3>' + esc(d.ten) + '</h3>';
      d.clubs.forEach(function(c){
        h += '<div class="cap"><span>' + esc(c.name) + '</span><input type="number" inputmode="numeric" min="1" step="1" data-cap="' +
          esc(c.id) + '" value="' + esc(CHI_TIEU[c.id] || '') + '"></div>';
      });
    });
    $('#gv-chi-tieu').innerHTML = h;
  }
  $('#gv-chi-tieu').addEventListener('input', function(e){
    const el = e.target;
    if(el && el.getAttribute && el.getAttribute('data-cap')) CHI_TIEU[el.getAttribute('data-cap')] = el.value;
  });
  // CLB chưa có chỉ tiêu hợp lệ (số nguyên dương, không có số 0 đứng đầu).
  function thieuChiTieu(){
    const thieu = [];
    BUOI.forEach(function(d){ d.clubs.forEach(function(c){
      if(!/^[1-9][0-9]*$/.test(String(CHI_TIEU[c.id] || '').trim())) thieu.push(c.name);
    }); });
    return thieu;
  }
  $('#gv-tai-xlsx').addEventListener('click', function(){
    const thieu = thieuChiTieu();
    if(thieu.length){
      $('#gv-so').textContent = 'Chưa xuất được. Thiếu hoặc sai chỉ tiêu của ' + thieu.length + ' CLB: ' + thieu.join(', ') + '.';
      return;
    }
    const kq = chamTheoCLB(phieuTheoNopLuc());
    const sheetClb = [['Tên CLB', 'Buổi', 'Chỉ tiêu', 'Suất ưu tiên', 'Nhóm ưu tiên', 'Mã CLB']];
    BUOI.forEach(function(d){ d.clubs.forEach(function(c){
      sheetClb.push([c.name, d.ma, Number(String(CHI_TIEU[c.id]).trim()), '', '', c.id]);
    }); });
    const bytes = dungXlsx([{ten: '1. CLB', dong: sheetClb}, {ten: '2. Học sinh', dong: kq.hs}]);
    taiTep('SO_NHAP_CLB.xlsx', new Blob([bytes], {type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}));
  });

  veChiTieu();
  render();
  renderGV();
})();
</script>
</body>
</html>
"""


# Chỉ thêm kiểu cho khung cảnh báo của trang này; phần còn lại dùng lại CSS của trang mẫu.
CSS_THEM = (".warnbox{background:var(--warn-bg);color:var(--warn-fg);padding:8px 12px;border-radius:8px;font-size:14px;margin:8px 0}"
            ".cap{display:grid;grid-template-columns:1fr 110px;gap:8px;align-items:center;margin:4px 0}"
            "input[type=number]{width:100%;font:inherit;padding:6px 8px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--fg)}")


def _css():
    return tw.KHUON.split("<style>")[1].split("</style>")[0] + CSS_THEM


def _logic():
    return tw.KHUON.split("/*LOGIC-BEGIN*/")[1].split("/*LOGIC-END*/")[0].strip()


def _js(v):
    return json.dumps(v, ensure_ascii=False).replace("</", "<\\/")


def noi_dung():
    """Toàn bộ tệp HTML, dữ liệu 60 CLB lấy từ de_thi_12_clb.du_lieu()."""
    logic = _logic().replace("__DU_LIEU__", _js(de_thi_12_clb.du_lieu()))
    return (KHUON.replace("__CSS__", _css())
                 .replace("__LOGIC__", logic)
                 .replace("__TRO_GIUP__", _js(TRO_GIUP)))


def main():
    os.makedirs(os.path.dirname(RA), exist_ok=True)
    with open(RA, "w", encoding="utf-8", newline="\n") as f:
        f.write(noi_dung())
    print("Đã ghi %s" % RA)


if __name__ == "__main__":
    main()
