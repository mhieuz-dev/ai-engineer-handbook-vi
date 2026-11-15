/**
 * Chạy Python thật bằng Pyodide trong Web Worker, nên trang không đơ.
 * Pyodide tải từ jsdelivr theo phiên bản ghim; nhúng bằng Blob để worker là classic (importScripts).
 */

export const PHIEN_BAN_PYODIDE = '0.29.5';
const GOC = `https://cdn.jsdelivr.net/pyodide/v${PHIEN_BAN_PYODIDE}/full/`;

const MA_WORKER = `
let pyodide = null;
let dangNap = null;
let idHienTai = 0;
let chiSo = 0;
let dangTaiGoi = false;

async function nap(url, index) {
  if (pyodide) return;
  if (dangNap) return dangNap;
  dangNap = (async () => {
    importScripts(url);
    pyodide = await loadPyodide({ indexURL: index });
    pyodide.setStdout({ batched: (s) => { if (!dangTaiGoi) self.postMessage({ loai: 'stdout', id: idHienTai, i: chiSo, s }); } });
    pyodide.setStderr({ batched: (s) => { if (!dangTaiGoi) self.postMessage({ loai: 'stderr', id: idHienTai, i: chiSo, s }); } });
    await pyodide.runPythonAsync(\`
def __lay_hinh__():
    import io, base64
    try:
        import matplotlib
        matplotlib.use('agg')
        import matplotlib.pyplot as plt
    except Exception:
        return []
    ds = []
    for n in plt.get_fignums():
        f = plt.figure(n)
        b = io.BytesIO()
        f.savefig(b, format='png', dpi=110, bbox_inches='tight')
        ds.append(base64.b64encode(b.getvalue()).decode())
    plt.close('all')
    return ds

def __goi_y__(code, line, col):
    try:
        import jedi
    except Exception:
        return None
    try:
        s = jedi.Script(code=code)
        return [[c.name, c.type, c.description] for c in s.complete(line, col)[:60]]
    except Exception:
        return []
\`);
    dangNap = null;
    self.postMessage({ loai: 'san-sang' });
  })();
  return dangNap;
}

async function caiJedi() {
  try {
    dangTaiGoi = true;
    await pyodide.loadPackage('micropip');
    const mp = pyodide.pyimport('micropip');
    await mp.install('jedi');
    dangTaiGoi = false;
    return true;
  } catch (e) {
    dangTaiGoi = false;
    return false;
  }
}

self.onmessage = async (e) => {
  const d = e.data || {};
  if (d.loai === 'nap') {
    try { await nap(d.url, d.index); }
    catch (err) { self.postMessage({ loai: 'loi-he-thong', message: 'Không tải được Python: ' + String(err) }); }
    return;
  }
  if (d.loai === 'chay') {
    idHienTai = d.id;
    try {
      for (let i = 0; i < d.chunks.length; i++) {
        chiSo = i;
        self.postMessage({ loai: 'bat-dau', id: d.id, i });
        try {
          dangTaiGoi = true;
          await pyodide.loadPackagesFromImports(d.chunks[i]);
          dangTaiGoi = false;
          await pyodide.runPythonAsync(d.chunks[i]);
        } catch (err) {
          const message = String(err && err.message ? err.message : err);
          self.postMessage({ loai: 'loi', id: d.id, i, message });
          self.postMessage({ loai: 'xong', id: d.id, loi: message });
          return;
        }
        let hinh = [];
        try { hinh = pyodide.runPython('__lay_hinh__()').toJs(); } catch (_) {}
        self.postMessage({ loai: 'hinh', id: d.id, i, hinh });
      }
      self.postMessage({ loai: 'xong', id: d.id, loi: null });
    } catch (err) {
      self.postMessage({ loai: 'loi-he-thong', id: d.id, message: String(err) });
    }
    return;
  }
  if (d.loai === 'goi-y') {
    try {
      if (!pyodide) { self.postMessage({ loai: 'goi-y-kq', id: d.id, ds: null }); return; }
      const kq = pyodide.runPython('__goi_y__(' + JSON.stringify(d.code) + ', ' + d.line + ', ' + d.column + ')');
      let ds = null;
      if (kq !== null && kq !== undefined) {
        ds = kq.toJs();
        if (kq.destroy) kq.destroy();
      }
      self.postMessage({ loai: 'goi-y-kq', id: d.id, ds });
    } catch (err) {
      self.postMessage({ loai: 'goi-y-kq', id: d.id, ds: null });
    }
    return;
  }
  if (d.loai === 'nap-jedi') {
    const ok = pyodide ? await caiJedi() : false;
    self.postMessage({ loai: 'jedi-kq', id: d.id, ok });
    return;
  }
  if (d.loai === 'ghi-tep') {
    try {
      pyodide.FS.writeFile(d.ten, d.noiDung);
      self.postMessage({ loai: 'ghi-tep-xong', id: d.id });
    } catch (err) {
      self.postMessage({ loai: 'ghi-tep-loi', id: d.id, message: String(err) });
    }
  }
};
`;

