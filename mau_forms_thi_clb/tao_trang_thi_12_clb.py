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
  <div class="toolbar">
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
  const GV = [];

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
      if(!a.student_id) return 'Em cần ghi mã học sinh.';
      if(!a.name) return 'Em cần ghi họ và tên.';
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
    if(p.loai === 'nop') return head('Xem lại lựa chọn', 'Bấm "Nộp bài" để gửi. Em sẽ không thấy điểm; giáo viên sẽ chấm.') + tomTat();
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
    DA_NOP = {loai: 'phieu_thi_12_clb', phien: 1, phieu: phieu};
    taiPhieu();
    st = moi('Đã nộp bài của ' + (phieu.name || 'thí sinh') + '. Tệp phiếu đã được tải về máy: em hãy gửi tệp đó cho giáo viên. Cảm ơn em.');
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
        const s = x == null ? '' : String(x);
        return /[",\n\r]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
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
    const kq = chamTheoCLB(GV);
    $('#gv-ket-qua').innerHTML = bang(kq.hs[0], kq.hs.slice(1));
    $('#gv-canh').innerHTML = bang(kq.canh[0], kq.canh.slice(1));
  }
  $('#gv-tep').addEventListener('change', function(e){
    const files = Array.prototype.slice.call(e.target.files || []);
    Promise.all(files.map(docTep)).then(function(texts){
      const loi = [], top11 = [];
      texts.forEach(function(t, i){
        let obj = null;
        try { obj = JSON.parse(t); } catch(err){ obj = null; }
        if(obj && obj.loai === 'phieu_thi_12_clb' && obj.phieu){
          const p = obj.phieu;
          let coTop11 = false;
          // Trang chỉ cho Top 1–10, nhưng tệp có thể bị sửa tay: bỏ Top 11 trở lên trước khi chấm.
          Object.keys(p).forEach(function(k){
            const m = /-top-(\d+)$/.exec(k);
            if(m && Number(m[1]) > 10){ delete p[k]; coTop11 = true; }
          });
          if(coTop11) top11.push(String(p.student_id || files[i].name));
          GV.push(p);
        } else loi.push(files[i].name);
      });
      $('#gv-so').textContent = 'Đã nạp ' + GV.length + ' phiếu.' +
        (loi.length ? ' Không đọc được: ' + loi.join(', ') + '.' : '') +
        (top11.length ? ' Đã bỏ Top 11 trở lên (trang chỉ có Top 1–10) của: ' + top11.join(', ') + '.' : '');
      renderGV();
    });
  });
  $('#gv-tai-clb').addEventListener('click', function(){ taiCSV('1_CLB.csv', chamTheoCLB(GV).clb); });
  $('#gv-tai-so').addEventListener('click', function(){ taiCSV('2_Hoc_sinh.csv', chamTheoCLB(GV).hs); });
  $('#gv-tai-canh').addEventListener('click', function(){ taiCSV('canh_bao.csv', chamTheoCLB(GV).canh); });
  $('#gv-xoa').addEventListener('click', function(){
    GV.length = 0;
    $('#gv-so').textContent = '';
    $('#gv-tep').value = '';
    renderGV();
  });

  render();
  renderGV();
})();
</script>
</body>
</html>
"""


# Chỉ thêm kiểu cho khung cảnh báo của trang này; phần còn lại dùng lại CSS của trang mẫu.
CSS_THEM = ".warnbox{background:var(--warn-bg);color:var(--warn-fg);padding:8px 12px;border-radius:8px;font-size:14px;margin:8px 0}"


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
