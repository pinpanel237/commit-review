from abc import ABC, abstractmethod

class LLMClient(ABC):
    @abstractmethod
    async def review_code(self, prompt: str) -> str:
        pass