from app.domain.commit import Push

def extract_push(payload: dict) -> Push:
    return Push(
        before=payload.get("before", ""),
        after=payload.get("after", ""),
    )
