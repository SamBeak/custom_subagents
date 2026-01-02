"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Loader2 } from "lucide-react";

interface Message {
	role: string;
	content: string;
}

interface ChatInterfaceProps {
	messages: Message[];
	onSendMessage: (message: string) => void;
	isProcessing: boolean;
}

export default function ChatInterface({
	messages,
	onSendMessage,
	isProcessing,
}: ChatInterfaceProps) {
	const [input, setInput] = useState("");
	const messagesEndRef = useRef<HTMLDivElement>(null);

	const scrollToBottom = () => {
		messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
	};

	useEffect(() => {
		scrollToBottom();
	}, [messages]);

	const handleSubmit = (e: React.FormEvent) => {
		e.preventDefault();
		if (input.trim() && !isProcessing) {
			onSendMessage(input.trim());
			setInput("");
		}
	};

	return (
		<div className="flex flex-col flex-1 overflow-hidden">
			{/* Messages Area */}
			<div className="flex-1 overflow-y-auto p-4 space-y-4">
				{messages.length === 0 ? (
					<div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
						<div className="text-6xl mb-4">💡</div>
						<h3 className="text-lg font-medium mb-2">아이디어를 입력해주세요</h3>
						<p className="text-sm max-w-md">
							초기 아이디어를 입력하면 10개의 전문 AI 에이전트가 협력하여
							체계적으로 발전시켜 드립니다.
						</p>
						<div className="mt-4 text-xs space-y-1">
							<p>예시: &quot;AI 기반 코드 리뷰 자동화 도구&quot;</p>
							<p>예시: &quot;원격 팀을 위한 비동기 협업 플랫폼&quot;</p>
						</div>
					</div>
				) : (
					messages.map((message, index) => (
						<div
							key={index}
							className={`flex ${
								message.role === "user" ? "justify-end" : "justify-start"
							}`}
						>
							<div
								className={`max-w-[80%] rounded-lg px-4 py-2 ${
									message.role === "user"
										? "bg-primary text-primary-foreground"
										: "bg-muted"
								}`}
							>
								<div className="whitespace-pre-wrap text-sm">
									{message.content}
								</div>
							</div>
						</div>
					))
				)}
				<div ref={messagesEndRef} />
			</div>

			{/* Input Area */}
			<form
				onSubmit={handleSubmit}
				className="p-4 border-t border-border bg-card"
			>
				<div className="flex gap-2">
					<input
						type="text"
						value={input}
						onChange={(e) => setInput(e.target.value)}
						placeholder="아이디어를 입력하세요..."
						disabled={isProcessing}
						className="flex-1 px-4 py-2 rounded-lg border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
					/>
					<button
						type="submit"
						disabled={!input.trim() || isProcessing}
						className="px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
					>
						{isProcessing ? (
							<Loader2 className="w-4 h-4 animate-spin" />
						) : (
							<Send className="w-4 h-4" />
						)}
					</button>
				</div>
				{isProcessing && (
					<p className="text-xs text-muted-foreground mt-2">
						에이전트가 작업 중입니다...
					</p>
				)}
			</form>
		</div>
	);
}
