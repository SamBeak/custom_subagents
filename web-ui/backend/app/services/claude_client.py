"""
Claude API Client - 실제 AI 에이전트 호출
"""

import os
from typing import Optional
from anthropic import Anthropic


class ClaudeClient:
	"""
	Claude API를 호출하여 실제 AI 에이전트 작업을 수행
	"""

	def __init__(self, api_key: Optional[str] = None):
		self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
		if not self.api_key:
			raise ValueError("ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")
		self.client = Anthropic(api_key=self.api_key)
		self.model = "claude-sonnet-4-20250514"

	async def call_agent(self, agent_type: str, idea: str, context: dict = None) -> str:
		"""
		특정 에이전트 역할로 Claude를 호출
		"""
		system_prompt = self._get_system_prompt(agent_type)
		user_message = self._build_user_message(agent_type, idea, context or {})

		response = self.client.messages.create(
			model=self.model,
			max_tokens=2000,
			system=system_prompt,
			messages=[{"role": "user", "content": user_message}],
		)

		return response.content[0].text

	def _get_system_prompt(self, agent_type: str) -> str:
		"""에이전트 타입별 시스템 프롬프트 반환"""
		prompts = {
			"researcher": """You are an Idea Researcher agent. Your role is to:
- Conduct comprehensive market research for the given idea
- Identify market size, trends, and growth potential
- Find relevant industry reports and data
- Analyze target market segments
Respond in Korean with structured markdown format.""",

			"competitor": """You are a Competitor Analyzer agent. Your role is to:
- Identify direct and indirect competitors
- Analyze competitor strengths and weaknesses
- Find market gaps and opportunities
- Compare pricing and features
Respond in Korean with structured markdown format.""",

			"persona": """You are a User Persona Creator agent. Your role is to:
- Define 2-3 detailed user personas
- Include demographics, behaviors, pain points, goals
- Map user journey touchpoints
- Identify key user needs and motivations
Respond in Korean with structured markdown format.""",

			"expander": """You are an Idea Expander agent. Your role is to:
- Expand the initial idea with creative variations
- Suggest additional features and capabilities
- Explore adjacent market opportunities
- Generate "what if" scenarios
Respond in Korean with structured markdown format.""",

			"critic": """You are an Idea Critic agent. Your role is to:
- Critically analyze the idea's weaknesses
- Identify potential risks and challenges
- Play devil's advocate constructively
- Highlight assumptions that need validation
Respond in Korean with structured markdown format.""",

			"refiner": """You are an Idea Refiner agent. Your role is to:
- Synthesize feedback from expansion and criticism
- Refine the core value proposition
- Clarify the unique selling points
- Create a polished, focused concept
Respond in Korean with structured markdown format.""",

			"feasibility": """You are a Feasibility Checker agent. Your role is to:
- Assess technical feasibility (1-10 scale)
- Estimate development timeline and resources
- Identify technology stack requirements
- Flag technical risks and dependencies
Respond in Korean with structured markdown format including scores.""",

			"validator": """You are an Idea Validator agent. Your role is to:
- Provide overall validation score (1-10)
- Summarize key strengths and weaknesses
- Recommend go/no-go decision
- Suggest priority improvements
IMPORTANT: Include a line "검증 점수: X/10" where X is your score.
Respond in Korean with structured markdown format.""",

			"monetization": """You are a Monetization Strategist agent. Your role is to:
- Design revenue models (subscription, freemium, etc.)
- Create pricing strategy recommendations
- Estimate revenue potential
- Build Business Model Canvas
Respond in Korean with structured markdown format.""",

			"pitch": """You are a Pitch Generator agent. Your role is to:
- Create compelling one-liner pitch
- Write elevator pitch (30 seconds)
- Develop investor pitch outline
- Suggest key metrics to highlight
Respond in Korean with structured markdown format.""",
		}
		return prompts.get(agent_type, "You are a helpful AI assistant.")

	def _build_user_message(self, agent_type: str, idea: str, context: dict) -> str:
		"""에이전트별 사용자 메시지 구성"""
		base_message = f"## 분석 대상 아이디어\n{idea}\n\n"

		if agent_type in ["researcher", "competitor", "persona"]:
			return base_message + "위 아이디어에 대해 분석해주세요."

		elif agent_type == "expander":
			research = context.get("research", "")
			return base_message + f"## 시장 조사 결과\n{research}\n\n위 정보를 바탕으로 아이디어를 확장해주세요."

		elif agent_type == "critic":
			expanded = context.get("expanded", "")
			return base_message + f"## 확장된 아이디어\n{expanded}\n\n비판적으로 분석해주세요."

		elif agent_type == "refiner":
			expanded = context.get("expanded", "")
			criticism = context.get("criticism", "")
			return base_message + f"## 확장된 아이디어\n{expanded}\n\n## 비판적 분석\n{criticism}\n\n아이디어를 정제해주세요."

		elif agent_type == "feasibility":
			refined = context.get("refined", "")
			return base_message + f"## 정제된 아이디어\n{refined}\n\n기술적 실현 가능성을 평가해주세요."

		elif agent_type == "validator":
			refined = context.get("refined", "")
			feasibility = context.get("feasibility", "")
			return base_message + f"## 정제된 아이디어\n{refined}\n\n## 실현 가능성\n{feasibility}\n\n최종 검증해주세요."

		elif agent_type == "monetization":
			refined = context.get("refined", "")
			return base_message + f"## 정제된 아이디어\n{refined}\n\n수익화 전략을 설계해주세요."

		elif agent_type == "pitch":
			refined = context.get("refined", "")
			monetization = context.get("monetization", "")
			return base_message + f"## 정제된 아이디어\n{refined}\n\n## 비즈니스 모델\n{monetization}\n\n피치 자료를 생성해주세요."

		return base_message
