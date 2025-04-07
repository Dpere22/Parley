import {useQuery} from "@tanstack/react-query";
import { useAuth } from "./hooks";
import api from "./api.js";

const nullChat = {
    id: -1,
    name: "loading...",
    owner_id: -1
};

const nullMessage = {
    "id": -1,
    "text": "Loading...",
    "account_id": -1,
    "chat_id": -1,
    "created_at": "",
};

const nullAccount = {
    "id": -1,
    "username": "loading...",
};

export const useChats = () =>{
    const {data, error, isLoading} = useQuery({
        queryKey: ["chats"],
        queryFn: () => api.get("/chats/", {}),
        retry: false,
    });

    const chats = isLoading ? [nullChat] : data?.chats || [];
    return {chats, error};
};

export const useMessages = (id) => {
    const {data, error, isLoading} = useQuery({
        queryKey: ["chats/chatId/messages", id],
        queryFn: () => api.get("/chats/" + id + "/messages", {}),
        retry: false,
    });

    const messageList = isLoading ? [nullMessage] : data?.messages || [];
    return {messageList, error};
};

export const useChatAccounts = (id) => {
    const {data, error, isLoading} = useQuery({
        queryKey: ["chats/chatId/accounts", id],
        queryFn: () => api.get("/chats/" + id + "/accounts", {}),
        retry: false,
    });

    const accounts = isLoading ? [nullAccount] : data?.accounts || [];
    return {accounts, error};
}

export const useAccount = () => {
    const { headers, loggedIn, logout } = useAuth();
    const { data, error } = useQuery({
        queryKey: ["account"],
        queryFn: () => api.get("/accounts/me", headers),
        enabled: loggedIn,
    });

    if (error?.code === "invalid_credentials") {
        logout();
    }

    const account = data || nullAccount;
    return { account, error };
};