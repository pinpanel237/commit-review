from app.domain.commit import Commit

def extract_commits_from_push(payload: dict) -> list[Commit]:
    commits = []

    for c in payload.get("commits", []):
        commits.append(Commit(
            sha=c.get("sha"),
            message=c.get("message"),
            author_name=c.get("author_name"),
            author_email=c.get("author_email"),
        ))

    return commits