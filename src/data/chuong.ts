export type TrangThai = 'xong' | 'sap-co';
export interface Nhanh { id: 'ai-engineer' | 'robotics'; ten: string }
export interface Phan { id: string; nhanh: Nhanh['id']; ten: string }
export interface Chuong { so: number; phan: Phan['id']; ten: string; slug: string; trangThai: TrangThai; notebook?: string }

/** Robotics chưa có Phần nào: sidebar và lộ trình bỏ qua nhánh không có Phần, chỉ kệ sách ở trang chủ hiện nó là "Sắp có". */
export const NHANH: Nhanh[] = [
	{ id: 'ai-engineer', ten: 'AI Engineer' },
	{ id: 'robotics', ten: 'Robotics' },
];

export const PHAN: Phan[] = [
	{ id: 'phan-0', nhanh: 'ai-engineer', ten: 'Phần 0. Bắt đầu' },
	{ id: 'phan-1', nhanh: 'ai-engineer', ten: 'Phần I. Nền tảng' },
	{ id: 'phan-2', nhanh: 'ai-engineer', ten: 'Phần II. Machine Learning cổ điển' },
	{ id: 'phan-3', nhanh: 'ai-engineer', ten: 'Phần III. Deep Learning' },
	{ id: 'phan-3b', nhanh: 'ai-engineer', ten: 'Phần III-B. Reinforcement Learning' },
	{ id: 'phan-4', nhanh: 'ai-engineer', ten: 'Phần IV. NLP và Transformer' },
	{ id: 'phan-5', nhanh: 'ai-engineer', ten: 'Phần V. Mô hình ngôn ngữ lớn' },
	{ id: 'phan-6', nhanh: 'ai-engineer', ten: 'Phần VI. Đưa vào sản xuất' },
	{ id: 'phan-7', nhanh: 'ai-engineer', ten: 'Phần VII. Lên senior' },
];

/** Chương đã xuất bản: thêm phần tử thứ 5 vào dòng của chương trong BANG. Xuất bản chương mới chỉ là sửa dữ liệu. */
interface XuatBan { trangThai: 'xong'; notebook?: string }

