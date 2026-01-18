<script lang="ts">
	import { onMount } from 'svelte';
	import { getOllamaStatus, startOllama, type OllamaStatus } from '$lib/api/client';
	import { t, type TranslationKeys } from '$lib/i18n';

	interface Props {
		onStarted?: () => void;
	}

	let { onStarted }: Props = $props();

	let status = $state<OllamaStatus | null>(null);
	let loading = $state(true);
	let starting = $state(false);
	let error = $state<string | null>(null);
	let texts: TranslationKeys = $state({} as TranslationKeys);

	t.subscribe((trans) => {
		texts = trans;
	});

	async function checkStatus() {
		try {
			status = await getOllamaStatus();
			error = null;
		} catch (e) {
			error = e instanceof Error ? e.message : (texts.ollama?.statusError || 'Status check failed');
			status = null;
		} finally {
			loading = false;
		}
	}

	async function handleStartOllama() {
		starting = true;
		error = null;
		try {
			await startOllama();
			await new Promise((resolve) => setTimeout(resolve, 2000));
			await checkStatus();
			if (status?.running) {
				onStarted?.();
			}
		} catch (e) {
			error = e instanceof Error ? e.message : (texts.ollama?.startError || 'Failed to start');
		} finally {
			starting = false;
		}
	}

	onMount(() => {
		checkStatus();
	});
</script>

{#if loading}
	<div class="h-[100px] bg-fill-tertiary rounded-apple-sm animate-pulse"></div>
{:else if !status}
	<div class="p-4 bg-accent-red/5 rounded-apple-sm">
		<p class="text-footnote text-accent-red">{error}</p>
	</div>
{:else if !status.installed}
	<div class="p-4 bg-accent-orange/5 rounded-apple-sm space-y-3">
		<div class="flex items-start gap-3">
			<div class="w-8 h-8 rounded-full bg-accent-orange/10 flex items-center justify-center flex-shrink-0">
				<svg class="w-4 h-4 text-accent-orange" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
				</svg>
			</div>
			<div>
				<p class="text-subhead font-medium text-label-primary">{texts.ollama?.installRequired || 'Ollama Required'}</p>
				<p class="text-footnote text-label-secondary mt-0.5">{texts.ollama?.installDescription || 'Ollama is required to use the translation feature'}</p>
			</div>
		</div>
		<a 
			href="https://ollama.com" 
			target="_blank"
			class="block w-full py-2.5 bg-accent-orange text-white text-subhead font-medium text-center rounded-apple-sm transition-opacity hover:opacity-90"
		>
			{texts.ollama?.installButton || 'Install from ollama.com'}
		</a>
	</div>
{:else if !status.running}
	<div class="p-4 bg-accent-orange/5 rounded-apple-sm space-y-3">
		<div class="flex items-start gap-3">
			<div class="w-8 h-8 rounded-full bg-accent-orange/10 flex items-center justify-center flex-shrink-0">
				<svg class="w-4 h-4 text-accent-orange" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
					<path stroke-linecap="round" stroke-linejoin="round" d="M5.25 5.653c0-.856.917-1.398 1.667-.986l11.54 6.348a1.125 1.125 0 010 1.971l-11.54 6.347a1.125 1.125 0 01-1.667-.985V5.653z" />
				</svg>
			</div>
			<div>
				<p class="text-subhead font-medium text-label-primary">{texts.ollama?.startRequired || 'Ollama Not Running'}</p>
				<p class="text-footnote text-label-secondary mt-0.5">{texts.ollama?.startDescription || 'The server is not running'}</p>
			</div>
		</div>
		<button
			onclick={handleStartOllama}
			disabled={starting}
			class="w-full py-2.5 bg-accent-orange text-white text-subhead font-medium rounded-apple-sm
				   transition-all duration-200 hover:opacity-90
				   disabled:opacity-50 disabled:cursor-not-allowed"
		>
			{#if starting}
				<span class="inline-flex items-center gap-2">
					<svg class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
						<circle class="opacity-20" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" />
						<path class="opacity-80" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
					</svg>
					{texts.ollama?.starting || 'Starting...'}
				</span>
			{:else}
				{texts.ollama?.startButton || 'Start Ollama'}
			{/if}
		</button>
		{#if error}
			<p class="text-footnote text-accent-red">{error}</p>
		{/if}
	</div>
{/if}
