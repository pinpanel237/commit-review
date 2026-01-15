import logging
import os
import textwrap
from typing import Optional

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

from app.domain.code_review_list import CodeReviewResult
from app.domain.llm import LLMClient

logger = logging.getLogger(__name__)


class GroqClient(LLMClient):
    def __init__(self,
                 model: str = "llama-3.3-70b-versatile",
                 temperature: float = 0.0,
                 max_tokens: int = 1024,
                 api_key: Optional[str] = None,
                 system_prompt: Optional[str] = None
                 ):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.parser = PydanticOutputParser(pydantic_object=CodeReviewResult)
        self.system_prompt = system_prompt or textwrap.dedent(f"""
                당신은 우리 회사의 시니어 코드 리뷰어입니다.
                모든 응답은 반드시 한국어로 작성해야 합니다.
                
                작업 절차:
                1. (issues) 코드의 개선이 필요한 부분을 설명한다.
                2. (improvements) issues에서 발생한 문제를 어떻게 개선할 수 있는지 추천한다.
                2. (issue_title) 위 개선점들을 종합하여 Git 이슈 제목 하나를 생성한다.
                
                규칙:
                - 이슈사항(issues)과 개선추천(improvements)은 번호를 붙이지 않고 상세하게 작성한다.
                - 이슈 제목(issue_title)은 60자 이내로 작성한다.
                - 이슈 제목(issue_title) 맨 앞에 내용에 따라 대괄호 안에 Bug, Feature request, Enhancement, Refactor 
                중 하나를 선택하여 반드시 기입한다.
                
                {self.parser.get_format_instructions()}
                
                코드:
                {{code}}
            """)
        self.llm = ChatGroq(model=self.model,
                            temperature=self.temperature,
                            max_tokens=self.max_tokens,
                            api_key=self.api_key).bind(response_format={"type": "json_object"})
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "{system_prompt}"),
            ("human", "{input}")
        ])
        self.chain = self.prompt | self.llm

    async def review_code(self, message: str) -> CodeReviewResult:
        try:
            response = await self.chain.ainvoke({
                "system_prompt": self.system_prompt,
                "input": message
            })
            logger.info(response.content)
            return self.parser.parse(response.content)
        except Exception as e:
            raise RuntimeError(f"Groq LLM error: {e}")
