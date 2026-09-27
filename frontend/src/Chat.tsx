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
  const username = msg.account_id === null ? 'one departed' : usernameMap[msg.account_id] || 'one departed';
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
    <li className="scroll-entry py-4">
      <div className="flex justify-between items-start gap-4">
        {/* min-w-0 is what lets the text wrap: a flex item defaults to
                    min-width:auto, so without it this div grows to fit the longest
                    line instead of shrinking and letting the text break. */}
        <div className="flex-1 min-w-0">
          <div className="flex items-baseline gap-3 mb-1">
            <span className="heading text-sm text-crimson">{username}</span>
            <span className="text-xs italic text-ink-faded">{time}</span>
          </div>

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
            <span className="whitespace-pre-wrap break-words leading-relaxed">{msg.text}</span>
          )}
        </div>

        {(isAuthor || isChatOwner) && (
          <div className="flex gap-2 shrink-0">
            {isAuthor && (
              <button
                className="btn-margin px-2 py-1 cursor-pointer"
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
                {isEditing ? "Seal" : "Amend"}
              </button>
            )}
            {isEditing ? (
              <button
                className="btn-margin px-2 py-1 cursor-pointer"
                onClick={() => setIsEditing(false)}
              >
                Abandon
              </button>
            ) : (
              <button
                className="btn-margin px-2 py-1 cursor-pointer"
                onClick={() => deleteMutation.mutate()}
              >
                Strike
              </button>
            )}
          </div>
        )}
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
        className={'field-ink px-2 py-1 w-full resize-none overflow-y-auto leading-6'}
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
    <div className="flex justify-between items-center gap-4 pb-3">
      <div className="flex items-baseline gap-3 min-w-0">
        <h1 className="heading text-2xl text-gilt-light truncate">{chat.name}</h1>
        {isMember && (
          <span
            title={connected ? "the rider is at the gate" : "awaiting the rider..."}
            className={`inline-block h-2.5 w-2.5 rounded-full shrink-0 ${connected
                ? "bg-moss shadow-[0_0_6px_2px_rgba(120,160,80,0.6)]"
                : "bg-ink-faded"
              }`}
          />
        )}
      </div>
      <div className="flex items-center gap-3 shrink-0">
        {errorMsg && <span className="text-xs text-crimson-light italic">{errorMsg}</span>}
        {isMember ? (
          <button
            onClick={() => leaveMutation.mutate()}
            disabled={isOwner}
            title={isOwner ? "a lord may not abandon their own council" : undefined}
            className={`btn-iron px-3 py-1 text-xs uppercase ${isOwner ? "" : "cursor-pointer"}`}
          >
            Depart
          </button>
        ) : (
          <button
            onClick={() => joinMutation.mutate()}
            className="btn-seal px-3 py-1 text-xs uppercase cursor-pointer"
          >
            Enter
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
    <div className={"pb-5 pt-4 flex flex-col h-screen"}>
      <ChatHeader chat_id={chat_id} isMember={isMember} connected={connected} />

      {/* The scroll itself: a turned rod at either end with parchment between. */}
      <div className="flex-1 min-h-0 flex flex-col px-2">
        <div className="scroll-rod shrink-0" />
        {/* pr-3 keeps the entries clear of the scrollbar instead of ending flush
                    against it. ChatForm carries the same padding so the compose row
                    stays aligned with the messages above it. */}
        <ul
          ref={containerRef}
          onScroll={handleScroll}
          className={"parchment parchment-curl flex-1 min-h-0 overflow-y-scroll px-8 py-2 pr-3"}
        >
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
        <div className="scroll-rod shrink-0" />
      </div>

      <div className="px-2">
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
    <form onSubmit={handleSubmit} className={"pt-4 pr-3"}>
      <label htmlFor="messageInput" className="sr-only">Message</label>
      <div className="flex gap-3 items-end">
        <textarea
          id="messageInput"
          ref={textareaRef}
          rows={1}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          value={text}
          placeholder={sendEnabled ? "Set quill to parchment..." : "Enter this council to send word"}
          disabled={!sendEnabled}
          autoComplete={"off"}
          className={"field-ink px-3 py-2 flex-1 resize-none overflow-y-auto leading-6"}
        />
        <button
          type="submit"
          disabled={!sendEnabled || !text.trim()}
          className={`btn-seal px-5 py-2 text-sm uppercase ${sendEnabled && text.trim() ? "cursor-pointer" : ""
            }`}
        >
          Dispatch
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
    <div className={"flex hall min-h-screen"}>
      <div className={"w-1/4 min-w-0 border-r-2 border-oak-dark"}>
        <NavList />
      </div>
      {/* min-w-0 for the same reason as the message row: without it a wide message
                could push this panel past 75% instead of wrapping inside it. */}
      <div className={"w-3/4 min-w-0 px-6"}>
        <MessageList chat_id={chat_id} />
      </div>
    </div>
  );
}
