# EPUB Translator Documentation

로컬 Ollama를 활용한 EPUB 파일 번역 도구

## 개요

EPUB 파일을 원하는 언어로 번역하는 웹 기반 도구입니다. OpenAI 등 외부 API 대신 로컬에 설치된 Ollama를 사용하여 프라이버시를 보호하고 비용 없이 번역할 수 있습니다.

### 주요 기능

- **다국어 번역**: 영어, 한국어, 일본어, 중국어 등 10개 언어 지원
- **Ollama 모델 선택**: 로컬에 설치된 모든 Ollama 모델 사용 가능
- **실시간 진행률**: WebSocket을 통한 번역 진행 상황 실시간 표시
- **EPUB 구조 보존**: 원본 EPUB의 챕터 구조, 스타일, 이미지 등 유지
- **간단한 웹 UI**: 드래그 앤 드롭으로 쉬운 파일 업로드

---

## 기술 스택

### Backend
- **FastAPI**: Python 비동기 웹 프레임워크
- **uvicorn**: ASGI 서버 (WebSocket 지원)
- **ebooklib**: EPUB 파일 파싱 및 생성
- **BeautifulSoup4 + lxml**: HTML 콘텐츠 처리
- **httpx**: Ollama API 비동기 호출

### Frontend
- **Svelte 5**: 반응형 UI 프레임워크
- **SvelteKit**: 풀스택 프레임워크
- **TailwindCSS**: 유틸리티 기반 CSS
- **TypeScript**: 타입 안전성

### 통신
- **REST API**: 파일 업로드, 번역 시작, 다운로드
- **WebSocket**: 실시간 진행률 업데이트

---

## 프로젝트 구조

```
epub-translator/
├── start.sh                    # 서버 시작 스크립트
├── README.md                   # 프로젝트 문서
│
├── backend/                    # Python FastAPI 백엔드
│   ├── requirements.txt        # Python 의존성
│   ├── uploads/                # 업로드된 EPUB 임시 저장
│   ├── outputs/                # 번역된 EPUB 저장
│   └── app/
│       ├── __init__.py
│       ├── main.py             # FastAPI 앱 진입점 및 라우트
│       ├── api/
│       │   ├── __init__.py
│       │   └── websocket.py    # WebSocket 연결 관리자
│       ├── core/
│       │   ├── __init__.py
│       │   ├── ollama_client.py   # Ollama API 클라이언트
│       │   ├── epub_parser.py     # EPUB 파싱/저장
│       │   ├── chunker.py         # 텍스트 청킹
│       │   └── translator.py      # 번역 오케스트레이터
│       └── models/
│           ├── __init__.py
│           └── schemas.py      # Pydantic 스키마
│
└── frontend/                   # Svelte 프론트엔드
    ├── package.json
    ├── svelte.config.js
    ├── vite.config.ts
    ├── tailwind.config.js
    ├── tsconfig.json
    └── src/
        ├── app.html
        ├── app.css             # TailwindCSS 설정
        ├── routes/
        │   ├── +layout.svelte
        │   └── +page.svelte    # 메인 페이지
        └── lib/
            ├── api/
            │   └── client.ts   # API 클라이언트
            ├── stores/
            │   └── translation.ts  # 상태 관리
            └── components/
                ├── FileUpload.svelte       # 파일 업로드
                ├── LanguageSelector.svelte # 언어 선택
                ├── ModelSelector.svelte    # 모델 선택
                └── ProgressDisplay.svelte  # 진행률 표시
```

---

## API 설계

### REST 엔드포인트

