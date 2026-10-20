import { describe, expect, it } from 'vitest';
import { num, pct, signed, withUnit } from './format';

describe('formato es-AR', () => {
	it('coma decimal', () => expect(num(12.7)).toBe('12,7'));
	it('menos tipográfico', () => expect(num(-0.5, 2)).toBe('−0,50'));
	it('porcentaje pegado', () => expect(pct(52.6)).toBe('52,6%'));
	it('miles con punto', () => expect(num(15169, 0)).toBe('15.169'));
	it('unidad', () => expect(withUnit(8.6, 'hab/km²', 1)).toBe('8,6 hab/km²'));
	it('signo explícito y cero sin signo', () => {
		expect(signed(1.234)).toBe('+1,2');
		expect(signed(-0.44)).toBe('−0,4');
		expect(signed(0.02)).toBe('0,0');
	});
});
