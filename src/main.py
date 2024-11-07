import sys
import os

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
import sys

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.staticfiles import StaticFiles

from src import config
from src.auth.router import router as auth_router

logging.basicConfig(stream=sys.stdout, level=config.LOGGING_LEVEL)

app = FastAPI()
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

if __name__ == "__main__":
    import uvicorn

    # todo use uvloop for NOT windows
    uvicorn.run(app, host="0.0.0.0", port=80)
