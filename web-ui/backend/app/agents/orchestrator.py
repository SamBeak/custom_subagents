"""
Idea Developer Orchestrator
Coordinates multi-agent workflow with real-time updates
"""

import asyncio
import os
import re
from typing import List, Optional
from datetime import datetime

from app.services.output_manager import OutputManager
from app.services.claude_client import ClaudeClient


class IdeaDeveloperOrchestrator:
	"""
	Orchestrates the idea development workflow across 10 specialized agents
	with parallel research phase and sequential development cycle.
	"""

	AGENTS = {
		"research": ["researcher", "competitor", "persona"],
		"development": ["expander", "critic", "refiner", "feasibility", "validator"],
		"strategy": ["monetization", "pitch"],
	}

	def __init__(self, connection_manager):
		self.manager = connection_manager
		self.current_phase = "idle"
		self.iteration = 0
		self.max_iterations = 3
		self.output_manager = OutputManager()

		# Initialize Claude client (None if no API key)
		try:
			self.claude = ClaudeClient()
			self.use_real_ai = True
		except ValueError:
			self.claude = None
			self.use_real_ai = False

	async def broadcast_status(self, agent_id: str, status: str, phase: str, output: Optional[str] = None):
		"""Broadcast agent status update to all connected clients"""
		await self.manager.broadcast(
			{
				"type": "agent_status",
				"agent_id": agent_id,
				"status": status,
				"phase": phase,
				"output": output,
				"timestamp": datetime.now().isoformat(),
			}
		)

	async def broadcast_message(self, content: str, role: str = "assistant"):
		"""Broadcast chat message to all connected clients"""
		await self.manager.broadcast(
			{
				"type": "message",
				"role": role,
				"content": content,
				"timestamp": datetime.now().isoformat(),
			}
		)

	async def broadcast_phase(self, phase: str):
		"""Broadcast current phase update"""
		self.current_phase = phase
		await self.manager.broadcast(
			{
				"type": "phase_update",
				"phase": phase,
				"timestamp": datetime.now().isoformat(),
			}
		)

	async def run_agent(self, agent_id: str, phase: str, idea: str, context: dict = None) -> str:
		"""
		Run a single agent using Claude API or simulation fallback
		"""
		await self.broadcast_status(agent_id, "running", phase)

		if self.use_real_ai and self.claude:
			# Real AI agent call
			try:
				output = await self.claude.call_agent(agent_id, idea, context)
			except Exception as e:
				output = f"[{agent_id}] 오류 발생: {str(e)}"
		else:
			# Simulation fallback
			await asyncio.sleep(1.5)
			output = self._get_mock_output(agent_id, idea)

		await self.broadcast_status(agent_id, "completed", phase, output)
		return output

	def _get_mock_output(self, agent_id: str, idea: str) -> str:
		"""시뮬레이션용 목 데이터 반환"""
		mock_outputs = {
			"researcher": f"## 시장 조사 결과\n\n**아이디어:** {idea}\n\n- 시장 규모: 약 50억 달러 (2025년 기준)\n- 연평균 성장률: 15.2%\n- 주요 트렌드: AI 자동화, 개발자 생산성 향상",
			"competitor": f"## 경쟁 분석\n\n### 직접 경쟁사\n1. **GitHub Copilot** - 코드 자동 완성\n2. **SonarQube** - 정적 코드 분석\n\n### 차별화 포인트\n- 실시간 리뷰 피드백\n- 팀 컨벤션 학습",
			"persona": f"## 사용자 페르소나\n\n### 페르소나 1: 시니어 개발자 김철수\n- 나이: 35세\n- 고민: 코드 리뷰에 너무 많은 시간 소요\n- 목표: 팀 생산성 향상",
			"expander": f"## 확장된 아이디어\n\n### 핵심 기능 확장\n1. AI 기반 자동 코드 리뷰\n2. 팀 스타일 가이드 학습\n3. PR 자동 요약\n4. 보안 취약점 탐지",
			"critic": f"## 비판적 분석\n\n### 잠재적 위험\n1. 기존 도구 대비 차별화 부족 가능성\n2. 초기 학습 데이터 확보 난이도\n3. 개발자 신뢰 구축 필요",
			"refiner": f"## 정제된 아이디어\n\n### 핵심 가치 제안\n\"팀의 코딩 컨벤션을 학습하여 일관된 코드 품질을 유지하는 AI 코드 리뷰 어시스턴트\"\n\n### MVP 기능\n1. GitHub/GitLab 연동\n2. 자동 PR 분석\n3. 컨벤션 기반 피드백",
			"feasibility": f"## 기술적 실현 가능성\n\n- **기술 점수**: 8/10\n- **예상 개발 기간**: 3-4개월 (MVP)\n- **필요 스택**: Python, LLM API, GitHub API",
			"validator": f"## 최종 검증\n\n검증 점수: 8/10\n\n### 강점\n- 명확한 문제 해결\n- 기술적 실현 가능\n\n### 개선 필요\n- 경쟁 차별화 강화",
			"monetization": f"## 비즈니스 모델\n\n### 수익 모델: SaaS 구독\n- **Free**: 월 100 PR까지\n- **Pro**: $29/월, 무제한 PR\n- **Enterprise**: 맞춤 견적\n\n### 예상 수익\n- Year 1: $500K ARR",
			"pitch": f"## 피치 자료\n\n### 원라이너\n\"AI가 당신의 시니어 개발자처럼 코드를 리뷰합니다\"\n\n### 엘리베이터 피치\n개발팀이 코드 리뷰에 쓰는 시간의 60%를 절약하면서도 코드 품질은 더 높일 수 있다면?\n우리 솔루션은 팀의 코딩 스타일을 학습해서 일관된 피드백을 자동으로 제공합니다.",
		}
		return mock_outputs.get(agent_id, f"[{agent_id}] 분석 완료")

	async def run_parallel_research(self, idea: str) -> dict:
		"""Run research phase agents in parallel"""
		await self.broadcast_phase("research")
		await self.broadcast_message("🔍 Research Phase 시작: 3개 에이전트 병렬 실행 중...")

		# Run all research agents in parallel
		results = await asyncio.gather(
			self.run_agent("researcher", "research", idea),
			self.run_agent("competitor", "research", idea),
			self.run_agent("persona", "research", idea),
		)

		await self.broadcast_message("✅ Research Phase 완료: 시장 조사, 경쟁 분석, 사용자 페르소나 생성됨")

		return {
			"market_research": results[0],
			"competitor_analysis": results[1],
			"user_personas": results[2],
		}

	async def run_development_cycle(self, idea: str, research_context: dict) -> dict:
		"""Run development cycle sequentially"""
		await self.broadcast_phase("development")
		await self.broadcast_message(f"🔄 Development Cycle {self.iteration + 1}/{self.max_iterations} 시작...")

		# Build context progressively
		context = {
			"research": research_context.get("market_research", ""),
		}

		# Expander
		expanded = await self.run_agent("expander", "development", idea, context)
		context["expanded"] = expanded

		# Critic
		criticism = await self.run_agent("critic", "development", idea, context)
		context["criticism"] = criticism

		# Refiner
		refined = await self.run_agent("refiner", "development", idea, context)
		context["refined"] = refined

		# Feasibility
		feasibility = await self.run_agent("feasibility", "development", idea, context)
		context["feasibility"] = feasibility

		# Validator
		validator_output = await self.run_agent("validator", "development", idea, context)
		context["validator"] = validator_output

		# Extract validation score from output
		validation_score = self._extract_validation_score(validator_output)

		await self.broadcast_message(
			f"✅ Development Cycle 완료: 아이디어 확장, 비판, 정제, 검증 완료 (Score: {validation_score}/10)"
		)

		return {
			"validation_score": validation_score,
			"expander": expanded,
			"critic": criticism,
			"refiner": refined,
			"feasibility": feasibility,
			"validator": validator_output,
		}

	def _extract_validation_score(self, validator_output: str) -> float:
		"""validator 출력에서 검증 점수 추출"""
		match = re.search(r"검증 점수[:\s]*(\d+(?:\.\d+)?)", validator_output)
		if match:
			return float(match.group(1))
		return 7.0  # Default score

	async def run_strategy_phase(self, idea: str, dev_context: dict) -> dict:
		"""Run strategy and output phase"""
		await self.broadcast_phase("strategy")
		await self.broadcast_message("📊 Strategy & Output Phase 시작...")

		context = {
			"refined": dev_context.get("refiner", ""),
		}

		# Monetization
		monetization = await self.run_agent("monetization", "strategy", idea, context)
		context["monetization"] = monetization

		# Pitch
		pitch = await self.run_agent("pitch", "strategy", idea, context)

		await self.broadcast_message("✅ Strategy & Output 완료: 비즈니스 모델 및 피치 자료 생성됨")

		return {
			"monetization": monetization,
			"pitch": pitch,
		}

	async def run_workflow(self, idea: str):
		"""
		Execute the complete idea development workflow
		1. Parallel Research Phase
		2. Development Cycle (max 3 iterations)
		3. Strategy & Output Phase
		"""
		try:
			await self.broadcast_message(f"💡 아이디어 개발 시작: {idea}")

			# Phase 1: Parallel Research
			research_results = await self.run_parallel_research(idea)

			# Phase 2: Development Cycle
			self.iteration = 0
			dev_results = {}

			while self.iteration < self.max_iterations:
				dev_results = await self.run_development_cycle(idea, research_results)
				self.iteration += 1

				if dev_results.get("validation_score", 0) >= 7:
					break

			# Phase 3: Strategy & Output
			final_results = await self.run_strategy_phase(idea, dev_results)

			# Save outputs to local files
			output_paths = self.output_manager.save_all_outputs(
				idea=idea,
				research=research_results,
				development=dev_results,
				monetization=final_results.get("monetization", ""),
				pitch=final_results.get("pitch", ""),
				validation_score=dev_results.get("validation_score", 0),
				iterations=self.iteration,
			)

			# Completion
			await self.broadcast_phase("completed")
			await self.broadcast_message(
				f"""## 🎉 아이디어 개발 완료!

**입력 아이디어:** {idea}

### 최종 산출물
1. 📊 고도화된 아이디어 문서
2. 💰 비즈니스 모델 Canvas
3. 🎤 피치 자료 패키지

**검증 점수:** {dev_results.get('validation_score', 'N/A')}/10
**반복 횟수:** {self.iteration}회

### 📁 저장 위치
`{output_paths['directory']}`"""
			)

			# Broadcast output paths for frontend download
			await self.manager.broadcast({
				"type": "outputs_saved",
				"paths": output_paths,
				"timestamp": datetime.now().isoformat(),
			})

			return {**final_results, "output_paths": output_paths}

		except Exception as e:
			await self.broadcast_message(f"❌ 오류 발생: {str(e)}")
			await self.broadcast_phase("error")
			raise
