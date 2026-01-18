<script lang="ts">
	import { onMount } from 'svelte';
	import { translationStore } from '$lib/stores/translation';
	import { getModels, getOllamaStatus, type OllamaStatus } from '$lib/api/client';
	import { t, type TranslationKeys } from '$lib/i18n';
	import OllamaStatusCard from './OllamaStatus.svelte';

	let models = $state<string[]>([]);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let ollamaStatus = $state<OllamaStatus | null>(null);
	let selectedModel = $state('');
	let texts: TranslationKeys = $state({} as TranslationKeys);

	translationStore.subscribe((s) => {
		selectedModel = s.selectedModel;
	});

	t.subscribe((trans) => {
		texts = trans;
	});

	async function checkOllama() {
		try {
			ollamaStatus = await getOllamaStatus();
			if (ollamaStatus.running) {
				await loadModels();
			}
		} catch (e) {
			error = e instanceof Error ? e.message : (texts.ollama?.statusError || 'Status check failed');
		} finally {
			loading = false;
		}
	}

	async function loadModels() {
		try {
			models = await getModels();
			if (models.length > 0 && !selectedModel) {
				translationStore.setModel(models[0]);
			}
		} catch (e) {
			error = texts.settings?.noModels || 'No models available';
		}
	}

	async function handleOllamaStarted() {
		loading = true;
		error = null;
		await checkOllama();
	}

	onMount(() => {
		checkOllama();
	});

	function handleChange(event: Event) {
		const select = event.target as HTMLSelectElement;
		translationStore.setModel(select.value);
	}
</script>

{#if ollamaStatus && (!ollamaStatus.installed || !ollamaStatus.running)}
	<OllamaStatusCard onStarted={handleOllamaStarted} />
{:else}
	<div class="input-group">
		<label for="model" class="input-label">{texts.settings?.aiModel || 'AI Model'}</label>
		{#if error}
			<div class="py-3 px-4 bg-accent-red/5 rounded-apple-sm">
				<p class="text-footnote text-accent-red">{error}</p>
			</div>
		{:else}
			<select
				id="model"
				class="input-select"
				value={selectedModel}
				onchange={handleChange}
				disabled={loading}
			>
				{#if loading}
					<option>{texts.settings?.loading || 'Loading...'}</option>
				{:else if models.length === 0}
					<option>{texts.settings?.noModels || 'No models'}</option>
				{:else}
					{#each models as model}
						<option value={model}>{model}</option>
					{/each}
				{/if}
			</select>
		{/if}
	</div>
{/if}
