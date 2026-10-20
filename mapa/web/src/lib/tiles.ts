/**
 * Mosaico de provincias: cada una ocupa una celda del mismo tamaño, ubicada aproximadamente donde está.
 * Corrige el sesgo del mapa geográfico, donde Santa Cruz pesa 100 veces más que CABA a simple vista.
 */
export interface Tile {
	col: number;
	row: number;
	abbr: string;
}

export const TILES: Record<string, Tile> = {
	jujuy: { col: 1, row: 0, abbr: 'JUJ' },
	salta: { col: 2, row: 0, abbr: 'SAL' },
	formosa: { col: 4, row: 0, abbr: 'FOR' },
	misiones: { col: 6, row: 0, abbr: 'MIS' },
	catamarca: { col: 1, row: 1, abbr: 'CAT' },
	tucuman: { col: 2, row: 1, abbr: 'TUC' },
	'santiago-del-estero': { col: 3, row: 1, abbr: 'SDE' },
	chaco: { col: 4, row: 1, abbr: 'CHA' },
	corrientes: { col: 5, row: 1, abbr: 'COR' },
	'san-juan': { col: 0, row: 2, abbr: 'SJU' },
	'la-rioja': { col: 1, row: 2, abbr: 'LRI' },
	cordoba: { col: 3, row: 2, abbr: 'CBA' },
	'santa-fe': { col: 4, row: 2, abbr: 'SFE' },
	'entre-rios': { col: 5, row: 2, abbr: 'ERI' },
	mendoza: { col: 0, row: 3, abbr: 'MZA' },
	'san-luis': { col: 1, row: 3, abbr: 'SLU' },
	'la-pampa': { col: 2, row: 3, abbr: 'LPA' },
	'buenos-aires': { col: 3, row: 3, abbr: 'BA' },
	caba: { col: 4, row: 3, abbr: 'CABA' },
	neuquen: { col: 1, row: 4, abbr: 'NQN' },
	'rio-negro': { col: 2, row: 4, abbr: 'RNE' },
	chubut: { col: 2, row: 5, abbr: 'CHU' },
	'santa-cruz': { col: 2, row: 6, abbr: 'SCR' },
	'tierra-del-fuego': { col: 2, row: 7, abbr: 'TDF' }
};

export const TILE_COLS = 7;
export const TILE_ROWS = 8;
