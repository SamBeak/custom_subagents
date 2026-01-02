"""
Idea Developer Backend API
Multi-Agent Orchestration Server with WebSocket support
"""

from dotenv import load_dotenv
load_dotenv()  # Load .env file

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from typing import List
from pathlib import Path
import json
import asyncio
import os
from datetime import datetime

from app.models.schemas import IdeaRequest, AgentStatusUpdate, WorkflowState
from app.agents.orchestrator import IdeaDeveloperOrchestrator

app = FastAPI(
	title="Idea Developer API",
	description="Multi-Agent Idea Development Orchestration API",
	version="1.0.0",
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["http://localhost:3000"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


class ConnectionManager:
	"""Manages WebSocket connections for real-time updates"""

	def __init__(self):
		self.active_connections: List[WebSocket] = []

	async def connect(self, websocket: WebSocket):
		await websocket.accept()
		self.active_connections.append(websocket)

	def disconnect(self, websocket: WebSocket):
		self.active_connections.remove(websocket)

	async def broadcast(self, message: dict):
		for connection in self.active_connections:
			await connection.send_json(message)


manager = ConnectionManager()


@app.get("/")
async def root():
	return {"message": "Idea Developer API", "status": "running"}


@app.get("/health")
async def health_check():
	return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
	"""WebSocket endpoint for real-time workflow updates"""
	await manager.connect(websocket)
	orchestrator = IdeaDeveloperOrchestrator(manager)

	try:
		while True:
			data = await websocket.receive_text()
			message = json.loads(data)

			if message.get("type") == "start_workflow":
				idea = message.get("idea", "")
				await orchestrator.run_workflow(idea)

			elif message.get("type") == "cancel":
				await websocket.send_json({"type": "cancelled", "message": "Workflow cancelled"})

	except WebSocketDisconnect:
		manager.disconnect(websocket)


@app.post("/api/develop")
async def develop_idea(request: IdeaRequest):
	"""
	REST endpoint for idea development (non-streaming)
	For simple use cases without real-time updates
	"""
	return {
		"status": "accepted",
		"message": "Use WebSocket endpoint /ws for real-time updates",
		"idea": request.idea,
	}


# Outputs directory path
OUTPUTS_DIR = Path(__file__).parent.parent.parent.parent / "outputs"


@app.get("/api/outputs")
async def list_outputs():
	"""List all output directories"""
	if not OUTPUTS_DIR.exists():
		return {"outputs": []}

	outputs = []
	for item in sorted(OUTPUTS_DIR.iterdir(), reverse=True):
		if item.is_dir():
			readme_path = item / "README.md"
			outputs.append({
				"name": item.name,
				"path": str(item),
				"has_readme": readme_path.exists(),
				"created": datetime.fromtimestamp(item.stat().st_ctime).isoformat(),
			})
	return {"outputs": outputs}


@app.get("/api/outputs/{output_name}/{file_name}")
async def get_output_file(output_name: str, file_name: str):
	"""Get a specific output file"""
	file_path = OUTPUTS_DIR / output_name / file_name
	if not file_path.exists():
		return {"error": "File not found"}
	return FileResponse(file_path, media_type="text/markdown", filename=file_name)


@app.get("/api/outputs/{output_name}")
async def get_output_directory(output_name: str):
	"""Get all files in an output directory"""
	dir_path = OUTPUTS_DIR / output_name
	if not dir_path.exists():
		return {"error": "Directory not found"}

	files = []
	for item in dir_path.iterdir():
		if item.is_file():
			files.append({
				"name": item.name,
				"size": item.stat().st_size,
				"content": item.read_text(encoding="utf-8") if item.suffix == ".md" else None,
			})
	return {"directory": output_name, "files": files}


if __name__ == "__main__":
	import uvicorn

	uvicorn.run(app, host="0.0.0.0", port=8000)
