const API_BASE = 'http://localhost:8000';
const WS_BASE = 'ws://localhost:8000';

export interface Language {
	code: string;
	name: string;
}

export interface OllamaStatus {
	installed: boolean;
	running: boolean;
}

export interface UploadResponse {
	file_id: string;
	filename: string;
	file_size: number;
	chapter_count: number;
}

export interface TranslateParams {
	file_id: string;
	source_language: string;
	target_language: string;
	model: string;
}

export interface ProgressMessage {
	type: string;
	job_id: string;
	status: string;
	chapter_current: number;
	chapter_total: number;
	chapter_title: string;
	chunk_current: number;
	chunk_total: number;
	percentage: number;
	estimated_time_remaining: number;
	preview_original: string;
	preview_translated: string;
	error_message?: string;
	download_url?: string;
}

export async function getOllamaStatus(): Promise<OllamaStatus> {
	const response = await fetch(`${API_BASE}/api/ollama/status`);
	const data = await response.json();
	return data;
}

export async function startOllama(): Promise<{ success: boolean }> {
	const response = await fetch(`${API_BASE}/api/ollama/start`, {
		method: 'POST'
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail || 'Failed to start Ollama');
	}

	return response.json();
}

export async function getModels(): Promise<string[]> {
	const response = await fetch(`${API_BASE}/api/models`);
	const data = await response.json();
	return data.models;
}

export async function getLanguages(): Promise<Language[]> {
	const response = await fetch(`${API_BASE}/api/languages`);
	const data = await response.json();
	return data.languages;
}

export async function uploadFile(file: File): Promise<UploadResponse> {
	const formData = new FormData();
	formData.append('file', file);

	const response = await fetch(`${API_BASE}/api/upload`, {
		method: 'POST',
		body: formData
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail || 'Upload failed');
	}

	return response.json();
}

export async function startTranslation(params: TranslateParams): Promise<{ job_id: string }> {
	const response = await fetch(`${API_BASE}/api/translate`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(params)
	});

	if (!response.ok) {
		const error = await response.json();
		throw new Error(error.detail || 'Failed to start translation');
	}

	return response.json();
}

export async function cancelJob(jobId: string): Promise<void> {
	await fetch(`${API_BASE}/api/job/${jobId}`, {
		method: 'DELETE'
	});
}

export function getDownloadUrl(jobId: string): string {
	return `${API_BASE}/api/download/${jobId}`;
}

export function connectWebSocket(
	jobId: string,
	onMessage: (msg: ProgressMessage) => void,
	onError?: (error: Event) => void
): WebSocket {
	const ws = new WebSocket(`${WS_BASE}/ws/progress/${jobId}`);

	ws.onmessage = (event) => {
		const message = JSON.parse(event.data);
		onMessage(message);
	};

	ws.onerror = (error) => {
		console.error('WebSocket error:', error);
		onError?.(error);
	};

	const pingInterval = setInterval(() => {
		if (ws.readyState === WebSocket.OPEN) {
			ws.send('ping');
		}
	}, 30000);

	ws.onclose = () => {
		clearInterval(pingInterval);
	};

	return ws;
}
