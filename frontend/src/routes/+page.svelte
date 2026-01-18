<script lang="ts">
	import FileUpload from '$lib/components/FileUpload.svelte';
	import LanguageSelector from '$lib/components/LanguageSelector.svelte';
	import ModelSelector from '$lib/components/ModelSelector.svelte';
	import ProgressDisplay from '$lib/components/ProgressDisplay.svelte';
	import LocaleSwitcher from '$lib/components/LocaleSwitcher.svelte';
	import { translationStore, type TranslationState } from '$lib/stores/translation';
	import { t, type TranslationKeys } from '$lib/i18n';
	import {
		startTranslation,
		connectWebSocket,
		getDownloadUrl,
		cancelJob
	} from '$lib/api/client';

	let ws: WebSocket | null = null;
	let appState: TranslationState = $state({
		fileId: null,
		fileName: null,
		chapterCount: 0,
		jobId: null,
		status: 'idle',
		sourceLanguage: 'en',
		targetLanguage: 'ko',
		selectedModel: '',
		progress: {
			chapterCurrent: 0,
			chapterTotal: 0,
			chapterTitle: '',
			chunkCurrent: 0,
			chunkTotal: 0,
			percentage: 0,
			estimatedTimeRemaining: 0,
			previewOriginal: '',
			previewTranslated: ''
		},
		error: null,
		downloadUrl: null
	});

	let texts: TranslationKeys = $state({} as TranslationKeys);

	translationStore.subscribe((s) => {
		appState = s;
	});

	t.subscribe((trans) => {
		texts = trans;
	});

	async function handleStartTranslation() {
		if (!appState.fileId || !appState.selectedModel) return;

		try {
			const { job_id } = await startTranslation({
				file_id: appState.fileId,
				source_language: appState.sourceLanguage,
				target_language: appState.targetLanguage,
				model: appState.selectedModel
			});

			translationStore.startTranslation(job_id);

			ws = connectWebSocket(job_id, (message) => {
				if (message.type === 'progress') {
					if (message.status === 'parsing') {
						translationStore.setStatus('parsing');
					} else if (message.status === 'translating') {
						translationStore.setStatus('translating');
					} else if (message.status === 'rebuilding') {
						translationStore.setStatus('rebuilding');
					} else if (message.status === 'completed' && message.download_url) {
						translationStore.setCompleted(getDownloadUrl(job_id));
						ws?.close();
					} else if (message.status === 'failed') {
						translationStore.setFailed(message.error_message || 'Translation failed');
						ws?.close();
					}

					translationStore.updateProgress({
						chapterCurrent: message.chapter_current,
						chapterTotal: message.chapter_total,
						chapterTitle: message.chapter_title,
						chunkCurrent: message.chunk_current,
						chunkTotal: message.chunk_total,
						percentage: message.percentage,
						estimatedTimeRemaining: message.estimated_time_remaining,
						previewOriginal: message.preview_original,
						previewTranslated: message.preview_translated
					});
				}
			});
		} catch (e) {
			translationStore.setFailed(e instanceof Error ? e.message : 'Failed to start translation');
		}
	}

	async function handleCancel() {
		if (appState.jobId) {
			await cancelJob(appState.jobId);
			ws?.close();
			translationStore.reset();
		}
	}

	function handleReset() {
		ws?.close();
		translationStore.reset();
	}

	function handleDownload() {
		if (appState.downloadUrl) {
			window.open(appState.downloadUrl, '_blank');
		}
	}
</script>

<div class="min-h-screen flex flex-col">
	<!-- Navigation Bar -->
	<nav class="h-12 flex items-center justify-between px-4 border-b border-separator bg-surface-elevated backdrop-blur-apple sticky top-0 z-10">
		<div class="w-20"></div>
		<span class="text-headline">{texts.app.title}</span>
		<div class="w-20 flex justify-end">
			<LocaleSwitcher />
		</div>
	</nav>

	<!-- Content -->
	<main class="flex-1 flex items-start justify-center px-5 py-8">
		<div class="w-full max-w-[480px] animate-fade-in">
			
			{#if appState.status === 'idle'}
				<FileUpload />
			
			{:else if appState.status === 'ready'}
				<div class="space-y-6">
					<!-- File Card -->
					<div class="card p-5">
						<div class="flex items-center gap-4">
							<div class="w-12 h-12 rounded-apple bg-accent-blue/10 flex items-center justify-center flex-shrink-0">
								<svg class="w-6 h-6 text-accent-blue" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
									<path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
								</svg>
							</div>
							<div class="flex-1 min-w-0">
								<p class="text-body font-medium truncate">{appState.fileName}</p>
								<p class="text-footnote text-label-secondary">{appState.chapterCount}{texts.file.chapters}</p>
							</div>
							<button onclick={handleReset} class="btn-text text-subhead">{texts.file.change}</button>
						</div>
					</div>

					<!-- Settings Card -->
					<div class="card p-5 space-y-5">
						<div class="grid grid-cols-2 gap-4">
							<LanguageSelector type="source" />
							<LanguageSelector type="target" />
						</div>
						<div class="separator"></div>
						<ModelSelector />
					</div>

					<!-- Action -->
					<button
						onclick={handleStartTranslation}
						disabled={!appState.selectedModel}
						class="btn-filled w-full"
					>
						{texts.translate.button}
					</button>
				</div>

			{:else if appState.status === 'parsing' || appState.status === 'translating' || appState.status === 'rebuilding'}
				<div class="card p-5">
					<div class="flex items-center justify-between mb-5">
						<p class="text-headline">{texts.translate.translating}</p>
						<button onclick={handleCancel} class="btn-text text-accent-red">{texts.translate.cancel}</button>
					</div>
					<ProgressDisplay />
				</div>

			{:else if appState.status === 'completed'}
				<div class="card p-8 text-center animate-scale-up">
					<div class="w-16 h-16 mx-auto mb-5 rounded-full bg-accent-green/10 flex items-center justify-center">
						<svg class="w-8 h-8 text-accent-green" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" d="M4.5 12.75l6 6 9-13.5" />
						</svg>
					</div>
					<h2 class="text-title-2 mb-1">{texts.complete.title}</h2>
					<p class="text-body text-label-secondary mb-8">{texts.complete.description}</p>
					<div class="space-y-3">
						<button onclick={handleDownload} class="btn-filled w-full">{texts.complete.download}</button>
						<button onclick={handleReset} class="btn-gray w-full">{texts.complete.newFile}</button>
					</div>
				</div>

			{:else if appState.status === 'failed'}
				<div class="card p-8 text-center animate-scale-up">
					<div class="w-16 h-16 mx-auto mb-5 rounded-full bg-accent-red/10 flex items-center justify-center">
						<svg class="w-8 h-8 text-accent-red" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
						</svg>
					</div>
					<h2 class="text-title-2 mb-1">{texts.error.title}</h2>
					<p class="text-callout text-label-secondary mb-2">{texts.error.description}</p>
					<p class="text-footnote text-accent-red mb-8">{appState.error}</p>
					<button onclick={handleReset} class="btn-filled w-full">{texts.error.retry}</button>
				</div>
			{/if}

		</div>
	</main>

	<!-- Footer -->
	<footer class="py-4 text-center">
		<p class="text-caption-1 text-label-tertiary">{texts.app.poweredBy}</p>
	</footer>
</div>
