from typing import AsyncGenerator, Sequence
import asyncio

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel

from ..db import get_session
from ..models import Carousel, CarouselStatusEnum, Generation, GenerationStatusEnum, Slide
from ..schemas import GenerationCreate, GenerationOut
from ..services_llm import generate_slides_for_carousel
from ..settings import settings

router = APIRouter()

# ===== МОДЕЛЬ ДЛЯ ОЦЕНКИ ТОКЕНОВ =====
class TokenEstimateRequest(BaseModel):
    source_text: str | None = None
    slides_count: int = 8
    language: str = "ru"
    style_hint: str | None = None

class TokenEstimateResponse(BaseModel):
    estimated_input_tokens: int
    estimated_output_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    model: str
    details: dict

# ===== ЭНДПОИНТ ОЦЕНКИ ТОКЕНОВ =====
@router.post("/token-estimate", response_model=TokenEstimateResponse)
async def estimate_tokens(payload: TokenEstimateRequest):
    """
    Оценивает количество токенов и стоимость генерации
    Поддерживает различные модели включая Llama-4
    """
    # Простая эвристика для оценки токенов
    # В реальности можно использовать tiktoken или аналоги
    
    # Оценка входных токенов
    input_text = f"{payload.source_text or ''} {payload.style_hint or ''}"
    # Грубая оценка: 1 токен ≈ 4 символа для английского, больше для русского
    char_count = len(input_text)
    lang_multiplier = 1.3 if payload.language == 'ru' else 1.0
    input_tokens = int(char_count / 3.5 * lang_multiplier) + 200  # +200 на промпт
    
    # Оценка выходных токенов
    # Каждый слайд: title (20-60 токенов) + body (50-150 токенов)
    output_tokens_per_slide = 150
    output_tokens = payload.slides_count * output_tokens_per_slide
    
    # Цены для разных моделей (за 1M токенов)
    # Актуальные цены на 2026 год
    pricing = {
        # OpenAI
        'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
        'gpt-4o': {'input': 2.50, 'output': 10.00},
        'gpt-3.5-turbo': {'input': 0.50, 'output': 1.50},
        
        # xAI (Grok)
        'grok-2-latest': {'input': 2.00, 'output': 10.00},
        'grok-2-1212': {'input': 2.00, 'output': 10.00},
        'grok-1': {'input': 1.00, 'output': 3.00},
        
        # Anthropic
        'claude-3-opus': {'input': 15.00, 'output': 75.00},
        'claude-3-sonnet': {'input': 3.00, 'output': 15.00},
        'claude-3-haiku': {'input': 0.25, 'output': 1.25},
        
        # Meta Llama (через различные провайдеры)
        'meta-llama/llama-4-scout-17b-16e-instruct': {'input': 0.80, 'output': 2.40},  # 17B параметров
        'meta-llama/llama-4-maverick-17b-16e-instruct': {'input': 1.20, 'output': 3.60},
        'meta-llama/llama-3-70b-instruct': {'input': 0.90, 'output': 2.70},
        'meta-llama/llama-3-8b-instruct': {'input': 0.20, 'output': 0.60},
        
        # Google
        'gemini-1.5-pro': {'input': 2.50, 'output': 7.50},
        'gemini-1.5-flash': {'input': 0.35, 'output': 1.05},
        
        # DeepSeek
        'deepseek-chat': {'input': 0.14, 'output': 0.28},
        
        # Mistral AI
        'mistral-large': {'input': 2.00, 'output': 6.00},
        'mistral-medium': {'input': 1.00, 'output': 3.00},
        'mistral-small': {'input': 0.20, 'output': 0.60},
        
        # Cohere
        'command-r-plus': {'input': 3.00, 'output': 15.00},
        'command-r': {'input': 0.50, 'output': 1.50},
    }
    
    model = settings.llm_model
    
    # Проверяем, есть ли точное совпадение
    if model in pricing:
        model_pricing = pricing[model]
        model_display = model
    else:
        # Пытаемся найти по частичному совпадению
        matched = False
        for key in pricing:
            if key in model or model in key:
                model_pricing = pricing[key]
                model_display = f"{model} (≈ {key})"
                matched = True
                break
        
        # Если не нашли, используем цены GPT-4o-mini как базовые
        if not matched:
            model_pricing = pricing['gpt-4o-mini']
            model_display = f"{model} (estimated)"
    
    # Стоимость в долларах
    input_cost = (input_tokens / 1_000_000) * model_pricing['input']
    output_cost = (output_tokens / 1_000_000) * model_pricing['output']
    total_cost = input_cost + output_cost
    
    # Детальная информация о модели Llama-4
    llama4_details = {}
    if 'llama-4' in model.lower():
        llama4_details = {
            'architecture': 'Mixture of Experts (MoE)',
            'parameters': '17B active / 109B total',
            'context_length': '1M tokens',
            'knowledge_cutoff': 'August 2024',
            'multilingual': True,
            'supported_languages': ['English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese', 'Dutch', 'Russian', 'Chinese', 'Japanese', 'Korean', 'Arabic'],
            'provider': 'Meta AI via Together.ai/Replicate/Perplexity/etc'
        }
    
    return TokenEstimateResponse(
        estimated_input_tokens=input_tokens,
        estimated_output_tokens=output_tokens,
        total_tokens=input_tokens + output_tokens,
        estimated_cost_usd=round(total_cost, 4),
        model=model_display,
        details={
            'pricing_model': model,
            'input_rate': model_pricing['input'],
            'output_rate': model_pricing['output'],
            'char_count': char_count,
            'slides': payload.slides_count,
            'language': payload.language,
            'llama4_info': llama4_details if llama4_details else None
        }
    )

