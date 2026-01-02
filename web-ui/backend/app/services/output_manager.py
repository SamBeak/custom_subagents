"""
Output Manager - 산출물 로컬 파일 저장 서비스
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional


class OutputManager:
	"""
	Manages saving workflow outputs to local files
	Saves to: custom_subagents/outputs/{timestamp}-{idea-slug}/
	"""

	def __init__(self, base_path: Optional[str] = None):
		if base_path:
			self.base_path = Path(base_path)
		else:
			# Default: custom_subagents/outputs/
			self.base_path = Path(__file__).parent.parent.parent.parent.parent / "outputs"

		self.base_path.mkdir(parents=True, exist_ok=True)

	def slugify(self, text: str, max_length: int = 50) -> str:
		"""Convert text to URL-friendly slug"""
		# Remove special characters, convert to lowercase
		slug = re.sub(r"[^\w\s-]", "", text.lower())
		slug = re.sub(r"[-\s]+", "-", slug).strip("-")
		return slug[:max_length]

	def create_output_directory(self, idea: str) -> Path:
		"""Create timestamped output directory for an idea"""
		timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
		slug = self.slugify(idea)
		dir_name = f"{timestamp}-{slug}"
		output_dir = self.base_path / dir_name
		output_dir.mkdir(parents=True, exist_ok=True)
		return output_dir

	def save_idea_report(self, output_dir: Path, idea: str, research: dict, development: dict) -> str:
		"""Save the refined idea report"""
		content = f"""# 아이디어 개발 보고서

## 원본 아이디어
{idea}

## 시장 조사 결과
{research.get('market_research', 'N/A')}

## 경쟁 분석
{research.get('competitor_analysis', 'N/A')}

## 타겟 사용자 페르소나
{research.get('user_personas', 'N/A')}

## 아이디어 확장
{development.get('expander', 'N/A')}

## 비판적 분석
{development.get('critic', 'N/A')}

## 정제된 아이디어
{development.get('refiner', 'N/A')}

## 기술적 실현 가능성
{development.get('feasibility', 'N/A')}

## 검증 결과
- **검증 점수**: {development.get('validation_score', 'N/A')}/10
- **검증 의견**: {development.get('validator', 'N/A')}

---
*생성 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
		file_path = output_dir / "idea-report.md"
		file_path.write_text(content, encoding="utf-8")
		return str(file_path)

	def save_business_model(self, output_dir: Path, idea: str, monetization: str) -> str:
		"""Save the business model canvas"""
		content = f"""# 비즈니스 모델 Canvas

## 아이디어
{idea}

## 비즈니스 모델 분석
{monetization}

---
*생성 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
		file_path = output_dir / "business-model.md"
		file_path.write_text(content, encoding="utf-8")
		return str(file_path)

	def save_pitch_materials(self, output_dir: Path, idea: str, pitch: str) -> str:
		"""Save the pitch materials"""
		content = f"""# 피치 자료 패키지

## 아이디어
{idea}

## 피치 자료
{pitch}

---
*생성 일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
		file_path = output_dir / "pitch-materials.md"
		file_path.write_text(content, encoding="utf-8")
		return str(file_path)

	def save_summary(self, output_dir: Path, idea: str, validation_score: float, iterations: int) -> str:
		"""Save a summary file with links to all outputs"""
		content = f"""# 아이디어 개발 완료 요약

## 📋 기본 정보
- **원본 아이디어**: {idea}
- **검증 점수**: {validation_score}/10
- **반복 횟수**: {iterations}회
- **생성 일시**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 📁 산출물 목록
1. [아이디어 개발 보고서](./idea-report.md)
2. [비즈니스 모델 Canvas](./business-model.md)
3. [피치 자료 패키지](./pitch-materials.md)

## 🚀 다음 단계
1. 아이디어 보고서를 검토하고 팀과 공유
2. 비즈니스 모델을 기반으로 MVP 범위 정의
3. 피치 자료를 활용하여 이해관계자 설득
"""
		file_path = output_dir / "README.md"
		file_path.write_text(content, encoding="utf-8")
		return str(file_path)

	def save_all_outputs(
		self,
		idea: str,
		research: dict,
		development: dict,
		monetization: str,
		pitch: str,
		validation_score: float,
		iterations: int,
	) -> dict:
		"""Save all outputs and return file paths"""
		output_dir = self.create_output_directory(idea)

		paths = {
			"directory": str(output_dir),
			"idea_report": self.save_idea_report(output_dir, idea, research, development),
			"business_model": self.save_business_model(output_dir, idea, monetization),
			"pitch_materials": self.save_pitch_materials(output_dir, idea, pitch),
			"summary": self.save_summary(output_dir, idea, validation_score, iterations),
		}

		return paths
