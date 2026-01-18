import { writable } from 'svelte/store';

export type TranslationStatus =
	| 'idle'
	| 'uploading'
	| 'ready'
	| 'parsing'
	| 'translating'
	| 'rebuilding'
	| 'completed'
	| 'failed'
	| 'cancelled';

export interface TranslationState {
	fileId: string | null;
	fileName: string | null;
	chapterCount: number;
	jobId: string | null;
	status: TranslationStatus;
	sourceLanguage: string;
	targetLanguage: string;
	selectedModel: string;
	progress: {
		chapterCurrent: number;
		chapterTotal: number;
		chapterTitle: string;
		chunkCurrent: number;
		chunkTotal: number;
		percentage: number;
		estimatedTimeRemaining: number;
		previewOriginal: string;
		previewTranslated: string;
	};
	error: string | null;
	downloadUrl: string | null;
}

const initialState: TranslationState = {
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
};

function createTranslationStore() {
	const { subscribe, set, update } = writable<TranslationState>(initialState);

	return {
		subscribe,
		setFile: (fileId: string, fileName: string, chapterCount: number) =>
			update((s) => ({
				...s,
				fileId,
				fileName,
				chapterCount,
				status: 'ready'
			})),
		setSourceLanguage: (lang: string) =>
			update((s) => ({
				...s,
				sourceLanguage: lang
			})),
		setTargetLanguage: (lang: string) =>
			update((s) => ({
				...s,
				targetLanguage: lang
			})),
		setModel: (model: string) =>
			update((s) => ({
				...s,
				selectedModel: model
			})),
		startTranslation: (jobId: string) =>
			update((s) => ({
				...s,
				jobId,
				status: 'translating',
				error: null
			})),
		setStatus: (status: TranslationStatus) =>
			update((s) => ({
				...s,
				status
			})),
		updateProgress: (progress: Partial<TranslationState['progress']>) =>
			update((s) => ({
				...s,
				progress: { ...s.progress, ...progress }
			})),
		setCompleted: (downloadUrl: string) =>
			update((s) => ({
				...s,
				status: 'completed',
				downloadUrl
			})),
		setFailed: (error: string) =>
			update((s) => ({
				...s,
				status: 'failed',
				error
			})),
		reset: () => set(initialState)
	};
}

export const translationStore = createTranslationStore();
