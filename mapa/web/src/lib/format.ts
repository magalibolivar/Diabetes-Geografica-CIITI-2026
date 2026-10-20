const nf = new Map<number, Intl.NumberFormat>();

function formatter(decimals: number): Intl.NumberFormat {
	let f = nf.get(decimals);
	if (!f) {
		f = new Intl.NumberFormat('es-AR', {
			minimumFractionDigits: decimals,
			maximumFractionDigits: decimals
		});
		nf.set(decimals, f);
	}
	return f;
}

/** 12,7 · usa coma decimal (es-AR) y el signo menos tipográfico (−) en lugar del guion. */
export function num(value: number, decimals = 1): string {
	return formatter(decimals).format(value).replace('-', '−');
}

/** 12,7% — el signo % pegado al número, como se escribe en castellano técnico argentino. */
export function pct(value: number, decimals = 1): string {
	return `${num(value, decimals)}%`;
}

export function withUnit(value: number, unit: string, decimals: number): string {
	return unit === '%' ? pct(value, decimals) : `${num(value, decimals)} ${unit}`;
}

/** Signo explícito: +1,2 / −0,4 (con el signo menos tipográfico). */
export function signed(value: number, decimals = 1): string {
	const s = num(Math.abs(value), decimals);
	if (Math.round(Math.abs(value) * 10 ** decimals) === 0) return s;
	return `${value > 0 ? '+' : '−'}${s}`;
}
