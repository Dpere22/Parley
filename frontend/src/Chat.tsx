import {
    useEffect,
    useLayoutEffect,
    useMemo,
    useRef,
    useState,
    type FormEvent,
    type KeyboardEvent,
} from "react";
import { useNavigate, useParams } from "react-router";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useAccount, useChat, useChatAccounts, useMessages } from "./queries";
import { useAuth } from "./hooks";
import NavList from "./NavList";
import api, { type ApiError } from "./api";
import { useChatSocket } from "./useChatSocket";
import type { Message } from "./types";

type UsernameMap = Record<number, string>;

/** How tall a message box may grow before it starts scrolling instead. */
const maxInputHeight = 200;

interface MessageItemProps {
    msg: Message;
    usernameMap: UsernameMap;
    account_id: number;
    chat_id: number;
    isChatOwner: boolean;
}

function MessageItem({ msg, usernameMap, account_id, chat_id, isChatOwner }: MessageItemProps) {
    const [isEditing, setIsEditing] = useState(false);
    const username = msg.account_id === null ? '[removed]' : usernameMap[msg.account_id] || '[removed]';
    const time = new Date(msg.created_at).toLocaleString();
    const isAuthor = msg.account_id === account_id;
    const { headers } = useAuth();
    const queryClient = useQueryClient();

    const deleteMutation = useMutation<unknown, ApiError>({
        mutationFn: () => api.del(`/chats/${chat_id}/messages/${msg.id}`, headers),
        onSuccess: () =>
            queryClient.invalidateQueries({ queryKey: ["chats/chatId/messages", chat_id] }),
    });

    return (
        <li className="py-4">
            <div className="flex flex-col border border-gray-600 p-2 rounded-lg">
                <div className="flex justify-between">
                    <div className="text-pink-950 text-sm">{username}</div>
                    <div className="text-sm">{time}</div>
                </div>

                <div className="flex justify-between items-start mt-2">
                    {/* min-w-0 is what lets the text wrap: a flex item defaults to
                        min-width:auto, so without it this div grows to fit the longest
                        line instead of shrinking and letting the text break. */}
                    <div className="flex-1 min-w-0">
                        {isEditing ? (
                            <EditMessageField
                                current_message={msg.text}
                                message_id={msg.id}
                                chat_id={chat_id}
                                onFinish={() => setIsEditing(false)}
                            />
                        ) : (
                            // pre-wrap so the line breaks a sender typed are kept, and
                            // break-words so an unbroken run of characters cannot widen the row
                            <span className="whitespace-pre-wrap break-words">{msg.text}</span>
                        )}
                    </div>

                    {(isAuthor || isChatOwner) && (
                        <div className="flex gap-2 ml-4">
                            {isAuthor && (
                                <button
                                    className="text-xs hover:bg-gray-200 border border-black rounded py-1 px-2 cursor-pointer"
                                    onClick={() => {
                                        if (isEditing) {
                                            document
                                                .getElementById(`editMessageField-${msg.id}`)
                                                ?.closest("form")
                                                ?.requestSubmit();
                                        } else {
                                            setIsEditing(true);
                                        }
                                    }}
                                >
                                    {isEditing ? "Save" : "Edit"}
                                </button>
                            )}
                            {isEditing ? (
                                <button
                                    className="text-xs text-gray-600 hover:underline cursor-pointer"
                                    onClick={() => setIsEditing(false)}
                                >
                                    Cancel
                                </button>
                            ) : (
                                <button
                                    className="text-xs hover:bg-red-500 border border-black rounded py-1 px-2 cursor-pointer"
                                    onClick={() => deleteMutation.mutate()}
                                >
                                    Delete
                                </button>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </li>
    );
}

interface EditMessageFieldProps {
    current_message: string;
    message_id: number;
    chat_id: number;
    onFinish: () => void;
}

function EditMessageField({ current_message, message_id, chat_id, onFinish }: EditMessageFieldProps) {
    const [text, setText] = useState(current_message);
    const { headers } = useAuth();
    const queryClient = useQueryClient();
    const inputRef = useRef<HTMLTextAreaElement>(null);

    useEffect(() => {
        inputRef.current?.focus();
    }, []);

    // Matches the compose box, so editing a message that has line breaks keeps them.
    useLayoutEffect(() => {
        const textarea = inputRef.current;
        if (textarea === null) {
            return;
        }
        textarea.style.height = "auto";
        textarea.style.height = `${Math.min(textarea.scrollHeight, maxInputHeight)}px`;
    }, [text]);

    const mutation = useMutation<Message, ApiError, { text: string }>({
        mutationFn: ({ text }) =>
            api.put<Message>(`/chats/${chat_id}/messages/${message_id}`, headers, { text }),
        onSuccess: () => {
            queryClient
                .invalidateQueries({ queryKey: ["chats/chatId/messages", chat_id] })
                .then(() => onFinish());
        },
    });

    const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (!text.trim()) return;
        mutation.mutate({ text });
    };

    const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            e.currentTarget.form?.requestSubmit();
        }
        if (e.key === "Escape") {
            onFinish();
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <textarea
                ref={inputRef}
                id={`editMessageField-${message_id}`}
                rows={1}
                onChange={(e) => setText(e.target.value)}
                onKeyDown={handleKeyDown}
                value={text}
                autoComplete={"off"}
                className={'border border-black px-2 py-1 rounded w-full resize-none overflow-y-auto leading-6'}
            />
        </form>
    );
}

interface ChatHeaderProps {
    chat_id: number;
    isMember: boolean;
    connected: boolean;
}

function ChatHeader({ chat_id, isMember, connected }: ChatHeaderProps) {
    const { chat } = useChat(chat_id);
    const { account } = useAccount();
    const { headers } = useAuth();
    const queryClient = useQueryClient();
    const navigate = useNavigate();
    const [errorMsg, setErrorMsg] = useState("");

    const isOwner = chat.owner_id === account.id;

    const joinMutation = useMutation<unknown, ApiError>({
        mutationFn: () => api.post(`/chats/${chat_id}/accounts`, headers, { account_id: account.id }),
        onSuccess: () => {
            setErrorMsg("");
            queryClient.invalidateQueries({ queryKey: ["my-chats"] });
            queryClient.invalidateQueries({ queryKey: ["chats/chatId/accounts", chat_id] });
        },
        onError: (error) => setErrorMsg(error.message),
    });

    const leaveMutation = useMutation<unknown, ApiError>({
        mutationFn: () => api.del(`/chats/${chat_id}/accounts/${account.id}`, headers),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["my-chats"] });
            navigate("/chats");
        },
        onError: (error) => setErrorMsg(error.message),
    });

    return (
        <div className="flex justify-between items-center border-b border-gray-300 py-3">
            <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold">{chat.name}</h1>
                {isMember && (
                    <span
                        title={connected ? "live" : "reconnecting..."}
                        className={`inline-block h-2 w-2 rounded-full ${
                            connected ? "bg-lime-500" : "bg-gray-400"
                        }`}
                    />
                )}
            </div>
            <div className="flex items-center gap-3">
                {errorMsg && <span className="text-xs text-amber-700">{errorMsg}</span>}
                {isMember ? (
                    <button
                        onClick={() => leaveMutation.mutate()}
                        disabled={isOwner}
                        title={isOwner ? "the owner of a chat cannot leave it" : undefined}
                        className={`text-sm border border-black rounded px-3 py-1 ${
                            isOwner
                                ? "bg-gray-200 text-gray-500 cursor-not-allowed"
                                : "hover:bg-red-400 cursor-pointer"
                        }`}
                    >
                        Leave
                    </button>
                ) : (
                    <button
                        onClick={() => joinMutation.mutate()}
                        className="text-sm border border-black rounded px-3 py-1 bg-pink-300 text-white hover:bg-pink-400 cursor-pointer"
                    >
                        Join
                    </button>
                )}
            </div>
        </div>
    );
}

