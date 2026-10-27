#!/usr/bin/env bash
# Kiểm một chương trước khi commit: notebook, code trên web, unit test, build, KaTeX, dấu gạch dài, e2e.
# Chạy:  scripts/kiem_chuong.sh ch20      (cần .venv và thư mục tạm qua biến THU_MUC_CHAY, mặc định /tmp)
# Dừng ở bước đầu tiên hỏng và trả mã lỗi khác 0.
set -euo pipefail
ch="$1"
goc="$(cd "$(dirname "$0")/.." && pwd)"
tam="${THU_MUC_CHAY:-/tmp}"
cd "$goc"
thu_muc=$(ls -d src/content/docs/ai-engineer/${ch}-*)
so=$((10#${ch#ch}))

echo "1. notebook"
python3 "scripts/notebook/${ch}.py"
nb=$(ls notebooks/${ch}_*.ipynb)
(cd "$tam" && "$goc/.venv/bin/python" -W ignore "$goc/scripts/notebook/kiem_output.py" "$goc/$nb") | tee /dev/stderr | grep -q "lech 0"

echo "2. code trên web"
THU_MUC_CHAY="$tam" .venv/bin/python -W ignore scripts/kiem_trang.py "$ch"

echo "3. mô tả trang có dấu hai chấm phải nằm trong ngoặc kép"
if grep -lE '^description: [^"].*: ' "$thu_muc"/*.mdx; then echo "   có description chứa ': ' chưa bọc ngoặc kép"; exit 1; fi

echo "4. ngoặc nhọn ngoài khối code và công thức (MDX hiểu là JSX)"
python3 - "$thu_muc" <<'EOF'
import re, sys, glob
loi = []
for p in glob.glob(sys.argv[1] + "/*.mdx"):
    s = open(p, encoding="utf-8").read()
    s = re.sub(r"```.*?```", "", s, flags=re.S)          # bỏ khối code
    s = re.sub(r"\$\$.*?\$\$", "", s, flags=re.S)        # bỏ công thức khối
    s = re.sub(r"\$[^$\n]*\$", "", s)                    # bỏ công thức dòng
    s = re.sub(r"`[^`\n]*`", "", s)                      # bỏ code dòng
    s = re.sub(r"<[A-Za-z][^>]*>", "", s)                # bỏ thẻ component (thuộc tính có ngoặc nhọn hợp lệ)
    for i, d in enumerate(s.splitlines()):
        if re.search(r"\{[^}]*\}", d) and not d.lstrip().startswith(("import", "export")):
            loi.append(f"{p}: {d.strip()[:80]}")
if loi:
    print("\n".join(loi)); sys.exit(1)
EOF

echo "5. dấu gạch dài"
if grep -c "—\|–" "$thu_muc"/*.mdx "$nb" src/data/thuat-ngu.yaml | grep -v ":0$"; then exit 1; fi

echo "6. unit test"
npm test --silent 2>&1 | tee "$tam/vitest.log" | grep -E "Tests " ; grep -q "failed" "$tam/vitest.log" && exit 1

echo "7. build"
npm run build > "$tam/build.log" 2>&1 || { grep -iE "error" "$tam/build.log" | head; exit 1; }
grep -q "Complete!" "$tam/build.log"
if grep -l "katex-error" dist/ai-engineer/${ch}-*/*/index.html; then echo "   có lỗi KaTeX"; exit 1; fi

echo "8. e2e"
npm run e2e > "$tam/e2e.log" 2>&1 || true
tail -1 "$tam/e2e.log"
if grep -q "✘\|failed" "$tam/e2e.log"; then grep "✘" "$tam/e2e.log" | head; exit 1; fi
echo "OK: chương $so qua mọi bước kiểm"
