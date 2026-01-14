from dataclasses import dataclass

@dataclass
class Commit:
    sha: str
    message: str
    author_name: str | None = None
    author_email: str | None = None