function MessageList({ chat_id }: { chat_id: number }) {
    const { messageList, isLoading } = useMessages(chat_id);
    const { account } = useAccount();
    const { accounts } = useChatAccounts(chat_id);
    const { chat } = useChat(chat_id);
    const { connected } = useChatSocket(chat_id);
    const containerRef = useRef<HTMLUListElement>(null);
    // False until this chat has been anchored to its latest message.
    const hasAnchored = useRef(false);
    // Whether the reader is currently parked at the newest message.
    const atBottom = useRef(true);

    const handleScroll = () => {
        const container = containerRef.current;
        if (container !== null) {
            atBottom.current =
                container.scrollHeight - container.clientHeight - container.scrollTop <= 8;
        }
    };

    // Opening a different chat should land at the bottom again.
    useLayoutEffect(() => {
        hasAnchored.current = false;
    }, [chat_id]);

    // useLayoutEffect rather than useEffect: this runs before the browser paints, so the
    // chat is never drawn at the top and then scrolled down.
    useLayoutEffect(() => {
        const container = containerRef.current;
        // While loading, the list holds a placeholder whose height is not the real one.
        if (container === null || isLoading) {
            return;
        }
        if (hasAnchored.current) {
            // messages arriving in an open chat animate into view
            container.scrollTo({ top: container.scrollHeight, behavior: "smooth" });
        } else {
            container.scrollTop = container.scrollHeight;
            hasAnchored.current = true;
        }
    }, [messageList, isLoading, chat_id]);

    // The list shrinks as the compose box grows, which would otherwise push the newest
    // message out of sight. Re-pin to the bottom on resize, but only for a reader who was
    // already there, so scrolling up to read history is not undone.
    useLayoutEffect(() => {
        const container = containerRef.current;
        if (container === null) {
            return;
        }
        const observer = new ResizeObserver(() => {
            if (atBottom.current) {
                container.scrollTop = container.scrollHeight;
            }
        });
        observer.observe(container);
        return () => observer.disconnect();
    }, []);

    const usernameMap = useMemo(() => {
        return accounts.reduce<UsernameMap>((acc, account) => {
            acc[account.id] = account.username;
            return acc;
        }, {});
    }, [accounts]);

    const isMember = account.id in usernameMap;
    const isChatOwner = chat.owner_id === account.id;

    return (
        <div className={"pb-5 flex flex-col h-screen"}>
            <ChatHeader chat_id={chat_id} isMember={isMember} connected={connected} />
            {/* pr-3 keeps the message cards clear of the scrollbar instead of ending
                flush against it. ChatForm carries the same padding so the compose row
                stays aligned with the messages above it. */}
            <ul ref={containerRef} onScroll={handleScroll} className={`overflow-y-scroll flex-1 pr-3`}>
                {messageList.map((message) => (
                    <MessageItem
                        key={message.id}
                        msg={message}
                        usernameMap={usernameMap}
                        account_id={account.id}
                        chat_id={chat_id}
                        isChatOwner={isChatOwner}
                    />
                ))}
            </ul>
            <div>
                <ChatForm sendEnabled={isMember} chat_id={chat_id} account_id={account.id} />
            </div>
        </div>
    );
}

