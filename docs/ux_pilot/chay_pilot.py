# -*- coding: utf-8 -*-
"""Chạy thử giao diện như người dùng MỚI (TASK 11): khởi động `python main.py` (cầu nối trình duyệt),
điều khiển bằng Playwright, chụp mọi màn hình và ghi chữ nhìn thấy ra tệp .txt cạnh ảnh.

    python docs/ux_pilot/chay_pilot.py --ra /duong/dan/ra [--nguoi nhan_su|su_kien] [--lan 1]

Không đụng vào kho mã: chép các tệp CHẠY của phần mềm sang một thư mục tạm rồi chạy `main.py` ở đó,
nên `workspaces/` và các bản xuất nằm trong thư mục tạm. Cầu nối: pywebview không có trong môi trường
này nên `main.py` rơi sang chế độ trình duyệt (`browser_host.serve`); biến RBDA_BROWSER trỏ tới một
tập lệnh chỉ GHI URL ra tệp (thay cho việc mở cửa sổ), và Playwright mở URL đó.
"""

import argparse
import glob
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time

GOC = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(GOC, "tests"))

CHROMIUM = None
for d in sorted(glob.glob("/opt/pw-browsers/chromium-*/chrome-linux/chrome"), reverse=True):
    CHROMIUM = d
    break

TEP_CHAY = ["*.py", "index.html", "style.css", "i18n.js", "i18n_loi.js", "chung.js", "recovery.html",
            "recovery.js", "logo.png", "logo.ico"]


def chep_phan_mem(dich):
    for mau in TEP_CHAY:
        for t in glob.glob(os.path.join(GOC, mau)):
            shutil.copy(t, dich)
    for thu_muc in ("js", "assets"):
        shutil.copytree(os.path.join(GOC, thu_muc), os.path.join(dich, thu_muc))


class PhanMem:
    """`python main.py` trong thư mục tạm, cầu nối trình duyệt, URL lấy từ tập lệnh trình duyệt giả."""

    def __init__(self, goc_tam):
        self.goc = goc_tam
        self.app = os.path.join(goc_tam, "app")
        self.xuat = os.path.join(goc_tam, "tai_xuong")
        os.makedirs(self.app)
        os.makedirs(self.xuat)
        chep_phan_mem(self.app)
        self.tep_url = os.path.join(goc_tam, "url.txt")
        gia = os.path.join(goc_tam, "trinh_duyet_gia.sh")
        with open(gia, "w") as f:
            f.write('#!/bin/sh\necho "$1" | sed "s/^--app=//" > "%s"\n' % self.tep_url)
        os.chmod(gia, os.stat(gia).st_mode | stat.S_IEXEC)
        env = dict(os.environ, RBDA_BROWSER=gia, RBDA_THU_MUC_TAI_VE=self.xuat, PYTHONIOENCODING="utf-8")
        self.log = open(os.path.join(goc_tam, "main.log"), "w", encoding="utf-8")  # noqa: SIM115 (đóng ở dung())
        self.p = subprocess.Popen([sys.executable, "main.py"], cwd=self.app, env=env,
                                  stdout=self.log, stderr=subprocess.STDOUT)
        for _ in range(100):
            if os.path.exists(self.tep_url) and os.path.getsize(self.tep_url) > 0:
                break
            time.sleep(0.2)
        else:
            raise RuntimeError("main.py không báo URL; xem " + self.log.name)
        with open(self.tep_url) as f:
            self.url = f.read().strip()

    def dong(self):
        self.p.terminate()
        try:
            self.p.wait(5)
        except subprocess.TimeoutExpired:
            self.p.kill()
        self.log.close()


class Chup:
    """Chụp màn hình + ghi chữ nhìn thấy: `NN_ten.png` và `NN_ten.txt`."""

    def __init__(self, page, thu_muc):
        self.page, self.thu_muc, self.n = page, thu_muc, 0
        os.makedirs(thu_muc, exist_ok=True)

    TRAN_CAO = 2200        # trang cao hơn thế thì cắt: ảnh 15.000px không ai đọc được

    def __call__(self, ten, toan_trang=True):
        self.n += 1
        ten = re.sub(r"^\d+_", "", ten)
        goc = os.path.join(self.thu_muc, "%02d_%s" % (self.n, ten))
        self.page.wait_for_timeout(400)
        cao = self.page.evaluate("document.documentElement.scrollHeight")
        if cao <= self.TRAN_CAO:
            self.page.screenshot(path=goc + ".png", full_page=True)
        else:
            # đầu trang + từng khối (panel) đang hiện, mỗi khối tối đa 1400px
            self.page.screenshot(path=goc + ".png", full_page=True,
                                 clip={"x": 0, "y": 0, "width": 1280, "height": 1600})
            khoi = self.page.locator(".view.is-active .panel:visible")
            for i in range(min(khoi.count(), 12)):
                hop = khoi.nth(i).evaluate(
                    "e => { const r = e.getBoundingClientRect(); return [r.top + scrollY, r.height]; }")
                if hop[1] < 60:
                    continue
                self.page.screenshot(path="%s_khoi%02d.png" % (goc, i + 1), full_page=True,
                                     clip={"x": 0, "y": hop[0], "width": 1280, "height": min(hop[1], 1400)})
        chu = self.page.evaluate("""() => {
            const hien = [...document.querySelectorAll('.view.is-active, #wsOverlay:not([hidden]), .toast-stack')];
            const phan = hien.map(e => e.innerText).filter(Boolean);
            return phan.join('\\n----\\n');
        }""")
        with open(goc + ".txt", "w", encoding="utf-8") as f:
            f.write(chu)
        return chu


def chay(nguoi, ra, lan):
    from playwright.sync_api import sync_playwright
    import hanh_trinh  # noqa: F401  (cạnh tệp này)
    goc_tam = tempfile.mkdtemp(prefix="pilot_")
    pm = PhanMem(goc_tam)
    try:
        with sync_playwright() as pw:
            br = pw.chromium.launch(executable_path=CHROMIUM, args=["--no-sandbox"])
            ctx = br.new_context(viewport={"width": 1280, "height": 900}, accept_downloads=True)
            page = ctx.new_page()
            loi_js = []
            page.on("pageerror", lambda e: loi_js.append(str(e)))
            page.on("console", lambda m: loi_js.append("console." + m.type + ": " + m.text)
                    if m.type in ("error",) else None)
            page.goto(pm.url)
            page.wait_for_selector("#dropZone")
            chup = Chup(page, os.path.join(ra, nguoi + ("" if lan == 1 else "_lan%d" % lan)))
            ghi = getattr(hanh_trinh, nguoi)(page, chup, pm, GOC)
            with open(os.path.join(chup.thu_muc, "ghi_chu_may.json"), "w", encoding="utf-8") as f:
                json.dump({"loi_js": loi_js, **(ghi or {})}, f, ensure_ascii=False, indent=1)
            br.close()
    finally:
        pm.dong()
        shutil.copy(os.path.join(goc_tam, "main.log"), os.path.join(ra, nguoi + "_main.log"))
        shutil.rmtree(goc_tam, ignore_errors=True)


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    ap = argparse.ArgumentParser()
    ap.add_argument("--ra", required=True)
    ap.add_argument("--nguoi", default="nhan_su", choices=["nhan_su", "su_kien"])
    ap.add_argument("--lan", type=int, default=1)
    ns = ap.parse_args()
    chay(ns.nguoi, ns.ra, ns.lan)
