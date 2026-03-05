from __future__ import annotations

import json
from typing import Any

import httpx
from pydantic import ValidationError

from .schemas import SlideCreate
from .settings import settings

async def _call_llm(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Реальный вызов LLM API (OpenAI-compatible)"""
    
    prompt = f"""Generate an Instagram carousel with {payload.get('slides_count', 8)} slides.
Language: {payload.get('language', 'en')}
Style: {payload.get('style_hint', '')}
Source text: {payload.get('source_payload', {}).get('source_text', '')}

Return a JSON array of slides, each with:
- order (integer)
- title (short, max 60 chars)
- body (main text, max 280 chars)
- footer (optional CTA, max 40 chars)

Example:
[
  {{"order": 1, "title": "Tip 1", "body": "Content here...", "footer": "Save this!"}},
  ...
]"""

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.llm_api_base}/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.llm_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.llm_model,
                "messages": [
                    {"role": "system", "content": "You are a social media content creator. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 2000,
            },
            timeout=30.0
        )
        
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        return json.loads(content)

async def generate_slides_for_carousel(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Обертка над LLM: несколько попыток + валидация JSON через Pydantic.
    """
    last_error: str | None = None
    
    if not settings.llm_api_key:
        return await _stub_llm_call(payload)
    
    for attempt in range(3):
        try:
            raw = await _call_llm(payload)
            validated = [SlideCreate(**item).model_dump() for item in raw]
            
            if len(validated) != payload.get("slides_count", 8):
                raise ValueError(f"Expected {payload.get('slides_count')} slides, got {len(validated)}")
                
            return validated
        except Exception as exc:
            last_error = str(exc)
            if attempt < 2:
                print(f"LLM attempt {attempt + 1} failed: {exc}")
            continue
            
    raise ValueError(f"Invalid LLM slides payload after retries: {last_error}")

async def _stub_llm_call(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Заглушка для разработки"""
    title = payload.get("title") or "Carousel"
    slides_count = int(payload.get("slides_count") or 8)

    slides: list[dict[str, Any]] = []
    for i in range(1, slides_count + 1):
        slides.append(
            {
                "order": i,
                "title": f"{title} — Slide {i}",
                "body": f"Auto-generated body for slide {i}. Replace with real LLM output.",
                "footer": None if i < slides_count else "Follow for more!",
            }
        )
    return slides