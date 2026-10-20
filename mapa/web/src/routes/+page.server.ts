import { loadMapGeometry } from '#lib/server/atlas';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async () => ({ geometry: await loadMapGeometry() });
