<script lang="ts">
	import { translationStore } from '$lib/stores/translation';
	import { uploadFile } from '$lib/api/client';
	import { t, type TranslationKeys } from '$lib/i18n';

	let isDragging = $state(false);
	let isUploading = $state(false);
	let error = $state<string | null>(null);
	let texts: TranslationKeys = $state({} as TranslationKeys);

	t.subscribe((trans) => {
		texts = trans;
	});

	async function handleFile(file: File) {
		if (!file.name.endsWith('.epub')) {
			error = texts.upload?.errorInvalidFile || 'Only EPUB files are supported';
			return;
		}

		error = null;
		isUploading = true;

		try {
			const response = await uploadFile(file);
			translationStore.setFile(response.file_id, response.filename, response.chapter_count);
		} catch (e) {
			error = e instanceof Error ? e.message : (texts.upload?.errorUploadFailed || 'Upload failed');
		} finally {
			isUploading = false;
		}
	}

	function handleDrop(event: DragEvent) {
		event.preventDefault();
		isDragging = false;
		const file = event.dataTransfer?.files[0];
		if (file) handleFile(file);
	}

	function handleDragOver(event: DragEvent) {
		event.preventDefault();
		isDragging = true;
	}

	function handleDragLeave() {
		isDragging = false;
	}

	function handleInputChange(event: Event) {
		const input = event.target as HTMLInputElement;
		const file = input.files?.[0];
		if (file) handleFile(file);
	}
</script>

<div class="card overflow-hidden">
	<div
		class="p-8 transition-colors duration-200 {isDragging ? 'bg-accent-blue/5' : ''}"
		ondrop={handleDrop}
		ondragover={handleDragOver}
		ondragleave={handleDragLeave}
		role="button"
		tabindex="0"
	>
		{#if isUploading}
			<div class="flex flex-col items-center py-4">
				<div class="w-10 h-10 mb-4 relative">
					<svg class="w-10 h-10 animate-spin text-accent-blue" viewBox="0 0 24 24" fill="none">
						<circle class="opacity-20" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" />
						<path class="opacity-80" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
					</svg>
				</div>
				<p class="text-body text-label-secondary">{texts.upload?.uploading || 'Uploading...'}</p>
			</div>
		{:else}
			<input
				type="file"
				accept=".epub"
				class="hidden"
				id="file-input"
				onchange={handleInputChange}
			/>
			<label for="file-input" class="cursor-pointer block">
				<div class="flex flex-col items-center">
					<div class="w-16 h-16 mb-5 rounded-full bg-fill-tertiary flex items-center justify-center">
						<svg class="w-7 h-7 text-label-secondary" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
							<path stroke-linecap="round" stroke-linejoin="round" d="M12 16.5V9.75m0 0l3 3m-3-3l-3 3M6.75 19.5a4.5 4.5 0 01-1.41-8.775 5.25 5.25 0 0110.233-2.33 3 3 0 013.758 3.848A3.752 3.752 0 0118 19.5H6.75z" />
						</svg>
					</div>
					<p class="text-body font-medium text-label-primary mb-1">{texts.upload?.title || 'Select EPUB File'}</p>
					<p class="text-footnote text-label-secondary">{texts.upload?.description || 'or drag and drop here'}</p>
				</div>
			</label>
		{/if}
	</div>

	{#if error}
		<div class="px-5 py-3 bg-accent-red/5 border-t border-accent-red/10">
			<p class="text-footnote text-accent-red text-center">{error}</p>
		</div>
	{/if}
</div>
