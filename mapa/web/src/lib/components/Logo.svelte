<script lang="ts">
	let { size = 30 }: { size?: number } = $props();
</script>

<!-- Mosaico de provincias en miniatura: la idea del sitio en un símbolo. -->
<svg width={size} height={size} viewBox="0 0 30 30" aria-hidden="true">
	<rect x="3" y="3" width="7" height="7" rx="1.6" style="fill: var(--seq-2)" />
	<rect x="11.5" y="3" width="7" height="7" rx="1.6" style="fill: var(--seq-4)" />
	<rect x="20" y="3" width="7" height="7" rx="1.6" style="fill: var(--seq-6)" />
	<rect x="3" y="11.5" width="7" height="7" rx="1.6" style="fill: var(--seq-4)" />
	<rect x="11.5" y="11.5" width="7" height="7" rx="1.6" style="fill: var(--orange)" />
	<rect x="20" y="11.5" width="7" height="7" rx="1.6" style="fill: var(--seq-3)" />
	<rect x="11.5" y="20" width="7" height="7" rx="1.6" style="fill: var(--seq-5)" />
</svg>
