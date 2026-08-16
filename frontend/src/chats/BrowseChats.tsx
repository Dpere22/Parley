import { useMemo, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router";
import NavList from "../NavList";
import CreateChat from "./CreateChat";
import { useAccount, useChats, useMyChats } from "../queries";
import { useAuth } from "../hooks";
import api, { type ApiError } from "../api";
import type { Chat } from "../types";

function JoinButton({ chat }: { chat: Chat }) {
    const { headers } = useAuth();
    const { account } = useAccount();
    const queryClient = useQueryClient();
    const navigate = useNavigate();
    const [errorMsg, setErrorMsg] = useState("");

    const mutation = useMutation<unknown, ApiError>({
        mutationFn: () => api.post(`/chats/${chat.id}/accounts`, headers, { account_id: account.id }),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["my-chats"] });
            queryClient.invalidateQueries({ queryKey: ["chats/chatId/accounts", chat.id] });
            navigate(`/chats/${chat.id}`);
        },
        onError: (error) => setErrorMsg(error.message),
    });

    return (
        <div className="flex items-center gap-2">
            {errorMsg && <span className="text-xs text-amber-700">{errorMsg}</span>}
            <button
                onClick={() => mutation.mutate()}
                className="text-sm border border-black rounded px-3 py-1 bg-pink-300 text-white hover:bg-pink-400 cursor-pointer"
            >
                Join
            </button>
        </div>
    );
}

export default function BrowseChats() {
    const { chats, error } = useChats();
    const { chats: myChats } = useMyChats();
    const navigate = useNavigate();

    const joinedIds = useMemo(
        () => new Set(myChats.map((chat) => chat.id)),
        [myChats],
    );

    return (
        <div className={"flex"}>
            <div className={"w-1/4 border-r border-gray-300"}>
                <NavList />
            </div>
            <div className={"w-3/4 pr-4 pl-4 pt-4 pb-8 bg-white h-screen overflow-y-auto"}>
                <h1 className={"text-3xl font-bold text-center pb-4"}>Browse chats</h1>
                <div className="max-w-2xl mx-auto space-y-4">
                    <CreateChat />
                    {error && <p className="text-sm text-amber-700">{error.message}</p>}
                    <ul className="border border-black rounded divide-y divide-gray-300">
                        {chats.map((chat) => (
                            <li key={chat.id} className="flex justify-between items-center p-3">
                                <span>{chat.name}</span>
                                {joinedIds.has(chat.id) ? (
                                    <button
                                        onClick={() => navigate(`/chats/${chat.id}`)}
                                        className="text-sm border border-black rounded px-3 py-1 hover:bg-gray-100 cursor-pointer"
                                    >
                                        Open
                                    </button>
                                ) : (
                                    <JoinButton chat={chat} />
                                )}
                            </li>
                        ))}
                    </ul>
                </div>
            </div>
        </div>
    );
}
