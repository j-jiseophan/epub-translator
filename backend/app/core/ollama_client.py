import asyncio
import httpx
from typing import Optional


class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=300.0)
        self._current_request: asyncio.Task | None = None

    async def list_models(self) -> list[str]:
        """Get list of available models."""
        response = await self.client.get(f"{self.base_url}/api/tags")
        response.raise_for_status()
        data = response.json()
        return [model["name"] for model in data.get("models", [])]

    async def translate(
        self,
        text: str,
        source_lang: str,
        target_lang: str,
        model: str,
        context: Optional[str] = None,
    ) -> str:
        """Translate text using Ollama."""
        system_prompt = f"""You are an expert literary translator specializing in {target_lang}.
Translate the following text from {source_lang} to {target_lang}.

Guidelines:
- Translate naturally so that native {target_lang} speakers can read it fluently.
- Use idiomatic expressions and natural phrasing in {target_lang}, not literal word-for-word translation.
- Preserve the original meaning, tone, and intent while adapting cultural references if needed.
- Maintain paragraph structure and formatting.
- Only output the translated text, nothing else.
- Do not add explanations, notes, or translator comments."""

        user_prompt = text
        if context:
            user_prompt = f"Context: {context}\n\nText to translate:\n{text}"

        response = await self.client.post(
            f"{self.base_url}/api/generate",
            json={
                "model": model,
                "prompt": user_prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                },
            },
        )
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()

    async def unload_model(self, model: str) -> bool:
        """Unload a model from memory by setting keep_alive to 0."""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": model,
                    "prompt": "",
                    "keep_alive": 0,
                },
            )
            response.raise_for_status()
            return True
        except Exception:
            return False

    async def close(self):
        await self.client.aclose()
