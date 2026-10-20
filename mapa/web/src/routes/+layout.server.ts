import { loadAtlas } from '#lib/server/atlas';
import type { LayoutServerLoad } from './$types';

export const load: LayoutServerLoad = async () => ({ atlas: await loadAtlas() });
