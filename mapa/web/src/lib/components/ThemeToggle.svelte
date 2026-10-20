<script lang="ts">
	import { onMount } from 'svelte';

	let dark = $state(false);

	function effective(): boolean {
		const set = document.documentElement.dataset.theme;
		if (set === 'dark') return true;
		if (set === 'light') return false;
		return matchMedia('(prefers-color-scheme: dark)').matches;
	}

	onMount(() => {
		dark = effective();
	});

	function toggle() {
		dark = !dark;
		const next = dark ? 'dark' : 'light';
		document.documentElement.dataset.theme = next;
		try {
			localStorage.setItem('mapa-theme', next);
		} catch {
			/* modo privado: el tema vale para esta visita */
		}
	}
</script>

<button class="t" onclick={toggle} aria-pressed={dark} aria-label="Modo oscuro">
	<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true">
		{#if dark}
			<circle cx="12" cy="12" r="4.2" />
			<path d="M12 2.5v2.4M12 19.1v2.4M2.5 12h2.4M19.1 12h2.4M5.3 5.3l1.7 1.7M17 17l1.7 1.7M5.3 18.7L7 17M17 7l1.7-1.7" stroke-linecap="round" />
		{:else}
			<path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z" stroke-linejoin="round" />
		{/if}
	</svg>
</button>

<style>
	.t {
		display: grid;
		place-items: center;
		width: 36px;
		height: 36px;
		border-radius: 999px;
		border: 1px solid var(--hair);
		background: var(--surface);
	}
	.t:hover {
		border-color: var(--ink-2);
	}
</style>
