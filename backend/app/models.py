from datetime import datetime
from enum import Enum

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class CarouselStatusEnum(str, Enum):
    draft = "draft"
    generating = "generating"
    ready = "ready"
    failed = "failed"


class GenerationStatusEnum(str, Enum):
    queued = "queued"
    running = "running"
    done = "done"
    failed = "failed"


class ExportStatusEnum(str, Enum):
    queued = "queued"
    running = "running"
    done = "done"
    failed = "failed"


class Carousel(Base):
    __tablename__ = "carousels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    status: Mapped[str] = mapped_column(String(32), default=CarouselStatusEnum.draft.value)
    language: Mapped[str] = mapped_column(String(8), default="ru")
    slides_count: Mapped[int] = mapped_column(Integer, default=8)
    style_hint: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[str] = mapped_column(String(32), default="text")
    source_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    design: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    slides: Mapped[list["Slide"]] = relationship(back_populates="carousel", cascade="all, delete-orphan")


class Slide(Base):
    __tablename__ = "slides"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    carousel_id: Mapped[int] = mapped_column(ForeignKey("carousels.id", ondelete="CASCADE"))
    order: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text)
    footer: Mapped[str | None] = mapped_column(String(255), nullable=True)

    carousel: Mapped[Carousel] = relationship(back_populates="slides")


class Generation(Base):
    __tablename__ = "generations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    carousel_id: Mapped[int] = mapped_column(ForeignKey("carousels.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(32), default=GenerationStatusEnum.queued.value)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)


class Export(Base):
    __tablename__ = "exports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    carousel_id: Mapped[int] = mapped_column(ForeignKey("carousels.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(32), default=ExportStatusEnum.queued.value)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