// [số, phần, tên, hậu tố slug, xuất bản?]
const BANG: [number, string, string, string, XuatBan?][] = [
	[0, 'phan-0', 'Lộ trình AI Engineer và cách dùng Colab', 'lo-trinh-va-colab'],
	[1, 'phan-1', 'Python từ đầu', 'python-tu-dau'],
	[2, 'phan-1', 'Python cho dữ liệu', 'python-cho-du-lieu'],
	[3, 'phan-1', 'NumPy', 'numpy'],
	[4, 'phan-1', 'Pandas và Matplotlib', 'pandas-va-matplotlib'],
	[5, 'phan-1', 'Đại số tuyến tính cho ML', 'dai-so-tuyen-tinh'],
	[6, 'phan-1', 'Giải tích cho ML', 'giai-tich'],
	[7, 'phan-1', 'Xác suất và thống kê', 'xac-suat-thong-ke'],
	[8, 'phan-1', 'Tối ưu hóa', 'toi-uu-hoa'],
	[9, 'phan-2', 'Quy trình một dự án ML', 'quy-trinh-du-an-ml'],
	[10, 'phan-2', 'Hồi quy tuyến tính', 'hoi-quy-tuyen-tinh', { trangThai: 'xong', notebook: 'ch10_hoi_quy_tuyen_tinh.ipynb' }],
	[11, 'phan-2', 'Hồi quy logistic', 'hoi-quy-logistic'],
	[12, 'phan-2', 'Đánh giá mô hình', 'danh-gia-mo-hinh'],
	[13, 'phan-2', 'Overfitting, bias-variance và regularization', 'overfitting-regularization'],
	[14, 'phan-2', 'KNN và khoảng cách', 'knn'],
	[15, 'phan-2', 'Naive Bayes', 'naive-bayes'],
	[16, 'phan-2', 'SVM và kernel', 'svm-kernel'],
	[17, 'phan-2', 'Cây quyết định', 'cay-quyet-dinh'],
	[18, 'phan-2', 'Ensemble', 'ensemble'],
	[19, 'phan-2', 'Phân cụm', 'phan-cum'],
	[20, 'phan-2', 'Giảm chiều', 'giam-chieu'],
	[21, 'phan-2', 'Feature engineering', 'feature-engineering'],
	[22, 'phan-2', 'Dự án Phần II', 'du-an-phan-2'],
	[23, 'phan-3', 'Nơ-ron và mạng nhiều lớp', 'no-ron-mang-nhieu-lop'],
	[24, 'phan-3', 'Backpropagation tự cài', 'backpropagation'],
	[25, 'phan-3', 'PyTorch căn bản', 'pytorch-can-ban'],
	[26, 'phan-3', 'Huấn luyện mạng sâu', 'huan-luyen-mang-sau'],
	[27, 'phan-3', 'CNN', 'cnn'],
	[28, 'phan-3', 'Kiến trúc CNN và transfer learning', 'kien-truc-cnn'],
	[29, 'phan-3', 'RNN, LSTM, GRU', 'rnn-lstm-gru'],
	[30, 'phan-3', 'Autoencoder và VAE', 'autoencoder-vae'],
	[31, 'phan-3', 'GAN và Diffusion', 'gan-diffusion'],
	[32, 'phan-3', 'Dự án Phần III', 'du-an-phan-3'],
	[33, 'phan-3b', 'Bài toán RL', 'bai-toan-rl'],
	[34, 'phan-3b', 'Quy hoạch động và Q-learning', 'q-learning'],
	[35, 'phan-3b', 'Deep Q-Network', 'dqn'],
	[36, 'phan-3b', 'Policy gradient', 'policy-gradient'],
	[37, 'phan-3b', 'PPO và Gymnasium', 'ppo-gymnasium'],
	[38, 'phan-4', 'Tổng quan NLP và tiền xử lý tiếng Việt', 'tong-quan-nlp'],
	[39, 'phan-4', 'BoW, TF-IDF và mô hình n-gram', 'bow-tfidf-ngram'],
	[40, 'phan-4', 'Word embeddings', 'word-embeddings'],
	[41, 'phan-4', 'Phân loại văn bản', 'phan-loai-van-ban'],
	[42, 'phan-4', 'Gán nhãn chuỗi', 'gan-nhan-chuoi'],
	[43, 'phan-4', 'Seq2Seq và attention', 'seq2seq-attention'],
	[44, 'phan-4', 'Transformer từ đầu', 'transformer'],
	[45, 'phan-4', 'Tokenization và mô hình tiền huấn luyện', 'tokenization-pretrained'],
	[46, 'phan-4', 'Fine-tune PhoBERT', 'fine-tune-phobert'],
	[47, 'phan-5', 'LLM hoạt động thế nào', 'llm-hoat-dong'],
	[48, 'phan-5', 'Prompt engineering', 'prompt-engineering'],
	[49, 'phan-5', 'Fine-tune LLM', 'fine-tune-llm'],
	[50, 'phan-5', 'Căn chỉnh: RLHF và DPO', 'can-chinh-rlhf-dpo'],
	[51, 'phan-5', 'Embeddings và vector database', 'embeddings-vector-db'],
	[52, 'phan-5', 'RAG', 'rag'],
	[53, 'phan-5', 'Agent và tool calling', 'agent-tool-calling'],
	[54, 'phan-5', 'Đánh giá LLM', 'danh-gia-llm'],
	[55, 'phan-5', 'Đa phương thức', 'da-phuong-thuc'],
	[56, 'phan-6', 'Đóng gói mô hình và API với FastAPI', 'fastapi'],
	[57, 'phan-6', 'Serving hiệu năng', 'serving-hieu-nang'],
	[58, 'phan-6', 'Docker và triển khai miễn phí', 'docker-trien-khai'],
	[59, 'phan-6', 'Theo dõi thí nghiệm và quản lý phiên bản', 'mlflow-dvc'],
	[60, 'phan-6', 'Giám sát, data drift và CI/CD cho ML', 'giam-sat-cicd'],
	[61, 'phan-6', 'AI có trách nhiệm', 'ai-co-trach-nhiem'],
	[62, 'phan-7', 'ML system design', 'ml-system-design'],
	[63, 'phan-7', 'Đọc paper và tái hiện kết quả', 'doc-paper'],
	[64, 'phan-7', 'Phỏng vấn và portfolio', 'phong-van-portfolio'],
];

export const CHUONG: Chuong[] = BANG.map(([so, phan, ten, hauTo, xuatBan]) => {
	const c: Chuong = {
		so,
		phan,
		ten,
		slug: `ai-engineer/ch${String(so).padStart(2, '0')}-${hauTo}`,
		trangThai: xuatBan?.trangThai ?? 'sap-co',
	};
	if (xuatBan?.notebook) c.notebook = xuatBan.notebook;
	return c;
});

export function chuongDaXuatBan(): Chuong[] {
	return CHUONG.filter((c) => c.trangThai === 'xong');
}

export function timChuongTheoSlugTrang(slugTrang: string): Chuong | undefined {
	return CHUONG.find((c) => slugTrang === c.slug || slugTrang.startsWith(`${c.slug}/`));
}

/** Cấu hình `sidebar` của Starlight: Nhánh > Phần > Chương, chỉ gồm chương đã xong. */
export function cauHinhSidebar() {
	return NHANH.flatMap((nhanh) => {
		const items = PHAN.filter((p) => p.nhanh === nhanh.id).flatMap((p) => {
			const chuong = chuongDaXuatBan().filter((c) => c.phan === p.id);
			if (chuong.length === 0) return [];
			return [{
				label: p.ten,
				items: chuong.map((c) => ({ label: `${c.so}. ${c.ten}`, items: [{ autogenerate: { directory: c.slug } }] })),
			}];
		});
		return items.length ? [{ label: nhanh.ten, items }] : [];
	});
}
