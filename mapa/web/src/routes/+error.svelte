<script lang="ts">
	import { page } from '$app/state';
</script>

<svelte:head><title>{page.status} · MAPA</title></svelte:head>

<div class="wrap err">
	<div class="code num">{page.status}</div>
	<h1>{page.status === 404 ? 'Esta página no existe.' : 'Algo no salió como esperábamos.'}</h1>
	<p class="lede">{page.error?.message}</p>
	<p><a class="chip" href="/">Volver al inicio</a> <a class="chip" href="/explorar">Ir al mapa</a></p>
</div>

<style>
	.err {
		padding: 6rem 0;
		max-width: 44rem;
	}
	.code {
		font-size: 1rem;
		font-weight: 600;
		letter-spacing: 0.14em;
		color: var(--orange-ink);
		margin-bottom: 1rem;
	}
	h1 {
		font-size: clamp(2rem, 5vw, 3.6rem);
		margin-bottom: 1.2rem;
	}
</style>
