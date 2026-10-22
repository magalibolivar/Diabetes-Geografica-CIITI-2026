<script lang="ts">
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();
	const atlas = $derived(data.atlas);

	/** El indicador con más provincias marcadas por el INDEC, calculado de los datos (no escrito a mano). */
	const mostFlagged = $derived.by(() => {
		let best: { label: string; n: number } | null = null;
		for (const ind of atlas.indicators) {
			if (ind.derived) continue;
			const n = atlas.provinces.filter((p) => {
				const r = atlas.values[ind.slug]?.[p.slug]?.reliability;
				return r === 'unreliable' || r === 'caution';
			}).length;
			if (n > (best?.n ?? 0)) best = { label: ind.label, n };
		}
		return best;
	});

	/** Un renglón por dataset, con los indicadores que salen de él. */
	const datasets = $derived.by(() => {
		const map = new Map<
			string,
			{ name: string; source: string; period: string; universe: string | null; where: string[]; indicators: string[] }
		>();
		for (const ind of atlas.indicators) {
			if (ind.derived) continue;
			for (const l of ind.lineage) {
				const row = map.get(l.dataset) ?? {
					name: l.datasetName,
					source: l.sourceName,
					period: l.referencePeriod,
					universe: l.universe,
					where: [],
					indicators: []
				};
				row.indicators.push(ind.label);
				row.where.push(l.sourceRef);
				map.set(l.dataset, row);
			}
		}
		return [...map.values()];
	});
</script>

<svelte:head>
	<title>Metodología · MAPA</title>
	<meta name="description" content="De dónde salen los datos de MAPA, qué miden, cómo se calcula cada cifra derivada y qué límites tienen." />
</svelte:head>

