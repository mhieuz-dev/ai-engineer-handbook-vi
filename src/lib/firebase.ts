/** Firebase (Auth Google + Firestore) nạp lười; chưa cấu hình thì mọi hàm báo lỗi và UI tự ẩn. */

const CFG = {
	apiKey: import.meta.env.PUBLIC_FIREBASE_API_KEY as string | undefined,
	authDomain: import.meta.env.PUBLIC_FIREBASE_AUTH_DOMAIN as string | undefined,
	projectId: import.meta.env.PUBLIC_FIREBASE_PROJECT_ID as string | undefined,
	appId: import.meta.env.PUBLIC_FIREBASE_APP_ID as string | undefined,
};

export const CO_CAU_HINH = Boolean(CFG.apiKey && CFG.authDomain && CFG.projectId && CFG.appId);

type Bo = {
	auth: import('firebase/auth').Auth;
	db: import('firebase/firestore').Firestore;
	authMod: typeof import('firebase/auth');
	fireMod: typeof import('firebase/firestore');
};

let bo: Promise<Bo> | null = null;

async function lay(): Promise<Bo> {
	if (!CO_CAU_HINH) throw new Error('Chưa cấu hình Firebase');
	if (!bo) {
		bo = (async () => {
			const [{ initializeApp }, authMod, fireMod] = await Promise.all([
				import('firebase/app'),
				import('firebase/auth'),
				import('firebase/firestore'),
			]);
			const app = initializeApp({
				apiKey: CFG.apiKey!,
				authDomain: CFG.authDomain!,
				projectId: CFG.projectId!,
				appId: CFG.appId!,
			});
			return { auth: authMod.getAuth(app), db: fireMod.getFirestore(app), authMod, fireMod };
		})();
	}
	return bo;
}

export interface NguoiDungNhe {
	uid: string;
	ten: string;
	anh: string;
	email: string;
}

export async function theoDoi(cb: (u: NguoiDungNhe | null) => void): Promise<() => void> {
	const { auth, authMod } = await lay();
	return authMod.onAuthStateChanged(auth, (u) => {
		cb(u ? { uid: u.uid, ten: u.displayName ?? 'Bạn', anh: u.photoURL ?? '', email: u.email ?? '' } : null);
	});
}

export async function dangNhapGoogle(): Promise<NguoiDungNhe> {
	const { auth, authMod } = await lay();
	const p = new authMod.GoogleAuthProvider();
	p.setCustomParameters({ prompt: 'select_account' });
	const kq = await authMod.signInWithPopup(auth, p);
	const u = kq.user;
	return { uid: u.uid, ten: u.displayName ?? 'Bạn', anh: u.photoURL ?? '', email: u.email ?? '' };
}

export async function dangXuat(): Promise<void> {
	const { auth, authMod } = await lay();
	await authMod.signOut(auth);
}

export async function layIdToken(): Promise<string | null> {
	if (!CO_CAU_HINH) return null;
	try {
		const { auth } = await lay();
		return (await auth.currentUser?.getIdToken()) ?? null;
	} catch {
		return null;
	}
}

export async function docNguoiDung(uid: string): Promise<Record<string, unknown> | null> {
	const { db, fireMod } = await lay();
	const snap = await fireMod.getDoc(fireMod.doc(db, 'nguoi_dung', uid));
	if (!snap.exists()) return null;
	const d = snap.data();
	return d && typeof d.duLieu === 'object' && d.duLieu !== null ? (d.duLieu as Record<string, unknown>) : null;
}

export async function ghiNguoiDung(uid: string, duLieu: Record<string, unknown>, hoSo?: { ten?: string; anh?: string }): Promise<void> {
	const { db, fireMod } = await lay();
	await fireMod.setDoc(
		fireMod.doc(db, 'nguoi_dung', uid),
		{ duLieu, capNhat: fireMod.serverTimestamp(), ...(hoSo ? { hoSo } : {}) },
		{ merge: true },
	);
}

export async function xoaNguoiDung(uid: string): Promise<void> {
	const { db, fireMod } = await lay();
	await fireMod.deleteDoc(fireMod.doc(db, 'nguoi_dung', uid));
}
