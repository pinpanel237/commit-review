from fastapi import Request, APIRouter
from app.adapters.gitea.parser import extract_commits_from_push
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/webhooks/gitea")
async def getWebhook(request: Request):
    # 어떤 이벤트인지 확인
    event = request.headers.get("X-Gitea-Event")

    if event == "push":
        # body 가져오기
        payload = await request.json()
        commits = extract_commits_from_push(payload)
        logger.info(f"Received {len(commits)} commits from Gitea: {payload}")

    return {"ok": True}