"use client";

import { useEffect, useRef, useCallback, useState } from "react";

interface WebSocketMessage {
	type: string;
	[key: string]: unknown;
}

interface UseWebSocketOptions {
	onMessage?: (message: WebSocketMessage) => void;
	onConnect?: () => void;
	onDisconnect?: () => void;
	onError?: (error: Event) => void;
}

export function useWebSocket(url: string, options: UseWebSocketOptions = {}) {
	const wsRef = useRef<WebSocket | null>(null);
	const [isConnected, setIsConnected] = useState(false);
	const [error, setError] = useState<string | null>(null);

	const connect = useCallback(() => {
		if (wsRef.current?.readyState === WebSocket.OPEN) return;

		try {
			wsRef.current = new WebSocket(url);

			wsRef.current.onopen = () => {
				setIsConnected(true);
				setError(null);
				options.onConnect?.();
			};

			wsRef.current.onmessage = (event) => {
				try {
					const data = JSON.parse(event.data);
					options.onMessage?.(data);
				} catch (e) {
					console.error("Failed to parse WebSocket message:", e);
				}
			};

			wsRef.current.onclose = () => {
				setIsConnected(false);
				options.onDisconnect?.();
			};

			wsRef.current.onerror = (event) => {
				setError("WebSocket connection error");
				options.onError?.(event);
			};
		} catch (e) {
			setError("Failed to create WebSocket connection");
		}
	}, [url, options]);

	const disconnect = useCallback(() => {
		wsRef.current?.close();
		wsRef.current = null;
		setIsConnected(false);
	}, []);

	const send = useCallback((data: WebSocketMessage) => {
		if (wsRef.current?.readyState === WebSocket.OPEN) {
			wsRef.current.send(JSON.stringify(data));
			return true;
		}
		return false;
	}, []);

	useEffect(() => {
		return () => {
			disconnect();
		};
	}, [disconnect]);

	return {
		isConnected,
		error,
		connect,
		disconnect,
		send,
	};
}
