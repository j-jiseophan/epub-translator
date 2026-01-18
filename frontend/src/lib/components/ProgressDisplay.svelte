<script lang="ts">
	import { translationStore, type TranslationState, type TranslationStatus } from '$lib/stores/translation';
	import { t, type TranslationKeys } from '$lib/i18n';

	let progress = $state<TranslationState['progress']>({
		chapterCurrent: 0,
		chapterTotal: 0,
		chapterTitle: '',
		chunkCurrent: 0,
		chunkTotal: 0,
		percentage: 0,
		estimatedTimeRemaining: 0,
		previewOriginal: '',
		previewTranslated: ''
	});

	let status = $state<TranslationStatus>('idle');
	let texts: TranslationKeys = $state({} as TranslationKeys);

	translationStore.subscribe((s) => {
		progress = s.progress;
		status = s.status;
	});

	t.subscribe((trans) => {
		texts = trans;
	});

	function formatTime(seconds: number): string {
		if (seconds < 60) return `${Math.round(seconds)}s`;
		if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
		const h = Math.floor(seconds / 3600);
		const m = Math.round((seconds % 3600) / 60);
		return `${h}h ${m}m`;
	}

	const hasStarted = $derived(progress.chapterTotal > 0 || progress.chunkTotal > 0);
	
	function getStatusText(s: TranslationStatus): string {
		const labels: Record<string, string> = {
			parsing: texts.translate?.analyzing || 'Analyzing...',
			translating: '',
			rebuilding: texts.translate?.generating || 'Generating file...'
		};
		return labels[s] || '';
	}

	const statusText = $derived(getStatusText(status));
</script>

<div class="space-y-5">
	{#if status === 'parsing' || status === 'rebuilding'}
		<!-- Indeterminate -->
		<div class="py-8 flex flex-col items-center">
			<div class="w-10 h-10 mb-4">
				<svg class="w-10 h-10 animate-spin text-accent-blue" viewBox="0 0 24 24" fill="none">
					<circle class="opacity-20" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" />
					<path class="opacity-80" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
				</svg>
			</div>
			<p class="text-body text-label-secondary">{statusText}</p>
		</div>
	{:else}
		<!-- Progress -->
		<div>
			<div class="flex items-baseline justify-between mb-2">
				<span class="text-title-3 tabular-nums">{progress.percentage.toFixed(0)}%</span>
				{#if progress.estimatedTimeRemaining > 0}
					<span class="text-footnote text-label-secondary">{formatTime(progress.estimatedTimeRemaining)} {texts.translate?.remaining || 'remaining'}</span>
				{/if}
			</div>
			<div class="progress-track">
				<div class="progress-fill" style="width: {progress.percentage}%"></div>
			</div>
		</div>

		<!-- Stats -->
		{#if hasStarted}
			<div class="flex justify-center gap-8">
				<div class="text-center">
					<p class="text-headline tabular-nums">{progress.chapterCurrent}<span class="text-label-tertiary font-normal">/{progress.chapterTotal}</span></p>
					<p class="text-caption-1 text-label-secondary">{texts.translate?.chapter || 'Chapter'}</p>
				</div>
				<div class="text-center">
					<p class="text-headline tabular-nums">{progress.chunkCurrent}<span class="text-label-tertiary font-normal">/{progress.chunkTotal}</span></p>
					<p class="text-caption-1 text-label-secondary">{texts.translate?.chunk || 'Chunk'}</p>
				</div>
			</div>
		{:else}
			<p class="text-footnote text-label-secondary text-center py-2">{texts.translate?.preprocessing || 'Preprocessing...'}</p>
		{/if}

		<!-- Chapter Title -->
		{#if progress.chapterTitle}
			<div class="separator"></div>
			<p class="text-footnote text-label-secondary truncate">{progress.chapterTitle}</p>
		{/if}

		<!-- Preview -->
		{#if progress.previewOriginal || progress.previewTranslated}
			<div class="separator"></div>
			<div class="space-y-3">
				{#if progress.previewOriginal}
					<div>
						<p class="text-caption-2 text-label-tertiary uppercase tracking-wide mb-1">{texts.translate?.original || 'Original'}</p>
						<p class="text-footnote text-label-secondary line-clamp-2 leading-relaxed">{progress.previewOriginal}</p>
					</div>
				{/if}
				{#if progress.previewTranslated}
					<div>
						<p class="text-caption-2 text-accent-blue uppercase tracking-wide mb-1">{texts.translate?.translated || 'Translated'}</p>
						<p class="text-footnote text-label-primary line-clamp-2 leading-relaxed">{progress.previewTranslated}</p>
					</div>
				{/if}
			</div>
		{/if}
	{/if}
</div>
