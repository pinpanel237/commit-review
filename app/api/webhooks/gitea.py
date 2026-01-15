import logging
import os
from textwrap import dedent

import httpx

from app.domain.code_review_list import CodeReviewResult
from app.domain.commit import Commit
from fastapi import Request, APIRouter

from app.adapters.gitea.parser import extract_commits_from_push

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
        responses = await get_diff(llm, commits)

        return responses

async def get_diff(llm, commits: list[Commit]) -> str:
    responses = []
    headers = {
        "Authorization": f"token {GITEA_TOKEN}",
        "Accept": "application/json"
    }

    async with httpx.AsyncClient() as client:
        for c in commits:
            diff_url = f"http://{GITEA_URL}/api/v1/repos/{GITEA_REPO}/git/commits/{c.id}.diff"
            logger.info(diff_url)
            diff_response = await client.get(diff_url, headers=headers)

            if diff_response.status_code == 200:
                logger.info(diff_response.text)
                code_review_result = await llm.review_code(diff_response.text)
                responses.append(code_review_result)

        await createIssues(llm, c.id, responses)

        return "개선 이슈 등록 완료"

async def createIssues(llm, commit_id, llm_responses: list[CodeReviewResult]):
    create_issue_url = f"http://{GITEA_URL}/api/v1/repos/{GITEA_REPO}/issues"
    headers = {
        "Authorization": f"token {GITEA_TOKEN}",
        "Accept": "application/json"
    }

    async with httpx.AsyncClient() as client:
        for response in llm_responses:
            body = {
                "title": response.issue_title,
                "body": dedent(f"""
                        **이슈사항**
                        
                        {response.issues}
                    
                        **개선추천**
                        
                        {response.improvements}
                        
                        **해당 커밋**
                        {commit_id}
                        
                        해당 이슈는 {llm.model}를 사용하여 자동으로 작성되었습니다.
                    """).strip(),
                "closed": False,
            }
            issue_response = await client.post(create_issue_url, headers=headers, json=body)
            if issue_response.status_code == 201:
                logger.info(issue_response.text)