| Method | Endpoint | 설명 | 요청 | 응답 |
|--------|----------|------|------|------|
| `GET` | `/api/models` | Ollama 모델 목록 조회 | - | `{ models: string[] }` |
| `GET` | `/api/languages` | 지원 언어 목록 조회 | - | `{ languages: Language[] }` |
| `POST` | `/api/upload` | EPUB 파일 업로드 | `multipart/form-data` | `FileUploadResponse` |
| `POST` | `/api/translate` | 번역 작업 시작 | `TranslationRequest` | `{ job_id: string }` |
| `GET` | `/api/job/{job_id}` | 작업 상태 조회 | - | `JobStatusResponse` |
| `DELETE` | `/api/job/{job_id}` | 작업 취소 | - | `{ success: bool }` |
| `GET` | `/api/download/{job_id}` | 번역된 EPUB 다운로드 | - | EPUB 파일 |

### WebSocket 엔드포인트

| Endpoint | 설명 |
|----------|------|
| `WS /ws/progress/{job_id}` | 번역 진행률 실시간 업데이트 |

### 데이터 스키마

```python
# 번역 요청
class TranslationRequest:
    file_id: str           # 업로드된 파일 ID
    source_language: str   # 원본 언어 코드 (예: "en")
    target_language: str   # 대상 언어 코드 (예: "ko")
    model: str             # Ollama 모델명

# 진행률 메시지 (WebSocket)
class ProgressMessage:
    type: str              # "progress"
    job_id: str
    status: str            # pending, parsing, translating, rebuilding, completed, failed
    chapter_current: int   # 현재 챕터 번호
    chapter_total: int     # 전체 챕터 수
    chapter_title: str     # 현재 챕터 제목
    chunk_current: int     # 현재 청크 번호
    chunk_total: int       # 전체 청크 수
    percentage: float      # 진행률 (0-100)
    preview_original: str  # 원문 미리보기
    preview_translated: str # 번역문 미리보기
```

---

## 핵심 모듈 설명

### 1. Ollama 클라이언트 (`ollama_client.py`)

Ollama API와 통신하는 비동기 클라이언트입니다.

```python
class OllamaClient:
    async def list_models() -> list[str]
        # 사용 가능한 모델 목록 조회

    async def translate(text, source_lang, target_lang, model) -> str
        # 텍스트 번역 수행
```

**번역 프롬프트 전략:**
- 시스템 프롬프트로 전문 번역가 역할 부여
- 원문의 포맷, 톤 유지 지시
- temperature 0.3으로 일관된 번역 품질 확보

### 2. EPUB 파서 (`epub_parser.py`)

EPUB 파일의 구조를 분석하고 번역 가능한 텍스트를 추출합니다.

```python
class EPUBParser:
    def get_chapters() -> List[Chapter]
        # 모든 챕터(문서) 추출

    def apply_translations(item, translations)
        # 번역된 텍스트를 원본 HTML에 적용

    def save(output_path)
        # 번역된 EPUB 저장
```

**번역 대상 태그:**
- `<p>`, `<h1>`~`<h6>`: 본문 및 제목
- `<li>`, `<td>`, `<th>`: 목록 및 표
- `<figcaption>`, `<blockquote>`: 캡션 및 인용
- `<title>`: 문서 제목

### 3. 텍스트 청커 (`chunker.py`)

LLM의 토큰 제한을 고려하여 텍스트를 적절한 크기로 분할합니다.

```python
class TextChunker:
    def chunk_elements(elements) -> List[TranslationChunk]
        # 요소들을 청크로 그룹화

    def parse_translated_chunk(chunk, translated) -> dict
        # 번역된 청크를 개별 요소로 분리
```

**청킹 전략:**
- 최대 2000자(약 500 토큰) 단위로 분할
- 문단 단위 유지 (중간에서 자르지 않음)
- 번호 마커(`[0]`, `[1]`, ...)로 요소 구분

### 4. 번역 오케스트레이터 (`translator.py`)

전체 번역 파이프라인을 조율하고 진행 상황을 보고합니다.

```python
class TranslationOrchestrator:
    async def run() -> str
        # 전체 번역 실행, 출력 경로 반환

    def cancel()
        # 번역 작업 취소
```

**번역 파이프라인:**
1. **Parsing**: EPUB 파싱, 챕터 및 요소 추출
2. **Translating**: 청크 단위로 Ollama 번역 수행
3. **Rebuilding**: 번역된 텍스트를 원본 구조에 적용
4. **Completed**: 새 EPUB 파일 저장