# ===== СУЩЕСТВУЮЩИЙ КОД ГЕНЕРАЦИИ =====

async def _run_generation(generation_id: int, session: AsyncSession) -> None:
    """Фоновая задача генерации слайдов"""
    generation = await session.get(Generation, generation_id)
    if not generation:
        return

    carousel = await session.get(Carousel, generation.carousel_id)
    if not carousel:
        generation.status = GenerationStatusEnum.failed.value
        generation.error = "Carousel not found"
        await session.commit()
        return

    generation.status = GenerationStatusEnum.running.value
    carousel.status = CarouselStatusEnum.generating.value
    await session.commit()

    try:
        payload = {
            "title": carousel.title,
            "language": carousel.language,
            "slides_count": carousel.slides_count,
            "style_hint": carousel.style_hint,
            "source_type": carousel.source_type,
            "source_payload": carousel.source_payload,
        }
        
        # Логируем какую модель используем
        print(f"Generating with model: {settings.llm_model}")
        
        slides_payload = await generate_slides_for_carousel(payload)

        # очистить существующие слайды
        result = await session.execute(
            select(Slide).where(Slide.carousel_id == carousel.id)
        )
        existing: Sequence[Slide] = result.scalars().all()
        for s in existing:
            await session.delete(s)
        await session.flush()

        # создать новые слайды
        for s in slides_payload:
            slide = Slide(
                carousel_id=carousel.id,
                order=s["order"],
                title=s["title"],
                body=s["body"],
                footer=s.get("footer"),
            )
            session.add(slide)

        generation.status = GenerationStatusEnum.done.value
        carousel.status = CarouselStatusEnum.ready.value
        await session.commit()
    except Exception as exc:  # noqa: BLE001
        generation.status = GenerationStatusEnum.failed.value
        carousel.status = CarouselStatusEnum.failed.value
        generation.error = str(exc)
        await session.commit()
        # Логируем ошибку
        print(f"Generation failed: {exc}")


@router.post("", response_model=GenerationOut, status_code=status.HTTP_202_ACCEPTED)
async def start_generation(
    payload: GenerationCreate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
) -> GenerationOut:
    """Запуск генерации для карусели"""
    carousel = await session.get(Carousel, payload.carousel_id)
    if not carousel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carousel not found")

    generation = Generation(carousel_id=carousel.id)
    session.add(generation)
    await session.commit()
    await session.refresh(generation)

    # run background task
    background_tasks.add_task(_run_generation, generation.id, session)

    return GenerationOut.model_validate(generation)


@router.get("/{generation_id}", response_model=GenerationOut)
async def get_generation(
    generation_id: int,
    session: AsyncSession = Depends(get_session),
) -> GenerationOut:
    """Получить статус генерации"""
    generation = await session.get(Generation, generation_id)
    if not generation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation not found")
    return GenerationOut.model_validate(generation)


@router.get("/by-carousel/{carousel_id}", response_model=list[GenerationOut])
async def list_generations_for_carousel(
    carousel_id: int,
    session: AsyncSession = Depends(get_session),
) -> list[GenerationOut]:
    """Список генераций для карусели"""
    result = await session.execute(
        select(Generation)
        .where(Generation.carousel_id == carousel_id)
        .order_by(Generation.created_at.desc())
    )
    gens = result.scalars().all()
    return [GenerationOut.model_validate(g) for g in gens]


@router.get("/{generation_id}/events")
async def generation_events(
    generation_id: int,
    session: AsyncSession = Depends(get_session),
) -> EventSourceResponse:
    """SSE события для отслеживания статуса генерации"""
    async def event_generator() -> AsyncGenerator[dict, None]:
        while True:
            generation = await session.get(Generation, generation_id)
            if not generation:
                yield {"event": "error", "data": "not-found"}
                break
            yield {"event": "status", "data": generation.status}
            if generation.status in {GenerationStatusEnum.done.value, GenerationStatusEnum.failed.value}:
                break
            await asyncio.sleep(2)

    return EventSourceResponse(event_generator())