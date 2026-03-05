from typing import Sequence

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models import Carousel, Slide
from ..schemas import (
    CarouselCreate,
    CarouselOut,
    CarouselUpdate,
    SlideOut,
    SlideUpdate,
)

router = APIRouter()


@router.get("", response_model=list[CarouselOut])
async def list_carousels(
    session: AsyncSession = Depends(get_session),
) -> list[CarouselOut]:
    result = await session.execute(select(Carousel).order_by(Carousel.created_at.desc()))
    carousels: Sequence[Carousel] = result.scalars().all()
    return [CarouselOut.model_validate(c) for c in carousels]


@router.post("", response_model=CarouselOut, status_code=status.HTTP_201_CREATED)
async def create_carousel(
    payload: CarouselCreate,
    session: AsyncSession = Depends(get_session),
) -> CarouselOut:
    carousel = Carousel(**payload.model_dump())
    session.add(carousel)
    await session.commit()
    await session.refresh(carousel)
    return CarouselOut.model_validate(carousel)


@router.get("/{carousel_id}", response_model=CarouselOut)
async def get_carousel(
    carousel_id: int,
    session: AsyncSession = Depends(get_session),
) -> CarouselOut:
    carousel = await session.get(Carousel, carousel_id)
    if not carousel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carousel not found")
    return CarouselOut.model_validate(carousel)


@router.patch("/{carousel_id}", response_model=CarouselOut)
async def update_carousel(
    carousel_id: int,
    payload: CarouselUpdate,
    session: AsyncSession = Depends(get_session),
) -> CarouselOut:
    carousel = await session.get(Carousel, carousel_id)
    if not carousel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carousel not found")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(carousel, key, value)

    await session.commit()
    await session.refresh(carousel)
    return CarouselOut.model_validate(carousel)


@router.get("/{carousel_id}/slides", response_model=list[SlideOut])
async def list_slides(
    carousel_id: int,
    session: AsyncSession = Depends(get_session),
) -> list[SlideOut]:
    result = await session.execute(
        select(Slide).where(Slide.carousel_id == carousel_id).order_by(Slide.order)
    )
    slides = result.scalars().all()
    return [SlideOut.model_validate(s) for s in slides]


@router.patch("/{carousel_id}/slides/{slide_id}", response_model=SlideOut)
async def update_slide(
    carousel_id: int,
    slide_id: int,
    payload: SlideUpdate,
    session: AsyncSession = Depends(get_session),
) -> SlideOut:
    slide = await session.get(Slide, slide_id)
    if not slide or slide.carousel_id != carousel_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Slide not found")

    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(slide, key, value)

    await session.commit()
    await session.refresh(slide)
    return SlideOut.model_validate(slide)


@router.delete("/{carousel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_carousel(
    carousel_id: int,
    session: AsyncSession = Depends(get_session),
) -> None:
    """Удалить карусель"""
    carousel = await session.get(Carousel, carousel_id)
    if not carousel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carousel not found")
    
    await session.delete(carousel)
    await session.commit()


@router.post("/{carousel_id}/duplicate", response_model=CarouselOut)
async def duplicate_carousel(
    carousel_id: int,
    session: AsyncSession = Depends(get_session),
) -> CarouselOut:
    """Создать копию карусели"""
    original = await session.get(Carousel, carousel_id)
    if not original:
        raise HTTPException(status_code=404, detail="Carousel not found")
    
    # Копируем все поля кроме id и created_at
    copy_data = {
        "title": f"{original.title} (copy)",
        "language": original.language,
        "slides_count": original.slides_count,
        "style_hint": original.style_hint,
        "source_type": original.source_type,
        "source_payload": original.source_payload,
        "design": original.design,
        "status": "draft"
    }
    
    new_carousel = Carousel(**copy_data)
    session.add(new_carousel)
    await session.commit()
    await session.refresh(new_carousel)
    
    return CarouselOut.model_validate(new_carousel)

