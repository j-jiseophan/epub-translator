<script lang="ts">
	import { onMount } from 'svelte';
	import { translationStore } from '$lib/stores/translation';
	import { getLanguages, type Language } from '$lib/api/client';
	import { t, type TranslationKeys } from '$lib/i18n';

	interface Props {
		type: 'source' | 'target';
	}

	let { type }: Props = $props();

	let languages = $state<Language[]>([]);
	let loading = $state(true);
	let texts: TranslationKeys = $state({} as TranslationKeys);

	let selectedValue = $derived.by(() => {
		let value = type === 'source' ? 'en' : 'ko';
		translationStore.subscribe((s) => {
			value = type === 'source' ? s.sourceLanguage : s.targetLanguage;
		})();
		return value;
	});

	t.subscribe((trans) => {
		texts = trans;
	});

	onMount(async () => {
		try {
			languages = await getLanguages();
		} catch (e) {
			console.error('Failed to load languages:', e);
		} finally {
			loading = false;
		}
	});

	function handleChange(event: Event) {
		const select = event.target as HTMLSelectElement;
		if (type === 'source') {
			translationStore.setSourceLanguage(select.value);
		} else {
			translationStore.setTargetLanguage(select.value);
		}
	}

	const label = $derived(type === 'source' 
		? (texts.settings?.sourceLanguage || 'Source Language') 
		: (texts.settings?.targetLanguage || 'Target Language'));
	const selectId = $derived(`lang-${type}`);
</script>

<div class="input-group">
	<label for={selectId} class="input-label">{label}</label>
	<select
		id={selectId}
		class="input-select"
		value={selectedValue}
		onchange={handleChange}
		disabled={loading}
	>
		{#if loading}
			<option>{texts.settings?.loading || 'Loading...'}</option>
		{:else}
			{#each languages as lang}
				<option value={lang.code}>{lang.name}</option>
			{/each}
		{/if}
	</select>
</div>
