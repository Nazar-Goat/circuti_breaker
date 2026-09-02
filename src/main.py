import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src.config import settings
from src.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa
    logger = logging.getLogger("uvicorn.access")
    console_formatter = uvicorn.logging.ColourizedFormatter(  # noqa
        "{asctime} {levelprefix} : {message}", style="{", use_colors=False
    )
    logger.handlers[0].setFormatter(console_formatter)
    yield

app = FastAPI(
        title=settings.APP_NAME,
        lifespan=lifespan,
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,
            "displayRequestDuration": True,
            "filter": True,
        },
    )


app.include_router(api_router)


@app.get("/healthz", tags=["infra"])
async def healthz():
    """Для Docker HEALTHCHECK / k8s liveness — не зависит от БД/Redis, просто 'процесс жив'."""
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=settings.APP_PORT, reload=True)