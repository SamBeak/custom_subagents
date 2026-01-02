"use client";

import { useState, useEffect, useCallback } from "react";
import ChatInterface from "@/components/chat/ChatInterface";
import WorkflowVisualization from "@/components/workflow/WorkflowVisualization";
import OutputPanel from "@/components/output/OutputPanel";
import { AgentStatus } from "@/types/agent";
import { useWebSocket } from "@/hooks/useWebSocket";

interface OutputPaths {
	directory: string;
	idea_report: string;
	business_model: string;
	pitch_materials: string;
	summary: string;
}

export default function Home() {
	const [agentStatuses, setAgentStatuses] = useState<AgentStatus[]>([
		{ id: "researcher", name: "idea-researcher", status: "idle", phase: "research" },
		{ id: "competitor", name: "idea-competitor-analyzer", status: "idle", phase: "research" },
		{ id: "persona", name: "idea-user-persona", status: "idle", phase: "research" },
		{ id: "expander", name: "idea-expander", status: "idle", phase: "development" },
		{ id: "critic", name: "idea-critic", status: "idle", phase: "development" },
		{ id: "refiner", name: "idea-refiner", status: "idle", phase: "development" },
		{ id: "feasibility", name: "idea-feasibility-checker", status: "idle", phase: "development" },
		{ id: "validator", name: "idea-validator", status: "idle", phase: "development" },
		{ id: "monetization", name: "idea-monetization-strategist", status: "idle", phase: "strategy" },
		{ id: "pitch", name: "idea-pitch-generator", status: "idle", phase: "strategy" },
	]);
	const [currentPhase, setCurrentPhase] = useState<string>("idle");
	const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([]);
	const [outputPaths, setOutputPaths] = useState<OutputPaths | null>(null);
	const [wsConnected, setWsConnected] = useState(false);

	// WebSocket message handler
	const handleWebSocketMessage = useCallback((data: Record<string, unknown>) => {
		switch (data.type) {
			case "agent_status":
				setAgentStatuses((prev) =>
					prev.map((agent) =>
						agent.id === data.agent_id
							? { ...agent, status: data.status as AgentStatus["status"] }
							: agent
					)
				);
				break;
			case "phase_update":
				setCurrentPhase(data.phase as string);
				break;
			case "message":
				setMessages((prev) => [...prev, { role: data.role as string, content: data.content as string }]);
				break;
			case "outputs_saved":
				setOutputPaths(data.paths as OutputPaths);
				break;
		}
	}, []);

	const { isConnected, connect, send } = useWebSocket("ws://localhost:8000/ws", {
		onMessage: handleWebSocketMessage,
		onConnect: () => setWsConnected(true),
		onDisconnect: () => setWsConnected(false),
	});

	// Auto-connect on mount
	useEffect(() => {
		connect();
	}, [connect]);

	const handleSendMessage = async (message: string) => {
		// Add user message
		setMessages((prev) => [...prev, { role: "user", content: message }]);
		setCurrentPhase("research");

		// Send to backend via WebSocket
		if (isConnected) {
			send({ type: "start_workflow", idea: message });
		} else {
			// Fallback: simulation mode if backend not connected
			setMessages((prev) => [
				...prev,
				{ role: "system", content: "⚠️ 백엔드 미연결 - 시뮬레이션 모드로 실행합니다." },
			]);
			simulateWorkflow(message);
		}
	};

	const simulateWorkflow = async (idea: string) => {
		// Phase 1: Parallel Research
		updateAgentStatus(["researcher", "competitor", "persona"], "running");
		await delay(2000);
		updateAgentStatus(["researcher", "competitor", "persona"], "completed");

		setMessages((prev) => [
			...prev,
			{ role: "assistant", content: "✅ Research Phase 완료: 시장 조사, 경쟁 분석, 사용자 페르소나 생성됨" },
		]);

		// Phase 2: Development Cycle
		setCurrentPhase("development");
		const devAgents = ["expander", "critic", "refiner", "feasibility", "validator"];
		for (const agent of devAgents) {
			updateAgentStatus([agent], "running");
			await delay(1500);
			updateAgentStatus([agent], "completed");
		}

		setMessages((prev) => [
			...prev,
			{ role: "assistant", content: "✅ Development Cycle 완료: 아이디어 확장, 비판, 정제, 검증 완료 (Score: 8/10)" },
		]);

		// Phase 3: Strategy & Output
		setCurrentPhase("strategy");
		updateAgentStatus(["monetization"], "running");
		await delay(2000);
		updateAgentStatus(["monetization"], "completed");

		updateAgentStatus(["pitch"], "running");
		await delay(2000);
		updateAgentStatus(["pitch"], "completed");

		setMessages((prev) => [
			...prev,
			{ role: "assistant", content: "✅ Strategy & Output 완료: 비즈니스 모델 및 피치 자료 생성됨" },
		]);

		setCurrentPhase("completed");
		setMessages((prev) => [
			...prev,
			{
				role: "assistant",
				content: `## 🎉 아이디어 개발 완료!\n\n**입력 아이디어:** ${idea}\n\n### 최종 산출물\n⚠️ 시뮬레이션 모드: 실제 파일은 저장되지 않았습니다.\n백엔드 서버를 실행하세요: \`uvicorn app.main:app --reload\``,
			},
		]);
	};

	const updateAgentStatus = (ids: string[], status: AgentStatus["status"]) => {
		setAgentStatuses((prev) =>
			prev.map((agent) => (ids.includes(agent.id) ? { ...agent, status } : agent))
		);
	};

	const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

	const handleReset = () => {
		setAgentStatuses((prev) => prev.map((agent) => ({ ...agent, status: "idle" })));
		setCurrentPhase("idle");
		setMessages([]);
		setOutputPaths(null);
	};

	return (
		<main className="flex h-screen bg-background">
			{/* Left: Chat Interface */}
			<div className="w-1/2 border-r border-border flex flex-col">
				<div className="p-4 border-b border-border bg-card">
					<div className="flex items-center justify-between">
						<h1 className="text-xl font-bold">💡 Idea Developer</h1>
						<span className={`text-xs px-2 py-1 rounded-full ${isConnected ? "bg-green-100 text-green-700" : "bg-yellow-100 text-yellow-700"}`}>
							{isConnected ? "🟢 Backend 연결됨" : "🟡 시뮬레이션 모드"}
						</span>
					</div>
					<p className="text-sm text-muted-foreground">Multi-Agent 아이디어 개발 시스템</p>
				</div>
				<ChatInterface
					messages={messages}
					onSendMessage={handleSendMessage}
					isProcessing={currentPhase !== "idle" && currentPhase !== "completed"}
				/>
				<OutputPanel
					outputPaths={outputPaths}
					isVisible={currentPhase === "completed"}
				/>
			</div>

			{/* Right: Workflow Visualization */}
			<div className="w-1/2 flex flex-col">
				<div className="p-4 border-b border-border bg-card flex justify-between items-center">
					<div>
						<h2 className="text-lg font-semibold">📊 Workflow Status</h2>
						<p className="text-sm text-muted-foreground">
							현재 단계: <span className="font-medium text-primary">{currentPhase}</span>
						</p>
					</div>
					<button
						onClick={handleReset}
						className="px-3 py-1 text-sm bg-secondary hover:bg-secondary/80 rounded-md"
					>
						Reset
					</button>
				</div>
				<WorkflowVisualization agentStatuses={agentStatuses} currentPhase={currentPhase} />
			</div>
		</main>
	);
}
