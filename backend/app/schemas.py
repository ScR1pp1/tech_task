from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class SlideBase(BaseModel):
    order: int
    title: str
    body: str
    footer: str | None = None


class SlideCreate(SlideBase):
    pass


class SlideUpdate(BaseModel):
    title: str | None = None
    body: str | None = None
    footer: str | None = None


class SlideOut(SlideBase):
    id: int

    class Config:
        from_attributes = True


class CarouselBase(BaseModel):
    title: str = Field(..., max_length=255)
    language: str = "ru"
    slides_count: int = 8
    style_hint: str | None = None
    source_type: str = "text"
    source_payload: dict[str, Any] | None = None
    design: dict[str, Any] | None = None


class CarouselCreate(CarouselBase):
    pass


class CarouselUpdate(BaseModel):
    title: str | None = None
    language: str | None = None
    slides_count: int | None = None
    style_hint: str | None = None
    design: dict[str, Any] | None = None


class CarouselOut(CarouselBase):
    id: int
    created_at: datetime
    status: str

    class Config:
        from_attributes = True


class GenerationCreate(BaseModel):
    carousel_id: int


class GenerationOut(BaseModel):
    id: int
    carousel_id: int
    status: str
    created_at: datetime
    error: str | None = None

    class Config:
        from_attributes = True


class ExportCreate(BaseModel):
    carousel_id: int


class ExportOut(BaseModel):
    id: int
    carousel_id: int
    status: str
    created_at: datetime
    url: str | None = None
    error: str | None = None

    class Config:
        from_attributes = True

