from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import get_api_key
from .db import engine
from .models import Base
from .routers import assets, carousels, exports, generations, health, preview


def create_app() -> FastAPI:
    app = FastAPI(title="Vibecoding Carousel API")

    # CORS so Nuxt frontend can call the API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    # защищённые роуты
    dependency = Depends(get_api_key)
    app.include_router(carousels.router, prefix="/carousels", tags=["carousels"], dependencies=[dependency])
    app.include_router(generations.router, prefix="/generations", tags=["generations"], dependencies=[dependency])
    app.include_router(exports.router, prefix="/exports", tags=["exports"], dependencies=[dependency])
    app.include_router(assets.router, prefix="/assets", tags=["assets"], dependencies=[dependency])
    app.include_router(preview.router, prefix="/preview", tags=["preview"], dependencies=[dependency])

    @app.on_event("startup")
    async def on_startup() -> None:
        """Create DB tables for demo if they do not exist."""
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    return app


app = create_app()

