from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

from app.api.webhooks.gitea import router
from app.core.logging import setup_logging


def create_app() -> FastAPI:
    setup_logging()

    app = FastAPI(title="Git 코드 자동 리뷰 서버")
    app.include_router(router)

    return app

app = create_app()