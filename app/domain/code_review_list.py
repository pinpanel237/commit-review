from pydantic import BaseModel

class CodeReviewResult(BaseModel):
    improvements: str
    issues: str
    issue_title: str