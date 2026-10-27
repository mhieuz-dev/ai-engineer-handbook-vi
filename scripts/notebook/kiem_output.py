import json, io, contextlib, re, sys
nb = json.load(open(sys.argv[1]))
g = {}; out = None; ok = bad = 0
for c in nb["cells"]:
    s = "".join(c["source"])
    if c["cell_type"] == "code":
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf): exec(s, g)
        out = buf.getvalue().strip()
    elif out is not None:
        m = re.search(r"Output mong đợi[^\n]*:\n+```text\n(.*?)\n```", s, re.S)
        if m:
            if m.group(1).strip() == out: ok += 1
            else: bad += 1; print("LECH:\n", out, "\n---\n", m.group(1))
            out = None
print("khop", ok, "lech", bad)
