"use client";

import { useCallback, useMemo } from "react";
import {
	ReactFlow,
	Node,
	Edge,
	Background,
	Controls,
	MiniMap,
	useNodesState,
	useEdgesState,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import AgentNode from "./AgentNode";
import { AgentStatus } from "@/types/agent";

interface WorkflowVisualizationProps {
	agentStatuses: AgentStatus[];
	currentPhase: string;
}

const nodeTypes = {
	agent: AgentNode,
};

export default function WorkflowVisualization({
	agentStatuses,
	currentPhase,
}: WorkflowVisualizationProps) {
	const getStatusColor = (status: AgentStatus["status"]) => {
		switch (status) {
			case "running":
				return "#3b82f6";
			case "completed":
				return "#22c55e";
			case "error":
				return "#ef4444";
			default:
				return "#6b7280";
		}
	};

	const initialNodes: Node[] = useMemo(() => {
		const findAgent = (id: string) =>
			agentStatuses.find((a) => a.id === id) || { status: "idle" };

		return [
			// Research Phase (Parallel)
			{
				id: "research-group",
				type: "group",
				position: { x: 50, y: 50 },
				data: { label: "Research Phase (Parallel)" },
				style: {
					width: 500,
					height: 120,
					backgroundColor: "rgba(59, 130, 246, 0.1)",
					borderRadius: 8,
					border: "1px dashed #3b82f6",
				},
			},
			{
				id: "researcher",
				type: "agent",
				position: { x: 20, y: 30 },
				parentId: "research-group",
				extent: "parent" as const,
				data: {
					label: "researcher",
					status: findAgent("researcher").status,
				},
			},
			{
				id: "competitor",
				type: "agent",
				position: { x: 180, y: 30 },
				parentId: "research-group",
				extent: "parent" as const,
				data: {
					label: "competitor",
					status: findAgent("competitor").status,
				},
			},
			{
				id: "persona",
				type: "agent",
				position: { x: 340, y: 30 },
				parentId: "research-group",
				extent: "parent" as const,
				data: {
					label: "user-persona",
					status: findAgent("persona").status,
				},
			},

			// Development Cycle
			{
				id: "expander",
				type: "agent",
				position: { x: 50, y: 220 },
				data: { label: "expander", status: findAgent("expander").status },
			},
			{
				id: "critic",
				type: "agent",
				position: { x: 200, y: 220 },
				data: { label: "critic", status: findAgent("critic").status },
			},
			{
				id: "refiner",
				type: "agent",
				position: { x: 350, y: 220 },
				data: { label: "refiner", status: findAgent("refiner").status },
			},
			{
				id: "feasibility",
				type: "agent",
				position: { x: 125, y: 320 },
				data: { label: "feasibility", status: findAgent("feasibility").status },
			},
			{
				id: "validator",
				type: "agent",
				position: { x: 275, y: 320 },
				data: { label: "validator", status: findAgent("validator").status },
			},

			// Strategy & Output
			{
				id: "monetization",
				type: "agent",
				position: { x: 125, y: 420 },
				data: {
					label: "monetization",
					status: findAgent("monetization").status,
				},
			},
			{
				id: "pitch",
				type: "agent",
				position: { x: 275, y: 420 },
				data: { label: "pitch", status: findAgent("pitch").status },
			},
		];
	}, [agentStatuses]);

	const initialEdges: Edge[] = useMemo(
		() => [
			// Research to Development
			{
				id: "e-research-dev",
				source: "research-group",
				target: "expander",
				animated: currentPhase === "research",
				style: { stroke: "#3b82f6" },
			},

			// Development Cycle
			{
				id: "e-exp-crit",
				source: "expander",
				target: "critic",
				animated: currentPhase === "development",
			},
			{
				id: "e-crit-ref",
				source: "critic",
				target: "refiner",
				animated: currentPhase === "development",
			},
			{
				id: "e-ref-feas",
				source: "refiner",
				target: "feasibility",
				animated: currentPhase === "development",
			},
			{
				id: "e-feas-val",
				source: "feasibility",
				target: "validator",
				animated: currentPhase === "development",
			},

			// Strategy
			{
				id: "e-val-mon",
				source: "validator",
				target: "monetization",
				animated: currentPhase === "strategy",
				style: { stroke: "#22c55e" },
			},
			{
				id: "e-mon-pitch",
				source: "monetization",
				target: "pitch",
				animated: currentPhase === "strategy",
			},
		],
		[currentPhase]
	);

	const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
	const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

	// Update nodes when agentStatuses change
	useMemo(() => {
		setNodes((nds) =>
			nds.map((node) => {
				const agent = agentStatuses.find((a) => a.id === node.id);
				if (agent && node.type === "agent") {
					return {
						...node,
						data: { ...node.data, status: agent.status },
					};
				}
				return node;
			})
		);
	}, [agentStatuses, setNodes]);

	return (
		<div className="flex-1 bg-muted/30">
			<ReactFlow
				nodes={nodes}
				edges={edges}
				onNodesChange={onNodesChange}
				onEdgesChange={onEdgesChange}
				nodeTypes={nodeTypes}
				fitView
				fitViewOptions={{ padding: 0.2 }}
				proOptions={{ hideAttribution: true }}
			>
				<Background color="#e5e7eb" gap={16} />
				<Controls />
				<MiniMap
					nodeColor={(node) => {
						if (node.type === "agent") {
							return getStatusColor(node.data?.status as AgentStatus["status"]);
						}
						return "#e5e7eb";
					}}
					maskColor="rgba(0,0,0,0.1)"
				/>
			</ReactFlow>
		</div>
	);
}
