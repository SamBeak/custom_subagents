"use client";

import { memo } from "react";
import { Handle, Position, NodeProps } from "@xyflow/react";
import { Loader2, CheckCircle2, XCircle, Circle } from "lucide-react";

interface AgentNodeData {
	label: string;
	status: "idle" | "running" | "completed" | "error";
}

function AgentNode({ data }: NodeProps) {
	const nodeData = data as AgentNodeData;

	const getStatusIcon = () => {
		switch (nodeData.status) {
			case "running":
				return <Loader2 className="w-4 h-4 animate-spin text-blue-500" />;
			case "completed":
				return <CheckCircle2 className="w-4 h-4 text-green-500" />;
			case "error":
				return <XCircle className="w-4 h-4 text-red-500" />;
			default:
				return <Circle className="w-4 h-4 text-gray-400" />;
		}
	};

	const getStatusStyle = () => {
		switch (nodeData.status) {
			case "running":
				return "border-blue-500 bg-blue-50 shadow-lg shadow-blue-500/20";
			case "completed":
				return "border-green-500 bg-green-50";
			case "error":
				return "border-red-500 bg-red-50";
			default:
				return "border-gray-300 bg-white";
		}
	};

	return (
		<>
			<Handle type="target" position={Position.Top} className="!bg-gray-400" />
			<div
				className={`px-4 py-2 rounded-lg border-2 transition-all duration-300 ${getStatusStyle()}`}
			>
				<div className="flex items-center gap-2">
					{getStatusIcon()}
					<span className="text-xs font-medium text-gray-700">
						{nodeData.label}
					</span>
				</div>
			</div>
			<Handle
				type="source"
				position={Position.Bottom}
				className="!bg-gray-400"
			/>
		</>
	);
}

export default memo(AgentNode);
