import { error } from '@sveltejs/kit';
import { loadMapGeometry } from '#lib/server/atlas';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ params, parent }) => {
	const { atlas } = await parent();
	if (!atlas.provinces.some((p) => p.slug === params.slug)) {
		error(404, 'No encontramos esa provincia.');
	}
	return { slug: params.slug, geometry: await loadMapGeometry() };
};
