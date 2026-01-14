from fastapi import Request, APIRouter
from app.adapters.gitea.parser import extract_push
import logging

from app.domain.commit import Push

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/webhooks/gitea")
async def getWebhook(request: Request):
    # 어떤 이벤트인지 확인
    event = request.headers.get("X-Github-Event")

    push: Push | None = None
    if event == "push":
        # body 가져오기
        payload = await request.json()
        push = extract_push(payload)

    if push is None:
        return "No push event"
    else:
        return f"before={push.before}, after={push.after}"