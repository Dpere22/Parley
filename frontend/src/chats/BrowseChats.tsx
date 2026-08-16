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
        <div className="flex items-center gap-2 shrink-0">
            {errorMsg && <span className="text-xs text-crimson-light italic">{errorMsg}</span>}
            <button
                onClick={() => mutation.mutate()}
                className="btn-seal px-4 py-1 text-xs uppercase cursor-pointer"
            >
                Enter
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
        <div className={"flex hall min-h-screen"}>
            <div className={"w-1/4 min-w-0 border-r-2 border-oak-dark"}>
                <NavList />
            </div>
            <div className={"w-3/4 min-w-0 px-6 pt-8 pb-8 h-screen overflow-y-auto"}>
                <h1 className={"heading text-3xl text-center text-gilt-light pb-2"}>The Great Hall</h1>
                <p className="text-center text-sm italic text-parchment/60">
                    Every council in the realm
                </p>
                <hr className="rule-gilt w-80 mx-auto my-6" />

                <div className="max-w-2xl mx-auto space-y-6">
                    <CreateChat />
                    {error && <p className="text-sm text-crimson-light italic">{error.message}</p>}

                    <div className="parchment parchment-curl border-2 border-oak-dark rounded-sm shadow-xl px-6 py-2">
                        <ul>
                            {chats.map((chat) => (
                                <li
                                    key={chat.id}
                                    className="scroll-entry flex justify-between items-center gap-4 py-3"
                                >
                                    <span className="heading text-base min-w-0 truncate">{chat.name}</span>
                                    {joinedIds.has(chat.id) ? (
                                        <button
                                            onClick={() => navigate(`/chats/${chat.id}`)}
                                            className="btn-iron px-4 py-1 text-xs uppercase cursor-pointer shrink-0"
                                        >
                                            Attend
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
        </div>
    );
}
