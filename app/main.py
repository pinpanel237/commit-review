from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI

from app.adapters.llm.groqClient import GroqClient

load_dotenv()

from app.api.webhooks.gitea import router
from app.core.logging import setup_logging


def startup():
    app.state.llm = GroqClient()


@asynccontextmanager
async def lifespan(app: FastAPI):
    startup()

    yield


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(title="Git 코드 자동 리뷰 서버", lifespan=lifespan)
    app.include_router(router)

    return app


app = create_app()
