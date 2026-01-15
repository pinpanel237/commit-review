import logging
import os
import httpx

from fastapi import Request, APIRouter

from app.adapters.gitea.parser import extract_commits_from_push
from app.domain.commit import Commit

GITEA_URL = os.getenv("GITEA_URL")
GITEA_REPO = os.getenv("GITEA_REPO")
GITEA_TOKEN = os.getenv("GITEA_TOKEN")

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/webhooks/gitea")
async def getWebhook(request: Request):
    # 어떤 이벤트인지 확인
    event = request.headers.get("X-Github-Event")

    commits = []
    if event == "push":
        # body 가져오기
        payload = await request.json()
        commits = extract_commits_from_push(payload)
        logger.info(commits)

    if len(commits) == 0:
        return "No push event"
    else:
        llm = request.app.state.llm
        headers = {
            "Authorization": f"token {GITEA_TOKEN}",
            "Accept": "application/json"
        }
        responses = []

        async with httpx.AsyncClient() as client:
            for c in commits:
                diff_url = f"http://{GITEA_URL}/api/v1/repos/{GITEA_REPO}/git/commits/{c.id}.diff"
                logger.info(diff_url)
                diff_response = await client.get(diff_url, headers=headers)

                if diff_response.status_code == 200:
                    logger.info(diff_response.text)
                    response = await llm.review_code(diff_response.text)
                    responses.append({"id": c.id, "review": response})

        return responses