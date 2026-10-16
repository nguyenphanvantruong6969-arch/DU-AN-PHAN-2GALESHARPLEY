# -*- coding: utf-8 -*-
"""Sinh docs/website_mau/index.html: trang mẫu giới thiệu và mô phỏng biểu mẫu Google Forms CLB.

Dữ liệu đề lấy từ tao_google_forms.du_lieu_gs() (cùng bộ với TAO_GOOGLE_FORM.gs), nên trang và
biểu mẫu không lệch nhau. Không sửa tay tệp HTML: sửa khuôn ở đây rồi chạy lại:

    python mau_forms_thi_clb/tao_website_mau.py

Khối giữa LOGIC-BEGIN và LOGIC-END là bản JavaScript của chamTheoCLB; test đối chiếu từng
kịch bản phiếu với tệp .gs (test_trang_web_cham_giong_chamtheoclb).
"""

import json
import os
import sys

THU_MUC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THU_MUC)
import tao_google_forms as tg  # noqa: E402  (dữ liệu đề và chữ trợ giúp của biểu mẫu)

RA = os.path.normpath(os.path.join(THU_MUC, os.pardir, "docs", "website_mau", "index.html"))

# Chữ trợ giúp giống hệt biểu mẫu Google (taoBieuMau / khuôn MAU). Test kiểm các câu có nguồn
# trong tao_google_forms.noi_dung(), nên sửa một bên mà quên bên kia thì đỏ.
TRO_GIUP = {
    "top": ("Top 1 là CLB em thích nhất. Bấm vào từng Top để chọn CLB trong danh sách. "
            "Mỗi CLB chỉ chọn một lần. Không muốn thêm thì để (Bỏ trống). "
            "Muốn CLB được chấm điểm: xếp CLB đó ở một Top, tick ở ô bên dưới, rồi làm bài thi."),
    "tick": ("Không thi CLB nào thì bỏ trống. CLB được chấm điểm khi vừa được xếp ở một Top, "
             "vừa được tick ở đây, và vừa được làm bài."),
    "chon_dau": ("Chọn CLB đứng trên cùng (đứng đầu trong danh sách) trong số các CLB em đã tick. "
                 "Không thi CLB nào thì chọn \"Em không thi CLB nào buổi này\". "
                 "Làm xong thì chỉ chọn được CLB đứng sau."),
    "thi_sau": ("Chỉ hiện các CLB đứng sau CLB vừa làm. "
                "Chọn CLB em đã tick tiếp theo; hết rồi thì chọn Không thi thêm."),
}

