# -*- coding: utf-8 -*-
"""Dữ liệu 60 CLB cho trang thi 12 CLB mỗi buổi (docs/thi_12_clb/index.html).

Mỗi buổi có 12 CLB: 10 CLB của bộ mẫu Google Forms (tao_google_forms.du_lieu_gs, không đổi)
cộng 2 CLB mới. Hai CLB mới mỗi buổi là BẢN NHÁP, đánh dấu nhap=True: giáo viên cần duyệt hoặc
thay nội dung trước khi dùng cho thi thật. Biểu mẫu Google Forms không dùng dữ liệu này.
"""

import os
import sys

THU_MUC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, THU_MUC)
import tao_google_forms as tg  # noqa: E402

# Mỗi CLB: id, name, de (2 câu, mỗi câu 4 lựa chọn, đáp án đúng là một trong các lựa chọn).
CLB_MOI = {
    "thu_2": [
        {"id": "clb_dantranh", "name": "CLB Đàn tranh", "de": [
            {"q": "Đàn tranh thường có bao nhiêu dây?", "opts": ["12", "16", "21", "25"], "dung": "16"},
            {"q": "Đàn tranh thuộc nhóm nhạc cụ nào?", "opts": ["Dây gảy", "Hơi", "Gõ", "Phím hơi"], "dung": "Dây gảy"},
        ]},
        {"id": "clb_camhoa", "name": "CLB Cắm hoa", "de": [
            {"q": "Nghệ thuật cắm hoa của Nhật Bản gọi là gì?", "opts": ["Ikebana", "Origami", "Bonsai", "Sushi"], "dung": "Ikebana"},
            {"q": "Yếu tố quan trọng nhất khi cắm hoa là gì?", "opts": ["Bố cục cân đối", "Nhiều màu nhất", "Cắm càng cao càng đẹp", "Dùng hoa giả"], "dung": "Bố cục cân đối"},
        ]},
    ],
    "thu_3": [
        {"id": "clb_khieuvu", "name": "CLB Khiêu vũ", "de": [
            {"q": "Điệu Waltz thường đếm theo nhịp mấy?", "opts": ["2", "3", "4", "6"], "dung": "3"},
            {"q": "Khởi động trước khi nhảy để làm gì?", "opts": ["Tránh chấn thương", "Mệt nhanh hơn", "Quên động tác", "Không cần thiết"], "dung": "Tránh chấn thương"},
        ]},
        {"id": "clb_cocaro", "name": "CLB Cờ caro", "de": [
            {"q": "Bàn cờ caro thường có bao nhiêu ô?", "opts": ["8 x 8", "10 x 10", "15 x 15", "20 x 20"], "dung": "15 x 15"},
            {"q": "Mục tiêu của cờ caro là gì?", "opts": ["Xếp 5 quân liên tiếp", "Bắt hết quân đối phương", "Đưa quân về cuối bàn", "Chiếm nhiều ô nhất"], "dung": "Xếp 5 quân liên tiếp"},
        ]},
    ],
    "thu_4": [
        {"id": "clb_aothuat", "name": "CLB Ảo thuật", "de": [
            {"q": "Đánh lạc hướng khán giả trong ảo thuật nghĩa là gì?", "opts": ["Khiến khán giả chú ý vào chỗ khác", "Làm vật biến mất ngay", "Đọc được suy nghĩ", "Tăng tốc động tác"], "dung": "Khiến khán giả chú ý vào chỗ khác"},
            {"q": "Ảo thuật gia cần chuẩn bị điều gì trước khi biểu diễn?", "opts": ["Tập luyện kỹ thủ pháp", "Mặc thật nhiều áo", "Bỏ qua kịch bản", "Không cần tập"], "dung": "Tập luyện kỹ thủ pháp"},
        ]},
        {"id": "clb_yoga", "name": "CLB Yoga", "de": [
            {"q": "Tư thế cây trong yoga có tên tiếng Phạn là gì?", "opts": ["Vrikshasana", "Trikonasana", "Shavasana", "Bhujangasana"], "dung": "Vrikshasana"},
            {"q": "Shavasana là tư thế gì?", "opts": ["Nằm thư giãn", "Chiến binh", "Cây", "Rắn hổ mang"], "dung": "Nằm thư giãn"},
        ]},
    ],
    "thu_5": [
        {"id": "clb_tiengthai", "name": "CLB Tiếng Thái", "de": [
            {"q": "Tiếng Thái thuộc họ ngôn ngữ nào?", "opts": ["Tai-Kadai", "Hán-Tạng", "Nam Á", "Ấn-Âu"], "dung": "Tai-Kadai"},
            {"q": "Thủ đô của Thái Lan là gì?", "opts": ["Bangkok", "Chiang Mai", "Phuket", "Pattaya"], "dung": "Bangkok"},
        ]},
        {"id": "clb_daukiem", "name": "CLB Đấu kiếm", "de": [
            {"q": "Đấu kiếm thể thao dùng thiết bị gì để ghi điểm?", "opts": ["Thiết bị điện tử", "Cờ", "Chuông", "Ánh sáng"], "dung": "Thiết bị điện tử"},
            {"q": "Đấu kiếm thể thao có mấy loại kiếm phổ biến?", "opts": ["2", "3", "4", "5"], "dung": "3"},
        ]},
    ],
    "thu_6": [
        {"id": "clb_caumay", "name": "CLB Cầu mây", "de": [
            {"q": "Cầu mây (sepak takraw) phổ biến ở khu vực nào?", "opts": ["Đông Nam Á", "Bắc Âu", "Nam Mỹ", "Trung Đông"], "dung": "Đông Nam Á"},
            {"q": "Mỗi đội cầu mây có mấy người trên sân?", "opts": ["3", "4", "5", "6"], "dung": "3"},
        ]},
        {"id": "clb_thuphap", "name": "CLB Thư pháp", "de": [
            {"q": "Thư pháp là nghệ thuật gì?", "opts": ["Viết chữ đẹp bằng bút lông", "Vẽ phong cảnh", "Làm gốm", "Chạm khắc gỗ"], "dung": "Viết chữ đẹp bằng bút lông"},
            {"q": "Dụng cụ chính của thư pháp là gì?", "opts": ["Bút lông và mực", "Cọ sơn dầu", "Bút chì", "Phấn màu"], "dung": "Bút lông và mực"},
        ]},
    ],
}


def _xao_clb(c):
    """Xáo đáp án CLB mới đúng cách bộ mẫu làm (tg.xao, hạt giống là mã CLB và số câu).

    Nếu không xáo, đáp án đúng nằm ở vị trí đầu trong 16 trên 20 câu, và học sinh luôn chọn lựa chọn
    đầu sẽ được 80% số điểm của CLB mới mà không cần biết bài."""
    de = [dict(q, opts=tg.xao(q["opts"], c["id"] + str(j))) for j, q in enumerate(c["de"])]
    return dict(c, de=de)


def du_lieu():
    """Năm buổi, mỗi buổi 12 CLB. CLB của bộ mẫu giữ nguyên thứ tự; CLB mới nối sau, đáp án đã xáo."""
    ngay = []
    for d in tg.du_lieu_gs():
        clubs = [dict(c, nhap=False) for c in d["clubs"]]
        for c in CLB_MOI[d["ma"]]:
            clubs.append(dict(_xao_clb(c), nhap=True))
        ngay.append({"ma": d["ma"], "ten": d["ten"], "clubs": clubs})
    return ngay