**에러 처리:**
- 최대 3회 재시도 (지수 백오프)
- 취소 가능한 비동기 작업

### 5. WebSocket 관리자 (`websocket.py`)

작업별 WebSocket 연결을 관리하고 진행률을 브로드캐스트합니다.

```python
class ConnectionManager:
    async def connect(websocket, job_id)
        # 연결 수락 및 작업에 등록

    async def broadcast_to_job(job_id, message)
        # 해당 작업의 모든 클라이언트에 메시지 전송
```

---

## 프론트엔드 컴포넌트

### 상태 관리 (`translation.ts`)

Svelte 스토어를 사용한 전역 상태 관리:

```typescript
interface TranslationState {
    fileId: string | null      // 업로드된 파일 ID
    fileName: string | null    // 파일명
    chapterCount: number       // 챕터 수
    jobId: string | null       // 번역 작업 ID
    status: TranslationStatus  // 현재 상태
    sourceLanguage: string     // 원본 언어
    targetLanguage: string     // 대상 언어
    selectedModel: string      // 선택된 모델
    progress: {...}            // 진행률 정보
    error: string | null       // 에러 메시지
    downloadUrl: string | null // 다운로드 URL
}
```

### 컴포넌트 흐름

```
+page.svelte (메인)
│
├─ [status: idle]
│  └─ FileUpload.svelte
│     └─ 드래그앤드롭 또는 클릭으로 EPUB 업로드
│
├─ [status: ready]
│  ├─ 파일 정보 표시
│  ├─ LanguageSelector.svelte (source)
│  ├─ LanguageSelector.svelte (target)
│  ├─ ModelSelector.svelte
│  └─ "Start Translation" 버튼
│
├─ [status: translating]
│  └─ ProgressDisplay.svelte
│     ├─ 전체 진행률 바
│     ├─ 챕터/청크 카운터
│     └─ 원문/번역문 미리보기
│
├─ [status: completed]
│  ├─ 완료 메시지
│  ├─ "Download EPUB" 버튼
│  └─ "Translate Another" 버튼
│
└─ [status: failed]
   ├─ 에러 메시지
   └─ "Try Again" 버튼
```

---

## 지원 언어

| 코드 | 언어 |
|------|------|
| en | English |
| ko | Korean (한국어) |
| ja | Japanese (日本語) |
| zh | Chinese (中文) |
| es | Spanish (Español) |
| fr | French (Français) |
| de | German (Deutsch) |
| it | Italian (Italiano) |
| pt | Portuguese (Português) |
| ru | Russian (Русский) |

---

## 사용 가능한 Ollama 모델

현재 시스템에 설치된 모델:

| 모델 | 크기 | 용도 |
|------|------|------|
| `translategemma:4b` | 3.3 GB | 번역 특화 모델 |
| `goekdenizguelmez/JOSIEFIED-Qwen3:8b` | 5.0 GB | 범용 모델 |
| `gemma3:12b` | 8.1 GB | 고품질 범용 모델 |

---

## 번역 품질 팁

1. **모델 선택**: `translategemma:4b`는 번역에 특화되어 있어 권장
2. **긴 문서**: 큰 EPUB 파일은 시간이 오래 걸릴 수 있음
3. **언어 쌍**: 영어 ↔ 타 언어 번역이 가장 품질이 좋음
4. **검토 필요**: AI 번역 결과는 항상 검토 권장

---

## 제한 사항

- 이미지 내 텍스트는 번역되지 않음
- 복잡한 레이아웃(표, 수식 등)은 일부 깨질 수 있음
- DRM이 적용된 EPUB는 지원하지 않음
- 매우 큰 파일(100MB+)은 메모리 문제가 발생할 수 있음

---

## 라이선스

MIT License

---

## 기여

버그 리포트, 기능 제안, PR 환영합니다!
