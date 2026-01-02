export interface AgentStatus {
	id: string;
	name: string;
	status: "idle" | "running" | "completed" | "error";
	phase: "research" | "development" | "strategy";
	output?: string;
	error?: string;
}

export interface Message {
	role: "user" | "assistant" | "system";
	content: string;
	timestamp?: Date;
}

export interface WorkflowState {
	currentPhase: "idle" | "research" | "development" | "strategy" | "completed";
	iteration: number;
	maxIterations: number;
	validationScore?: number;
}
