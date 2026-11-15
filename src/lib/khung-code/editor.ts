/** CodeMirror 6 tải lười: tô màu Python, số dòng, lịch sử, gợi ý (jedi khi có), tô đỏ dòng lỗi. */
import { basicSetup, EditorView } from 'codemirror';
import { Compartment, StateEffect, StateField } from '@codemirror/state';
import { Decoration, type DecorationSet, keymap } from '@codemirror/view';
import { undo, redo } from '@codemirror/commands';
import { python, pythonLanguage } from '@codemirror/lang-python';
import type { CompletionContext, CompletionResult } from '@codemirror/autocomplete';
import { oneDark } from '@codemirror/theme-one-dark';

export interface TrinhSoan {
	view: EditorView;
	lay(): string;
	dat(ma: string): void;
	danhDauLoi(dong: number | null): void;
	undo(): void;
	redo(): void;
	huy(): void;
}

const hieuLoi = StateEffect.define<number | null>();
const truongLoi = StateField.define<DecorationSet>({
	create: () => Decoration.none,
	update(deco, tr) {
		deco = deco.map(tr.changes);
		for (const e of tr.effects) {
			if (!e.is(hieuLoi)) continue;
			if (e.value == null) deco = Decoration.none;
			else {
				const n = Math.min(Math.max(1, e.value), tr.state.doc.lines);
				deco = Decoration.set([Decoration.line({ class: 'cm-dong-loi' }).range(tr.state.doc.line(n).from)]);
			}
		}
		return deco;
	},
	provide: (f) => EditorView.decorations.from(f),
});

const TU_KHOA = [
	'import', 'from', 'def', 'class', 'return', 'for', 'in', 'while', 'if', 'elif', 'else', 'try', 'except', 'finally',
	'with', 'as', 'lambda', 'yield', 'assert', 'pass', 'break', 'continue', 'print', 'len', 'range', 'enumerate', 'zip',
	'map', 'filter', 'sum', 'min', 'max', 'sorted', 'list', 'dict', 'set', 'tuple', 'int', 'float', 'str', 'bool',
	'abs', 'round', 'open', 'isinstance', 'np', 'pd', 'plt',
];

export type HamGoiY = (code: string, line: number, column: number) => Promise<[string, string, string][] | null>;

const giaoDienSang = EditorView.theme({
	'&': { backgroundColor: 'var(--bg)', color: 'var(--tx)', fontSize: '13.5px' },
	'.cm-content': { fontFamily: "'JetBrains Mono', ui-monospace, monospace", caretColor: 'var(--pri)' },
	'.cm-gutters': { backgroundColor: 'var(--panel)', color: 'var(--mut-chu)', border: 'none' },
	'.cm-activeLine': { backgroundColor: 'color-mix(in srgb, var(--pri) 7%, transparent)' },
	'.cm-activeLineGutter': { backgroundColor: 'color-mix(in srgb, var(--pri) 10%, transparent)' },
	'&.cm-focused': { outline: 'none' },
});

export async function taoTrinhSoan(
	cha: HTMLElement,
	ma: string,
	goiY: HamGoiY,
	khiDoi: (s: string) => void,
	khiChay: () => void,
): Promise<TrinhSoan> {
	const nguonGoiY = async (ctx: CompletionContext): Promise<CompletionResult | null> => {
		const truoc = ctx.matchBefore(/[\w.\u00C0-\u1EF9]*/);
		if (!truoc || (truoc.from === truoc.to && !ctx.explicit)) return null;
		const dong = ctx.state.doc.lineAt(ctx.pos);
		const tienTo = ctx.state.sliceDoc(truoc.from, truoc.to);
		let ds: [string, string, string][] | null = null;
		if (ctx.explicit || tienTo.length >= 1) {
			try {
				ds = await goiY(ctx.state.doc.toString(), dong.number, ctx.pos - dong.from);
			} catch {
				ds = null;
			}
		}
		const tuyChon: { label: string; type: string; detail?: string }[] = [];
		if (ds) {
			for (const [ten, loai, mo] of ds) {
				tuyChon.push({ label: ten, type: loai === 'function' ? 'function' : loai === 'class' ? 'class' : 'variable', detail: mo });
			}
		} else {
			for (const k of TU_KHOA) if (k.startsWith(tienTo) && k !== tienTo) tuyChon.push({ label: k, type: 'keyword' });
		}
		if (!tuyChon.length) return null;
		return { from: truoc.from, options: tuyChon.slice(0, 60), validFor: /^[\w.\u00C0-\u1EF9]*$/ };
	};

	const giaoDien = new Compartment();
	const giaoDienHienTai = () =>
		document.documentElement.getAttribute('data-theme') === 'dark' ? oneDark : giaoDienSang;

	const view = new EditorView({
		parent: cha,
		doc: ma,
		extensions: [
			basicSetup,
			python(),
			pythonLanguage.data.of({ autocomplete: nguonGoiY }),
			EditorView.lineWrapping,
			truongLoi,
			giaoDien.of(giaoDienHienTai()),
			keymap.of([
				{ key: 'Mod-Enter', run: () => { khiChay(); return true; } },
				{ key: 'Ctrl-Enter', run: () => { khiChay(); return true; } },
			]),
			EditorView.updateListener.of((u) => {
				if (u.docChanged) khiDoi(u.state.doc.toString());
			}),
		],
	});

	const theoDoi = new MutationObserver(() => {
		view.dispatch({ effects: giaoDien.reconfigure(giaoDienHienTai()) });
	});
	theoDoi.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

	return {
		view,
		lay: () => view.state.doc.toString(),
		dat(ma) {
			view.dispatch({ changes: { from: 0, to: view.state.doc.length, insert: ma } });
		},
		danhDauLoi(dong) {
			view.dispatch({ effects: hieuLoi.of(dong) });
		},
		undo: () => undo(view),
		redo: () => redo(view),
		huy() {
			theoDoi.disconnect();
			view.destroy();
		},
	};
}
