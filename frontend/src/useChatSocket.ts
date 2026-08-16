import { useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useAuth } from "./hooks";
import type { ChatMessages, Message } from "./types";

const socketBaseUrl = "ws://localhost:8000";

/** Matches the event envelope built in `backend/realtime.py`. */
type ChatEvent =
    | { type: "message_new"; payload: Message }
    | { type: "message_edit"; payload: Message }
    | { type: "message_delete"; payload: { id: number; chat_id: number } }
    | { type: "member_join"; payload: { chat_id: number; account_id: number } }
    | { type: "member_leave"; payload: { chat_id: number; account_id: number } };

const emptyMessages: ChatMessages = { metadata: { count: 0 }, messages: [] };

const withMessages = (messages: Message[]): ChatMessages => ({
    metadata: { count: messages.length },
    messages,
});

/**
 * Keeps the message cache for a chat up to date over a WebSocket.
 *
 * Events are applied to the cache directly rather than triggering a refetch, so a new
 * message costs one small frame instead of a full reload of the chat.
 */
export function useChatSocket(chatId: number) {
    const { headers, loggedIn } = useAuth();
    const queryClient = useQueryClient();
    const [connected, setConnected] = useState(false);
    // Held in a ref so the reconnect timer can be cleared without re-running the effect.
    const reconnectRef = useRef<ReturnType<typeof setTimeout> | null>(null);
    const attemptsRef = useRef(0);

    const token = headers.Authorization?.replace("Bearer ", "") ?? "";

    useEffect(() => {
        if (!loggedIn || !token || Number.isNaN(chatId)) {
            return;
        }

        let socket: WebSocket | null = null;
        let closedByEffect = false;

        const messagesKey = ["chats/chatId/messages", chatId];
        const accountsKey = ["chats/chatId/accounts", chatId];

        const applyEvent = (event: ChatEvent) => {
            switch (event.type) {
                case "message_new":
                case "message_edit": {
                    const incoming = event.payload;
                    queryClient.setQueryData<ChatMessages>(messagesKey, (current) => {
                        const messages = (current ?? emptyMessages).messages;
                        const existing = messages.findIndex((m) => m.id === incoming.id);
                        if (existing === -1) {
                            return withMessages([...messages, incoming]);
                        }
                        const next = [...messages];
                        next[existing] = incoming;
                        return withMessages(next);
                    });
                    break;
                }
                case "message_delete": {
                    const { id } = event.payload;
                    queryClient.setQueryData<ChatMessages>(messagesKey, (current) => {
                        const messages = (current ?? emptyMessages).messages;
                        return withMessages(messages.filter((m) => m.id !== id));
                    });
                    break;
                }
                case "member_join":
                case "member_leave": {
                    queryClient.invalidateQueries({ queryKey: accountsKey });
                    // a leave rewrites that member's messages to have no author
                    queryClient.invalidateQueries({ queryKey: messagesKey });
                    break;
                }
            }
        };

        const connect = () => {
            socket = new WebSocket(
                `${socketBaseUrl}/chats/${chatId}/ws?token=${encodeURIComponent(token)}`,
            );

            socket.onopen = () => {
                attemptsRef.current = 0;
                setConnected(true);
                // Resync whatever was missed while disconnected.
                queryClient.invalidateQueries({ queryKey: messagesKey });
            };

            socket.onmessage = (raw) => {
                try {
                    applyEvent(JSON.parse(raw.data) as ChatEvent);
                } catch {
                    // ignore frames we cannot parse rather than tearing down the socket
                }
            };

            socket.onclose = (closeEvent) => {
                setConnected(false);
                // 4401/4403 are our own auth and membership refusals: retrying cannot help.
                if (closedByEffect || closeEvent.code === 4401 || closeEvent.code === 4403) {
                    return;
                }
                const delay = Math.min(1000 * 2 ** attemptsRef.current, 15000);
                attemptsRef.current += 1;
                reconnectRef.current = setTimeout(connect, delay);
            };

            socket.onerror = () => socket?.close();
        };

        connect();

        return () => {
            closedByEffect = true;
            if (reconnectRef.current !== null) {
                clearTimeout(reconnectRef.current);
                reconnectRef.current = null;
            }
            socket?.close();
        };
    }, [chatId, token, loggedIn, queryClient]);

    return { connected };
}
