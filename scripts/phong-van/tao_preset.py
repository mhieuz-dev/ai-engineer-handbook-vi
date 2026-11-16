"""Sinh 8 preset phỏng vấn vào src/data/phong-van/.

Chạy: .venv/bin/python scripts/phong-van/tao_preset.py
Preset mô phỏng từ chia sẻ công khai của ứng viên; không dùng logo, không
liên kết công ty. Mỗi preset ghi rõ nguồn và trọng tâm.
"""
from __future__ import annotations

from pathlib import Path

import yaml

GOC = Path(__file__).resolve().parents[2]
RA = GOC / "src" / "data" / "phong-van"

NGUON = (
    "Mô phỏng từ chia sẻ công khai của ứng viên trên Glassdoor, LeetCode Discuss và các trang luyện phỏng vấn. "
    "Không dùng logo, không liên kết với công ty nào."
)

P: list[dict] = [
    {
        "id": "google",
        "ten": "Kiểu Google",
        "moTa": "Hai vòng code, ML system design, ML chuyên sâu, hành vi. Hỏi sâu vào dự án và nền tảng.",
        "trongTam": ["Thuật toán", "Pipeline ML đầu cuối", "Attention", "Sâu dự án"],
        "vong": [
            {"ten": "Sàng lọc", "loai": "hanh-vi"},
            {"ten": "Vòng code 1", "loai": "code"},
            {"ten": "Vòng code 2", "loai": "code"},
            {"ten": "ML system design", "loai": "system"},
            {"ten": "ML chuyên sâu", "loai": "ml"},
            {"ten": "Hành vi", "loai": "hanh-vi"},
        ],
        "cau_hoi": {
            "hanh-vi": [
                "Kể về một dự án ML bạn tự hào nhất. Vai trò của bạn, số liệu trước và sau, và điều gì bạn sẽ làm khác?",
                "Kể một lần bạn phát hiện kết quả mô hình sai. Bạn tìm ra nguyên nhân thế nào?",
            ],
            "ml": [
                "Giải thích multi-head attention từ đầu. Vì sao cần nhiều đầu thay vì một đầu lớn?",
                "Vì sao Transformer dùng residual và layer norm? Nếu bỏ đi thì chuyện gì xảy ra?",
                "Bạn có một mô hình phân loại đạt F1 0,9 trên train nhưng 0,6 trên test. Nêu các giả thuyết và cách kiểm.",
            ],
            "system": [
                "Thiết kế hệ thống phát hiện vi phạm bản quyền video cho một nền tảng có 1 tỷ video. Nêu pipeline, dữ liệu, cách đánh giá và cách xử lý khi mô hình sai.",
                "Thiết kế hệ thống gợi ý nội dung cho người dùng mới chưa có lịch sử. Xử lý cold start thế nào?",
            ],
            "product": [],
        },
    },
    {
        "id": "meta",
        "ten": "Kiểu Meta",
        "moTa": "System design gắn sản phẩm, product sense, code và hành vi. Quan tâm chỉ số và tác động người dùng.",
        "trongTam": ["Sản phẩm", "Kiểm duyệt nội dung", "Xếp hạng", "Chỉ số"],
        "vong": [
            {"ten": "Sàng lọc", "loai": "hanh-vi"},
            {"ten": "Code", "loai": "code"},
            {"ten": "ML system design", "loai": "system"},
            {"ten": "Product sense", "loai": "product"},
            {"ten": "Hành vi", "loai": "hanh-vi"},
        ],
        "cau_hoi": {
            "hanh-vi": [
                "Kể một lần bạn phải thuyết phục nhóm đổi hướng kỹ thuật. Bạn dùng dữ liệu gì?",
                "Kể một dự án thất bại. Bạn học được gì và áp dụng ở đâu?",
            ],
            "ml": [
                "Bạn xây mô hình dự đoán tỷ lệ nhấp. AUC tăng nhưng doanh thu giảm. Bạn kiểm tra gì?",
            ],
            "system": [
                "Thiết kế hệ thống kiểm duyệt nội dung đa phương tiện (văn bản, ảnh, video) cho hàng trăm triệu người dùng. Nêu kiến trúc, ngưỡng và quy trình con người.",
                "Thiết kế hệ thống xếp hạng feed. Nêu tín hiệu đầu vào, cách huấn luyện và cách đo tác động.",
            ],
            "product": [
                "Chỉ số tương tác giảm 8% sau một thay đổi mô hình. Bạn xem tín hiệu nào trước, và hỏi ai điều gì?",
                "Bạn có hai tính năng: tăng thời gian xem nhưng giảm số người quay lại. Bạn chọn tính năng nào và vì sao?",
            ],
        },
    },
    {
        "id": "amazon",
        "ten": "Kiểu Amazon",
        "moTa": "Hỏi rộng và sâu, câu hành vi STAR ở mọi vòng, gắn Leadership Principles.",
        "trongTam": ["ML breadth", "ML depth", "STAR", "Ảnh hưởng"],
        "vong": [
            {"ten": "Sàng lọc", "loai": "hanh-vi"},
            {"ten": "ML breadth", "loai": "ml"},
            {"ten": "ML depth", "loai": "ml"},
            {"ten": "Code", "loai": "code"},
            {"ten": "System design", "loai": "system"},
            {"ten": "Hành vi / LP", "loai": "hanh-vi"},
        ],
        "cau_hoi": {
            "hanh-vi": [
                "Kể lần bạn tạo ảnh hưởng khi không có quyền trực tiếp. Bạn làm gì và kết quả ra sao? (STAR)",
                "Kể lần bạn bất đồng với quản lý. Bạn xử lý thế nào? (STAR)",
                "Kể lần bạn phải ra quyết định với dữ liệu chưa đủ. (STAR)",
            ],
            "ml": [
                "Overfitting là gì? Nêu ba cách xử lý và khi nào dùng cách nào.",
                "Giải thích sự khác nhau giữa batch norm và layer norm. Khi nào chọn cái nào?",
                "Bạn đánh giá một mô hình phân loại mất cân bằng thế nào? Vì sao accuracy dễ gây hiểu nhầm?",
            ],
            "system": [
                "Thiết kế hệ thống phát hiện gian lận giao dịch với 1% dương tính. Nêu dữ liệu, mô hình, ngưỡng và chi phí sai.",
            ],
            "product": [],
        },
    },
    {
        "id": "microsoft",
        "ten": "Kiểu Microsoft",
        "moTa": "Bốn đến năm vòng: code, lý thuyết ML, DL/GenAI, thiết kế hệ thống, hành vi.",
        "trongTam": ["Code", "Lý thuyết ML", "GenAI", "Thiết kế"],
        "vong": [
            {"ten": "Sàng lọc", "loai": "hanh-vi"},
            {"ten": "Kỹ thuật qua điện thoại", "loai": "ml"},
            {"ten": "Code", "loai": "code"},
            {"ten": "DL/GenAI", "loai": "ml"},
            {"ten": "System design", "loai": "system"},
            {"ten": "Hành vi", "loai": "hanh-vi"},
        ],
        "cau_hoi": {
            "hanh-vi": [
                "Kể một lần bạn học công nghệ mới trong thời gian ngắn để giải quyết việc thật.",
                "Kể một lần bạn nhận phản hồi khó nghe và thay đổi thế nào.",
            ],
            "ml": [
                "Giải thích backpropagation cho một mạng hai lớp bằng lời, không viết công thức.",
                "RAG là gì? Nêu hai nguyên nhân khiến RAG trả lời sai và cách đo.",
                "Khi nào nên tinh chỉnh một LLM thay vì dùng prompt + RAG?",
            ],
            "system": [
                "Thiết kế dịch vụ tóm tắt tài liệu nội bộ bằng LLM, có kiểm soát chi phí và chất lượng.",
            ],
            "product": [],
        },
    },
    {
        "id": "nvidia",
        "ten": "Kiểu NVIDIA",
        "moTa": "Viết conv2d, attention, forward/backward; GPU, huấn luyện song song, tối ưu suy luận.",
        "trongTam": ["CUDA/GPU", "conv2d", "Attention", "Tối ưu suy luận"],
        "vong": [
            {"ten": "Sàng lọc", "loai": "hanh-vi"},
            {"ten": "Kỹ thuật", "loai": "ml"},
            {"ten": "ML chuyên sâu", "loai": "ml"},
            {"ten": "Code", "loai": "code"},
            {"ten": "Hiring manager", "loai": "system"},
        ],
        "cau_hoi": {
            "hanh-vi": [
                "Kể một lần bạn tối ưu một đoạn code chậm. Bạn đo gì trước và sau?",
            ],
            "ml": [
                "Viết conv2d bằng NumPy (hoặc mô tả từng bước) và nêu độ phức tạp.",
                "Giải thích forward và backward của một MLP hai lớp. Gradient của lớp đầu tính thế nào?",
                "Batch norm và dropout khác nhau ở lúc huấn luyện và lúc suy luận thế nào?",
            ],
            "system": [
                "Bạn có mô hình 7B chạy trên một GPU. Nêu ba cách giảm độ trễ suy luận và đánh đổi của từng cách.",
            ],
            "product": [],
        },
    },
    {
        "id": "viet-nam",
        "ten": "Doanh nghiệp Việt Nam",
        "moTa": "Vòng HR có tiếng Anh, hỏi theo CV và dự án, hệ thống AI chạy ổn định khi lỗi. Thông tin công khai còn ít.",
        "trongTam": ["CV", "Tiếng Anh", "Ổn định hệ thống", "STAR"],
        "vong": [
            {"ten": "HR", "loai": "hanh-vi"},
            {"ten": "Kỹ thuật theo CV", "loai": "ml"},
            {"ten": "Thiết kế / xử lý vấn đề", "loai": "system"},
            {"ten": "Hành vi", "loai": "hanh-vi"},
        ],
        "cau_hoi": {
            "hanh-vi": [
                "Giới thiệu bản thân bằng tiếng Anh trong 90 giây, tập trung vào dự án AI bạn đã làm.",
                "Kể một lần hệ thống bạn phụ trách gặp sự cố. Bạn phát hiện và xử lý thế nào? (STAR)",
                "Kỳ vọng của bạn trong 1 năm tới là gì?",
            ],
            "ml": [
                "Trong dự án gần nhất, bạn chọn mô hình dựa trên tiêu chí nào? Nêu số liệu.",
                "Bạn xử lý dữ liệu thiếu và nhãn nhiễu thế nào?",
                "Làm sao biết mô hình tụt chất lượng sau khi triển khai?",
            ],
            "system": [
                "Thiết kế hệ thống AI chạy ổn định khi một thành phần lỗi. Nêu fallback, giám sát và cảnh báo.",
            ],
            "product": [],
        },
    },
    {
        "id": "startup-genai",
        "ten": "Startup GenAI",
        "moTa": "Code thực hành, thiết kế RAG/LLM, evaluation, hành vi. Quan tâm tốc độ và chi phí.",
        "trongTam": ["RAG", "Evaluation", "Chi phí", "Agent"],
        "vong": [
            {"ten": "Sàng lọc", "loai": "hanh-vi"},
            {"ten": "Code thực hành", "loai": "code"},
            {"ten": "Thiết kế RAG/LLM", "loai": "system"},
            {"ten": "Evaluation", "loai": "ml"},
            {"ten": "Hành vi", "loai": "hanh-vi"},
        ],
        "cau_hoi": {
            "hanh-vi": [
                "Kể một lần bạn phải chọn giữa làm nhanh và làm đúng. Bạn quyết thế nào?",
            ],
            "ml": [
                "Bạn xây dựng golden set để đánh giá chatbot nội bộ thế nào? Nêu quy trình và chỉ số.",
                "Làm sao biết một thay đổi prompt làm chatbot tốt hơn, không chỉ khác đi?",
            ],
            "system": [
                "Thiết kế RAG cho kho tài liệu nội bộ 1 triệu trang. Nêu chunking, truy hồi, xếp hạng lại và cách giảm bịa.",
                "Khi nào nên dùng agent thay vì một pipeline cố định? Nêu rủi ro và cách kiểm soát.",
            ],
            "product": [],
        },
    },
    {
        "id": "tu-do",
        "ten": "Tự do",
        "moTa": "Tự chọn vòng và chủ đề để luyện một kỹ năng.",
        "trongTam": ["Tự chọn"],
        "vong": [
            {"ten": "Khởi động", "loai": "hanh-vi"},
            {"ten": "ML", "loai": "ml"},
            {"ten": "Code", "loai": "code"},
            {"ten": "Hệ thống", "loai": "system"},
        ],
        "cau_hoi": {
            "hanh-vi": ["Kể về bản thân và mục tiêu học AI của bạn."],
            "ml": [
                "Bias-variance là gì? Cho một ví dụ bạn từng gặp.",
                "Giải thích sự khác nhau giữa precision và recall bằng một tình huống thật.",
            ],
            "system": [
                "Thiết kế một hệ thống ML nhỏ bạn có thể tự dựng trong một tuần.",
            ],
            "product": [],
        },
    },
]


def main() -> None:
    assert len(P) == 8, len(P)
    RA.mkdir(parents=True, exist_ok=True)
    for p in P:
        p["nguon"] = NGUON
        with (RA / f"{p['id']}.yaml").open("w", encoding="utf-8") as f:
            yaml.safe_dump(p, f, allow_unicode=True, sort_keys=False, width=100)
    print("da ghi", len(P), "preset vao", RA)


if __name__ == "__main__":
    main()
