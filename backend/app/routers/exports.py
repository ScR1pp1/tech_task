from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models import Carousel, Export, ExportStatusEnum
from ..schemas import ExportCreate, ExportOut

router = APIRouter()


@router.post("", response_model=ExportOut, status_code=status.HTTP_202_ACCEPTED)
async def start_export(
    payload: ExportCreate,
    session: AsyncSession = Depends(get_session),
) -> ExportOut:
    carousel = await session.get(Carousel, payload.carousel_id)
    if not carousel:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carousel not found")

    export = Export(carousel_id=carousel.id, status=ExportStatusEnum.done.value, url=None)
    session.add(export)
    await session.commit()
    await session.refresh(export)

    # Для MVP экспорт пока заглушка: фронт будет сам рендерить PNG.
    return ExportOut.model_validate(export)


@router.get("/{export_id}", response_model=ExportOut)
async def get_export(
    export_id: int,
    session: AsyncSession = Depends(get_session),
) -> ExportOut:
    export = await session.get(Export, export_id)
    if not export:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export not found")
    return ExportOut.model_validate(export)