interface ChatFormProps {
    sendEnabled: boolean;
    chat_id: number;
    account_id: number;
}

function ChatForm({ sendEnabled, chat_id, account_id }: ChatFormProps) {
    const [text, setMessage] = useState("");
    const { headers } = useAuth();
    const queryClient = useQueryClient();
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    const mutation = useMutation<Message, ApiError, { text: string; account_id: number }>({
        mutationFn: ({ text, account_id }) =>
            api.post<Message>(`/chats/${chat_id}/messages`, headers, { text, account_id }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["chats/chatId/messages", chat_id] });
        },
    });

    const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        if (!text.trim()) return;
        mutation.mutate({ text, account_id });
        setMessage("");
    };

    // Enter sends and shift+enter breaks the line, so a textarea still behaves like a
    // chat box rather than swallowing the key that used to submit the form.
    const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            e.currentTarget.form?.requestSubmit();
        }
    };

    // Grow to fit the text, then scroll internally once it hits the cap. Height has to be
    // cleared first so scrollHeight reports the content height rather than the current one.
    useLayoutEffect(() => {
        const textarea = textareaRef.current;
        if (textarea === null) {
            return;
        }
        textarea.style.height = "auto";
        textarea.style.height = `${Math.min(textarea.scrollHeight, maxInputHeight)}px`;
    }, [text]);

    return (
        <form onSubmit={handleSubmit} className={"pt-3 pr-3"}>
            <label htmlFor="messageInput" className="sr-only">Message</label>
            <div className="flex gap-2 items-end">
                <textarea
                    id="messageInput"
                    ref={textareaRef}
                    rows={1}
                    onChange={(e) => setMessage(e.target.value)}
                    onKeyDown={handleKeyDown}
                    value={text}
                    placeholder={sendEnabled ? "Type a message..." : "Join this chat to send messages"}
                    disabled={!sendEnabled}
                    autoComplete={"off"}
                    className={`border border-black px-3 py-2 rounded flex-1 resize-none overflow-y-auto leading-6 ${
                        !sendEnabled ? "bg-gray-200 text-gray-500 cursor-not-allowed" : ""
                    }`}
                />
                <button
                    type="submit"
                    disabled={!sendEnabled || !text.trim()}
                    className={`px-4 py-2 rounded border border-black ${
                        sendEnabled && text.trim()
                            ? "bg-pink-300 text-white hover:bg-pink-400 cursor-pointer"
                            : "bg-gray-200 text-gray-500 cursor-not-allowed"
                    }`}
                >
                    Send
                </button>
            </div>
        </form>
    );
}

export default function Chat() {
    const { id } = useParams();
    // useParams yields a string, while the API returns numeric ids. Normalizing here
    // keeps the react-query cache keys consistent with the ids carried on messages.
    const chat_id = Number(id);

    return (
        <div className={"flex"}>
            <div className={"w-1/4 border-r border-gray-300"}>
                <NavList />
            </div>
            {/* min-w-0 for the same reason as the message row: without it a wide message
                could push this panel past 75% instead of wrapping inside it. */}
            <div className={"w-3/4 min-w-0 pr-4 pl-4 bg-white"}>
                <MessageList chat_id={chat_id} />
            </div>
        </div>
    );
}