# Các câu (không cần ghép hằng số) phải có nguyên văn trong biểu mẫu Google.
CAU_TRO_GIUP_CO_NGUON = [
    "Top 1 là CLB em thích nhất.",
    "Mỗi CLB chỉ chọn một lần.",
    "Muốn CLB được chấm điểm: xếp CLB đó ở một Top, tick ở ô bên dưới, rồi làm bài thi.",
    "CLB được chấm điểm khi vừa được xếp ở một Top, vừa được tick ở đây, và vừa được làm bài.",
    "Không thi CLB nào thì bỏ trống.",
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
<title>Đăng ký CLB và thi tuyển: trang mẫu</title>
<style>
:root{--bg:#f6f6f3;--fg:#1d1d1b;--muted:#5f5f59;--card:#fff;--line:#d9d9d1;--accent:#2f5d8c;--soft:#eaf1f9;--ok-fg:#1f6b3a;--ok-bg:#e7f4ec;--err-fg:#b42318;--warn-fg:#8a5a00;--warn-bg:#fdf3e1}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#161716;--fg:#ecebe6;--muted:#a9a9a1;--card:#20211f;--line:#3d3f3b;--accent:#8fb4dd;--soft:#263140;--ok-fg:#9fe0b4;--ok-bg:#1d3326;--err-fg:#ff8a80;--warn-fg:#ffcf8a;--warn-bg:#3a2c1b}}
:root[data-theme="dark"]{--bg:#161716;--fg:#ecebe6;--muted:#a9a9a1;--card:#20211f;--line:#3d3f3b;--accent:#8fb4dd;--soft:#263140;--ok-fg:#9fe0b4;--ok-bg:#1d3326;--err-fg:#ff8a80;--warn-fg:#ffcf8a;--warn-bg:#3a2c1b}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{background:var(--bg);color:var(--fg);font:15px/1.6 system-ui,"Segoe UI",Roboto,Arial,sans-serif}
main{max-width:880px;margin:0 auto;padding:16px}
h1{font-size:24px;margin:6px 0 4px;line-height:1.3}
h2{font-size:18px;margin:0 0 8px;color:var(--accent)}
h3{font-size:16px;margin:14px 0 4px}
p{margin:6px 0}
.muted{color:var(--muted);font-size:13px}
.hero{padding:18px 0 6px}
.badge{display:inline-block;font-size:12px;font-weight:600;color:var(--warn-fg);background:var(--warn-bg);padding:2px 10px;border-radius:999px;margin:0 0 6px}
nav.top{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 4px}
nav.top a{color:var(--accent);text-decoration:none;font-size:14px;border:1px solid var(--line);border-radius:999px;padding:4px 12px;background:var(--card)}
section.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;margin:14px 0}
ol.steps{padding-left:20px;margin:6px 0}
ol.steps li{margin:6px 0}
.rules{background:var(--soft);border-radius:10px;padding:10px 14px;margin-top:10px}
.rules ul{margin:4px 0;padding-left:20px}
.pagebox{border:1px solid var(--line);border-radius:10px;padding:14px;background:var(--bg)}
fieldset.q{border:1px solid var(--line);border-radius:10px;padding:10px 12px;margin:10px 0;background:var(--card);min-width:0}
fieldset.q legend{font-weight:600;padding:0 6px}
.help{color:var(--muted);font-size:13.5px;margin:4px 0 8px}
label.opt{display:flex;align-items:flex-start;gap:8px;padding:6px 4px;border-radius:6px;cursor:pointer}
label.opt input{margin-top:5px}
label.rowsel{display:grid;grid-template-columns:70px 1fr;gap:8px;align-items:center;margin:6px 0}
select,input[type=text]{width:100%;font:inherit;padding:7px 9px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--fg)}
.nav{display:flex;flex-wrap:wrap;gap:8px;justify-content:space-between;align-items:center;margin-top:14px}
.btn{font:inherit;padding:8px 16px;border-radius:8px;border:1px solid var(--accent);background:var(--accent);color:#fff;cursor:pointer}
.btn.ghost{background:transparent;color:var(--accent)}
.btn:disabled{opacity:.4;cursor:default}
.linkbtn{background:none;border:none;color:var(--accent);cursor:pointer;font:inherit;padding:4px 0;text-decoration:underline}
.ok{background:var(--ok-bg);color:var(--ok-fg);padding:8px 12px;border-radius:8px;margin-bottom:10px}
.err{color:var(--err-fg);margin:8px 0 0;font-size:14px}
.tablewrap{overflow-x:auto;margin-top:8px;min-width:0}
table{border-collapse:collapse;width:100%;font-size:13.5px}
th,td{text-align:left;vertical-align:top;padding:6px 8px;border-bottom:1px solid var(--line)}
th{background:var(--soft);font-weight:600;white-space:nowrap}
td{word-break:break-word}
.toolbar{display:flex;flex-wrap:wrap;gap:8px;margin:6px 0 10px}
footer{color:var(--muted);font-size:12.5px;padding:14px 0 30px}
code{font-family:ui-monospace,Consolas,monospace;font-size:12.5px;background:var(--soft);padding:0 4px;border-radius:4px}
@media (max-width:480px){main{padding:12px}section.card{padding:12px}h1{font-size:21px}}
</style>
</head>
<body>
<main>
<header class="hero">
  <span class="badge">Dữ liệu mô phỏng</span>
  <h1>Đăng ký CLB và thi tuyển</h1>
  <p>Trang mẫu cho một trường phổ thông. Học sinh xếp nguyện vọng CLB theo từng buổi, chọn CLB muốn thi, rồi làm đề. Mọi dữ liệu trên trang là dữ liệu mẫu, không phải của học sinh thật.</p>
  <nav class="top"><a href="#gioi-thieu">Giới thiệu</a><a href="#thu">Thử biểu mẫu</a><a href="#so-nhap">Sổ nhập mẫu</a></nav>
</header>

<section id="gioi-thieu" class="card">
  <h2>Quy trình</h2>
  <ol class="steps">
    <li><b>Biểu mẫu Google Forms.</b> Mỗi buổi, học sinh xếp Top 1 đến Top 10 các CLB (danh sách thả xuống) và tick tối đa 5 CLB muốn thi.</li>
    <li><b>Làm đề.</b> Học sinh chọn lần lượt CLB muốn thi rồi làm đề của CLB đó. Mỗi đề 2 câu, mỗi câu 5 điểm.</li>
    <li><b>Chấm điểm.</b> Hàm chamTheoCLB chấm lại theo đáp án gốc. Điểm một CLB chỉ được tính khi CLB đó được xếp Top, được tick và được làm bài.</li>
    <li><b>Sổ nhập.</b> Ra một tệp SO_NHAP_CLB.xlsx, kéo vào phần mềm xếp CLB (rbda-kiosk). Phần mềm chỉ đọc trang "1. CLB" và "2. Học sinh".</li>
  </ol>
  <div class="rules">
    <b>Quy tắc so trùng mã học sinh</b>
    <ul>
      <li>"HS 001" và "HS001" là một học sinh (gõ thừa khoảng trắng): giữ phiếu nộp đầu tiên.</li>
      <li>"HS001" và "hs001" là hai học sinh, theo quy tắc của phần mềm kiosk: giữ cả hai và có cảnh báo để giáo viên soát.</li>
    </ul>
  </div>
</section>

<section id="thu" class="card">
  <h2>Thử biểu mẫu</h2>
  <p class="muted">Điền một phiếu như học sinh. Phiếu nộp sẽ hiện ở phần "Sổ nhập mẫu". Dữ liệu chỉ nằm trong trình duyệt và mất khi tải lại trang.</p>
  <div id="form"></div>
</section>

<section id="so-nhap" class="card">
  <h2>Sổ nhập mẫu (phần giáo viên thấy)</h2>
  <p class="muted">Bấm "Thêm phiếu mẫu" để xem ba trường hợp so trùng: phiếu bị bỏ vì nộp lại, và phiếu được giữ nhưng có cảnh báo vì chỉ khác hoa thường.</p>
  <div class="toolbar">
    <button class="btn ghost" data-mau="1">Thêm phiếu mẫu 1</button>
    <button class="btn ghost" data-mau="2">Thêm phiếu mẫu 2 (nộp lại)</button>
    <button class="btn ghost" data-mau="3">Thêm phiếu mẫu 3 (khác hoa thường)</button>
    <button class="btn ghost" id="xoa-het">Xoá hết phiếu</button>
  </div>
  <h3>Phiếu đã nộp</h3>
  <div id="ds-phieu" class="tablewrap"></div>
  <h3>Cảnh báo</h3>
  <div id="canh-bao" class="tablewrap"></div>
  <h3>Trang "1. CLB"</h3>
  <div id="sheet-clb" class="tablewrap"></div>
  <h3>Trang "2. Học sinh"</h3>
  <div id="sheet-hs" class="tablewrap"></div>
</section>

<footer>Trang này do <code>mau_forms_thi_clb/tao_website_mau.py</code> sinh ra từ cùng dữ liệu đề với <code>TAO_GOOGLE_FORM.gs</code>. Không sửa tay.</footer>
</main>
<script>
/*LOGIC-BEGIN*/
const BUOI = __DU_LIEU__;
const DIEM_CAU = 5, TRAN_THI = 5;
const CO_BUOI = "Có", KHONG_BUOI = "Không, em bận buổi này";
const KHONG_THI = "Em không thi CLB nào buổi này";
const DUNG = "Em không thi thêm CLB nào buổi này";
const BO_TRONG = "(Bỏ trống)";

function nhan(c){ return c.name + ' (' + c.id + ')'; }
function maClb(v){ const m = String(v == null ? '' : v).match(/\(([A-Za-z0-9_]+)\)\s*$/); return m ? m[1] : ''; }
function chuanHoa(s){ return String(s == null ? '' : s).trim().replace(/\s+/g, ' ').toLowerCase(); }

function docTopPhieu(d, tl){
  const ds = []; let coThaXuong = false;
  d.clubs.forEach(function(_, k){
    const ma = d.ma + '-top-' + (k + 1);
    if(!(ma in tl)) return;
    coThaXuong = true;
    const id = maClb(tl[ma]);
    if(id) ds.push({id: id, top: k + 1});
  });
  return coThaXuong ? ds : [];
}

function chamTheoCLB(phieuList){
  const daCo = {}, daThuong = {}, hocSinh = [], canhBao = [];
  phieuList.forEach(function(tl, i){
    const sid = String(tl.student_id || '').trim();
    const khoa = sid.replace(/\s+/g, '');
    const dong = 'Phiếu thứ ' + (i + 1);
    if(!sid){ canhBao.push([dong, '', 'Không có mã học sinh, bỏ cả phiếu']); return; }
    if(daCo[khoa]){ canhBao.push([dong, sid, 'Nộp lần nữa. Bỏ phiếu này, giữ phiếu đầu (' + daCo[khoa] + ')']); return; }
    daCo[khoa] = dong;
    const chuThuong = sid.toLowerCase();
    if(daThuong[chuThuong] && daThuong[chuThuong] !== sid){
      canhBao.push([dong, sid, 'Chỉ khác hoa thường với mã ' + daThuong[chuThuong] + ' đã nộp: giữ cả hai, nên soát.']);
    } else {
      daThuong[chuThuong] = sid;
    }
    const hs = {sid: sid, ten: String(tl.name || '').trim(), nv: {}, diem: {}, thi: []};
    BUOI.forEach(function(d){
      if(tl['di-' + d.ma] !== CO_BUOI) return;
      const top = docTopPhieu(d, tl);
      let truoc = 0; const topCua = {}; const nv = [];
      top.forEach(function(x){
        if(x.top !== truoc + 1){
          canhBao.push([dong, sid, d.ten + ': bỏ trống Top ' + (truoc + 1) + ' nhưng có chọn Top ' + x.top + ', đã dồn lên.']);
        }
        truoc = x.top;
        if(topCua[x.id]){
          canhBao.push([dong, sid, d.ten + ': chọn ' + x.id + ' ở cả Top ' + topCua[x.id] + ' và Top ' + x.top + ', giữ Top ' + topCua[x.id] + '.']);
          return;
        }
        topCua[x.id] = x.top; nv.push(x.id);
      });
      if(!nv.length) canhBao.push([dong, sid, d.ten + ': đăng ký buổi nhưng không xếp CLB nào.']);
      hs.nv[d.ma] = nv;

      const daTick = {};
      [].concat(tl['chon-' + d.ma] || []).forEach(function(v){ const m = maClb(v); if(m) daTick[m] = true; });
      const daLam = {};
      [tl['thi-' + d.ma]].concat(d.clubs.map(function(c){ return tl['thi-sau-' + c.id]; })).forEach(function(v){
        const id = maClb(v); if(id) daLam[id] = true;
      });

      let soThi = 0;
      d.clubs.forEach(function(c){
        if(!daLam[c.id]){
          if(daTick[c.id]) canhBao.push([dong, sid, d.ten + ': tick ' + c.name + ' nhưng không làm bài.']);
          return;
        }
        if(!daTick[c.id]){
          canhBao.push([dong, sid, d.ten + ': làm bài ' + c.name + ' nhưng không tick ở câu chọn CLB thi, không tính điểm.']);
          return;
        }
        if(nv.indexOf(c.id) < 0){
          canhBao.push([dong, sid, d.ten + ': làm bài ' + c.name + ' nhưng không chọn CLB này ở Top nào, không tính điểm.']);
          return;
        }
        if(soThi >= TRAN_THI){
          canhBao.push([dong, sid, d.ten + ': quá ' + TRAN_THI + ' CLB, bỏ bài ' + c.name + '.']);
          return;
        }
        soThi++;
        let dung = 0;
        c.de.forEach(function(q, j){ if(chuanHoa(tl[c.id + '-' + (j + 1)]) === chuanHoa(q.dung)) dung++; });
        hs.diem[c.id] = dung * DIEM_CAU;
        hs.thi.push(c.id);
      });
    });
    hocSinh.push(hs);
  });

  const tenClb = {}, daDung = {};
  BUOI.forEach(function(d){ d.clubs.forEach(function(c){
    let ten = c.name;
    if(daDung[ten.toLowerCase()]) ten = c.name + ' (' + d.ten + ')';
    if(daDung[ten.toLowerCase()]) ten = c.name + ' (' + c.id + ')';
    daDung[ten.toLowerCase()] = true;
    tenClb[c.id] = ten;
  }); });
  const soNv = Math.max.apply(null, [1].concat(hocSinh.map(function(h){
    return BUOI.reduce(function(n, d){ return n + (h.nv[d.ma] || []).length; }, 0);
  })));
  const tHs = ['Mã HS', 'Họ tên'];
  for(let i = 1; i <= soNv; i++) tHs.push('NV' + i, 'Điểm ' + i);
  const soHs = [tHs].concat(hocSinh.map(function(h){
    const row = [h.sid, h.ten];
    BUOI.forEach(function(d){
      (h.nv[d.ma] || []).forEach(function(id){
        row.push(tenClb[id] || id, h.diem.hasOwnProperty(id) ? h.diem[id] : '');
      });
    });
    while(row.length < tHs.length) row.push('');
    return row;
  }));
  const soClb = [['Tên CLB', 'Buổi', 'Chỉ tiêu', 'Suất ưu tiên', 'Nhóm ưu tiên', 'Mã CLB']];
  BUOI.forEach(function(d){ d.clubs.forEach(function(c){ soClb.push([tenClb[c.id], d.ma, '', '', '', c.id]); }); });
  const canh = [['Phiếu', 'Mã HS', 'Nội dung']].concat(canhBao.length ? canhBao : [['', '', 'Không có cảnh báo nào.']]);
  return {clb: soClb, hs: soHs, canh: canh};
}
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

  // Lập trang theo đúng thứ tự của taoBieuMau: mỗi buổi là trang buổi, trang xếp hạng,
  // trang chọn đầu, rồi mỗi CLB có đề là một trang đề và (trừ CLB cuối) một trang "tiếp theo".
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

  const PHIEU = [];
  function moi(thongBao){ return {cur: 0, path: [0], ans: {}, loi: '', thongBao: thongBao || ''}; }
  let st = moi();

  // Trang kế tiếp khi bấm Tiếp, theo câu trả lời hiện có (-1 nếu chưa đủ).
  function sang(idx){
    const p = TRANG[idx], a = st.ans;
    if(p.loai === 'info') return NGAY[0].iDi;
    const ng = NGAY[p.k], ma = ng.d.ma;
    if(p.loai === 'di') return a['di-' + ma] === CO_BUOI ? ng.iTop : tiepNgay(p.k);
    if(p.loai === 'top') return ng.coThi.length ? ng.iFirst : tiepNgay(p.k);
    if(p.loai === 'first'){
      const v = a['thi-' + ma];
      if(v === KHONG_THI) return tiepNgay(p.k);
      const j = ng.coThi.findIndex(function(c){ return nhan(c) === v; });
      return j < 0 ? -1 : ng.iExam[j];
    }
    if(p.loai === 'exam') return ng.iTiep[p.i] >= 0 ? ng.iTiep[p.i] : tiepNgay(p.k);
    if(p.loai === 'tiep'){
      const v = a['thi-sau-' + ng.coThi[p.i].id];
      if(v === DUNG) return tiepNgay(p.k);
      const j = ng.coThi.findIndex(function(c){ return nhan(c) === v; });
      return j < 0 ? -1 : ng.iExam[j];
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

  // Các khoá câu trả lời của một trang (để chỉ gửi những trang đã đi qua).
  function keysOf(idx){
    const p = TRANG[idx];
    if(p.loai === 'info') return ['student_id', 'name'];
    if(p.loai === 'nop') return [];
    const ng = NGAY[p.k], ma = ng.d.ma;
    if(p.loai === 'di') return ['di-' + ma];
    if(p.loai === 'top'){
      const ks = ng.d.clubs.map(function(_, k){ return ma + '-top-' + (k + 1); });
      if(ng.coThi.length) ks.push('chon-' + ma);
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
        dong.push(['Học sinh', (st.ans.name || '') + ' (' + (st.ans.student_id || '') + ')']);
        return;
      }
      const ng = NGAY[p.k];
      if(p.loai === 'di'){
        dong.push([ng.d.ten, st.ans['di-' + ng.d.ma] === CO_BUOI ? 'Có sinh hoạt' : 'Bận buổi này']);
      } else if(p.loai === 'top'){
        const tops = ng.d.clubs.map(function(_, k){ return [k + 1, st.ans[ng.d.ma + '-top-' + (k + 1)]]; })
          .filter(function(x){ return x[1] && x[1] !== BO_TRONG; });
        dong.push([ng.d.ten + ': xếp Top', tops.length ? tops.map(function(x){ return 'Top ' + x[0] + ': ' + x[1]; }).join('; ') : 'Không xếp CLB nào']);
        if(ng.coThi.length){
          const chon = st.ans['chon-' + ng.d.ma] || [];
          dong.push([ng.d.ten + ': CLB muốn thi', chon.length ? chon.join('; ') : 'Không thi CLB nào']);
        }
      } else if(p.loai === 'first'){
        dong.push([ng.d.ten + ': thi trước', st.ans['thi-' + ng.d.ma] || '']);
      } else if(p.loai === 'exam'){
        const c = ng.coThi[p.i];
        const da = c.de.filter(function(_, j){ return st.ans[c.id + '-' + (j + 1)]; }).length;
        dong.push(['Đề ' + c.name, 'Đã trả lời ' + da + '/' + c.de.length + ' câu']);
      } else if(p.loai === 'tiep'){
        dong.push([ng.d.ten + ': thi tiếp theo', st.ans['thi-sau-' + ng.coThi[p.i].id] || '']);
      }
    });
    return bang(['Mục', 'Lựa chọn'], dong);
  }

  function noiDung(p){
    if(p.loai === 'info') return head('Thông tin học sinh', 'Ghi đúng mã trên thẻ học sinh.') +
      oText('student_id', 'Mã học sinh', 'Ví dụ: HS001') + oText('name', 'Họ và tên', 'Họ và tên học sinh');
    if(p.loai === 'nop') return head('Xem lại phiếu', 'Đây là các lựa chọn của em. Bấm "Nộp phiếu" để gửi.') + tomTat();
    const ng = NGAY[p.k];
    if(p.loai === 'di') return head(ng.d.ten, 'Buổi này em có đăng ký sinh hoạt không?') +
      radios('di-' + ng.d.ma, 'Em có đăng ký sinh hoạt ' + ng.d.ten + ' không?', [CO_BUOI, KHONG_BUOI]);
    if(p.loai === 'top'){
      let h = head(ng.d.ten + ': nguyện vọng và chọn CLB thi', TRO_GIUP.top);
      const cacNhan = [BO_TRONG].concat(ng.d.clubs.map(nhan));
      ng.d.clubs.forEach(function(_, k){
        const key = ng.d.ma + '-top-' + (k + 1);
        h += '<label class="rowsel"><span>Top ' + (k + 1) + '</span><select data-key="' + esc(key) + '">' +
          '<option value="">Chọn CLB</option>' +
          cacNhan.map(function(o){ return '<option value="' + esc(o) + '"' + (st.ans[key] === o ? ' selected' : '') + '>' + esc(o) + '</option>'; }).join('') +
          '</select></label>';
      });
      if(ng.coThi.length){
        const dang = st.ans['chon-' + ng.d.ma] || [];
        h += '<fieldset class="q"><legend>Chọn các CLB em muốn thi ' + esc(ng.d.ten) + ' (tối đa ' + TRAN_THI + ')</legend>' +
          '<p class="help">' + esc(TRO_GIUP.tick) + '</p>';
        ng.coThi.forEach(function(c){
          const o = nhan(c);
          h += '<label class="opt"><input type="checkbox" data-chon="1" data-key="chon-' + esc(ng.d.ma) + '" value="' + esc(o) + '"' +
            (dang.indexOf(o) >= 0 ? ' checked' : '') + '><span>' + esc(o) + '</span></label>';
        });
        h += '</fieldset>';
      }
      return h;
    }
    if(p.loai === 'first') return head(ng.d.ten + ': làm bài thi', TRO_GIUP.chon_dau) +
      radios('thi-' + ng.d.ma, 'Em thi CLB nào trước? Chọn một CLB em đã tick. Làm xong sẽ được chọn CLB tiếp theo.',
        ng.coThi.map(nhan).concat([KHONG_THI]));
    if(p.loai === 'exam'){
      const c = ng.coThi[p.i];
      let h = head('Đề thi ' + c.name, 'Mỗi câu ' + DIEM_CAU + ' điểm. Trả lời đủ các câu để sang bước tiếp theo.');
      c.de.forEach(function(q, j){ h += radios(c.id + '-' + (j + 1), q.q, q.opts); });
      return h;
    }
    if(p.loai === 'tiep'){
      const c = ng.coThi[p.i];
      return head(ng.d.ten + ': CLB tiếp theo', TRO_GIUP.thi_sau) +
        radios('thi-sau-' + c.id, 'Em thi CLB nào tiếp theo? Chỉ còn các CLB đứng sau ' + c.name + ' trong danh sách.',
          ng.coThi.slice(p.i + 1).map(nhan).concat([DUNG]));
    }
    return '';
  }

  function render(){
    const p = TRANG[st.cur];
    let h = st.thongBao ? '<div class="ok">' + esc(st.thongBao) + '</div>' : '';
    h += '<div class="pagebox">' + noiDung(p) + '</div>';
    h += '<div class="nav"><button class="btn ghost" id="quay"' + (st.path.length < 2 ? ' disabled' : '') + '>Quay lại</button>';
    h += '<div>' + (p.loai === 'nop' ? '<button class="btn" id="nop">Nộp phiếu</button>' : '<button class="btn" id="tiep">Tiếp</button>') + '</div></div>';
    h += st.loi ? '<p class="err">' + esc(st.loi) + '</p>' : '';
    h += '<p><button class="linkbtn" id="lam-lai">Làm lại từ đầu</button></p>';
    $('#form').innerHTML = h;
  }

  function tiepTrang(){
    const loi = thieu(st.cur);
    if(loi){ st.loi = loi; render(); return; }
    const nx = sang(st.cur);
    if(nx < 0){ st.loi = 'Em hãy chọn lại lựa chọn ở trang này.'; render(); return; }
    st.cur = nx; st.path.push(nx); st.loi = ''; st.thongBao = '';
    render();
    $('#thu').scrollIntoView({behavior: 'smooth', block: 'start'});
  }

  function nopPhieu(){
    const phieu = {};
    st.path.forEach(function(idx){
      keysOf(idx).forEach(function(k){ if(st.ans[k] !== undefined) phieu[k] = st.ans[k]; });
    });
    PHIEU.push(phieu);
    st = moi('Đã nộp phiếu của ' + (phieu.name || 'học sinh') + '. Cảm ơn em.');
    render();
    renderSo();
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
        st.loi = 'Chỉ được tick tối đa ' + TRAN_THI + ' CLB.';
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
      nopPhieu();
    } else if(b.id === 'lam-lai'){
      st = moi();
      render();
    }
  });

  // Phiếu mẫu cho phần giáo viên: 1 là phiếu đúng, 2 nộp lại cùng mã (bị bỏ), 3 khác hoa thường (có cảnh báo).
  function mauPhieu(n){
    const ng = NGAY[0], cs = ng.coThi, a = cs[0], b = cs[1], ma = ng.d.ma;
    const p = {student_id: n === 1 ? 'HS001' : (n === 2 ? 'HS 001' : 'hs001'),
      name: n === 3 ? 'Học sinh mẫu B' : 'Học sinh mẫu A'};
    BUOI.forEach(function(d, k){ p['di-' + d.ma] = k === 0 ? CO_BUOI : KHONG_BUOI; });
    p[ma + '-top-1'] = nhan(a);
    p[ma + '-top-2'] = nhan(b);
    p['chon-' + ma] = [nhan(a), nhan(b)];
    p['thi-' + ma] = nhan(a);
    a.de.forEach(function(q, j){ p[a.id + '-' + (j + 1)] = q.dung; });
    b.de.forEach(function(q, j){
      p[b.id + '-' + (j + 1)] = j === 0 ? q.dung : q.opts.find(function(o){ return o !== q.dung; });
    });
    p['thi-sau-' + a.id] = nhan(b);
    p['thi-sau-' + b.id] = DUNG;
    return p;
  }

  function bang(tieu, dong){
    let h = '<table><thead><tr>' + tieu.map(function(t){ return '<th>' + esc(t) + '</th>'; }).join('') + '</tr></thead><tbody>';
    if(!dong.length) h += '<tr><td colspan="' + tieu.length + '" class="muted">Không có dòng nào.</td></tr>';
    dong.forEach(function(r){
      h += '<tr>' + tieu.map(function(_, i){ return '<td>' + esc(r[i] == null ? '' : r[i]) + '</td>'; }).join('') + '</tr>';
    });
    return h + '</tbody></table>';
  }

  function renderSo(){
    const kq = chamTheoCLB(PHIEU);
    $('#ds-phieu').innerHTML = PHIEU.length
      ? bang(['Phiếu', 'Mã', 'Họ tên', 'Số buổi đăng ký'], PHIEU.map(function(p, i){
          return ['Phiếu ' + (i + 1), p.student_id || '', p.name || '', NGAY.filter(function(ng){ return p['di-' + ng.d.ma] === CO_BUOI; }).length];
        }))
      : '<p class="muted">Chưa có phiếu nào. Em có thể nộp phiếu ở phần trên, hoặc bấm "Thêm phiếu mẫu".</p>';
    $('#canh-bao').innerHTML = bang(kq.canh[0], kq.canh.slice(1));
    $('#sheet-clb').innerHTML = bang(kq.clb[0], kq.clb.slice(1));
    $('#sheet-hs').innerHTML = bang(kq.hs[0], kq.hs.slice(1));
  }

  document.querySelectorAll('[data-mau]').forEach(function(b){
    b.addEventListener('click', function(){
      PHIEU.push(mauPhieu(Number(b.getAttribute('data-mau'))));
      renderSo();
    });
  });
  $('#xoa-het').addEventListener('click', function(){ PHIEU.length = 0; renderSo(); });

  render();
  renderSo();
})();
</script>
</body>
</html>
"""


def _js(v):
    """Giá trị JSON nhúng vào <script>: không để chuỗi "</" đóng thẻ sớm."""
    return json.dumps(v, ensure_ascii=False).replace("</", "<\\/")


def noi_dung():
    """Toàn bộ tệp HTML. Dữ liệu đề lấy từ khuôn biểu mẫu, đúng bộ của TAO_GOOGLE_FORM.gs."""
    return (KHUON.replace("__DU_LIEU__", _js(tg.du_lieu_gs()))
                 .replace("__TRO_GIUP__", _js(TRO_GIUP)))


def main():
    os.makedirs(os.path.dirname(RA), exist_ok=True)
    with open(RA, "w", encoding="utf-8", newline="\n") as f:
        f.write(noi_dung())
    print("Đã ghi %s" % RA)


if __name__ == "__main__":
    main()
