export type Reliability = 'ok' | 'caution' | 'unreliable' | null;
export type Category = 'outcome' | 'care' | 'risk_factor' | 'context';

export interface Lineage {
	dataset: string;
	datasetName: string;
	sourceName: string;
	publisher: string;
	sourceUrl: string | null;
	referencePeriod: string;
	universe: string | null;
	sourceRef: string;
	note: string | null;
	datasetNotes: string | null;
}

export interface Indicator {
	slug: string;
	label: string;
	description: string;
	unit: string;
	decimals: number;
	higherIs: 'better' | 'worse' | 'neutral';
	category: Category;
	lineage: Lineage[];
	/** Calculado por el sitio a partir de otro indicador (no viene de la fuente). */
	derived?: { formula: string; from: string };
}

export interface Province {
	slug: string;
	iso: string;
	name: string;
	shortName: string;
	region: string | null;
}

export interface Value {
	value: number;
	/** Coeficiente de variación (%) publicado por la fuente. */
	cv: number | null;
	reliability: Reliability;
	period: string;
	dataset: string;
}

/** Todo lo que el sitio necesita saber, ya compuesto. Es JSON puro (viaja al navegador). */
export interface Atlas {
	indicators: Indicator[];
	provinces: Province[];
	country: Province;
	/** values[indicador][jurisdicción] — incluye al total del país cuando la fuente lo informa. */
	values: Record<string, Record<string, Value>>;
}

export interface MapGeometry {
	width: number;
	height: number;
	paths: Record<string, string>;
	centroids: Record<string, [number, number]>;
}

/** Lo que el mapa necesita para dibujar una provincia (ya resuelto por la escala de color). */
export interface MapItem {
	slug: string;
	name: string;
	/** Relleno CSS (variable de tema) */
	fill: string;
	/** Tinta legible sobre el relleno */
	ink: string;
	/** Texto corto para el mosaico (p. ej. "12,7") */
	label: string;
	reliability: Reliability;
	/** Descripción accesible completa */
	aria: string;
}
