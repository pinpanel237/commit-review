from app.domain.commit import Commit

def extract_commits_from_push(payload: dict) -> list[Commit]:
    commits = []

    for c in payload.get("commits", []):
        commits.append(
            Commit(
                id=c.get("id")
            )
        )

    return commits
