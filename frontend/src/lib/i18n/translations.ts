export const translations = {
	ko: {
		app: {
			title: 'EPUB 번역',
			poweredBy: 'Powered by Ollama'
		},
		upload: {
			title: 'EPUB 파일 선택',
			description: '또는 여기에 파일을 드래그하세요',
			uploading: '업로드 중...',
			errorInvalidFile: 'EPUB 파일만 지원됩니다',
			errorUploadFailed: '업로드 실패'
		},
		file: {
			chapters: '개의 챕터',
			change: '변경'
		},
		settings: {
			sourceLanguage: '원본 언어',
			targetLanguage: '번역 언어',
			aiModel: 'AI 모델',
			loading: '로딩 중...',
			noModels: '모델 없음'
		},
		ollama: {
			installRequired: 'Ollama 설치 필요',
			installDescription: '번역 기능을 사용하려면 Ollama가 필요합니다',
			installButton: 'ollama.com에서 설치',
			startRequired: 'Ollama 실행 필요',
			startDescription: '서버가 실행되지 않고 있습니다',
			startButton: 'Ollama 시작하기',
			starting: '시작 중...',
			statusError: '상태 확인 실패',
			startError: '시작 실패'
		},
		translate: {
			button: '번역하기',
			translating: '번역 중',
			cancel: '취소',
			preprocessing: '전처리 중...',
			analyzing: '분석 중...',
			generating: '파일 생성 중...',
			remaining: '남음',
			chapter: '챕터',
			chunk: '청크',
			original: '원문',
			translated: '번역'
		},
		complete: {
			title: '번역 완료',
			description: '파일이 준비되었습니다',
			download: '다운로드',
			newFile: '새 파일 번역'
		},
		error: {
			title: '오류 발생',
			description: '번역 중 문제가 발생했습니다',
			retry: '다시 시도'
		},
		language: {
			system: '시스템 언어',
			ko: '한국어',
			en: 'English'
		}
	},
	en: {
		app: {
			title: 'EPUB Translator',
			poweredBy: 'Powered by Ollama'
		},
		upload: {
			title: 'Select EPUB File',
			description: 'or drag and drop here',
			uploading: 'Uploading...',
			errorInvalidFile: 'Only EPUB files are supported',
			errorUploadFailed: 'Upload failed'
		},
		file: {
			chapters: ' chapters',
			change: 'Change'
		},
		settings: {
			sourceLanguage: 'Source Language',
			targetLanguage: 'Target Language',
			aiModel: 'AI Model',
			loading: 'Loading...',
			noModels: 'No models'
		},
		ollama: {
			installRequired: 'Ollama Required',
			installDescription: 'Ollama is required to use the translation feature',
			installButton: 'Install from ollama.com',
			startRequired: 'Ollama Not Running',
			startDescription: 'The server is not running',
			startButton: 'Start Ollama',
			starting: 'Starting...',
			statusError: 'Status check failed',
			startError: 'Failed to start'
		},
		translate: {
			button: 'Translate',
			translating: 'Translating',
			cancel: 'Cancel',
			preprocessing: 'Preprocessing...',
			analyzing: 'Analyzing...',
			generating: 'Generating file...',
			remaining: 'remaining',
			chapter: 'Chapter',
			chunk: 'Chunk',
			original: 'Original',
			translated: 'Translated'
		},
		complete: {
			title: 'Translation Complete',
			description: 'Your file is ready',
			download: 'Download',
			newFile: 'Translate New File'
		},
		error: {
			title: 'Error Occurred',
			description: 'A problem occurred during translation',
			retry: 'Try Again'
		},
		language: {
			system: 'System Language',
			ko: '한국어',
			en: 'English'
		}
	}
} as const;

export type Locale = keyof typeof translations;

type DeepReadonly<T> = {
	readonly [P in keyof T]: T[P] extends object ? DeepReadonly<T[P]> : T[P];
};

export type TranslationKeys = DeepReadonly<{
	app: { title: string; poweredBy: string };
	upload: { title: string; description: string; uploading: string; errorInvalidFile: string; errorUploadFailed: string };
	file: { chapters: string; change: string };
	settings: { sourceLanguage: string; targetLanguage: string; aiModel: string; loading: string; noModels: string };
	ollama: { installRequired: string; installDescription: string; installButton: string; startRequired: string; startDescription: string; startButton: string; starting: string; statusError: string; startError: string };
	translate: { button: string; translating: string; cancel: string; preprocessing: string; analyzing: string; generating: string; remaining: string; chapter: string; chunk: string; original: string; translated: string };
	complete: { title: string; description: string; download: string; newFile: string };
	error: { title: string; description: string; retry: string };
	language: { system: string; ko: string; en: string };
}>;