export interface ThongDiep {
	loai: string;
	id?: number;
	i?: number;
	s?: string;
	message?: string;
	hinh?: string[];
	ds?: [string, string, string][] | null;
	ok?: boolean;
	loi?: string | null;
}

export type Nhan = (m: ThongDiep) => void;

/** Một phiên Pyodide. Huỷ = terminate worker, lần chạy sau tạo phiên mới. */
export class MayChay {
	private worker: Worker | null = null;
	private blobUrl: string | null = null;
	private napXong: Promise<void> | null = null;
	private giaiQuyetNap: { ok: () => void; loi: (e: Error) => void } | null = null;
	private id = 0;
	private cho = new Map<number, Nhan>();
	private moiLuc: Nhan[] = [];
	private daSanSang = false;
	private soLanThu = 0;

	get sanSang(): boolean {
		return this.daSanSang;
	}

	private tao(): void {
		if (this.worker) return;
		const blob = new Blob([MA_WORKER], { type: 'text/javascript' });
		this.blobUrl = URL.createObjectURL(blob);
		this.worker = new Worker(this.blobUrl);
		this.daSanSang = false;
		this.worker.onmessage = (e: MessageEvent<ThongDiep>) => {
			const m = e.data;
			if (m.loai === 'san-sang') {
				this.daSanSang = true;
				this.soLanThu = 0;
				this.giaiQuyetNap?.ok();
				this.giaiQuyetNap = null;
			}
			if (m.loai === 'loi-he-thong') {
				this.giaiQuyetNap?.loi(new Error(m.message ?? 'Lỗi worker'));
				this.giaiQuyetNap = null;
			}
			for (const f of this.moiLuc) f(m);
			if (typeof m.id === 'number') {
				const f = this.cho.get(m.id);
				if (f) {
					f(m);
					if (m.loai === 'xong' || m.loai === 'loi-he-thong' || m.loai === 'goi-y-kq' || m.loai === 'jedi-kq' || m.loai === 'ghi-tep-xong' || m.loai === 'ghi-tep-loi') this.cho.delete(m.id);
				}
			}
		};
		this.worker.onerror = (e) => {
			this.giaiQuyetNap?.loi(new Error(e.message || 'Worker lỗi'));
			this.giaiQuyetNap = null;
			for (const f of this.moiLuc) f({ loai: 'loi-he-thong', message: e.message });
		};
	}

	/** Nghe mọi thông điệp (dùng cho controller lọc theo lượt chạy đang hiển thị). */
	nghe(f: Nhan): void {
		this.moiLuc.push(f);
	}

	async nap(): Promise<void> {
		if (this.daSanSang) return;
		if (this.napXong) return this.napXong;
		this.tao();
		const motLan = new Promise<void>((ok, loi) => {
			this.giaiQuyetNap = { ok, loi };
			this.worker!.postMessage({ loai: 'nap', url: `${GOC}pyodide.js`, index: GOC });
		});
		this.napXong = motLan.catch(async (e) => {
			this.huy();
			this.napXong = null;
			// CDN đôi khi chập chờn: thử lại tối đa 2 lần với worker mới.
			if (this.soLanThu >= 2) throw e;
			this.soLanThu++;
			await new Promise((r) => setTimeout(r, 1200 * this.soLanThu));
			return this.nap();
		});
		return this.napXong;
	}

	chay(chunks: string[], nhan: Nhan): Promise<void> {
		const id = ++this.id;
		return new Promise<void>((xong) => {
			this.cho.set(id, (m) => {
				nhan(m);
				if (m.loai === 'xong' || m.loai === 'loi-he-thong') xong();
			});
			this.worker!.postMessage({ loai: 'chay', id, chunks });
		});
	}

	async goiY(code: string, line: number, column: number): Promise<[string, string, string][] | null> {
		if (!this.daSanSang) return null;
		const id = ++this.id;
		return new Promise((xong) => {
			this.cho.set(id, (m) => {
				if (m.loai === 'goi-y-kq') xong(m.ds ?? null);
			});
			this.worker!.postMessage({ loai: 'goi-y', id, code, line, column });
		});
	}

	async ghiTep(ten: string, noiDung: string): Promise<void> {
		await this.nap();
		const id = ++this.id;
		return new Promise((xong) => {
			this.cho.set(id, (m) => {
				if (m.loai === 'ghi-tep-xong' || m.loai === 'ghi-tep-loi') xong();
			});
			this.worker!.postMessage({ loai: 'ghi-tep', id, ten, noiDung });
		});
	}

	async caiJedi(): Promise<boolean> {
		if (!this.daSanSang) return false;
		const id = ++this.id;
		return new Promise((xong) => {
			this.cho.set(id, (m) => {
				if (m.loai === 'jedi-kq') xong(!!m.ok);
			});
			this.worker!.postMessage({ loai: 'nap-jedi', id });
		});
	}

	huy(): void {
		this.worker?.terminate();
		this.worker = null;
		if (this.blobUrl) URL.revokeObjectURL(this.blobUrl);
		this.blobUrl = null;
		this.napXong = null;
		this.daSanSang = false;
		this.cho.clear();
		this.giaiQuyetNap = null;
	}
}
