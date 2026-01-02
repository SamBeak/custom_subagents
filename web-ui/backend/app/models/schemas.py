"""
Pydantic models for API schemas
"""

from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import datetime


class IdeaRequest(BaseModel):
	"""Request model for idea development"""

	idea: str
	constraints: Optional[str] = None
	target_users: Optional[str] = None
	focus_areas: Optional[List[str]] = None


class AgentStatusUpdate(BaseModel):
	"""Real-time agent status update"""

	agent_id: str
	agent_name: str
	status: Literal["idle", "running", "completed", "error"]
	phase: Literal["research", "development", "strategy"]
	output: Optional[str] = None
	error: Optional[str] = None
	timestamp: datetime = datetime.now()


class WorkflowState(BaseModel):
	"""Current workflow state"""

	current_phase: Literal["idle", "research", "development", "strategy", "completed"]
	iteration: int = 1
	max_iterations: int = 3
	validation_score: Optional[float] = None


class Message(BaseModel):
	"""Chat message model"""

	role: Literal["user", "assistant", "system"]
	content: str
	timestamp: datetime = datetime.now()


class WorkflowResult(BaseModel):
	"""Final workflow result"""

	success: bool
	idea: str
	refined_concept: Optional[str] = None
	value_proposition: Optional[str] = None
	execution_plan: Optional[str] = None
	business_model: Optional[str] = None
	pitch_materials: Optional[str] = None
	validation_score: Optional[float] = None
	iterations_completed: int = 0
	errors: Optional[List[str]] = None
