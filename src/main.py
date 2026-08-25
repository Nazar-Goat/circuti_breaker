import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src.config import Settings
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
        title=Settings.APP_NAME,
        lifespan=lifespan,
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,
            "displayRequestDuration": True,
            "filter": True,
        },
    )


app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=Settings.APP_PORT, reload=True)