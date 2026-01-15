import logging
import os
import textwrap
from typing import Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.domain.llm import LLMClient

logger = logging.getLogger(__name__)


class GroqClient(LLMClient):
    def __init__(self,
                 model: str = "llama-3.1-8b-instant",
                 temperature: float = 0.0,
                 max_tokens: int = 1024,
                 api_key: Optional[str] = None,
                 system_prompt: Optional[str] = None
                 ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.system_prompt = system_prompt or textwrap.dedent("""
                너는 우리 회사의 시니어 코드 리뷰어다.
                모든 응답은 반드시 한국어로 작성한다.
                코드의 가독성, 안전성, 성능, 유지보수성 관점에서 개선점을 구체적으로 설명한다.
                필요하면 예제 코드와 근거를 함께 제안한다.
            """)
        self.llm = ChatGroq(model=self.model,
                            temperature=self.temperature,
                            max_tokens=self.max_tokens,
                            api_key=self.api_key)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            ("human", "{input}")
        ])
        self.chain = self.prompt | self.llm

    async def review_code(self, message: str) -> str:
        try:
            response = await self.chain.ainvoke({
                "system_prompt": self.system_prompt,
                "input": message
            })
            logger.info(response.content)
            return response.content
        except Exception as e:
            raise RuntimeError(f"Groq LLM error: {e}")
