import { useQuery } from "@tanstack/react-query";
import { useAuth } from "./hooks";
import api, { ApiError } from "./api";
import type { Account, Chat, ChatAccounts, ChatMessages, Chats, Message, User } from "./types";

const nullChat: Chat = {
    id: -1,
    name: "loading...",
    owner_id: -1,
};

const nullMessage: Message = {
    id: -1,
    text: "Loading...",
    account_id: -1,
    chat_id: -1,
    created_at: "",
};

const nullAccount: Account = {
    id: -1,
    username: "loading...",
};

const nullUser: User = {
    id: -1,
    username: "loading...",
    email: "",
};

/** Every chat on the server, for the browse page. */
export const useChats = () => {
    const { headers } = useAuth();
    const { data, error, isLoading } = useQuery<Chats, ApiError>({
        queryKey: ["chats"],
        queryFn: () => api.get<Chats>("/chats/", headers),
        retry: false,
    });

    const chats = isLoading ? [nullChat] : data?.chats || [];
    return { chats, error };
};

/** Only the chats the logged in user has joined, for the sidebar. */
export const useMyChats = () => {
    const { headers, loggedIn } = useAuth();
    const { data, error, isLoading } = useQuery<Chats, ApiError>({
        queryKey: ["my-chats"],
        queryFn: () => api.get<Chats>("/accounts/me/chats", headers),
        enabled: loggedIn,
        retry: false,
    });

    const chats = isLoading ? [nullChat] : data?.chats || [];
    return { chats, error };
};

export const useChat = (id: number) => {
    const { headers } = useAuth();
    const { data, error } = useQuery<Chat, ApiError>({
        queryKey: ["chats/chatId", id],
        queryFn: () => api.get<Chat>("/chats/" + id, headers),
        retry: false,
    });

    return { chat: data || nullChat, error };
};

export const useMessages = (id: number) => {
    const { headers } = useAuth();
    const { data, error, isLoading } = useQuery<ChatMessages, ApiError>({
        queryKey: ["chats/chatId/messages", id],
        queryFn: () => api.get<ChatMessages>("/chats/" + id + "/messages", headers),
        retry: false,
        // No polling: useChatSocket pushes new, edited and deleted messages into this
        // cache entry, and resyncs it whenever the socket reconnects.
    });

    const messageList = isLoading ? [nullMessage] : data?.messages || [];
    return { messageList, isLoading, error };
};

export const useChatAccounts = (id: number) => {
    const { headers } = useAuth();
    const { data, error, isLoading } = useQuery<ChatAccounts, ApiError>({
        queryKey: ["chats/chatId/accounts", id],
        queryFn: () => api.get<ChatAccounts>("/chats/" + id + "/accounts", headers),
        retry: false,
    });

    const accounts = isLoading ? [nullAccount] : data?.accounts || [];
    return { accounts, error };
};

export const useAccount = () => {
    const { headers, loggedIn, logout } = useAuth();
    const { data, error } = useQuery<User, ApiError>({
        queryKey: ["account"],
        queryFn: () => api.get<User>("/accounts/me", headers),
        enabled: loggedIn,
    });

    if (error?.code === "invalid_credentials") {
        logout();
    }

    const account = data || nullUser;
    return { account, error };
};
