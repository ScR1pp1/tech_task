from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import html
import textwrap

from ..db import get_session
from ..models import Carousel, Slide

router = APIRouter(prefix="/preview", tags=["preview"])

@router.get("/{carousel_id}")
async def get_carousel_preview(
    carousel_id: int,
    session: AsyncSession = Depends(get_session)
) -> Response:
    """Генерирует SVG превью первого слайда карусели"""
    
    # Получаем карусель и первый слайд
    carousel = await session.get(Carousel, carousel_id)
    if not carousel:
        raise HTTPException(status_code=404, detail="Carousel not found")
    
    result = await session.execute(
        select(Slide).where(Slide.carousel_id == carousel_id).order_by(Slide.order).limit(1)
    )
    first_slide = result.scalar_one_or_none()
    
    if not first_slide:
        # Если нет слайдов, показываем заглушку
        svg = generate_placeholder_svg(carousel.title)
        return Response(content=svg, media_type="image/svg+xml")
    
    # Генерируем SVG с первым слайдом
    svg = generate_slide_preview(
        title=first_slide.title,
        body=first_slide.body,
        footer=first_slide.footer,
        design=carousel.design or {}
    )
    
    return Response(content=svg, media_type="image/svg+xml")

def generate_slide_preview(title: str, body: str, footer: str | None, design: dict) -> str:
    """Генерирует SVG миниатюру слайда"""
    
    # Обрезаем длинные тексты
    title = textwrap.shorten(title, width=40, placeholder="...")
    body = textwrap.shorten(body, width=100, placeholder="...")
    
    # Цвета из дизайна или по умолчанию
    bg_color = design.get('bgColor', '#020617')
    text_color = '#e5e7eb'
    
    # Экранируем для XML
    title = html.escape(title)
    body = html.escape(body)
    footer = html.escape(footer) if footer else ""
    
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="500" viewBox="0 0 400 500" xmlns="http://www.w3.org/2000/svg">
    <rect width="400" height="500" fill="{bg_color}" />
    
    <!-- Градиентный оверлей -->
    <defs>
        <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="black" stop-opacity="0.3"/>
            <stop offset="100%" stop-color="black" stop-opacity="0.6"/>
        </linearGradient>
    </defs>
    <rect width="400" height="500" fill="url(#grad)" opacity="0.4" />
    
    <!-- Контент -->
    <text x="30" y="80" font-family="system-ui, -apple-system, sans-serif" font-size="18" font-weight="bold" fill="{text_color}">
        {title}
    </text>
    
    <text x="30" y="130" font-family="system-ui, sans-serif" font-size="14" fill="{text_color}" opacity="0.9">
        <tspan x="30" dy="0">{body[:50]}</tspan>
        <tspan x="30" dy="20">{body[50:100] if len(body) > 50 else ''}</tspan>
    </text>
    
    {f'<text x="30" y="450" font-family="system-ui, sans-serif" font-size="12" fill="{text_color}" opacity="0.7">{footer}</text>' if footer else ''}
    
    <!-- Индикатор слайдов -->
    <circle cx="350" cy="450" r="15" fill="#8b5cf6" opacity="0.8" />
    <text x="350" y="455" font-size="12" fill="white" text-anchor="middle">1</text>
</svg>'''

def generate_placeholder_svg(title: str) -> str:
    """Генерирует SVG заглушку"""
    title = html.escape(textwrap.shorten(title, width=30, placeholder="..."))
    
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="400" height="500" viewBox="0 0 400 500" xmlns="http://www.w3.org/2000/svg">
    <rect width="400" height="500" fill="#1e293b" />
    <rect width="400" height="500" fill="url(#pattern)" opacity="0.1" />
    
    <defs>
        <pattern id="pattern" patternUnits="userSpaceOnUse" width="40" height="40">
            <path d="M0 20 L40 20 M20 0 L20 40" stroke="#475569" stroke-width="1"/>
        </pattern>
    </defs>
    
    <text x="200" y="250" font-family="system-ui, sans-serif" font-size="16" fill="#94a3b8" text-anchor="middle">
        {title}
    </text>
    <text x="200" y="280" font-family="system-ui, sans-serif" font-size="12" fill="#64748b" text-anchor="middle">
        No slides yet
    </text>
</svg>'''