<div class="wrap doc">
	<header>
		<div class="eyebrow">Metodología</div>
		<h1>Cómo se hizo, y qué no se puede decir con estos datos.</h1>
		<p class="lede">
			El sitio muestra cifras de fuentes públicas. Lo que sigue explica de dónde vienen, cómo se leen y
			dónde conviene desconfiar, incluso de nosotros.
		</p>
	</header>

	<section>
		<h2>1. Qué es y qué no es</h2>
		<p>
			Es un atlas descriptivo: muestra cómo varían entre las 24 jurisdicciones el autorreporte de diabetes,
			la atención, los factores de riesgo y el contexto socioeconómico.
		</p>
		<p>
			<strong>No es</strong> una medición de cuántas personas tienen diabetes (la encuesta se basa en lo que
			la gente declara), <strong>no explica causas</strong> y no sirve para evaluar a un sistema de salud.
			Las provincias no son personas: una relación entre provincias puede no valer para individuos.
		</p>
	</section>

	<section>
		<h2>2. De dónde salen los datos</h2>
		<div class="tablewrap">
			<table>
				<thead>
					<tr>
						<th>Fuente</th>
						<th>Período</th>
						<th>Población</th>
						<th>Indicadores</th>
						<th>Dónde</th>
					</tr>
				</thead>
				<tbody>
					{#each datasets as d (d.name)}
						<tr>
							<td><strong>{d.source}</strong></td>
							<td class="num">{d.period}</td>
							<td>{d.universe ?? '—'}</td>
							<td>{d.indicators.join(' · ')}</td>
							<td class="where">{[...new Set(d.where)].join('; ')}</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
		<p class="note">
			Los datos no son de un mismo año: la encuesta es de 2018; el NBI que muestra el mapa, la cobertura y la densidad
			provienen del Censo 2022. La serie histórica de NBI 2010 se conserva por separado. No se comparan como si describieran el mismo momento.
		</p>
	</section>

	<section>
		<h2>3. Qué tan confiable es cada cifra</h2>
		<p>
			La Encuesta Nacional de Factores de Riesgo es una muestra, no un censo: cada cifra tiene un margen de
			error. El INDEC publica el <strong>coeficiente de variación (CV)</strong> de cada estimación y la
			clasifica con dos marcas. Las respetamos tal cual:
		</p>
		<ul class="marks">
			<li>
				<span class="flag caution">Con precaución</span>
				El CV está entre 16,6% y 33,3%. La estimación se puede usar, pero con cuidado.
			</li>
			<li>
				<span class="flag">Poco confiable</span>
				El CV supera 33,3%, hay muy pocos casos o la proporción es menor al 5%. Se muestra rayada.
				<strong>No hay que armar rankings ni titulares con ella.</strong>
			</li>
		</ul>
		<p>
			La marca no depende solo del CV: hay provincias con CV moderado que el INDEC igual marca como poco
			confiables, por tener pocos casos. Por eso mostramos la marca oficial y no una regla propia.
		</p>
		<p>
			El <strong>intervalo de confianza del 95%</strong> que aparece en gráficos y tablas lo calculamos
			nosotros a partir del CV: como el CV es el error estándar dividido por la estimación, el intervalo es
			<em>valor ± 1,96 × valor × CV</em>. Es una aproximación normal, acotada entre 0 y 100.
			Cuando dos intervalos se superponen mucho, la diferencia entre provincias puede ser puro azar de la
			muestra.
		</p>
		<p class="note">
			Los indicadores del Censo y de la EPH que mostramos no traen CV en las fuentes que usamos, así que no
			tienen intervalo de confianza.
		</p>
	</section>

	<section>
		<h2>4. Lo que calcula este sitio</h2>
		<dl>
			<dt>Brecha de tratamiento</dt>
			<dd>
				<em>100 − tratamiento.</em> El indicador original (Cuadro 7.5 de la encuesta) mide el porcentaje que
				<strong>realizó algún tipo de tratamiento en las últimas dos semanas</strong>; no distingue si fue
				medicación, dieta u otro, ni si es continuo. Por eso hablamos de <em>brecha de tratamiento</em> y no
				de «falta de acceso». Hereda el margen de error y la marca del original.
			</dd>
			<dt>Diferencia con el país</dt>
			<dd>
				Valor de la provincia menos el total del país, en puntos porcentuales. Si la fuente no publica
				total (algunos indicadores de contexto), se usa el promedio simple de las 24 jurisdicciones y se
				aclara; no pondera por población.
			</dd>
			<dt>Colores del mapa</dt>
			<dd>
				Cortes de igual intervalo con bordes redondos, para que la leyenda se lea sin esfuerzo. La
				densidad de población usa cortes propios porque CABA es cientos de veces más densa que el resto.
			</dd>
			<dt>Correlaciones</dt>
			<dd>
				Mostramos la de Spearman (por rangos), menos sensible a valores extremos que la de Pearson, y
				avisamos cuando sacar a CABA la cambia mucho. Con 24 puntos, una sola provincia puede dar vuelta el
				resultado.
			</dd>
		</dl>
	</section>

	<section>
		<h2>5. El mapa</h2>
		<p>
			Los límites provinciales son los del Instituto Geográfico Nacional (IGN), simplificados para la web
			(tolerancia de unos 440 metros) de modo que provincias vecinas no se superpongan. Se dibujan con una
			proyección cónica de áreas iguales.
		</p>
		<p>
			La provincia de Tierra del Fuego, Antártida e Islas del Atlántico Sur incluye, además de la Isla
			Grande, las <strong>Islas Malvinas</strong>, la <strong>Antártida Argentina</strong> y las islas
			australes (Georgias del Sur, Sandwich del Sur y Orcadas del Sur). Se dibujan como en el mapa oficial
			del IGN: las Malvinas en su lugar y la Antártida con las islas australes en un recuadro aparte.
		</p>
		<p>
			Esos territorios <strong>no tienen datos separados en el mapa</strong>, por eso se ven en gris. Para la ENFR,
			los datos de la provincia describen solo sus localidades urbanas de la Isla Grande. Al tocar cualquiera de
			ellos se abre la ficha de la provincia.
		</p>
		<p>
			El <strong>mosaico</strong> es otra forma de ver lo mismo: cada provincia ocupa un cuadrado igual, así
			ninguna pesa más por su superficie.
		</p>
	</section>

	<section>
		<h2>6. Límites que conviene tener presentes</h2>
		<ul>
			<li><strong>Solo población urbana:</strong> la encuesta cubre localidades de 5.000 o más habitantes.</li>
			<li><strong>Autorreporte:</strong> mide lo que la gente declara; quien nunca se hizo un análisis no lo sabe.</li>
			{#if mostFlagged}
				<li>
					<strong>Muchas estimaciones provinciales son frágiles:</strong> en «{mostFlagged.label}», el INDEC
					marca {mostFlagged.n} de las 24 provincias. Mirá siempre la marca antes de comparar.
				</li>
			{/if}
			<li><strong>Años distintos:</strong> la ENFR corresponde a 2018 y los indicadores censales actuales a 2022. No describen necesariamente la situación presente.</li>
			<li><strong>Sin causalidad:</strong> las comparaciones son descriptivas.</li>
		</ul>
	</section>

	<section>
		<h2>7. Reproducibilidad</h2>
		<p>
			Cada cifra viene de un archivo oficial, se carga con un proceso que verifica que coincida con la
			fuente y queda versionada: cualquier dato nuevo entra como borrador y se revisa antes de publicarse.
			El código y el procedimiento están en el repositorio del proyecto.
		</p>
	</section>
</div>

<style>
	.doc {
		max-width: 52rem;
		padding-bottom: 2rem;
	}
	header {
		padding: 3.5rem 0 1rem;
	}
	h1 {
		font-size: clamp(2.2rem, 5.2vw, 3.9rem);
		margin: 0.7rem 0 1.4rem;
	}
	section {
		margin-top: 3.2rem;
	}
	h2 {
		font-size: 1.8rem;
		margin-bottom: 1rem;
	}
	p,
	li,
	dd {
		font-size: 1.04rem;
		line-height: 1.65;
	}
	ul {
		padding-left: 1.2rem;
	}
	li {
		margin-bottom: 0.5rem;
	}
	.marks {
		list-style: none;
		padding: 0;
		display: grid;
		gap: 0.9rem;
	}
	.marks li {
		display: grid;
		gap: 0.3rem;
		padding: 0.9rem 1.1rem;
		background: var(--surface);
		border-radius: var(--radius-sm);
		box-shadow: 0 0 0 1px var(--ring);
		margin: 0;
	}
	dl {
		display: grid;
		gap: 0.2rem 0;
	}
	dt {
		font-weight: 600;
		margin-top: 1rem;
	}
	dd {
		margin: 0.2rem 0 0;
		color: var(--ink-2);
	}
	.note {
		font-size: 0.92rem;
		color: var(--ink-2);
	}
	.tablewrap {
		overflow-x: auto;
		margin-bottom: 1rem;
	}
	table {
		border-collapse: collapse;
		width: 100%;
		font-size: 0.88rem;
		min-width: 640px;
	}
	th,
	td {
		text-align: left;
		vertical-align: top;
		padding: 0.7rem 0.9rem 0.7rem 0;
		border-bottom: 1px solid var(--hair);
		line-height: 1.45;
	}
	th {
		font-size: 0.72rem;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--ink-2);
	}
	.where {
		color: var(--ink-2);
		font-size: 0.82rem;
	}
</style>
